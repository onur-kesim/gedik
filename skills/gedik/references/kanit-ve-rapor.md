# Evidence, Self-Mutant, and Report

---

## 1. EVIDENCE RULE (K2)

Every finding **mandatorily** carries three parts:

1. **Reproduction:** verbatim input (copyable), command, or sequence of steps.
2. **Observed result:** what happened — screen, console output, value, exit code.
3. **Evidence type:** one of the three tags below.

| Tag | Meaning |
|---|---|
| `RAN` | Actually executed the payload, measured the result |
| `STATIC` | Read and derived from the code, did not execute — the logic chain is written in the report |
| `NOT MEASURED` | Could not access/run it. **Why** and **how to measure it** are written |

`NOT MEASURED` is not a failure, it is honesty. **Writing "clean" instead of
`NOT MEASURED` is this skill's one unforgivable mistake.**

### Harmless marker
The evidence payload never causes real harm. The marker to use:
```
window.__ZAFIYET_KANITI = 1
```
Measurement: is this variable defined after the payload? If defined, injection occurred.
A payload that exfiltrates data, deletes files, or reaches the network is NEVER written.

---

## 2. SELF-MUTANT (K4) — test your own gate

Before calling an area "clean," prove that the scan **actually bites** in that area.
Recipe:

1. Take a **temporary copy** of the target (do not touch the actual project).
2. Inject a known vulnerability into the copy. Examples:
   - Remove escaping from a sink: `el.innerHTML = esc(x)` → `el.innerHTML = x`
   - Strip the filter: remove the `continue` line that drops the unknown key
   - Add `android:debuggable="true"` to the manifest
   - Add a `postinstall` script to `package.json`
   - Convert the query to concatenation (Lane B)
3. Run **the same scan** on the dirty copy. It must catch it.
4. **Also run it on the clean version.** It must not catch anything (no false positive).
5. Write both results into the report.

| Mutant | Location | On dirty copy | On clean version | Verdict |
|---|---|---|---|---|
| M-1 | ... | CAUGHT | clean | scan BITES |
| M-2 | ... | ESCAPED | — | **scan BLIND → that area cannot be called "clean"** |

**At least two mutants** are mandatory; one on the input side, one on the
configuration/sink side. If a mutant escapes: the related item becomes `NOT MEASURED`,
not "clean."

### 2.1 BEFORE the mutant: origin tracing (skipping this step makes the mutant give false confidence)

A mutant shows that the **single line** you mutated is covered. It does not show that
your inventory is **complete**. That is why the order is non-negotiable:

1. **Inventory:** list every sink.
2. **Origin tracing:** trace the variable each sink prints **backward** — where does it
   come from? Is it generated content (rng/generator/fixed template), or does it come
   from `load()` / a repository / import / network / file? Do the tracing not by looking
   at the variable name, but by **reading the assignment chain**.
3. **Mutant:** only for the ones that came out "fed by untrusted input" in (2), each one
   separately.

Skipping step (2) and saying "I mutated the most obvious sink, the class is closed" is
this skill's known failure mode — in a real audit exactly this kind of sink slipped
through (a backed-up counter fed into an unescaped `innerHTML` template; the first
mutant was on a different line).

---

## 3. FALSE "CLEAN" TRAPS — do not write the report without reading

| Trap | Why it's wrong | The correct approach |
|---|---|---|
| "I didn't search for `eval`, there is none" | `new Function`, `setTimeout("...")`, `import()`, `Reflect` | Full sink inventory |
| "`esc()` exists, so no XSS" | Escaping varies by context; attribute/URL context differs | Read the sink's context |
| "Not in the selector/pattern text" | Text search is not proof of behavior (in this project it was WRONG once) | Measure the runtime |
| "ORM is used, no SQLi" | Every ORM has a raw-query escape hatch | Open every dynamic query |
| "No permission, no network" | `data:`/`intent:`/an external app is still a surface | Measure the scheme policy |
| "Pattern matched, a secret leaked" | Could be a placeholder | Open and read every match |
| "User does it to themselves, doesn't matter" | Can be induced via social engineering | Write the scenario separately |
| "I ran one tool, it said clean" | A single tool sees a single angle | Cross-validate with a second independent method |
| **"The mutant bit, that class is closed"** | **A mutant only proves the line you MUTATED; it does not prove the inventory is complete.** A sink missing from the inventory never gets mutated and slips through the gap | First **origin tracing** (§2.1), then a separate mutant for each untrusted-fed sink |

---

## 4. REPORT TEMPLATE

File name: `ZAFIYET_RAPORU_<proje>_<surum>.md`

```markdown
# ZAFİYET RAPORU — <proje> <sürüm>
> Tarih: <YYYY-AA-GG> · Denetleyen: gedik <gedik-sürümü> · Kapsam: kullanıcının kendi
> kod tabanı/artefaktı · Salt-okunur (düzeltme yapılmadı)

## 0. TRİYAJ (ölçülen mimari)
| # | Soru | Cevap | Neyle ölçüldü |
|---|---|---|---|
| T1 | Ağ var mı | ... | ... |
| T2 | Sunucu kodu | ... | ... |
| T3 | Veritabanı | ... | ... |
| T4 | Hesap/kimlik | ... | ... |
| T5 | Güvenilmeyen girdi yolları | N adet (aşağıda) | ... |
| T6 | Sır/imza malzemesi | ... | ... |

**Şerit kararı:** ...
**Yapısal olarak uygulanamayan sınıflar:** ... (tek satır, N/A listesi yazma)

## 1. YÜZEY ENVANTERİ
### 1.1 Güvenilmeyen girdi yolları
| # | Yol | Konum | Kim kontrol ediyor | Sanitize |
### 1.2 Çıktı sink'leri
| # | Sink | Konum | Beslendiği veri | Güvenilmeyen mi | Kaçış |

## 2. BULGULAR
### G-1 · [ŞİDDET] <tek cümlelik başlık>
- **Nerede:** dosya:satır
- **Tekrar üretim:** <birebir girdi/komut>
- **Gözlenen:** <ölçülen sonuç>
- **Etki:** <mimarinin izin verdiği tavana göre, şişirmesiz>
- **Yama:** <somut, uygulanabilir düzeltme>
- **Kanıt türü:** KOŞULDU / STATİK / ÖLÇÜLMEDİ
- **Doğrulayan:** alt-ajan / ayrı tur — bağımsız çürütme turunu yapan (JSON: `dogrulayan`)

### 2.1 ŞÜPHE (ÇALIŞTIRILMADI) — `needs_validation`, şiddet YOK
- **G-n · <başlık>** — çözülmemiş tek somut olgu: <...>

### 2.2 ÇÜRÜTÜLEN ADAYLAR — `rejected`
- **G-n · <başlık>** — elenme nedeni: <...> · doğrulayan: alt-ajan / ayrı tur

## 3. TEMİZ ÇIKANLAR (her biri neyle ölçüldü)
| Başlık | Sonuç | Ölçüm yöntemi |

## 4. ÖLÇÜLMEYENLER
| Başlık | Neden ölçülmedi | Nasıl ölçülür |

## 5. SELF-MUTANT SONUCU
| Mutant | Kirli kopya | Temiz sürüm | Karar |

## 6. KARAR
**GÜVENLİK AÇISINDAN YETERLİ** (kritik/yüksek bulgu yok, ölçülmeyen kritik başlık yok)
— veya —
**DÜZELT:** [G-1, G-3, ...] · **ÖNCE ÖLÇ:** [ölçülmeyen kritik başlıklar]

## 7. SONRAKİ TURA DEVREDİLENLER
- ...
```

### 4.1 `gedik-bulgular.json` — machine-readable output (full audit mode)

The `.md` report is primary and is for humans; the JSON does **not replace** it — it is
written next to it (same folder). Report files go to the output folder the user names (if
none, the session's output/scratch folder); they are not written into the target project's
source tree (SKILL.md §6). The schema and validator live in the `araclar/` folder at the
plugin root (`<plugin-root>/araclar/`; two directories above the skill folder): the schema is
`bulgu-semasi.json`, the validating gate is `bulgu_kapisi.py`
(`python <araclar-path>/bulgu_kapisi.py --dosya gedik-bulgular.json`). A file that does not match the
schema is not delivered. If the tool or Python is unreachable, apply the field dictionary by
hand and write "JSON not validated against the schema (NOT MEASURED)" in the delivery
message. There is NO SARIF or CI/Action output; this is only gedik's own JSON.

**Three verdicts** — they map onto gedik's own concepts; they are not new concepts:

| `hukum` | Meaning | Required fields | Forbidden fields |
|---|---|---|---|
| `confirmed` | a finding that satisfies K2 (with a PoC), having passed refutation | `siddet`, `etkilenen`, `poc_girdi`, `gozlenen`, `tekrar_uretim`, `yama`, `dogrulayan` | `cozulmemis_olgu`, `eleme_nedeni` |
| `needs_validation` | `SUSPECTED (NOT RUN)`: an uncertain hypothesis | `cozulmemis_olgu` (the single unresolved concrete fact) | `siddet`, `eleme_nedeni` |
| `rejected` | a candidate that was eliminated (refuted) | `eleme_nedeni` | `siddet`, `cozulmemis_olgu` |

`bulgu_id`, `serit` and `hukum` are mandatory on every record. A field that the table lists as
neither required nor forbidden is optional for that verdict (e.g. `etkilenen` on a
`needs_validation` record, `dogrulayan` on a `rejected` record); an unknown field is
rejected.

**Evidence type ↔ verdict:** `RAN` and `STATIC` → `confirmed` (for `STATIC`, `poc_girdi` carries
the exact input that would trigger it, `gozlenen` the result derived from the code,
`tekrar_uretim` the chain of logic). A candidate whose evidence type is `NOT MEASURED` →
`needs_validation` (`cozulmemis_olgu`: why it could not be measured). `NOT MEASURED` is not a
verdict; if the surface could not be measured at all, also write a `kapsam` row.

**Severity appears only on a `confirmed` record.** Values (the SKILL.md §4 criteria):
`KRITIK`, `YUKSEK`, `ORTA`, `DUSUK`, `BILGI` (CRITICAL, HIGH, MEDIUM, LOW, INFO) — in
JSON always this ASCII form.

Field dictionary (field names are the same in the TR and EN flows):
- `sema`: the constant `gedik-bulgular/1`. `bulgular`: the list of records (empty if there
  are no findings). `kapsam`: at least one row.
- `bulgu_id`: `G-n`, unique (one shared numbering across the three verdicts). `serit`:
  `A`, `B`, `C`, `D`, `E`, `TEST` (test suite mutation), `KOD` (code review), `CICD`
  (CI/CD and repository).
- `etkilenen`: the affected resource (file:line, table, endpoint, user/role). `poc_girdi`:
  the exact input or command. `gozlenen`: the measured result. `tekrar_uretim`: a single
  string; number the steps `1) 2) 3)`. `yama`: the narrowest suggested patch.
- `dogrulayan`: who ran the independent refutation round — `alt-ajan` (a separate
  sub-agent) or `ayri-tur` (the environment did not allow a sub-agent; a separate round
  that does not see the reasoning). `ayri-tur` is a weaker form of independence.
- `kapsam`: at most one `{yuzey, durum, sebep}` row per surface; `yuzey`: the same value
  set as `serit`; `durum`: `olculdu` | `olculmedi` (`sebep` mandatory) | `mimari-yok`
  (`sebep` optional). A partially measured surface is written `olculmedi`; `sebep` says what
  was measured and what was not. **`NOT MEASURED` is NOT a finding verdict, it is a coverage
  status** — it is never written into the `hukum` field.
- Someone else's real data enters no field (SKILL.md §0): row count + field name + HTTP
  code.

```json
{
  "sema": "gedik-bulgular/1",
  "bulgular": [
    {
      "bulgu_id": "G-1", "serit": "B", "hukum": "confirmed", "siddet": "KRITIK",
      "etkilenen": "api/orders.js:42 (no ownership check)",
      "poc_girdi": "GET /orders/1002 (session: user A)",
      "gozlenen": "HTTP 200, 1 row, fields: id, owner_id, total",
      "tekrar_uretim": "1) sign in as A 2) GET /orders/1002 3) response belongs to B",
      "yama": "add owner_id = :uid to the query",
      "dogrulayan": "alt-ajan"
    },
    {
      "bulgu_id": "G-2", "serit": "C", "hukum": "needs_validation",
      "etkilenen": "supabase/migrations/0003.sql",
      "cozulmemis_olgu": "is RLS enabled on the live project? only the migration was read"
    },
    {
      "bulgu_id": "G-3", "serit": "A", "hukum": "rejected", "dogrulayan": "ayri-tur",
      "eleme_nedeni": "sink is fed only by a constant template (origin traced)"
    }
  ],
  "kapsam": [
    { "yuzey": "A", "durum": "olculdu" },
    { "yuzey": "B", "durum": "olculdu" },
    { "yuzey": "C", "durum": "olculmedi", "sebep": "no live authorization" },
    { "yuzey": "D", "durum": "mimari-yok" }
  ]
}
```

---

## 5. DECISION THRESHOLD

To say **SUFFICIENT FROM A SECURITY STANDPOINT**, all three are required:

1. **No** CRITICAL or HIGH findings.
2. Every item on the lane's close-out checklist is `RAN` or `STATIC` — if a critical
   item is `NOT MEASURED`, no decision can be made.
3. The self-mutant **bit** in at least two areas.

If any one of the three is missing, the decision becomes `FIX` or `MEASURE FIRST`.
There is no decision called "probably fine."

---

## 6. HANDOFF

Once the report is done:
- If findings are to be fixed, they are itemized into the task text (Claude Code); this
  skill **does not modify code**.
- The decision is written as a single line into the project memory's decision log.
- If a new generally-applicable lesson emerged (such as a new false-"clean" trap), it is
  added to this reference file's §3 table — lessons must be permanent.
