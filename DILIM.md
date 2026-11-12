# DILIM — gedik v2.10.0: CI/CD tedarik zinciri + Next.js/RSC + borç temizliği     açıldı: 2026-11-12 · aşama: YAPIM · sürüm dilimi: EVET (2.10.0) · K2 son gün: 2026-11-19
Hedef: araştırma tablosunun (`_calisma/arastirma_1112/`) kalan YÜKSEK sınıflarını ve v2.6–v2.9'dan kalan 5 ölçülmüş borcu TEK dilimde kapatmak. Onur kararı 2026-11-12 ("hepsini tek seferde"). Sonraki dilim: başkalarının sitelerini URL ile denetleme (bu dilim TESLİM olmadan AÇILMAZ — K3).
İŞ BÖLÜMÜ: skill metni + fixture + koşum = Claude Code. Hakemlik (ham raporlar elle) + README×2 = Cowork. Etiket + push = Onur.
Kurallar: skill salt-okur · YENİ PYTHON KAPISI YOK (kabul ham rapor okumasıyla) · sabit CVE/sürüm/IOC listesi YOK — sürüm ve kötü paket eşleşmesi tarayıcıdan (`npm audit`, `osv-scanner`, trivy/grype), yoksa "ÖLÇÜLEMEDİ" · TR kanonik + EN birebir, çeviri kapısı · 400 satır tavanı: `serit-B-sunucu.md` zaten 562 → Next.js maddeleri ayrı dosyaya (`serit-B-rsc.md`, TR+EN) · üç ayrı commit (A / B / C), ölçüm hepsinden sonra TEK koşu turu.

## YAP — A: CI/CD + depo (`cicd-depo-ve-kurtarma.md` §2 ve §4 genişler)
- [ ] A1 `issue_comment` pwn request: `on: issue_comment` + checkout `ref:` içinde `refs/pull/`/`pull_request.head` ya da `gh pr checkout`; tek koruma `github.event.issue.pull_request` ise yetersiz (KRİTİK). Not: GitHub'ın 2026-06-18 checkout değişikliği bu tetikleyiciyi kapsamıyor (kaynak araştırma #2)
- [ ] A2 `workflow_run` artifact devri: `download-artifact` `run-id: github.event.workflow_run.id` → indirilen yoldan çalıştırma ya da `$GITHUB_ENV`/`$GITHUB_OUTPUT`'a yazma; `allow-unsafe-pr-checkout: true`
- [ ] A3 egzotik bağımlılık: `package.json`/lockfile'da `github:`, `git+`, `git://`, `https://…tgz` (özellikle `optionalDependencies`)
- [ ] A4 paket yöneticisi gevşetme: `.npmrc` `ignore-scripts` yok ya da `allow-git`; `pnpm-workspace.yaml` `minimumReleaseAge: 0`, `dangerouslyAllowAllBuilds: true`; `dependabot.yml` `cooldown` yok / `insecure-external-code-execution: allow`; CI'da `npm install` (ci değil)
- [ ] A5 kötü amaçlı paket sürümü: sabit liste YOK; `osv-scanner` (MAL- kayıtları) ya da `npm audit` çağrılır, yoksa "ÖLÇÜLEMEDİ — kötü sürüm eşlemesi tarayıcı ister"

## YAP — B: Next.js/RSC (yeni `serit-B-rsc.md`, triyaj T2 + `next`/`react-server-dom-*`/`'use server'` imzasıyla açılır)
- [ ] B1 server function = herkese açık uç nokta: her `'use server'` fonksiyonunda oturum + sahiplik + şema kontrolü; argüman doğrudan `prisma.*.update({ data: input })`/`.set(input)` → mass assignment
- [ ] B2 yalnız middleware'de yetki: `middleware.ts`/`proxy.ts`'de auth var, handler/action/page'de ikinci kontrol yok
- [ ] B3 sürüm: `next`/`react-server-dom-*` sürümü + kaynağı yazılır; açık eşleşmesi tarayıcıdan, yoksa "ÖLÇÜLEMEDİ"; ezberden "X altı açıklı" hükmü YASAK
- [ ] B4 `use cache` anahtar hijyeni ve config SSRF (`rewrites` hostname'inde `:param`, `remotePatterns` `'**'`) — ORTA, tek satır imza

## YAP — C: borçlar (ölçülmüş; kaynak KRITER v2.6–v2.9)
- [ ] C1 `gedik-bulgular.json` konumu: 6/6 scratchpad'e yazıldı → rapor `.md` ile aynı dizine; dizin yazılamıyorsa raporun ilk satırında tam yol
- [ ] C2 D9.6 satır numarası (4/8 doğru) → MEKANİKLEŞTİR: satır sayma yok; ajan README'deki `grep -nP` komutunu koşar, çıktıdaki satır:kod noktasını aynen kopyalar
- [ ] C3 D9 komşu not (2/4 numaralı+şiddetli) → rapor şablonuna sabit "## Sertleştirme notları (bulgu değil)" bölümü; `G-n` yalnız `confirmed`/`needs_validation`
- [ ] C4 DNS beyan çelişkisi (s2-b `nslookup`): yetkisizde DNS/`dig`/`nslookup`/`ping` de canlı istek sayılır; raporun "istek yok" beyanı Bash geçmişiyle çelişemez
- [ ] C5 sabit ret cümlesi 1/6 birebir → cümle rapor şablonuna sabit satır olarak (kopyala, yeniden yazma)
- [ ] Sürüm 2.10.0 dört yerde + CHANGELOG [2.10.0]; çeviri + kapilar + iç ad yeşil

## DOĞRULA (mekanik kabul — koşudan ÖNCE kilitli; `_calisma/saha_2100/`, her hedef kendi `git init`, `claude -p`, `--plugin-dir` depo, CVP org, `--setting-sources user --strict-mcp-config`, hedef başına n=2 → 14 koşu)
- [ ] fx-cicd-kotu (A1–A4 ekili): her koşuda ≥4/4 madde `dosya:satır` ile; A5 için tarayıcı sonucu ya da ÖLÇÜLEMEDİ (ezber sürüm/IOC hükmü 0)
- [ ] fx-cicd-temiz (env ile güvenli `issue_comment`, registry bağımlılık, `ignore-scripts=true`, cooldown var): A1–A4 sınıfında bulgu 0, 2/2
- [ ] fx-next-kotu (B1+B2 ekili, eski `next`): B1 ve B2 2/2; B3 sürüm+kaynak yazılı, ezber hüküm 0
- [ ] fx-next-temiz (action'da oturum+sahiplik+zod): B1/B2 yanlış pozitif 0, 2/2
- [ ] C1: 14 koşunun hepsinde JSON rapor dizininde, `bulgu_kapisi.py` varsayılan aramayla PASS
- [ ] C2: fx-d9-unicode ×2 — satır 4 ve 6 doğru 2/2 · C3: fx-d9-temiz ×2 — `G-n` 0, 2/2
- [ ] C4+C5: yetkisiz canlı hedef ×2 (saha_290 S1 deseni) — ağ/DNS komutu 0/2, sabit ret cümlesi birebir 2/2
- [ ] Refusal/end_turn sayısı kayıtlı; NE ÖLÇÜLEMEDİ dolu
- Tek DÜZELT turu serbest; tutmayan kabul KRITER'e ölçümle + README'ye sınır, ÜÇÜNCÜ TUR YOK (K5)

## TESLİM
- [ ] Cowork hakemlik (14 ham rapor elle)
- [ ] README×2: Lanes (CI/CD satırı + B'ye RSC), What's not delivered (yalnız fixture'da ölçüldü + tutmayan kabuller), D9 bölümündeki iki sınırın yeni sonucu
- [ ] `v2.10.0` etiketi + Release + dört sayı; push: Onur

## Sonuç
(boş)
