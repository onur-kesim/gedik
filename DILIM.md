# DILIM — gedik v2.7.1: PHP kapısının iki yanlış alarmı + saha ölçümünün ölçülemeyenleri     açıldı: 2026-10-23 · aşama: YAPIM · sürüm dilimi: EVET (2.7.1, yama)
Hedef: (A) saha ölçümünde hakemlikle ÖLÇÜLMÜŞ iki kapı kusurunu kapatmak; (B) saha ölçümünde "ÖLÇÜLEMEDİ" kalan, ölçülebilir her şeyi ölçmek. Kaynak: KRITER "v2.7.0 SAHA ÖLÇÜMÜ" + BAĞIMSIZ DENETİM paragrafı.
İŞ BÖLÜMÜ: kod + ölçüm + koşum = Claude Code. Bağımsız denetim + KRITER/README metni = Cowork.
Kurallar: skill salt-okur kalır; canlı sisteme istek yok (registry'den imaj/DB, yayıncıdan araç/checksum çekimi hedef testi değildir). Araçlar yalnız `_calisma/araclar/` (taşınabilir). Her ölçüm ham dosyasıyla `_calisma/saha_271/` altına; KRITER'e yalnız ham dosyadan sayı.
Kapsam dışı (bilinçli, ÖLÇÜLEMEDİ kalır): paylaşımlı hosting'in gerçek çalışma zamanı sürümü — canlı sunucuya yetkiyle erişim ister; gedik'in tasarım sınırı.

## YAP — A: kapı kusurları (kod)
- [ ] A1 `TEMIZ` deseni: EOL'a kapsamlı hüküm ("EOL kuralına göre/açısından sorun yok", "no EOL issue") temiz iddiası sayılmaz; gerçek "PHP tarafında risk yok / no action needed" hâlâ KIRMIZI. Vaka: fx-a satır 38 aynen (TR) + EN karşılığı
- [ ] A2 `kusur_uydurma`: dosya deseni tam ad eşleşmesi (`composer.lock` ≠ compose dosyası); `swagger-php` / `gen_openapi.php` gibi alt dizgiler PHP sürüm iddiası sayılmaz. Vaka: dvwa-r1 satır 187 aynen + gerçek uydurma kaynaklı bozuk kopya KIRMIZI
- [ ] A3 koşum istemi (`_calisma` koşum betiği): "raporu son mesajında TAM ve satır içi ver"
- [ ] Her düzeltme: TR+EN doğru-YEŞİL / bozuk-kopya-KIRMIZI; mutasyon ölçümü yeniden; sürüm 2.7.1 dört yerde + CHANGELOG [2.7.1]

## YAP — B: ölçülemeyenleri ölç
- [ ] B1 grype yamalı imajda PHP'yi tanıyor mu: `syft` (anchore/syft, taşınabilir) ile `php:8.3.30-fpm`, `php:8.3.36-fpm`, `php:8-apache` paket envanteri → `php` ikilisi + sürüm listede mi (pozitif kontrol: 8.3.30)
- [ ] B2 grype `composer.lock` kaçırma nedeni: `grype db search` ile CVE-2026-109413 / `symfony/yaml` DB'de var mı + grype'ın DVWA lock'u katalogladığı paket listesi
- [ ] B3 trivy başka ayarlarla PHP'yi görür mü: en az 2 bayrak/yol (ör. SBOM girdisi, `--detection-priority comprehensive`) — sonuç ne olursa olsun kayıt
- [ ] B4 pozitif kontrol ham dosyası: trivy fs + grype dir, DVWA ve sentetik kilit → JSON kaydet (18/18 beyanı kanıtlansın ya da düzeltilsin)
- [ ] B5 SHA256 yayıncı eşleşmesi: PHP 8.4.27 (windows.php.net yayıncı checksum'u) + composer 2.10.3 (`.sha256sum`) — referans dosyası saklanır
- [ ] B6 model uyum ORANI: 5 hedefin her biri ×3 (mevcut 1 + 2 yeni = 15 koşu), yeni kapıyla; her koşu: end_turn/refusal, php_kapisi sonucu, rapor satır içi mi. Oran + %95 Wilson aralığı; eski 5 rapor yeni kapıyla yeniden puanlanır
- [ ] SONUÇ → KRITER yeni bölüm "v2.7.1 ÖLÇÜMÜ"

## DOĞRULA (mekanik kabul)
- [ ] Kapılar yeşil (kapilar · çeviri · kilit · iç ad · bulgu · php); A1/A2 vakaları + bozuk kopyaları; mutasyon 0 hayatta (eşdeğer olan gerekçeli)
- [ ] B1–B5 her biri EVET/HAYIR + ham dosya yolu; B6 oran + aralık + n
- [ ] NE ÖLÇÜLEMEDİ (yalnız gerçekten ölçülemeyen kalır, sebebiyle)

## TESLİM
- [ ] Bağımsız denetim (Cowork) TESLİME UYGUN
- [ ] README×2 (B1–B3 sonucu sınırı değiştiriyorsa)
- [ ] `v2.7.1` etiketi + Release; push: Onur

## Sonuç
(açık)
