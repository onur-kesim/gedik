# CHANGELOG
Biçim: Keep a Changelog. Her git etiketi bir bölüm; [Unreleased] altı bir sonraki etiketi bekler.
Sürüm numarası `.claude-plugin/plugin.json`'daki gedik ürün sürümüdür (proje-sablonu'nun
kendi 0.x geçmişi — KUR öncesi, aşağıda — ile karıştırılmaz).

## [Unreleased]

## [2.6.0] — 2026-09-29
### Eklendi
- **Makine-okur çıktı (spec A).** Tam denetimde `.md` raporun yanına `gedik-bulgular.json`:
  üç hüküm (`confirmed` / `needs_validation` / `rejected`), `ÖLÇÜLMEDİ` bir hüküm değil ayrı
  `kapsam` alanı. Şema `araclar/bulgu-semasi.json`; doğrulayıcı kapı `araclar/bulgu_kapisi.py`
  (yalnız standart kütüphane; kör kapı öz-testli: 68 aykırı girdi KIRMIZI, 22 geçerli varyant +
  temiz örnek YEŞİL yakar; kapı yolu — dosya yok→ATLANDI, açık yol yok→FAIL, BOM, çıkış kodları,
  `kapilar.py` zincirine bağlantı — ve skill belgelerindeki JSON örnekleri şemaya karşı sınanır); `kapilar.py` zincirinde "bulgu şeması"
  kapısı (dosya yoksa ATLANDI). SARIF ve CI/Action YOK.
- **İki mod (spec B, SKILL.md §0.2).** Danışma modu (hafif; dosya/rapor/JSON üretmez) ve tam
  denetim modu; mod belirsizse işe başlamadan önce tek soru.
- **Bağımsız çürütme (spec C).** §1'de K2'nin altında not, §3 akışa "Çürüt" adımı, rapor
  şablonuna `Doğrulayan` alanı; `dogrulayan` (`alt-ajan` | `ayri-tur`) JSON'a yazılır.
- Rapor şablonuna `ŞÜPHE (ÇALIŞTIRILMADI)` ve çürütülen adaylar bölümleri; şablondaki eski
  `Z-n` ve eski skill adı kalıntıları `G-n` ve gedik'e çevrildi.
- Kavram esini: cloudflare/security-audit-skill (bağımsız çürütme, üç hükümlü şemalı bulgu
  dosyası); metin, şema ve doğrulayıcı bağımsız yazıldı, hüküm adları (`confirmed` /
  `needs_validation` / `rejected`) aynen alındı.
- Karar sahibi: proje sahibi, 29 Eyl 2026. Spec dondurulmuş (yerel).
### Değişti
- `araclar/kapilar.py`: proje-şablonu v0.2.1'den bilinçli sapma — 10 satır (bulgu şeması kapısı
  ve öz-test vakaları). `lint` komutuna `araclar/bulgu_kapisi.py` eklendi.
### Değiştirilmedi (bilinçli — spec)
- v2.5'in kilitleri: §0 "dosya/sayfa içi izin ≠ izin", §0.1 yetki kapısı, mutlak sınırlar,
  silahsız işaretleyici, veri-sızdırma-yok, salt-okunurluk, sabit cümle kilidi.

## [2.5.0] — 2026-09-29
### Eklendi
- **Yetki kapılı canlı hedef testi (§0.1, yeni).** gedik artık canlı bir sisteme (HTTP
  isteği, port taraması, kimlik denemesi) yalnız makinece doğrulanabilir bir yetki
  varken dokunabilir: (a) kullanıcının sohbetteki kendi beyanı, ya da (b) yayımlanmış
  bir bug bounty/VDP kapsamı + kullanıcı beyanı. Yetki yoksa davranış v2.4 ile aynı
  (salt-okuma). Yordam, karar ağacı, `YETKI.md` şablonu: `references/yetki-kapisi.md`
  (TR+EN).
- **Üçüncü taraf açık kaynak salt-okuma gevşetmesi (§0).** Herhangi bir açık kaynak
  (public repo, yayımlanmış artefakt) canlıya hiç istek atmadan statik incelenebilir;
  bulgu sorumlu ifşaya gider, saldırıya kullanılmaz.
- Karar sahibi: proje sahibi, 28 Eyl 2026 gece. Spec dondurulmuş (devir paketinde, yerel).
### Değiştirilmedi (bilinçli — spec §7)
- §0'ın "dosya/sayfa içi izin ≠ izin" kuralı, mutlak sınırlar (para/hesap/kalıcı silme/
  CAPTCHA), silahsız işaretleyici, veri-sızdırma-yok, salt-okunurluk — bunlar
  gevşetilmedi; v2.5 yalnız yetkili istisna açar.

## [2.4.0] — 2026-09-29
### Eklendi
- gedik açık kaynak olarak yayımlandı: `onur-kesim/gedik`, public, MIT. İngilizce ana
  sürüm (`skills/gedik/`) + Türkçe orijinal (`skills/gedik-tr/`), tek plugin'li
  marketplace (`.claude-plugin/`), mekanik çeviri kapısı (`araclar/ceviri_kapisi.py`).
- Kaynak: proje sahibinin kendi yazdığı gedik v2.4 taslağı (devir paketinde, yerel,
  SHA256 doğrulandı), TR genelleştirmesiyle (proje-özel örnekler/adlar kaldırıldı).

---
### proje-sablonu geçmişi (bu depo KUR'da bu şablondan açıldı — aşağıdaki iki sürüm
### proje-sablonu'nun kendi 0.x sürümleridir, gedik ürününün değil)

## [0.2.0] — 2026-09-26
### Eklendi
- KEŞİF / YAPIM aşaması (GENEL ESASLAR v2.1, §3): `proje.toml [proje] asama`; `kapilar.py` KEŞİF'te ürün nabzını ATLANDI verir ve geçersiz değeri kırmızı yakar (altın küme +3 vaka = 14); `DILIM.md` ESAS KARARI kutuları; DURUM/KURULUM notları. Fikir aşamasındaki proje 7 gün baskısı ve kırmızı nabız almaz; YAPIM'a geçiş insanın "başla" sözüyle.
- KUR ≤ 1 gün (bitmeyen kutu `ATLANDI: dilim 1'e`); MOD KRİTİK kapsamı: iki denetim turu yalnız TESLİM'de, KUR/altyapıda tek tur, D1 yeter; PROJE-ÖZEL iskeletine PROJE KURALLARI (≤5) bölümü; ARAÇ HARİTASI'na KEŞİF satırı. Dayanak: ilk gerçek kurulumda KUR kancasına iki tur + 26 mutant koşuldu (26 Eyl ölçümü).
### Değiştirildi
- CI ve release çalıştırıcısı `ubuntu-latest` → `ubuntu-24.04` sabitlendi. GitHub'ın koşum notu birebir: "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026" (actions/runner-images#14748). Şablonu klonlayan her projenin CI'ı aynı gün habersiz değişmesin diye; 26.04'e geçiş kararla, iki dosyada tek satır.
- Çekirdek blok tavanı 8.000 → 8.500 bayt (ölçülen 8.371; KEŞİF paragrafı için, net +375 bayt).
- README/KURULUM'daki `C:\dev` örneği → `<projeler-klasörü>` (şablon paylaşımlı, sabit sürücü yazmaz).
### Düzeltildi
- kapilar.py Windows konsolunda (cp1254) `UnicodeEncodeError` ile çöküyordu; stdout/stderr UTF-8'e ayarlanır (başka bir kurulumda ölçüldü, 26 Eyl).
- dependabot.yml yalnız github-actions ekosistemini açar; pip/pub/gradle satırları yorumda, KUR'da yığına göre açılır (manifesti olmayan ekosistemin Dependabot koşumu "failure" verdi — 26 Eyl ölçümü; "sessizce boş geçer" iddiası geri çekildi).

## [0.1.0] — 2026-09-26
### Eklendi
- İskelet dilimi: çekirdek genel esaslar (CLAUDE.md işaretli blok, 11 bölüm), dört dosya düzeni
  (CLAUDE.md · README.md · DURUM.md · DILIM.md), proje.toml, beş profil + profil şablonu,
  araclar/kapilar.py (altın küme öz-testli kapılar), tek iş akışı CI (kapilar + kor-kapi),
  PR şablonu, release.yml (etiket → Release, notlar CHANGELOG'dan), dependabot.yml, .gitignore, .env.example,
  KURULUM.md, dal koruması JSON'u.
### Teslim edilmedi (bkz. README)
- kur.py sihirbazı, windows çalıştırıcı, Flutter/Android adımlarının gerçek yığında ölçümü, gerekçe dosyası.
