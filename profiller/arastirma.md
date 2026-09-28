<!-- PROFİL: arastirma v1.0 -->
# PROFİL — ARAŞTIRMA
## 1. NE
Bir soruya kaynaklı, tarihli, güven etiketli cevap üreten her proje: pazar, teknoloji, hukuk, strateji araştırması.
## 2. ÜRÜN DESENİ
`rapor/*` — teslim edilen rapor dosyaları. Notlar, kaynak listeleri, taslaklar ürün değildir.
## 3. SAYAÇ
Karara dönüşen bulgu sayısı; raporu alan okuyucu sayısı (İŞLEYİŞ'te kim, nasıl sayılıyor).
## 4. KOMUTLAR ŞABLONU
kur: yok · test: doğrulayıcı (varsa) · build: belge kapısı.
## 5. KUR EKLERİ
- [ ] **kapsam listesi** yazıldı: sorular · kaynak türleri · zaman penceresi · kaynak yaşı sınırı (varsayılan 12 ay, hızlı alanda 3 ay)
- [ ] kapsam bir alt-ajanla düşmanca genişletildi ("eksik açı var mı?") — tek tur, sonra dondu
- [ ] araç haritası: arama/getirme araçları, doğrulayıcı, belge kapısı
## 6. KAPI EKLERİ
YAP: her iddiada kaynak + tarih + GÜVEN (KESİN / ZAYIF / ÖLÇÜLEMEDİ); canlılık iddiasında birebir alıntı; alıntı kaynağın KENDİ metnidir, araç özeti gözlemdir · DOĞRULA: bağımsız doğrulayıcı; türetilmiş sayı ↔ liste tutarlılığı ("29 paket / 32 satır" sınıfı); tazelik turu — en kritik 3 iddia teslimden 24 saat içinde yeniden aranır; belge kapısı · TESLİM: kapsam listesinin her kalemi ölçüldü ya da NE ÖLÇÜLEMEDİ'de · SÜRÜM: rapor sunumu/yayını öncesi ikinci bağımsız ölçüm yolu (kritik iddialar).
## 7. DIŞARI ÇIKTI
Rapor teslim edildi (dosya + gönderim kaydı) ve okuyucu aldı; raporun ilk bölümü kapsam dışı + NE ÖLÇÜLEMEDİ.
## 8. EK KURALLAR
1. Kapsamda olmayan konu sonradan "akıl etmedim" değil, kapsam listesinin ölçülmüş eksiğidir; listeye eklenir, yeni dilim açılır.
2. 24 saatten eski canlılık ölçümü yenilenir; HTTP 200 ve üçüncü taraf listeler kanıt değildir.
3. Bulgu bloğu başlığına yazılan atıf altındaki maddelere miras kalmaz; her madde kendi kaynağını taşır.
