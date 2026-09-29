# Triage and Scope — command patterns

Purpose: to **measure the architecture** before scanning begins. Every command in this file
answers a T-question. Write the answers into the report verbatim (command + output summary).

---

## T1 — Is there a network?

**Web/JS side**
```
rg -n "fetch\(|XMLHttpRequest|new WebSocket|sendBeacon|EventSource|navigator\.connection" <kaynak>
rg -n "https?://" <kaynak> | rg -v "w3\.org|schema\.org"     # SVG/XML ad alanları hariç
rg -n "import\s*\(" <kaynak>                                  # dinamik import uzak URL olabilir
```
**Android artifact (authority: aapt, not the string pool)**
```
aapt dump permissions <apk>
aapt dump badging <apk>
```
If the `INTERNET` permission is ABSENT and the web side has 0 network APIs → T1 = NO. This alone
closes off **the entire server-side class** (SQLi, SSRF, CSRF, session hijacking, TLS).

> Note: even without the `INTERNET` permission, `data:`/`blob:`/`file:`/`content:` schemes and
> opening external apps (`intent:`, `market:`, browser) are still attack surface — handled in Lane A.

---

## T2 — Is there server code?
```
fd -t d "^(api|server|routes|handlers|controllers|functions)$"
rg -n "express\(|fastify\(|Flask\(|FastAPI\(|createServer|app\.(get|post|put|delete)\("
fd "serverless\.(yml|yaml)|Dockerfile|docker-compose\.(yml|yaml)|Procfile"
```

## T3 — Is there a database?
```
rg -n -i "SELECT .* FROM|INSERT INTO|UPDATE .* SET|DELETE FROM"
rg -n "prisma|sequelize|typeorm|knex|mongoose|sqlalchemy|psycopg|mysql2|better-sqlite3"
fd -e sql
rg -n -i "(postgres|mysql|mongodb|redis)://"
```

## T4 — Is there an account/identity system?
```
rg -n -i "password|passwd|bcrypt|argon2|scrypt|pbkdf2|jsonwebtoken|jwt\.|session|passport|oauth"
rg -n "type=[\"']password[\"']"
```

## T5 — Untrusted input paths (THE MOST CRITICAL OUTPUT)

This is not a search, it is an **inventory**. Ask this question for every input: *can this
value be determined by the outside world (a user, another app, a file, the network)?*

Sources to search:
```
rg -n "\.value|FormData|addEventListener\(['\"](paste|drop|message)|clipboard"
rg -n "JSON\.parse|parseFloat|parseInt|decodeURI|atob|TextDecoder"
rg -n "location\.(search|hash|href)|URLSearchParams|getIntent|getData\(\)"
rg -n "<input|<textarea|type=[\"']file[\"']"
rg -n "postMessage|onmessage|BroadcastChannel"
```
On the Android side, additionally:
```
rg -n "intent-filter" AndroidManifest.xml -A6
rg -n "exported=" AndroidManifest.xml
```

Output format (verbatim into the report):

| # | Input path | Source | Who controls it | Sanitized? |
|---|---|---|---|---|
| G-1 | ... | file:line | user / another app / network | yes+where / no |

**Rule:** if the inventory comes out with 0 input paths, the inventory is WRONG — every
application has at least one input. Search again.

## T6 — Secrets and signing material

**Working tree**
```
fd -H -e jks -e keystore -e p12 -e pfx -e pem -e key -e env
rg -n -i "(api[_-]?key|secret|token|password|passwd|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY)" \
   -g '!node_modules' -g '!*.lock'
```
**The ENTIRE git history (persists even if deleted)**
```
git log --all --diff-filter=A --name-only --pretty=format: | sort -u \
  | rg -i "\.(jks|keystore|p12|pfx|pem|key)$|(^|/)\.env"
git rev-list --objects --all | rg -i "\.(jks|keystore|p12|pfx)$"
```
**`.gitignore` coverage**
```
rg -n "keystore|jks|key\.properties|signing|\.env|\.apk|\.aab" .gitignore
```

**Interpretation rule:** a pattern match ≠ a secret. `storePassword=<user enters>` is a
placeholder, not a secret. OPEN and read every match; write into the report "N matches,
all/this many are placeholders" — do not just give the raw count.

---

## T7 — Is there BaaS / a direct-to-client database?

**How to measure:** in dependencies, `@supabase/supabase-js`, `firebase`, `firebase-admin`,
`appwrite`, `pocketbase`, `@aws-amplify/*` · in environment variables, `SUPABASE_URL`,
`FIREBASE_CONFIG`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` · in code, `createClient(`,
`initializeApp(`, `.from('<table>').select(` · in the repo, a `supabase/` folder,
`firestore.rules`, `storage.rules`, `firebase.json`.

**If YES → LANE C is mandatory** (`references/serit-C-baas-rls.md`).
In this architecture the client talks DIRECTLY to the database; there is no server to enforce
authorization, RLS/rules are the only authorization layer. Even if T2 (server code) is NO, Lane C
still opens — the inference "no server, therefore no server vulnerability" is WRONG in this
architecture.

## T8 — Is there an AI / LLM surface?

**How to measure:** in dependencies, `openai`, `@anthropic-ai/sdk`, `langchain`,
`llamaindex`, `@google/generative-ai`, `ollama`, `transformers` · in environment
variables, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` or similar · in code, `chat.completions`,
`messages.create`, `embeddings`, `vectorStore`, a `tools:`/`functions:` definition ·
prompt template files (`prompts/`, `*.prompt`, system prompt strings).

**If YES → LANE D is mandatory** (`references/serit-D-yapayzeka.md`).
An LLM call is the one place where **text written by an attacker can be read as an
instruction**; if the model has tools, that instruction turns into action. Lane D does not
replace Lane B — the LLM endpoint is also an API endpoint (identity, rate limiting, cost →
B2/B9).

**Additional measurement for T8 — vector/agent surface (opens D7/D8):** in dependencies,
`pgvector`, `@pinecone-database/pinecone`, `weaviate-client`, `chromadb`, `qdrant-client`,
`faiss` · in code, `embeddings.create`, `.similaritySearch(`, `.upsert(`, `.query(vector` ·
an MCP server connection (`mcpServers`, `@modelcontextprotocol/*`) · an agent framework
(LangChain agent, LlamaIndex agent, AutoGen, CrewAI) · persistent memory (`memory`, vector
memory, conversation history persistence). If any one of these is YES, D7 (vector/embedding)
and/or D8 (tool/MCP supply-chain trust, agent memory) additionally run **inside** the lane —
no new T is needed, since Lane D is already open because T8 is YES.

**Note — iOS detection:** Lane A **always** runs (no new T needed); if `Info.plist`,
`*.xcodeproj`/`*.xcworkspace`, a Capacitor `ios/` folder, or `.ipa` is present, Lane A's iOS
column (`serit-A-istemci.md` §A8) also runs. It is not repeated here — this is a single
cross-reference line.

---

## T11 — Is there a reverse proxy / CDN / multi-layer setup?

```
fd "nginx\.conf|haproxy\.cfg"
rg -n -i "cloudflare|fastly|akamai|cloudfront" -g '!node_modules'
rg -n -i "x-forwarded-(for|host|proto)" -g '!node_modules'
```
If both a front end (reverse proxy/CDN) **and** a back end (application server) are present,
YES. `X-Forwarded-*` handling code and HTTP/2-3 usage are also signals.

**If YES → Lane B goes deeper** (`references/serit-B-sunucu.md`): request smuggling (B16),
host header injection (B17), cache poisoning/deception (B18). Note: subdomain takeover (B19)
is triggered separately — T1 (network) + a deployment artifact (CNAME/DNS) is enough, T11 is
not required.

## T12 — Is there IaC / cloud configuration?

```
fd -e tf -e tfvars
fd "serverless\.(yml|yaml)|Dockerfile|docker-compose\.(yml|yaml)"
rg -l "kind:\s*(Deployment|Pod|StatefulSet|DaemonSet)" -g '*.yaml' -g '*.yml'
rg -n -i "cloudformation|pulumi" -g '!node_modules'
```
If `*.tf`/`*.tfvars`, a CloudFormation/Pulumi template, a k8s manifest (`kind:`), `Dockerfile`
content, or a cloud SDK dependency is present, YES.

**If YES → the container/IaC hardening section opens in the CI/CD lane**
(`references/cicd-depo-ve-kurtarma.md` §6).

## Lane decision — examples

| Project | T1 | T2 | T3 | T4 | Decision |
|---|---|---|---|---|---|
| Offline Capacitor application | No | No | No | No | Lane A only |
| Static marketing site (no form) | Yes (CDN) | No | No | No | Lane A (narrow) + supply chain |
| Next.js + Postgres + login | Yes | Yes | Yes | Yes | Lane A + Lane B (full) |
| Local desktop tool, reads files | No | No | No | No | Lane A (file/deserialization-heavy) |

For a serverless project, the report closes out Lane B **in a single line**:

> **Lane B (server/API/DB/identity): ARCHITECTURALLY ABSENT.** T1–T4 measurement: no
> INTERNET permission (aapt), 0 network APIs, no server code, no DB, no accounts. The SQL
> injection, SSRF, CSRF, session hijacking, and authorization-bypass classes are
> **structurally inapplicable** — an item-by-item N/A list was not written out.
