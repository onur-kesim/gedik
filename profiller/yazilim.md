<!-- PROFİL: yazilim v1.0 -->
# PROFİL — YAZILIM / WEB / MOBİL
## 1. NE
Uygulama, web sitesi, araç, kütüphane — kod yazılan her proje.
## 2. ÜRÜN DESENİ
Kod: `src/*`, `app/*`, `lib/*` (proje.toml). Build çıktısı, kanıt, belge ürün değildir.
## 3. SAYAÇ
Kullanıcı/indirme/ziyaret (mağaza konsolu, analitik, sunucu logu); kaynağı İŞLEYİŞ'te.
## 4. KOMUTLAR ŞABLONU
kur (`npm ci` / `pip install -r requirements.txt` / `flutter pub get`) · çalıştır · test · lint · build — README ve CI'da aynı komut.
## 5. KUR EKLERİ
- [ ] LICENSE · `.gitignore` · `.env.example` · kilit dosyası commit'te
- [ ] biçimlendirici + lint yapılandırması depoda
- [ ] CI ilk push'ta yeşil, `kor-kapi` geçti
- [ ] dal koruması açık (araclar/dal-korumasi.json)
- [ ] kod sağlığı tabanı donduruldu (`taban_dosya_ihlal`)
## 6. KAPI EKLERİ
YAP: bir dilim = bir PR, ≤ ~400 satır; gövde-temelli, bitmemiş özellik bayrak arkasında · DOĞRULA: CI yeşil; kod sağlığı (dosya ≤400 satır, karmaşıklık ≤15, taban aşılmaz); güvenlik taraması; belge/kod ≤1,0 · TESLİM: `vX.Y.Z` etiketi + CHANGELOG · SÜRÜM: sürüm artefaktı hijyeni (sır, debug bayrağı, source map, test uç noktası, geniş izin YOK); sürüm QA (mobil: izin diff'i, paket boyutu; web: erişilebilirlik + performans bütçesi); yayın metni; **geri alma planı**.
## 7. DIŞARI ÇIKTI
Etiket + CHANGELOG satırı; sürüm diliminde mağaza/yayın; bir insan = kurup deneyen kişi.
## 8. EK KURALLAR
1. Yeni bağımlılık = lisans + bilinen açık + kilit dosyası; kaynağı belirsiz paket alınmaz.
2. Dört DORA sayısı DURUM'a: teslim sıklığı · dilim süresi · kırmızı oranı · kırmızıdan yeşile süre.
3. Yabancı depoya katkı: fork → dal → PR; ölçüt: açılmış PR + bir yabancı yorum; gönderim insanın elinden.
4. Test paketi mutasyonu: ürün kodunda bilerek bozulan bir satır paketi kırmızıya döndürmüyorsa test ölüdür.
