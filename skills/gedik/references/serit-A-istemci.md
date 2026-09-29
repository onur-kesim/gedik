# LANE A — Client / Offline / Mobile-WebView Surface

In an app with no server, "there's nothing to hack" is WRONG. The surface shifts:
it moves from the network to **input, sink, platform configuration, and supply
chain**. The seven headings below are this lane in full.

---

## A1 — Fuzzing untrusted input paths

For EVERY entry in the T5 inventory, apply the payload families below. After each
payload, measure three things: **(1)** does the app still open (no white screen),
**(2)** did persistent state get corrupted, **(3)** did unexpected execution/navigation
occur.

### A1.1 Prototype pollution
```json
{"__proto__":{"zafiyetKaniti":1}}
{"constructor":{"prototype":{"zafiyetKaniti":1}}}
{"a":{"__proto__":{"zafiyetKaniti":1}}}
{"__proto__":{"toString":"kirli"}}
```
Measurement: after loading, is `({}).zafiyetKaniti` defined? If defined: CRITICAL/HIGH.
Note: `JSON.parse` does **not** pollute `__proto__` **by itself**; the danger is in
code that, after parsing, does `for...in` + assignment / a deep merge (`merge`, an
`Object.assign` loop). So read **not the parse, but the post-parse walk**.

### A1.2 Type confusion
Wrong types in expected places: an array instead of an object, a string instead of a
number, `null`, `true`, a nested array. Measurement: `undefined is not a function` /
white screen / infinite loop.

### A1.3 Numeric exploitation
`NaN`, `Infinity`, `-Infinity`, `-1`, `0`, `1e308`, `9007199254740993`,
the `0.1+0.2` remainder, numeric string `"12"`, `"1e3"`, `"0x10"`.
Measurement: is there a clamp? Negative progress, an infinite counter, date overflow?

### A1.4 Version/migration exploitation (in every schema with a `_v` field)
- Lower `_v` (older version) → does the migration path run, is existing data OVERWRITTEN?
- Raise `_v` (future version) → does the app safely say "unknown version," or does it
  half-load and corrupt data?
- Delete `_v` / turn `_v` into a string.

### A1.5 Size and depth (resource exhaustion)
- ~5–10 MB single string; a 100k-element array.
- 10,000 levels of nested `{"a":{"a":{...}}}` → stack overflow in recursive traversal.
- Thousands of repeats of the same key; extremely long key names.
Measurement: freeze, crash, storage quota error. When the quota fills, `setItem`
throws — is it caught, or does the app lock up?

### A1.6 String/Unicode
```
</script><img src=x onerror="window.__ZAFIYET_KANITI=1">
"><svg onload=window.__ZAFIYET_KANITI=1>
javascript:window.__ZAFIYET_KANITI=1
&#x3c;img src=x onerror=...&#x3e;          (çift kodlama)
‮ ... ​ ... (RTL override, sıfır genişlik)
lone surrogate: "\uD800"
NUL: "\x00" (yük listesinde literal NUL baytı yazma; kaçışlı metin kullan)
```
Measurement: where does this string get written? Safe if `textContent`; if
`innerHTML`, go to A2.

### A1.7 Date/format validation
`2026-13-45`, `9999-99-99`, `2026-1-1` (unpadded), `١٤٤٧-٠١-٠١` (Arabic-Indic
digits), `2026-07-26T00:00:00Z<script>`, negative epoch, `Infinity`.
Measurement: does the regex fully anchor (`^...$`)? If not, a payload can be added
before/after.

### A1.8 Malformed/partial input
Truncated JSON, trailing comma, with a BOM, containing `NaN`/`undefined` (invalid
JSON), completely empty, whitespace only, binary garbage.
Measurement: **is the error caught, does the UI stay up?** White screen = finding.

---

## A2 — Output sink inventory (injection chain)

Count the sinks and **classify** them — counting alone is useless.

```
rg -n "innerHTML|outerHTML|insertAdjacentHTML|document\.write|\.srcdoc"
rg -n "eval\(|new Function|setTimeout\(\s*[\"'`]|setInterval\(\s*[\"'`]"
rg -n "\.src\s*=|\.href\s*=|setAttribute\(\s*[\"'](src|href|on\w+|style)"
rg -n "dangerouslySetInnerHTML|v-html|\{\{\{"
```

A table for every sink — **the "Data it's fed" column cannot be filled by guessing;
it is filled by reading the assignment chain backward** (see `kanit-ve-rapor.md` §2.1
provenance tracing):

| # | Sink | File:line | Data it's fed | Origin | Untrusted? | Escaping |
|---|---|---|---|---|---|---|
| S-1 | innerHTML | x.html:1234 | static template | — | No | unnecessary |
| S-2 | innerHTML | x.html:5678 | `S.mastery[k]` | `load('mastery')` → fallback | **Yes** | `esc()` present/absent |
| S-3 | innerHTML | x.html:9012 | `STREAK.count` | `load('streak')` → fallback | **Yes** | **MISSING ← finding** |

**A commonly missed type:** fields *assumed to be numbers*. A template like
`'…'+sayac+'…'` is an unescaped sink if `sayac` can arrive from storage as a string.
The "it's already a number" assumption cannot be made until numeric coercion is
proven on **every path** where that field is written.

**Also audit the escape function itself.** A typical `esc()` only converts `& < > "`.
This is sufficient for the **element body** and a **double-quoted attribute**, but
INSUFFICIENT in three places: (a) an unquoted attribute (`<div class=X>` — escaped by
a space/`>`), (b) a single-quoted attribute (escaped only if `'` is converted), (c) the
`<script>`/`<style>` body and an `href="javascript:"` context. Read the sink's
**context** — don't just check whether the function exists.

Also: if data passes through a **filter** (an allow-list of known keys, type
checking, a clamp) before reaching the sink, that filter is the real defense — test
the filter with a mutant (K4).

**A2 addendum — DOM Clobbering and CSS injection:**
- **DOM Clobbering (CWE-79 neighbor):** overwriting a JS variable/`document.x` with
  `<a id="x">`/`name=`, without executing script. Signature: implicit global/
  `document.<name>` access + user HTML. `innerHTML` assumed to be "just text" bites
  here.
- **CSS injection/exfil:** if user data goes into `<style>`/`style=`, token
  exfiltration via an attribute selector + `background:url()`, `@import`. Signature:
  user-controlled style.

---

## A3 — Persistent storage integrity

- Is the key prefix consistent; is there a collision risk with another app (same
  origin)?
- **Manual corruption test:** write invalid JSON / a wrong type into `localStorage`,
  open the app. Does it recover, or does it lock up? (A user can't do this
  themselves, but a corrupted write/quota error produces the same result.)
- Quota filling: fill 5 MB, then try a normal save.
- Is sensitive data being stored? (In an offline app, localStorage is unencrypted
  and open to anyone with access to the device — PII/passwords must NEVER go there.)
- Backup export: does the file leak an unexpected field (device ID, path, an extra
  timestamp)?

---

## A4 — Android / platform configuration

**Manifest (from the APK, not the source — the artifact is authoritative)**
```
aapt dump xmltree <apk> AndroidManifest.xml
aapt dump permissions <apk>
```
Checklist:

| Item | Required | Why |
|---|---|---|
| `android:debuggable` | `false`/absent | if true, anyone on the device can debug the process |
| `android:allowBackup` | `false` (if data is sensitive) | `adb backup` exfiltrates data |
| `android:usesCleartextTraffic` | `false`/absent | leaving it open is unnecessary surface even without a network |
| `exported=` | only the LAUNCHER activity | an exported component = another app's entry door |
| `intent-filter` (custom scheme/host) | only if needed | a deep link = an untrusted input path (add to T5) |
| `<provider>` / `grantUriPermissions` | absent | file leakage |
| `launchMode` / `taskAffinity` | default | task hijacking (StrandHogg class) |
| `android:networkSecurityConfig` | — | if present, read its content |

**WebView settings (Capacitor/native code)**
```
rg -n "setJavaScriptEnabled|addJavascriptInterface|@JavascriptInterface"
rg -n "setAllowFileAccess|AllowFileAccessFromFileURLs|AllowUniversalAccessFromFileURLs"
rg -n "setAllowContentAccess|setMixedContentMode|shouldOverrideUrlLoading|WebViewClient"
```
- If `addJavascriptInterface` is present: which methods are exposed? If the JS side
  is compromised it gains native privileges — **the single highest-risk line**.
- `AllowUniversalAccessFromFileURLs=true` → a `file://` page can read every origin:
  CRITICAL.

**Capacitor configuration** (`capacitor.config.*`)
- `server.url` / `server.cleartext` → a development leftover may have leaked into
  production.
- `server.allowNavigation` → is there a wildcard (`*`) in the allow-list?
- `android.allowMixedContent`, `androidScheme`.

**Android inter-component surface (in addition to the manifest checks above)**
- **Intent redirection (CWE-926/940):** does an `exported` component forward an
  `Intent` without trust — `getParcelableExtra("intent")` → `startActivity`.
  Privilege delegation.
- **Mutable PendingIntent:** `FLAG_MUTABLE` on `PendingIntent.get*` calls (or the
  default before API 31) + an empty base intent → another app fills it in and it
  runs with your privileges.
- **Deep link → WebView `loadUrl`:** if a deep-link parameter is loaded directly
  into the WebView, that's universal XSS / JS-bridge access. (T5 counts the deep
  link as input; measure this **chain** separately.)
- **Exported ContentProvider:** `openFile` path traversal, provider query
  injection, `grantUriPermissions` abuse.

**Mutant:** make a component `exported=true` / make a PendingIntent mutable (on a
copy of the manifest) — does the scan catch it?

**Scheme policy (Fable K-J class — measure systematically)**
When navigation is attempted inside the WebView with the following schemes, what
happens: `data:`, `blob:`, `javascript:`, `file:`, `content:`, `intent:`, `market:`,
`tel:`, `mailto:`.
Expected: what should stay in-app stays, what should leave the app exits via a
confirmation dialog, everything else is rejected. **Don't call it "safe" without
measuring.**

---

## A5 — External navigation and intent surface

- EVERY path that leaves the app: `location.href`, `window.open`, `<a href>`,
  `Browser.open` (Capacitor), `startActivity`.
- Is the target URL fixed, or does it come from data? If from data, that's the
  **open redirect** class: can a field in the backup file determine the target?
- Is there a confirmation dialog; does the dialog text show the real destination?
- Is state preserved on return (data loss after returning from an external app =
  an integrity issue)?
- **Reverse tabnabbing:** `target="_blank"` + `rel="noopener"` **absent** → the
  opened page can redirect `window.opener`. Signature: `_blank` links/`window.open`
  missing noopener.

---

## A6 — Supply chain

```
npm ls --all --depth=2         # gerçek ağaç
npm audit --omit=dev           # bilinen CVE
rg -n "\"(preinstall|install|postinstall|prepare)\"" package.json */package.json
```
- Is there a lock file (`package-lock.json`) and is it committed? Otherwise the
  build is not reproducible.
- Any dependency with a `postinstall` script: each one runs code at install time —
  list them.
- The count of direct dependencies and whether each one is actually used.
- If a script is pulled from a CDN: is there SRI (`integrity=`)? If not, compromising
  the CDN compromises the app. (An offline app should have NO CDN at all.)

---

## A7 — Build artifact hygiene

- Things that must NOT be inside the APK/AAB: `.map` source maps, `.git`,
  `node_modules`, test files, keys inside comments, backup `.bak`/`~` files.
- Does the packaged `index.html`'s SHA256 match the source prototype **exactly**?
  (Packaging the wrong file is a security incident: unaudited code ships to the
  device.)
- The signature scheme (v1/v2/v3) and that signing was actually applied.
- Keystore/key store is NOT in the repo; passwords are NOT in plaintext
  configuration (overlaps with T6 — measure it there, don't repeat here).

---

## A8 — iOS / Capacitor-iOS SURFACE (a column that can currently be totally blind)

**Trigger:** an iOS artifact/source — `Info.plist`, `*.xcodeproj`/`*.xcworkspace`,
the Capacitor `ios/` folder, `.ipa`. The artifact is authoritative: `plutil -p
Info.plist`, `otool`, `codesign -dv`.

| Item | Required | Why |
|---|---|---|
| `NSAppTransportSecurity` → `NSAllowsArbitraryLoads` | `false`/absent | `true` = the iOS equivalent of cleartext |
| Custom URL scheme (`CFBundleURLSchemes`) | only if needed | another app can register the same scheme → **scheme hijacking**; the incoming URL must be validated |
| Universal Links (`apple-app-site-association`) | verified | an unverified link can be hijacked |
| Keychain accessibility class | `…WhenUnlocked…ThisDeviceOnly` | `…Always` leaks while the device is unlocked/via backup |
| Pasteboard | no sensitive data placed | the general pasteboard is open to other apps |
| `WKWebView` configuration | `allowFileAccessFromFileURLs` etc. off | the iOS equivalent of the Android WebView controls |
| Code signature / entitlements | matches what's expected | excess entitlements = excess privilege |
| (Optional) jailbreak detection | for sensitive apps | MASVS-RESILIENCE |

**Mutant:** set `NSAllowsArbitraryLoads` to true / remove a URL scheme validation
(on a copy) — does the scan catch it?

---

## A9 — CLIENT MESSAGING & PERSISTENCE

- **postMessage origin (CWE-345/346):** **no `event.origin` check** inside
  `addEventListener('message')`; `targetOrigin:"*"` on send. Signature: look for an
  origin comparison in the message handler; absent = finding.
- **Service Worker:** malicious SW persistence, in-client injection via `fetch`
  intercept, scope breadth. Signature: `serviceWorker.register`, `caches.put`, an
  external source inside the SW.

**Mutant:** remove the postMessage origin check / strip noopener from a `_blank`
(on a copy) — does the scan catch it?

---

## LANE A quick closeout check

If you cannot answer ALL of the following with evidence, the scan is NOT DONE:

1. What is the exact count of untrusted input paths, and were the A1 payloads
   applied to every one of them?
2. How many sinks are there, **was provenance tracing done for each one** (§A2),
   how many touch untrusted data, and is the escaping **context-appropriate** in
   each?
2b. Was a **separate** mutant run for each untrusted-fed sink? (One sink's mutant
   does not cover the others.)
2c. Was **every path** to the same surface measured separately? (E.g. if a storage
   key is reachable via both an "import" path and a "direct write" path, both are
   tried; one may be blocked while the other is open.)
3. Was exported/debuggable/allowBackup measured in the manifest (from the APK)?
4. Was the scheme policy (data:/blob:/javascript:/file:) **measured**?
5. Was the entire git history scanned for secrets?
6. Was the Android inter-component surface (intent redirection, mutable
   PendingIntent, deep-link→WebView) measured?
7. If an iOS artifact/source exists, did A8 run — if not, was it closed out with a
   one-line "no iOS"?
8. Were DOM clobbering and CSS injection/exfil included in the sink chain (A2
   addendum)?
9. Was reverse tabnabbing (`_blank` + missing noopener) measured on external links
   (A5 addendum)?
10. Was the `event.origin` check in `postMessage` handlers and Service Worker scope
    measured (A9)?
11. Did a self-mutant run and bite in at least two areas?
