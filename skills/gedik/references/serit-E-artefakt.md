# LANE E — SHIPPED ARTIFACT HYGIENE

**When it runs:** If T9 is YES (there is a shipped artifact).

**Its axis:** Not what's written in the source, but **what's in the shipped file.** What
reaches the user's hands is the artifact; not the source. So *"I fixed it in the source"* does
not close a finding — the measurement is taken on the shipped artifact, and repeated there.

> **Handoff boundary.** Android/Play-specific package teardown, signature chain, dex-diff, and
> store policy compliance are the job of the relevant **build QA** tool. This lane's
> items are **platform-independent**. Do not report the same finding in two places; state which
> one ran in a single line in section 0 of the report.

---

## E0 — IDENTIFY AND OPEN THE ARTIFACT

Artifact types: web bundle (`dist/`, `build/`, `.next/`, `out/`) · APK / AAB ·
exe / dmg / AppImage / MSI · container image · npm tarball · `.whl` / `.jar` / `.nupkg` ·
browser extension `.zip` / `.crx` · serverless function package.

If it's zip-based, open it and **produce a file inventory**: name, size, count. There is no
scan without an inventory — a scan that doesn't know what it didn't scan cannot say "clean."

Looking at a file in the source tree is **not** this lane's job; that belongs to LANE A/B and
code review. Every finding here comes out of the artifact itself.

---

## E1 — SECRET LEAKAGE (in the artifact)

**Search for:** API key patterns (`AKIA`, `sk-`, `ghp_`, `AIza`, `xox[baprs]-`,
`-----BEGIN * PRIVATE KEY-----`) · JWT (`eyJ`) · connection strings (`://user:password@`) ·
`.env` contents · keystore / p12 / pem · a `.git` folder or source archive leaked into the
package. Also **high-entropy scanning**: base64/hex, length ≥ 20, out of dictionary.

> **Per K3:** Pattern searching alone is not enough to say "no secrets." Either produce the
> full embedded-string inventory and give its count, or write `NOT MEASURED`.

**Blind gate (K4):** Plant a fake key (`AKIA` + a random string) into a **copy** of the
artifact and run the scan. If it doesn't bite, the scan is blind — the area is not clean, it
means **no measurement**.

**False-alarm discrimination — important.** Not every key that reaches the client is a
finding: the Firebase web `apiKey`, the Supabase `anon` key, and similar are public by design
and carry no authority on their own. The finding is a key that **carries authority**:
`service_role`, secret key, private key, admin/CI token, signing key. Measure the key's scope
and state it in the report; if you cannot measure it, say "scope NOT MEASURED," not "critical."

When a secret is found, **deleting it from the file does not close the finding.** The rotation
procedure is in `cicd-depo-ve-kurtarma.md`, and the finding closes only once rotation is done.

---

## E2 — DEBUG / DEVELOPMENT FLAG

`debuggable=true` · `NODE_ENV` not production · `__DEV__` · `DEBUG=1` · developer menu ·
hot-reload server address · test account or backdoor · stack trace exposed to the user · an
open React/Vue DevTools hook · an `assert` left in production · a log line that writes a token
or personal data.

Evidence: where the flag occurs in the artifact **plus** an observation of the behavior.
Finding the string alone is not enough; if possible, run the artifact and see the behavior. If
you can't run it, say so.

---

## E3 — SOURCE MAP AND SOURCE RECONSTRUCTION

Check: are `*.map` files in the package · does the production bundle have
`//# sourceMappingURL=` and is its target reachable · has `.ts`/`.jsx` source made it into the
package · is `sourcesContent` embedded.

**Impact:** The source is reconstructed; internal logic, comments, remaining secrets, and the
attack surface are exposed.

**Measurement:** If a map exists, **actually decode one file back** and state how many source
files were recovered. The finding is not "a map exists"; the finding is *"214 source files were
recovered via the map."*

---

## E4 — TEST / STAGING LEFTOVERS

Hardcoded `localhost`, `127.0.0.1`, `10.0.2.2`, `*.ngrok*`, `staging.`, `test.`, `dev.` hosts ·
internal network IPs · plaintext `http://` endpoints · certificate pinning disabled · Android
`network_security_config` with `cleartextTrafficPermitted="true"` or `debug-overrides` · iOS
`NSAllowsArbitraryLoads`.

**The impact runs two ways:** (a) the production client can talk to the test environment,
(b) the test environment's address is handed to the attacker — test environments are usually
less protected.

---

## E5 — OVER-BROAD PERMISSIONS / LOOSE CONFIGURATION

Platform-independent question: **what more can the artifact ask for than it needs to do its
job?**

- **Mobile:** declared permissions ↔ APIs actually used · an `exported=true` component that
  carries no permission · a broad intent-filter · `android:allowBackup=true` (data extraction
  via backup)
- **Desktop / Electron:** `nodeIntegration:true` · `contextIsolation:false` ·
  `webSecurity:false` · a window loading remote content
- **Browser extension:** `<all_urls>` · `tabs` · `cookies` · `webRequest` — is it necessary
- **Container:** `USER root` · `--privileged` · unnecessary capabilities · secrets embedded via
  `ENV` (stays in the image layer, readable with `docker history`)
- **Package (npm/pip):** `files` / `MANIFEST.in` scope — have tests, `.env`, internal scripts
  made it into the package · is there a `postinstall` script and what does it do

Rule (SKILL.md §4): *"we don't show it in the UI"* is not a defense. Authority is measured in
the artifact.

---

## E6 — ARTIFACT ↔ SOURCE MATCHING

Three questions: **Which commit** was the shipped artifact built from? Was its **hash**
recorded? When rebuilt from the same source, does it come out identical (or at least the same
version string and manifest)?

**Measurement:** the artifact's SHA-256 + the commit it was built from + the build command.
If any one of the three is missing, the result is **NOT MEASURED**, and this is itself a
finding: what was delivered cannot be proven.

If you have the previous version, produce a **file inventory diff** between the two artifacts.
A new file, library, or permission that doesn't appear in the release notes is an unexplained
change.

---

## E7 — EMBEDDED DEPENDENCY FOOTPRINT

Declared dependencies ↔ libraries that **actually make it into** the artifact. A leaked
analytics / ad / telemetry SDK, an unexpected network client, a permission that arrives via a
transitive dependency.

This also affects the accuracy of the privacy declaration — **but compliance of the
declaration form is the job of build QA.** Here only "what's in the artifact" is measured; the
conclusion is handed off there.

---

## BLIND GATE (K4) — mandatory in this lane

At least two mutants, into a **copy** of the artifact:

1. Plant a fake key (E1) → the scan must bite
2. Turn on the `debuggable` / `__DEV__` flag (E2) → the scan must bite

If it doesn't bite, the area is not clean, it's **no measurement**. Also run it on the clean
copy — it must not produce a false positive.

---

## REPORT LINE

```
G-n · <E maddesi> — <artefakt>/<yol>
  kanıt          : <birebir bulunan dizge ya da komut çıktısı — sır MASKELİ>
  tekrar üretim  : <komut>
  etki           : <mimarinin izin verdiği tavana göre>
  şiddet         : ...
  yama           : ...
```

**Secret masking:** Everything except the first 4 and last 2 characters of the found key is
masked; the full value is not written into the report.

---

## LIMITS

- If the artifact cannot be opened (encrypted, a signed closed format, a commercial packer),
  write **NOT MEASURED**; do not say "clean."
- A commercial packer or obfuscator is not broken.
- A found secret is **not used**: whether it's valid is not tested by sending a request to the
  live service (SKILL.md §0 scope lock).
