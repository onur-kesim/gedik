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
