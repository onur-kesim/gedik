# DURUM — gedik

## DEVİR O2 · 2026-09-29 · yazan: Claude Code · N=—
Aşama: YAPIM (proje.toml asama). Yerel zincir (hiçbiri push edilmedi): `5429b2d` (canlı kök) →
KUR → Dilim 1+2 → Dilim 3 (v2.5) → kapilar.py v0.2.1+CI → DEVİR O1 → DÜZELT-2 → DEVİR O2.
Dallar: main = KUR · dilim-1-2-repo-yayin = Dilim 1+2 · dilim-3-sinir-spec-v2.5 = tepe.
Boş kutu: bağımsız denetimin TESLİME UYGUN hükmü (Cowork 2. denetimi DÜZELT verdi, aşağıdaki
DÜZELT-2 bitti ama taze tur koşmadı).
Son yapılan (Cowork 2. denetim, DILIM.md DÜZELT-2): (1) `_calisma/ic_adlar.txt` birleşik 31 desen;
3 eşleşme + `d4d4ce1` commit MESAJI redakte edildi, önce yeni bundle (`..-b.bundle`), sonra 5 commit
yeniden oynatıldı — `git grep` üç yerel dalda 0, yerel commit mesajlarında 0. (2) Sabit cümle
kilidi (EK-1.4): `araclar/sabit_cumleler.json` 10 cümle × TR+EN, `ceviri_kapisi.py` koşuyor;
pozitif kontrol EN'den "NOT" silme (yapı PASS, kilit KIRMIZI), gerçek koşu 3 diskte mutasyonla
çıkış 1. (3) §0 madde 1-2 EK-1.1 drop-in birebir (TR+EN); description×2+plugin.json+
marketplace.json EK-1.2 birebir. (4) DILIM DÜZELT kutuları gerçeğe göre düzeltildi.
Yarım kalan: bağımsız denetim turu (DÜZELT-2 sonrası) koşmadı.
Kendi hatalarım (2. denetimde ortaya çıktı, DILIM'de kayıtlı): `ic_adlar.txt`'yi okumadan yazıp
Cowork'ün ilk listesini ezmiştim (geri getirilemedi; yalnız mesajda sayılan 14 eksik desen
eklendi — ilk listede başka desen varsa bilemiyorum, Cowork teyit etsin) · EK-1'i dosya ADIYLA
arayıp "erişilemedi" demiştim, oysa SINIR_SPEC dosyasının sonundaydı · "NOT" bulgusunu yanlış
okuyup "doğrulanamadı" yazmıştım (bulgu kapının anlam-körlüğünü ölçen bir mutasyondu, geçerli).
🔴 Açık/kritik: **`onur-kesim/gedik` `main` (origin) depo oluşturulduğundan beri (2026-09-28
20:58 UTC) PUBLIC ve canlı; tek commit'i (`5429b2d`, şablon) hâlâ 2 iç-ad eşleşmesi taşıyor**
(CHANGELOG.md + araclar/kapilar.py yorumu, bkz. `_calisma/ic_adlar.txt`). Yerel geçmiş temiz,
uzak değil; düzeltme yalnız push/force-push ile olur — karar kullanıcıda ("push YOK" sürüyor).
Sıradaki ilk iş: 1) bağımsız denetimi tazeden koştur (ayrı bağlam, salt-okunur) 2) Cowork
`ic_adlar.txt` ilk listesini teyit etsin 3) TESLİME UYGUN ise kullanıcıdan (a) canlı `main`
sızıntısı için karar (küçük düzeltme push'u / force-push / depoyu geçici private) ve (b) yerel
commit'lerin push'u için "push et" iste.
Açık karar / bloker: bağımsız denetim + canlı main kararı + push onayı kullanıcıda.
Araç eksiği: `ceviri_kapisi.py` (sabit cümle kilidi dahil) ve `ic_ad_kapisi.py` CI'da KOŞMUYOR
(proje.toml test = yalnız kapilar.py; ic_ad_kapisi `_calisma/`ya bağlı, CI'da ATLANDI verir) —
D2: en geç sonraki teslimde CI'ya bağlanmalı, kullanıcı kararı bekliyor.
Dosyalar: SKILL.md×2 (skills/gedik-tr, skills/gedik), araclar/ceviri_kapisi.py,
araclar/sabit_cumleler.json, araclar/ic_ad_kapisi.py, .claude-plugin/*.json, DILIM.md, DURUM.md
Uyarı: (1) `_calisma/gedik-yerel-yedek-2026-09-29.bundle` ve `..-b.bundle` ESKİ kirli geçmişleri
taşır — yalnız yerel, gitignore'lu, asla push edilmeyecek. (2) PR gövdesine iş emri §5'teki
"genelleştirme diff'i"ni YAPIŞTIRMA: ham diff silinen satırlarda iç adları içerir; özet
(satır/dosya sayısı) yaz, ham diff yerelde (`_calisma/genellestirme_diff.txt`) kalsın;
`_calisma/pr_body.md` taslağı bu yüzden olduğu gibi kullanılmamalı.
Yeni oturumda yaz:  gedik · O3 · başla

## DÖRT SAYI (her TESLİM'de bir satır — K8; KEŞİF'te nabız sütununa "KEŞİF" yazılır)
| tarih | ürün nabzı (gün) | açık dilim yaşı (gün) | kapı kırmızı | sayaç |
|---|---|---|---|---|

## KARAR GÜNLÜĞÜ (sona eklenir, silinmez; tek satır, tarihli)
- 2026-09-29 — proje-sablonu'ndan (onur-kesim/proje-sablonu, `main`) klonsuz kuruldu; `gh repo create onur-kesim/gedik --template onur-kesim/proje-sablonu --public`.
- 2026-09-29 — AŞAMA doğrudan YAPIM ile açıldı (KEŞİF atlandı): iş emri ve sınır tasarımı proje sahibi tarafından zaten kilitlenmiş kararlar olarak geldi (devir paketindeki açılış notu, yerel).
- 2026-09-29 — **public depo — bilinçli sapma** (şablonun varsayılanı private). Gerekçe: yıldız ve awesome-list başvurusu için gerekli. Karar sahibi: proje sahibi, 28 Eyl 2026 gece. Public depoya kişisel veri/müşteri adı/iç proje adı girmeyecek şekilde denetlendi (29 Eyl'de bir tur daha: bkz. aşağıdaki denetim ve redaksiyon satırları).
- 2026-09-29 — kaynak (devir paketindeki taslak, yerel) SHA256SUMS.txt ile doğrulandı: 13/13 OK (iki kez).
- 2026-09-29 — Dilim 1 (iskelet + TR orijinal): `skills/gedik-tr/` oluşturuldu, iş emri §1'deki 6 genelleştirme uygulandı (proje-belleği dosya adı, iki araç örnek adı, bir uygulama adı ve bir kişi adı yer tutucusu genel ifadeye çevrildi; sürüm "v2.4"→"v2.4.0"; frontmatter name→gedik-tr). Mekanik kontrol (iç-ad listesi `_calisma/ic_adlar.txt`, repoya girmez) → 0 eşleşme; genel "tuzak" (trap) kelimesi 3 yerde bulundu, tümü ilgisiz (rapor/RLS bağlamında), değiştirilmedi.
- 2026-09-29 — Dilim 2 (EN çeviri): `skills/gedik/` (11 dosya) paralel ajanlarla çevrildi; `araclar/ceviri_kapisi.py` mekanik kapı yazıldı (başlık/tablo-satırı/kod-bloğu sayısı + kod bloğu hash eşitliği, `--pozitif-kontrol` kör kapı öz-testi dahil).
- 2026-09-29 — Dilim 1+2 anlam kontrolü: ayrı ajan (çeviriyi yazmamış) 3 rastgele + 2 ek bölümü TR↔EN karşılaştırdı, hepsi MATCH, düzeltme gerekmedi. Dilim yerelde TESLİM'e hazır (`dilim-1-2-repo-yayin` dalı); push kullanıcı onayı ("push et") bekliyor.
- 2026-09-29 — **v2.5 — yetki kapılı canlı test + üçüncü taraf salt-okuma; proje sahibinin 28 Eyl gece onayı (devir paketindeki açılış notu, yerel); gevşetilmez sınırlar korundu.** Sürüm 2.4.0→2.5.0 (plugin.json, marketplace.json, SKILL.md×2). Spec dondurulmuş (devir paketinde, yerel) — §0 sonuna 3. taraf açık kaynak salt-okuma bloğu + yeni §0.1 (canlı hedef testi, yetki kapısı) + yeni `references/yetki-kapisi.md` (TR+EN, `YETKI.md` şablonu) birebir uygulandı; §6 SINIRLAR dokunuşu yapıldı. `dilim-3-sinir-spec-v2.5` dalı (`dilim-1-2-repo-yayin`in üstünde), ayrı dilim olarak DILIM.md'de izleniyor.
- 2026-09-29 — **bağımsız denetim (ayrı bağlam) DÜZELT verdiği: iç proje adı/oturum no/yerel yol** `skills/` dışındaki dosyalarda (CLAUDE.md, DURUM.md, CHANGELOG.md, .gitignore, DILIM.md) ve `yetki-kapisi.md` §5'in dangling iç-belge atfında bulundu; §0/§0.1 arasında mantık çelişkisi (madde 1-2 hâlâ mutlak "asla" diyordu) ve description×2/plugin.json'da aynı çelişki tespit edildi. **G2 gereği yukarıdaki ve bu dosyanın diğer satırlarındaki iç ad/oturum-no/yerel-yol referansları redakte edildi (29 Eyl)** — devir paketi, iç proje adları ve mutlak yerel yollar genel ifadeyle değiştirildi, tarih ve karar özeti korundu. Ayrıntı: DILIM.md DENETİM tablosu ve DÜZELT listesi.
- 2026-09-29 — **DÜZELT kapandı (5/5).** İç ad kapısı (`araclar/ic_ad_kapisi.py`, D1 kör kapı öz-testli) yazıldı, 48 izlenen dosyada 0 eşleşme (vendor `araclar/kapilar.py`'deki bir yorumda da aynı iç ad bulunup düzeltildi). §0 madde 1-2 ve description×2+plugin.json §0.1 istisnasıyla uyumlu hâle getirildi (dondurulmuş spec'in EK'i bu oturumda erişilebilir değildi; minimal-diff çözüm elle türetildi). yetki-kapisi.md §5'teki iç-belge atfı kaldırıldı. DURUM DEVİR başlığı ve CLAUDE.md PROFİL bloğu gerçek içerikle dolduruldu. Git geçmişi (KUR/Dilim1+2/Dilim3, 3 commit) `git bundle` yedeğinden sonra temiz içerikle yeniden yazıldı — hiçbiri push edilmemişti, force-push değil.
- 2026-09-29 — araclar/kapilar.py şablon v0.2.1'e güncellendi (blob = etiket v0.2.1); Windows'ta tam kapı 7 PASS · 0 FAIL · 3 ATLANDI (Cowork ölçtü); cp1254 ortam mayını kaldırıldı. (Bir istisna: v0.2.1 blobundaki bir yorum satırı iç proje adı taşıyordu, public depo kuralı gereği o tek kelime redakte edildi — ayrıntı ilgili commit'te.) Önceden açılan görev önerisi bu yüzden geri çekildi.
- 2026-09-29 — Çeviri kapısının anlam-körlüğüne dair bir denetim iddiası ("EN §0.1'de bir NOT silinmiş") bu dilimi yazan taraf tarafından elle yeniden okunarak doğrulanamadı — TR/EN'de ilgili cümlede olumsuzluk ("DEĞİLDİR"/"is NOT") mevcut bulundu. Düzeltme yapılmadı; sonraki bağımsız denetim turunda yeniden bakılması istendi (D5 usulü).
- 2026-09-29 — **İkinci yeniden yazım:** ilk yeniden yazımda `CHANGELOG.md`'nin kök commit'ten (`5429b2d`, şablonun kendi [0.2.0] bölümü) miras kalan bir iç proje adı satırı atlanmıştı — `main` ve `dilim-1-2-repo-yayin` dalları hâlâ bu satırı taşıyordu. Düzeltme kök commit'in hemen üstündeki KUR commit'ine taşındı, 4 commit (KUR·Dilim1+2·Dilim3·kapilar.py v0.2.1+CI) yeniden yazıldı. `git grep -i -F -f _calisma/ic_adlar.txt` üç yerel dalda da (main, dilim-1-2-repo-yayin, dilim-3-sinir-spec-v2.5) **0 eşleşme**.
- 2026-09-29 — 🔴 **Ayrıca ölçüldü (yereldeki commit'lerden bağımsız): `onur-kesim/gedik` deposunun uzaktaki (origin) `main` dalı depo oluşturulduğundan beri (2026-09-28 20:58 UTC) public ve canlı, ve o dalın tek commit'i (`5429b2d`, şablon kontrolü) hâlâ aynı iç proje adını (bkz. `_calisma/ic_adlar.txt`) taşıyor.** Bu bir "yerel geçmiş" sorunu değil — gerçek zamanlı bir kamuya açıklık. Düzeltme yerelde hazır ama "push YOK" talimatı gereği origin'e gönderilmedi; kullanıcıya ayrıca bildirilecek (bkz. DEVİR).
- 2026-09-29 — **GERİ ÇEKİLDİ (B2): "dondurulmuş spec'in EK'i bu oturumda erişilebilir değildi" beyanım yanlıştı.** EK-1, SINIR_SPEC dosyasının sonundaydı; ilk aramamda yalnız dosya ADINA (`*EK-1*`) baktım, içeriğe bakmadım. 1. turdaki §0/description/yetki-kapisi düzeltmelerim bu yüzden kendi türetmemdi (madde 1'e dokunmamıştım, çelişki sürdü) ve "iki ısırık kuralı" gerekçesiyle sabit cümle kilidini kurmamıştım — spec kilidi açıkça istiyordu. EK-1 şimdi birebir uygulandı (DÜZELT-2).
- 2026-09-29 — **GERİ ÇEKİLDİ (B2): "EN §0.1'de NOT silinmiş iddiası doğrulanamadı" satırım yanlıştı.** Cowork'ün bulgusu dosyada NOT eksik olduğunu söylemiyordu; kapının anlamı ölçmediğini gösteren bir mutasyon ölçümüydü (NOT silinince ceviri_kapisi PASS). Bulgu geçerliydi; sabit cümle kilidi (`araclar/sabit_cumleler.json`, EK-1.4) ile kapatıldı: EN'den NOT silme → yapı kapısı PASS, kilit KIRMIZI.
- 2026-09-29 — **Cowork 2. denetim: DÜZELT, push YOK → DÜZELT-2 kapandı.** (1) `_calisma/ic_adlar.txt` Cowork'ün ilk listesiyle birleştirilecekken ben o dosyayı okumadan yazıp ezmiştim; ezilen liste geri getirilemedi, birleşik liste = benim 17 + Cowork'ün mesajda saydığı 14 eksik desen (31). Bu listeyle 3 dosya eşleşmesi (gh ikinci hesap adı, DURUM, DILIM) ve `d4d4ce1` commit MESAJI (git grep mesajlara bakmaz) redakte edildi; yeni bundle sonrası 5 commit yeniden oynatıldı; `git grep` üç yerel dalda 0, commit mesajları 0. Kök commit `5429b2d` (zaten canlı, uzakta) 2 eşleşme taşıyor, yeniden yazılamaz. (2) Sabit cümle kilidi EK-1.4. (3) §0 madde 1-2 EK-1.1, description'lar EK-1.2. (4) DILIM DÜZELT 1. tur kutuları (madde 1 ve 4) gerçeğe göre düzeltildi.
- 2026-09-29 — **Cowork 3. denetim: TESLİME UYGUN (koşullu).** İç ad (20 desen) 7 commit 0 · kapilar 7 PASS/0 FAIL · çeviri 12/12 · sabit cümle kilidi 3 anlam mutasyonunun 2'sini yakaladı (3.sü kilitli asıl cümleyle korunuyor) · §0 m.1 EK-1.1 uyumlu · rastgele beyan (kilit pozitif kontrolü) tuttu. Koşul: README'ye "kapı metin düzeyinde doğrulandı, davranışı canlı ajan koşusunda denenmedi" notu (EN+TR) — yapıldı. NE ÖLÇÜLEMEDİ: §0.1 davranışsal kör kapı (canlı ajan koşumu), CI (push sonrası), `/plugin install`. Push YOK sürüyor; canlı `main` sızıntısı kararı ve "push et" kullanıcıda. (DEVİR O2 başlığı bu satırla bayat: "bağımsız denetim koşmadı" artık geçersiz — bir sonraki DEVİR'de düzelir.)
