# DILIM — gedik v2.8.0: PHP rapor bloğu (sabit alanlı) + alan-tabanlı kapı     açıldı: 2026-10-23 · aşama: YAPIM · sürüm dilimi: EVET (2.8.0)
Hedef: PHP bulgusunu serbest metinden SABİT ALANLI bir rapor bloğuna taşımak. Model formu doldurur, kapı alanları `php_olc` ölçümüyle birebir karşılaştırır. Anahtar-sözcük avı kalkar.
Neden (ölçüldü): aynı anahtar-sözcük kapısı 4 turdur her turda yeni okuma hatası çıkarıyor. v2.7.1'in A2 düzeltmesi kör nokta açtı (uydurma kaynaklı kötü raporlar PASS). Gerçek uyum 11/15: 2 gerçek ihlal (composer sonucu sayısız) + 3 kapı yanlış alarmı. K5 radarı → MEKANİKLEŞTİR (Onur kararı 2026-10-23). Ayrıntı: `_calisma/denetim_271/RAPOR.md`.
İŞ BÖLÜMÜ: kod + koşum = Claude Code. Bağımsız denetim + README = Cowork (yeni oturum).
Kurallar: skill salt-okur; canlı sisteme istek yok; sabit CVE tablosu yok; EOL kuralı aynen.

## YAP — 0: v2.7.1'i kenara al (ilk iş)
- [x] (709dab4 `deneme/271-kapi`, Cowork O15 ölçtü) v2.7.1 kapı/öz-test kodu + sürüm 2.7.1 + CHANGELOG [2.7.1] → `deneme/271-kapi` dalına commit (kaybolmasın); `main`'e GİRMEZ, v2.7.1 yayımlanmaz
- [x] (çalışma ağacında, commit'siz) `main`'de kalır: KRITER "v2.7.1 ÖLÇÜMÜ" (B1–B6 ölçümleri) — RAPOR Bulgu 3'e göre düzeltilmiş: 7 FAIL = 3 kapı · 2 rapor · 1 biçim · 1 refusal; gerçek uyum 11/15 [48,0–89,1]; B3 "bayrak etkisi kanıtsız"

## YAP — A: blok (skill metni, TR kanonik + EN birebir, sabit cümle kilidine)
- [x] SKILL.md Lane B / §2.1'e ZORUNLU blok; etiketler TR+EN sabit:
  `### PHP çalışma zamanı` — `T2 PHP: EVET|HAYIR — kanıt: <dosya>` · `Sürüm: <x.y[.z]>|YOK — kaynak: <dosya:satır>` · `Yama düzeyi: TAM|ÖLÇÜLEMEDİ` · `EOL: DESTEKLENEN|UYARI|BULGU|ÖLÇÜLEMEDİ` · `composer audit: <N> danışma|ÖLÇÜLEMEDİ (<sebep>)|UYGULANMAZ (composer.lock yok)` · `İmaj taraması: grype <N|ÖLÇÜLEMEDİ> · trivy <N|ÖLÇÜLEMEDİ>`
- [x] Sürüm YOK ise bloğa mevcut sabit ÖLÇÜLEMEDİ cümlesi; blokta "temiz/clean" yasak; serbest metin bloğu tekrar etmek zorunda değil
- [x] Koşum/rapor kuralı: rapor son mesajda TAM ve satır içi (dosyaya yazılırsa da son mesajda blok olmalı)

## YAP — B: kapı (araclar)
- [x] `php_kapisi.py`: blok yoksa `BLOK_YOK`; her alan ölçümle eşleşir (T2 · sürüm+kaynak dosya:satır · yama düzeyi · EOL · composer N/ÖLÇÜLEMEDİ/UYGULANMAZ · imaj); blok içi temiz yasağı. Serbest-metin anahtar-sözcük kuralları kaldırılır (eski kodlar ölçüm dışı)
- [x] Mutasyon aracı regex/etiket sabitlerini de bozar; her alan için doğru-YEŞİL / yanlış-KIRMIZI vaka TR+EN; öz-test dosyaları doğrudan çalışınca gerçekten koşar (`__main__`)
- [x] Sürüm 2.8.0 dört yerde + CHANGELOG [2.8.0]; komut satırı 4 dosyada aynı

## DOĞRULA (mekanik kabul)
- [x] Kapılar yeşil (kapilar · çeviri · kilit · iç ad · bulgu · php); mutasyon: hayatta 0 (eşdeğer olan gerekçeli)
- [x] Denetçinin kör nokta satırları (`| php-cli | 8.1.5 | Dockerfile:2 |`, "PHP-FPM 8.1.5 … Dockerfile:2", "DOCKERFILE:1") → KIRMIZI; v2.7.1 yanlış alarm cümleleri (EOL-kapsamlı "sorun yok", "1 uyarı", "yama seviyesi", varsayım cümlesi) → blok doğruysa YEŞİL
- [x] Model koşusu: 5 hedef ×3 = 15 (v2.8.0, `--plugin-dir`, CVP org, `claude -p`, ham `_calisma/saha_280/`). KABUL: kapı PASS ≥ 13/15 ve gerçek ihlal 0 (FAIL'ler tek tek hakemli); refusal sayısı kayıtlı; Wilson aralığı
- [x] NE ÖLÇÜLEMEDİ (dolu)

## DÜZELT (bağımsız denetim 2026-10-24, `_calisma/denetim_280/RAPOR.md` — K5: ölçülmüş kusur)
- [x] B1: öz-teste etiket yazım hatası → `ALAN_YOK` vakaları (T2 + composer, TR+EN; #5/#6 ölür) + YÜZEN çift tire (`8-apache--kaynak:`) davranışına karar + vaka (#8 ölür); mutasyonu pozitif kontrolle yeniden koş → gerekçesiz hayatta 0
- [x] B2: "temiz/güvenli/risk yok" yasağı blok bölgesinin TÜM satırlarına (yalnız alan satırı değil)
- [x] B3: `T2 PHP` kanıt dosyası `php_olc` imza listesinde olmalı; README/CHANGELOG/KRITER'de "kapının doğrulamadığı" listesi tam: sayılar · ÖLÇÜLEMEDİ/UYGULANMAZ sebep metni · serbest metin (yalnız `x.y … dosya:satır` kalıbı denetlenir)
- [x] B4: yanlış alarmlar — blok bölgesi ilk boş satırda biter (altındaki "Notlar:" alan sayılmaz); tarayıcı-çözümü satırı (grype/trivy/syft/tarayıcı/scanner/resolved) `UYDURMA_KAYNAK`'tan muaf; imaj alanı `ÖLÇÜLEMEDİ (<sebep>)` kabul; her biri TR+EN doğru-YEŞİL / bozuk-KIRMIZI (denetçi girdileri `denetci.tgz` → `kor.py`, `yanlis_alarm.py`)
- [x] B7: `puan.py` çıktı yolu parametreli (ham/*.md üzerine yazmaz); §2.1 başlığındaki "(v2.7.0)" düzelt
- [x] 15 saha raporu yeni kapıyla yeniden puanlanır (model koşusu YENİDEN KOŞULMAZ; kapı değişti, rapor değişmedi) → PASS ≥ 13/15; KRITER v2.8.0 ölçümü güncellenir (24 eşdeğer iddiası geri çekilir, B2)

## DÜZELT-2 · DARALT (son denetim 2026-10-26, `_calisma/denetim_280b/RAPOR.md`; 2 gerileme, Cowork yeniden üretti) — YENİ DENETİM TURU YOK, kabul mekanik
- [x] G1: tarayıcı-sözcüğü muafiyeti yalnız SÜRÜMÜ atlar; satırdaki `dosya:satır` yine gerçek kaynak olmalı (prototip `denetci.tgz` → `denetci/onerı/php_kapisi.py`)
- [x] G2: blok bölgesi dışındaki alan-etiketli satırlar (`- Sürüm:`/`- Version:` …) `x.y … dosya:satır` denetimine girer; değer çelişkisi (EOL/yama/T2) kuralı YAZILMAZ → README sınırı
- [x] G3: CHANGELOG muafiyet listesine `çözül`
- [x] KABUL (mekanik, Cowork betikle koşar): `denetci/regresyon.py` 18 girdinin ≥15'i KIRMIZI (kalan 3 = değer çelişkisi, belgeli); Bulgu 4 tarayıcı satırları YEŞİL; kapılar + öz-test yeşil; mutasyon pozitif kontrollü, gerekçesiz hayatta 0; saha 14/15 değişmez

## TESLİM
- [x] (2026-10-26 Cowork) Bağımsız denetim: tur 1 DÜZELT (`denetim_280`), tur 2 DÜZELT (`denetim_280b`, 2 gerileme) → DÜZELT-2 DARALT; KABUL mekanik GEÇTİ: regresyon 15/19 KIRMIZI (4 = değer çelişkisi, belgeli), G1/G2 yeniden üretilip KIRMIZI, saha 14/15 Cowork yeniden puanladı, kapılar 7 PASS/0 FAIL — TESLİME UYGUN
- [x] (2026-10-26 Cowork; ic_ad 0, çeviri TESLIME UYGUN) README×2: blok + "CVP onaylı hesapta bile raporlar kesilebilir (v2.7.1: 15'te 1; v2.8.0: 15'te 0)" + kapının doğrulamadıkları (B3) + tarayıcı sınırı (trivy resmî imajda PHP'yi görmüyor; grype görüyor, composer kaydını kaçırdı) + gerçek uyum oranı
- [x] (2026-10-26 23:58 TRT, Onur push) `v2.8.0` etiketi + Release; push: Onur — Cowork Chrome'dan ölçtü: Release "v2.8.0 Latest" fa85111; CI kapilar #18 (main) + #19 (tag) + surum #3 "completed successfully"; canlı README yeni PHP metnini gösteriyor

## Sonuç
**KAPANDI 2026-10-26** — v2.8.0 yayında (fa85111). Dört sayı: ürün nabzı 0 gün · dilim yaşı 3 gün · kapı kırmızı 0 · sayaç ÖLÇÜLEMEDİ (yıldız/fork sayfa metninde yok; gh API bu oturumda kapalı).
2026-10-24 TRT: YAP 0/A/B ve DOĞRULA kutuları [x]; TESLİM 0/3 (Cowork bağımsız denetim · README×2 · tag+Release+push: Onur). Ayrıntı KRITER "v2.8.0 ÖLÇÜMÜ", ham `_calisma/saha_280/`.
- YAP-0: v2.7.1 kodu `deneme/271-kapi` (709dab4); KRITER v2.7.1 bölümü Bulgu 3'e göre düzeltildi.
- Blok + alan-tabanlı kapı: öz-test 464 ✓/0 ✗; mutasyon 333 → 328 geçerli, 304 öldü, 24 hayatta = 24 eşdeğer (sınıf sayıları KRITER'de).
- B6: end_turn 15/15, refusal 0/15, kapı PASS 14/15 [70,2–98,8]; tek FAIL = blok alanına serbest not (biçim sapması, içerik doğru). CLI 2.1.269→2.1.309 (dvwa-r1-a/r2-a segfault, 1 yeniden deneme).
- Önceki oturumdan devralınan 3 düzeltme: `kusur_uydurma` dal-öneki (8.3 ← 8.3.30), mutasyon aracı WinError 1450 (copytree → 2 SKILL.md), 15 koşu sıralı + yeniden puan.
- Sapma: DILIM'de olmayan yeni dosya `araclar/php_oz_sabit.py` (regex sabitleri vakaları; `proje.toml`/README komut satırına eklendi).
- DÜZELT turu (2026-10-26): B1–B4, B7 + yeniden puan [x]. "24 eşdeğer" beyanı GERİ ÇEKİLDİ (3'ü eşdeğer değildi); son mutasyon 361/356 geçerli/335 öldü/21 hayatta = 21 girdi taramasıyla eşdeğer (KRITER "DÜZELT TURU"). Öz-test 638 ✓/0 ✗; denetçinin 68 vakası birebir `php_oz_denetci.py`'de. 15 rapor yeni kapıyla 14/15 PASS (ham değişmedi). Yeni dosyalar: `php_oz_denetim.py`, `php_oz_denetci.py` (komut satırı 4 dosyada). README×2 Cowork'te.
- DÜZELT-2 (2026-10-26): G1/G2/G3 [x]. Regresyon 19 girdiden 15 KIRMIZI (kalan 4 = bölge dışı alan değeri çelişkisi, belgeli sınır, kural yazılmadı); öz-test 796 ✓/0 ✗; mutasyon 364 → 359 geçerli, 338 öldü, 21 hayatta = 21 girdi taramasıyla eşdeğer (1 eşdeğer-değil mutant vaka ile öldürüldü); saha 14/15 değişmedi (ham sha aynı). Yeni dosya `araclar/php_oz_gerileme.py` (komut satırı 4 dosyada). Ayrıntı KRITER "DÜZELT-2".
