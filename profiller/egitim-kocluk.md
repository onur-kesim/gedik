<!-- PROFİL: egitim-kocluk v1.0 -->
# PROFİL — EĞİTİM / KOÇLUK
## 1. NE
Bir öğrencinin (çocuk dahil) sınav/ders hazırlığını haftalık programla yürüten ve sonucu ölçen projeler.
## 2. ÜRÜN DESENİ
`haftalar/*` — her hafta bir dosya: program + ölçülen sonuç. Ders notu, kaynak listesi ürün değildir.
## 3. SAYAÇ
Net/puan eğilimi (deneme sonuçları), tamamlanan program oranı, çalışılan saat; kaynağı İŞLEYİŞ'te.
## 4. KOMUTLAR ŞABLONU
kur: yok · test: haftalık ölçüm kaydı var mı (dosya denetimi) · build: yok.
## 5. KUR EKLERİ
- [ ] öğrenci takma adı/kodu seçildi; okul, öğretmen, arkadaş adı hiçbir dosyaya yazılmaz (G2)
- [ ] uzak depo YOK; yerel git + `git bundle` yedeği proje klasöründe
- [ ] ölçüm aracı belirlendi (deneme, test, konu tarama) ve ilk taban ölçümü alındı
- [ ] araç haritası: pedagoji/matematik danışman skill'i, soru bankası, belge kapısı
## 6. KAPI EKLERİ
YAP: dilim = 1 hafta; hedef ölçülebilir ("3 deneme, hedef net ≥ X", "konu Y tamamlandı") · DOĞRULA: haftanın ölçümü kaydedildi; öğrencinin kendi geri bildirimi bir satır; program gerçekle karşılaştırıldı (yapılan/yapılmayan) · TESLİM: program öğrenciye ulaştı, veli gördü · SÜRÜM: sınav öncesi genel prova + son 4 haftanın eğilim özeti.
## 7. DIŞARI ÇIKTI
Haftalık program öğrencinin elinde, haftanın ölçümü dosyada, veli gördü.
## 8. EK KURALLAR
1. Ceza dili yok, ölçüm var: yapılmayan iş "başarısızlık" değil, sonraki haftanın planına giren veridir.
2. Yürüyen iskelet = ilk haftanın programı ilk oturumda çıkar; mükemmel plan aranmaz.
3. Kişisel veri iş bitince (sınav sonrası) silinir; tarih ve karar günlüğüne yazılır, kullanıcı onayıyla.
