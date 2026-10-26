# Security-Focused Code Review

> **This file is not a "general code review."** Readability, architectural elegance,
> performance tuning, naming, test coverage → those are `engineering:code-review`'s
> job; NOT done here. Here we look only for **correctness bugs with security impact**:
> bugs that, when they misbehave, open a door for an attacker, leak data, escape
> authorization, or make the system stoppable.

> **The distinguishing test:** "Could an attacker trigger this bug on purpose, and if
> they did, what would they gain?" If the answer is "nothing, it just gets
> ugly/slow" → hand it off, don't write it here.

---

## 0. How to read — backward from the sink

Reading file by file, start to finish, wastes time and misses things. **Start from
the sink, walk backward toward the input** (taint tracing):

1. List the dangerous sinks (query, `exec`, file path, HTML output, `fetch(url)`,
   deserialization, redirect, log).
2. For each sink: where did this value come from? Follow the call chain **all the
   way to the input point**.
3. Is there validation/escaping anywhere in the chain? If so, **does that validation
   actually run** (is it conditional, behind `if (config.strict)`, disabled in
   tests)?
4. If you can't reach the input point → `NOT MEASURED`, don't guess.

**Give a number:** "N sinks found, M of them touch untrusted data, K of them have
unconditional validation." Without an inventory, there is no review.

---

## 1. Correctness bugs with security impact

### 1.1 Control flow
- **Missing early return:** authorization check `if (!authorized) { log(); }` — no
  `return`, flow continues. Classic and lethal.
- **Negative/default-allow:** `if (role === "banned") deny;` — an unknown role is
  accepted. The correct approach is a **whitelist**: everything except a known
  permitted role is DENIED.
- **Caught-and-swallowed error:** `try { validate() } catch {}` — validation blows
  up, the flow is assumed "successful." A silent `catch` block is a CRITICAL
  candidate.
- **Forgotten async/await:** `if (userAuthorized(x))` — the function returns a
  Promise, a Promise is always truthy → **the check never runs**. Search these one
  by one in JS/TS.
- **Short-circuit mistake:** `a || b` confused with `a ?? b`; `0`, `""`, `false`
  values falling through to the default (e.g. `limit = req.query.limit || 1000`).

### 1.2 Type and coercion
- **Loose comparison:** `==` with type coercion (`"0" == false`), `parseInt`
  without a radix.
- **Numeric overflow / floating point:** `float` in money and quota math; negative
  quantity accepted (`quantity: -5` → balance goes up).
- **JSON type confusion:** expected `string`, received `{"$ne":null}` or an array.
  **Is there schema validation, or is there not even a `typeof` check?**

### 1.3 Concurrency and state
- **TOCTOU:** can state change between the check and the use (balance check →
  debit; file exists → open)?
- **Non-atomic counter:** if a quota/attempt counter is updated with
  read-increment-write, there's a race condition; that's how rate limits get
  bypassed.
- **Shared mutable state:** per-request data (user context) held at module scope →
  leakage across requests.
- **Idempotency:** what happens if a payment/creation endpoint is called twice?

### 1.4 Bounds and resources
- No upper bound on pagination/limit → pulling the entire table in one request.
- Unbounded loop/recursion depth fed by user data.
- File/buffer size loaded into memory without validation.

### 1.5 Crypto and randomness hygiene
- `Math.random()`, `rand()`, a timestamp used for a token/password-reset/session ID
  → **predictable**. `crypto.randomBytes` / `secrets` is required.
- Fixed IV, ECB mode, homegrown encryption, a hardcoded string used as a secret key.
- **Timing-safe comparison:** is the token/HMAC comparison done with `===` (timing
  leak), or with `timingSafeEqual`?
- Hashing: a fast hash (MD5/SHA) for passwords → CRITICAL.

### 1.6 User enumeration and leakage
- Different error message: "user does not exist" vs. "wrong password" → user
  enumeration.
- Different response time: bcrypt runs for an existing user, doesn't run for a
  nonexistent one.
- Sequential/predictable ID (auto-increment) + weak authorization = bulk data
  scraping.

---

## 2. Dependencies and supply chain

- **CVE scan:** `npm audit` / `pip-audit` / `osv-scanner` — write the output in the
  report **as a count** (number of critical/high). If not run, `NOT MEASURED`.
- **Lock file:** is `package-lock.json` / `poetry.lock` in the repo; is install done
  with `ci`/`--frozen` (otherwise versions drift)?
- **`postinstall` scripts:** dependencies running code at install time.
- **Typosquatting / ownership:** is a newly added package name a spelling variant of
  a popular package; is it maintenance-abandoned (date of last release)?
- **License:** the user's red line — a new dependency = license + CVE check.

### 2.1 PHP project: runtime version and package audit (v2.8.0)

This section runs when T2 finds a PHP signature. **No fixed CVE table is kept** (it goes stale):
the match for a known vulnerability comes from a scanner database; only the EOL-branch rule
is fixed here.

**Runtime version — source order.** Every version found is written into the report WITH ITS
SOURCE (`8.3.30 — Dockerfile:1`); a comment line (`#`) is not a source:
1. Dockerfile / docker-compose image tag (`FROM php:8.3.30-fpm`, `image: php:…`; the default
   value if given through `ARG`)
2. `.php-version`
3. `composer.json` → `config.platform.php` (a dependency-resolution target, which may not be
   what runs; say so)
4. CI: `setup-php` / matrix (`php-version:`) — a matrix lists tested versions, which may not
   be what runs in production; say so
5. Buildpack/platform file (`.platform.app.yaml` `type: php:…`, `app.yaml` `runtime: php…`,
   `.htaccess` with a PHP handler)

- In a multi-stage Dockerfile the LAST `FROM php:` stage is the runtime; earlier stages are written separately.
- If sources disagree (e.g. compose `php:7.4`, Dockerfile `php:8.3.30`), every version is written
  with its source and the disagreement is stated; the EOL rule applies to the oldest runtime source.
- `"require": {"php": ">=8.1"}` in `composer.json` is a **lower bound and does NOT count as the running version**.
- If the tag does not give the patch level (`php:8.3-fpm`, `php:8-apache`, `latest`), write the
  tag + source (the branch, if the tag gives one) and mark the missing level NOT MEASURED; the
  source EXISTS, so the fixed "not in the repository" line below is not written.
- If only `composer.json` (or only `*.php`) exists and there is no server entry point, framework or
  image, the project may be a library: write "library — the runtime belongs to the consumer" on that
  line; the fixed "not in the repository" line and `MEASURE FIRST` are not required (a
  `config.platform.php`, if present, is still written with its source).
- If the version is nowhere in the repository (shared hosting, a file backup), write **this
  fixed line** into the report and do NOT say "clean": "PHP runtime version is not in the repository — NOT MEASURED; check it on the server/hosting panel."
  This result is also written to the report's NOT MEASURED section and to a `kapsam` row in the
  JSON (`olculmedi`, `sebep`); the verdict becomes `MEASURE FIRST`.

**EOL rule** (measured 2026-10-22, php.net `supported-versions` and `eol.php`; **re-verify**):
PHP ≤ 8.1 no longer receives official security patches → finding (the distribution's/LTS
vendor's backport may exist; ask separately, do not assume). PHP 8.2's security support ends
on 2026-12-31 → warning; after that date 8.2 is a finding too. Report mapping: a ≤ 8.1 finding is
`confirmed`, evidence type STATIC (`poc_girdi` = the `file:line` of the tag, `gozlenen` = the
version), severity MEDIUM — or the severity of a critical/high CVE that scanner output matches to
that version; the 8.2 warning is INFO.

**Package and image scan** (output into the report **as a count**): if `composer.lock` exists at
any depth (excluding `vendor/`), `composer audit` (if composer is missing or the package database
is unreachable, NOT MEASURED + reason); if `composer.json` exists but `composer.lock` does not,
"composer.lock missing — composer audit does not run, NOT MEASURED". The image scan covers only a
PUBLIC base-image tag (`php:…`): `trivy image <tag>` / `grype <tag>` (if the tool is installed;
pulling an image needs network — no tool or network, NOT MEASURED). For an image in the target's
own/private registry write "NOT MEASURED — no authorization (§0.1)". CVEs that hit the version
found, and the versions that fix them, are written **from scanner output**; with no scanner,
write "comparison with the current patched version NOT MEASURED".

**Report block (v2.8.0).** The PHP finding is not free text but the FIXED-FIELD block in `SKILL.md` LANE B (`### PHP runtime`). The mechanical gate `php_kapisi.py` compares every field with the `php_olc` measurement one to one: T2 PHP, version+`file:line` (a real source; case included), patch level, EOL, composer audit (a count, or not-measured+reason, or n/a), image-scan format. What the gate CANNOT verify: (1) whether the numbers (composer N, scanner N) are true; (2) the content of the `NOT MEASURED (<reason>)` / `N/A (<reason>)` reason text (only ≥ 3 characters); (3) the free text as a whole — only the `PHP x.y … file:line` pattern is checked (a version without a source, "Dockerfile line 2", a line without the word `php`, a line containing a constraint word slip through; on a line with a scanner word only the version is exempt, the `file:line` must be real; field-labelled lines outside the block fall under this pattern too, but a field VALUE contradiction — e.g. `EOL: SUPPORTED` outside the region — is not checked). Block region: from the heading to the first blank line; "clean/safe/no risk" is forbidden on ALL lines of the region; a "Notes:" below it does not count as a field; the `T2 PHP` evidence must be a list of files/directories that exist in the target and include at least one PHP signature file.

Optional mechanical check: `python <araclar-path>/php_kapisi.py --hedef <dir> --rapor <report.md>`.
---

## 3. Secret used in the WRONG LAYER

It's not enough for a secret to be in `.env`; **where it's read from** is also
audited.

| Bug | How to find it | Why it's critical |
|---|---|---|
| Server key is bundled into the client | search compiled bundle/APK for key patterns; a secret key carrying a `NEXT_PUBLIC_`, `VITE_`, `REACT_APP_` prefix | Anything that reaches the browser is public to everyone |
| Admin/service-role key is called from the browser | Supabase `service_role`, Firebase admin SDK, Stripe `sk_live` in client code | Direct full-privilege access to the database |
| Secret ends up in a log | `console.log(config)`, `set -x`, full request in an error body | Logs go to third parties |
| Secret in the URL | token in the query string → browser history, referer, server log | Too many leak paths |
| Secret in client storage | long-lived token in `localStorage` | Stolen in one line via XSS |
| Real value in a test/example file | `.env.example`, fixture, seed, README | If the repo is public, it's over |

**Measurement:** scan not just HEAD but the **entire git history**
(`git log -p -S "<pattern>" --all`). A secret deleted from HEAD is still in history
and **remains valid until revoked** — write the "rotate the key" patch into the
finding.

---

## 4. What NOT TO WRITE HERE (hand off)

| Observation | Where to |
|---|---|
| Slow query, N+1, unnecessary render | `engineering:code-review` |
| Naming, dead code, test coverage | `engineering:code-review` |
| Architectural choice (Kafka or SQS) | `engineering:architecture` |
| Release/artifact spec compliance (permissions, SDK, signature) | the relevant build QA skill |
| Product/design logic (pedagogy, penalty, tone) | the relevant design red-team |

Borderline case: a performance bug **that can be triggered by an attacker** (ReDoS,
unbounded pagination, compression bomb) stays here — at that point it's a security
issue.

---

## 5. MECHANICAL SCAN LAYER (widens the inventory, does NOT decide)

gedik's manual taint-tracing is the core; the mechanical layer **widens** it, it
does not replace it. Tools:
- **SAST:** `semgrep --config auto` · CodeQL (if the language supports it) ·
  `bandit` (Py) · `gosec` (Go) · `brakeman` (Rails) · `eslint-plugin-security` (JS)
- **Secrets:** `gitleaks` · `trufflehog` (mechanizes gedik's git-history scan)
- **Dependency/container:** `osv-scanner` · `grype` · `trivy` · `retire.js`
- **IaC:** `checkov` · `tfsec` · `trivy config`

> **K2 still applies:** every mechanical finding passes through gedik's PoC/
> provenance-tracing filter. "semgrep said so" is **not a finding by itself**;
> false positives are eliminated, real ones are proven with a PoC. The mechanical
> layer is reported **as a count** (number of critical/high), otherwise
> NOT MEASURED.
