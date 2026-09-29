# ŞERİT E — SEVK EDİLEN ARTEFAKT HİJYENİ

**Ne zaman koşar:** T9 EVET ise (sevk edilen bir artefakt var).

**Ekseni:** Kaynakta ne yazdığı değil, **sevk edilen dosyada ne olduğu.** Kullanıcının
eline geçen şey artefakttır; kaynak değildir. Bu yüzden *"kaynakta düzelttim"* bir bulguyu
kapatmaz — ölçüm sevk edilen artefaktta yapılır ve orada tekrarlanır.

> **Devir sınırı.** Android/Play'e özgü paket sökümü, imza zinciri, dex-diff ve mağaza
> politikası uyumu ilgili **build QA** aracının işidir. Bu şeritteki
> maddeler **platformdan bağımsızdır**. Aynı bulguyu iki yerde raporlama; hangisinin koştuğunu
> raporun 0. bölümünde tek satırla yaz.

---

## E0 — ARTEFAKTI TESPİT ET VE AÇ

Artefakt türleri: web bundle (`dist/`, `build/`, `.next/`, `out/`) · APK / AAB ·
exe / dmg / AppImage / MSI · container imajı · npm tarball · `.whl` / `.jar` / `.nupkg` ·
tarayıcı eklentisi `.zip` / `.crx` · sunucusuz fonksiyon paketi.

Zip tabanlıysa aç ve **dosya envanteri çıkar**: ad, boyut, adet. Envanter olmadan tarama olmaz —
neyin taranmadığını bilmeyen tarama "temiz" diyemez.

Kaynak ağacındaki dosyaya bakmak bu şeridin işi **değildir**; o ŞERİT A/B ve kod incelemesinin
işidir. Buradaki her bulgu artefaktın içinden çıkar.

---

## E1 — SIR SIZMASI (artefaktta)

**Ara:** API anahtarı desenleri (`AKIA`, `sk-`, `ghp_`, `AIza`, `xox[baprs]-`,
`-----BEGIN * PRIVATE KEY-----`) · JWT (`eyJ`) · bağlantı dizesi (`://kullanıcı:parola@`) ·
`.env` içeriği · keystore / p12 / pem · pakete sızmış `.git` klasörü ya da kaynak arşivi.
Ayrıca **yüksek entropi taraması**: base64/hex, uzunluk ≥ 20, sözlük dışı.

> **K3 gereği:** "Sır yok" demek için desen aramak yetmez. Ya gömülü dizge envanterini tam
> çıkar ve sayısını ver, ya `ÖLÇÜLMEDİ` yaz.

**Kör kapı (K4):** Artefaktın **kopyasına** sahte bir anahtar göm (`AKIA` + rastgele dizi) ve
taramayı koş. Isırmıyorsa tarama kördür — alan temiz değil, **ölçüm yok** demektir.

**Yanlış alarm ayrımı — önemli.** İstemciye giden her anahtar bulgu değildir: Firebase web
`apiKey`, Supabase `anon` anahtarı ve benzerleri tasarımı gereği herkese açıktır ve tek başına
yetki taşımaz. Bulgu, **yetkisi olan** anahtardır: `service_role`, secret key, private key,
admin/CI token'ı, imzalama anahtarı. Anahtarın kapsamını ölç ve raporda yaz; ölçemiyorsan
"kapsam ÖLÇÜLMEDİ" de, "kritik" deme.

Bir sır bulunduğunda **dosyadan silmek bulguyu kapatmaz.** Döndürme (rotation) sırası
`cicd-depo-ve-kurtarma.md` içindedir ve bulgu ancak döndürme yapılınca kapanır.

---

## E2 — DEBUG / GELİŞTİRME BAYRAĞI

`debuggable=true` · `NODE_ENV` production değil · `__DEV__` · `DEBUG=1` · geliştirici menüsü ·
hot-reload sunucusu adresi · test hesabı ya da arka kapı · kullanıcıya çıkan yığın izi (stack
trace) · açık React/Vue DevTools kancası · üretime kalmış `assert` · token ya da kişisel veri
yazan log satırı.

Kanıt: bayrağın artefaktta geçtiği yer **artı** davranışın gözlemi. Yalnız dizgeyi bulmak
yeterli değildir; mümkünse artefaktı çalıştır ve davranışı gör. Çalıştıramıyorsan bunu yaz.

---

## E3 — SOURCE MAP VE KAYNAK YENİDEN İNŞASI

Kontrol: `*.map` dosyaları pakette mi · üretim bundle'ında `//# sourceMappingURL=` var mı ve
hedefi erişilebilir mi · `.ts`/`.jsx` kaynağı pakete girmiş mi · `sourcesContent` gömülü mü.

**Etki:** Kaynak yeniden inşa edilir; iç mantık, yorumlar, kalan sırlar ve saldırı yüzeyi
ifşa olur.

**Ölçüm:** Map varsa **fiilen bir dosyayı geri çöz** ve kaç kaynak dosyanın kurtarıldığını yaz.
Bulgu "map var" değildir; bulgu *"map ile 214 kaynak dosya kurtarıldı"*dır.

---

## E4 — TEST / STAGING KALINTISI

Sabit kodlu `localhost`, `127.0.0.1`, `10.0.2.2`, `*.ngrok*`, `staging.`, `test.`, `dev.`
hostları · iç ağ IP'leri · düz metin `http://` uçlar · sertifika sabitlemesinin devre dışı
olması · Android `network_security_config` içinde `cleartextTrafficPermitted="true"` ya da
`debug-overrides` · iOS `NSAllowsArbitraryLoads`.

**Etki iki yönlüdür:** (a) üretim istemcisi test ortamına konuşabilir, (b) test ortamının
adresi saldırgana verilmiş olur — test ortamları genellikle daha az korunur.

---

## E5 — GENİŞ YETKİ / GEVŞEK YAPILANDIRMA

Platformdan bağımsız soru: **artefakt, işini yapmak için gerekenden fazla ne isteyebiliyor?**

- **Mobil:** beyan edilen izinler ↔ fiilen kullanılan API'ler · izin taşımayan `exported=true`
  bileşen · geniş intent-filter · `android:allowBackup=true` (yedekten veri çekme)
- **Masaüstü / Electron:** `nodeIntegration:true` · `contextIsolation:false` ·
  `webSecurity:false` · uzak içerik yükleyen pencere
- **Tarayıcı eklentisi:** `<all_urls>` · `tabs` · `cookies` · `webRequest` — gerekli mi
- **Container:** `USER root` · `--privileged` · gereksiz capability · sırların `ENV` ile
  gömülmesi (imaj katmanında kalır, `docker history` ile okunur)
- **Paket (npm/pip):** `files` / `MANIFEST.in` kapsamı — testler, `.env`, iç betikler pakete
  girmiş mi · `postinstall` betiği var mı ve ne yapıyor

Kural (SKILL.md §4): *"arayüzde göstermiyoruz"* bir savunma değildir. Yetki artefaktta ölçülür.

---

## E6 — ARTEFAKT ↔ KAYNAK EŞLEŞMESİ

Üç soru: Sevk edilen artefakt **hangi commit'ten** üretildi? **Hash'i** kaydedildi mi? Aynı
kaynaktan yeniden üretilince aynı mı çıkıyor (ya da en azından aynı sürüm dizesi ve manifest)?

**Ölçüm:** artefaktın SHA-256'sı + üretildiği commit + üretim komutu. Üçünden biri yoksa sonuç
**ÖLÇÜLMEDİ**'dir ve bu kendi başına bir bulgudur: teslim edilen şeyin ne olduğu kanıtlanamıyor.

Önceki sürüm elinizdeyse iki artefakt arasında **dosya envanteri farkı** çıkar. Sürüm notunda
geçmeyen yeni bir dosya, kütüphane ya da izin, açıklanmamış bir değişikliktir.

---

## E7 — GÖMÜLÜ BAĞIMLILIK AYAK İZİ

Beyan edilen bağımlılıklar ↔ artefakta **fiilen giren** kütüphaneler. Sızmış analitik / reklam /
telemetri SDK'sı, beklenmeyen ağ istemcisi, geçişli bağımlılıkla gelen izin.

Bu, gizlilik beyanının doğruluğunu da etkiler — **ama beyan formu uyumu build QA'nın işidir.**
Burada yalnız "artefaktta ne var" ölçülür, sonuç oraya devredilir.

---

## KÖR KAPI (K4) — bu şeritte zorunlu

En az iki mutant, artefaktın **kopyasına**:

1. Sahte anahtar göm (E1) → tarama ısırmalı
2. `debuggable` / `__DEV__` bayrağını aç (E2) → tarama ısırmalı

Isırmıyorsa alan temiz değil, **ölçüm yok**. Temiz kopyada da koş — yanlış-pozitif üretmemeli.

---

## RAPOR SATIRI

```
G-n · <E maddesi> — <artefakt>/<yol>
  kanıt          : <birebir bulunan dizge ya da komut çıktısı — sır MASKELİ>
  tekrar üretim  : <komut>
  etki           : <mimarinin izin verdiği tavana göre>
  şiddet         : ...
  yama           : ...
```

**Sır maskeleme:** Bulunan anahtarın ilk 4 ve son 2 karakteri dışı maskelenir; tam değer
rapora yazılmaz.

---

## SINIRLAR

- Artefakt açılamıyorsa (şifreli, imzalı kapalı biçim, ticari paketleyici) **ÖLÇÜLMEDİ**
  yazılır; "temiz" denmez.
- Ticari paketleyici ya da obfuscator kırılmaz.
- Bulunan sır **kullanılmaz**: geçerli olup olmadığı canlı servise istek atılarak sınanmaz
  (SKILL.md §0 kapsam kilidi).
