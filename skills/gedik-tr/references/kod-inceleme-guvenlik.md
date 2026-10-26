# Güvenlik Odaklı Kod İncelemesi

> **Bu dosya bir "genel kod incelemesi" değildir.** Okunabilirlik, mimari zarafet,
> performans ayarı, isimlendirme, test kapsamı → bunlar `engineering:code-review`'un
> işidir; burada YAPILMAZ. Burada yalnız **güvenlik etkisi olan doğruluk hataları**
> aranır: yanlış çalıştığında saldırgana kapı açan, veri sızdıran, yetki kaçıran ya da
> sistemi durdurulabilir hâle getiren hatalar.
>
> **Ayrım testi:** "Bu hatayı bir saldırgan bilerek tetikleyebilir mi, tetiklerse ne
> kazanır?" Cevap "hiçbir şey, sadece çirkin/yavaş olur" ise → devret, buraya yazma.

---

## 0. Nasıl okunur — sink'ten geriye

Dosya dosya baştan sona okumak zaman kaybıdır ve kaçırır. **Sink'ten başla, girdiye
doğru geriye yürü** (taint tracing):

1. Tehlikeli sink'leri listele (sorgu, `exec`, dosya yolu, HTML çıktısı, `fetch(url)`,
   deserileştirme, yönlendirme, log).
2. Her sink için: bu değer nereden geldi? Çağrı zincirini **girdi noktasına kadar** sür.
3. Zincirde bir yerde doğrulama/kaçış var mı? Varsa **o doğrulama gerçekten koşuyor mu**
   (koşullu mu, `if (config.strict)` arkasında mı, testte devre dışı mı)?
4. Girdi noktasına ulaşamıyorsan → `ÖLÇÜLMEDİ`, tahmin yazma.

**Sayı ver:** "N sink bulundu, M tanesi güvenilmeyen veriye dokunuyor, K tanesinde
doğrulama koşulsuz." Envanter yoksa inceleme yoktur.

---

## 1. Güvenlik etkili doğruluk hataları

### 1.1 Kontrol akışı
- **Erken dönüş eksikliği:** yetki kontrolü `if (!yetkili) { logla(); }` — `return` yok,
  akış devam ediyor. Klasik ve ölümcül.
- **Negatif/varsayılan izin:** `if (rol === "banned") reddet;` — bilinmeyen rol kabul
  ediliyor. Doğrusu **beyaz liste**: bilinen izinli rol dışında her şey RED.
- **Yakalanıp yutulan hata:** `try { dogrula() } catch {}` — doğrulama patlıyor, akış
  "başarılı" sanılıyor. `catch` bloğu sessizse KRİTİK adaydır.
- **Async/await unutulmuş:** `if (kullaniciYetkili(x))` — fonksiyon Promise dönüyor,
  Promise her zaman truthy → **kontrol hiç çalışmıyor**. JS/TS'de tek tek ara.
- **Kısa devre yanlışlığı:** `a || b` ile `a ?? b` karışması; `0`, `""`, `false`
  değerlerinin varsayılana düşmesi (ör. `limit = req.query.limit || 1000`).

### 1.2 Tip ve dönüşüm
- **Gevşek karşılaştırma:** `==` ile tip zorlaması (`"0" == false`), `parseInt` radix'siz.
- **Sayı taşması / kayan nokta:** para ve kota hesabında `float`; negatif miktar kabulü
  (`adet: -5` → bakiye artıyor).
- **JSON tip karışması:** beklenen `string`, gelen `{"$ne":null}` veya dizi. **Şema
  doğrulaması var mı, yoksa `typeof` bile yok mu?**

### 1.3 Eşzamanlılık ve durum
- **TOCTOU:** kontrol ile kullanım arasında durum değişebiliyor mu (bakiye kontrolü →
  düşme; dosya var mı → aç)?
- **Atomik olmayan sayaç:** kota/deneme sayacı oku-artır-yaz ile güncelleniyorsa yarış
  durumu; hız sınırı böyle atlatılır.
- **Paylaşılan değişebilir durum:** modül seviyesinde tutulan istek-bazlı veri
  (kullanıcı bağlamı) → istekler arası sızıntı.
- **İdempotans:** ödeme/oluşturma ucu iki kez çağrılırsa ne olur?

### 1.4 Sınır ve kaynak
- Sayfalama/limit üst sınırı yok → tek istekle tüm tabloyu çekme.
- Kullanıcı verisiyle beslenen döngü/özyineleme derinliği sınırsız.
- Dosya/tampon boyutu doğrulanmadan belleğe alınıyor.

### 1.5 Kripto ve rastgelelik hijyeni
- Token/parola sıfırlama/oturum kimliği için `Math.random()`, `rand()`, zaman damgası
  → **tahmin edilebilir**. `crypto.randomBytes` / `secrets` gerekir.
- Sabit IV, ECB modu, kendi yazılmış şifreleme, gizli anahtar olarak sabit dizge.
- **Sabit zamanlı karşılaştırma:** token/HMAC karşılaştırması `===` ile mi
  (zamanlama sızıntısı), `timingSafeEqual` mı?
- Hash: parola için hızlı hash (MD5/SHA) → KRİTİK.

### 1.6 Numaralandırma ve sızıntı
- Farklı hata mesajı: "kullanıcı yok" ↔ "parola yanlış" → kullanıcı numaralandırması.
- Farklı yanıt süresi: var olan kullanıcıda bcrypt koşuyor, olmayanda koşmuyor.
- Sıralı/tahmin edilebilir kimlik (auto-increment) + zayıf yetki = toplu veri çekme.

---

## 2. Bağımlılık ve tedarik zinciri

- **CVE taraması:** `npm audit` / `pip-audit` / `osv-scanner` — çıktıyı rapora **sayıyla**
  yaz (kritik/yüksek adedi). Yoksa `ÖLÇÜLMEDİ`.
- **Kilit dosyası:** `package-lock.json` / `poetry.lock` repoda mı; kurulum `ci`/`--frozen`
  ile mi (aksi hâlde sürüm sürüklenir)?
- **`postinstall` betikleri:** bağımlılıkların kurulumda kod çalıştırması.
- **Typosquat / sahiplik:** yeni eklenen paket adı popüler bir paketin yazım varyantı mı;
  bakım terk edilmiş mi (son yayın tarihi)?
- **Lisans:** kullanıcının kırmızı çizgisi — yeni bağımlılık = lisans + CVE kontrolü.

### 2.1 PHP projesi: çalışma zamanı sürümü ve paket denetimi (v2.8.0)

T2'de PHP imzası bulunduysa bu bölüm koşar. **Sabit CVE tablosu tutulmaz** (bayatlar): açık
eşleşmesi tarayıcı veri tabanından gelir; burada yalnız EOL dalı kuralı sabittir.

**Çalışma zamanı sürümü — kaynak sırası.** Bulunan her sürüm KAYNAĞIYLA rapora yazılır
(`8.3.30 — Dockerfile:1`); yorum satırı (`#`) kaynak sayılmaz:
1. Dockerfile / docker-compose imaj etiketi (`FROM php:8.3.30-fpm`, `image: php:…`; `ARG` ile
   verilmişse varsayılan değeri)
2. `.php-version`
3. `composer.json` → `config.platform.php` (bağımlılık çözümleme hedefidir, çalışan sürüm
   olmayabilir; öyle yazılır)
4. CI: `setup-php` / matris (`php-version:`) — matris test edilen sürümlerdir, canlıda çalışan
   olmayabilir; öyle yazılır
5. Buildpack/platform dosyası (`.platform.app.yaml` `type: php:…`, `app.yaml` `runtime: php…`,
   PHP işleyicili `.htaccess`)

- Çok aşamalı Dockerfile'da SON `FROM php:` aşaması çalışma zamanıdır; önceki aşamalar ayrıca yazılır.
- Kaynaklar çelişirse (ör. compose `php:7.4`, Dockerfile `php:8.3.30`) her sürüm kaynağıyla
  yazılır, çelişki belirtilir; EOL kuralı çalışma zamanı kaynaklarının en eskisine uygulanır.
- `composer.json` içindeki `"require": {"php": ">=8.1"}` bir **alt sınırdır, çalışan sürüm SAYILMAZ**.
- Etiket yama düzeyini vermiyorsa (`php:8.3-fpm`, `php:8-apache`, `latest`) rapora etiket +
  kaynak yazılır (dal belliyse dal), eksik düzey ÖLÇÜLMEDİ; bu durumda kaynak VAR olduğundan
  aşağıdaki sabit "depoda yok" satırı yazılmaz.
- Yalnız `composer.json` (ya da yalnız `*.php`) varsa ve sunucu giriş noktası, çatı ya da imaj yoksa
  proje kütüphane olabilir: satıra "kütüphane — çalışma zamanı tüketene ait" yazılır; sabit "depoda yok"
  satırı ve `ÖNCE ÖLÇ` gerekmez (varsa `config.platform.php` yine kaynağıyla yazılır).
- Sürüm depoda hiç yoksa (paylaşımlı hosting, dosya yedeği) rapora **şu sabit satır** yazılır
  ve "temiz" DENMEZ: "PHP çalışma zamanı sürümü depoda yok — ÖLÇÜLEMEDİ; sunucu/hosting panelinden kontrol et."
  Bu sonuç raporun ÖLÇÜLMEYENLER bölümüne ve JSON'da `kapsam` (`olculmedi`, `sebep`) satırına da
  yazılır; karar `ÖNCE ÖLÇ` olur. `ÖLÇÜLEMEDİ` ile `ÖLÇÜLMEDİ` aynı durumdur.

**EOL kuralı** (ölçüm 2026-10-22, php.net `supported-versions` ve `eol.php`; **yeniden doğrula**):
PHP ≤ 8.1 resmî güvenlik yaması almıyor → bulgu (dağıtımın/LTS sağlayıcısının backport'u
olabilir; ayrıca sorulur, varsayılmaz). PHP 8.2'nin güvenlik desteği 2026-12-31'de bitiyor →
uyarı; bu tarih geçtikten sonra 8.2 de bulgudur. Rapor eşlemesi: ≤ 8.1 bulgusu `confirmed`,
kanıt türü STATİK (`poc_girdi` = etiketin `dosya:satır`ı, `gozlenen` = sürüm), şiddet ORTA —
tarayıcı çıktısında bu sürüme düşen kritik/yüksek CVE varsa onun şiddeti; 8.2 uyarısı BILGI.

**Paket ve imaj taraması** (çıktı rapora **sayıyla**): `composer.lock` herhangi bir derinlikte
(`vendor/` hariç) varsa `composer audit` (composer yoksa ya da paket veri tabanına ulaşılamıyorsa
ÖLÇÜLMEDİ + sebep); `composer.json` var, `composer.lock` yoksa "composer.lock yok — composer audit
koşmaz, ÖLÇÜLMEDİ". İmaj taraması yalnız KAMUYA AÇIK taban imaj etiketi için (`php:…`):
`trivy image <etiket>` / `grype <etiket>` (araç kuruluysa; imaj çekmek ağ ister — araç ya da ağ
yoksa ÖLÇÜLMEDİ). Hedefin kendi/özel kayıt defterindeki imaj için "ÖLÇÜLMEDİ — yetki yok (§0.1)"
yazılır. Bulunan sürüme düşen CVE'ler ve düzeltildiği sürümler **tarayıcı çıktısından** yazılır;
tarayıcı yoksa "güncel yamalı sürümle karşılaştırma ÖLÇÜLMEDİ" yazılır.

**Rapor bloğu (v2.8.0).** PHP bulgusu serbest metin değil, `SKILL.md` ŞERİT B'deki SABİT ALANLI bloktur (`### PHP çalışma zamanı`). Mekanik kapı `php_kapisi.py` her alanı `php_olc` ölçümüyle birebir karşılaştırır: T2 PHP, sürüm+`dosya:satır` (gerçek kaynak; büyük/küçük harf dahil), yama düzeyi, EOL, composer audit (sayı ya da ölçülemedi+sebep ya da uygulanmaz), imaj taraması biçimi. Kapının DOĞRULAYAMADIĞI: (1) sayıların (composer N, tarayıcı N) gerçekliği; (2) `ÖLÇÜLEMEDİ (<sebep>)` / `UYGULANMAZ (<sebep>)` sebep metninin içeriği (yalnız ≥ 3 karakter); (3) serbest metnin tamamı — yalnız `PHP x.y … dosya:satır` kalıbı denetlenir (kaynaksız sürüm, "Dockerfile satır 2", `php` sözcüksüz satır, kısıt sözcüğü geçen satır kaçar; tarayıcı sözcüğü geçen satırda yalnız sürüm muaftır, `dosya:satır` gerçek olmalı; blok dışı alan-etiketli satırlar da bu kalıba girer ama alan DEĞERİ çelişkisi — ör. bölge dışı `EOL: DESTEKLENEN` — denetlenmez). Blok bölgesi: başlıktan ilk boş satıra kadar; bölgenin TÜM satırlarında "temiz/güvenli/risk yok" yasak; altındaki "Notlar:" alan sayılmaz; `T2 PHP` kanıtı hedefte var olan ve en az bir PHP imza dosyası içeren dosya/dizin listesi olmalı.

İsteğe bağlı mekanik denetim: `python <araclar-yolu>/php_kapisi.py --hedef <dizin> --rapor <rapor.md>`.
---

## 3. Sırrın YANLIŞ KATMANDA kullanımı

Sırrın `.env`'de olması yetmez; **nereden okunduğu** da denetlenir.

| Hata | Nasıl aranır | Neden kritik |
|---|---|---|
| Sunucu anahtarı istemciye paketleniyor | derlenmiş bundle/APK içinde anahtar deseni ara; `NEXT_PUBLIC_`, `VITE_`, `REACT_APP_` öneki taşıyan gizli anahtar | Tarayıcıya inen her şey herkese açıktır |
| Admin/service-role anahtarı tarayıcıdan çağrılıyor | Supabase `service_role`, Firebase admin SDK, Stripe `sk_live` istemci kodunda | Tam yetkiyle veri tabanına doğrudan erişim |
| Sır log'a düşüyor | `console.log(config)`, `set -x`, hata gövdesinde tam istek | Log'lar üçüncü tarafa gider |
| Sır URL'de | query string'de token → tarayıcı geçmişi, referer, sunucu log'u | Sızıntı yolları çok |
| Sır istemci depolamasında | `localStorage`'da uzun ömürlü token | XSS ile tek satırda çalınır |
| Test/örnek dosyada gerçek değer | `.env.example`, fixture, seed, README | Repo herkese açıksa bitti |

**Ölçüm:** yalnız HEAD'i değil **git geçmişinin tamamını** tara
(`git log -p -S "<desen>" --all`). HEAD'den silinmiş sır hâlâ geçmiştedir ve
**iptal edilmedikçe geçerlidir** — bulguya "anahtarı döndür" yamasını yaz.

---

## 4. Neyi BURAYA YAZMA (devir)

| Gözlem | Nereye |
|---|---|
| Yavaş sorgu, N+1, gereksiz render | `engineering:code-review` |
| İsimlendirme, ölü kod, test kapsamı | `engineering:code-review` |
| Mimari tercih (Kafka mı SQS mi) | `engineering:architecture` |
| Sürüm/artefakt spec uyumu (izin, SDK, imza) | ilgili build QA skill'i |
| Ürün/tasarım mantığı (pedagoji, ceza, ton) | ilgili tasarım red-team'i |

Sınırdaki durum: bir performans hatası **saldırgan tarafından tetiklenebiliyorsa**
(ReDoS, sınırsız sayfalama, sıkıştırma bombası) burada kalır — o zaman güvenliktir.

---

## 5. MEKANİK TARAMA KATI (envanteri genişletir, karar VERMEZ)

gedik'in elle taint-tracing'i çekirdektir; mekanik kat onu **genişletir**, yerine geçmez. Araçlar:
- **SAST:** `semgrep --config auto` · CodeQL (dil destekliyorsa) · `bandit` (Py) ·
  `gosec` (Go) · `brakeman` (Rails) · `eslint-plugin-security` (JS)
- **Sır:** `gitleaks` · `trufflehog` (gedik'in git-geçmişi taramasını mekanikleştirir)
- **Bağımlılık/konteyner:** `osv-scanner` · `grype` · `trivy` · `retire.js`
- **IaC:** `checkov` · `tfsec` · `trivy config`

> **K2 hâlâ geçerli:** her mekanik bulgu gedik'in PoC/köken-izleme süzgecinden geçer.
> "semgrep dedi" **tek başına bulgu değildir**; yanlış-pozitif elenir, gerçek olan
> PoC'yle kanıtlanır. Mekanik kat **sayıyla** raporlanır (kritik/yüksek adedi), yoksa
> ÖLÇÜLMEDİ.
