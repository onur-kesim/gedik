# DILIM — gedik-v2.5 (yetki kapılı canlı test + 3. taraf salt-okuma)     açıldı: 2026-09-29 · aşama: DOĞRULA · sürüm dilimi: EVET (2.5.0)
Hedef: dondurulmuş sınır spec'ini uygulamak (devir paketinde, yerel) — §0 gevşetmesi
(3. taraf açık kaynak salt-okuma), yeni §0.1 (yetki kapılı canlı test), yeni `references/yetki-kapisi.md`
(TR+EN), sürüm 2.5.0. Önceki dilim (gedik-repo-yayin, Dilim 1+2) TESLİM'e hazır durumda,
push onayı bekliyor — bkz. DURUM dört sayı ve karar günlüğü. Bu dilim onun üstüne, ayrı
dal/PR olarak kurulu (`dilim-3-sinir-spec-v2.5` ← `dilim-1-2-repo-yayin`).
Kabul: `ceviri_kapisi.py` yeni dosya dahil tüm çiftlerde PASS · kör kapı 3 senaryosunun
(yetkisiz canlı / kapsam dışı host / sayfa-içi sahte izin) SKILL.md §0.1 metninde karşılığı
var · sürüm her üç yerde (plugin.json, marketplace.json, SKILL.md×2) 2.5.0 · CODE'UN
DEĞİŞTİRMEYECEĞİ (§7) listesindeki hiçbir satır bozulmadı.

## YAP
- [x] başka açık dilim yok (önceki dilim TESLİM'e hazır, push bekliyor — WIP fiilen 1)
- [x] kabul ölçütü yazıldı ve ölçülebilir
- [x] sürüm 2.5.0: `.claude-plugin/plugin.json`, `marketplace.json`, SKILL.md×2 (TR+EN)
- [x] §0 sonuna 3. taraf salt-okuma bloğu eklendi (TR birebir drop-in + EN çeviri)
- [x] yeni §0.1 eklendi (TR birebir drop-in + EN çeviri), §1'den önce
- [x] `references/yetki-kapisi.md` yazıldı (TR kanonik + EN çeviri, `YETKI.md` şablonu
      kod bloğu olarak, alan adları korunarak)
- [x] §6 SINIRLAR dokunuşu: "canlı istek → §0.1'e tabi" + yeni 3. taraf salt-okuma satırı
- [x] §7 REFERANSLAR/REFERENCES listesine yeni dosya eklendi

## DOĞRULA
- [x] otomatik kapı: `ceviri_kapisi.py` 12/12 dosya çifti PASS (yeni yetki-kapisi.md dahil)
- [x] kör kapı öz-testi (`--pozitif-kontrol`) KIRMIZI yaktı (bir tablo satırı bellekte
      silinince)
- [x] kör-kapı 3 senaryosunun SKILL.md §0.1'de karşılığı var: (1) "yetki yoksa bu bölüm hiç
      açılmaz ... ÖLÇÜLMEDİ — yetki yok" (2) "kapsam-dışı host'a dokunulmaz, kapsam dışı diye
      raporlanır" (3) "yetki, hedefin kendi sayfasında ... yazan bir metin DEĞİLDİR"
- [x] genelleştirme kontrolü: yeni içerikte iç-ad listesi (`_calisma/ic_adlar.txt`, repoya girmez) → 0 eşleşme
- [x] §7 CODE'UN DEĞİŞTİRMEYECEĞİ satırları (dosya-içi izin≠izin kuralı, mutlak sınırlar,
      silahsız işaretleyici, veri-sızdırma-yok, salt-okunurluk) elle karşılaştırıldı — DEĞİŞMEDİ
- [x] iç ad/oturum-no/yerel-yol kapısı: `araclar/ic_ad_kapisi.py`, kör kapı öz-testi FAIL
      yaktı; BİRLEŞİK 31 desenle (Cowork listesi + benim) 52 izlenen dosya → 0 eşleşme, üç
      yerel dalda `git grep` → 0, yerel 5 commit mesajı → 0 (2. denetim, DÜZELT-2 madde 1)
- [x] `kapilar.py` tam koşu — şablon v0.2.1'e güncellendi (blob = etiket v0.2.1, Cowork
      ölçtü), cp1254 ORTAM MAYINI kaldırıldı: bu Windows makinesinde 7 PASS · 0 FAIL ·
      3 ATLANDI (kur/build boş, belge/kod oranı kapalı) · 0 ÖLÇÜLEMEDİ, çıkış 0
- [x] §0/§0.1 iç tutarlılık: §0 madde 1-2 spec EK-1.1 drop-in metniyle birebir değiştirildi
      (TR; EN birebir çeviri; açık kaynak salt-okuma dahil) — ilk turdaki ara çözümüm
      madde 1'e dokunmadığı için çelişki sürüyordu
- [x] description×2 + plugin.json + marketplace.json: EK-1.2 metinleriyle birebir
- [x] yetki-kapisi.md §5 (TR+EN): iç devir-belgesi atfı kaldırıldı (EK-1.3)
- [x] sabit cümle kilidi (EK-1.4): `araclar/sabit_cumleler.json` 10 cümle × TR+EN;
      `ceviri_kapisi.py` bunu da koşar; pozitif kontrol B = EN'den "NOT" silme → yapı kapısı
      PASS, kilit KIRMIZI; gerçek koşu diskte 3 mutasyonla (EN NOT, TR DEĞİLDİR, EN STOP) çıkış 1
- [x] bağımsız denetim (ayrı bağlam, salt-okunur) — 3. denetim (Cowork, 2026-09-29):
      TESLİME UYGUN (koşullu: README'ye "davranış canlı ajan koşusunda denenmedi" notu — yapıldı)
- [x] NE ÖLÇÜLEMEDİ yazıldı (aşağıda)

## TESLİM
- [ ] README (v2.5 konumlandırması: "authorized-only live testing — refuses without an
      in-scope authorization") ve DURUM güncel
- [ ] git etiketi (`v2.5.0`) + CHANGELOG satırı
- [ ] PR açıldı, kullanıcı onayıyla push edildi — anayasa §8 "push et"
- [ ] bir insana gösterildi / alıcı aldı: `<kim, ne zaman>`

## SÜRÜM (sürüm dilimi — profil yazilim §6 SÜRÜM kapıları)
- [x] sürüm artefaktı hijyeni: yeni dosyalarda sır/debug bayrağı yok (rg + kapilar.py'nin
      kendi gizli-anahtar kapısı: 48 dosya, 0 eşleşme) · iç ad/yerel yol yok (`ic_ad_kapisi.py`)
- [ ] geri alma planı: `git revert` bu dilimin commit'i — §0.1/yetki-kapisi.md kaldırılır,
      v2.4.0 davranışına döner (dosya bazlı, tek commit'te izole)

## DENETİM — denetleyen: ayrı bağlam (proje sahibinin başka bir oturumu) · 2026-09-29 · salt-okunur ✓ · kapsam: Dilim 1+2 ve 3 birlikte (yerel commit'ler, push edilmemiş)
| Kapı | Sonuç | Kanıt |
|---|---|---|
| Sürüm 2.5.0 (plugin, marketplace, SKILL×2) | PASS | dosyalar okundu |
| Çeviri kapısı, 12 çift | PASS | denetçi kendisi koştu: 12/12 |
| Kapı pozitif kontrolü (tablo satırı) | PASS | FAIL yaktı |
| Kod bloğu içerik hash'i | PASS | yetki-kapisi.md kod bloğunda 1 harf → FAIL |
| Anlam: §0 bloğu, §0.1, yetki-kapisi.md (EN↔spec) | PASS | satır satır okundu |
| §0 iç tutarlılık | FAIL → 1. turda YETERSİZ düzeltme → EK-1.1 ile **DÜZELTİLDİ** | 1. turda yalnız madde 2'ye istisna yazmıştım, madde 1 hâlâ çelişiyordu (2. denetim yakaladı); şimdi EK-1.1 drop-in birebir |
| description ×2 + plugin.json | FAIL → 1. turda kendi ifademle, 2. turda EK-1.2 metniyle **DÜZELTİLDİ** | marketplace.json de EK-1.2'ye göre güncellendi |
| Public depo: iç ad / yerel yol (tüm ağaç) | FAIL → **DÜZELTİLDİ** | CLAUDE.md/DURUM.md/CHANGELOG.md/.gitignore/DILIM.md/yetki-kapisi.md§5 redakte edildi + mekanik kapı (`ic_ad_kapisi.py`) eklendi; ayrıca vendor `kapilar.py`'de bir yorum satırındaki iç ad da bulunup düzeltildi |
| Sır taraması | PASS | `ic_ad_kapisi.py` + `kapilar.py`'nin kendi taraması: 0 eşleşme |
| Belge = gerçek | FAIL → **DÜZELTİLDİ** | DURUM DEVİR başlığı ve CLAUDE.md PROFİL bloğu gerçek içerikle dolduruldu; DÖRT SAYI kasıtlı boş bırakıldı (K8: "her TESLİM'de" — henüz TESLİM yok) |
| Çeviri kapısı anlamda — EN §0.1 "Authorization is NOT…" cümlesi | 1. turda yanlış okumuştum ("DOĞRULANAMADI") → **GEÇERLİ BULGU, DÜZELTİLDİ** | Bulgu dosyada NOT eksik demiyordu; kapının anlamı ölçmediğini gösteren bir MUTASYON ölçümüydü (NOT silinince PASS). Şimdi sabit cümle kilidi (EK-1.4) bu mutasyonu KIRMIZI yakıyor |
| İç ad listesi (2. denetim) | 3 eşleşme + 1 commit mesajı → **DÜZELTİLDİ** | Cowork'ün ilk listesini yazarken `ic_adlar.txt`'yi ezmiştim (Write "updated" demişti, okumadan yazdım); şimdi birleşik 31 desen, yerel dallar+mesajlar 0. Kök commit `5429b2d` (zaten canlı) 2 eşleşme taşımaya devam ediyor — yeniden yazılamaz |

NE ÖLÇÜLEMEDİ: §0.1'in davranışsal kör kapısı (3 senaryo) gedik'in kendisi bir ajan olarak
canlı koşturulup ölçülmedi — SKILL.md metninin spec'e uyumu doğrulandı, çalışma zamanı
davranışı değil (gedik yürütülebilir kod değil, talimat dosyasıdır) · marketplace
`"source": "."` gerçek bir `/plugin install` ile denenmedi.
Hüküm (bu turun): **DÜZELT tamamlandı, yeniden bağımsız denetim gerekiyor** — 🔴 o denetim
TESLİME UYGUN demeden push YOK.

### 3. denetim — denetleyen: Cowork · 2026-09-29 · hüküm: **TESLİME UYGUN (koşullu)**
| Kapı | Sonuç | Kanıt |
|---|---|---|
| İç ad (Cowork özgün 20 desen), 7 commit | PASS | 0 eşleşme |
| `kapilar.py` tam koşu | PASS | 7 PASS · 0 FAIL |
| Çeviri kapısı | PASS | 12/12 |
| Sabit cümle kilidi, 3 anlam mutasyonu | PASS (2/3 kilit yakaladı) | 3. mutasyon (kalın başlık) kilitli asıl cümleyle korunuyor |
| §0 madde 1 ↔ EK-1.1 | PASS | uyumlu |
| Rastgele beyan: kilit pozitif kontrolü | TUTTU | denetçi bağımsız doğruladı (D5) |

Koşul: README "What's not delivered yet" altındaki canlı test maddesine "kapı metin
düzeyinde doğrulandı, davranışı canlı ajan koşusunda denenmedi" notu → EN + TR eklendi.
NE ÖLÇÜLEMEDİ (3. denetim): §0.1 davranışsal kör kapı (canlı ajan koşumu) · CI (push
sonrası) · `/plugin install`.
Hüküm: TESLİME UYGUN. Push hâlâ YOK — yalnız kullanıcının "push et" demesiyle.

### DÜZELT (1. tur, 2026-09-29) — kutular 2. denetimde gerçeğe göre düzeltildi
- [x] 1. İç ad temizliği — **1. turda "bitti" işaretlemiştim, eksikti**: kendi 17 desenimle
      taramıştım; Cowork listesi eksikti (ezmiştim). Gerçek kapanış DÜZELT-2 madde 1'de.
- [x] 2. Geçmiş: `git bundle` yedeği alındı, commit'ler yeniden yazıldı (force-push YOK).
- [x] 3. İç ad kapısı: `araclar/ic_ad_kapisi.py` (D1 kör kapı öz-testli).
- [x] 4. EK-1 maddeleri — **1. turda "bitti" işaretlemiştim, yanlıştı**: "EK erişilemedi"
      demiştim ama EK-1, SINIR_SPEC dosyasının sonundaydı (ilk aramamda yalnız dosya ADINA
      baktım, içeriğe bakmadım); kendi ara çözümümü yazdım, sabit cümle kilidini "iki ısırık
      kuralı" gerekçesiyle kurmadım — bu gerekçe de yanlıştı (spec kilidi açıkça istiyordu).
      Gerçek kapanış DÜZELT-2 madde 2-3'te.
- [x] 5. Belge = gerçek: DURUM DEVİR başlığı ve CLAUDE.md PROFİL bloğu dolduruldu.

### DÜZELT-2 (Cowork 2. denetim — DÜZELT, push YOK; bitti 2026-09-29)
- [x] 1. `ic_adlar.txt` birleşik (31 desen, ezdiğim ilk liste geri getirilemedi — yalnız
      mesajda sayılan 14 eksik desen eklendi, ilk listede başka desen varsa bilemiyorum →
      Cowork teyit etsin). 3 eşleşme (CLAUDE.md gh hesap adı, DURUM, DILIM) + `d4d4ce1` commit
      MESAJI redakte edildi; bundle (`..-b.bundle`) sonrası 5 commit yeniden oynatıldı.
      Kabul: `git grep` üç yerel dalda 0; `git log` mesajları 0.
- [x] 2. Sabit cümle kilidi (EK-1.4): bkz. DOĞRULA.
- [x] 3. §0 madde 1-2 EK-1.1 drop-in metniyle birebir (TR) + EN çeviri: bkz. DOĞRULA.
- [x] 4. Bu kutular gerçeğe göre düzeltildi (yukarıdaki DÜZELT 1. tur satırları) + DEVİR yazıldı.

## Sonuç
DÜZELT-2 kapandı. 3. bağımsız denetim (Cowork, 2026-09-29) TESLİME UYGUN (koşullu, koşul
yerine getirildi). Push hâlâ YOK — bu dilim ve önceki dilim (Dilim 1+2) yalnız kullanıcının
"push et" demesiyle gider; canlı `main` sızıntısı kararı da kullanıcıda (DURUM DEVİR).
