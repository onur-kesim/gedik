# DILIM — gedik v2.8.0: PHP rapor bloğu (sabit alanlı) + alan-tabanlı kapı     açıldı: 2026-10-23 · aşama: YAPIM · sürüm dilimi: EVET (2.8.0)
Hedef: PHP bulgusunu serbest metinden SABİT ALANLI bir rapor bloğuna taşımak. Model formu doldurur, kapı alanları `php_olc` ölçümüyle birebir karşılaştırır. Anahtar-sözcük avı kalkar.
Neden (ölçüldü): aynı anahtar-sözcük kapısı 4 turdur her turda yeni okuma hatası çıkarıyor. v2.7.1'in A2 düzeltmesi kör nokta açtı (uydurma kaynaklı kötü raporlar PASS). Gerçek uyum 11/15: 2 gerçek ihlal (composer sonucu sayısız) + 3 kapı yanlış alarmı. K5 radarı → MEKANİKLEŞTİR (Onur kararı 2026-10-23). Ayrıntı: `_calisma/denetim_271/RAPOR.md`.
İŞ BÖLÜMÜ: kod + koşum = Claude Code. Bağımsız denetim + README = Cowork (yeni oturum).
Kurallar: skill salt-okur; canlı sisteme istek yok; sabit CVE tablosu yok; EOL kuralı aynen.

## YAP — 0: v2.7.1'i kenara al (ilk iş)
- [ ] v2.7.1 kapı/öz-test kodu + sürüm 2.7.1 + CHANGELOG [2.7.1] → `deneme/271-kapi` dalına commit (kaybolmasın); `main`'e GİRMEZ, v2.7.1 yayımlanmaz
- [ ] `main`'de kalır: KRITER "v2.7.1 ÖLÇÜMÜ" (B1–B6 ölçümleri) — RAPOR Bulgu 3'e göre düzeltilmiş: 7 FAIL = 3 kapı · 2 rapor · 1 biçim · 1 refusal; gerçek uyum 11/15 [48,0–89,1]; B3 "bayrak etkisi kanıtsız"

## YAP — A: blok (skill metni, TR kanonik + EN birebir, sabit cümle kilidine)
- [ ] SKILL.md Lane B / §2.1'e ZORUNLU blok; etiketler TR+EN sabit:
  `### PHP çalışma zamanı` — `T2 PHP: EVET|HAYIR — kanıt: <dosya>` · `Sürüm: <x.y[.z]>|YOK — kaynak: <dosya:satır>` · `Yama düzeyi: TAM|ÖLÇÜLEMEDİ` · `EOL: DESTEKLENEN|UYARI|BULGU|ÖLÇÜLEMEDİ` · `composer audit: <N> danışma|ÖLÇÜLEMEDİ (<sebep>)|UYGULANMAZ (composer.lock yok)` · `İmaj taraması: grype <N|ÖLÇÜLEMEDİ> · trivy <N|ÖLÇÜLEMEDİ>`
- [ ] Sürüm YOK ise bloğa mevcut sabit ÖLÇÜLEMEDİ cümlesi; blokta "temiz/clean" yasak; serbest metin bloğu tekrar etmek zorunda değil
- [ ] Koşum/rapor kuralı: rapor son mesajda TAM ve satır içi (dosyaya yazılırsa da son mesajda blok olmalı)

## YAP — B: kapı (araclar)
- [ ] `php_kapisi.py`: blok yoksa `BLOK_YOK`; her alan ölçümle eşleşir (T2 · sürüm+kaynak dosya:satır · yama düzeyi · EOL · composer N/ÖLÇÜLEMEDİ/UYGULANMAZ · imaj); blok içi temiz yasağı. Serbest-metin anahtar-sözcük kuralları kaldırılır (eski kodlar ölçüm dışı)
- [ ] Mutasyon aracı regex/etiket sabitlerini de bozar; her alan için doğru-YEŞİL / yanlış-KIRMIZI vaka TR+EN; öz-test dosyaları doğrudan çalışınca gerçekten koşar (`__main__`)
- [ ] Sürüm 2.8.0 dört yerde + CHANGELOG [2.8.0]; komut satırı 4 dosyada aynı

## DOĞRULA (mekanik kabul)
- [ ] Kapılar yeşil (kapilar · çeviri · kilit · iç ad · bulgu · php); mutasyon: hayatta 0 (eşdeğer olan gerekçeli)
- [ ] Denetçinin kör nokta satırları (`| php-cli | 8.1.5 | Dockerfile:2 |`, "PHP-FPM 8.1.5 … Dockerfile:2", "DOCKERFILE:1") → KIRMIZI; v2.7.1 yanlış alarm cümleleri (EOL-kapsamlı "sorun yok", "1 uyarı", "yama seviyesi", varsayım cümlesi) → blok doğruysa YEŞİL
- [ ] Model koşusu: 5 hedef ×3 = 15 (v2.8.0, `--plugin-dir`, CVP org, `claude -p`, ham `_calisma/saha_280/`). KABUL: kapı PASS ≥ 13/15 ve gerçek ihlal 0 (FAIL'ler tek tek hakemli); refusal sayısı kayıtlı; Wilson aralığı
- [ ] NE ÖLÇÜLEMEDİ (dolu)

## TESLİM
- [ ] Bağımsız denetim (Cowork, yeni oturum) TESLİME UYGUN
- [ ] README×2: blok + "CVP onaylı hesapta bile raporların küçük kısmı kesilebilir (15'te 1)" + tarayıcı sınırı (trivy resmî imajda PHP'yi görmüyor; grype görüyor, composer kaydını kaçırdı) + gerçek uyum oranı
- [ ] `v2.8.0` etiketi + Release; push: Onur

## Sonuç
(açık)
