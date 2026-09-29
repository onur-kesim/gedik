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
> Tarih: <YYYY-AA-GG> · Denetleyen: zafiyet-avcisi v1.0 · Kapsam: kullanıcının kendi
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
### Z-1 · [ŞİDDET] <tek cümlelik başlık>
- **Nerede:** dosya:satır
- **Tekrar üretim:** <birebir girdi/komut>
- **Gözlenen:** <ölçülen sonuç>
- **Etki:** <mimarinin izin verdiği tavana göre, şişirmesiz>
- **Yama:** <somut, uygulanabilir düzeltme>
- **Kanıt türü:** KOŞULDU / STATİK / ÖLÇÜLMEDİ

## 3. TEMİZ ÇIKANLAR (her biri neyle ölçüldü)
| Başlık | Sonuç | Ölçüm yöntemi |

## 4. ÖLÇÜLMEYENLER
| Başlık | Neden ölçülmedi | Nasıl ölçülür |

## 5. SELF-MUTANT SONUCU
| Mutant | Kirli kopya | Temiz sürüm | Karar |

## 6. KARAR
**GÜVENLİK AÇISINDAN YETERLİ** (kritik/yüksek bulgu yok, ölçülmeyen kritik başlık yok)
— veya —
**DÜZELT:** [Z-1, Z-3, ...] · **ÖNCE ÖLÇ:** [ölçülmeyen kritik başlıklar]

## 7. SONRAKİ TURA DEVREDİLENLER
- ...
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
