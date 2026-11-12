# LANE B / RSC — Next.js · React Server Components · Server Actions

**An addendum to Lane B:** if T2 is YES and the repo has `next`, `react-server-dom-*`, or a `'use server'`
signature, read it TOGETHER with `serit-B-sunucu.md`. Findings enter Lane B's report as `G-n`.

> **Core principle:** every function marked `'use server'` is an **HTTP endpoint that can be called
> directly from the browser** — being wired to a form button does not make it "internal". The client
> chooses the arguments.

**PoC rule (K2, without running):** `file:line` + function + missing check + the sink the argument flows
to. A live call is FORBIDDEN (§0.1); it is tried only on the user's own local test instance.

---

## R1 — Server function = public endpoint (HIGH/CRITICAL)

In every `'use server'` function LOOK FOR: (1) a **session** (who is calling), (2) **ownership/authorization**
(is this record theirs), (3) a **schema** (is the argument validated with `zod` or similar). If any of the
three is missing, it is a finding. If the argument goes straight into the data layer via
`prisma.*.update({ data: input })` / `.set(input)` / `Object.assign` it is **mass assignment**: the client
writes fields such as `role`, `isAdmin`, `ownerId` itself (CRITICAL).

```ts
// bad: argument goes straight to the data layer (mass assignment), no session/ownership/schema
'use server'
export async function updateProfile(id: string, input: any) {
  return prisma.user.update({ where: { id }, data: input })
}
```

Compare:

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

**NOT a finding:** if session + ownership + schema are all present (as in the example above), write "no
finding" for R1.

## R2 — Authorization only in middleware (HIGH)

`middleware.ts` / `proxy.ts` has auth but the route handler / server action / page has **no second check**:
a path that bypasses the matcher (e.g. a rewrite or an internal header) or one the middleware does not
cover stays unprotected. Authorization must also be verified **next to the data** (inside the action/handler).

```ts
// middleware.ts: auth only here; no second check in app/admin/page.tsx or actions -> R2
export const config = { matcher: ['/admin/:path*'] }
```

## R3 — Version (vulnerability matching from a scanner)

The `next` and `react-server-dom-*` version and its **source** (`file:line`: `package.json`, lockfile) are
written in the report. Whether the version is vulnerable comes **from a scanner** (`npm audit`,
`osv-scanner`, trivy/grype); with no scanner or no network write **"NOT MEASURED — version matching needs a
scanner"**. A from-memory "below X is vulnerable" or "current, clean" verdict is FORBIDDEN: this skill keeps no
fixed CVE list.

## R4 — `use cache` key and configuration SSRF (MEDIUM, one-line signature)

- If the key of a `use cache` function holds no user/session-specific value, one user's data can be served
  to another (the RSC form of B18 cache deception).
- `next.config.js`: input in a `rewrites` destination hostname (`:param`) or `hostname: '**'` in
  `images.remotePatterns` → a server-side request-forwarding (SSRF) surface:

```js
// next.config.js signatures (R4)
rewrites: [{ source: '/p/:host', destination: 'https://:host/x' }]
images: { remotePatterns: [{ hostname: '**' }] }
```

---

## Lane B / RSC quick close-out check

1. Was every `'use server'` function listed; was session + ownership + schema looked for in each (R1)?
2. Does an argument go straight into the data layer as `data: input` / `.set(input)` (mass assignment)?
3. Is the middleware auth backed by a second check in the handler/action/page (R2)?
4. Were the `next` / `react-server-dom-*` version + source written; did matching come from a scanner, or is it
   NOT MEASURED (R3)?
5. Were the `use cache` key and the `rewrites`/`remotePatterns` signature checked (R4)?
