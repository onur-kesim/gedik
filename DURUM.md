# DURUM — gedik

## DEVİR — henüz yazılmadı (bu bir oturum devri değil, aktif oturum içi durum)
Aşama: YAPIM (proje.toml asama) — KUR kapandı, Dilim 1+2 ve Dilim 3 (v2.5) yerelde
tamamlandı ve doğrulandı; git geçmişi (3 commit) temiz içerikle yeniden yazıldı.
Son yapılan: DILIM.md'deki bağımsız denetimin DÜZELT listesi (5 madde) kapatıldı; iç ad/
oturum no/yerel yol kapısı (`araclar/ic_ad_kapisi.py`) yazıldı ve 0 eşleşme verdi;
`kapilar.py`'nin bu makinede çöken tam koşusu ayrı bir oturumda düzeltildi, şimdi 7 PASS.
Yarım kalan: DÜZELT'ten sonraki bağımsız denetim turu henüz koşmadı.
Sıradaki ilk iş: bağımsız denetimi tazeden koştur (ayrı bağlam, salt-okunur) → TESLİME UYGUN
çıkarsa kullanıcıdan "push et" onayı iste.
Açık karar / bloker: bağımsız denetim + push onayı kullanıcıda.
Araç eksiği: —
Dosyalar: CLAUDE.md, proje.toml, DILIM.md, araclar/ceviri_kapisi.py, araclar/ic_ad_kapisi.py
Uyarı: gerçek bir DEVİR (oturum sayacı artışı) burada YAPILMADI; bu blok yalnız
DURUM'un B4 gereği güncel tutulması içindir.

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
