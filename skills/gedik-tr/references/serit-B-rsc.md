# ŞERİT B / RSC — Next.js · React Server Components · Server Actions

**Şerit B'nin ekidir:** T2 EVET ve depoda `next`, `react-server-dom-*` ya da `'use server'` imzası varsa
`serit-B-sunucu.md` ile BİRLİKTE okunur. Bulgular `G-n` olarak B şeridinin raporuna girer.

> **Temel ilke:** `'use server'` işaretli her fonksiyon, tarayıcıdan **doğrudan çağrılabilen bir HTTP
> uç noktasıdır** — formdaki düğmeye bağlı olması onu "iç" yapmaz. İstemci, argümanları kendi seçer.

**PoC kuralı (K2, çalıştırmadan):** `dosya:satır` + fonksiyon + eksik kontrol + argümanın aktığı sink.
Canlı çağrı YASAK (§0.1); yerel test örneğinde yalnız kullanıcının kendi kurulumunda denenir.

---

## R1 — Server function = herkese açık uç nokta (YÜKSEK/KRİTİK)

Her `'use server'` fonksiyonunda şunlar ARANIR: (1) **oturum** (kim çağırıyor), (2) **sahiplik/yetki**
(bu kayıt onun mu), (3) **şema** (argüman `zod`/benzeriyle doğrulanıyor mu). Üçünden biri yoksa bulgu.
Argüman doğrudan `prisma.*.update({ data: input })` / `.set(input)` / `Object.assign` ile veri katmanına
gidiyorsa **mass assignment**: istemci `role`, `isAdmin`, `ownerId` gibi alanları kendi yazar (KRİTİK).

```ts
// bad: argument goes straight to the data layer (mass assignment), no session/ownership/schema
'use server'
export async function updateProfile(id: string, input: any) {
  return prisma.user.update({ where: { id }, data: input })
}
```

Karşılaştır:

```ts
// good: session + ownership + schema, then allowed fields only
'use server'
export async function updateProfile(id: string, input: unknown) {
  const s = await auth(); if (!s) throw new Error('401')
  if (s.user.id !== id) throw new Error('403')
  const data = schema.pick({ name: true }).parse(input)
  return prisma.user.update({ where: { id }, data })
}
```

**Bulgu DEĞİL:** oturum + sahiplik + şema üçü de varsa (örnek yukarıdaki gibi) R1'de "bulgu yok" yazılır.

## R2 — Yalnız middleware'de yetki (YÜKSEK)

`middleware.ts` / `proxy.ts` içinde auth var ama ilgili route handler / server action / sayfada **ikinci
kontrol yok**: matcher'ı atlatan yol (ör. rewrite ya da dahili başlık) ya da middleware'in kapsamadığı yol
korumasız kalır. Yetki **verinin yanında** (action/handler içinde) da doğrulanmalıdır.

```ts
// middleware.ts: auth only here; no second check in app/admin/page.tsx or actions -> R2
export const config = { matcher: ['/admin/:path*'] }
```

## R3 — Sürüm (açık eşleşmesi tarayıcıdan)

`next` ve `react-server-dom-*` sürümü ve **kaynağı** (`dosya:satır`: `package.json`, lockfile) raporda
yazılır. Sürümün açıklı olup olmadığı **tarayıcıdan** gelir (`npm audit`, `osv-scanner`, trivy/grype); tarayıcı
yoksa ya da ağ yoksa **"ÖLÇÜLEMEDİ — sürüm eşlemesi tarayıcı ister"**. Ezberden "X altı açıklı" ya da
"güncel, temiz" hükmü YASAK: sabit CVE listesi bu skill'de tutulmaz.

## R4 — `use cache` anahtarı ve yapılandırma SSRF'si (ORTA, tek satır imza)

- `use cache` ile önbelleğe alınan fonksiyonun anahtarında kullanıcıya/oturuma özgü değer yoksa bir
  kullanıcının verisi başkasına sunulabilir (B18 cache deception'ın RSC hâli).
- `next.config.js`: `rewrites` hedefinde hostname'e girdi (`:param`) ya da `images.remotePatterns` içinde
  `hostname: '**'` → sunucu tarafı istek yönlendirme (SSRF) yüzeyi:

```js
// next.config.js signatures (R4)
rewrites: [{ source: '/p/:host', destination: 'https://:host/x' }]
images: { remotePatterns: [{ hostname: '**' }] }
```

---

## Şerit B / RSC hızlı kapanış kontrolü

1. Her `'use server'` fonksiyonu listelendi mi; her birinde oturum + sahiplik + şema arandı mı (R1)?
2. Argüman doğrudan `data: input` / `.set(input)` ile veri katmanına gidiyor mu (mass assignment)?
3. Middleware'deki auth, handler/action/sayfada ikinci kontrolle destekleniyor mu (R2)?
4. `next` / `react-server-dom-*` sürümü + kaynağı yazıldı mı; eşleme tarayıcıdan mı, yoksa ÖLÇÜLEMEDİ mi (R3)?
5. `use cache` anahtarı ve `rewrites`/`remotePatterns` imzası baktı mı (R4)?
