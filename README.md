# gedik

**"Find it so it can be closed."** gedik breaks your own projects like an attacker and
lists the breaches. Output: findings numbered `G-1`, `G-2`… each with a working PoC and
a suggested patch. ("gedik" is Turkish for *a breach in a fortress wall.*)

## What's not delivered yet

- **No benchmark numbers.** gedik has never been run against a scored target. No "better
  than X" claim is made anywhere in this repo until one exists — see
  [Alternatives, honestly](#alternatives-honestly) below.
- **iOS lane (A8) is a checklist, not validated on a real system.** It has not yet been
  run against a real iOS / Capacitor-iOS app.
- **No live exploitation, by design.** gedik reads code, configuration, and artifacts;
  it does not send requests to third-party live systems (see Scope Lock in `SKILL.md §0`).
- **No machine-readable output.** Reports are Markdown only — no SARIF/JSON, no CI/Action
  integration.
- **Lane B (auth/OAuth) and T12 (cloud/IaC) are checklists, not validated on a real
  system.** They encode known attack patterns but have not yet been exercised against a
  live production stack.

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
6. **Your own project only.** No third-party live systems, no weaponized exploits, no
   money/account/permanent-deletion actions — those are reported, never taken.

This skill's biggest failure mode is not missing a vulnerability. It's calling something
**"clean" that was never actually scanned.**

## How to invoke it

"find vulnerabilities" · "security audit" · "pentest my project" · "check RLS" ·
"CORS check" · "did a secret leak" · "prompt injection audit" · "is my test suite blind"
· "mutation testing"

Only on your own project, and only when invoked.

## Lanes

| Lane | When | Scope |
|---|---|---|
| **A** client/offline/mobile | always | prototype pollution, type confusion, migration exploits, sink inventory, platform configuration, intent surface, iOS/Capacitor surface (A8, checklist-only — see above) |
| **B** server/API/DB/identity | T2/T3/T4 yes | injection + ORM open-filter, AuthN/AuthZ (IDOR), account lifecycle, XSS/CSRF/SSRF, **CORS lock**, webhook signatures, **error-channel separation**, secret layering, **rate limits + cost-DoS + cache**, **server-side validation** |
| **C** BaaS/RLS | T7 yes | **RLS-disabled table scan**, policy correctness (`USING`/`WITH CHECK`), anon vs. service_role, storage, RPC, realtime, Firebase equivalents |
| **D** AI/LLM | T8 yes | direct + **indirect prompt injection**, **tool authorization**, output trust (model output = untrusted input), data flow, cost abuse |
| **E** shipped artifact | T9 yes | **leaked secrets** in artifacts, debug flags, **source-map reconstruction**, test/staging leftovers, over-broad permissions (Electron/container/extension/mobile), **artifact↔source matching**, embedded dependency footprint |
| **Test-suite mutation** | T10 yes | poisoned-test scan + a ten-item mutant catalog; **M6 (authorization removal) and M7 (validation bypass) are mandatory** — an escaping mutant is a dead zone |
| **Code review** | source available | security-impact correctness bugs, dependency/CVE, secrets used in the wrong layer |
| **CI/CD + repo** | repo/CI available | git-history secret scanning, `pull_request_target`, action pinning, **post-leak recovery sequence** |

## Alternatives, honestly

gedik has never been benchmarked. The comparison below is *design differences*, not
measured superiority — treat every "ahead" claim as a hypothesis, not a result.

| Tool | Stars | License | Attacks live targets? | Note |
|---|---|---|---|---|
| [usestrix/strix](https://github.com/usestrix/strix) | 65k+ | Apache-2.0 | **Yes** | CLI + 9 skills + MCP; has its own Supabase-RLS skill |
| [KeygraphHQ/shannon](https://github.com/KeygraphHQ/shannon) | 48k+ | AGPL-3.0 | **Yes** | CLI + CI + skill; "no exploit, no report" |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (`claude-security`) | 37k+ (repo) | Apache-2.0 | No | Anthropic's own official marketplace plugin; independent verifier agents; entered the directory 2026-09-25 |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 7k+ | CC-BY-SA-4.0 | No | Marketplace, 44 plugins; **mutation testing is a separate skill** there |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | 6k+ | MIT | No | GitHub Action + `/security-review`; FP filter + `evals/` |

**Where gedik is meant to differ (unmeasured design claims):**
- **Triage before scanning (K1, T1–T12)** — doesn't open a surface the architecture
  doesn't have.
- **K4 self-mutant, both directions** — poisons its own scan *and* the project's test
  suite to prove they bite. No other tool surveyed self-tests its own blindness this way.
- **Lane C (BaaS/RLS) as a first-class column** — only Strix has something similar.

**Where gedik is honestly behind (all real, all current gaps):**
- **No scored benchmark.** Anthropic's and [agamm/claude-code-owasp](https://github.com/agamm/claude-code-owasp)'s
  tools ship `evals/`; Shannon and PentestGPT report numbers. This is the biggest gap.
- **No live exploitation, by design** — blind to classes that only manifest at runtime
  against a live target.
- **No machine-readable output** (SARIF/JSON), no CI/Action integration.
- Anthropic's own **official** `claude-security` plugin covers similar ground for free,
  from the platform owner. What gedik argues for over it is not breadth — it's the K4
  and triage discipline above.

## Install

```
/plugin marketplace add onur-kesim/gedik
/plugin install gedik@gedik
```

Turkish original: [`skills/gedik-tr/`](skills/gedik-tr/) · [README.tr.md](README.tr.md)

## Limits

Read-only (never fixes, only reports) · your own project only · never sends requests to
third-party live systems · never produces weaponized exploits · money/account-security
changes and permanent deletion are only ever reported, never touched.

If you're not sure, gedik is supposed to write `NOT MEASURED` — not "clean."

## License

MIT — see [LICENSE](LICENSE).
