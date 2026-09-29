# TEST SUITE MUTATION — is there a gate, does it bite

This file is K4 ('test your own gate') **applied to the project**. It is not a new doctrine.

**Reason for existing:** The test suite is a gate, and when CI is green it is called "passed."
But green can show two different things at once: green because the product is correct, or
green **because the test is blind**. The second is more dangerous than the flaw itself — it
makes an unmeasured area look measured and produces false confidence. This is gedik's axis:
*what isn't measured isn't assumed clean.*

**When it runs:** When there is access to the source code and a runnable test suite.
If the test suite **doesn't exist**, mutation isn't run; the finding is directly: "no test
gate" — its severity is set by the security surface. This is not a NOT MEASURED, it is a
measured NONE.

---

## 0. PRECONDITION — clean run

1. Find the test command (`package.json` scripts, `pytest.ini`, `Makefile`, CI file) and run
   it. Record the number passed / failed / skipped **and the duration**.
2. If the suite is not GREEN on a clean run, mutation is meaningless — in a suite that's
   already red, you cannot tell whether a mutant was killed. Finding: *"test suite is red or
   flaky — the gate isn't even shut to begin with"*.
3. The duration record is the budget: mutation ≈ N mutants × suite duration. Calculate from
   this how many mutants you can run, and **state it in the report**.

---

## 1. FREE SCAN FIRST — poisoned tests (no mutant needed)

The following are dead without needing mutation. Produce a full inventory and **give a
count**:

- **Tautology:** `assert True`, `expect(true).toBe(true)`, `assert 1 == 1`, empty
  `assertDoesNotThrow`
- **Assert-less test:** a test whose body contains no assert/expect at all — it calls, but
  never checks the result
- **Silenced test:** `skip`, `xit`, `xfail`, `@Ignore`, `#[ignore]` — and the most dangerous
  of all, `.only`/`fit`/`fdescribe`: it **silently** shuts off the other tests, and the suite
  still looks green
- **Swallowed error:** `try/except: pass`, `catch {}` in the test body
- **Blind snapshot:** if the CI command has `-u` / `--update-snapshots`, the snapshot test
  isn't verifying anything — the expectation is rewritten on every run
- **Mock replacing the target:** the very function under test is mocked — the test is testing
  the mock
- **Loose expectation:** `toBeDefined()`, `assertIsNotNone`, `assertTrue(x is not None)` used
  alone
- **Scope exclusion:** the `exclude`/`ignore` list in the coverage configuration. If a
  security-relevant file is on it, that is a finding in itself

> **K3 warning:** This scan is pattern matching and is not enough to declare "none found."
> The inventory is produced in full and a count is given. "Clean" is not written; what's
> written is *"this many found, in these patterns."*

---

## 2. MUTANT CATALOG — the mutant is injected into PRODUCT code, not the test

Breaking the test measures nothing. The mutant is made in the product code, **one at a
time**, and only in the working copy (gedik is read-only — no file in the target project is
modified).

| # | Mutant | Example | What it measures |
|---|---|---|---|
| M1 | Condition inversion | `if (a)` → `if (!a)` | Whether the branch is tested at all |
| M2 | Boundary shift | `<=` → `<` · `>` → `>=` | Whether there's a boundary-value test (off-by-one) |
| M3 | Return-value pinning | `return f(x)` → `return null` / `0` / `[]` | Whether the return value is verified |
| M4 | Side-effect removal | the record/send/write line is deleted | Whether the effect is verified, or only "didn't throw" |
| M5 | Error swallowing | `throw` / `raise` → `pass` | Whether the error path is tested |
| M6 | **Authorization check removal** | `if (!user.canEdit) return 403` is deleted | Whether there's an authorization test — **mandatory mutant** |
| M7 | **Validation bypass** | input validation / schema check is removed | Whether there's a bad-input test — **mandatory mutant** |
| M8 | Logical operator | `&&` → `||` | Whether every leg of the compound condition is tested |
| M9 | Order/index shift | `i` → `i+1` · sort order reversed | Whether there's an ordering/pagination test |
| M10 | Threshold shift | timeout, rate limit, retry count ×10 | Whether thresholds are tested |

**Selection rule:** The mutant is injected not into a random file, but into **the path
touched by untrusted input** (SKILL.md §2, T5 inventory). Random selection wastes time.

**M6 and M7 are mandatory.** gedik's axis is authorization and adversarial input; if these
two mutants escape, the test suite is blind from gedik's standpoint, and this result goes
into the report's verdict.

---

## 3. RUN

For each mutant: inject → run the suite → record the result → revert.

- **RED** = mutant killed, test alive ✓
- **GREEN** = mutant escaped → that behavior isn't tested → **DEAD ZONE**
- **Doesn't compile / errors** = mutant is invalid; it's dropped from the score's denominator
  and noted in the report

**False-positive check:** If a mutant escaped, first ask — is this code called at all? If it
isn't, the finding is not "dead test" but **"dead code"**; it's written to a separate class
(INFO) and the test suite isn't blamed.

**Time limit:** A mutant that couldn't be run is **NOT MEASURED**, it is not counted as
killed. The report states "10 mutants planned, 6 run."

---

## 4. IF A TOOL EXISTS, USE THE TOOL

Manual mutation is a **sample**. If the language has a built-in tool, run it and state so in
the report:

Python `mutmut` / `cosmic-ray` · JS-TS `Stryker` · Java `PIT` · C# `Stryker.NET` ·
Ruby `mutant` · Go `go-mutesting` · Rust `cargo-mutants` · PHP `Infection`

If the tool was run, state its score. If not, write **"manual sample, N mutants"**.
Don't report the tool's score and the manual sample as if they were the same number.

---

## 5. SEVERITY — based on the escaped mutant's behavior

| Escaped mutant | Severity |
|---|---|
| M6 authorization check · M7 input validation | **HIGH** — an authorization/validation regression passes silently |
| M4 side effect · M5 error swallowing, on a security-relevant path | **MEDIUM** |
| M10 threshold (rate limit, timeout, retry) | **MEDIUM** — a cost/DoS regression is invisible |
| Display, formatting, logging | **INFO** |

**The score alone is not a finding.** "Mutation score X%" is not reported without stating
which behavior is dead.

---

## 6. REPORT LINE

```
G-n · TEST KAPISI KÖR — <dosya>:<fonksiyon>
  mutant   : M6 (yetki kontrolü kaldırıldı)
  komut    : <test komutu>
  sonuç    : 142 geçti / 0 kaldı  → mutant KAÇTI
  anlamı   : bu yetki kontrolünün kaldırılması hiçbir testi kırmıyor
  şiddet   : YÜKSEK
  yama     : <yazılması gereken test, tek cümle>
```

Section summary: `mutation: 10 planned · 8 run · 6 killed · 2 escaped · 2 NOT MEASURED`

---

## LIMITS

- No file in the target project is modified; the mutant lives only in the working copy
  (SKILL.md §6).
- Mutation is not a **coverage** measure. High line coverage is not evidence unless the
  mutant is actually killed — that is exactly why this section exists.
- **The sentence "test suite is sound" is not written.** What's written: *"M of N mutants
  were killed, here's what escaped."*
