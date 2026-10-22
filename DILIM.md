# DILIM — gedik v2.7.0: PHP görünürlüğü (triyaj + çalışma zamanı + paket CVE)     açıldı: 2026-10-22 · aşama: YAPIM · sürüm dilimi: EVET (2.7.0)
Hedef: gedik bir PHP projesinde (Laravel/Symfony/WordPress/düz PHP) sunucu şeridini doğru açsın, PHP çalışma zamanı sürümünü ve composer paket açıklarını ÖLÇSÜN, ölçemediğini "ÖLÇÜLEMEDİ" yazsın — asla "temiz" demesin. gedik salt-okur kalır: yamalamaz, raporlar.
Tetik (2026-10-22, Cowork ölçümü): PHP CVE-2026-109618/109619 (CVSS v4 9,2, kimliksiz RCE; yamalı: 8.5.12 · 8.4.27 · 8.3.36 · 8.2.35; ≤8.1 resmî yama yok — kaynak php.net 21 Eki). Skill metni ölçüldü: (1) triyaj T2 imzalarında PHP yok (express/flask/django/spring/rails var); (2) `composer audit` hiç geçmiyor; (3) çalışma zamanı sürümü yalnız Docker base-imaj CVE'si üzerinden dolaylı görülüyor; paylaşımlı hosting'de sürüm depoda yok.
İŞ BÖLÜMÜ: YAP + re-koşum = Claude Code. Bağımsız denetim + README metni = Cowork (ayrı oturum).
Kural: sabit CVE tablosu YAZILMAZ (bayatlar) — açık eşleşmesi tarayıcı veritabanından (trivy/grype/osv-scanner/composer audit) gelir. Yalnız EOL dalı kuralı sabittir, ölçüm tarihiyle yazılır.

## YAP  (Claude Code)
- [ ] ÖN ÖLÇÜM: sürümün geçtiği yerler (önceki dilim "4 yer" dedi — grep'le doğrula) + `araclar/kapilar.py` altın küme/fixture yapısı; DILIM'e tek satır yaz
- [ ] TRİYAJ (SKILL.md T2 + triyaj-ve-kapsam.md): PHP imzaları — `composer.json`, `artisan`, `laravel/framework`, `symfony/*`, `wp-config.php` / `wp-content/`, kökte `index.php` router, `php-fpm` pool dosyası, `.htaccess` + PHP handler; T9/T12: `Dockerfile` `FROM php:` / docker-compose `image: php`
- [ ] ÇALIŞMA ZAMANI SÜRÜMÜ (kod-inceleme-guvenlik.md): kaynak sırası — Dockerfile/compose imaj etiketi · `.php-version` · `composer.json` `config.platform.php` · CI `setup-php`/matris · buildpack/platform dosyası. Bulunan sürüm rapora KAYNAĞIYLA yazılır; `composer.json` `"php": ">=x"` kısıtı çalışan sürüm SAYILMAZ (yalnız alt sınır)
- [ ] ÖLÇÜLEMEDİ KURALI: sürüm depoda yoksa sabit satır — "PHP çalışma zamanı sürümü depoda yok — ÖLÇÜLEMEDİ; sunucu/hosting panelinden kontrol et." Temiz DENMEZ
- [ ] EOL KURALI (ölçüm 2026-10-22, php.net): PHP ≤8.1 = resmî güvenlik yaması yok → bulgu (dağıtım/LTS backport'u ayrıca sorulur); 8.2 EOL 2026-12-31 → uyarı. Referansa ölçüm tarihi + "yeniden doğrula" notu
- [ ] PAKET CVE: `composer.lock` varsa `composer audit` (yoksa ÖLÇÜLEMEDİ); imaj varsa `trivy`/`grype` ile base imaj; çıktı SAYIYLA
- [ ] TR kanonik + EN birebir; değişen sabit cümleler `sabit_cumleler.json`'a; sürüm 2.7.0 tüm yerlerde; CHANGELOG

## DOĞRULA (mekanik kabul)
- [ ] Altın küme +3 fixture (kapilar.py zincirinde): (a) Laravel iskeleti + `FROM php:8.3.30-fpm` → T2 PHP=evet, sürüm=8.3.30 kaynağıyla, 8.3.36 altında olduğu raporda; (b) `composer.lock`'lu depo → composer audit adımı koşar ya da ÖLÇÜLEMEDİ; (c) WordPress dosya yedeği, sürüm yok → ÖLÇÜLEMEDİ satırı çıkar
- [ ] Kör kapı/mutant: (a)'dan imaj satırı silinince kapı KIRMIZI; (c) için "temiz" yazan sahte rapor KIRMIZI; EOL fixture'ında `FROM php:8.1` → bulgu yoksa KIRMIZI
- [ ] Var olan kapılar yeşil: kapilar · çeviri · sabit cümle · iç ad · bulgu_kapisi
- [ ] Gerçek hedef koşumu (CVP org, üst düzey, salt-okuma kaynak): açık kaynak bir PHP uygulaması (aday: DVWA — Dockerfile'ı php base imaj) → T2 PHP açıldı, çalışma zamanı sürümü kaynağıyla raporda, rapor teslim (stop_reason ≠ refusal). Canlı sisteme istek YOK
- [ ] NE ÖLÇÜLEMEDİ (dolu)

## TESLİM
- [ ] Bağımsız denetim (Cowork, ayrı oturum) TESLİME UYGUN
- [ ] README×2: PHP kapsamı + "bu sürümde HAYIR: paylaşımlı hosting'de çalışma zamanı sürümü depodan görülemez"; rakip/öncül satırı gerekirse
- [ ] `v2.7.0` etiketi + CHANGELOG + Release; geri alma = önceki etikete dönüş
- [ ] push: Onur ("push et" ile Cowork/Code)

## Sonuç
(açık)
