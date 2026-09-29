# TEST PAKETİ MUTASYONU — kapı var mı, ısırıyor mu

Bu dosya K4'ün (kendi kapını sına) **projeye uygulanmış** hâlidir. Yeni bir doktrin değildir.

**Var olma sebebi:** Test paketi bir kapıdır ve CI yeşilse "geçti" denir. Ama yeşil iki ayrı
şeyi aynı anda gösterebilir: ürün doğru olduğu için yeşil, ya da **test kör olduğu için**
yeşil. İkincisi açığın kendisinden tehlikelidir — ölçülmemiş bir alanı ölçülmüş gibi gösterir
ve yanlış güven üretir. gedik'in ekseni budur: *ölçülmeyen şey temiz sayılmaz.*

**Ne zaman koşar:** Kaynak koda ve koşabilir bir test paketine erişim varsa.
Test paketi **yoksa** mutasyon koşulmaz; bulgu doğrudan şudur: "test kapısı yok" — şiddeti
güvenlik yüzeyine göre verilir. Bu bir ÖLÇÜLMEDİ değil, ölçülmüş bir YOK'tur.

---

## 0. ÖN KOŞUL — temiz koşu

1. Test komutunu bul (`package.json` scripts, `pytest.ini`, `Makefile`, CI dosyası) ve koş.
   Geçen / kalan / atlanan sayısını **ve süreyi** kaydet.
2. Suite temiz koşuda YEŞİL değilse mutasyon anlamsızdır — zaten kırmızı bir suitede mutantın
   öldürülüp öldürülmediği ayırt edilemez. Bulgu: *"test paketi kırmızı ya da kararsız — kapı
   zaten kapalı değil"*.
3. Süre kaydı bütçedir: mutasyon ≈ N mutant × suite süresi. Kaç mutant koşabileceğini buradan
   hesapla ve **raporda yaz**.

---

## 1. ÖNCE BEDAVA TARAMA — zehirlenmiş test (mutant gerekmez)

Aşağıdakiler mutasyona gerek kalmadan ölüdür. Tam envanter çıkar ve **sayı ver**:

- **Totoloji:** `assert True`, `expect(true).toBe(true)`, `assert 1 == 1`, boş `assertDoesNotThrow`
- **Assert'siz test:** gövdesinde hiç assert/expect geçmeyen test — çağırır, sonuca bakmaz
- **Susturulmuş test:** `skip`, `xit`, `xfail`, `@Ignore`, `#[ignore]` — ve en tehlikelisi
  `.only`/`fit`/`fdescribe`: diğer testleri **sessizce** kapatır, suite yine yeşil görünür
- **Yutulmuş hata:** test gövdesinde `try/except: pass`, `catch {}`
- **Kör snapshot:** CI komutunda `-u` / `--update-snapshots` varsa snapshot testi hiçbir şey
  doğrulamıyor demektir; her koşuda beklenti yeniden yazılır
- **Mock'un yerine geçmesi:** test edilen fonksiyonun kendisi mock'lanmış — test mock'u test ediyor
- **Gevşek beklenti:** tek başına `toBeDefined()`, `assertIsNotNone`, `assertTrue(x is not None)`
- **Kapsam dışı bırakma:** coverage yapılandırmasındaki `exclude`/`ignore` listesi. Güvenlik
  ilgili bir dosya oradaysa bu kendi başına bulgudur

> **K3 uyarısı:** Bu tarama desen aramasıdır ve "yok" demeye yetmez. Envanter tam çıkarılır ve
> sayı verilir. "Temiz" denmez; *"şu desenlerde şu kadar bulundu"* denir.

---

## 2. MUTANT KATALOĞU — mutant ÜRÜN koduna enjekte edilir, teste değil

Testi bozmak hiçbir şey ölçmez. Mutant ürün kodunda yapılır, **tek başına**, ve yalnız
çalışma kopyasında (gedik salt-okunurdur — hedef projede dosya değiştirilmez).

| # | Mutant | Örnek | Ne ölçer |
|---|---|---|---|
| M1 | Koşul tersleme | `if (a)` → `if (!a)` | Dalın hiç test edilip edilmediği |
| M2 | Sınır kaydırma | `<=` → `<` · `>` → `>=` | Sınır değeri testi var mı (off-by-one) |
| M3 | Dönüş sabitleme | `return f(x)` → `return null` / `0` / `[]` | Dönüş değeri doğrulanıyor mu |
| M4 | Yan etki silme | kayıt / gönderme / yazma satırı silinir | Etki doğrulanıyor mu, yoksa yalnız "hata fırlatmadı" mı |
| M5 | Hata yutma | `throw` / `raise` → `pass` | Hata yolu test ediliyor mu |
| M6 | **Yetki kontrolü kaldırma** | `if (!user.canEdit) return 403` silinir | Yetki testi var mı — **zorunlu mutant** |
| M7 | **Doğrulama atlama** | girdi doğrulama / şema kontrolü kaldırılır | Kötü girdi testi var mı — **zorunlu mutant** |
| M8 | Mantık operatörü | `&&` → `||` | Bileşik koşulun her ayağı test ediliyor mu |
| M9 | Sıra/indeks kaydırma | `i` → `i+1` · sıralama ters çevrilir | Sıralama/sayfalama testi var mı |
| M10 | Eşik kaydırma | zaman aşımı, hız sınırı, tekrar sayısı ×10 | Eşikler test ediliyor mu |

**Seçim kuralı:** Mutant rastgele dosyaya değil, **güvenilmeyen girdinin dokunduğu yola**
enjekte edilir (SKILL.md §2, T5 envanteri). Rastgele seçim zaman israfıdır.

**M6 ve M7 zorunludur.** gedik'in ekseni yetki ve düşmanca girdidir; bu iki mutant kaçıyorsa
test paketi gedik açısından kördür ve bu sonuç raporun kararına girer.

---

## 3. KOŞUM

Her mutant için: enjekte et → suite koş → sonucu kaydet → geri al.

- **KIRMIZI** = mutant öldürüldü, test canlı ✓
- **YEŞİL** = mutant kaçtı → o davranış test edilmiyor → **ÖLÜ BÖLGE**
- **Derlenmiyor / hata** = mutant geçersiz; skor paydasından düşülür ve raporda belirtilir

**Yanlış-pozitif ayrımı:** Mutant kaçtıysa önce şunu sor — bu kod hiç çağrılıyor mu?
Çağrılmıyorsa bulgu "ölü test" değil **"ölü kod"**dur; ayrı sınıfa (BİLGİ) yazılır ve test
paketi suçlanmaz.

**Zaman sınırı:** Koşulamayan mutant **ÖLÇÜLMEDİ**'dir, öldürülmüş sayılmaz.
Raporda "10 mutant planlandı, 6'sı koşuldu" yazılır.

---

## 4. ARAÇ VARSA ARAÇ KULLAN

Elle mutasyon bir **örneklemdir**. Dilde yerleşik araç varsa onu koş ve raporda söyle:

Python `mutmut` / `cosmic-ray` · JS-TS `Stryker` · Java `PIT` · C# `Stryker.NET` ·
Ruby `mutant` · Go `go-mutesting` · Rust `cargo-mutants` · PHP `Infection`

Araç koşulduysa skorunu yaz. Koşulmadıysa **"elle örneklem, N mutant"** yaz.
Araç skoruyla elle örneklemi aynı sayıymış gibi raporlama.

---

## 5. ŞİDDET — kaçan mutantın davranışına göre

| Kaçan mutant | Şiddet |
|---|---|
| M6 yetki kontrolü · M7 girdi doğrulama | **YÜKSEK** — yetki/doğrulama regresyonu sessizce geçer |
| M4 yan etki · M5 hata yutma, güvenlik ilgili yolda | **ORTA** |
| M10 eşik (hız sınırı, zaman aşımı, tekrar) | **ORTA** — maliyet/DoS regresyonu görünmez |
| Görüntüleme, biçimleme, log | **BİLGİ** |

**Skor tek başına bulgu değildir.** Hangi davranışın ölü olduğu yazılmadan
"mutasyon skoru %X" raporlanmaz.

---

## 6. RAPOR SATIRI

```
G-n · TEST KAPISI KÖR — <dosya>:<fonksiyon>
  mutant   : M6 (yetki kontrolü kaldırıldı)
  komut    : <test komutu>
  sonuç    : 142 geçti / 0 kaldı  → mutant KAÇTI
  anlamı   : bu yetki kontrolünün kaldırılması hiçbir testi kırmıyor
  şiddet   : YÜKSEK
  yama     : <yazılması gereken test, tek cümle>
```

Bölüm özeti: `mutasyon: 10 planlandı · 8 koşuldu · 6 öldürüldü · 2 kaçtı · 2 ÖLÇÜLMEDİ`

---

## SINIRLAR

- Hedef projede dosya değiştirilmez; mutant yalnız çalışma kopyasında yaşar (SKILL.md §6).
- Mutasyon bir **kapsam** ölçüsü değildir. Yüksek satır kapsamı, mutant öldürülmediği sürece
  kanıt değildir — bu bölümün var olma sebebi tam olarak budur.
- **"Test paketi sağlam" cümlesi yazılmaz.** Yazılan: *"N mutantın M'si öldürüldü, kaçanlar şunlar."*
