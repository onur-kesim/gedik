# ŞERİT B — Sunucu / API / Veritabanı / Kimlik Yüzeyi

**Yalnızca T2/T3/T4'ten en az biri EVET ise açılır.** Sunucusuz projede bu dosya
okunmaz; rapor Şerit B'yi tek satırda "mimari olarak yok" diye kapatır.

**Kapsam hatırlatması:** bu şerit **kodu ve yapılandırmayı** denetler ve gerekirse
kullanıcının **kendi yerel test örneğinde** dener. Canlı üçüncü taraf sisteme istek
atılmaz.

---

## B1 — Enjeksiyon

| Sınıf | Nerede aranır | Güvenli kalıp |
|---|---|---|
| SQL | dizge birleştirme ile sorgu: `"SELECT ... " + x`, f-string, `%s` yerine `%` | parametreli sorgu / hazır ifade (prepared statement); ORM'de `raw`/`literal` kullanımını tek tek incele |
| NoSQL | `find({user: req.body.user})` — nesne enjeksiyonu (`{"$ne":null}`) | tip zorlama + şema doğrulama |
| Komut | `exec`, `execSync`, `system`, `subprocess` `shell=True`, backtick | argüman dizisi, `shell=False`, beyaz liste |
| Şablon (SSTI) | `render_template_string`, kullanıcı verisi şablon kaynağı olarak | şablonu sabitle, veriyi bağlam olarak geç |
| Yol geçişi | `path.join(kök, kullanıcıGirdisi)`, `../`, mutlak yol, URL kodlu `%2e%2e` | `path.resolve` + kökün altında kalma doğrulaması |
| LDAP / XPath / CRLF | filtre/başlık birleştirme | kütüphane kaçışı |
| XXE | XML ayrıştırıcı varsayılanları | dış varlık (external entity) kapalı |
| Deserileştirme | `pickle.loads`, `yaml.load` (safe_load değil), Java `readObject`, PHP `unserialize` | güvenli ayrıştırıcı, imzalı veri |

Ölçüm kuralı: **her dinamik sorguyu tek tek aç.** "ORM kullanıyoruz" bir kanıt değildir;
her ORM'de ham sorgu kaçış kapısı vardır.

### B1.1 — ORM'de hatalı dinamik koşul ve AÇIK KALAN FİLTRE

Enjeksiyon olmadan da veri sızar: **filtre hiç uygulanmazsa.** En sık dört kalıp:

| Kalıp | Örnek | Sonuç |
|---|---|---|
| **Boş/undefined koşul** | `where(req.query.filtre ? {...} : {})` — parametre gelmezse `{}` → **tüm tablo** | Toplu veri çekme |
| **Nesne yayma (spread)** | `where: { ...req.query }` — saldırgan `{"rol":"admin"}` ya da `{"id":{"gt":0}}` enjekte eder | Filtre atlatma |
| **Koşullu `AND` düşmesi** | `if (kiraciId) q.where('tenant', kiraciId)` — `kiraciId` yoksa koşul **sessizce yok** | Kiracı sızması |
| **`OR` önceliği** | `WHERE a AND b OR c` — parantezsiz; `c` doğruysa `a AND b` baypas | Yetki atlatma |

**Denetim yöntemi (oku değil, ÖLÇ):** sorgu günlüğünü aç (Prisma `log:['query']`,
Sequelize `logging`, SQLAlchemy `echo=True`, Django `connection.queries`) ve **üretilen
SQL'i gör.** Kritik uçlarda parametre GÖNDERMEDEN çağır: üretilen SQL'de `WHERE` var mı?
Yoksa **açık filtre** bulgusudur — PoC olarak üretilen SQL'i rapora yapıştır.

**Ek:** `findMany` üst sınırı (`take`/`LIMIT`) var mı · `select` alan beyaz listesi var mı
yoksa tüm sütunlar mı dönüyor (parola hash'i dâhil) · soft-delete filtresi
(`deletedAt: null`) her sorguda var mı · `raw`/`literal`/`$queryRawUnsafe` kullanımları
tek tek gerekçeli mi.

---

### B1.2 — SQL ENJEKSİYON VARYANT MATRİSİ (CWE-89) + ORM HAM KAPILARI

> **Neden ayrı:** "parametreli sorgu kullan" tek satır bir tavsiyedir; tarayıcının **her varyantı ayrı tanıması** gerekir çünkü her biri farklı tespit tekniği ister. "ORM var, güvenli" bir kanıt değildir.

| Varyant | Neden kaçar | Bakılacak imza |
|---|---|---|
| **İkinci-mertebe (second-order)** | Sink'te birleştirme yok; zararlı veri önce **kaydedilip sonra** başka sorguda kullanılıyor | Kaynak-izlemeyi **depodan geri okumada** sürdür: DB'den okunan alan → yeni sorguya birleşiyor mu |
| **Kör (boolean-based)** | Hata yok, yanıt **farkı** var | Koşullu birleştirme + yanıtın veriye göre değişmesi |
| **Kör (time-based)** | Çıktı yok, **gecikme** var | `SLEEP`/`pg_sleep`/`WAITFOR DELAY` sink'e ulaşabiliyor mu |
| **Bant-dışı (OOB)** | Yanıtta iz yok; DNS/HTTP dışarı | DB'nin dış çağrı fonksiyonları: `UTL_HTTP`, `xp_dirtree`, `COPY…PROGRAM`, `pg_read_file`, `LOAD_FILE` |
| **`ORDER BY` / `LIMIT` / kolon-tablo adı** | **Parametrelenemez** — tavsiye burada geçersiz | Bu konumlarda **beyaz liste** var mı; kullanıcı sıralama/sütun adı belirliyorsa |
| **JSON/array operatörü** (`->>`, `@>`) | Klasik string aramasına yakalanmaz | Operatör bağlamında kullanıcı verisi birleşiyor mu |
| **Yığın/batch (stacked)** | Tek sorgu sanılır | `;` ile ikinci ifade; sürücü çoklu-ifade açık mı |
| **DB fonksiyonu içi dinamik SQL** | Uygulamada değil, DB'de | `EXECUTE format(...)` / dinamik `EXECUTE` içeren fonksiyon (Şerit C `SECURITY DEFINER` ile kesişir) |
| **ORM ham kapısı** | "ORM güvenli" varsayımı | `$queryRawUnsafe`/`$executeRawUnsafe` (Prisma) · `literal()`/`where:{[Op…]}` string (Sequelize) · `.extra()`/`.raw()`/`RawSQL` (Django) · `.where("…${x}")` (TypeORM) · `.whereRaw` (Knex) · `text()` (SQLAlchemy) |

**Denetim yöntemi (oku değil ÖLÇ):** sorgu günlüğünü aç (`log:['query']` / `echo=True` / `connection.queries`), kritik uçları **parametre göndermeden** çağır, üretilen SQL'i gör.

**PoC/mutant:** bir sink'te parametreli sorguyu string birleştirmeye çevir (kopyada) → tarama ısırıyor mu. İkinci-mertebe için: zararsız işaretli veriyi depoya yaz, sonra onu okuyan sorguda birleşme var mı izle.

> **SQLi'nin şiddeti, erişilebilen escalation sink'leriyle ölçülür — "veri okundu" ile bitmez:**
> - **MSSQL:** `xp_cmdshell` → OS komutu = **RCE**; `OPENROWSET`/`OPENQUERY`/linked server → lateral hareket / SSRF.
> - **MySQL:** `INTO OUTFILE`/`INTO DUMPFILE` → web köküne dosya yazma (webshell) = **RCE**; `LOAD_FILE` → dosya okuma. (Gerektirir: `FILE` yetkisi + `secure_file_priv`.)
> - **Postgres:** `COPY … PROGRAM` → **RCE**; `pg_read_file`/`pg_ls_dir` → dosya okuma.
> Bu sink'lere erişim **DB hesabının yetkisine** bağlıdır (→ B20). Erişim varsa bulgu **KRİTİK** (RCE/sunucu ele geçirme), yoksa veri-etkisi tavanında kalır.
> **Mutant:** kopyada app'in DB kullanıcısına ilgili yetkiyi ver + sink'e ulaşan bir enjeksiyon yolu bırak; tarama "escalation mümkün" diye işaretliyor mu.

---

### B1.3 — ENJEKSİYON VARYANT DERİNLEŞTİRME (B1.2 SQLi matrisinin kardeşi)

| Sınıf | Eksik varyant | Bakılacak imza |
|---|---|---|
| **NoSQL** | `$where` ile sunucu-taraflı **JS yürütme** (Mongo) · `$regex` ReDoS · aggregation/`mapReduce` enjeksiyonu · operatör enjeksiyonu (gövdeye `{"$..."}`) | `find/aggregate` içine kullanıcı nesnesi; tip zorlama+şema yok |
| **Komut** | **Argüman enjeksiyonu** (metakarakter değil, `--flag` sokma: `tar`/`git`/`ffmpeg`/`curl`) · env/`LD_PRELOAD`/PATH · Windows (`cmd &`, PowerShell) · dolaylı (kütüphane binary çağırıyor) | argüman dizisine kullanıcı verisi; `--`/`-` ile başlayan değer engeli var mı |
| **SSTI** | Motor matrisi: **Jinja2 · Twig · Freemarker · Velocity · Handlebars · ERB · Razor · Thymeleaf** + istemci (AngularJS `{{}}`, Vue) | kullanıcı verisi şablon **kaynağı** olarak; motor sandbox'ı |
| **XXE** | **Kör/OOB** · XML tabanlı dosya (**SVG/DOCX/XLSX/PPTX** yükleme) · XInclude · parametre entity · **billion-laughs** (entity expansion DoS) | XML ayrıştırıcı + dış varlık/DTD açık; ofis dosyası yükleme yolu |
| **Deserializasyon** | **.NET** (`BinaryFormatter`, `Json.NET TypeNameHandling`, ViewState) · **Ruby** (Marshal, `Psych`) · **Node** (`node-serialize`) · **Jackson** polymorphic · **gadget-zinciri** farkındalığı (kütüphane varlığı=risk) | dile özel ayrıştırıcı + güvenilmeyen bayt |
| **Log injection / Log4Shell** | Kullanıcı verisi log'a → **sahte kayıt** (CWE-117); **JNDI lookup** (`${jndi:ldap://…}`) → RCE | log çağrısına doğrudan kullanıcı verisi; Log4j/Logback sürümü |

**Mutant:** her sınıf için bir sink'te güvenli kalıbı güvensize çevir (kopyada); NoSQL `$where` için tip-zorlamayı kaldır; XXE için dış-varlık kapatmayı aç; tarama ısırıyor mu.

---

## B2 — Kimlik doğrulama (AuthN)

- **Parola saklama:** `bcrypt`/`argon2id`/`scrypt` — maliyet parametresi ne? Düz metin,
  MD5, SHA-1, tuzsuz SHA-256 → KRİTİK.
- **Oturum:** token nerede saklanıyor (cookie mi localStorage mı), süre, iptal
  (revocation) yolu var mı, çıkışta gerçekten geçersizleşiyor mu?
- **JWT:** `alg` doğrulanıyor mu (`none` ve HS/RS karışıklığı), imza kütüphane
  varsayılanına bırakılmış mı, `exp`/`nbf`/`aud`/`iss` kontrol ediliyor mu, sır
  uzunluğu yeterli mi?
- **Cookie bayrakları:** `HttpOnly`, `Secure`, `SameSite=Lax/Strict`, `Domain` kapsamı.
- **Parola sıfırlama:** token entropisi, tek kullanımlık mı, süreli mi, kullanıcı
  numaralandırmasına (user enumeration) izin veriyor mu ("bu e-posta kayıtlı değil")?
- **Hız sınırı / kilitleme:** giriş, sıfırlama, OTP uçlarında deneme sınırı var mı?
- **Varsayılan kimlik bilgisi:** seed/fixture içinde `admin/admin` benzeri kayıt.

### B2.1 — Hesap yaşam döngüsü ve parola politikası

- **E-posta/telefon doğrulaması var mı?** Yoksa saldırgan **başkasının e-postasıyla**
  hesap açar; o kişi sonradan kaydolmak isteyince hesap kapılmıştır (pre-hijacking).
  Doğrulanmamış hesap hangi işlemleri yapabiliyor — hiçbiri mi, hepsi mi?
- **Parola politikası:** asgari uzunluk (12+ önerilir) · **sızmış parola listesi
  kontrolü** (k-anonimlik ile HIBP) · yalnız karmaşıklık kuralı dayatmak zayıf
  parolayı engellemez (`Parola1!` kuralı geçer, sızmış listede vardır).
- **Parola değiştirme/e-posta değiştirme** mevcut parolayı istiyor mu?
- **Oturum iptali:** parola değişince diğer oturumlar düşüyor mu?
- **Hesap silme/dondurma** gerçekten erişimi kesiyor mu (KVKK ile birlikte B7).
- **Kayıt ucunda numaralandırma:** "bu e-posta zaten kayıtlı" mesajı kullanıcı listesi
  çıkarmaya izin verir; hız sınırı ve genel mesaj gerekir.

### B2.2 — OAuth/OIDC · OTURUM SABİTLEME · MFA · JWT EK VARYANTLARI

**Tetik:** B2 zaten açıksa (T4 EVET). OAuth/OIDC/SSO, MFA veya JWT görülüyorsa bu blok koşar.

**OAuth 2.0 / OIDC / SSO:**
- `redirect_uri` **tam eşleşme** ile mi doğrulanıyor (prefix/substring değil) → gevşekse **token hırsızlığı** (açık yönlendirme zinciriyle).
- `state` parametresi var ve doğrulanıyor mu (CSRF) · **PKCE** var mı (public client) · **implicit flow** kullanılıyor mu (token URL'de sızar).
- `id_token` doğrulaması: `aud` · `iss` · `nonce` · `exp` · imza. Eksikse sahte token kabul.
- **Account linking**: e-posta üzerinden hesap birleştirme doğrulanmış e-posta gerektiriyor mu (pre-hijack).
- **SAML** varsa: imza sarma (XSW), imzasız assertion, `SAMLResponse` replay.

**Oturum sabitleme (session fixation, CWE-384):** girişte session id **rotate ediliyor mu**? (B2 iptal/revocation'ı kapsar; **rotasyonu** ayrı ölç — girişten önceki id girişten sonra da geçerliyse bulgu.)

**MFA/2FA:** adım atlama (MFA'yı atlayıp korunan uca doğrudan gitme) · TOTP yeniden oynatma · backup-code brute force (hız sınırı) · "cihazı hatırla" kalıcılığı/entropisi · MFA kayıt yarışı.

**JWT ek (B2 alg=none/confusion'a ek):** `kid` header injection (path traversal/SQLi `kid` üzerinden) · `jku`/`x5u` ile sahte anahtar URL'i (**SSRF**) · gömülü `jwk` header · zayıf HMAC sırrı (brute-force) · `crit` bypass.

**PoC/mutant:** her biri için kendi örneğinde: fixation → giriş öncesi/sonrası cookie'yi karşılaştır; MFA bypass → korunan ucu MFA adımını atlayıp `curl` ile çağır; redirect_uri → beyaz liste dışı bir uri ile akışı başlat. Mutant: `state` kontrolünü / redirect_uri tam-eşleşmesini kaldır (kopyada), tarama ısırıyor mu.

---

## B3 — Yetkilendirme (AuthZ)

- **IDOR/BOLA:** `/api/kayit/123` — kayıt sahibi kontrol ediliyor mu, yoksa yalnız
  oturum açık olması yetiyor mu? **En sık ve en pahalı sunucu açığı budur.**
- **Fonksiyon düzeyi kontrol:** yönetici uçları yalnız arayüzde mi gizli?
- **Toplu atama (mass assignment):** `Object.assign(kullanıcı, req.body)` → `rol:"admin"`.
- **Kiracı izolasyonu → B3.1.**

### B3.1 — ÇOK KİRACILI / ÇOK KULLANICILI İZOLASYON

**Tek eksik `WHERE` bütün izolasyonu bitirir.** Bu yüzden "her sorguda yazmayı
hatırlarız" bir savunma değildir; mekanik zorlama aranır.

- **Zorlama nerede?** (a) her sorguda elle yazılıyor → **kırılgan**, sayıyla ölç:
  kaç sorgu var, kaçında kiracı koşulu var · (b) ORM global scope / middleware ·
  (c) veritabanı seviyesinde RLS → **en güçlüsü.**
- **Kaçak yolları:** ham SQL (`raw`, `$queryRaw`) · toplu işlem/rapor sorguları ·
  yönetici uçları · arka plan işleri (cron, kuyruk — istek bağlamı yok, kiracı
  nereden geliyor?) · dışa aktarma · arama indeksi (Elastic/Meili ayrı sistem,
  filtre orada da var mı?) · önbellek anahtarı kiracı içeriyor mu (yoksa çapraz servis).
- **Kiracı kimliği nereden geliyor?** İstek gövdesinden/başlığından geliyorsa
  saldırgan değiştirir. **Oturumdan/token'dan** türetilmeli.
- **Dosya/depolama:** yol kiracıya göre ayrılmış mı; imzalı URL kiracı doğruluyor mu?
- **Toplu/istatistik uçları:** "kaç kayıt var" sayıları başka kiracının verisini
  sızdırıyor mu?
- **PoC:** A kiracısının oturumuyla B'nin kaynak kimliğini iste — 200 dönüyorsa bulgu;
  404 mü 403 mü döndüğü de ayrı bir sızıntı (varlık teyidi).
- **Doğrudan nesne referansı içeren dosya erişimi** (imzasız S3/URL).

## B4 — Girdi/çıktı ve tarayıcı sınıfı

- **XSS:** yansıyan / kalıcı / DOM tabanlı. Şablon motoru varsayılan kaçış yapıyor mu;
  `|safe`, `dangerouslySetInnerHTML`, `v-html` kullanımlarını tek tek gerekçelendir.
- **CSP:** var mı; `unsafe-inline`/`unsafe-eval` içeriyor mu; `default-src` dar mı?
- **CSRF:** durum değiştiren istekler token veya `SameSite` ile korunuyor mu; `GET`
  ile durum değiştiren uç var mı?
- **Açık yönlendirme:** `redirect(req.query.next)` — beyaz liste var mı?
- **SSRF:** sunucu kullanıcı verdiği URL'ye istek atıyor mu; iç ağ/bulut meta veri
  adresi (`169.254.169.254`) engelli mi; yönlendirme takibi sınırlı mı?
- **Dosya yükleme:** tip **içerikten** mi doğrulanıyor (uzantıdan değil), boyut sınırı,
  yeniden adlandırma, web kökü dışına kaydetme, çalıştırılabilir uzantı engeli, zip
  bombası / zip slip.
- **CORS — KİLİTLE:** ayrıntı B4.1'de. Kısa hâli: beyaz liste sabit, yansıtma yok.

### B4.2 — WEBHOOK İMZASI (gelen webhook uçları)

Webhook ucu **kimlik doğrulaması olmayan, herkese açık bir yazma ucudur.** Saldırgan
"ödeme başarılı" ya da "abonelik yükseltildi" olayını kendisi gönderebilir.

- **İmza doğrulanıyor mu?** (Stripe `Stripe-Signature`, GitHub `X-Hub-Signature-256`,
  genel HMAC-SHA256). Doğrulanmıyorsa → **KRİTİK.**
- **HAM gövde üzerinden mi doğrulanıyor?** Gövde JSON'a çevrildikten sonra yeniden
  serileştirilirse imza tutmaz ya da baypas edilir — ham byte gerekir.
- **Sabit zamanlı karşılaştırma** kullanılıyor mu (`===` değil `timingSafeEqual`)?
- **Replay penceresi:** zaman damgası kontrol ediliyor mu (ör. ±5 dk), olay kimliği
  tekrar işlenmeye karşı **idempotent** mi kaydediliyor?
- **Kaynak IP/gizli yol** tek başına savunma sayılmaz; imza şarttır.
- Giden webhook'larda: hedef URL kullanıcı kontrolündeyse **SSRF** (B4).

### B4.1 — CORS KİLİDİ

CORS yanlış kurulduğunda **tarayıcıdaki her kullanıcı, saldırganın sayfası adına** senin
API'ne kimlikli istek atabilir. Kilit beş maddedir:

1. **Sabit beyaz liste.** İzinli origin'ler kodda/yapılandırmada SABİTTİR.
   `Access-Control-Allow-Origin` gelen `Origin` başlığından **yansıtılmaz.**
   Yansıtma varsa (`res.header('ACAO', req.headers.origin)`) bu **CORS yok** demektir.
2. **`*` + `credentials: true` YASAK.** Tarayıcı reddeder ama yansıtmayla atlatılır;
   ikisinin bir arada görülmesi tek başına KRİTİK adayıdır.
3. **Eşleşme TAM olmalı.** `startsWith`/`endsWith`/`includes` ile kontrol ATLATILIR:
   `https://site.com.saldirgan.tr` `endsWith` testini geçer ·
   `https://saldirgansite.com` `includes("site.com")` testini geçer.
   Tam eşitlik ya da ayrıştırılmış origin karşılaştırması kullan.
4. **`null` origin reddedilir.** Sandbox iframe, `data:` ve bazı yönlendirmeler
   `Origin: null` gönderir; beyaz listede `null` OLMAMALI.
5. **`Vary: Origin` zorunlu.** Yoksa CDN/ara önbellek bir origin için verilen izinli
   yanıtı başka origin'e servis eder — önbellek zehirlenmesi.

**Ek:** `Allow-Methods`/`Allow-Headers` dar mı (`*` değil) · `Max-Age` makul mü ·
preflight'a (OPTIONS) kimlik doğrulaması uygulanmıyor mu (uygulanırsa preflight kırılır).

**PoC:** `curl -i -H "Origin: https://saldirgan.example" <uç>` → yanıtta
`Access-Control-Allow-Origin: https://saldirgan.example` görünüyorsa yansıtma vardır.
`Origin: null` ve `https://<izinli>.saldirgan.example` ile de dene.

---

## B5 — Aktarım ve yapılandırma

- TLS zorunlu mu (HTTP → HTTPS yönlendirme), HSTS var mı?
- Güvenlik başlıkları: `X-Content-Type-Options`, `Referrer-Policy`,
  `X-Frame-Options`/`frame-ancestors`, `Permissions-Policy`.
- **Hata ayrıntısı → B5.1'e bak (kanal ayrımı).**
- **Uygulama→DB bağlantısı şifreli mi ve sunucu sertifikası doğrulanıyor mu?** Cleartext DB
  trafiği veya doğrulanmayan sertifika = MITM ile kimlik/veri sızıntısı.
  - MSSQL: `Encrypt=true` **ve** `TrustServerCertificate=false` (true → sahte sertifika kabul edilir).
  - MySQL: `--ssl-mode=VERIFY_IDENTITY` (yalnız `REQUIRED` sertifikayı doğrulamaz).
  - Postgres: `sslmode=verify-full`.
  **İmza:** connection string'de şifreleme kapalı ya da sertifika doğrulaması atlanmış.
  **Şiddet:** DB trafiği güvenilmeyen ağdan geçiyorsa YÜKSEK; aynı host/güvenli segment ise DÜŞÜK.

### B5.1 — HATA MESAJI KANAL AYRIMI

Tek kural: **ayrıntı log'a, genel ifade kullanıcıya.** Aynı hata iki farklı metin üretir.

| Bilgi | Kullanıcı ekranı | Sunucu log'u |
|---|---|---|
| Yığın izi (stack trace), dosya adı, satır no | **ASLA** | evet |
| Tablo/sütun adı, SQL metni, ORM hatası | **ASLA** | evet |
| İç uç yolu, kuyruk adı, servis adı, IP/port | **ASLA** | evet |
| Kütüphane/çerçeve sürümü, yığın adı | **ASLA** | evet |
| Üçüncü taraf sağlayıcı ham hatası | **ASLA** | evet |
| Kullanıcının düzeltebileceği doğrulama hatası ("tarih geçmişte olamaz") | evet | evet |
| **Korelasyon kimliği** (ör. `hata-kodu: 7f3a91`) | **evet — bu şart** | evet |

**Doğru kalıp:** kullanıcıya *"İşlem tamamlanamadı. Destek için kod: 7f3a91"*;
log'a tam ayrıntı + aynı kod. Kullanıcı kodu iletir, sen log'da bulursun — hem
sızıntı yok hem destek edilebilir.

**Neden önemli:** hata metni bir **keşif aracıdır.** SQL hatası şema adını, yığın izi
dosya yapısını ve sürümü, "kullanıcı bulunamadı" ile "parola yanlış" farkı kullanıcı
listesini verir. Saldırgan önce buradan harita çıkarır.

**Nasıl ölçülür (oku değil, TETİKLE):** üretim yapılandırmasıyla bilerek hata üret —
bozuk JSON gövde · var olmayan kaynak kimliği · tip uyumsuzluğu · aşırı uzun alan ·
veritabanı kısıtı ihlali (yinelenen benzersiz alan). **Dönen gövdenin tamamını**
incele; JSON içinde `stack`, `detail`, `hint`, `where`, `constraint`, `query`
alanları var mı bak. Çerçeve varsayılanları sızdırır: Express hata middleware'i,
FastAPI `debug=True`, Django `DEBUG=True`, Next.js dev overlay, PostgREST/Supabase
`details`/`hint` alanları.

**Ek:** hata sayfası sürüm/çerçeve başlığı (`X-Powered-By`, `Server`) döndürüyor mu ·
404 ile 403 ayrımı kaynak varlığını sızdırıyor mu · log'a **PII/token düşmüyor** mu
(B7 ile birlikte).
- Debug/geliştirme uçları açık mı (`/debug`, `/__profile`, GraphQL introspection,
  Swagger üretimde, dizin listeleme)?
- Varsayılan yönetim panelleri, açıkta kalan `.git/`, `.env`, yedek dosyaları.

## B6 — Sır yönetimi

- Kodda gömülü anahtar/parola (T6 ile aynı komutlar, sunucu dosyalarına genişlet).
- `.env` repoda mı; `.env.example` gerçek değer içeriyor mu?
- CI/CD sırları log'a yazılıyor mu (`set -x`, echo).
- Sır döndürme (rotation) yolu var mı; sızarsa ne yapılacağı yazılı mı?

### B6.1 — Sır DOĞRU KATMANDA mı kullanılıyor?

`.env`'de olması yetmez; **nereden okunduğu** denetlenir. Tam tablo:
`references/kod-inceleme-guvenlik.md` §3. Kırmızı bayraklar:
- Sunucu anahtarı istemci paketine giriyor (`NEXT_PUBLIC_`/`VITE_`/`REACT_APP_` öneki
  taşıyan **gizli** anahtar; derlenmiş bundle ya da APK içinde anahtar deseni).
- `service_role` / admin SDK / `sk_live` sınıfı tam yetkili anahtar tarayıcıdan çağrılıyor.
- Sır log'a, URL query string'ine ya da `localStorage`'a düşüyor.
- `.env.example` / fixture / seed / README gerçek değer taşıyor.

**Git geçmişinin tamamını tara** (`git log -p -S "<desen>" --all`). HEAD'den silinmiş sır
hâlâ geçmiştedir ve **iptal edilmedikçe geçerlidir** — yama "anahtarı DÖNDÜR" olur,
"dosyadan sil" YETERLİ DEĞİLDİR.

## B7 — Veri ve gizlilik

- PII envanteri: hangi alan, nerede, ne kadar süre saklanıyor?
- Dinlenme halinde şifreleme gerekiyor mu; yedekler nerede, erişimi kimde?
- **Log sızıntısı:** token, parola, kart, PII log'a düşüyor mu? (En sık gözden kaçan.)
- Silme talebi gerçekten siliyor mu (KVKK/GDPR).
- Üçüncü taraf SDK'lara giden veri.

## B8 — Kaynak tüketimi / hizmet dışı bırakma

- Sayfalama sınırı olmayan sorgu; `LIMIT` yok.
- N+1 sorgu; indekssiz filtre.
- **ReDoS:** kullanıcı verisine uygulanan geri-izlemeli (catastrophic backtracking)
  regex — `(a+)+`, iç içe niceleyici.
- İstek gövdesi boyut sınırı; JSON derinlik sınırı; sıkıştırma bombası.
- Pahalı iş (rapor, dışa aktarma) kuyruğa alınıyor mu, senkron mu?

---

## B10 — SUNUCU TARAFI DOĞRULAMA (istemci doğrulaması doğrulama DEĞİLDİR)

Arayüzdeki her kontrol bir **kolaylıktır**, savunma değildir. Saldırgan arayüzü hiç
kullanmaz: `curl` ile doğrudan uca gider.

**İlke:** istemcide yapılan HER doğrulama sunucuda **aynen tekrarlanır.**
Bu bir tercih değil, mimari kuraldır.

Denetim:
- **Şema doğrulaması var mı?** (zod, yup, joi, pydantic, JSON Schema, DTO+validator)
  Yoksa `req.body` doğrudan kullanılıyor demektir → B3 toplu atama ile birleşir.
- **Beyaz liste mi kara liste mi?** Bilinmeyen alan **atılıyor** mu (`strict`/`.strip()`),
  yoksa geçiyor mu?
- **Tip zorlaması:** `"5"` ile `5`, `"true"` ile `true`, dizi beklenirken nesne.
- **Aralık ve işaret:** negatif miktar/adet/fiyat kabul ediliyor mu? Üst sınır var mı?
- **Enum/durum geçişi:** istemci `durum: "onaylandi"` gönderebiliyor mu; iş akışı
  adımı atlanabiliyor mu (sipariş → ödeme atlanıp → kargo)?
- **Sunucunun belirlemesi gereken alanlar** istemciden geliyor mu: `fiyat`, `toplam`,
  `indirim`, `rol`, `kullanici_id`, `olusturma_tarihi`, `dogrulandi`.
  **Fiyatı istemciden almak** klasik ve ölümcül olanıdır.
- **Dosya/medya:** boyut ve MIME sunucuda mı doğrulanıyor (uzantıdan değil içerikten)?
- **İş kuralı:** kupon istifleme, aynı ödülü iki kez alma, kota aşımı — sunucuda
  atomik olarak mı uygulanıyor (yarış durumu için `kod-inceleme-guvenlik.md` §1.3)?

**PoC yöntemi:** arayüzü atla, ucu doğrudan çağır. Arayüzün engellediği değeri
`curl`/istek ile gönder; kabul ediliyorsa **bulgu**, PoC olarak isteği ve yanıtı yaz.

---

## B11 — İŞ MANTIĞI İSTİSMARI

Teknik olarak "geçerli" isteklerle sistemi soymaktır. Tarayıcılar bunu bulmaz; yalnız
**iş kurallarını okuyup kötüye kullanmayı denemek** bulur. B10 girdiyi doğrular;
burada **kuralın kendisi** kırılır.

- **İşaret ve sıfır:** negatif miktar/adet/tutar · sıfır fiyat · negatif indirim
  (iade yerine tahsil) · `Infinity`/`NaN` · çok büyük sayı taşması.
- **Tekrar ve istifleme:** aynı kupon iki kez · birden çok kupon üst üste ·
  hoş geldin bonusunu ikinci hesapla tekrar alma · davet ödülü döngüsü (A davet eder B,
  B davet eder A).
- **Yarış durumu ile çift harcama:** aynı bakiye/kotayı iki eşzamanlı istekle kullanma.
  **Test:** aynı isteği paralel 10 kez gönder; sonuç tekil mi?
  (Mekanik ayrıntı: `kod-inceleme-guvenlik.md` §1.3.)
- **İş akışı adımı atlama:** doğrudan son adımın ucuna istek atma (sepet → **ödemeyi
  atla** → kargo). Durum makinesi sunucuda mı zorlanıyor, yoksa arayüz sırası mı?
- **Geri alma/iptal istismarı:** ödülü al → işlemi iptal et → ödül kalsın mı?
- **Zaman manipülasyonu:** istemciden gelen tarih/saat ile kampanya penceresi,
  günlük limit veya seri hesaplanıyor mu? Sunucu saati esas alınmalı.
- **Kimlik çoğaltma:** e-posta `+` etiketi, nokta varyantı, tek kullanımlık e-posta ile
  aynı kişinin çok hesabı; kota/ödül bu yolla katlanıyor mu?
- **Fiyat/toplam istemciden mi geliyor?** (B10 ile aynı sınıf, en pahalısı budur.)

**Şiddet:** doğrudan parasal kayıp veya başkasının kotasını tüketme varsa **YÜKSEK**;
yalnız kendi hesabını bozuyorsa ORTA.

---

## B12 — WEBSOCKET / GERÇEK ZAMANLI KANALLAR

HTTP korumalarının çoğu WebSocket'e **kendiliğinden uygulanmaz.**

- **Origin kontrolü:** WebSocket el sıkışmasında **CORS uygulanmaz** ve `SameSite`
  çerezi çoğu tarayıcıda gönderilir → **Cross-Site WebSocket Hijacking.** Sunucu
  `Origin` başlığını beyaz listeye karşı doğruluyor mu? Doğrulamıyorsa herhangi bir
  site, kullanıcının oturumuyla soket açar. **KRİTİK aday.**
- **Kimlik:** bağlantı anında doğrulanıyor mu; token **URL'de mi** taşınıyor
  (log'a düşer) yoksa ilk mesajda/başlıkta mı?
- **Yetki her mesajda mı?** Bağlantı açılırken bir kez kontrol edip sonra her mesajı
  kabul etmek yaygın hatadır — abone olunan kanal/oda için sahiplik her mesajda
  doğrulanmalı.
- **Kanal adı tahmin edilebilir mi** (`oda-123`)? Yayın (broadcast) yanlış aboneye
  gidiyor mu?
- **Mesaj şeması:** gelen mesaj doğrulanıyor mu (B10 aynen geçerli); boyut ve hız
  sınırı var mı (bağlantı başına mesaj/saniye)?
- **Kaynak:** bağlantı sayısı sınırı, kimliksiz bağlantıya izin, ölü bağlantı temizliği.
- **Oturum sonlanması:** kullanıcı çıkış yapınca/yetkisi alınınca açık soket kapanıyor mu?

---

## B13 — GraphQL

- **Introspection** üretimde açık mı? Tek başına açık değildir ama saldırgana tam
  şema haritası verir → kapatılması beklenir.
- **Derinlik ve karmaşıklık sınırı:** iç içe ilişki sorgusu (`a{b{a{b...}}}`) ile
  tek istekte veritabanını yorma → **DoS.** Derinlik sınırı, karmaşıklık puanı ve
  zaman aşımı var mı?
- **Toplu sorgu (batching) istismarı:** tek HTTP isteğinde yüzlerce mutation ile
  **hız sınırını atlatma** (parola deneme). Hız sınırı istek başına mı, **işlem
  başına** mı?
- **Alan düzeyi yetki:** REST'te uç bazlı kontrol vardır; GraphQL'de bir alan
  (`user { email }`) yanlışlıkla açık kalabilir. Yetki **resolver seviyesinde** mi?
- **Alias çoğaltma:** aynı alanı farklı alias'larla yüzlerce kez isteme.
- **Hata mesajları:** GraphQL varsayılan olarak ayrıntılı hata döner → B5.1.
- **Kalıcı sorgu (persisted query)** kullanılıyorsa keyfi sorgu kapalı mı?

---

## B14 — İSTİSNAİ KOŞULLARIN YANLIŞ YÖNETİMİ / FAIL-OPEN (OWASP A10:2025)

Kimlik, yetki, WAF, hız-sınırlayıcı, ödeme doğrulaması **hata/zaman aşımı/kaynak tükenmesi** altında ne yapıyor: **açılıyor mu (fail-open) kapanıyor mu (fail-closed)?**

**Bakılacak imza:** `try/catch` · timeout · circuit-breaker · bağımlılık-hatası dallarında **varsayılanın "izin ver / devam et" olması**. `catch { /* logla */ }` sonrası akışın korunan işleme devam etmesi. Yetki servisi cevap vermeyince "geç" denmesi.

**PoC/mutant:** korunan yolun bağımlılığını (auth/yetki servisi, rate-limiter deposu) bilerek düşür (kopyada/yerel); istek **kabul mü ediliyor** (fail-open = bulgu) yoksa reddediliyor mu? Mutant: fail-closed dalını fail-open'a çevir, tarama ısırıyor mu.

**Şiddet:** korunan şey yetki/kimlik/ödeme ise YÜKSEK/KRİTİK.

---

## B15 — GÜVENLİK LOGLAMA & ALARM YETERSİZLİĞİ (OWASP A09:2025)

B7 log'un **sızdırmadığını** ölçer; bu bölüm **tersini**: güvenlik olayları **loglanıyor ve alarma bağlanıyor mu?**

**Bakılacak imza:** başarısız giriş · yetki reddi (403/RLS reddi) · girdi doğrulama hatası · yüksek-değerli işlem (para, rol değişimi, silme) · MFA olayları — bu yolların **audit log çağrısı var mı**, log yapısal/aranabilir mi, kritik olayda **alarm/eşik** var mı.

**PoC/mutant:** yetki-reddi ve başarısız-giriş yollarını tetikle; log kaydı **oluşuyor mu** kontrol et. Mutant: bir audit-log çağrısını kaldır (kopyada), tarama farkı görüyor mu.

**Şiddet:** genelde DÜŞÜK/BİLGİ (tek başına sömürülmez, savunma-derinliği); ama **hiç** tespit yoksa ve sistem para/PII tutuyorsa ORTA. (gedik saldırgan-odaklı; bu madde "tespit edilemezlik"i bir gedik sayar — şişirme yok.)

---

## B16 — HTTP REQUEST SMUGGLING (ön-uç/arka-uç uyuşmazlığı)

**Tetik:** T11 EVET (ters vekil/CDN + arka-uç). Statik tespit zayıftır; mimari + **kendi yerel yığınında** test gerekir.

**Bakılacak imza:** ön-uç ile arka-uç `Content-Length`/`Transfer-Encoding` işleme farkı; CL.TE / TE.CL / TE.TE / CL.CL; **HTTP/2 downgrade** (H2.CL/H2.TE). Ön-uç normalize etmeden iletiyor mu; yinelenen/uyumsuz başlıklar reddediliyor mu.

**PoC/mutant (kendi yerel ön-uç+arka-uç ikilinde):** zararsız işaretli, hem CL hem TE taşıyan istek gönder; arka-uç ikinci isteği **önceki isteğin gövdesi** olarak yorumluyor mu (desync). Etki: ön-uç yetki atlatma, başka kullanıcının isteğini zehirleme, cache poisoning (B18). **Şiddet: KRİTİK** (desync doğrulanırsa).

---

## B17 — HOST HEADER INJECTION

**Bakılacak imza:** `Host`/`X-Forwarded-Host` **güvenilmeden** kullanılıyor mu — mutlak URL üretimi (**parola-sıfırlama linki**), yönlendirme, cache anahtarı, e-posta linki. Beyaz-liste/`ALLOWED_HOSTS` var mı.

**PoC/mutant:** parola sıfırlama isteğini saldırgan `Host`'uyla gönder; üretilen link saldırgan host'u yansıtıyorsa → **hesap ele geçirme zinciri**. Mutant: host beyaz-listesini kaldır (kopyada). **Şiddet: YÜKSEK/KRİTİK.**

---

## B18 — WEB CACHE POISONING & CACHE DECEPTION

B9.3 "yanlış paylaşım"ı görür; bu **saldırgan-kontrollü** zehirlemedir.

**Bakılacak imza:** **poisoning** — unkeyed header/parametre yanıta yansıyıp önbelleğe yazılıyor (cache key'de olmayan girdi çıktıyı etkiliyor). **deception** — `/hesap/profil.css` gibi uzantı/path hilesiyle kişiye-özel yanıt önbelleğe düşüyor. Cache key bileşenleri neler; `Vary` doğru mu.

**PoC/mutant:** unkeyed header'a zararsız işaretleyici koy; **ikinci istek (header'sız)** işaretleyiciyi dönüyorsa önbellek zehirlendi. Deception: statik-görünen yol kişisel yanıtı cache'liyor mu. **Şiddet: YÜKSEK.**

---

## B19 — SUBDOMAIN TAKEOVER / DANGLING DNS

**Bakılacak imza:** CNAME kullanılmayan bir servise (S3/GitHub Pages/Heroku/Vercel/Azure) işaret ediyor; hedef "NoSuchBucket/404/unclaimed" durumunda → saldırgan claim eder. Çerez/OAuth/CSP güveni çalınır.

**PoC/mutant (kendi alan adlarında):** alt alan adlarını numaralandır, CNAME hedeflerini ve hedef servis durumunu kontrol et; dangling olan bulgu. **Şiddet: YÜKSEK** (çerez/güven kapsamı genişse KRİTİK).

---

## B20 — UYGULAMA DB-HESABI YETKİ KAPSAMI (en-az-ayrıcalık)

**Neden:** Bir SQLi'nin (ve genel DB erişiminin) ne kadar yıkıcı olacağını, uygulamanın DB'ye **hangi yetkiyle bağlandığı** belirler. App `sa`/`sysadmin`/`root`/`db_owner`/`SUPERUSER` ile bağlanıyorsa tek enjeksiyon = tüm sunucu. Bu, C3'ün (anon vs service_role) klasik-SQL karşılığıdır.

**Bakılacak imza:**
- Connection string'deki DB kullanıcısının rolü: MSSQL `sysadmin`/`db_owner`/`CONTROL SERVER`; MySQL `root`/`ALL PRIVILEGES`/`FILE`/`GRANT OPTION`; Postgres `SUPERUSER`/`CREATEROLE`.
- App tek yüksek-yetkili hesapla mı çalışıyor, yoksa okuma/yazma ayrımı + tabloya/şemaya özel GRANT var mı.
- Tehlikeli yetkiler app hesabında gereksizse fazla: `FILE` (MySQL), `xp_cmdshell` EXECUTE (MSSQL), extended/`SECURITY DEFINER` proc EXECUTE, DDL (`DROP`/`ALTER`).

**Şiddet:** yüksek-yetkili hesap + erişilebilir enjeksiyon/sink yolu → **KRİTİK**; yalnız fazla yetki ama sömürü yolu yok → DÜŞÜK (sertleştirme).

**PoC/mutant (kendi test örneğinde):** app'in bağlandığı hesabın etkin yetkilerini sorgula — MSSQL `SELECT IS_SRVROLEMEMBER('sysadmin')`; MySQL `SHOW GRANTS FOR CURRENT_USER()`; Postgres `rolsuper`/`\du`. Yüksek yetki + erişilebilir sink = blast-radius kanıtı (satır sayısı/kod yeter, veri çıkarma yok). **Mutant:** hesabı en-az-ayrıcalığa çek (kopyada) → escalation kapanıyor mu; tarama farkı görüyor mu.

---

## B9 — Hız sınırı, maliyet ve önbellek

B2'deki hız sınırı yalnız giriş/OTP uçlarını kapsar. **Bu bölüm API'nin tamamı içindir.**

### B9.1 — Hız sınırı
- **Var mı, NEREDE?** Uygulama kodunda / ters vekilde (nginx, Cloudflare) / API ağ
  geçidinde? Yalnız arayüzde (istemci debounce) ise **hız sınırı YOKTUR.**
- **Anahtar neye göre?** Yalnız IP ise NAT arkasındaki herkes aynı kovada ve saldırgan
  IP döndürerek atlatır. Kimlikli uçta kullanıcı/API-anahtarı bazlı olmalı.
- **Sayaç atomik mi?** Oku-artır-yaz yarış durumuyla sınır atlatılır
  (bkz. `kod-inceleme-guvenlik.md` §1.3). Redis `INCR` / token bucket gerekir.
- **Pahalı uçlar ayrı kovada mı?** Arama, rapor, dışa aktarma, dosya işleme, LLM/3. taraf
  çağrısı genel limitle aynı kovadaysa tek kullanıcı servisi tüketir.
- **Yanıt doğru mu?** `429` + `Retry-After`; sınır aşımında sessizce boş dönme.
- **Kilitleme DoS:** başarısız giriş kilidi, saldırganın KURBANI kilitlemesine izin veriyor mu?

### B9.2 — Maliyet kontrolü (ücretli/üçüncü taraf servisler)
LLM, SMS, e-posta, harita, depolama çağıran her uç için:
- İstek başına üst sınır (token/karakter/boyut) var mı?
- Kullanıcı başına günlük/aylık kota var mı; aşımda ne oluyor?
- Sağlayıcı panelinde bütçe alarmı kurulu mu?
- **Kimliksiz kullanıcı ücretli çağrı tetikleyebiliyor mu → doğrudan fatura DoS.**

> Klasik OWASP listelerinde yoktur ama gerçek zarar üretir: saldırgan veri çalmaz,
> **faturayı şişirir.** Şiddet genelde ORTA; otomatik ödeme varsa YÜKSEK.

### B9.3 — Önbellek
Güvenlik tarafı **yanlış paylaşımdır:**
- Kişiye özel yanıt paylaşılan önbelleğe düşüyor mu? `Cache-Control: private`/`no-store`
  eksikse CDN bir kullanıcının verisini başkasına servis eder.
- `Vary` doğru mu (`Origin, Authorization, Accept-Encoding`) — eksikse önbellek zehirlenmesi.
- Önbellek anahtarı kimlikli içerikte kullanıcıyı içeriyor mu?
- Başarım tarafı (TTL, geçersizleştirme, pahalı yanıtın önbelleğe alınması) **öneri**
  olarak yazılır, güvenlik bulgusu değildir.

---

## Şerit B hızlı kapanış kontrolü

1. Her dinamik sorgu tek tek incelendi mi (ORM "güvenli" varsayılmadı)?
2. Her kaynak uç için **sahiplik** kontrolü doğrulandı mı (IDOR)?
3. Parola/token saklama algoritması ve parametreleri okundu mu?
4. Üretim yapılandırmasında hata ayrıntısı ve debug uçları kapalı mı?
5. `.env`/sır git geçmişinin tamamında arandı mı?
6. CORS beyaz listesi SABİT mi (yansıtma yok), `Vary: Origin` var mı?
7. Her pahalı/ücretli uçta hız sınırı ve kota SUNUCUDA ölçüldü mü?
8. Sır yalnız `.env`'de değil, **doğru katmanda** mı kullanılıyor (istemciye sızmıyor)?
9. ORM sorguları parametresiz çağrılınca `WHERE` üretiyor mu (açık filtre yok)?
10. Bağımlılık CVE taraması koştu mu (sayıyla)?
11. Üretim yapılandırmasında hata BİLEREK tetiklendi mi; dönen gövdede `stack`/`detail`/
    `hint`/`query` alanı yok mu (B5.1)?
12. İstemcinin engellediği bir değer `curl` ile kabul ediliyor mu (B10)?
13. Gelen webhook uçlarında imza HAM gövdeden ve sabit zamanlı doğrulanıyor mu (B4.2)?
14. Kiracı koşulu kaç sorguda var, kaçında yok — sayıyla ölçüldü mü (B3.1)?
15. Aynı istek paralel 10 kez gönderildiğinde sonuç tekil mi (B11 yarış)?
16. WebSocket el sıkışmasında `Origin` beyaz listeye karşı doğrulanıyor mu (B12)?
17. GraphQL varsa derinlik/karmaşıklık sınırı ve işlem-başı hız sınırı var mı (B13)?
18. SQLi varyant matrisi tarandı mı — özellikle **ikinci-mertebe** ve **ORDER BY/kolon beyaz-liste** (B1.2)?
19. OAuth/OIDC akışı varsa `redirect_uri`/`state`/PKCE, oturum sabitleme (fixation) ve MFA ölçüldü mü (B2.2)?
20. Kritik yollarda bağımlılık düşürülünce sistem **fail-open** mı oluyor (B14)?
21. Yetki reddi/başarısız giriş yolları **audit log**'a düşüyor mu (B15)?
22. NoSQL/komut/SSTI/XXE/deserializasyon varyant derinleştirmesi ve Log4Shell/JNDI tarandı mı (B1.3)?
23. T11 EVET ise (ters vekil/CDN): request smuggling (B16), host header injection (B17),
    cache poisoning/deception (B18) ölçüldü mü?
24. Subdomain/DNS envanteri dangling CNAME için tarandı mı (B19)?
25. **B20 app DB-hesabı yetkisi ölçüldü mü; SQLi escalation sink'leri erişilebilir mi (B1.2)?**
26. En az iki alanda self-mutant koştu ve ısırdı mı?
