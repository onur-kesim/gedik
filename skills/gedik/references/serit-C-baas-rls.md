# LANE C — BaaS / Direct-Client Database (Supabase · Firebase · Appwrite · PocketBase)

**Opens only if T7 is YES.**

## Why a separate lane

In classic architecture the client → **server** → database; the server enforces authorization.
In BaaS architecture the client talks **directly to the database**. There is NO code in
between to enforce authorization.

> **One-sentence takeaway:** In BaaS, RLS/rules are **the only authorization layer.**
> If it's off, there is no authorization — it doesn't matter what the UI does or doesn't show.
> An attacker doesn't use the UI; they call the REST/SDK directly with the anon key.

**In this lane, "we don't show it in the UI" is NOT a defense**, and this justification
is not accepted as a rebuttal to a finding.

---

## C1 — RLS-DISABLED TABLE SCAN (first task, no exceptions)

Full list in Supabase/Postgres (in the user's **own** project, in the SQL editor):

```sql
select schemaname, tablename, rowsecurity
from pg_tables
where schemaname not in ('pg_catalog','information_schema')
order by rowsecurity asc, tablename;
```

**Every row** where `rowsecurity = false` **is a finding.** Severity: **CRITICAL** if the
table carries PII/user data; INFO if it's generic reference data (a province list, categories).

**Don't conflate these three states:**

| State | Meaning | Outcome |
|---|---|---|
| RLS **disabled** | Anyone with the anon key can read/write the table | **OPEN** — critical candidate |
| RLS **enabled, NO policy** | Postgres default: everything DENIED | Secure but the app breaks — functional finding |
| RLS **enabled, policy exists** | The policy itself must be audited → C2 | Never call it "clean" without measuring |

> **The most common false "clean":** seeing "RLS enabled" and moving on. If RLS is
> enabled but the policy is `USING (true)`, RLS is **doing nothing at all**. Skipping C2
> is the same as never running this lane.

---

## C2 — POLICY CORRECTNESS

```sql
select schemaname, tablename, policyname, cmd, roles, qual, with_check
from pg_policies
order by tablename, cmd;
```

Four questions for every policy:

**1. Does `USING` actually restrict ownership?**
- `USING (true)` → RLS exists but is wide open. **FINDING.**
- `USING (auth.uid() = user_id)` → the correct pattern.
- `USING (auth.role() = 'authenticated')` → **INSUFFICIENT**: ANY logged-in user sees
  everyone's data. This is the most common RLS misconfiguration.

**2. Is there a `WITH CHECK`?** (for INSERT/UPDATE)
- Without `WITH CHECK`, a user **can write a row on someone else's behalf**
  (by sending `user_id: <someone-else>`). `USING` only restricts reads/the target row,
  not the content being written. **This is the costliest and most frequently missed item.**
- UPDATE needs both `USING` and `WITH CHECK` — otherwise a user can transfer their own
  row to someone else.

**3. Are all four commands covered?** `SELECT · INSERT · UPDATE · DELETE`
- On tables where only a `FOR SELECT` policy was written, DELETE can be left wide open.
- If `FOR ALL` was used, verify that `WITH CHECK` was also supplied.

**4. Is the role scope correct?** If the `roles` column is `{public}`, the policy
also covers `anon`; for a table that should require authentication, `{authenticated}`
is expected.

**Additional traps:**
- **`SECURITY DEFINER` functions BYPASS RLS.** `select proname, prosecdef
  from pg_proc where prosecdef = true;` — justify each one individually; if it builds
  a query from user input, also apply B1 (injection).
- **Views:** before Postgres 15, a view runs with the view owner's privileges and can
  bypass RLS; is `security_invoker = true` set?
- **The `postgres`/`service_role` role is not subject to RLS** → C3.

---

## C3 — KEY SCOPE (anon vs service_role)

| Key | Where it should be | Where it must NOT be |
|---|---|---|
| `anon` / publishable | Being in the client is **normal** — RLS provides the security | — |
| `service_role` / secret | **Server only** (Edge Function, backend, CI) | Client code, bundle, mobile package, repo, `NEXT_PUBLIC_*` |

- **`service_role` completely bypasses RLS.** If it has leaked into the client, the
  entire database is exposed → **CRITICAL**, no debate.
- Search: inside the compiled bundle/APK for `service_role`, the `eyJ...` JWT pattern,
  `SUPABASE_SERVICE_ROLE_KEY`, `sk_live`, an admin SDK init call.
- **No variable prefixed `NEXT_PUBLIC_` / `VITE_` / `REACT_APP_` can be secret** — a
  secret key carrying that prefix has, by definition, already been published.
- Scan the entire git history; any key found is **rotated**, not deleted.

---

## C4 — STORAGE POLICIES

It's common for the database to be locked down while storage stays wide open.
- Is the bucket **public or private**? Every object in a public bucket is accessible
  to anyone who knows the URL.
- Is there an object-level policy; is the path partitioned by user id
  (`user_id/file.png`), and does the policy actually **enforce** that?
- Is the signed-URL lifetime reasonable; are unexpired/long-lived signed URLs being
  generated?
- Uploads: is the MIME type validated **from content**, is there a size limit, does
  the filename come from the user (path traversal)?
- If there's no upload quota, that's a **storage-cost DoS** (see B9.2).

---

## C5 — RPC / EDGE FUNCTION / SERVER FUNCTION

- Is **authentication** enforced on the Edge Function, or is it a public endpoint?
- If the function uses `service_role`: are input validation and authorization checks
  done **inside the function**? (Since RLS is disabled, this is the only protection.)
- Do RPC parameters pass schema validation; do they go straight into a query (B1)?
- Is the function subject to rate limiting (B9.1); if it calls a paid service, does it
  have a quota (B9.2)?

---

## C6 — REALTIME / SUBSCRIPTION CHANNELS

- Is the realtime broadcast subject to RLS (in Supabase it's enabled per table — is
  it enabled)?
- Does everyone who subscribes to a channel name see all changes?
- Is there authorization on presence/broadcast channels, and is the channel name
  guessable?

---

## C7 — FIREBASE / OTHER BaaS EQUIVALENTS

| Supabase | Firebase | Check |
|---|---|---|
| RLS policy | Firestore/RTDB Security Rules | `allow read, write: if true;` → **OPEN** |
| `auth.uid() = user_id` | `request.auth.uid == resource.data.uid` | is ownership enforced |
| `WITH CHECK` | `allow create/update: if request.resource.data...` | is written content validated |
| `service_role` | Admin SDK | must NOT be in the client |
| Storage policy | Storage Rules | bucket rules are written separately, get forgotten |

Firebase-specific: has it been tested with the **Rules Simulator**; `if request.auth
!= null` alone is insufficient (any logged-in user ≠ the owner).

---

## C8 — PoC: HOW TO PROVE IT (K2 mandatory)

Measurement is done not through the UI but **directly against the API** — in the
user's **own** project:

1. With the anon key, try to fetch a row **known to belong to another user**:
   `curl "<project>/rest/v1/<table>?select=*" -H "apikey: <anon>"`
   → if a row is returned, **RLS is missing/ineffective**. Record the number of rows
   returned in the report.
2. Using authenticated user A's session, try to read/update user B's row (the BaaS
   equivalent of BOLA).
3. Try an INSERT sending the `user_id` field with **someone else's identity** → if
   it succeeds, `WITH CHECK` is missing.
4. In storage: call the URL of an object that should be private, without a signature.

**Harmlessness rule:** actual other users' data is never exfiltrated for proof; the
row count, the returned field names, and the HTTP code are sufficient. Do not paste
the data into the report.

---

## C9 — SUPABASE/POSTGREST DEEP DIVE

RLS restricts table rows; the items below go **around RLS** entirely.

| # | Weakness | Signature to look for | Severity |
|---|---|---|---|
| C9.1 | **Exposed VIEW/function** | PostgREST automatically turns every VIEW and function in the `public` schema into an **endpoint**; RLS may not apply to the view (pre-PG15) | HIGH |
| C9.2 | **Column-level GRANT** | RLS restricts rows, but `GRANT SELECT(column)` is separate; has too broad a column (password hash, email) been granted to `anon`/`authenticated` | HIGH |
| C9.3 | **SSRF from the DB (`pg_net`/`http`)** | The `pg_net`/`http` extension is enabled + a function builds a URL from user data → the DB makes a request into the internal network | CRITICAL |
| C9.4 | **EXECUTE granted to `anon`** | Functions have `EXECUTE` granted to the `anon` role; the RPC can be called unauthenticated | VARIABLE |
| C9.5 | **Over-exposed `public` schema** | The schema exposed to PostgREST hasn't been narrowed; internal tables are visible via REST | MEDIUM/HIGH |

**PoC/mutant (in your own project, directly against REST):** `curl "<project>/rest/v1/<view>?select=*" -H "apikey: <anon>"` → the **row count** and field names returned (not the content). For `pg_net`: call the function with your own harmless URL, observe that the DB makes an outbound request. Mutant: widen a column GRANT / remove `security_invoker` from a view (on a copy) — does the scan catch it?

---

## Lane C quick close-out checklist

1. Did the `pg_tables` scan run; is the count of tables with `rowsecurity=false` in the report?
2. Was every policy audited for `USING` **and** (if it writes) `WITH CHECK`?
3. Is there a false-restriction policy of the `auth.role() = 'authenticated'` kind?
4. Are all four commands (SELECT/INSERT/UPDATE/DELETE) covered?
5. Were `SECURITY DEFINER` functions justified one by one?
6. Was the client bundle searched for `service_role` and its **absence** proven?
7. Were storage buckets and their rules audited separately?
8. Was at least one PoC run directly against the API (not through the UI)?
9. Were exposed VIEWs/functions and column-level GRANTs audited (C9.1/C9.2)?
10. Was SSRF from the DB via the `pg_net`/`http` extension measured (C9.3)?
