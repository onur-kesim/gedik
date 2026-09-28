# DILIM — `<ad>`     açıldı: `<tarih>` · aşama: `<KEŞİF | YAP | DOĞRULA | TESLİM>` · sürüm dilimi: HAYIR
Hedef: `<uçtan uca çalışan tek parça — ilk dilim yürüyen iskelettir, ≤7 gün>`
Kabul: `<koşan test ya da ölçülebilir sonuç; düzyazı değil>`

## ESAS KARARI (yalnız AŞAMA: KEŞİF — süre tavanı yok; hepsi dolunca insan "başla" der → YAPIM, bu bölüm silinir)
- [ ] NE: tek paragraf — kim için, hangi sorun, neden şimdi (`belgeler/kesif/`)
- [ ] danışılanlar ve görüşler kaydedildi — kim, tarih, ne dedi (kişisel veri: G2)
- [ ] ARAÇ HARİTASI dolu: KEŞİF ve YAP satırları, BEKLE / ARAÇSIZ YAP sınıflarıyla
- [ ] ilk dilim adayı yazıldı: ince yol + mekanik kabul + "dışarı çıktı" tanımı (kim alacak)
- [ ] insan "başla" dedi → proje.toml asama = "yapim", tarih karar günlüğüne
### KEŞİF ADIMLARI (sırayla; tarih baskısı yok, biten işaretlenir)
- [ ] 

## YAP
- [ ] başka açık dilim yok (WIP = 1)
- [ ] kabul ölçütü yazıldı ve ölçülebilir
- [ ] bu aşamanın araçları kurulu (ARAÇ HARİTASI'ndan ölçüldü)
<!-- profilin YAP ekleri buraya -->

## DOĞRULA
- [ ] otomatik kapılar yeşil (CI: kapilar + kor-kapi; git'siz projede `python -B araclar/kapilar.py`)
- [ ] bağımsız denetim koştu — ayrı bağlam, salt-okunur (rapor: DENETİM)
- [ ] NE ÖLÇÜLEMEDİ yazıldı (boş olamaz)
<!-- profilin DOĞRULA ekleri buraya -->

## TESLİM
- [ ] README (NE TESLİM EDİLMEDİ + BİTTİ) ve DURUM (dört sayı) güncel
- [ ] git etiketi + CHANGELOG satırı
- [ ] bir insana gösterildi / alıcı aldı: `<kim, ne zaman>`
<!-- profilin TESLİM ekleri buraya -->

## SÜRÜM (yalnız sürüm dilimi — profilden)
- [ ] 

## DENETİM — denetleyen: `<Cowork / alt-ajan / kişi>` · bağlam: ayrı ✓ · salt-okunur ✓
| Kapı | Sonuç | Kanıt |
|---|---|---|
| | PASS / FAIL / ÖLÇÜLEMEDİ | |

Rastgele doğrulanan beyan: `<beyan → ölçüm>`
NE ÖLÇÜLEMEDİ: `<boş olamaz>`
Hüküm: TESLİME UYGUN / DÜZELT

## Sonuç
`<bitince tek satır → README BİTTİ'ye iner, bu dosya iskelete sıfırlanır>`
