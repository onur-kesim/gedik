# ŞERİT C — BaaS / Doğrudan-İstemci Veritabanı (Supabase · Firebase · Appwrite · PocketBase)

**Yalnızca T7 EVET ise açılır.**

## Neden ayrı bir şerit

Klasik mimaride istemci → **sunucu** → veritabanı gider; yetkiyi sunucu uygular.
BaaS mimarisinde istemci **doğrudan veritabanıyla** konuşur. Arada yetki uygulayacak
kod YOKTUR.

> **Tek cümlelik sonuç:** BaaS'ta RLS/kurallar **tek yetkilendirme katmanıdır.**
> Kapalıysa yetkilendirme yoktur — arayüzde ne yazdığının hiçbir önemi yok.
> Saldırgan arayüzü kullanmaz; anon anahtarla REST/SDK'ya doğrudan çağrı atar.

**Bu şeritte "arayüzde göstermiyoruz" bir savunma DEĞİLDİR** ve bulgu olarak bu
gerekçe kabul edilmez.

---

## C1 — RLS KAPALI TABLO TARAMASI (ilk iş, istisnasız)

Supabase/Postgres'te tam liste (kullanıcının **kendi** projesinde, SQL editöründe):

```sql
select schemaname, tablename, rowsecurity
from pg_tables
where schemaname not in ('pg_catalog','information_schema')
order by rowsecurity asc, tablename;
```

`rowsecurity = false` olan **her satır bir bulgudur.** Şiddet: tablo PII/kullanıcı
verisi taşıyorsa **KRİTİK**; genel referans verisi (il listesi, kategori) ise BİLGİ.

**Üç durumu birbirine karıştırma:**

| Durum | Anlamı | Sonuç |
|---|---|---|
| RLS **kapalı** | Anon anahtarı olan herkes tabloyu okur/yazar | **AÇIK** — kritik aday |
| RLS **açık, politika YOK** | Postgres varsayılanı: her şey RED | Güvenli ama uygulama kırılır — işlevsel bulgu |
| RLS **açık, politika var** | Politikanın kendisi denetlenir → C2 | Ölçülmeden "temiz" DENMEZ |

> **En sık yanlış "temiz":** "RLS açık" görüp geçmek. RLS açık ama politika
> `USING (true)` ise RLS **hiçbir şey yapmıyor** demektir. C2'yi atlamak, bu şeridi
> hiç koşmamakla aynıdır.

---

## C2 — POLİTİKA DOĞRULUĞU

```sql
select schemaname, tablename, policyname, cmd, roles, qual, with_check
from pg_policies
order by tablename, cmd;
```

Her politika için dört soru:

**1. `USING` sahipliği gerçekten kısıtlıyor mu?**
- `USING (true)` → RLS var ama açık. **BULGU.**
- `USING (auth.uid() = user_id)` → doğru kalıp.
- `USING (auth.role() = 'authenticated')` → **YETERSİZ**: giriş yapan HERKES herkesin
  verisini görür. Bu, RLS'nin en sık yanlış kurulumu.

**2. `WITH CHECK` var mı?** (INSERT/UPDATE için)
- `WITH CHECK` yoksa kullanıcı **başkasının adına satır yazabilir**
  (`user_id: <başkası>` göndererek). `USING` yalnız okumayı/hedef satırı kısıtlar,
  yazılan içeriği kısıtlamaz. **En pahalı ve en sık kaçan madde budur.**
- UPDATE'te hem `USING` hem `WITH CHECK` olmalı — aksi hâlde kullanıcı kendi satırını
  başkasına devredebilir.

**3. Dört komutun hepsi kapsanmış mı?** `SELECT · INSERT · UPDATE · DELETE`
- Yalnız `FOR SELECT` politikası yazılmış tablolarda DELETE serbest kalabilir.
- `FOR ALL` yazıldıysa `WITH CHECK`'in de verildiğini doğrula.

**4. Rol kapsamı doğru mu?** `roles` sütunu `{public}` ise politika `anon`'u da kapsar;
kimlikli olması gereken bir tablo için beklenen `{authenticated}`.

**Ek tuzaklar:**
- **`SECURITY DEFINER` fonksiyonlar RLS'yi BAYPAS EDER.** `select proname, prosecdef
  from pg_proc where prosecdef = true;` — her birini tek tek gerekçelendir; içinde
  kullanıcı girdisiyle sorgu kuruyorsa ayrıca B1 (enjeksiyon) uygula.
- **Görünümler (VIEW):** Postgres 15 öncesinde view sahibinin haklarıyla çalışır ve
  RLS'yi atlatabilir; `security_invoker = true` var mı?
- **`postgres`/`service_role` rolü RLS'ye tabi değildir** → C3.

---

## C3 — ANAHTAR KAPSAMI (anon vs service_role)

| Anahtar | Nerede olmalı | Nerede OLMAMALI |
|---|---|---|
| `anon` / publishable | İstemcide olması **normaldir** — güvenliği RLS sağlar | — |
| `service_role` / secret | **Yalnız sunucu** (Edge Function, backend, CI) | İstemci kodu, bundle, mobil paket, repo, `NEXT_PUBLIC_*` |

- **`service_role` RLS'yi tamamen baypas eder.** İstemciye sızmışsa tüm veritabanı
  açıktır → **KRİTİK**, tartışmasız.
- Arama: derlenmiş bundle/APK içinde `service_role`, `eyJ...` JWT deseni,
  `SUPABASE_SERVICE_ROLE_KEY`, `sk_live`, admin SDK başlatma çağrısı.
- **`NEXT_PUBLIC_` / `VITE_` / `REACT_APP_` önekli hiçbir değişken gizli olamaz** —
  öneki taşıyan bir gizli anahtar tanım gereği yayınlanmıştır.
- Git geçmişinin tamamını tara; bulunan anahtar **döndürülür**, silinmez.

---

## C4 — DEPOLAMA (Storage) POLİTİKALARI

Veritabanı kilitli olup depolamanın açık kalması yaygındır.
- Kova (bucket) **public mi private mı**? Public kovadaki her nesne URL'i bilen herkese açık.
- Nesne düzeyinde politika var mı; yol kullanıcı kimliğiyle ayrılıyor mu
  (`user_id/dosya.png`) ve politika bunu **zorunlu kılıyor mu**?
- İmzalı URL süresi makul mü; süresiz/uzun ömürlü imzalı URL üretiliyor mu?
- Yükleme: MIME **içerikten** doğrulanıyor mu, boyut sınırı var mı, dosya adı
  kullanıcıdan mı geliyor (yol geçişi)?
- Yükleme kotası yok ise **depolama maliyeti DoS** (bkz. B9.2).

---

## C5 — RPC / EDGE FUNCTION / SUNUCU FONKSİYONU

- Edge Function'a **kimlik doğrulaması** uygulanıyor mu, yoksa herkese açık uç mu?
- Fonksiyon içinde `service_role` kullanılıyorsa: girdi doğrulaması ve yetki kontrolü
  **fonksiyonun içinde** yapılıyor mu? (RLS devre dışı olduğu için tek koruma budur.)
- RPC parametreleri şema doğrulamasından geçiyor mu; doğrudan sorguya giriyor mu (B1)?
- Fonksiyon hız sınırına tabi mi (B9.1); ücretli servis çağırıyorsa kotası var mı (B9.2)?

---

## C6 — REALTIME / ABONELİK KANALLARI

- Realtime yayını RLS'ye tabi mi (Supabase'de tablo bazında açılır — açık mı)?
- Kanal adına abone olan herkes tüm değişiklikleri görüyor mu?
- Presence/broadcast kanallarında yetki kontrolü var mı, kanal adı tahmin edilebilir mi?

---

## C7 — FIREBASE / DİĞER BaaS KARŞILIKLARI

| Supabase | Firebase | Kontrol |
|---|---|---|
| RLS politikası | Firestore/RTDB Security Rules | `allow read, write: if true;` → **AÇIK** |
| `auth.uid() = user_id` | `request.auth.uid == resource.data.uid` | sahiplik zorunlu mu |
| `WITH CHECK` | `allow create/update: if request.resource.data...` | yazılan içerik doğrulanıyor mu |
| `service_role` | Admin SDK | istemcide OLMAMALI |
| Storage politikası | Storage Rules | kova kuralı ayrı yazılır, unutulur |

Firebase'e özel: **kurallar simülatörü** ile test edilmiş mi; `if request.auth != null`
tek başına yetersizdir (giriş yapan herkes ≠ sahip).

---

## C8 — PoC: NASIL KANITLANIR (K2 zorunlu)

Ölçüm arayüzden değil, **doğrudan API'den** yapılır — kullanıcının **kendi** projesinde:

1. Anon anahtarla, **başka bir kullanıcıya ait** olduğu bilinen bir satırı çekmeyi dene:
   `curl "<proje>/rest/v1/<tablo>?select=*" -H "apikey: <anon>"`
   → satır dönüyorsa **RLS yok/etkisiz**. Dönen satır sayısını rapora yaz.
2. Kimlikli kullanıcı A'nın oturumuyla kullanıcı B'nin satırını okumayı/güncellemeyi dene
   (BOLA'nın BaaS hâli).
3. `user_id` alanını **başkasının kimliğiyle** göndererek INSERT dene → başarılıysa
   `WITH CHECK` eksiktir.
4. Depolamada: private olması gereken bir nesnenin URL'ini imzasız çağır.

**Zararsızlık kuralı:** kanıt için gerçek başkasının verisi dışarı çıkarılmaz; satır
sayısı, dönen alan adları ve HTTP kodu yeterlidir. Veriyi rapora yapıştırma.

---

## C9 — SUPABASE/POSTGREST DERİNLEŞTİRME

RLS tablo satırını kısıtlar; aşağıdakiler **RLS'nin yanından** dolaşır.

| # | Zayıflık | Bakılacak imza | Şiddet |
|---|---|---|---|
| C9.1 | **Açığa çıkan VIEW/function** | PostgREST `public` şemadaki VIEW ve fonksiyonları **otomatik uç** yapar; RLS view'a (PG15 öncesi) uygulanmayabilir | YÜKSEK |
| C9.2 | **Kolon-düzeyi GRANT** | RLS satırı kısıtlar ama `GRANT SELECT(kolon)` ayrıdır; `anon`/`authenticated`'a fazla kolon (parola hash, e-posta) verilmiş mi | YÜKSEK |
| C9.3 | **DB'den SSRF (`pg_net`/`http`)** | `pg_net`/`http` uzantısı açık + fonksiyon kullanıcı verisiyle URL kuruyor → DB iç ağa istek atar | KRİTİK |
| C9.4 | **`anon`'a EXECUTE** | Fonksiyonlara `anon` rolüne verilmiş `EXECUTE`; RPC kimliksiz çağrılabiliyor | DEĞİŞKEN |
| C9.5 | **`public` şema aşırı ifşası** | PostgREST'e açık şema daraltılmamış; iç tablolar REST'te görünür | ORTA/YÜKSEK |

**PoC/mutant (kendi projende, doğrudan REST):** `curl "<proje>/rest/v1/<view>?select=*" -H "apikey: <anon>"` → dönen **satır sayısı** ve alan adları (içerik değil). `pg_net` için: fonksiyonu zararsız kendi-URL'inle çağır, DB'nin dış istek attığını gör. Mutant: bir kolon GRANT'ini genişlet / view'ı `security_invoker`'dan çıkar (kopyada), tarama ısırıyor mu.

---

## Şerit C hızlı kapanış kontrolü

1. `pg_tables` taraması koştu mu; `rowsecurity=false` tablo sayısı raporda var mı?
2. Her politika `USING` **ve** (yazma varsa) `WITH CHECK` ile mi denetlendi?
3. `auth.role() = 'authenticated'` tipi sahte-kısıt politika var mı?
4. Dört komutun (SELECT/INSERT/UPDATE/DELETE) hepsi kapsandı mı?
5. `SECURITY DEFINER` fonksiyonlar tek tek gerekçelendirildi mi?
6. `service_role` istemci paketinde aranıp **bulunmadığı** kanıtlandı mı?
7. Storage kovaları ve kuralları ayrıca denetlendi mi?
8. En az bir PoC doğrudan API'den koşturuldu mu (arayüzden değil)?
9. Açığa çıkan VIEW/function ve kolon-düzeyi GRANT'ler denetlendi mi (C9.1/C9.2)?
10. `pg_net`/`http` uzantısı üzerinden DB'den SSRF ölçüldü mü (C9.3)?
