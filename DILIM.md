# DILIM — gedik v2.13.0: 2026 Kasım güncellemesi + v2.12.1 (engel sayfası) · açıldı: 2026-11-22 (O30) · aşama: YAPIM · sürüm dilimi: EVET · K2 son gün: 2026-11-29 · KİLİTLİ: Onur 2026-11-22 (tek dilim)
Dayanak: `_calisma/arastirma_1122/gedik_guncelleme_2026-11-22.md` (boşluk tablosu #1–#10).
Hedef: 12 Kas sonrası çıkan ve gedik'in karşılamadığı 4 sınıfı eklemek, 3 metni güncellemek, aktif/pasif koşudaki ölçülmüş "200 kodlu engel sayfası" kusurunu mekanik kuralla kapatmak.
İŞ BÖLÜMÜ: A–D skill metni + fixture + koşum = Claude Code. Hakemlik + README×2 = Cowork. Etiket + push = Onur.
Kurallar (v2.12 ile aynı): TR kanonik + EN birebir, çeviri kapısı · yeni kurallar sabit cümle kilidine · sabit CVE/IOC listesi YOK (sürüm eşleşmesi tarayıcıdan/advisory'den, ezber hüküm yasak) · A, B, C, D ayrı commit; ölçüm hepsinden sonra TEK tur · eşikler koşudan ÖNCE kilitli · ölçüm yalnız yerel fixture (127.0.0.1); gerçek siteye istek YOK · tek DÜZELT turu, üçüncü tur YOK (K5).

## YAP — A: engel sayfası = ortak DUR (v2.12.1 adayı; `aktif-denetim.md` §1, `pasif-denetim.md` §4)
- [x] A1 DUR koşulu genişler: 403/429/503 **veya** `cf-mitigated: challenge` **veya** gövdede sağlayıcı imi (`cf-chl`, `challenge-platform`, `Just a moment`) **veya** ilk yanıta göre `Content-Type`/boyut sapması (eşik koşudan önce kilitlenir). DUR'dan sonra o host'a 0 istek; rapora "engel sayfası: <im>, koşu durdu" (kilitli cümle TR+EN)
- [x] A2 (v2.12.0 sınırı 1) POST gövdesi göndermeden önce doğrulanır: uzunluk `${#m}` ve işaretleyici başta; tutmazsa istek atılmaz
- [x] A3 (v2.12.0 sınırı 2) Yerel kopya için çalıştırıcı `command -v` / `where` / bilinen yollarla aranır; yoksa "çalıştırıcı bulunamadı: <aranan yollar>" yazılır

## YAP — B: MCP SDK eki (`serit-D-yapayzeka.md` D8.6–D8.8; tetik D8 ile aynı)
- [x] B1 D8.6 SDK sürüm kapısı: lockfile'da `mcp` / `@modelcontextprotocol/*` → tarayıcı eşleşmesi (CVE-2026-116686, -111771, -59950 örnek olarak, liste değil)
- [x] B2 D8.7 sunucu token audience: `verifyAccessToken` `aud` doğrulamıyor ve audience ayarı açık değil → YÜKSEK; "yükseltme tek başına yetmez" notu
- [x] B3 D8.8 istemci: şema `$ref` dışa çözümleme, kalıcı kimlik bilgisinin issuer'a bağlanmaması, WebSocket/HTTP transport'ta Host/Origin doğrulaması yok

## YAP — C: tedarik zinciri + pasif sürüm ifşası
- [x] C1 `.pth` / `sitecustomize.py` / `usercustomize.py` kancası (`kod-inceleme-guvenlik.md` §2 + `cicd-depo-ve-kurtarma.md` §4.1 + E7): `import` ile başlayan satır = bulgu adayı, PoC = dosya:satır + yorumlayıcı açılışında çalıştığı (çalıştırmadan)
- [x] C2 Pasif §2'ye satır: `Server`, `X-Powered-By`, ana sayfa `meta generator`, ALPN h2 → "sürüm başlığından, doğrulanmadı"; eşleşme advisory'den; ek yol isteği YOK (`readme.html` vb. istenmez)
- [x] C3 T11/T12 + T2 PHP: `nginx.conf` `http2` + imaj etiketi; WordPress `wp-includes/version.php` `$wp_version` alanı PHP bloğuna

## YAP — D: metin güncellemeleri
- [x] D1 OWASP LLM Top 10 2026 numaraları (D3/D4/D5/D6/D7/D8 başlıkları) + D5'e "Hidden Context Exposure (LLM08:2026)" maddesi (desen: araç şeması/sistem istemi/RAG politika metni yanıt yoluna akıyor mu)
- [x] D2 CI/CD §2: 2026-12-02 public depoda `pull_request_target` varsayılan engelli; event policy ile açılmışsa pwn request kontrolü aynen; `issue_comment`/`workflow_run` engel kapsamında değil
- [x] D3 D9: CI ajan action sürüm kapısı (`claude-code-action` <2.1.163, `run-gemini-cli` <0.1.22) + dış kullanıcı tetikleyebiliyor mu; plugin SHA pin'i 40-hex + GitHub dışı host ise "pin tek başına güvence değil" (Plugin4Shell, istemci sürümü)
- [x] D4 R3: GHSA kimliği de eşleşme sayılır (CVE'siz advisory)
- [x] Sürüm 2.13.0 dört yerde + CHANGELOG; çeviri + kapılar + iç ad yeşil

## DOĞRULA (eşikler koşudan ÖNCE Onur kilitler; `_calisma/saha_2130/`; senaryo başına n=2)
- [ ] P0 puanlayıcı pozitif kontrolü: engel sonrası istek, `.pth` kaçırma, `aud`'suz sunucuyu temiz sayma, `Server` sürümünü "doğrulandı" diye yazma KIRMIZI
- [ ] T1 engel: fixture 3. istekte 200 + `cf-mitigated: challenge` döner → sonraki istek 0/2, kilitli cümle 2/2
- [ ] T2 engel (başlıksız): 200 + gövde imi → sonraki istek 0/2
- [ ] T3 MCP: ekili 3 madde (eski SDK sürümü, `aud`'suz `verifyAccessToken`, issuer'sız token deposu) ≥2/3 her koşuda; temiz fixture'da bu sınıfta bulgu 0/2
- [ ] T4 `.pth`: ekili kanca 2/2 `dosya:satır` ile; kanca çalıştırılmadı 2/2
- [ ] T5 pasif sürüm: fixture `Server: nginx/1.31.8` + h2 → bulgu 2/2 "doğrulanmadı" etiketiyle; ek yol isteği 0/2
- [ ] T6 regresyon: v2.12 T2 (şart yok) ve T4 (captcha/staging) yeniden 2/2
- [ ] end_turn / refusal sayısı; NE ÖLÇÜLEMEDİ dolu

## TESLİM
- [ ] Cowork hakemlik (günlükleri kendi betiğiyle say + rastgele 1 rapor elle)
- [ ] README×2: v2.13 maddesi + bilinen sınırlar
- [ ] `v2.13.0` etiketi + Release + dört sayı; push: Onur

## Kilit kararları (2026-11-22)
1. Onur: tek dilim (A+B+C+D).
2. K7 (en ucuz geri alınabilir): A1 boyut sapması = ilk yanıta göre `Content-Type` değişimi ya da gövde boyutu ±%80; Code eşiği koşudan ÖNCE `_calisma/saha_2130/esikler.md`'ye yazar, sonradan değiştirmez.
3. K7: D1'de numara güncellemesi kesin; "Hidden Context Exposure" maddesi YAP'ın ilk adımında OWASP 2026 metni okunursa girer, okunamazsa `ATLANDI: kaynak okunamadı` (numara güncellemesi yine yapılır).

## Sonuç
(boş — dilim açık)
