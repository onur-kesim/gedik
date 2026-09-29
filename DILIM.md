# DILIM — gedik-v2.6 (makine-okur çıktı + iki mod + bağımsız çürütücü)     açıldı: 2026-09-29 · aşama: DOĞRULA · sürüm dilimi: EVET (2.6.0)
Hedef: dondurulmuş v2.6 spec'ini uygulamak (`_calisma/SINIR_SPEC_GEDIK_v2.6_2026-09-29.md`, yerel): A) `gedik-bulgular.json` +
`araclar/bulgu-semasi.json` + `araclar/bulgu_kapisi.py` (kör kapı testli, `kapilar.py` zincirinde), B) SKILL.md §0.2 iki mod,
C) bağımsız çürütücü (§1 K2 altı not, §3 "Çürüt" adımı, rapor şablonunda `Doğrulayan`). Sürüm 2.6.0.
Dal: `dilim-4-makineokur-v2.6` ← `dilim-3-sinir-spec-v2.5`. v2.5 dilimi TESLİM'de bekliyor (etiket/CHANGELOG/PR/push/insan; kaydı
`git show 26a8291:DILIM.md`, 3. denetim TESLİME UYGUN); v2.5 push edilmeden v2.6 push edilmez (spec §0).
Kabul (spec KABUL): kapı şemayı doğruluyor, iki aykırı kayıtta KIRMIZI · üç mevcut kapı yeşil, JSON kapısı `kapilar.py` özetinde ·
§0.2 + §1 notu + §3 adımı TR+EN, çeviri kapısı + sabit cümle kilidi PASS · sürüm 2.6.0 dört yerde · iç ad kapısı 0, Cloudflare
metni kopyalanmadı, "better than" yok · v2.5 kilitlerine dokunulmadı.

## YAP
- [x] başka açık dilim yok — v2.5 TESLİM'de bekliyor, WIP fiilen 1 (spec: v2.6 v2.5'in üstüne ayrı dilim)
- [x] A) şema + kapı + `kapilar.py` bağlantısı (+10 satır, şablon v0.2.1'den bilinçli sapma) + kör kapı öz-testi
- [x] B) `SKILL.md §0.2` (TR+EN)
- [x] C) §1 K2 altı not + §3 adım 6 "Çürüt" + rapor şablonu `Doğrulayan` (TR+EN); referans §4.1 (üç hüküm, alan sözlüğü, örnek)
- [x] sürüm 2.6.0: plugin.json, marketplace.json, SKILL.md×2
- [x] README×2 + CHANGELOG [2.6.0] + `lint` komutu (proje.toml = CLAUDE.md) güncellendi (belge = gerçek)

## DOĞRULA
- [x] `kapilar.py` tam: 7 PASS · 0 FAIL · 4 ATLANDI · 0 ÖLÇÜLEMEDİ (bulgu şeması: ATLANDI — depoda gedik-bulgular.json yok), altın küme 21/21, `kapilar.py` 393 satır
- [x] `ceviri_kapisi.py` 12/12 + sabit cümle kilidi 25/25 PASS; `--pozitif-kontrol` üç mutasyon KIRMIZI · `ic_ad_kapisi.py` 54 dosya/31 desen 0 eşleşme
- [x] kör kapı (spec A): needs_validation+siddet ve confirmed−poc_girdi KIRMIZI; öz-test 68 aykırı girdi KIRMIZI + 22 geçerli varyant + temiz örnek YEŞİL
      + kapı yolu (dosya yok→ATLANDI, açık yol yok→FAIL, BOM, çıkış kodları, `kapilar.py` zincirine bağlantı) + belge örnekleri (TR+EN) şemaya karşı
- [x] öz-testin gücü: 218 tek-noktalı mutant (152 şema + 66 kod/zincir) → 205 yakalandı; hayatta 13 = 8 eşdeğer (`if.required`, `hukum`/`durum` zaten zorunlu),
      2 eşdeğer (tür koruması), 3 koşum artığı (`--pozitif-kontrol` dalı, `__main__`); 1. turda denetçinin 159'luk kümesinde 59 hayatta (42 gerçek zayıflama) vardı; bu kümede gerçek zayıflama 0
- [x] zincir deneyi (repo dışı kopya): zayıflatılmış şema → öz-test KIRMIZI, çıkış 2 · bozuk gedik-bulgular.json → FAIL, çıkış 1 · temiz → PASS
- [x] Cloudflare metni: eklenen satırlar × 21 dosya, 5 kelimelik ortak dizi 0 (2026-09-29)
- [x] v2.5 kilitleri (SKILL §0/§0.1/§6, `sabit_cumleler.json`, `yetki-kapisi.md`) HEAD ile aynı (2. tur denetçisi de teyit etti)
- [x] sabit cümle kilidi genişletildi (Cowork 4. denetim önerisi; kullanıcı: "eklersen"): v2.5'in 10 kilidi DEĞİŞMEDİ (diff yalnız ekleme, 0 silinen satır), 15 v2.6 cümlesi eklendi
      (§0.2 mod geçişleri, çürütücü, "çürütülemezse confirmed kalır", §4.1 şiddet/ÖLÇÜLMEDİ/yerine geçmez/yazım konumu/şema) → 25 cümle × TR+EN birebir
- [x] kilit pozitif kontrolü: `ceviri_kapisi.py --pozitif-kontrol` mutasyon C (kalıcı): her kilit her tarafta bir sözcük silinince KIRMIZI + cümle dosyada tek yerde;
      15 yeni kilit × TR/EN × 4 mutasyon türü = 120 mutasyon, kaçan 0; ilk denemede bir EN cümle SKILL.md'de iki yerde geçtiği için zayıf çıktı → benzersizleştirildi;
      bilerek zayıf bir kilitle C KIRMIZI yaktı (kör değil)
- [x] belge → JSON: yalnız skill belgelerini okuyan ajanlar (TR ve EN, 2 tur, 4 koşu) şemaya bakmadan gedik-bulgular.json yazdı; 4/4 kapıdan PASS
- [x] bağımsız denetim (Cowork, ayrı bağlam, salt-okunur) — 4. denetim, 2026-09-29: **TESLİME UYGUN** (küçük eksik: v2.6 cümleleri kilitsiz → kapatıldı, yukarıdaki iki kutu)
- [x] NE ÖLÇÜLEMEDİ yazıldı (aşağıda)

## TESLİM
- [ ] README (v2.6 konumlandırması) ve DURUM dört sayı güncel — README yazıldı; dört sayı TESLİM'de
- [ ] git etiketi (`v2.6.0`) — v2.5.0'dan sonra
- [ ] PR açıldı, kullanıcı onayıyla push edildi — anayasa §8 "push et"
- [ ] bir insana gösterildi / alıcı aldı: `<kim, ne zaman>`

## SÜRÜM (sürüm dilimi — profil yazilim §6 SÜRÜM kapıları)
- [x] sürüm artefaktı hijyeni: gizli anahtar taraması 54 dosya 0; iç ad kapısı 0; debug bayrağı/test ucu yok
- [ ] geri alma planı: `git revert` bu dilimin commit'i → v2.5.0 davranışı (JSON çıktısı, §0.2, çürütme adımı kalkar; `kapilar.py` +10 satır geri gider)

## DENETİM
**4. denetim — Cowork (ayrı bağlam, salt-okunur) · 2026-09-29 · hüküm: TESLİME UYGUN.** Şema kuralı bağımsız doğrulandı: `confirmed` + PoC yok RED, `needs_validation` + şiddet RED
— kapı kör değil. Kapılar 7 PASS/0 FAIL; çeviri + sabit cümle + iç ad 0. Küçük eksik (bloker değil): v2.6'nın yeni cümleleri (§0.2 mod geçişi, "çürütülemezse `confirmed` kalır")
`sabit_cumleler.json`'da yok → KAPATILDI: 15 cümle eklendi, pozitif kontrol koşuldu (DOĞRULA).
İç turlar (ayrı bağlamlı ajanlar; resmî denetim değil):
1. tur, 6 ajan: çeviri eşitliği TESLİME UYGUN (8 DÜŞÜK) · spec uyumu DÜZELT (3 ORTA) · kapı kırma DÜZELT (3 ORTA) · entegrasyon DÜZELT (1 YÜKSEK, 7 ORTA) ·
belge→JSON TR ve EN PASS. Kapatılanlar: açık `--dosya` yolu yoksa ATLANDI (→FAIL); `bulgu_id` `G-1\n` deliği; `if` içinde yutulan şema hatası;
RecursionError; öz-test kapsamı (59→0 gerçek hayatta mutant); `needs_validation`/`rejected` zorunlu alanları spec-harfiyen; "varsayılan" ↔ "mod belirsizse sor" çelişkisi;
rapor/doğrulayıcı konumu; kanıt türü ↔ hüküm eşlemesi; örnek G-1 şiddeti (§4 → KRİTİK); README/CHANGELOG atıf ve sayılar; lint komutu.
2. tur, 4 ajan: TR↔EN eşitliği TESLİME UYGUN (1 DÜŞÜK: EN "touching any file" → düzeltildi) · regresyon DÜZELT (1 YÜKSEK, 4 ORTA, 5 DÜŞÜK) · belge→JSON TR ve EN PASS.
Regresyonun YÜKSEK/ORTA'ları kapatıldı: kanıt türü eşlemesi mevcut belgelerle (SS1, SS5, şablon, serit-E E6) çeliştiği için `KOŞULDU`/`STATİK`→`confirmed`,
`ÖLÇÜLMEDİ` etiketli aday→`needs_validation` olarak yeniden yazıldı; danışma modu sınırları ve "denetle" + odaklı kapsam tie-break'i eklendi; öz-teste BOM,
belge-örneği pozitif kontrolü ve `kapilar.py` zincirine bağlantı eklendi. Bilerek AÇIK bırakılanlar: DEVİR'de.

NE ÖLÇÜLEMEDİ: çürütücünün ve iki modun canlı ajanda davranışı (skill talimat dosyası; yalnız metin düzeyi + 4 sentetik belge→JSON koşusu) · gerçek bir denetimin
ürettiği gedik-bulgular.json · `bulgu-semasi.json`'un gerçek bir draft-07 doğrulayıcısıyla (jsonschema/ajv) eşitliği (kurulu değil; `\Z`/ECMA farkı elle giderildi) ·
`/plugin install` sonrası `<eklenti-kökü>/araclar/` yolunun kurulu eklentide çözülmesi · CI (ubuntu-24.04 + windows-latest; push sonrası) · SARIF/CI çıktısı (spec: kapsam dışı) ·
`ayri-tur` değerinin gerçekten "gerekçe-görmeyen" olduğu (öz-beyan; kapı doğrulayamaz) · v2.6 cümlelerinin kilit DIŞINDA kalanları (yalnız 15 kritik cümle kilitli; gerisi elle okundu).

## Sonuç
Uygulama + iç doğrulama + Cowork 4. denetimi (TESLİME UYGUN) tamam; kilit eksiği kapandı. Kalan TESLİM kutuları (dört sayı, etiket, PR, insan) push'a bağlı.
Push YOK — v2.5 ve v2.6 yalnız kullanıcının "push et" demesiyle, v2.5 önce.
