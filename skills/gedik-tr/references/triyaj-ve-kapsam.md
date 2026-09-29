# Triyaj ve Kapsam — komut kalıpları

Amaç: taramaya başlamadan önce **mimariyi ölçmek**. Bu dosyadaki her komut bir
T-sorusunu cevaplar. Cevapları rapora aynen (komut + çıktı özeti) yaz.

---

## T1 — Ağ var mı?

**Web/JS tarafı**
```
rg -n "fetch\(|XMLHttpRequest|new WebSocket|sendBeacon|EventSource|navigator\.connection" <kaynak>
rg -n "https?://" <kaynak> | rg -v "w3\.org|schema\.org"     # SVG/XML ad alanları hariç
rg -n "import\s*\(" <kaynak>                                  # dinamik import uzak URL olabilir
```
**Android artefaktı (otorite: aapt, string-pool değil)**
```
aapt dump permissions <apk>
aapt dump badging <apk>
```
`INTERNET` izni YOKSA ve web tarafında ağ API'si 0 ise → T1 = HAYIR. Bu tek başına
**sunucu tarafı tüm sınıfı** (SQLi, SSRF, CSRF, oturum kaçırma, TLS) kapatır.

> Not: `INTERNET` izni yoksa bile `data:`/`blob:`/`file:`/`content:` şemaları ve harici
> uygulama açma (`intent:`, `market:`, tarayıcı) hâlâ yüzeydir — Şerit A'da işlenir.

---

## T2 — Sunucu kodu var mı?
```
fd -t d "^(api|server|routes|handlers|controllers|functions)$"
rg -n "express\(|fastify\(|Flask\(|FastAPI\(|createServer|app\.(get|post|put|delete)\("
fd "serverless\.(yml|yaml)|Dockerfile|docker-compose\.(yml|yaml)|Procfile"
```

## T3 — Veritabanı var mı?
```
rg -n -i "SELECT .* FROM|INSERT INTO|UPDATE .* SET|DELETE FROM"
rg -n "prisma|sequelize|typeorm|knex|mongoose|sqlalchemy|psycopg|mysql2|better-sqlite3"
fd -e sql
rg -n -i "(postgres|mysql|mongodb|redis)://"
```

## T4 — Hesap/kimlik var mı?
```
rg -n -i "password|passwd|bcrypt|argon2|scrypt|pbkdf2|jsonwebtoken|jwt\.|session|passport|oauth"
rg -n "type=[\"']password[\"']"
```

## T5 — Güvenilmeyen girdi yolları (EN KRİTİK ÇIKTI)

Bu bir arama değil, bir **envanterdir**. Şu soruyu her giriş için sor: *bu değeri
dış dünya (kullanıcı, başka uygulama, dosya, ağ) belirleyebiliyor mu?*

Aranacak kaynaklar:
```
rg -n "\.value|FormData|addEventListener\(['\"](paste|drop|message)|clipboard"
rg -n "JSON\.parse|parseFloat|parseInt|decodeURI|atob|TextDecoder"
rg -n "location\.(search|hash|href)|URLSearchParams|getIntent|getData\(\)"
rg -n "<input|<textarea|type=[\"']file[\"']"
rg -n "postMessage|onmessage|BroadcastChannel"
```
Android tarafında ayrıca:
```
rg -n "intent-filter" AndroidManifest.xml -A6
rg -n "exported=" AndroidManifest.xml
```

Çıktı formatı (rapora aynen):

| # | Giriş yolu | Kaynak | Kim kontrol ediyor | Sanitize var mı |
|---|---|---|---|---|
| G-1 | ... | dosya:satır | kullanıcı / başka uygulama / ağ | evet+nerede / hayır |

**Kural:** envanterde 0 giriş yolu çıkıyorsa envanter YANLIŞTIR — her uygulamanın en
az bir girdisi vardır. Tekrar ara.

## T6 — Sır ve imza malzemesi

**Çalışma ağacı**
```
fd -H -e jks -e keystore -e p12 -e pfx -e pem -e key -e env
rg -n -i "(api[_-]?key|secret|token|password|passwd|private[_-]?key|BEGIN [A-Z ]*PRIVATE KEY)" \
   -g '!node_modules' -g '!*.lock'
```
**Git geçmişinin TAMAMI (silinmiş olsa bile kalır)**
```
git log --all --diff-filter=A --name-only --pretty=format: | sort -u \
  | rg -i "\.(jks|keystore|p12|pfx|pem|key)$|(^|/)\.env"
git rev-list --objects --all | rg -i "\.(jks|keystore|p12|pfx)$"
```
**`.gitignore` kapsamı**
```
rg -n "keystore|jks|key\.properties|signing|\.env|\.apk|\.aab" .gitignore
```

**Yorumlama kuralı:** desen eşleşmesi ≠ sır. `storePassword=<kullanıcı girer>` bir yer
tutucudur, sır değildir. Her eşleşmeyi AÇ ve oku; rapora "N eşleşme, hepsi/şu kadarı
yer tutucu" diye yaz — ham sayı verme.

---

## T7 — BaaS / doğrudan-istemci veritabanı var mı?

**Nasıl ölçülür:** bağımlılıklarda `@supabase/supabase-js`, `firebase`, `firebase-admin`,
`appwrite`, `pocketbase`, `@aws-amplify/*` · ortam değişkenlerinde `SUPABASE_URL`,
`FIREBASE_CONFIG`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` · kodda `createClient(`,
`initializeApp(`, `.from('<tablo>').select(` · repoda `supabase/` klasörü,
`firestore.rules`, `storage.rules`, `firebase.json`.

**EVET ise → ŞERİT C zorunlu** (`references/serit-C-baas-rls.md`).
Bu mimaride istemci veritabanıyla DOĞRUDAN konuşur; yetkiyi uygulayacak sunucu yoktur,
RLS/kurallar tek yetkilendirme katmanıdır. T2 (sunucu kodu) HAYIR olsa bile Şerit C açılır —
"sunucu yok, o hâlde sunucu açığı yok" çıkarımı bu mimaride YANLIŞTIR.

## T8 — Yapay zekâ / LLM yüzeyi var mı?

**Nasıl ölçülür:** bağımlılıklarda `openai`, `@anthropic-ai/sdk`, `langchain`,
`llamaindex`, `@google/generative-ai`, `ollama`, `transformers` · ortam
değişkenlerinde `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` benzeri · kodda `chat.completions`,
`messages.create`, `embeddings`, `vectorStore`, `tools:`/`functions:` tanımı ·
istem şablonu dosyaları (`prompts/`, `*.prompt`, sistem istemi dizgeleri).

**EVET ise → ŞERİT D zorunlu** (`references/serit-D-yapayzeka.md`).
LLM çağrısı, **saldırganın yazdığı metnin talimat olarak okunabildiği** tek yerdir;
modelin araçları varsa o talimat eyleme dönüşür. Şerit D, Şerit B'nin yerini almaz —
LLM ucu da bir API ucudur (kimlik, hız sınırı, maliyet → B2/B9).

**T8'e ek ölçüm — vektör/ajan yüzeyi (D7/D8'i açar):** bağımlılıklarda `pgvector`,
`@pinecone-database/pinecone`, `weaviate-client`, `chromadb`, `qdrant-client`, `faiss` ·
kodda `embeddings.create`, `.similaritySearch(`, `.upsert(`, `.query(vector` · MCP
sunucu bağlantısı (`mcpServers`, `@modelcontextprotocol/*`) · ajan çerçevesi (LangChain
agent, LlamaIndex agent, AutoGen, CrewAI) · kalıcı hafıza (`memory`, vektör-hafıza,
konuşma geçmişi kalıcılığı). Bunlardan biri EVET ise D7 (vektör/embedding) ve/veya D8
(araç/MCP tedarik güveni, ajan hafızası) şeridin **içinde** ayrıca koşar — yeni T
gerekmez, zaten T8 EVET olduğu için Şerit D açık.

**Not — iOS tespiti:** Şerit A **her zaman** koşar (yeni T gerekmez); `Info.plist`,
`*.xcodeproj`/`*.xcworkspace`, Capacitor `ios/` klasörü veya `.ipa` varsa Şerit A'nın
iOS kolonu (`serit-A-istemci.md` §A8) da koşar. Burada tekrar edilmez, tek satır
çapraz-referanstır.

---

## T11 — Ters vekil / CDN / çok-katman var mı?

```
fd "nginx\.conf|haproxy\.cfg"
rg -n -i "cloudflare|fastly|akamai|cloudfront" -g '!node_modules'
rg -n -i "x-forwarded-(for|host|proto)" -g '!node_modules'
```
Ön-uç (ters vekil/CDN) **ve** arka-uç (uygulama sunucusu) ikilisi varsa EVET.
`X-Forwarded-*` işleme kodu, HTTP/2-3 kullanımı da işaret.

**EVET ise → Şerit B derinleşir** (`references/serit-B-sunucu.md`): request smuggling
(B16), host header injection (B17), cache poisoning/deception (B18). Not: subdomain
takeover (B19) ayrı tetiklenir — T1 (ağ) + dağıtım artefaktı (CNAME/DNS) yeterlidir,
T11 şart değildir.

## T12 — IaC / bulut yapılandırması var mı?

```
fd -e tf -e tfvars
fd "serverless\.(yml|yaml)|Dockerfile|docker-compose\.(yml|yaml)"
rg -l "kind:\s*(Deployment|Pod|StatefulSet|DaemonSet)" -g '*.yaml' -g '*.yml'
rg -n -i "cloudformation|pulumi" -g '!node_modules'
```
`*.tf`/`*.tfvars`, CloudFormation/Pulumi şablonu, k8s manifest (`kind:`), `Dockerfile`
içeriği ya da bulut SDK bağımlılığı varsa EVET.

**EVET ise → CI/CD şeridinde konteyner/IaC sertleştirme bölümü açılır**
(`references/cicd-depo-ve-kurtarma.md` §6).

## Şerit kararı — örnekler

| Proje | T1 | T2 | T3 | T4 | Karar |
|---|---|---|---|---|---|
| Offline Capacitor uygulaması | Hayır | Hayır | Hayır | Hayır | Yalnız Şerit A |
| Statik tanıtım sitesi (form yok) | Evet (CDN) | Hayır | Hayır | Hayır | Şerit A (dar) + tedarik zinciri |
| Next.js + Postgres + giriş | Evet | Evet | Evet | Evet | Şerit A + Şerit B (tam) |
| Yerel masaüstü aracı, dosya okur | Hayır | Hayır | Hayır | Hayır | Şerit A (dosya/deserileştirme ağırlıklı) |

Sunucusuz projede rapor Şerit B'yi **tek satırda** kapatır:

> **Şerit B (sunucu/API/DB/kimlik): MİMARİ OLARAK YOK.** T1–T4 ölçümü: INTERNET izni
> yok (aapt), ağ API'si 0, sunucu kodu yok, DB yok, hesap yok. SQL injection, SSRF,
> CSRF, oturum kaçırma, yetkilendirme atlatma sınıfları **yapısal olarak
> uygulanamaz** — madde madde N/A listesi yazılmadı.
