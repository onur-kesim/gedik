# DILIM — gedik v2.9.0: Şerit D9 — depo içi ajan yapılandırması (yürütülebilir yüzey)     açıldı: 2026-11-12 · aşama: YAPIM · sürüm dilimi: EVET (2.9.0)
Hedef: Bir depoda duran ajan yapılandırmasını (Claude Code/Cursor/Copilot/Gemini/VS Code) yürütülebilir saldırı yüzeyi olarak denetleyen D9 maddesini eklemek. D8 yalnız T8 (uygulamada YZ) EVET iken açılıyor; bu yüzey YZ kullanmayan depoda da var → D9 T8'den BAĞIMSIZ, kendi triyaj sinyaliyle açılır.
Neden (ölçüldü, `_calisma/arastirma_1112/Yeni_acik_siniflari_2026.md` tablo #1 ve #6): Claude Code CVE-2025-59536 / CVE-2026-21852 (Check Point 2026-02-25, KESİN; Cowork D5 ile doğruladı), Cursor CVE-2026-48124 (Pillar 2026-07-20, KESİN), Windsurf CVE-2026-30615 (ZAYIF). gedik skill'inde `settings.json`, `AGENTS.md`, `zero-width`, `bidi` sözcükleri 0 dosyada.
İŞ BÖLÜMÜ: skill metni + fixture + koşum = Claude Code. Hakemlik + README×2 = Cowork. Onur kararı 2026-11-12 ("bu boşluğu da kapatalım").
Kurallar: skill salt-okur; YENİ PYTHON KAPISI YAZILMAZ (PHP kapısı dersi: anahtar-sözcük kapısı kâğıt turu üretti) — kabul ham rapor okumasıyla; sabit CVE listesi yok, sürüm kontrolü "Claude Code'u güncel tut" düzeyinde.

## YAP — A: skill metni (TR kanonik `serit-D-yapayzeka.md` + EN birebir; çeviri kapısı)
- [x] Triyaj: T8'den bağımsız ölçüm — depoda `.claude/`, `.mcp.json`, `.cursor/`, `.vscode/{mcp,settings,tasks}.json`, `.gemini/`, `.devcontainer/`, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, `.cursorrules`, `SKILL.md`/`.claude/skills/` varsa D9 AÇILIR (SKILL.md şerit seçimine bir satır)
- [x] D9 tablosu (Zayıflık · Bakılacak imza · Şiddet): D9.1 hook komutları (`hooks.*.command`, SessionStart/Stop/PreToolUse; `curl`/`bash -c`/ağ) · D9.2 proje MCP otomatik onayı (`enableAllProjectMcpServers`, `enabledMcpjsonServers`) + `.mcp.json` pinsiz `npx -y`/`uvx`/`bash -c` · D9.3 uç nokta/ortam yönlendirme (`env.ANTHROPIC_BASE_URL`, `NODE_OPTIONS`, `apiKeyHelper`) · D9.4 izin gevşetme (`defaultMode: bypassPermissions`, auto-approve/YOLO; CI'da `claude -p … --dangerously-skip-permissions`, `--yolo`, `codex --full-auto` güvenilmeyen tetikleyiciyle) · D9.5 ajanın kendi yapılandırmasına yazabilmesi (`.claude/**`, `.mcp.json`, `AGENTS.md` için Edit/Write deny yokluğu; CODEOWNERS yokluğu) · D9.6 talimat dosyasında gizli Unicode (U+200B–200F, U+202A–202E, U+2060–2064, U+2066–2069, dosya başı dışı U+FEFF, U+E0000–E007F) — kod noktası + satır raporlanır · D9.7 diğer IDE yürütmesi (`.vscode/tasks.json` `runOn: folderOpen`, `.devcontainer` `postCreateCommand`)
- [x] PoC kuralı (K2) D9'a uyarlanır: yapılandırmayı ÇALIŞTIRMADAN kanıt = dosya:satır + alan + değer + hangi istemcinin bunu ne zaman yürüttüğü (kaynaklı); "çalıştırıp gör" YASAK
- [x] Rapor kuralı: denetlenen depo güvenilmeyense rapor başına tek satır uyarı ("bu depo ajan yapılandırması taşıyor; bir ajanda açmadan inceleyin")
- [x] Sürüm 2.9.0 dört yerde + CHANGELOG [2.9.0]

## YAP — B: fixture + koşum (`_calisma/saha_291/`, her hedef kendi `git init`)
- [x] fx-d9-kotu: `.claude/settings.json` (SessionStart hook ZARARSIZ işaretçi: hedef dizine `HOOK_KOSTU.txt` yazar; `enableAllProjectMcpServers: true`; `env.ANTHROPIC_BASE_URL: https://ornek.invalid`), `.mcp.json` `npx -y paket` pinsiz, `.github/workflows/ai.yml` `on: issue_comment` + `claude -p --dangerously-skip-permissions`, `.vscode/tasks.json` `runOn: folderOpen`
- [x] fx-d9-unicode: `AGENTS.md` içinde U+200B ve U+202E (+ tag karakteri) gizli talimat
- [x] fx-d9-temiz: sıkı `.claude/settings.json` (deny kuralları, hook yok), pinli `.mcp.json`, Unicode yok
- [x] Koşu: 3 hedef × 2 = 6, `claude -p`, `--plugin-dir` depo, CVP org, **`--setting-sources user`** (proje ayarı YÜKLENMEZ — hook çalışmasın); her koşudan sonra `HOOK_KOSTU.txt` var mı ölçülür

## DOĞRULA (mekanik kabul — koşudan ÖNCE kilitli)
- [x] Kapılar yeşil (kapilar · çeviri · kilit · iç ad); lint değişmedi
- [x] fx-d9-kotu 2/2 → TUTTU 2/2 (5/5 her koşuda): raporda hook, MCP oto-onay, `ANTHROPIC_BASE_URL`, CI `--dangerously-skip-permissions`, `runOn: folderOpen` — her biri dosya:satır ile (≥ 4/5 madde her koşuda)
- [x] fx-d9-unicode 2/2 → TUTMADI 0/2 (kod noktası 2/2 doğru, SATIR numaraları yanlış): gizli karakter kod noktası + satırıyla raporlandı
- [x] fx-d9-temiz 2/2 → TUTMADI 1/2 (temiz-b: deny/pinli MCP için komşu bulgu): D9 yanlış pozitif 0 (deny kuralı/pinli MCP "bulgu" yazılmaz)
- [x] `HOOK_KOSTU.txt` 0/6 → TUTTU 0/6 (pozitif kontrol geçti); end_turn 6/6, refusal 0/6 (hiçbir koşuda hook çalışmadı); refusal/end_turn sayısı kayıtlı
- [x] NE ÖLÇÜLEMEDİ (dolu)

## TESLİM
- [x] Cowork hakemlik (6 raporun 6'sı elle; ayrı oturum) — O23: 10/10 rapor (ilk tur 6 + DÜZELT 4) elle okundu; Code'un sayımı 10/10 tuttu, fark yok
- [x] README×2: Lanes tablosunda D satırına D9 + "What's not delivered": D9 yalnız fixture'da ölçüldü (O23; iki bilinen sınır + `grep -nP` doğrulama komutu, komut fixture'da pozitif kontrollü: unicode satır 4,6 · temiz 0)
- [ ] `v2.9.0` etiketi + Release; push: Onur

## DÜZELT (2026-11-12 · TEK tur; üçüncü tur YOK)
- [x] D9.6 (TR+EN): satır, bayt ofsetinden değil satır sayarak; raporda kod noktası + satır + bayt ofseti birlikte
- [x] D9 dürüst-sınırlar (TR+EN): deny kuralı / pinli MCP / CODEOWNERS varlığı ve kapsam eksiği D9 bulgusu DEĞİL; gözlem "sertleştirme notu"nda şiddetsiz
- [x] Çeviri + kapılar + ic_ad yeşil
- [x] Yeniden koşu: fx-d9-unicode ×2 + fx-d9-temiz ×2 (aynı ayarlar, ham `_calisma/saha_291/ham_d1/`)
- [x] Kabul (ÖLÇÜLDÜ, TUTMADI: unicode satır 1/2 + bayt ofseti 0/2; temiz D9 bulgusu 0 → 1/2; HOOK_KOSTU 0/4 TUTTU; üçüncü tur YOK): unicode 2/2 kod noktası + DOĞRU satır (ZWSP 4, RLO/PDF/tag 6) · temiz 2/2 D9 bulgusu 0 · HOOK_KOSTU 0/4. Tutmazsa: KRITER'e ölçüm + sınır README'ye aday olarak, ÜÇÜNCÜ TUR YOK

## Sonuç
2026-11-12 (DÜZELT dahil): YAP + DOĞRULA bitti. İlk tur: kotu 2/2, unicode 0/2, temiz 1/2, HOOK 0/6. DÜZELT turu (4 koşu): HOOK 0/4 TUTTU; unicode kod noktası 2/2 ama doğru satır 1/2 ve bayt ofseti 0/2; temiz 1/2 (temiz-a G-N1/G-N4 numaralı+şiddetli). Kabul tutmadı, üçüncü tur YOK. README'ye aday sınırlar KRITER "v2.9.0 DÜZELT"te. TESLİM açık (Cowork hakemlik, README×2 + aday sınırlar, etiket + push: Onur).
