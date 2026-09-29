# ŞERİT A — İstemci / Offline / Mobil-WebView Yüzeyi

Sunucusu olmayan bir uygulamada "hacklenecek bir şey yok" YANLIŞTIR. Yüzey yer
değiştirir: ağdan **girdiye, sink'e, platform yapılandırmasına ve tedarik zincirine**
kayar. Aşağıdaki yedi başlık bu şeridin tamamıdır.

---

## A1 — Güvenilmeyen girdi yollarını dövme (fuzz)

T5 envanterindeki HER giriş için aşağıdaki yük ailelerini uygula. Her yükten sonra
üç şeyi ölç: **(1)** uygulama açılıyor mu (beyaz ekran yok), **(2)** kalıcı durum
bozuldu mu, **(3)** beklenmedik çalıştırma/gezinme oldu mu.

### A1.1 Prototip kirletme (prototype pollution)
```json
{"__proto__":{"zafiyetKaniti":1}}
{"constructor":{"prototype":{"zafiyetKaniti":1}}}
{"a":{"__proto__":{"zafiyetKaniti":1}}}
{"__proto__":{"toString":"kirli"}}
```
Ölçüm: yükledikten sonra `({}).zafiyetKaniti` tanımlı mı? Tanımlıysa KRİTİK/YÜKSEK.
Not: `JSON.parse` `__proto__`'yu **kendi başına** kirletmez; tehlike parse sonrası
`for...in` + atama / derin birleştirme (`merge`, `Object.assign` döngüsü) yapan koddadır.
Bu yüzden **parse'ı değil, parse sonrası yürüyüşü** oku.

### A1.2 Tip karışıklığı
Beklenen yerlere yanlış tip: nesne yerine dizi, sayı yerine dizge, `null`, `true`,
iç içe dizi. Ölçüm: `undefined is not a function` / beyaz ekran / sonsuz döngü.

### A1.3 Sayısal istismar
`NaN`, `Infinity`, `-Infinity`, `-1`, `0`, `1e308`, `9007199254740993`,
`0.1+0.2` artığı, string sayı `"12"`, `"1e3"`, `"0x10"`.
Ölçüm: clamp var mı? Negatif ilerleme, sonsuz sayaç, tarih taşması?

### A1.4 Sürüm/göç istismarı (`_v` alanı olan her şemada)
- `_v` düşür (eski sürüm) → göç yolu çalışıyor mu, mevcut veri EZİLİYOR mu?
- `_v` yükselt (gelecek sürüm) → uygulama "bilmediğim sürüm" deyip güvenli mi
  duruyor, yoksa yarı-yükleyip bozuyor mu?
- `_v` sil / `_v` string yap.

### A1.5 Boyut ve derinlik (kaynak tüketimi)
- ~5–10 MB tek dizge; 100k elemanlı dizi.
- 10.000 seviye iç içe `{"a":{"a":{...}}}` → özyinelemeli yürüyüşte yığın taşması.
- Aynı anahtarın binlerce tekrarı; çok uzun anahtar adları.
Ölçüm: donma, çökme, depolama kotası hatası. Kota dolduğunda `setItem` fırlatır —
yakalanıyor mu, yoksa uygulama kilitleniyor mu?

### A1.6 Dizge/Unicode
```
</script><img src=x onerror="window.__ZAFIYET_KANITI=1">
"><svg onload=window.__ZAFIYET_KANITI=1>
javascript:window.__ZAFIYET_KANITI=1
&#x3c;img src=x onerror=...&#x3e;          (çift kodlama)
‮ ... ​ ... (RTL override, sıfır genişlik)
lone surrogate: "\uD800"
NUL: "\x00" (yük listesinde literal NUL baytı yazma; kaçışlı metin kullan)
```
Ölçüm: bu dizge nereye yazılıyor? `textContent` ise güvenli; `innerHTML` ise A2'ye git.

### A1.7 Tarih/biçim doğrulaması
`2026-13-45`, `9999-99-99`, `2026-1-1` (dolgusuz), `١٤٤٧-٠١-٠١` (Arapça rakam),
`2026-07-26T00:00:00Z<script>`, negatif epoch, `Infinity`.
Ölçüm: regex tam çapa (`^...$`) kullanıyor mu? Yoksa öncesine/sonrasına yük eklenebilir.

### A1.8 Bozuk/kısmi girdi
Kesik JSON, sondaki virgül, BOM'lu, `NaN`/`undefined` içeren (geçersiz JSON),
tamamen boş, yalnızca boşluk, ikili çöp.
Ölçüm: **hata yakalanıyor mu, arayüz ayakta kalıyor mu?** Beyaz ekran = bulgu.

---

## A2 — Çıktı sink envanteri (enjeksiyon zinciri)

Sink'leri say ve **sınıflandır** — yalnız saymak işe yaramaz.

```
rg -n "innerHTML|outerHTML|insertAdjacentHTML|document\.write|\.srcdoc"
rg -n "eval\(|new Function|setTimeout\(\s*[\"'`]|setInterval\(\s*[\"'`]"
rg -n "\.src\s*=|\.href\s*=|setAttribute\(\s*[\"'](src|href|on\w+|style)"
rg -n "dangerouslySetInnerHTML|v-html|\{\{\{"
```

Her sink için tablo — **"Beslendiği veri" sütunu tahminle doldurulamaz; atama zincirini geriye
doğru okuyarak doldurulur** (bkz. `kanit-ve-rapor.md` §2.1 köken izlemesi):

| # | Sink | Dosya:satır | Beslendiği veri | Kökeni | Güvenilmeyen mi | Kaçış (escape) |
|---|---|---|---|---|---|---|
| S-1 | innerHTML | x.html:1234 | sabit şablon | — | Hayır | gereksiz |
| S-2 | innerHTML | x.html:5678 | `S.mastery[k]` | `load('mastery')` → yedek | **Evet** | `esc()` var/yok |
| S-3 | innerHTML | x.html:9012 | `STREAK.count` | `load('streak')` → yedek | **Evet** | **YOK ← bulgu** |

**Sık kaçan tip:** *sayı sanılan* alanlar. `'…'+sayac+'…'` şeklindeki bir şablon, `sayac`
depodan dizge olarak gelebiliyorsa kaçışsız bir sink'tir. "Zaten sayı" varsayımı, o alanın
yazıldığı **her yolda** sayısal zorlama olduğu kanıtlanmadan yapılamaz.

**Kaçış fonksiyonunun kendisini de denetle.** Tipik `esc()` yalnız `& < > "` çevirir.
Bu, **eleman gövdesi** ve **çift tırnaklı öznitelik** için yeterlidir; ama şu üç yerde
YETERSİZDİR: (a) tırnaksız öznitelik (`<div class=X>` — boşluk/`>` ile kaçılır),
(b) tek tırnaklı öznitelik (`'` çevrilmiyorsa kaçılır), (c) `<script>`/`<style>`
gövdesi ve `href="javascript:"` bağlamı. Sink'in **bağlamını** oku, sadece
fonksiyonun varlığına bakma.

Ayrıca: veri sink'e ulaşmadan önce bir **filtreden** (bilinen anahtar listesi, tip
kontrolü, clamp) geçiyorsa, o filtre asıl savunmadır — filtreyi mutantla sına (K4).

**A2'ye ek — DOM Clobbering ve CSS enjeksiyonu:**
- **DOM Clobbering (CWE-79 komşusu):** script çalıştırmadan, `<a id="x">`/`name=` ile JS
  değişkenini/`document.x`'i ezme. İmza: örtük global/`document.<ad>` erişimi + kullanıcı
  HTML'i. "Sadece metin" sanılan `innerHTML` burada ısırır.
- **CSS injection/exfil:** kullanıcı verisi `<style>`/`style=` içine giriyorsa
  öznitelik-seçici + `background:url()` ile token sızdırma, `@import`. İmza: kullanıcı-kontrollü
  stil.

---

## A3 — Kalıcı depolama bütünlüğü

- Anahtar öneki tutarlı mı; başka uygulamayla çakışma riski (aynı origin) var mı?
- **Elle bozma testi:** `localStorage` içine geçersiz JSON / yanlış tip yaz, uygulamayı
  aç. Kurtarıyor mu, yoksa kilitleniyor mu? (Kullanıcı bunu kendi yapamaz ama bozuk
  yazma/kota hatası aynı sonucu üretir.)
- Kota doldurma: 5 MB'ı doldur, sonra normal kaydetmeyi dene.
- Hassas veri saklanıyor mu? (Offline uygulamada localStorage şifresiz ve cihaza
  erişen herkese açıktır — PII/parola ASLA konmaz.)
- Yedek dışa aktarma: dosyada beklenmeyen alan (cihaz kimliği, yol, zaman damgası
  fazlası) sızıyor mu?

---

## A4 — Android / platform yapılandırması

**Manifest (APK'dan, kaynaktan değil — otorite artefakttır)**
```
aapt dump xmltree <apk> AndroidManifest.xml
aapt dump permissions <apk>
```
Kontrol listesi:

| Öğe | İstenen | Neden |
|---|---|---|
| `android:debuggable` | `false`/yok | true ise cihazdaki herkes süreci ayıklayabilir |
| `android:allowBackup` | `false` (veri hassassa) | adb backup ile veri dışarı çıkar |
| `android:usesCleartextTraffic` | `false`/yok | ağ yoksa da açık kalması gereksiz yüzey |
| `exported=` | yalnız LAUNCHER activity | exported bileşen = başka uygulamanın giriş kapısı |
| `intent-filter` (özel şema/host) | yalnız gerekliyse | deep link = güvenilmeyen girdi yolu (T5'e ekle) |
| `<provider>` / `grantUriPermissions` | yok | dosya sızıntısı |
| `launchMode` / `taskAffinity` | varsayılan | task hijacking (StrandHogg sınıfı) |
| `android:networkSecurityConfig` | — | varsa içeriğini oku |

**WebView ayarları (Capacitor/native kod)**
```
rg -n "setJavaScriptEnabled|addJavascriptInterface|@JavascriptInterface"
rg -n "setAllowFileAccess|AllowFileAccessFromFileURLs|AllowUniversalAccessFromFileURLs"
rg -n "setAllowContentAccess|setMixedContentMode|shouldOverrideUrlLoading|WebViewClient"
```
- `addJavascriptInterface` varsa: hangi metotlar açık? JS tarafı ele geçerse native
  yetki kazanır — **en yüksek riskli tek satır**.
- `AllowUniversalAccessFromFileURLs=true` → `file://` sayfası her origin'i okur: KRİTİK.

**Capacitor yapılandırması** (`capacitor.config.*`)
- `server.url` / `server.cleartext` → geliştirme kalıntısı üretime kaçmış olabilir.
- `server.allowNavigation` → beyaz listede joker (`*`) var mı?
- `android.allowMixedContent`, `androidScheme`.

**Android bileşen-arası yüzey (mevcut manifest kontrollerine ek)**
- **Intent redirection (CWE-926/940):** `exported` bileşen bir `Intent`'i güvenmeden iletiyor mu — `getParcelableExtra("intent")` → `startActivity`. Yetki devri.
- **Mutable PendingIntent:** `PendingIntent.get*` çağrılarında `FLAG_MUTABLE` (veya API 31 öncesi varsayılan) + boş base intent → başka uygulama doldurur, senin yetkinle çalışır.
- **Deep link → WebView `loadUrl`:** deep link parametresi doğrudan WebView'e yükleniyorsa universal XSS / JS-bridge erişimi. (T5 deep link'i girdi sayar; bu **zinciri** ayrı ölç.)
- **Exported ContentProvider:** `openFile` yol geçişi, provider sorgusu enjeksiyonu, `grantUriPermissions` istismarı.

**Mutant:** bir bileşeni `exported=true` yap / PendingIntent'i mutable yap (kopya manifest), tarama ısırıyor mu.

**Şema politikası (Fable K-J sınıfı — sistematik ölç)**
WebView içinde şu şemalarla gezinme denendiğinde ne oluyor: `data:`, `blob:`,
`javascript:`, `file:`, `content:`, `intent:`, `market:`, `tel:`, `mailto:`.
Beklenen: uygulama içinde kalması gerekenler kalır, dışarı çıkması gerekenler
onay diyaloğuyla çıkar, geri kalanı reddedilir. **Ölçmeden "güvenli" deme.**

---

## A5 — Harici gezinme ve niyet (intent) yüzeyi

- Uygulama dışına çıkan HER yol: `location.href`, `window.open`, `<a href>`,
  `Browser.open` (Capacitor), `startActivity`.
- Hedef URL sabit mi, yoksa veriden mi geliyor? Veriden geliyorsa **açık yönlendirme**
  (open redirect) sınıfı: yedek dosyasındaki bir alan hedefi belirleyebiliyor mu?
- Onay diyaloğu var mı; diyalog metni gerçek hedefi gösteriyor mu?
- Geri dönüşte durum korunuyor mu (dış uygulamadan dönünce veri kaybı = bütünlük).
- **Reverse tabnabbing:** `target="_blank"` + `rel="noopener"` **yok** → açılan sayfa
  `window.opener`'ı yönlendirir. İmza: `_blank` linkler/`window.open` + noopener eksik.

---

## A6 — Tedarik zinciri

```
npm ls --all --depth=2         # gerçek ağaç
npm audit --omit=dev           # bilinen CVE
rg -n "\"(preinstall|install|postinstall|prepare)\"" package.json */package.json
```
- Kilit dosyası (`package-lock.json`) var mı ve commit'li mi? Yoksa yapı tekrar
  üretilebilir değildir.
- `postinstall` script'i olan bağımlılık: her biri kurulumda kod çalıştırır — listele.
- Doğrudan bağımlılık sayısı ve her birinin gerçekten kullanılıp kullanılmadığı.
- CDN'den çekilen script varsa: SRI (`integrity=`) var mı? Yoksa CDN ele geçerse
  uygulama ele geçer. (Offline uygulamada CDN OLMAMALI.)

---

## A7 — Yapı artefaktı hijyeni

- APK/AAB içinde olmaması gerekenler: `.map` kaynak haritası, `.git`, `node_modules`,
  test dosyaları, yorum içinde anahtar, yedek `.bak`/`~` dosyaları.
- Paketlenen `index.html` SHA256'sı, kaynaktaki prototiple **birebir** mi? (Yanlış
  dosya paketlenmesi bir güvenlik olayıdır: denetlenmemiş kod cihaza gider.)
- İmza şeması (v1/v2/v3) ve imzanın gerçekten uygulanmış olması.
- Keystore/anahtar deposu repoda YOK; parolalar düz metin yapılandırmada YOK
  (T6 ile çakışır, orada ölç, burada tekrar etme).

---

## A8 — iOS / Capacitor-iOS YÜZEYİ (şu an tamamen kör olabilecek kolon)

**Tetik:** iOS artefaktı/kaynağı — `Info.plist`, `*.xcodeproj`/`*.xcworkspace`, Capacitor `ios/` klasörü, `.ipa`. Otorite artefakttır: `plutil -p Info.plist`, `otool`, `codesign -dv`.

| Öğe | İstenen | Neden |
|---|---|---|
| `NSAppTransportSecurity` → `NSAllowsArbitraryLoads` | `false`/yok | `true` = cleartext'in iOS karşılığı |
| Custom URL scheme (`CFBundleURLSchemes`) | yalnız gerekliyse | başka uygulama aynı şemayı kaydeder → **scheme hijacking**; gelen URL doğrulanmalı |
| Universal Links (`apple-app-site-association`) | doğrulanmış | doğrulanmamış link ele geçirme |
| Keychain erişilebilirlik sınıfı | `…WhenUnlocked…ThisDeviceOnly` | `…Always` cihaz kilidli değilken/yedekle sızar |
| Pasteboard | hassas veri konmaz | genel pano başka uygulamalara açık |
| `WKWebView` yapılandırması | `allowFileAccessFromFileURLs` vb. kapalı | Android WebView kontrollerinin iOS karşılığı |
| Kod imzası / entitlements | beklenenle eşleşir | fazla entitlement = fazla yetki |
| (Opsiyonel) jailbreak tespiti | hassas app'te | MASVS-RESILIENCE |

**Mutant:** `NSAllowsArbitraryLoads`'ı true yap / bir URL scheme doğrulamasını kaldır (kopyada), tarama ısırıyor mu.

---

## A9 — İSTEMCİ MESAJLAŞMA & KALICILIK

- **postMessage origin (CWE-345/346):** `addEventListener('message')` içinde
  **`event.origin` kontrolü yok**; gönderimde `targetOrigin:"*"`. İmza: message handler'da
  origin karşılaştırması aranır; yoksa bulgu.
- **Service Worker:** kötü SW kalıcılığı, `fetch` intercept ile istemci-içi enjeksiyon,
  kapsam (scope) genişliği. İmza: `serviceWorker.register`, `caches.put`, SW'de dış kaynak.

**Mutant:** postMessage origin kontrolünü kaldır / `_blank`'ten noopener'ı sök (kopyada),
tarama ısırıyor mu.

---

## Şerit A hızlı kapanış kontrolü

Aşağıdakilerin hepsine kanıtla cevap veremiyorsan tarama BİTMEMİŞTİR:

1. Güvenilmeyen girdi yollarının tam sayısı kaç ve her birine A1 yükleri uygulandı mı?
2. Sink sayısı kaç, **her biri için köken izlemesi yapıldı mı** (§A2), kaçı güvenilmeyen veriye
   dokunuyor, her birinde kaçış **bağlama uygun** mu?
2b. Her güvenilmeyen-beslemeli sink için **ayrı** mutant koştu mu? (Bir sink'in mutantı
   diğerlerini kapsamaz.)
2c. Aynı yüzeye giden **her yol** ayrı ölçüldü mü? (Ör. bir depo anahtarına hem "import"
   hem "doğrudan yazma" yolundan ulaşılıyorsa ikisi de denenir; biri bloke, diğeri açık olabilir.)
3. Manifest'te exported/debuggable/allowBackup ölçüldü mü (APK'dan)?
4. Şema politikası (data:/blob:/javascript:/file:) **ölçüldü** mü?
5. Git geçmişinin tamamı sır için tarandı mı?
6. Android bileşen-arası yüzey (intent redirection, mutable PendingIntent, deep-link→WebView) ölçüldü mü?
7. iOS artefaktı/kaynağı varsa A8 koştu mu — yoksa tek satırda "iOS yok" diye kapatıldı mı?
8. DOM clobbering ve CSS injection/exfil sink zincirine dahil edildi mi (A2 eki)?
9. Harici linklerde reverse tabnabbing (`_blank` + noopener eksikliği) ölçüldü mü (A5 eki)?
10. `postMessage` handler'larında `event.origin` kontrolü ve Service Worker kapsamı ölçüldü mü (A9)?
11. En az iki alanda self-mutant koştu ve ısırdı mı?
