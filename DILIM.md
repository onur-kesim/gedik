# DILIM — gedik v2.7.0 saha ölçümü: gerçek tarayıcı çıktısı + yeni kodla model koşusu     açıldı: 2026-10-23 · aşama: YAPIM · sürüm dilimi: HAYIR (yalnız ölçüm; kod değişmez)
Hedef: v2.7.0'ın ölçülmemiş iki ayağını ölçmek. (1) `composer audit` / `trivy` / `grype` gerçek çıktısı: gedik'in tarayıcıya dayalı açık eşleşmesi PHP2Shell'i (CVE-2026-109618/109619) gerçekten görüyor mu? (2) Yüklü v2.7.0 skill'i model koşusunda kurala uyuyor mu?
Hipotez (TAHMİN, ölçülecek): resmî `php:*` imajlarında PHP kaynaktan derlenir, OS paketi değildir → trivy/grype PHP2Shell'i GÖRMEYEBİLİR. Görmüyorsa bu bir ÜRÜN SINIRIDIR: README'ye yazılır; o durumda tek sinyal gedik'in kendi sürüm okuması + EOL kuralıdır.
İŞ BÖLÜMÜ: kurulum + koşum + ölçüm = Claude Code. Bağımsız denetim + README/KRITER metni = Cowork.
Kural: araçlar sisteme KURULMAZ — taşınabilir ikililer `_calisma/araclar/` altına (gitignore'lu, silinebilir). Canlı sisteme istek YOK (registry'den imaj/DB çekmek hedef testi değildir). Ürün kodu değişmez; bulgu kod değişikliği gerektirirse yeni dilim açılır.

## YAP  (Claude Code)
- [x] ARAÇLAR (taşınabilir, `_calisma/araclar/`): trivy (aquasecurity/trivy GitHub Release, Windows zip), grype (anchore/grype GitHub Release, Windows zip), PHP 8.4 NTS (windows.php.net zip; yalnız composer'ı çalıştırmak için) + `composer.phar` (getcomposer.org). Her biri: sürüm + SHA256 + lisans DURUM'a; PATH yalnız koşum kabuğunda
- [x] COMPOSER AUDIT: (a) DVWA `vulnerabilities/api/composer.lock` → bulgu sayısı; (b) pozitif kontrol: bilinen danışmalı (Packagist advisory) eski bir paketi kilitleyen sentetik `composer.lock` → ≥1 bulgu GÖRMELİ (görmezse araç kör)
- [x] İMAJ TARAMASI (trivy + grype, ikisi de): `php:8.3.30-fpm` (yama öncesi) ve `php:8.3.36-fpm` (yamalı; etiket yoksa en yakın yamalı) + DVWA `php:8-apache`. Her imajda: CVE-2026-109618/109619 görüldü mü (EVET/HAYIR) + tarayıcının PHP'yi hangi paket/ikili olarak tanıdığı (ya da tanımadığı) + DB tarihi
- [x] MODEL KOŞUSU (SAPMA: kurulu eklenti 2.6.0 → `--plugin-dir` ile depodan 2.7.0; init olayında doğrulandı): yüklü plugin sürümü 2.7.0 doğrulanır (`claude plugin` çıktısı); CVP org (`31805ed8-…`); üst düzey `claude -p`; araçlar PATH'te. Hedefler: DVWA ×2, fixture Laravel+`php:8.3.30-fpm` ×1, `docker/php.Dockerfile` 7.4 ×1, WordPress yedeği (sürüm yok) ×1. Her rapor `php_kapisi.py --hedef … --rapor …` ile; stop_reason kaydı
- [x] SONUÇ → KRITER.md yeni bölüm "v2.7.0 SAHA ÖLÇÜMÜ" (ham çıktılar `_calisma/saha_270/`, repoya girmez)

## DOĞRULA (mekanik kabul)
- [x] composer audit pozitif kontrolü ≥1 bulgu (kör değil)
- [x] İmaj tablosu dolu: 3 imaj × 2 tarayıcı × (CVE görüldü mü · PHP tanındı mı · DB tarihi)
- [x] Model koşuları: 5 rapor, her biri php_kapisi PASS ya da FAIL+kod kayıtlı; refusal sayısı; raporda tarayıcı çıktısı SAYIYLA var mı
- [x] Hipotez hükmü yazılı: tarayıcılar PHP2Shell'i görüyor / görmüyor (kanıtla)
- [x] NE ÖLÇÜLEMEDİ (dolu)

## TESLİM
- [x] Bağımsız denetim (Cowork, ayrı bağlam) 2026-10-23: DÜZELT (yalnız kayıt: süre kayması, kanıtsız 18/18, PATH beyanı, grype genellemesi) → Cowork belge düzeltmelerini uyguladı → TESLİME UYGUN; hakemlik: fx-a ve dvwa-r1 FAIL'leri KAPI KUSURU (yeni dilim adayı)
- [x] README×2 güncel (Cowork 2026-10-23: saha sonucu — trivy görmedi, grype 1 imajda gördü, grype composer.lock kaçırdı) (sınır değiştiyse; ör. "tarayıcılar resmî imajda derlenmiş PHP'yi görmüyor")
- [ ] push: Onur

## Sonuç
2026-10-23 TRT: YAP 5/5 + DOĞRULA 5/5 [x]; TESLİM 0/3 (Cowork denetimi · README×2 · Onur push). Ayrıntı KRITER.md "v2.7.0 SAHA ÖLÇÜMÜ".
- composer audit: DVWA 1 advisory; pozitif kontrol 18 (kör değil). grype aynı DVWA lock'ta 0 (trivy 1) — grype kaçırıyor.
- Hipotez YARIM TUTTU: trivy resmî php imajında PHP'yi tanımıyor → PHP2Shell GÖRMÜYOR; grype ikili kataloglayıcıyla tanıyor → `php:8.3.30-fpm`'de CVE-2026-109618/109619 EVET, 8.3.36'da HAYIR (beklenen).
- Model koşuları (v2.7.0 `--plugin-dir`; KURULU eklenti hâlâ 2.6.0): 5/5 end_turn, refusal 0; php_kapisi PASS 3 / FAIL 2 (fx-a `TEMIZ_DENMIS`: kapı keskinliği şüphesi; dvwa-r1: rapor satır içi verilmedi + `UYDURMA_KAYNAK`). Ürün kodu değişmedi; kapı hakemliği/teslim biçimi bulgusu yeni dilim adayı.
- Sapma: DILIM'deki "docker/php.Dockerfile 7.4" fixture'ı yoktu; `_calisma/saha_270/hedef/fx-d-php74` (php:7.4-apache + 1 SQLi satırı) bu ölçüm için yazıldı.
