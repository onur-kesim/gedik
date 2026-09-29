# LANE B — Server / API / Database / Identity Surface

**Opens only if at least one of T2/T3/T4 is YES.** In a serverless project this file
is not read; the report closes LANE B in a single line as "architecturally absent."

**Scope reminder:** this lane audits **code and configuration** and, when needed,
tests it against the user's **own local test instance**. No requests are sent to a live
third-party system.

---

## B1 — Injection

| Class | Where to look | Safe pattern |
|---|---|---|
| SQL | query built via string concatenation: `"SELECT ... " + x`, f-string, `%` instead of `%s` | parameterized query / prepared statement; review every `raw`/`literal` use in the ORM individually |
| NoSQL | `find({user: req.body.user})` — object injection (`{"$ne":null}`) | type coercion + schema validation |
| Command | `exec`, `execSync`, `system`, `subprocess` `shell=True`, backtick | argument array, `shell=False`, allowlist |
| Template (SSTI) | `render_template_string`, user data used as the template source | fix the template, pass data only as context |
| Path traversal | `path.join(root, userInput)`, `../`, absolute path, URL-encoded `%2e%2e` | `path.resolve` + validation that the result stays under the root |
| LDAP / XPath / CRLF | filter/header concatenation | library-provided escaping |
| XXE | XML parser defaults | external entities disabled |
| Deserialization | `pickle.loads`, `yaml.load` (not safe_load), Java `readObject`, PHP `unserialize` | safe parser, signed data |

Measurement rule: **open every dynamic query individually.** "We use an ORM" is not
proof; every ORM has a raw-query escape hatch.

### B1.1 — Faulty dynamic conditions in the ORM and an OPEN FILTER

Data leaks even without injection: **when the filter is never applied at all.** The
four most common patterns:

| Pattern | Example | Result |
|---|---|---|
| **Empty/undefined condition** | `where(req.query.filter ? {...} : {})` — if the parameter is absent, `{}` → **the entire table** | Bulk data extraction |
| **Object spread** | `where: { ...req.query }` — the attacker injects `{"role":"admin"}` or `{"id":{"gt":0}}` | Filter bypass |
| **Conditional `AND` dropping** | `if (tenantId) q.where('tenant', tenantId)` — if `tenantId` is absent the condition is **silently missing** | Tenant leakage |
| **`OR` precedence** | `WHERE a AND b OR c` — unparenthesized; if `c` is true, `a AND b` is bypassed | Authorization bypass |

**Audit method (don't read, MEASURE):** turn on query logging (Prisma `log:['query']`,
Sequelize `logging`, SQLAlchemy `echo=True`, Django `connection.queries`) and **see the
generated SQL.** Call critical endpoints WITHOUT sending a parameter: does the generated
SQL have a `WHERE`? If not, that's an **open filter** finding — paste the generated SQL
into the report as the PoC.

**Also:** is there an upper bound (`take`/`LIMIT`) on `findMany` · is there a `select`
field allowlist or do all columns come back (including the password hash) · is the
soft-delete filter (`deletedAt: null`) present on every query · is every use of
`raw`/`literal`/`$queryRawUnsafe` individually justified.

---

### B1.2 — SQL INJECTION VARIANT MATRIX (CWE-89) + ORM RAW ESCAPE HATCHES

> **Why separate:** "use a parameterized query" is a one-line recommendation; the
> scanner needs to **recognize every variant separately** because each requires a
> different detection technique. "We have an ORM, so we're safe" is not proof.

| Variant | Why it slips through | Signature to look for |
|---|---|---|
| **Second-order** | No concatenation at the sink; the malicious data is **first stored and then** used in another query | Extend source-tracing **into the read-back from storage**: does a field read from the DB get concatenated into a new query |
| **Blind (boolean-based)** | No error, but there's a **difference** in the response | Conditional concatenation + response changing based on data |
| **Blind (time-based)** | No output, but there's a **delay** | Can `SLEEP`/`pg_sleep`/`WAITFOR DELAY` reach the sink |
| **Out-of-band (OOB)** | No trace in the response; DNS/HTTP goes outbound | The DB's outbound-call functions: `UTL_HTTP`, `xp_dirtree`, `COPY…PROGRAM`, `pg_read_file`, `LOAD_FILE` |
| **`ORDER BY` / `LIMIT` / column-table name** | **Cannot be parameterized** — the standard advice doesn't apply here | Is there an **allowlist** at these positions; if the user determines the sort/column name |
| **JSON/array operator** (`->>`, `@>`) | Not caught by classic string searching | Is user data concatenated in the operator context |
| **Stacked/batch** | Assumed to be a single query | A second statement via `;`; is the driver's multi-statement support enabled |
| **Dynamic SQL inside a DB function** | Lives in the DB, not the application | A function containing `EXECUTE format(...)` / dynamic `EXECUTE` (overlaps with LANE C `SECURITY DEFINER`) |
| **ORM raw escape hatch** | The "ORM is safe" assumption | `$queryRawUnsafe`/`$executeRawUnsafe` (Prisma) · `literal()`/`where:{[Op…]}` string (Sequelize) · `.extra()`/`.raw()`/`RawSQL` (Django) · `.where("…${x}")` (TypeORM) · `.whereRaw` (Knex) · `text()` (SQLAlchemy) |

**Audit method (don't read, MEASURE):** turn on query logging (`log:['query']` /
`echo=True` / `connection.queries`), call critical endpoints **without sending a
parameter**, see the generated SQL.

**PoC/mutant:** at one sink, convert the parameterized query to string concatenation
(in a copy) → does the scan bite. For second-order: write a harmless marked value to
storage, then trace whether the query that reads it back concatenates it in.

> **SQLi's severity is measured by the escalation sinks it can reach — it doesn't stop
> at "data was read":**
> - **MSSQL:** `xp_cmdshell` → OS command = **RCE**; `OPENROWSET`/`OPENQUERY`/linked server → lateral movement / SSRF.
> - **MySQL:** `INTO OUTFILE`/`INTO DUMPFILE` → writing a file to the web root (webshell) = **RCE**; `LOAD_FILE` → file read. (Requires: `FILE` privilege + `secure_file_priv`.)
> - **Postgres:** `COPY … PROGRAM` → **RCE**; `pg_read_file`/`pg_ls_dir` → file read.
> Access to these sinks depends on the **DB account's privileges** (→ B20). If access exists the finding is **CRITICAL** (RCE/server takeover); otherwise it stays capped at data-impact.
> **Mutant:** in a copy, grant the app's DB user the relevant privilege + leave an injection path reaching the sink; does the scan flag "escalation possible."

---

### B1.3 — INJECTION VARIANT DEEPENING (sibling of the B1.2 SQLi matrix)

| Class | Missing variant | Signature to look for |
|---|---|---|
| **NoSQL** | Server-side **JS execution** via `$where` (Mongo) · `$regex` ReDoS · aggregation/`mapReduce` injection · operator injection (`{"$..."}` in the body) | A user object passed into `find/aggregate`; no type coercion + schema |
| **Command** | **Argument injection** (not a metacharacter, but slipping in a `--flag`: `tar`/`git`/`ffmpeg`/`curl`) · env/`LD_PRELOAD`/PATH · Windows (`cmd &`, PowerShell) · indirect (a library shelling out to a binary) | User data in the argument array; is there a block on values starting with `--`/`-` |
| **SSTI** | Engine matrix: **Jinja2 · Twig · Freemarker · Velocity · Handlebars · ERB · Razor · Thymeleaf** + client-side (AngularJS `{{}}`, Vue) | User data used as the template **source**; the engine's sandbox |
| **XXE** | **Blind/OOB** · XML-based files (**SVG/DOCX/XLSX/PPTX** upload) · XInclude · parameter entity · **billion-laughs** (entity expansion DoS) | XML parser with external entities/DTD enabled; office-file upload path |
| **Deserialization** | **.NET** (`BinaryFormatter`, `Json.NET TypeNameHandling`, ViewState) · **Ruby** (Marshal, `Psych`) · **Node** (`node-serialize`) · **Jackson** polymorphic · **gadget-chain** awareness (a library's mere presence = risk) | Language-specific parser + untrusted bytes |
| **Log injection / Log4Shell** | User data into a log → **forged log entry** (CWE-117); **JNDI lookup** (`${jndi:ldap://…}`) → RCE | User data going directly into a log call; Log4j/Logback version |

**Mutant:** for each class, convert the safe pattern at one sink to an unsafe one (in a
copy); for NoSQL `$where`, remove the type coercion; for XXE, re-enable external
entities; does the scan bite.

---

## B2 — Authentication (AuthN)

- **Password storage:** `bcrypt`/`argon2id`/`scrypt` — what's the cost parameter?
  Plaintext, MD5, SHA-1, unsalted SHA-256 → CRITICAL.
- **Session:** where is the token stored (cookie vs. localStorage), lifetime, is there
  a revocation path, does it actually invalidate on logout?
- **JWT:** is `alg` validated (`none` and HS/RS confusion), is the signature left to
  the library default, are `exp`/`nbf`/`aud`/`iss` checked, is the secret long enough?
- **Cookie flags:** `HttpOnly`, `Secure`, `SameSite=Lax/Strict`, `Domain` scope.
- **Password reset:** token entropy, is it single-use, is it time-limited, does it
  allow user enumeration ("this email is not registered")?
- **Rate limiting / lockout:** is there an attempt limit on login, reset, and OTP endpoints?
- **Default credentials:** an `admin/admin`-style record in seed/fixture data.

### B2.1 — Account lifecycle and password policy

- **Is there email/phone verification?** If not, an attacker opens an account **using
  someone else's email**; when that person later tries to sign up, the account has
  already been hijacked (pre-hijacking). What can an unverified account do — nothing,
  or everything?
- **Password policy:** minimum length (12+ recommended) · **breached-password list
  check** (HIBP via k-anonymity) · enforcing a complexity rule alone doesn't stop a
  weak password (`Password1!` passes the rule and is on breach lists).
- Does **changing the password/changing the email** require the current password?
- **Session revocation:** do other sessions get dropped when the password changes?
- Does **account deletion/suspension** actually cut off access (together with KVKK/B7).
- **Enumeration on the registration endpoint:** an "this email is already registered"
  message allows deriving a user list; a rate limit and a generic message are needed.

### B2.2 — OAuth/OIDC · SESSION FIXATION · MFA · JWT ADDITIONAL VARIANTS

**Trigger:** runs if B2 is already open (T4 YES). This block runs when OAuth/OIDC/SSO,
MFA, or JWT is present.

**OAuth 2.0 / OIDC / SSO:**
- Is `redirect_uri` validated by **exact match** (not prefix/substring) → if loose,
  **token theft** (via an open-redirect chain).
- Is the `state` parameter present and validated (CSRF) · is **PKCE** present (public
  client) · is the **implicit flow** used (token leaks in the URL).
- `id_token` validation: `aud` · `iss` · `nonce` · `exp` · signature. If missing, a
  forged token is accepted.
- **Account linking**: does linking accounts via email require a verified email (pre-hijack).
- If **SAML** is present: signature wrapping (XSW), unsigned assertion, `SAMLResponse` replay.

**Session fixation (CWE-384):** is the session id **rotated** on login? (B2 covers
revocation; measure **rotation** separately — if the pre-login id is still valid after
login, that's a finding.)

**MFA/2FA:** step-skipping (going straight to the protected endpoint, bypassing MFA) ·
TOTP replay · backup-code brute force (rate limiting) · "remember this device"
persistence/entropy · MFA enrollment race.

**JWT additional (in addition to B2's alg=none/confusion):** `kid` header injection
(path traversal/SQLi via `kid`) · a forged key URL via `jku`/`x5u` (**SSRF**) ·
embedded `jwk` header · weak HMAC secret (brute-force) · `crit` bypass.

**PoC/mutant:** for each, in the user's own instance: fixation → compare the cookie
before/after login; MFA bypass → call the protected endpoint with `curl`, skipping the
MFA step; redirect_uri → start the flow with a URI outside the allowlist. Mutant:
remove the `state` check / redirect_uri exact-match (in a copy), does the scan bite.

---

## B3 — Authorization (AuthZ)

- **IDOR/BOLA:** `/api/record/123` — is record ownership checked, or is merely being
  logged in enough? **This is the most common and most expensive server flaw.**
- **Function-level control:** are admin endpoints hidden only in the UI?
- **Mass assignment:** `Object.assign(user, req.body)` → `role:"admin"`.
- **Tenant isolation → B3.1.**

### B3.1 — MULTI-TENANT / MULTI-USER ISOLATION

**A single missing `WHERE` ends all isolation.** That's why "we remember to write it
on every query" is not a defense; look for mechanical enforcement.

- **Where is it enforced?** (a) written by hand on every query → **fragile**, measure
  with a count: how many queries exist, how many have the tenant condition · (b) ORM
  global scope / middleware · (c) database-level RLS → **the strongest.**
- **Leak paths:** raw SQL (`raw`, `$queryRaw`) · batch/report queries · admin
  endpoints · background jobs (cron, queue — no request context, where does the tenant
  come from?) · exports · the search index (Elastic/Meili is a separate system — is
  the filter there too?) · does the cache key include the tenant (otherwise
  cross-tenant leakage).
- **Where does the tenant id come from?** If it comes from the request body/header,
  the attacker changes it. It must be derived **from the session/token.**
- **Files/storage:** is the path partitioned by tenant; does the signed URL validate the tenant?
- **Aggregate/statistics endpoints:** do "how many records" counts leak another
  tenant's data?
- **PoC:** with tenant A's session, request tenant B's resource id — if it returns
  200, that's a finding; whether it returns 404 or 403 is a separate leak too
  (existence confirmation).
- **File access containing a direct object reference** (unsigned S3/URL).

## B4 — Input/output and browser-class issues

- **XSS:** reflected / stored / DOM-based. Does the template engine escape by
  default; individually justify every use of `|safe`, `dangerouslySetInnerHTML`, `v-html`.
- **CSP:** is it present; does it include `unsafe-inline`/`unsafe-eval`; is
  `default-src` narrow?
- **CSRF:** are state-changing requests protected by a token or `SameSite`; is there
  an endpoint that changes state via `GET`?
- **Open redirect:** `redirect(req.query.next)` — is there an allowlist?
- **SSRF:** does the server make requests to a user-supplied URL; is the internal
  network/cloud metadata address (`169.254.169.254`) blocked; is redirect-following limited?
- **File upload:** is the type validated **from content** (not the extension), size
  limit, renaming, saving outside the web root, blocking executable extensions, zip
  bomb / zip slip.
- **CORS — LOCK IT DOWN:** details in B4.1. Short version: a fixed allowlist, no reflection.

### B4.2 — WEBHOOK SIGNATURE (inbound webhook endpoints)

A webhook endpoint is **a publicly reachable write endpoint with no authentication.**
An attacker can send a "payment succeeded" or "subscription upgraded" event themselves.

- **Is the signature validated?** (Stripe `Stripe-Signature`, GitHub
  `X-Hub-Signature-256`, generic HMAC-SHA256). If not validated → **CRITICAL.**
- **Is it validated against the RAW body?** If the body is parsed to JSON and then
  re-serialized, the signature won't match or gets bypassed — raw bytes are required.
- Is a **constant-time comparison** used (`timingSafeEqual`, not `===`)?
- **Replay window:** is the timestamp checked (e.g. ±5 min), is the event id recorded
  **idempotently** against reprocessing?
- **Source IP/secret path** alone doesn't count as a defense; a signature is mandatory.
- For outbound webhooks: if the destination URL is user-controlled, that's **SSRF** (B4).

### B4.1 — CORS LOCK

When CORS is misconfigured, **any user in a browser, on behalf of the attacker's
page,** can make an authenticated request to your API. The lock has five items:

1. **Fixed allowlist.** The permitted origins are FIXED in code/configuration.
   `Access-Control-Allow-Origin` is **not reflected** from the incoming `Origin`
   header. If it is reflected (`res.header('ACAO', req.headers.origin)`), that means
   **there is no CORS** at all.
2. **`*` + `credentials: true` FORBIDDEN.** The browser rejects it, but reflection
   bypasses that; seeing the two together is a CRITICAL candidate on its own.
3. **The match must be EXACT.** Checking with `startsWith`/`endsWith`/`includes` gets
   BYPASSED: `https://site.com.attacker.tr` passes an `endsWith` test ·
   `https://attackersite.com` passes an `includes("site.com")` test.
   Use exact equality or parsed-origin comparison.
4. **`null` origin is rejected.** A sandboxed iframe, `data:`, and some redirects send
   `Origin: null`; `null` must NOT be on the allowlist.
5. **`Vary: Origin` is mandatory.** Without it, a CDN/intermediate cache can serve the
   response granted for one origin to a different origin — cache poisoning.

**Also:** are `Allow-Methods`/`Allow-Headers` narrow (not `*`) · is `Max-Age`
reasonable · is authentication not applied to preflight (OPTIONS) (if it is, preflight breaks).

**PoC:** `curl -i -H "Origin: https://attacker.example" <endpoint>` → if
`Access-Control-Allow-Origin: https://attacker.example` appears in the response, there
is reflection. Also try with `Origin: null` and `https://<allowed>.attacker.example`.

---

## B5 — Transport and configuration

- Is TLS mandatory (HTTP → HTTPS redirect), is HSTS present?
- Security headers: `X-Content-Type-Options`, `Referrer-Policy`,
  `X-Frame-Options`/`frame-ancestors`, `Permissions-Policy`.
- **Error detail → see B5.1 (channel separation).**
- **Is the application→DB connection encrypted, and is the server certificate
  validated?** Cleartext DB traffic or an unvalidated certificate = identity/data leak
  via MITM.
  - MSSQL: `Encrypt=true` **and** `TrustServerCertificate=false` (true → a forged
    certificate is accepted).
  - MySQL: `--ssl-mode=VERIFY_IDENTITY` (`REQUIRED` alone doesn't validate the certificate).
  - Postgres: `sslmode=verify-full`.
  **Signature:** encryption disabled in the connection string, or certificate
  validation skipped.
  **Severity:** HIGH if DB traffic crosses an untrusted network; LOW if it's the same
  host/a secure segment.

### B5.1 — ERROR MESSAGE CHANNEL SEPARATION

One rule: **detail goes to the log, a generic statement goes to the user.** The same
error produces two different texts.

| Information | User screen | Server log |
|---|---|---|
| Stack trace, file name, line number | **NEVER** | yes |
| Table/column name, SQL text, ORM error | **NEVER** | yes |
| Internal endpoint path, queue name, service name, IP/port | **NEVER** | yes |
| Library/framework version, stack name | **NEVER** | yes |
| Raw error from a third-party provider | **NEVER** | yes |
| A validation error the user can fix ("date cannot be in the past") | yes | yes |
| **Correlation id** (e.g. `error-code: 7f3a91`) | **yes — this is required** | yes |

**Correct pattern:** to the user, *"The operation could not be completed. Support
code: 7f3a91"*; to the log, the full detail + the same code. The user relays the code,
you find it in the log — no leak, and it's still supportable.

**Why it matters:** error text is a **reconnaissance tool.** A SQL error gives away
the schema name, a stack trace gives away the file structure and version, and the
difference between "user not found" and "wrong password" gives away a user list. An
attacker maps the system from here first.

**How to measure (don't read, TRIGGER):** deliberately produce an error with the
production configuration — malformed JSON body · a nonexistent resource id · a type
mismatch · an overly long field · a database-constraint violation (duplicate unique
field). Inspect the **entire returned body**; check whether the JSON contains `stack`,
`detail`, `hint`, `where`, `constraint`, `query` fields. Framework defaults leak this:
the Express error middleware, FastAPI `debug=True`, Django `DEBUG=True`, the Next.js
dev overlay, PostgREST/Supabase `details`/`hint` fields.

**Also:** does the error page return a version/framework header (`X-Powered-By`,
`Server`) · does the 404-vs-403 distinction leak resource existence · **is no
PII/token falling into the log** (together with B7).
- Are debug/development endpoints open (`/debug`, `/__profile`, GraphQL
  introspection, Swagger in production, directory listing)?
- Default admin panels, exposed `.git/`, `.env`, backup files.

## B6 — Secrets management

- Keys/passwords hardcoded in code (same commands as T6, extended to server files).
- Is `.env` in the repo; does `.env.example` contain real values?
- Are CI/CD secrets written to the log (`set -x`, echo).
- Is there a secret-rotation path; is it documented what to do if one leaks?

### B6.1 — Is the secret used in the RIGHT LAYER?

Being in `.env` is not enough; **where it's read from** is what gets audited. Full
table: `references/kod-inceleme-guvenlik.md` §3. Red flags:
- A server key ends up in the client bundle (a **secret** key carrying a
  `NEXT_PUBLIC_`/`VITE_`/`REACT_APP_` prefix; a key pattern inside a compiled bundle or APK).
- A fully privileged key of the `service_role` / admin SDK / `sk_live` class is called
  from the browser.
- A secret falls into a log, a URL query string, or `localStorage`.
- `.env.example` / fixture / seed / README carries a real value.

**Scan the entire git history** (`git log -p -S "<pattern>" --all`). A secret removed
from HEAD is still in history and **remains valid until revoked** — the fix is
"ROTATE the key"; "delete it from the file" is NOT ENOUGH.

## B7 — Data and privacy

- PII inventory: which field, where, and for how long is it retained?
- Is encryption at rest required; where are the backups, who has access?
- **Log leakage:** do tokens, passwords, card data, or PII fall into the log? (The
  most commonly missed item.)
- Does a deletion request actually delete (KVKK/GDPR).
- Data going to third-party SDKs.

## B8 — Resource consumption / denial of service

- A query with no pagination limit; no `LIMIT`.
- N+1 queries; an unindexed filter.
- **ReDoS:** a backtracking (catastrophic backtracking) regex applied to user data —
  `(a+)+`, nested quantifiers.
- Request-body size limit; JSON depth limit; compression bomb.
- Is an expensive job (report, export) queued, or is it synchronous?

---

## B10 — SERVER-SIDE VALIDATION (client-side validation is NOT validation)

Every check in the UI is a **convenience**, not a defense. An attacker never uses the
UI at all: they go straight to the endpoint with `curl`.

**Principle:** EVERY validation done on the client is **repeated identically** on the
server. This is not a preference — it is an architectural rule.

Audit:
- **Is there schema validation?** (zod, yup, joi, pydantic, JSON Schema,
  DTO+validator) If not, `req.body` is being used directly → converges with B3 mass
  assignment.
- **Allowlist or denylist?** Is an unknown field **dropped** (`strict`/`.strip()`), or
  does it pass through?
- **Type coercion:** `"5"` vs. `5`, `"true"` vs. `true`, an object where an array is expected.
- **Range and sign:** is a negative amount/quantity/price accepted? Is there an upper bound?
- **Enum/state transitions:** can the client send `status: "approved"`; can a workflow
  step be skipped (order → skip payment → shipping)?
- Are **fields the server should determine** coming from the client: `price`, `total`,
  `discount`, `role`, `user_id`, `created_at`, `verified`.
  **Taking the price from the client** is the classic, fatal one.
- **File/media:** is size and MIME validated server-side (from content, not the extension)?
- **Business rule:** coupon stacking, claiming the same reward twice, quota overrun —
  is it enforced atomically on the server (for race conditions, see
  `kod-inceleme-guvenlik.md` §1.3)?

**PoC method:** skip the UI, call the endpoint directly. Send the value the UI blocks
via `curl`/a request; if it's accepted, that's a **finding** — write the request and
response as the PoC.

---

## B11 — BUSINESS LOGIC ABUSE

This is robbing the system with technically "valid" requests. Scanners don't find
this; only **reading the business rules and trying to abuse them** finds it. B10
validates input; here **the rule itself** is broken.

- **Sign and zero:** negative quantity/count/amount · zero price · negative discount
  (charging instead of refunding) · `Infinity`/`NaN` · overflow from an oversized number.
- **Repetition and stacking:** the same coupon twice · multiple coupons stacked ·
  claiming the welcome bonus again with a second account · a referral-reward loop (A
  refers B, B refers A).
- **Double-spend via race condition:** using the same balance/quota with two
  concurrent requests. **Test:** send the same request 10 times in parallel; is the
  result singular? (Mechanical detail: `kod-inceleme-guvenlik.md` §1.3.)
- **Workflow-step skipping:** sending a request directly to the final step's endpoint
  (cart → **skip payment** → shipping). Is the state machine enforced on the server,
  or is it just the UI's ordering?
- **Undo/cancel abuse:** claim the reward → cancel the transaction → does the reward stay?
- **Time manipulation:** is the campaign window, daily limit, or streak computed from
  a client-supplied date/time? The server clock must be authoritative.
- **Identity multiplication:** the same person having many accounts via an email `+`
  tag, a dot variant, or a disposable email; is the quota/reward being multiplied this way?
- **Does the price/total come from the client?** (Same class as B10, and the most costly one.)

**Severity:** **HIGH** if there's direct monetary loss or consumption of someone
else's quota; MEDIUM if it only breaks the attacker's own account.

---

## B12 — WEBSOCKET / REAL-TIME CHANNELS

Most HTTP protections **do not automatically apply** to WebSocket.

- **Origin check:** **CORS does not apply** to the WebSocket handshake, and the
  `SameSite` cookie is sent by most browsers anyway → **cross-site WebSocket
  hijacking.** Does the server validate the `Origin` header against an allowlist? If
  not, any site can open a socket using the user's session. **CRITICAL candidate.**
- **Identity:** is it authenticated at connection time; is the token carried **in the
  URL** (falls into logs) or in the first message/header?
- **Is authorization checked on every message?** Checking once at connection open and
  then accepting every subsequent message is a common mistake — ownership of the
  subscribed channel/room must be validated on every message.
- **Is the channel name guessable** (`room-123`)? Does a broadcast go to the wrong subscriber?
- **Message schema:** is the inbound message validated (B10 applies identically); is
  there a size and rate limit (messages/second per connection)?
- **Resources:** connection-count limit, whether unauthenticated connections are
  allowed, dead-connection cleanup.
- **Session termination:** when the user logs out/loses authorization, does the open
  socket get closed?

---

## B13 — GraphQL

- Is **introspection** enabled in production? It's not a flaw by itself, but it gives
  the attacker a complete schema map → it's expected to be disabled.
- **Depth and complexity limits:** exhausting the database in a single request with a
  nested relation query (`a{b{a{b...}}}`) → **DoS.** Is there a depth limit, a
  complexity score, and a timeout?
- **Query batching abuse:** **bypassing rate limits** with hundreds of mutations in a
  single HTTP request (password attempts). Is the rate limit per request, or **per
  operation**?
- **Field-level authorization:** REST has per-endpoint controls; in GraphQL, a field
  (`user { email }`) can be left open by mistake. Is authorization enforced **at the
  resolver level**?
- **Alias duplication:** requesting the same field hundreds of times under different aliases.
- **Error messages:** GraphQL returns detailed errors by default → B5.1.
- If **persisted queries** are used, is arbitrary querying disabled?

---

## B14 — MISHANDLING EXCEPTIONAL CONDITIONS / FAIL-OPEN (OWASP A10:2025)

What do identity, authorization, the WAF, the rate limiter, and payment validation do
under **error/timeout/resource exhaustion**: do they **open (fail-open) or close
(fail-closed)?**

**Signature to look for:** `try/catch` · timeout · circuit-breaker · **the default
being "allow / proceed"** in dependency-failure branches. The flow continuing into the
protected operation after `catch { /* log it */ }`. Saying "let it through" when the
authorization service doesn't respond.

**PoC/mutant:** deliberately take down the protected path's dependency (the
auth/authorization service, the rate-limiter's store) (in a copy/locally); **is the
request accepted** (fail-open = finding), or rejected? Mutant: convert the fail-closed
branch to fail-open, does the scan bite.

**Severity:** HIGH/CRITICAL if what's protected is authorization/identity/payment.

---

## B15 — SECURITY LOGGING & ALERTING FAILURES (OWASP A09:2025)

B7 measures that the log **doesn't leak**; this section measures the **opposite**: are
security events **logged and wired to alerts?**

**Signature to look for:** failed login · authorization denial (403/RLS denial) ·
input-validation error · a high-value operation (money, role change, deletion) · MFA
events — do these paths have an **audit-log call**, is the log structured/searchable,
is there an **alert/threshold** on a critical event.

**PoC/mutant:** trigger the authorization-denial and failed-login paths; check whether
a log entry **is created**. Mutant: remove one audit-log call (in a copy), does the
scan notice the difference.

**Severity:** generally LOW/INFO (not exploitable on its own, defense-in-depth); but
MEDIUM if there is **no** detection at all and the system holds money/PII. (gedik is
attacker-focused; this item counts "undetectability" itself as a gap — no inflation.)

---

## B16 — HTTP REQUEST SMUGGLING (front-end/back-end mismatch)

**Trigger:** T11 YES (reverse proxy/CDN + back-end). Static detection is weak;
architecture + testing in **the user's own local stack** is required.

**Signature to look for:** a difference in how the front-end and back-end process
`Content-Length`/`Transfer-Encoding`; CL.TE / TE.CL / TE.TE / CL.CL; **HTTP/2
downgrade** (H2.CL/H2.TE). Does the front-end forward without normalizing; are
duplicate/inconsistent headers rejected.

**PoC/mutant (in the user's own local front-end+back-end pair):** send a harmlessly
marked request carrying both CL and TE; does the back-end interpret the second request
**as the body of the previous request** (desync)? Impact: front-end authorization
bypass, poisoning another user's request, cache poisoning (B18). **Severity: CRITICAL**
(if desync is confirmed).

---

## B17 — HOST HEADER INJECTION

**Signature to look for:** is `Host`/`X-Forwarded-Host` used **without being
trusted** — absolute-URL generation (**password-reset link**), redirect, cache key,
email link. Is there an allowlist/`ALLOWED_HOSTS`.

**PoC/mutant:** send the password-reset request with the attacker's `Host`; if the
generated link reflects the attacker's host → **an account-takeover chain**. Mutant:
remove the host allowlist (in a copy). **Severity: HIGH/CRITICAL.**

---

## B18 — WEB CACHE POISONING & CACHE DECEPTION

B9.3 covers "accidental sharing"; this is **attacker-controlled** poisoning.

**Signature to look for: poisoning** — an unkeyed header/parameter is reflected into
the response and written to cache (input that isn't in the cache key affects the
output). **deception** — a personalized response gets cached via an extension/path
trick like `/account/profile.css`. What are the cache key's components; is `Vary` correct.

**PoC/mutant:** put a harmless marker in an unkeyed header; if the **second request
(without the header)** returns the marker, the cache was poisoned. Deception: does a
static-looking path cache a personalized response. **Severity: HIGH.**

---

## B19 — SUBDOMAIN TAKEOVER / DANGLING DNS

**Signature to look for:** a CNAME points at a service that's no longer in use
(S3/GitHub Pages/Heroku/Vercel/Azure); if the target is in a
"NoSuchBucket/404/unclaimed" state → an attacker claims it. Cookie/OAuth/CSP trust
gets stolen.

**PoC/mutant (on the user's own domains):** enumerate subdomains, check the CNAME
targets and the target service's status; a dangling one is a finding. **Severity:
HIGH** (CRITICAL if the cookie/trust scope is broad).

---

## B20 — APPLICATION DB-ACCOUNT PRIVILEGE SCOPE (least privilege)

**Why:** how destructive a SQLi (and general DB access) turns out to be is determined
by **what privilege the application connects to the DB with.** If the app connects as
`sa`/`sysadmin`/`root`/`db_owner`/`SUPERUSER`, one injection = the entire server. This
is the classic-SQL counterpart of C3 (anon vs. service_role).

**Signature to look for:**
- The role of the DB user in the connection string: MSSQL
  `sysadmin`/`db_owner`/`CONTROL SERVER`; MySQL `root`/`ALL PRIVILEGES`/`FILE`/`GRANT
  OPTION`; Postgres `SUPERUSER`/`CREATEROLE`.
- Does the app run under a single high-privilege account, or is there a read/write
  split + table/schema-specific GRANTs.
- Dangerous privileges are excessive on the app account if unneeded: `FILE` (MySQL),
  `xp_cmdshell` EXECUTE (MSSQL), extended/`SECURITY DEFINER` proc EXECUTE, DDL
  (`DROP`/`ALTER`).

**Severity:** a high-privilege account + a reachable injection/sink path →
**CRITICAL**; excess privilege alone with no exploit path → LOW (hardening).

**PoC/mutant (in the user's own test instance):** query the effective privileges of
the account the app connects as — MSSQL `SELECT IS_SRVROLEMEMBER('sysadmin')`; MySQL
`SHOW GRANTS FOR CURRENT_USER()`; Postgres `rolsuper`/`\du`. High privilege + a
reachable sink = proof of blast radius (a row count/code is enough, no data
exfiltration). **Mutant:** pull the account back to least privilege (in a copy) → does
the escalation close; does the scan notice the difference.

---

## B9 — Rate limiting, cost, and caching

The rate limit in B2 only covers login/OTP endpoints. **This section is for the entire API.**

### B9.1 — Rate limiting
- **Does it exist, and WHERE?** In application code / the reverse proxy (nginx,
  Cloudflare) / the API gateway? If it's only in the UI (client-side debounce),
  **there is NO rate limit.**
- **Keyed on what?** If it's IP-only, everyone behind the same NAT shares a bucket,
  and an attacker bypasses it by rotating IPs. On authenticated endpoints it should be
  keyed by user/API key.
- **Is the counter atomic?** Read-increment-write races let the limit be bypassed
  (see `kod-inceleme-guvenlik.md` §1.3). A Redis `INCR` / token bucket is required.
- **Are expensive endpoints in a separate bucket?** If search, reports, exports, file
  processing, and LLM/third-party calls share the general limit's bucket, one user can
  exhaust the service.
- **Is the response correct?** `429` + `Retry-After`; not silently returning empty on
  limit overflow.
- **Lockout DoS:** does the failed-login lockout let an attacker lock out the VICTIM?

### B9.2 — Cost control (paid/third-party services)
For every endpoint that calls an LLM, SMS, email, maps, or storage service:
- Is there a per-request upper bound (tokens/characters/size)?
- Is there a per-user daily/monthly quota; what happens on overrun?
- Is a budget alert set up in the provider's dashboard?
- **Can an unauthenticated user trigger a paid call → a direct billing DoS.**

> It's not on the classic OWASP lists, but it produces real damage: the attacker
> doesn't steal data, **they inflate the bill.** Severity is generally MEDIUM; HIGH if
> automatic payment is enabled.

### B9.3 — Caching
The security angle is **accidental sharing:**
- Does a personalized response fall into a shared cache? If `Cache-Control:
  private`/`no-store` is missing, the CDN serves one user's data to another.
- Is `Vary` correct (`Origin, Authorization, Accept-Encoding`) — if missing, cache poisoning.
- Does the cache key include the user for authenticated content?
- The performance side (TTL, invalidation, caching an expensive response) is written
  up as a **recommendation**, not a security finding.

---

## LANE B quick closing checklist

1. Was every dynamic query reviewed individually (the ORM was not assumed "safe")?
2. Was the **ownership** check verified for every resource endpoint (IDOR)?
3. Were the password/token storage algorithm and its parameters reviewed?
4. Are error detail and debug endpoints disabled in the production configuration?
5. Was `.env`/secrets searched for across the entire git history?
6. Is the CORS allowlist FIXED (no reflection), is `Vary: Origin` present?
7. Was the rate limit and quota measured ON THE SERVER for every expensive/paid endpoint?
8. Is the secret used in the **right layer**, not just in `.env` (not leaking to the client)?
9. Does an ORM query still produce a `WHERE` when called without parameters (no open filter)?
10. Was a dependency CVE scan run (with a count)?
11. Was an error deliberately triggered against the production configuration; does the
    returned body lack `stack`/`detail`/`hint`/`query` fields (B5.1)?
12. Is a value the client blocks accepted via `curl` (B10)?
13. Is the signature on inbound webhook endpoints validated against the RAW body and
    with a constant-time comparison (B4.2)?
14. In how many queries is the tenant condition present, and in how many is it
    missing — was this measured with a count (B3.1)?
15. When the same request is sent 10 times in parallel, is the result singular (B11 race)?
16. Is `Origin` validated against an allowlist during the WebSocket handshake (B12)?
17. If GraphQL is present, is there a depth/complexity limit and a per-operation rate limit (B13)?
18. Was the SQLi variant matrix scanned — especially **second-order** and **ORDER
    BY/column allowlist** (B1.2)?
19. If an OAuth/OIDC flow exists, were `redirect_uri`/`state`/PKCE, session fixation,
    and MFA measured (B2.2)?
20. When a dependency is taken down on critical paths, does the system **fail-open** (B14)?
21. Do authorization-denial/failed-login paths fall into the **audit log** (B15)?
22. Was the NoSQL/command/SSTI/XXE/deserialization variant deepening and
    Log4Shell/JNDI scanned (B1.3)?
23. If T11 is YES (reverse proxy/CDN): were request smuggling (B16), host header
    injection (B17), and cache poisoning/deception (B18) measured?
24. Was the subdomain/DNS inventory scanned for dangling CNAMEs (B19)?
25. **Was the B20 app DB-account privilege measured; are SQLi escalation sinks
    reachable (B1.2)?**
26. Did a self-mutant run in at least two areas, and did it bite?
