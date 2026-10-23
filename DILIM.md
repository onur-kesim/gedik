# DILIM — gedik v2.7.0 saha ölçümü: gerçek tarayıcı çıktısı + yeni kodla model koşusu     açıldı: 2026-10-23 · aşama: YAPIM · sürüm dilimi: HAYIR (yalnız ölçüm; kod değişmez)
Hedef: v2.7.0'ın ölçülmemiş iki ayağını ölçmek. (1) `composer audit` / `trivy` / `grype` gerçek çıktısı: gedik'in tarayıcıya dayalı açık eşleşmesi PHP2Shell'i (CVE-2026-109618/109619) gerçekten görüyor mu? (2) Yüklü v2.7.0 skill'i model koşusunda kurala uyuyor mu?
Hipotez (TAHMİN, ölçülecek): resmî `php:*` imajlarında PHP kaynaktan derlenir, OS paketi değildir → trivy/grype PHP2Shell'i GÖRMEYEBİLİR. Görmüyorsa bu bir ÜRÜN SINIRIDIR: README'ye yazılır; o durumda tek sinyal gedik'in kendi sürüm okuması + EOL kuralıdır.
İŞ BÖLÜMÜ: kurulum + koşum + ölçüm = Claude Code. Bağımsız denetim + README/KRITER metni = Cowork.
Kural: araçlar sisteme KURULMAZ — taşınabilir ikililer `_calisma/araclar/` altına (gitignore'lu, silinebilir). Canlı sisteme istek YOK (registry'den imaj/DB çekmek hedef testi değildir). Ürün kodu değişmez; bulgu kod değişikliği gerektirirse yeni dilim açılır.

## YAP  (Claude Code)
- [ ] ARAÇLAR (taşınabilir, `_calisma/araclar/`): trivy (aquasecurity/trivy GitHub Release, Windows zip), grype (anchore/grype GitHub Release, Windows zip), PHP 8.4 NTS (windows.php.net zip; yalnız composer'ı çalıştırmak için) + `composer.phar` (getcomposer.org). Her biri: sürüm + SHA256 + lisans DURUM'a; PATH yalnız koşum kabuğunda
- [ ] COMPOSER AUDIT: (a) DVWA `vulnerabilities/api/composer.lock` → bulgu sayısı; (b) pozitif kontrol: bilinen danışmalı (Packagist advisory) eski bir paketi kilitleyen sentetik `composer.lock` → ≥1 bulgu GÖRMELİ (görmezse araç kör)
- [ ] İMAJ TARAMASI (trivy + grype, ikisi de): `php:8.3.30-fpm` (yama öncesi) ve `php:8.3.36-fpm` (yamalı; etiket yoksa en yakın yamalı) + DVWA `php:8-apache`. Her imajda: CVE-2026-109618/109619 görüldü mü (EVET/HAYIR) + tarayıcının PHP'yi hangi paket/ikili olarak tanıdığı (ya da tanımadığı) + DB tarihi
- [ ] MODEL KOŞUSU: yüklü plugin sürümü 2.7.0 doğrulanır (`claude plugin` çıktısı); CVP org (`31805ed8-…`); üst düzey `claude -p`; araçlar PATH'te. Hedefler: DVWA ×2, fixture Laravel+`php:8.3.30-fpm` ×1, `docker/php.Dockerfile` 7.4 ×1, WordPress yedeği (sürüm yok) ×1. Her rapor `php_kapisi.py --hedef … --rapor …` ile; stop_reason kaydı
- [ ] SONUÇ → KRITER.md yeni bölüm "v2.7.0 SAHA ÖLÇÜMÜ" (ham çıktılar `_calisma/saha_270/`, repoya girmez)

## DOĞRULA (mekanik kabul)
- [ ] composer audit pozitif kontrolü ≥1 bulgu (kör değil)
- [ ] İmaj tablosu dolu: 3 imaj × 2 tarayıcı × (CVE görüldü mü · PHP tanındı mı · DB tarihi)
- [ ] Model koşuları: 5 rapor, her biri php_kapisi PASS ya da FAIL+kod kayıtlı; refusal sayısı; raporda tarayıcı çıktısı SAYIYLA var mı
- [ ] Hipotez hükmü yazılı: tarayıcılar PHP2Shell'i görüyor / görmüyor (kanıtla)
- [ ] NE ÖLÇÜLEMEDİ (dolu)

## TESLİM
- [ ] Bağımsız denetim (Cowork) TESLİME UYGUN
- [ ] README×2 güncel (sınır değiştiyse; ör. "tarayıcılar resmî imajda derlenmiş PHP'yi görmüyor")
- [ ] push: Onur

## Sonuç
(açık)
