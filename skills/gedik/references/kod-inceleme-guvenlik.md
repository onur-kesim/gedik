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
