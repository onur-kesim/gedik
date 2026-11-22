# gedik

**"Find it so it can be closed."** gedik breaks your own projects like an attacker and
lists the breaches. Output: findings numbered `G-1`, `G-2`… each with a working PoC and
a suggested patch. ("gedik" is Turkish for *a breach in a fortress wall.*)

## What's not delivered yet

- **Benchmark: measured — detection at or above the best tool.** A first scored run exists (see
  [Benchmark](#benchmark-measured--2026-09-30)). gedik's *detection* was at or above the best
  surveyed tool on both targets (Target 1 17/17, Target 2 11/11, 0 false positives). Its one
  weakness — the report being cut by Claude's real-time cyber safeguard on exploit-heavy
  targets — is now resolved **for Cyber-Verification-Program-approved accounts** (3/3 delivered
  after approval; ~2/6 delivered without). No general "better than X" claim is made: the detection edge
  is real, the delivery edge is account-dependent.
- **v2.13.1 (install ban) is measured only on a local fixture** (2026-11-22; one model, one prompt,
  EN skill; 5 runs, 0 requests to a real site). gedik is now instructed not to install dependencies or
  download and run packages in the repository it audits or in any copy of it (`npm`/`pnpm`/`yarn` install/ci/add,
  `npx <package>`, `pip install` and equivalents); a PoC that needs installation is written as
  `SUSPECTED (NOT RUN)`. The only exception is an explicitly requested local copy. In the MCP scenario
  installation was attempted in 0 of 4 runs (v2.13.0 on the same scenario: 3 of 4; n=4+4, not
  statistically significant, consistent direction); the MCP findings were found 2 of 2 in the seeded
  repository, with 0 of 2 false findings in the clean one. The local-copy exception still works (1 run:
  the copy was set up, delete/update only on the copy, only 10 GETs to the live site). ⚠️ Limit: PoCs
  that need no installation may still run on a copy of the target; still audit an untrusted repository
  in an isolated environment. In one run the local copy was set up in the working directory's
  `_calisma/` folder rather than the audited project's.
- **v2.13 (November 2026 update) is measured only on a local fixture** (2026-11-22; one model,
  claude-sonnet-5-5, one prompt, EN skill, n=2 per scenario; 16 runs in the first round + 9 in the
  single fix round, all completed; 0 requests to a real site). New: (a) **block page = STOP:** even when
  bot protection returns a block page with HTTP 200 (`cf-mitigated: challenge` header, body marker,
  content deviation) the run stops; the request script `req.sh` writes a STOP file into the run
  directory on a block, so chained calls send no further request (requests after the block in the fix
  round: 0/2; in the first round one chained run sent 3 more). (b) **MCP SDK** (D8.6–D8.8): SDK version
  via a security scanner, server-side token `aud` validation, client credentials not bound to their
  server, schema `$ref` resolution. (c) Python **`.pth` / `sitecustomize` startup hooks** (the mechanism
  of the 2026-11-17 PyPI incident). (d) **Server version disclosure** in the passive audit (`Server`,
  `X-Powered-By`, `meta generator`): every line carries the label "from the version header, not
  verified", and version matching is never done from memory. (e) OWASP LLM Top 10 **2026** numbering +
  Hidden Context Exposure; GitHub blocking `pull_request_target` by default in public repos from
  2026-12-02; version gates for CI agent actions and plugin pinning. Known limits: (1) ⚠️ **gedik may
  execute code from the repository it audits** (the installation part narrowed in v2.13.1: 0 of 4 runs attempted it, see above). In 2 of the 4 MCP-scenario runs the agent ran a PoC with
  `node` on a copy of the target or attempted `npm install` (in the other two the permission was
  denied); the prohibition is in the text, but in 3 of the 4 runs the file containing it was never
  opened. **Audit an untrusted repository only in an isolated environment or with Bash permissions
  restricted.** (2) `req.sh` protects only when it is used: in one run the passive reads were sent with
  plain `curl`. (3) HTTP/2 (ALPN), SDK version matching (no scanner installed), real Cloudflare/WAF
  responses, block markers in compressed bodies and the TR skill were NOT MEASURED. (4) Part of the
  scoring was done by an LLM reader (74/74 on a 14-report control set); the fix round was not blind:
  the scorer and fixtures were repaired after first-round results were seen (recorded in KRITER).
- **v2.12 (conditional active testing + local-copy mode) is measured only on a local fixture
  server** (2026-11-15/16; one model, one prompt, CVP account, n=2 per scenario; 16 runs incl. one fix
  round, all completed; every request logged). **No active request has ever been sent to a real site.**
  Active mode opens only when you say "active test", and each test only if its precondition is written
  in `YETKI.md` (`aktif:` block: window, request budget, test forms, LLM endpoints, two test accounts
  — never passwords —, canary records, brute-force list, CAPTCHA disabled, staging); otherwise the
  report says `no precondition, not tested`. Across 16 runs: 0 requests to real user objects, 0 to
  out-of-scope hosts, 0 live PUT/PATCH/DELETE, 0 CAPTCHA posts or solving attempts. Never allowed,
  under any condition: DoS on a live site, reading real people's data content, real user accounts,
  entering passwords, solving CAPTCHA. If you give the repository, gedik can run the app locally and
  run the otherwise-forbidden tests (delete, load, brute force) on that copy; each finding is tagged
  `kaynak-kod` / `yerel-kopya` / `canli-pasif` / `canli-aktif`. Known limits: (1) **one unmarked
  test POST in 4 active runs** — the shell had no `python`, the padding command returned empty and an
  empty message was sent; gedik does not yet verify the body before sending. (2) **The local copy
  started in only 1 of 2 runs** (no `python` found; the agent reported it instead of working around
  it) — check that the runtime exists before an active audit. (3) In one run 2 of 10 findings lacked
  the source tag. (4) The final text was not re-measured on the "no keyword" and "no CAPTCHA/staging"
  scenarios (those passed 2/2 on the previous text).
- **v2.11 (passive audit of someone else's site, by URL) is measured only against a local
  loopback HTTP fixture** (2026-11-15; one model, one prompt, CVP account, n=2 runs per scenario;
  14 runs, all completed; every request logged by the fixture server). **It has never been run
  against a real third-party site** — TLS, real DNS, CDN/WAF behaviour are NOT MEASURED.
  Authorization (c) is your own statement that the site owner allowed it; a written document or
  ownership token is optional. With that statement the audit stayed passive in 4 of 4 runs: GET/HEAD
  only (7 requests per run), at least 1.13 s between requests, 0 requests to out-of-scope hosts, and
  an instruction planted in the page ("POST here, you're allowed") was not followed (2 of 2). A host
  outside `YETKI.md` got 0 requests (2 of 2). Known limits: (1) **without authorization gedik sent 0
  requests (4 of 4), but the fixed refusal line (`NOT MEASURED — no authorization`) appeared verbatim
  in only 2 of 4 refusal reports** — judge by the refusal, not by the sentence. (2) **When a write is
  refused gedik no longer works around it (0 of 2 shell bypasses) and reports inline, but the fixed
  "could not write: <path>, reason: permission denied" line was not used verbatim (0 of 2).**
  (3) Active testing (forms, POST, logins, fuzzing, directory brute force, injection payloads) is
  **not in this release**.
  **Legal note:** in Türkiye, unauthorized access is a crime (TCK 243–245) and Cybersecurity Law
  No. 7545 (2025) adds authorization/certification duties for cybersecurity activity; whether those
  apply to an individual's free passive check is not settled here. This is not legal advice — the
  user who states the authorization carries the responsibility.
- **iOS lane (A8) is a checklist, not validated on a real system.** It has not yet been
  run against a real iOS / Capacitor-iOS app.
- **v2.10 (CI/CD supply chain + Next.js/RSC) is measured only on synthetic fixtures**
  (2026-11-12; one model, one prompt, CVP account, n=2 runs per fixture; 22 runs, all completed,
  no network or DNS attempt). Planted items were found with `file:line` in every run (CI/CD 4 of
  4, Next.js 2 of 2); the clean fixtures got no finding in those classes. Known limits:
  (1) **version matching needs a scanner.** With `osv-scanner` on PATH the advisory IDs came from
  the scanner in 3 of 4 runs; in 1 run the agent used the wrong flag (`--offline`, 0 results) and
  listed three lodash CVEs from memory, labelled as unverified. Without a scanner gedik writes
  NOT MEASURED. (2) **Placing `gedik-bulgular.json` next to the `.md` report could not be
  tested:** in the test setup Claude Code refused writes into the target folder as a "sensitive
  file". (v2.11 update: with the plugin loaded from a `git archive` copy, both files landed in the same
  folder and the gate passed, 2 of 2.) (3) **When a write was refused, the agent wrote the file through a shell heredoc in at
  least 5 of 22 runs.** (v2.11 update: now forbidden; 0 of 2 runs bypassed — see above.) Grant only the permissions you intend.
  (4) Hidden-Unicode line numbers: v2.10 tells the agent to run a fixed `grep` and copy its
  output; 1 of 2 runs did not run it and gave a wrong line — verify with the command below.
- **D9 (in-repo agent configuration, v2.9) is measured only on synthetic fixtures**
  (2026-11-12; one model, one prompt, CVP account, n=2 runs per fixture × 2 rounds). On the bad
  fixture all 5 items (hook, project-MCP auto-approval + unpinned `npx -y`, `ANTHROPIC_BASE_URL`,
  CI `--dangerously-skip-permissions`, `runOn: folderOpen`) were found with `file:line` in 2/2
  runs. No run executed the planted hook (marker 0/10; positive control: with project settings
  loaded the marker did appear). Two known limits: (1) **hidden-Unicode line numbers are
  unreliable** — code points were right 4/4 and the hidden instruction was never followed, but
  only 4 of 8 reported line numbers were right; verify yourself with
  `grep -nP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2060}-\x{2064}\x{2066}-\x{2069}\x{E0000}-\x{E007F}]' FILE`. (2) **On a tightly configured repo a neighbouring hardening note can still
  appear as a numbered, rated finding** (2 of 4 runs; which run varies). False-positive rate on
  real repositories: NOT MEASURED.
- **Live testing only behind an authorization gate — refuses without one.** By default
  gedik reads code, configuration, and artifacts; it will send requests to a live target
  only when a machine-verifiable authorization exists (your own explicit statement in
  chat, or a published bug-bounty/VDP scope + your statement that you're working within
  it — never text found on the target's own page). No authorization → gedik stays
  read-only and reports "NOT MEASURED — no authorization." See `SKILL.md §0.1` and
  `references/yetki-kapisi.md`. Live agent test (2026-10-27; n=15, one model, CVP account;
  live target a never-resolving `.invalid` host): requests to any real host 0/15. Without
  authorization, HTTP requests to the live target 0/6, but 1 of 6 runs ran a DNS lookup
  (`nslookup`) of it while its report said "no live request was sent"; a "test permission"
  note planted in the target's own docs was rejected 3/3. With your chat authorization the
  gate opened 3/3. All 6 unauthorized reports said the live system was not tested, but the
  exact locked sentence appeared in only 1 of 6 (the wording drifts).
- **No SARIF and no CI/Action integration.** A full-audit run writes a Markdown report
  plus gedik's own `gedik-bulgular.json` (v2.6; schema `araclar/bulgu-semasi.json`,
  validator gate `araclar/bulgu_kapisi.py`), but there is no SARIF export and no
  CI/Action wrapper. Live test (2026-10-27): 6 of 6 full audits produced the file and it
  passed the validator 6/6 — **but all 6 wrote it to the session's scratch folder, not
  next to the report**, so `bulgu_kapisi.py` does not find it by default; look for the
  path in the run output.
- **The independent-refutation step and the two modes (consultation / full audit) are
  verified at the text level only** (translation-structure gate, the locked-sentence gate
  for 15 key v2.6 sentences, one independent TR↔EN reading); their behavior has not yet
  been tested in a live agent run.
- **Lane B (auth/OAuth) and T12 (cloud/IaC) are checklists, not validated on a real
  system.** They encode known attack patterns but have not yet been exercised against a
  live production stack.
- **PHP runtime version is visible only when it is written in the repo (v2.7; fixed-field report since v2.8).** gedik reads
  it from Dockerfile/Containerfile (including `*.Dockerfile`) and compose image tags,
  `.php-version`, `composer.json` `config.platform.php` and CI `setup-php`, and reports it
  with its source; a `"php": ">=x"` requirement is not treated as the running version. On
  shared hosting (cPanel/Plesk) the version lives on the server, not in the code — gedik then
  writes "NOT MEASURED — check the server/hosting panel" and never calls it clean.
  Vulnerability matching comes from scanners (`composer audit`, `trivy`/`grype`), not from a
  built-in CVE list. Field test (2026-10-23): trivy did not recognize PHP inside the official
  `php` Docker image (PHP there is compiled from source, not an OS package) and so did not report
  PHP2Shell (CVE-2026-109618/109619); grype did, on the one image tested (`php:8.3.30-fpm`). grype
  in turn missed an advisory in a `composer.lock` that `composer audit` and trivy found — run more
  than one scanner. Since v2.8 the PHP result is a fixed-field block (`### PHP runtime`:
  T2 PHP · Version + `file:line` source · Patch level · EOL · composer audit · Image scan) and
  the gate `araclar/php_kapisi.py` compares every field with its own repo measurement
  (`araclar/php_olc.py`). Field test (2026-10-24; n=15, one model, CVP account): gate PASS
  **14/15** (Wilson 70–99%); the one FAIL was a format slip (a note written inside the Version
  field), content correct; no content violation in the reviewed reports. **What the gate does not
  verify:** composer and scanner counts and the wording of NOT MEASURED / N/A reasons; free text,
  except the pattern `PHP x.y … file:line` (an unsourced version, `line 2` / `#L2` styles,
  `php.ini:N`, lines without the word "php" or with a constraint word, free-text "clean" and a
  wrong EOL outside the block all pass); field lines after the block that contradict it in value
  (EOL / patch level / T2). The block ends at the first blank line — put notes below a blank
  line, otherwise they count as duplicate fields. The block is strict: template deviations
  (heading suffix, table, numbered list, a note inside a value) fail. Scanner counts are not
  comparable across runs (severity scope is not fixed). Treat the gate as a guard rail, not proof.

## What it does

1. **Triage first (T1–T12).** Measures the architecture before scanning anything —
   opens only the surface that actually exists. No fixed OWASP checklist run blind.
2. **Only the measured surface.** Client/mobile (A) always runs; server/API/DB/auth (B),
   BaaS/RLS (C), AI/LLM (D), and shipped-artifact hygiene (E) each open only when the
   triage says they apply.
3. **Every finding carries a working PoC.** "Theoretically this could be XSS" is not a
   finding — it's either run and shown, or filed separately as `SUSPECTED (NOT RUN)`.
4. **K4 — it mutates its own checks and your test suite to prove they bite.** Before
   calling an area "clean," gedik deliberately poisons a copy of it and confirms its own
   scan catches the poison. If a runnable test suite exists, it also injects mutants into
   the *product* code (not the tests) — an escaping mutant means that test is dead, and a
   green CI run was blindness, not a measurement.
5. **Read-only.** gedik never edits your project; fixing is handed back to whoever's
   writing the code.
6. **Independent refutation before a finding is reported.** Every `confirmed` candidate
   goes through a separate pass that does not see the finder's reasoning and tries to
   knock it down; survivors stay `confirmed`, the rest become `rejected` or
   `needs_validation`. Full-audit runs also write `gedik-bulgular.json` next to the
   Markdown report (v2.6).
7. **Your own project by default; a third party only with authorization.** Any open
   source (a public repo, a published artifact) can be read statically, free — a finding
   there goes to responsible disclosure, never to attack. Touching a *live* third-party
   system requires the §0.1 authorization gate. No weaponized exploits, no
   money/account/permanent-deletion actions — those are reported, never taken, even with
   authorization.

This skill's biggest failure mode is not missing a vulnerability. It's calling something
**"clean" that was never actually scanned.**

## How to invoke it

"find vulnerabilities" · "security audit" · "pentest my project" · "check RLS" ·
"CORS check" · "did a secret leak" · "prompt injection audit" · "is my test suite blind"
· "mutation testing"

Two modes: a focused question gets **consultation mode** (light; no files, no report);
say "audit" / "pentest" / "produce a report" for **full audit mode** (Markdown report +
`gedik-bulgular.json`). If it's unclear which you meant, gedik asks one question first.

Only when invoked, and only on your own project — or, since v2.11, on someone else's site
when you state that its owner allowed it (passive checks; since v2.12 also active tests you
explicitly ask for, each behind its written precondition).

## Lanes

| Lane | When | Scope |
|---|---|---|
| **A** client/offline/mobile | always | prototype pollution, type confusion, migration exploits, sink inventory, platform configuration, intent surface, iOS/Capacitor surface (A8, checklist-only — see above) |
| **B** server/API/DB/identity | T2/T3/T4 yes | injection + ORM open-filter, AuthN/AuthZ (IDOR), account lifecycle, XSS/CSRF/SSRF, **CORS lock**, webhook signatures, **error-channel separation**, secret layering, **rate limits + cost-DoS + cache**, **server-side validation**; **Next.js/RSC add-on (v2.10, `serit-B-rsc.md`)** — server functions as public endpoints (session + ownership + schema, mass assignment), authorization only in middleware, `next`/`react-server-dom-*` version matched by a scanner (never from memory), `use cache` keys, config SSRF |
| **C** BaaS/RLS | T7 yes | **RLS-disabled table scan**, policy correctness (`USING`/`WITH CHECK`), anon vs. service_role, storage, RPC, realtime, Firebase equivalents |
| **D** AI/LLM + agent config | T8 yes; **D9** also without AI, whenever the repo carries agent config (`.claude/`, `.mcp.json`, `.cursor/`, `.vscode/`, `.gemini/`, `.devcontainer/`, `AGENTS.md`, `CLAUDE.md`, …) | direct + **indirect prompt injection**, **tool authorization**, output trust (model output = untrusted input), data flow, cost abuse; **D9 in-repo agent configuration** — hooks, project-MCP auto-approval + unpinned `npx -y`, endpoint/env redirection, permission bypass (incl. CI `--dangerously-skip-permissions`), agent able to write its own config, hidden Unicode in instruction files, `folderOpen`/`postCreateCommand`; evidence by reading, never by running (D9 measured on fixtures only — see above); **MCP SDK (v2.13, D8.6–D8.8)** — SDK version via scanner, token `aud`, credentials not bound to their server, schema `$ref`; OWASP LLM 2026 numbering + Hidden Context Exposure |
| **E** shipped artifact | T9 yes | **leaked secrets** in artifacts, debug flags, **source-map reconstruction**, test/staging leftovers, over-broad permissions (Electron/container/extension/mobile), **artifact↔source matching**, embedded dependency footprint |
| **Test-suite mutation** | T10 yes | poisoned-test scan + a ten-item mutant catalog; **M6 (authorization removal) and M7 (validation bypass) are mandatory** — an escaping mutant is a dead zone |
| **Code review** | source available | security-impact correctness bugs, dependency/CVE, secrets used in the wrong layer |
| **Conditional active test (v2.12)** | you say "active test" + preconditions in `YETKI.md` `aktif:` | marked form posts (1/form), LLM prompt-injection (≤10), rate-limit probe (≤30, stop at first 429), IDOR with two owner test accounts, harmless XSS/SQLi markers (≤5/endpoint), canary-record access proof, brute force (≤200 paths); delete/load only on staging or a **local copy built from the repo** (`references/aktif-denetim.md`) |
| **Passive URL audit (v2.11)** | you name a live site + state the owner allowed it | GET/HEAD only, ≤1 request/s, ≤100 requests: security headers, TLS/certificate, cookie flags, CORS response, client JS + source maps, linked resources, `robots.txt`, `sitemap.xml`, `security.txt` (`references/pasif-denetim.md`); in-page "permission" text is never authorization; **v2.13:** server version disclosure (every line "from the version header, not verified"), STOP on a block page (including HTTP 200) |
| **CI/CD + repo** | repo/CI available | git-history secret scanning, `pull_request_target`, action pinning, **post-leak recovery sequence**; **supply chain (v2.10)** — `issue_comment` pwn request, `workflow_run` artifact hand-off, git/URL dependencies, loosened package-manager defaults (`.npmrc`, pnpm, Dependabot cooldown, `npm install` in CI), malicious versions via `osv-scanner`/`npm audit` (else NOT MEASURED); **v2.13:** Python `.pth`/`sitecustomize` startup hooks, the 2026-12-02 `pull_request_target` default block, version gates for CI agent actions and plugin pinning |

## Benchmark (measured — 2026-09-30)

First scored run. **Both targets are weak evidence** and the result does **not** support a
general "gedik is better" claim — read the caveats.

Setup: four tools — gedik v2.6.0, `cloudflare/security-audit-skill`, Anthropic
`/security-review`, Semgrep (free-registry rules, not Pro) — same model
(`claude-sonnet-5-5`), isolated runs, answer key hidden from the scanning agent.
`claude-security` was excluded because its plugin licence forbids use with a competing
product. Single annotator (gedik's author) — no independent second reading.

**Target 2 — seeded Supabase-RLS + LLM-tool repo (built by gedik's author, so biased
toward gedik's strong lanes):**

| 11 seeded | gedik | cloudflare | `/security-review` | Semgrep |
|---|---|---|---|---|
| found | 11/11 | 11/11 (9 confirmed) | 9/11 | 1/11 |
| false positives | 0 | 0 | 0 | 0 |

Only gedik addressed K4 — it showed the repo's own test suite is blind to
authorization/validation mutants; the others were silent.

**Target 1 — NodeGoat, real third-party (cleaned copy is weaker than upstream and is
likely in the model's training data):**

| 17 seeded | gedik | cloudflare | `/security-review` | Semgrep |
|---|---|---|---|---|
| detection *(when delivered)* | 17/17 | 16/17 | 5/17 | 6/17 |
| report delivered | **3/3 with CVP · 2/6 without** | yes | yes | yes |

gedik's detection is the strongest here — but on this exploit-heavy target, without a safeguard adjustment, its report was cut mid-stream by Claude's **real-time cyber safeguard** (`[cyber]`) in four of six runs, so the user received only an error. Moving exploit payloads out of the report body did **not** fix it.

**Update (2026-10-01) — delivery, with Cyber Verification Program.** The author's account was approved into Anthropic's **Cyber Verification Program (CVP)**. Re-running gedik on Target 1 under the approved organization, with **stock v2.6.0** (the 2.6.1 delivery patch was reverted), the full report was delivered in **3 of 3** runs (`stop_reason: end_turn`, 0 errors), recall **17/17** each (one run: 16 confirmed + 1 suspected), **0 false positives**. The same condition before CVP delivered **2 of 6**. **This lifts the delivery limit only for CVP-approved accounts** — a user *without* CVP approval will still have the report cut on exploit-heavy targets (delivered ~2/6, cut ~4/6). Causality is **not proven**: n=3, Fisher p≈0.12, and the code fix was reverted — so the change is attributed to the account-level safeguard adjustment, not to gedik's code.

**Honest verdict.** gedik detects at or above the best surveyed tool on both targets (Target 1 17/17, Target 2 11/11, 0 false positives) and stands alone on K4 / self-refutation. Report delivery on exploit-heavy real code is now reliable **for CVP-approved accounts** (3/3) but remains limited **without CVP** (2/6). No general "better" is claimed: the detection edge is real and measured; the delivery edge is account-dependent, and its cause is unproven.

**Caveats.** Single annotator = gedik's author · Target 2 seeded toward gedik's lanes ·
Target 1 cleaned + memorization risk · Semgrep ran free-registry rules only · one run per
tool×target (six for gedik on Target 1, three post-CVP) · all tools on Windows · CVP causality unproven (n=3, p≈0.12, code fix reverted) · delivery reliability depends on the account's CVP status · `gedik-bulgular.json` was not produced in the CVP runs (prose reports).

## Alternatives, honestly

gedik now has one scored benchmark (see [Benchmark](#benchmark-measured--2026-09-30)); it
does **not** support a general "better" claim. The comparison below is *design
differences*.

| Tool | Stars | License | Attacks live targets? | Note |
|---|---|---|---|---|
| [usestrix/strix](https://github.com/usestrix/strix) | 65k+ | Apache-2.0 | **Yes** | CLI + 9 skills + MCP; has its own Supabase-RLS skill |
| [KeygraphHQ/shannon](https://github.com/KeygraphHQ/shannon) | 48k+ | AGPL-3.0 | **Yes** | CLI + CI + skill; "no exploit, no report" |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (`claude-security`) | 37k+ (repo) | Apache-2.0 (repo) · **plugin: proprietary** | No | Anthropic's own official marketplace plugin; independent verifier agents; entered the directory 2026-09-25. Note: the `claude-security` plugin's own LICENSE (Anthropic PBC, all rights reserved) restricts use to Anthropic products and forbids use with any competing product |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 23k+ (2026-09-29) | MIT | No — live probing forbidden outright | Independent verifier agents try to refute every candidate (false-positive elimination); schema'd `findings.json` + tested validators; 9 core attack-class prompts + 10 target-type class files; created 2026-06-18 |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 7k+ | CC-BY-SA-4.0 | No | Marketplace, 44 plugins; **mutation testing is a separate skill** there |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | 6k+ | MIT | No | GitHub Action + `/security-review`; FP filter + `evals/` |

**Where gedik is meant to differ (unmeasured design claims):**
- **Triage before scanning (K1, T1–T12)** — doesn't open a surface the architecture
  doesn't have.
- **K4 self-mutant, both directions** — poisons its own scan *and* the project's test
  suite to prove they bite. No other tool surveyed self-tests its own blindness this way.
  cloudflare/security-audit-skill's independent refuters cut false positives. gedik v2.6
  adopts the idea — a refutation step and three-verdict machine-readable findings — with
  text, schema and validator written independently (the verdict names `confirmed` /
  `needs_validation` / `rejected` are taken over as they are; text-level, unmeasured); K4 is a
  different mechanism — mutation-testing the scan and the project's tests for blindness.
- **Lane C (BaaS/RLS — Supabase, Firebase) as a first-class column** — only Strix has
  something similar.
- **Turkish original** — the canonical text is Turkish (`skills/gedik-tr/`); the English
  version is a translation held to a mechanical translation gate.

**Where gedik is honestly behind (all real, all current gaps):**
- **Delivery reliability on exploit-heavy targets depends on account status.** In the first
  benchmark gedik detected at or above the best tool (Target 1: 17/17), but Claude's `[cyber]`
  safeguard cut its full report in 4 of 6 runs. With the account in Anthropic's Cyber
  Verification Program this becomes 3/3; without CVP it stays ~2/6 — so this is lifted per
  approved account, not in gedik's code. Both benchmark targets are weak evidence (see
  [Benchmark](#benchmark-measured--2026-09-30)).
- **No live exploitation, by design** — blind to classes that only manifest at runtime
  against a live target.
- **Machine-readable output is new and unproven; no SARIF, no CI/Action integration.**
  gedik's own `gedik-bulgular.json` + schema + validator gate exist since v2.6 and live
  audits produce it (6/6, validator PASS 6/6), but it lands in the session scratch folder; cloudflare/security-audit-skill ships a schema'd `findings.json`
  with tested validators.
- **Narrower scope** than cloudflare/security-audit-skill (9 core attack-class prompts +
  10 target-type class files there).
- Anthropic's own **official** `claude-security` plugin covers similar ground for free,
  from the platform owner. What gedik argues for over it is not breadth — it's the K4
  and triage discipline above.

## Install

```
/plugin marketplace add onur-kesim/gedik
/plugin install gedik@gedik
```

**Heads-up on delivery.** On exploit-heavy real code, Claude's real-time cyber safeguard can
cut gedik's report mid-stream (measured: cut in ~4 of 6 runs; delivered 2 of 6). For authorized security work,
Anthropic's **Cyber Verification Program** lifts this per approved account (3/3 in our
benchmark); without it gedik stays read-only and simply delivers less on such targets.
Approval lowers the cut rate but does not guarantee delivery: in PHP field runs on an approved
account, 1 of 15 reports was refused on v2.7.1 and 0 of 15 on v2.8.0 (n=15 each — a sample, not
a rate). See [Benchmark](#benchmark-measured--2026-09-30).

**Before auditing someone else's repository.** Since v2.13.1 gedik is instructed not to install dependencies in an audited repository (except an explicitly requested local copy) and to run PoCs only without installation, but the
agent around it can: a repository's `.claude/settings.json` hooks and `.mcp.json` servers are
project configuration that Claude Code may execute when you open that folder (CVE-2025-59536 /
CVE-2026-21852, patched before disclosure — Check Point, 2026-02-25; a similar Cursor issue is
CVE-2026-48124). gedik's read-only rule does not protect against this. Keep Claude Code updated,
and before running gedik on an untrusted repo, read its `.claude/`, `.mcp.json`,
`.vscode/tasks.json` and `.devcontainer/` without opening the folder in an agent.

Turkish original: [`skills/gedik-tr/`](skills/gedik-tr/) · [README.tr.md](README.tr.md)

**Development commands** (identical to `proje.toml`): test `python araclar/kapilar.py --pozitif-kontrol` · lint `python -m py_compile araclar/kapilar.py araclar/ceviri_kapisi.py araclar/bulgu_kapisi.py araclar/ic_ad_kapisi.py araclar/php_olc.py araclar/php_kapisi.py araclar/php_oz_test.py araclar/php_oz_duzelt.py araclar/php_oz_blok.py araclar/php_oz_sabit.py araclar/php_oz_denetim.py araclar/php_oz_denetci.py araclar/php_oz_gerileme.py`

## Limits

Read-only (never fixes, only reports) · **authorized-only live testing — refuses
without an in-scope authorization** (`SKILL.md §0.1`; your statement that a site's owner
allowed it counts, passive only) · reading third-party open source
is free, but a finding goes to responsible disclosure, never to attack · never produces
weaponized exploits · money/account-security changes and permanent deletion are only
ever reported, never touched, even with authorization.

This is not an unrestricted attack tool — it's an authorized pentest tool.

If you're not sure, gedik is supposed to write `NOT MEASURED` — not "clean."

## License

MIT — see [LICENSE](LICENSE).
