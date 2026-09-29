# Kanıt, Self-Mutant ve Rapor

---

## 1. KANIT KURALI (K2)

Her bulgu üç parçayı **zorunlu** taşır:

1. **Tekrar üretim:** birebir girdi (kopyalanabilir), komut ya da adım dizisi.
2. **Gözlenen sonuç:** ne oldu — ekran, konsol çıktısı, değer, exit kodu.
3. **Kanıt türü:** aşağıdaki üç etiketten biri.

| Etiket | Anlamı |
|---|---|
| `KOŞULDU` | Yükü gerçekten uyguladım, sonucu ölçtüm |
| `STATİK` | Kodu okuyup çıkardım, çalıştırmadım — mantık zinciri raporda yazılı |
| `ÖLÇÜLMEDİ` | Erişemedim/koşamadım. **Neden** ve **nasıl ölçülür** yazılır |

`ÖLÇÜLMEDİ` bir başarısızlık değil, dürüstlüktür. **`ÖLÇÜLMEDİ` yerine "temiz" yazmak
bu skill'in tek affedilmez hatasıdır.**

### Zararsız işaretleyici
Kanıt yükü asla gerçek zarar vermez. Kullanılacak işaretleyici:
```
window.__ZAFIYET_KANITI = 1
```
Ölçüm: yükten sonra bu değişken tanımlı mı? Tanımlıysa enjeksiyon gerçekleşti.
Veri sızdıran, dosya silen, ağa çıkan yük YAZILMAZ.

---

## 2. SELF-MUTANT (K4) — kendi kapını sına

Bir alana "temiz" demeden önce, taramanın o alanda **gerçekten ısırdığını** kanıtla.
Reçete:

1. Hedefin **geçici kopyasını** al (asıl projeye dokunma).
2. Kopyaya bilinen bir açık enjekte et. Örnekler:
   - Bir sink'ten kaçışı kaldır: `el.innerHTML = esc(x)` → `el.innerHTML = x`
   - Filtreyi sök: bilinmeyen anahtarı atan `continue` satırını kaldır
   - Manifest'e `android:debuggable="true"` ekle
   - `package.json`'a `postinstall` script'i ekle
   - Sorguyu birleştirmeye çevir (Şerit B)
3. **Aynı taramayı** kirli kopyada koş. Yakalamalı.
4. **Temiz sürümde de koş.** Yakalamamalı (yanlış-pozitif yok).
5. İkisinin sonucunu rapora yaz.

| Mutant | Konum | Kirli kopyada | Temiz sürümde | Karar |
|---|---|---|---|---|
| M-1 | ... | YAKALANDI | temiz | tarama ISIRIYOR |
| M-2 | ... | KAÇTI | — | **tarama KÖR → o alan "temiz" sayılamaz** |

**En az iki mutant** zorunlu; biri girdi tarafında, biri yapılandırma/sink tarafında.
Bir mutant kaçarsa: ilgili başlık `ÖLÇÜLMEDİ` olur, "temiz" olmaz.

### 2.1 Mutanttan ÖNCE: köken izlemesi (bu adım atlanırsa mutant yanlış güven verir)

Bir mutant, mutasyona uğrattığın **tek satırın** kapsandığını gösterir. Envanterin **tam**
olduğunu göstermez. Bu yüzden sıra pazarlıksızdır:

1. **Envanter:** her sink'i listele.
2. **Köken izlemesi:** her sink'in bastığı değişkeni **geriye doğru** izle — nereden geliyor?
   Üretilmiş içerik mi (rng/generator/sabit şablon), yoksa `load()` / depo / import / ağ /
   dosya kaynaklı mı? İzlemeyi değişken adına bakarak değil, **atama zincirini okuyarak** yap.
3. **Mutant:** yalnız (2)'de "güvenilmeyen beslemeli" çıkanlar için, her biri ayrı ayrı.

Adım (2)'yi atlayıp "en bariz sink'i mutantladım, sınıf kapalı" demek bu skill'in bilinen
başarısızlık biçimidir — gerçek bir denetimde tam olarak böyle bir sink kaçtı (yedeklenen bir
sayaç, kaçışsız bir `innerHTML` şablonuna gidiyordu; ilk mutant başka bir satırdaydı).

---

## 3. YANLIŞ "TEMİZ" TUZAKLARI — okumadan rapor yazma

| Tuzak | Neden yanlış | Doğrusu |
|---|---|---|
| "`eval` aramadım, yok" | `new Function`, `setTimeout("...")`, `import()`, `Reflect` | Tam sink envanteri |
| "`esc()` var, XSS yok" | Kaçış bağlama göre değişir; öznitelik/URL bağlamı farklı | Sink bağlamını oku |
| "Seçici/desen metninde yok" | Metin araması davranış kanıtı değildir (bu projede bir kez YANLIŞ çıktı) | Çalışma zamanını ölç |
| "ORM var, SQLi yok" | Her ORM'de ham sorgu kapısı var | Her dinamik sorguyu aç |
| "İzin yok, ağ yok" | `data:`/`intent:`/harici uygulama hâlâ yüzey | Şema politikasını ölç |
| "Desen eşleşti, sır sızdı" | Yer tutucu olabilir | Her eşleşmeyi aç ve oku |
| "Kullanıcı kendine yapar, önemsiz" | Sosyal mühendislikle yaptırılır | Senaryoyu ayrıca yaz |
| "Bir aracı koştum, temiz dedi" | Tek araç tek açı görür | İkinci bağımsız yöntemle çapraz doğrula |
| **"Mutant ısırdı, o sınıf kapalı"** | **Mutant yalnız MUTASYONA UĞRATTIĞIN satırı kanıtlar; envanterin tam olduğunu kanıtlamaz.** Envanterde eksik bir sink hiç mutasyona uğramaz ve gaptan geçer | Önce **köken izlemesi** (§2.1), sonra her güvenilmeyen-beslemeli sink için ayrı mutant |

---

## 4. RAPOR ŞABLONU

Dosya adı: `ZAFIYET_RAPORU_<proje>_<surum>.md`

```markdown
# ZAFİYET RAPORU — <proje> <sürüm>
> Tarih: <YYYY-AA-GG> · Denetleyen: zafiyet-avcisi v1.0 · Kapsam: kullanıcının kendi
> kod tabanı/artefaktı · Salt-okunur (düzeltme yapılmadı)

## 0. TRİYAJ (ölçülen mimari)
| # | Soru | Cevap | Neyle ölçüldü |
|---|---|---|---|
| T1 | Ağ var mı | ... | ... |
| T2 | Sunucu kodu | ... | ... |
| T3 | Veritabanı | ... | ... |
| T4 | Hesap/kimlik | ... | ... |
| T5 | Güvenilmeyen girdi yolları | N adet (aşağıda) | ... |
| T6 | Sır/imza malzemesi | ... | ... |

**Şerit kararı:** ...
**Yapısal olarak uygulanamayan sınıflar:** ... (tek satır, N/A listesi yazma)

## 1. YÜZEY ENVANTERİ
### 1.1 Güvenilmeyen girdi yolları
| # | Yol | Konum | Kim kontrol ediyor | Sanitize |
### 1.2 Çıktı sink'leri
| # | Sink | Konum | Beslendiği veri | Güvenilmeyen mi | Kaçış |

## 2. BULGULAR
### Z-1 · [ŞİDDET] <tek cümlelik başlık>
- **Nerede:** dosya:satır
- **Tekrar üretim:** <birebir girdi/komut>
- **Gözlenen:** <ölçülen sonuç>
- **Etki:** <mimarinin izin verdiği tavana göre, şişirmesiz>
- **Yama:** <somut, uygulanabilir düzeltme>
- **Kanıt türü:** KOŞULDU / STATİK / ÖLÇÜLMEDİ

## 3. TEMİZ ÇIKANLAR (her biri neyle ölçüldü)
| Başlık | Sonuç | Ölçüm yöntemi |

## 4. ÖLÇÜLMEYENLER
| Başlık | Neden ölçülmedi | Nasıl ölçülür |

## 5. SELF-MUTANT SONUCU
| Mutant | Kirli kopya | Temiz sürüm | Karar |

## 6. KARAR
**GÜVENLİK AÇISINDAN YETERLİ** (kritik/yüksek bulgu yok, ölçülmeyen kritik başlık yok)
— veya —
**DÜZELT:** [Z-1, Z-3, ...] · **ÖNCE ÖLÇ:** [ölçülmeyen kritik başlıklar]

## 7. SONRAKİ TURA DEVREDİLENLER
- ...
```

---

## 5. KARAR EŞİĞİ

**GÜVENLİK AÇISINDAN YETERLİ** demek için üçü birden gerekir:

1. KRİTİK ve YÜKSEK bulgu **yok**.
2. Şeridin kapanış kontrol listesindeki her madde `KOŞULDU` ya da `STATİK` — kritik
   bir maddede `ÖLÇÜLMEDİ` varsa karar verilemez.
3. Self-mutant en az iki alanda **ısırdı**.

Üçünden biri eksikse karar `DÜZELT` ya da `ÖNCE ÖLÇ` olur. "Muhtemelen tamam"
diye bir karar yoktur.

---

## 6. DEVİR

Rapor bittiğinde:
- Bulgular düzeltilecekse görev metnine (Claude Code) madde madde geçer; bu skill
  **kod değiştirmez**.
- Karar tek satır olarak proje hafızasının karar günlüğüne yazılır.
- Genel-geçer yeni bir ders çıktıysa (yeni bir yanlış-"temiz" tuzağı gibi) bu
  referans dosyasının §3 tablosuna eklenir — dersler kalıcı olmalı.
