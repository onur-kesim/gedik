# CHANGELOG
Biçim: Keep a Changelog. Her git etiketi bir bölüm; [Unreleased] altı bir sonraki etiketi bekler.
Sürüm numarası `.claude-plugin/plugin.json`'daki gedik ürün sürümüdür (proje-sablonu'nun
kendi 0.x geçmişi — KUR öncesi, aşağıda — ile karıştırılmaz).

## [Unreleased]

### Belgeler
- **Benchmark güncellemesi (2026-10-01).** README×2: Hedef 1 (NodeGoat) tespit 17/17, yanlış pozitif 0; rapor teslimi Cyber Verification Program onaylı hesapta 3/3, onaysız 2/6 (nedensellik kanıtsız, n=3). Bu satır 2.6.0 dönemine aittir.

## [2.13.0] — 2026-11-22
### Değişti (A — v2.12.1 adayı: engel sayfası, v2.12.0 bilinen sınırları 1 ve 2)
- **A1 engel sayfası = ortak DUR** (`aktif-denetim.md` §1 madde 9 + Ortak DUR; `pasif-denetim.md` §4): HTTP kodu yetmez (bir bot koruması 200 kodlu engel sayfası döndürüp 72 istek daha aldı). DUR koşulları: (a) `403`/`429`/`503` (aktifte testin beklediği sonuç hariç: B3 429, B4/B7 403/404) · (b) `cf-mitigated: challenge` başlığı · (c) gövdenin ilk 4096 baytında `cf-chl` / `challenge-platform` / `Just a moment` · (d) aynı yol/kaynak türünden ilk yanıta göre `Content-Type` ana türü değişimi ya da gövde boyutunun ±%80'den fazla sapması. DUR'dan sonra o host'a 0 istek (pasif okuma dahil); rapora kilitli cümle `engel sayfası: <im>, koşu durdu` / `challenge page: <marker>, run stopped`. Örnek akış kod bloğu artık başlığı ve gövde başını dosyaya yazıp bu koşulları kendisi denetler (yerel sahte sunucuda 3 koşul + temiz akış elle sınandı).
- **A2 POST gövdesi göndermeden önce doğrulanır** (`aktif-denetim.md` §2): gövde değişkende kurulur, `${#m}` uzunluğu ve işaretleyicinin başta olması denetlenir, tutmazsa istek atılmaz ("gövde doğrulanamadı, istek atılmadı"); dolgu için `python` varsayılmaz (`printf '%*s' | tr` örneği, boş komut ikamesi sınandı: gönderilmedi).
- **A3 yerel kopyada çalıştırıcı aranır** (`aktif-denetim.md` §4.4): `command -v` / `where` + bilinen yollar; bulunamazsa kopya kurulmaz ve "çalıştırıcı bulunamadı: <aranan yollar>" (aranan her yol listelenir).
- 8 yeni kilitli cümle (`sabit_cumleler.json` 76 → 84).
### Eklendi (B — MCP SDK eki, `serit-D-yapayzeka.md` D8.6–D8.8; tetik D8 ile aynı, PyPI `mcp` tetiğe eklendi)
- **D8.6 SDK sürüm kapısı:** kilit dosyalarında `mcp` (PyPI) / `@modelcontextprotocol/*` → sürüm eşleşmesi YALNIZ tarayıcıdan (`osv-scanner`, `npm audit`, `pip-audit`); tarayıcı yoksa "ÖLÇÜLEMEDİ — SDK sürüm eşlemesi tarayıcı ister"; sabit CVE/sürüm aralığı listesi YOK (CVE-2026-116686, -111771, -59950 yalnız sınıf örneği, ezber hüküm yasak).
- **D8.7 sunucu token audience:** `verifyAccessToken` token'ın `aud`'unu kendi kaynak kimliğiyle karşılaştırmıyor ve SDK audience ayarı açık değil → YÜKSEK; "SDK'yı yükseltmek tek başına yetmez" (bulgu sürüm VE ayar+kod olarak ayrı yazılır).
- **D8.8 MCP istemci tarafı:** şema `$ref` dışa çözümleme (SSRF/yerel dosya), kalıcı kimlik bilgisi tek global anahtar (issuer'a bağlı değil), WebSocket/HTTP transport'ta `Host`/`Origin` doğrulaması yok → YÜKSEK. PoC çalıştırmadan (`dosya:satır` + eksik kontrol); karşıt örnek "bulgu yok", "güvenli" değil.
- 3 yeni kilitli cümle (`sabit_cumleler.json` 84 → 87).
### Eklendi (C — tedarik zinciri + pasif sürüm ifşası)
- **C1 Python başlangıç kancası** (`kod-inceleme-guvenlik.md` §2 + `cicd-depo-ve-kurtarma.md` §4.1 A6 + `serit-E-artefakt.md` E7): `*.pth` içinde `import` ile başlayan satır ya da `sitecustomize.py`/`usercustomize.py` = bulgu adayı (paket `import` edilmeden her yorumlayıcı açılışında çalışır); şiddet `exec`/`base64`/`subprocess`… içeriğine ve `dist-info/RECORD` kaydına göre; sabit ad/IOC listesi YOK (imza mekanizma); çalıştırmadan tespit komutu (kod bloğu) + PoC `dosya:satır`; o `site-packages`'i kullanan `python`/`pip` başlatmak YASAK (kancayı tetikler).
- **C2 pasif sunucu sürüm ifşası** (`pasif-denetim.md` §2 yeni tablo satırı + kurallar): `Server`, `X-Powered-By`, ana sayfa `meta generator`, ALPN `h2` yalnız zaten yapılmış isteklerin yanıtından; satır "sürüm başlığından, doğrulanmadı" etiketiyle; eşleşme yalnız advisory/tarayıcıdan, yoksa ÖLÇÜLEMEDİ; sürüm için ek yola (`readme.html`, `license.txt`, `wp-login.php`, `/nginx_status`…) istek YOK.
- **C3** `triyaj-ve-kapsam.md` T11 (`nginx.conf` `http2` + `nginx:<sürüm>` imaj etiketi, kaynağıyla; yüzen etikette ÖLÇÜLEMEDİ) ve T2 PHP (WordPress `wp-includes/version.php` `$wp_version`, `kod-inceleme-guvenlik.md` §2.1); `SKILL.md` PHP bloğuna İSTEĞE BAĞLI `WordPress çekirdek` satırı (mekanik kapı bu satırı doğrulamaz).
- 7 yeni kilitli cümle (`sabit_cumleler.json` 87 → 94).
### Değişti (D — metin güncellemeleri; sürüm 2.13.0 `plugin.json`, `marketplace.json`, `SKILL.md` TR+EN)
- **D1 OWASP LLM Top 10 2026** (resmî kaynak, 2026-08-04 yayımı; liste ve LLM08 ham metni 2026-11-22'de okundu): `serit-D-yapayzeka.md` başlıkları 2026 numaralarıyla (D1/D2 LLM01 · D3 LLM03 Excessive Agency · D4 LLM10 Improper Output Handling · D5 LLM02 + LLM08 · D6 LLM06 Unbounded Consumption · D7 LLM09 (2025'te LLM08) · D8 LLM04 Supply Chain); D5'e yeni madde **Gizli bağlam ifşası (LLM08:2026 Hidden Context Exposure)**: bağlamdaki sır, bağlamın gizliliğine dayanan yetki/filtre, araç şeması/iç kuralın yanıt yoluna akması; "ifşa edilebileceğini varsay"; işaretleyici PoC'si; `SKILL.md` TR+EN başvurusu.
- **D2 CI/CD §2:** 2026-12-02'den itibaren public depolarda `pull_request_target` varsayılan engelli (GitHub Changelog 2026-11-02; platform davranışı ÖLÇÜLMEZ); event policy ile açılmışsa pwn request kontrolü AYNEN sürer; `issue_comment`/`workflow_run` engel kapsamında değil; private/internal değişmedi.
- **D3 D9:** D9.8 CI'da koşan kod ajanı (action/CLI sürüm kapısı advisory'den, tek tarihli örnek eşikler `claude-code-action` <2.1.163, `run-gemini-cli` <0.1.22 — BAYATLAR, hüküm advisory'den; dış kullanıcı tetikleyebiliyor mu + sır/yazma jetonu); D9.9 plugin SHA pin'i 40-hex + GitHub dışı host → "pin tek başına güvence değildir" (Plugin4Shell; istemci sürüm eşiği tek ikincil kaynak, GÜVEN ZAYIF). D9 tetiği `.claude-plugin/` ve CI'daki kod ajanı adımını da kapsar.
- **D4 R3:** CVE'si olmayan advisory'nin GHSA kimliği de eşleşme sayılır.
- 6 yeni kilitli cümle (`sabit_cumleler.json` 94 → 100).

## [2.12.0] — 2026-11-15
### Eklendi
- **Şartlı aktif test** (yeni `references/aktif-denetim.md` TR+EN, `SKILL.md` §0.1 (c) işaretçisi): (c) yetkisinin ÜSTÜNE oturur, (a)/(b)'yi değiştirmez. Aktif kip yalnız kullanıcı "aktif test" derse açılır ("denetle", "pentest", "canlı testleri de yap" anahtar değildir); her test `YETKI.md` `aktif:` bölümündeki kendi şartına bağlıdır ve şart yoksa rapora kilitli cümle yazılır: "şart yok, test edilmedi" / "no precondition, not tested". Alanlar: `pencere` (dışı = DUR), `istek_butcesi` (varsayılan 60, toplam, ≤1 istek/sn), `test_formlari`, `llm_uclari`, `test_hesaplari` (2 adet, parola yok), `kanarya_kayitlar`, `kaba_kuvvet`, `captcha`, `staging`, `yuk_testi`.
- **B1–B10** ve tavanları: form (form başına 1 gönderim) · LLM/sohbet (≤10 istek) · hız sınırı (≤30 istek, ilk 429'da DUR) · IDOR (gerçek kullanıcı nesnesine 0 istek) · zararsız XSS/SQLi işaretleyici (uç başına ≤5, veri çeken yük yok) · kanarya kayıt · dizin kaba kuvveti (≤200 yol, ≤1/sn) · CAPTCHA (çözme/atlatma hiçbir şartla yok) · silme/değiştirme/yük yalnız `staging` · B10 mutlak yasak (canlıda DoS, gerçek kişinin veri içeriği, gerçek kullanıcı hesabı, parola girme, CAPTCHA çözme).
- Her POST `GEDIK-TEST-<koşu-id>` işaretleyici taşır; raporda AKTİF İSTEK GÜNLÜĞÜ ve OLUŞTURULAN TEST KAYITLARI (sahip siler).
- **YEREL KOPYA kipi** (`aktif-denetim.md` §4): sahip depo verirse `_calisma/yerel/` altında ayağa kalkar; B1–B9 yerelde şartsız; dış entegrasyonlar etkisiz, yalnız 127.0.0.1; gerçek kişisel veri içeren döküm istenmez/işlenmez ("anonim döküm iste"), yüklemeden önce yalnız sayı veren tarama. Her bulgu `kaynak-kod` / `yerel-kopya` / `canli-pasif` / `canli-aktif` etiketiyle raporlanır; yerelde bulunup canlıda doğrulanmayan "canlıda ÖLÇÜLMEDİ" (`kanit-ve-rapor.md` şablonuna "Kaynak" satırı).
### Değişti
- 21 yeni kilitli cümle (`sabit_cumleler.json` 49 → 70); `pasif-denetim.md` §3: aktif testler artık "yalnız `aktif-denetim.md` kapısıyla" açılabilir.
- **DARALMA (a)/(b) için de:** `SKILL.md` §0.1 "Nazik hız" — canlıda DoS denemesi artık HİÇBİR şartla yapılmaz (önceki metin: "kullanıcı ayrıca ister ve program izin verirse"); B10 ile tutarlılık için. Yük testi yalnız `staging`'de ya da yerel kopyada.
- **DÜZELT turu (K5, tek tur; `aktif-denetim.md` + `pasif-denetim.md` TR+EN, kilit 70 → 76):** her Bash çağrısı TEK istek ya da `sleep 1`'li sayaçlı akış (zincirli `curl`, çoklu URL, `&`, `xargs -P` yasak, örnek akış kod bloğu); B2 uzunluk testinde işaretleyici mesajın başında ve TOPLAM uzunluk tam L+1; kaynak etiketleri yalnız ASCII ve aynen kopyalanır, EN dosyada Türkçe "şart yok, test edilmedi" literal; yerel kopya kapanışında başlatılan süreç kapatılır ve port kapalı doğrulanır (§4.7).
- **DARALMA (pasif denetim, (c) için):** JS'ten çıkan API uçlarına İSTEK ATILMAZ, yalnız adıyla ve dosyasıyla raporlanır (sorgusuz/oturumsuz GET dahil); CORS kontrolü yalnız `/` ve HTML'de açıkça bağlı kaynaklarda yapılır, API uçlarındaki CORS pasifte ÖLÇÜLMEDİ listesine girer (v2.11.0'da bu iki konu belirsizdi).
- DÜZELTME (v2.11.0'dan kalan gizli kusur): `ceviri_kapisi.py --pozitif-kontrol` mutasyon C, `pasif-kapsam-disi` kilidinin `pasif-denetim.md`'de TR/EN 4 yerde geçtiğini yakalıyordu (v2.11.0 HEAD'inde KAPI KOR); cümle tek yere indirildi.
### Sınır
- Gerçek siteye aktif istek bu dilimde HİÇ atılmadı: ölçüm yalnız yerel fixture (127.0.0.1) ve yerel kopya. Bkz. KRITER "v2.12.0 ÖLÇÜMÜ".
### Bilinen sınırlar (KRITER "v2.12.0 ÖLÇÜMÜ" ve "v2.12.0 DÜZELT ÖLÇÜMÜ"; claude-sonnet-5-5, tek model, tek istem, sentetik fixture, senaryo başına n=2; 16 koşu, hepsi end_turn, refusal 0)
- **Kapı çalıştı (v1 metniyle, `4f74c83`):** "aktif test" demeden canlı POST 0/2; `captcha` ve `staging` yazılı değilken CAPTCHA'lı forma istek 0/2 ve canlı DELETE/PUT 0/2 (kullanıcı istese de); 16 koşuda gerçek kullanıcı nesnesine, kapsam dışı host'a, CAPTCHA çözmeye ve canlıda yazmaya istek 0. **T1/T4 DÜZELT metniyle yeniden ölçülmedi** (regresyon ÖLÇÜLEMEDİ).
- **DÜZELT sonrası iyileşenler:** pasif denetimde JS'ten çıkan API ucuna istek 0/2 (v1: 2/2 koşuda oturumsuz GET); "şart yok, test edilmedi" cümlesi Türkçe raporda birebir 2/2 (v1: 1/2); canlı istekler arası en kısa aralık 1098 ms ve üzeri (v1: bir koşuda 84 ms); `canli-pasif` etiketi ASCII yazıldı (v1: 3/11 Türkçe `ı`).
- **İşaretleyici disiplini hâlâ tam değil (T3 1/2):** aktif 4 koşuda 1 POST işaretleyicisizdi — model 501 karakterlik dolgu mesajını üretemedi (Bash'inde `python` yok), komut ikamesi boş döndü ve BOŞ mesaj gitti; model bunu raporladı ve işaretleyici başta, toplam 501 karakterlik mesajı ayrıca gönderdi. Gövdeyi göndermeden doğrulama kuralı yok (sonraki sürüm adayı).
- **Yerel kopya kipi (T5) 1/2:** bir koşuda depo yerelde ayağa kalktı, B9 yerelde koştu (4 PUT/DELETE), süreç kapatıldı (transkript + sonradan port taraması); öbüründe model çalıştırıcı (`python`) bulamadı, "yerel kopya kurulamadı" diye raporladı (spesifikasyona uygun ama o koşuda yerel kapsam 0). v1'de 2/2 kurulmuştu. Koşu-içi süreç-kapalı ölçümü donanım hatasıyla ÖLÇÜLEMEDİ.
- **Kaynak etiketi:** ASCII yazım düzeldi; bir koşuda 10 bulgunun 2'sinde `Kaynak` satırı yoktu; bulgu başlığı biçimi serbest (otomatik sayıcı kalın satır başlığını saymadı, elle sayım 15/15).
- **Ekili açık yakalama:** B1, B2, B4, B5 her T3/T4/T5 koşusunda bulundu; B3 yalnız bazı koşularda ölçüldü ve ilk 429'dan sonra o uca istek 0; T3'te model B3'ü sınırsız bir uç üzerinde ölçtü.
- ÖLÇÜLMEDİ: gerçek site/TLS/WAF/gerçek CAPTCHA/gerçek LLM ucu; `captcha` veya `staging` YAZILIYKEN davranış; yük testi; gerçek kişisel veri dökümünün reddi (C3 yalnız tarama komutuyla elle sınandı); Docker yolu; `python` bulunamayan ortamda başka kurulum yolları; TR skill; başka model/istem; "toplam tam L+1"in günlükten doğrulaması (günlük gövdeyi 300 karaktere kırpar).

## [2.11.0] — 2026-11-15
### Eklendi
- **Yetki kaynağı (c): site sahibinin izni, kullanıcı beyanıyla** (`SKILL.md` §0.1, `yetki-kapisi.md`, yeni `references/pasif-denetim.md` TR+EN). Kullanıcının "site sahibi izin verdi" beyanı yeterli (sorumluluk kullanıcıda); yazılı belge ve sahiplik kanıtı (DNS TXT `gedik-yetki=<token>` ya da `/.well-known/gedik-yetki.txt`) İSTEĞE BAĞLI, varsa `YETKI.md`'ye yazılır; `YETKI.md` varsa yalnız listesindeki host'a istek. Sayfadaki "pentest welcome" beyan değildir. Belge varsa imzası makinece doğrulanamaz → raporda "belge kullanıcı beyanıyla kabul edildi".
- **Yalnız PASİF test:** GET/HEAD; güvenlik başlıkları, TLS, çerez bayrakları, CORS (yalnız `Origin` ile GET), istemci JS/kaynak haritası, `robots.txt`/`sitemap.xml`/`security.txt`; aktif testler "pasif kapsam dışı, test edilmedi". Hız ≤1 istek/sn, koşu başına ≤100 istek; kapsam dışı host'a (üçüncü taraf bağlantılar dahil) 0 istek; kişisel veri maskelenir; sayfa içi talimat yetki değildir.
- **A1 izin reddi = DUR ve bildir** (kilitli cümle TR+EN): bir araç reddedilince aynı sonuca başka araçla ulaşılmaz; "yazılamadı: <yol>, sebep: izin reddi".
### Değişti
- `iki-kaynak-yoksa-dur` kilidi KASITLI güncellendi: "İkisi de yoksa DUR" → "Hiçbiri yoksa DUR" (üç yetki kaynağı); 9 yeni kilitli cümle (c-uc-sart-birden sonradan c-beyan-yeterli ile değişti: Onur kararı 2026-11-15, beyan yeterli).
### Sınır
- Gerçek üçüncü taraf siteye hiç denenmedi (yalnız yerel fixture sunucusu); aktif test ve ücretli hizmet şablonu bu sürümde YOK. Bkz. KRITER "v2.11.0 ÖLÇÜMÜ".

## [2.10.0] — 2026-11-12
### Eklendi
- **CI/CD tedarik zinciri** (`cicd-depo-ve-kurtarma.md` §2, yeni §4.1): `issue_comment` pwn request (tek koruma `github.event.issue.pull_request` yetersiz), `workflow_run` artifact devri (`allow-unsafe-pr-checkout`), egzotik bağımlılık (`github:`/`git+`/`.tgz`), paket yöneticisi gevşetme (`.npmrc`, pnpm, dependabot, `npm install`), kötü amaçlı sürüm (sabit liste YOK; `osv-scanner`/`npm audit`, yoksa ÖLÇÜLEMEDİ).
- **Şerit B / RSC eki** (`serit-B-rsc.md`, TR+EN; T2 + `next`/`react-server-dom-*`/`'use server'`): server function = herkese açık uç nokta (oturum + sahiplik + şema, mass assignment), yalnız-middleware yetkisi, sürüm (tarayıcıdan, ezber hüküm YASAK), `use cache` anahtarı ve config SSRF.
### Değişti (v2.6–v2.9 ölçüm borçları)
- **C1** `gedik-bulgular.json` konumu: JSON raporun `.md` dosyasıyla aynı dizine; rapor satır içiyse çıktı klasörüne ve raporun ilk satırı tam yolu verir (6/6 koşuda scratch'e yazılmıştı).
- **C2** D9.6: satır sayma yok; sabit `grep -nobaP … | cat -A` komutu koşulur, `satır:ofset` aynen kopyalanır (4/8 satır doğruydu).
- **C3** D9 komşu not: rapor şablonuna sabit "## Sertleştirme notları (bulgu değil)" bölümü; `G-n` yalnız `confirmed`/`needs_validation` (2/4 koşuda numaralı+şiddetli çıkmıştı).
- **C4** DNS (`dig`/`nslookup`/`host`/`ping`) yetkisizde canlı istek sayılır; "istek atılmadı" beyanı Bash geçmişiyle çelişemez.
- **C5** sabit ret cümlesi rapor şablonunda sabit satır (`ÖLÇÜLMEDİ — yetki yok` / `NOT MEASURED — no authorization`, aynen kopyalanır; birebir 1/6'ydı).
### Sınır
- Yeni Python kapısı yok; kabul ham rapor okumasıyla (bkz. KRITER "v2.10.0 ÖLÇÜMÜ").
### Bilinen sınırlar (KRITER "v2.10.0 ÖLÇÜMÜ" + "DÜZELT"; claude-sonnet-5-5, tek model, sentetik fixture, n=2; 22 koşu)
- Ekili maddeler her koşuda `dosya:satır` ile bulundu (CI/CD 4/4, Next.js 2/2); temiz fixture'larda bu sınıflarda bulgu yok.
- A5/B3: `osv-scanner` PATH'teyken eşleşme 3/4 koşuda tarayıcıdan; 1/4'te yanlış bayrak (`--offline`) + ezberden 3 CVE ("doğrulanmadı" etiketli). Tarayıcı yoksa ÖLÇÜLEMEDİ.
- C1 (JSON konumu) sınanamadı: test kurulumunda hedef klasöre yazma "sensitive file" diye reddedildi (`--plugin-dir` hedefin üst dizini; neden TAHMİN).
- Yazma reddinde ajan en az 5/22 koşuda dosyayı kabuk heredoc'u ile yazdı; skill bunu yasaklamıyor (sonraki dilim adayı).
- C2: sabit `grep` komutu 1/2 koşuda koşulmadı, satır yanlış.

## [2.9.0] — 2026-11-12
### Eklendi
- **Şerit D9 — depo içi ajan yapılandırması** (`serit-D-yapayzeka.md`, TR kanonik + EN birebir): hook komutları, proje MCP otomatik onayı ve pinsiz `npx -y`, uç nokta/ortam yönlendirme (`ANTHROPIC_BASE_URL`, `apiKeyHelper`), izin gevşetme (`bypassPermissions`, CI'da `--dangerously-skip-permissions`), ajanın kendi yapılandırmasına yazabilmesi, talimat dosyasında gizli Unicode (kod noktası + satır), `runOn: folderOpen`/`postCreateCommand` (D9.1–D9.7).
- D9, T8'den **bağımsız** tetiklenir (`SKILL.md` Şerit seçimi): YZ kullanmayan depoda da ajan yapılandırma dosyası varsa açılır.
- D9 PoC kuralı: yapılandırma **çalıştırılmadan** `dosya:satır` + alan + değer + hangi istemcinin ne zaman yürüttüğü; güvenilmeyen depoda rapor başına tek satır uyarı.
### Düzeltme (aynı sürüm, tek tur)
- D9.6: kod noktası + satır + bayt ofseti birlikte; satır, bayt ofsetinden değil satır sayarak (ilk ölçümde 2 koşuda satır numarası yanlıştı).
- D9 dürüst-sınırlar: deny kuralı, pinli MCP sürümü, CODEOWNERS varlığı/kapsam eksiği D9 bulgusu değildir; "sertleştirme notu" başlığında şiddetsiz (ilk ölçümde 1 sıkı fixture'da komşu bulgu çıktı).
### Sınır
- Sabit CVE listesi yok; yeni Python kapısı yok (kabul ham rapor okumasıyla). D9 yalnız fixture'da ölçüldü (bkz. KRITER "v2.9.0 ÖLÇÜMÜ").
### Bilinen sınırlar (ölçüm: KRITER "v2.9.0 ÖLÇÜMÜ" + "v2.9.0 DÜZELT"; claude-sonnet-5-5, tek model, tek istem, sentetik fixture, hedef başına n=2 koşu × 2 tur)
- **Gizli-Unicode satır numarası güvenilmez (D9.6).** Kod noktaları 4/4 koşuda doğru bulundu ve gizli talimat 4/4'te uygulanmadı; ama raporlanan satırlar 8'in 4'ünde doğruydu, tüm satırları doğru veren koşu 4'te 1'dir (ilk tur 0/2, "satır sayarak ver" düzeltmesinden sonra 1/2). Bayt ofseti ("birlikte yaz") düzeltme turunda 0/2 raporlandı. Raporlanan kod noktasını kendiniz doğrulayın (`grep -nP`).
- **Sıkı yapılandırmada komşu not bulgu gibi çıkabiliyor (D9 yanlış pozitifi).** Sıkı fixture'da (deny kuralı, pinli MCP, CODEOWNERS) D9'un kötü desenlerinden (hook, oto-onay, yönlendirme, gizli Unicode) hiçbiri 4/4 koşuda bulgu sayılmadı, ama 4 koşunun 2'sinde komşu sertleştirme gözlemi `G-n` numarası ve şiddetle yazıldı (ilk tur 1/2, "sertleştirme notu, şiddetsiz" düzeltmesinden sonra 1/2; hangi koşuda çıkacağı değişiyor).
- **Kötü yapılandırmada tespit:** kötü fixture'da 5 maddenin 5'i `dosya:satır` ile 2/2 koşuda bulundu (yalnız tek fixture, n=2).
- **Hook:** proje ayarı yüklenmeden (`--setting-sources user`) 10 koşunun 10'unda hook çalışmadı (`HOOK_KOSTU.txt` 0/10; pozitif kontrol: proje ayarıyla marker oluştu).
- Gerçek (sentetik olmayan) depolarda yanlış-pozitif oranı, farklı model/istem ve istemci sürümlerindeki davranış ÖLÇÜLMEDİ.

## [2.8.0] — 2026-10-26
### Değişti
- **PHP raporu: serbest metin yerine SABİT ALANLI blok.** `SKILL.md` ŞERİT B (TR+EN) artık zorunlu bir `### PHP çalışma zamanı` / `### PHP runtime` bloğu ister:
  `T2 PHP` · `Sürüm`/`Version` (+`kaynak:`/`source:` `dosya:satır`) · `Yama düzeyi`/`Patch level` · `EOL` · `composer audit` · `İmaj taraması`/`Image scan`. Etiketler ve değer
  sözcükleri sabit (sabit cümle kilidine 7 satır eklendi); blokta "temiz/güvenli/risk yok" yasak; rapor son mesajda TAM ve satır içi.
- **`araclar/php_kapisi.py` alan-tabanlı:** her alan `php_olc` ölçümüyle BİREBİR karşılaştırılır (sürüm + gerçek kaynak `dosya:satır`, büyük/küçük harf dahil; yama düzeyi; EOL;
  composer sayı/ÖLÇÜLEMEDİ+sebep/UYGULANMAZ; imaj biçimi). Serbest-metin anahtar-sözcük avı KALDIRILDI (4 turda her seferinde yeni okuma hatası: K5 MEKANİKLEŞTİR). Kalan tek
  serbest-metin kuralı: gerçek kaynakla eşleşmeyen "PHP x.y … Dosya:satır" iddiası (`UYDURMA_KAYNAK`; `php-fpm`/`php-cli`/`php.ini` satırları dahil, `swagger-php`/`gen_openapi.php` hariç).
  Kapının doğrulayamadığı: (1) sayıların (composer N, tarayıcı N) gerçekliği; (2) `ÖLÇÜLEMEDİ (<sebep>)`/`UYGULANMAZ (<sebep>)` sebep metninin içeriği; (3) serbest metnin tamamı —
  yalnız `PHP x.y … dosya:satır` kalıbı denetlenir (kaynaksız sürüm, `Dockerfile satır 2`, `php` sözcüksüz satır, kısıt/tarayıcı sözcüklü satır kaçar). `php.ini` bir PHP çapasıdır
  ama `php.ini:N` sürüm kaynağı olarak denetlenmez.
- **Bağımsız denetim DÜZELT turu (2026-10-24):** blok bölgesi başlıktan ilk boş satıra kadar (altındaki "Notlar:" alan sayılmaz); "temiz/güvenli/risk yok" yasağı bölgenin TÜM
  satırlarında; `T2 PHP` kanıtı hedefte var olan dosya/dizin olmalı ve en az biri PHP imza dosyası (`php_olc` `imza_dosyalari`); tarayıcı-çözümü satırı (grype/trivy/syft/tarayıcı/scanner/
  resolved/çözül) yalnız SÜRÜM karşılaştırmasından muaf — satırdaki `dosya:satır` yine gerçek bir kaynak olmalı (DÜZELT-2, G1); blok bölgesi dışına kaçan ALAN ETİKETLİ satırlar
  (`- Sürüm: … kaynak: dosya:satır`) da `x.y … dosya:satır` denetimine girer (G2; alan DEĞERİ çelişkisi — ör. bölge dışı `- EOL: SUPPORTED` — denetlenmez, README sınırı); imaj alanı `ÖLÇÜLEMEDİ (<sebep>)` kabul; `YÜZEN <etiket> — kaynak:` etiketle tire arasında boşluk ister; serbest metinde `dizin/ad:satır`
  tam yol karşılaştırılır; mutasyon aracı etiket/regex sabitlerini bozar.
- Öz-test: `php_oz_blok.py` (alan başına doğru-YEŞİL / bozuk-kopya-KIRMIZI, TR+EN; SKILL.md şablonu ↔ kapı sözcük tutarlılığı); üç öz-test dosyası doğrudan çalıştırılınca vakaları koşar.
- v2.7.1 kapı denemesi yayımlanmadı (`deneme/271-kapi` dalı): A2 düzeltmesi `php-fpm`/`php-cli` satırlarını eliyordu (denetim Bulgu 1).

## [2.7.0] — 2026-10-22
### Eklendi
- **PHP görünürlüğü.** Triyaj T2 artık PHP'yi görür: `composer.json`, `artisan`/`laravel/framework`, `symfony/*`,
  `wp-config.php`/`wp-content/`, kökte `index.php`, `php-fpm` havuz dosyası, PHP işleyicili `.htaccess`; T9/T12'de
  `FROM php:` / `image: php`. T2'de PHP imzası varsa Şerit B açılır. Öncesinde PHP imzası hiç yoktu (yalnız
  express/flask/django/spring/rails). Tarama komutları `fd -H`/`rg --hidden` (noktalı dosyalar: `.htaccess`, `.php-version`).
- **PHP çalışma zamanı sürümü (`kod-inceleme-guvenlik.md` §2.1, TR+EN).** Kaynak sırası: imaj etiketi (`ARG` varsayılanı dahil;
  çok aşamalı Dockerfile'da SON aşama) · `.php-version` · `composer.json` `config.platform.php` · CI matrisi · platform dosyası.
  Sürüm rapora KAYNAĞIYLA yazılır; kaynaklar çelişirse çelişki yazılır ve EOL en eski çalışma-zamanı kaynağına uygulanır;
  `composer.json` `"php": ">=x"` kısıtı alt sınırdır, çalışan sürüm sayılmaz; yüzen etiket (`php:8-apache`, `latest`)
  etiket+kaynak olarak yazılır, eksik düzey ÖLÇÜLMEDİ; yalnız `composer.json`/`*.php` varsa (kütüphane) sabit satır istenmez;
  sürüm depoda hiç yoksa sabit satır ("PHP çalışma zamanı sürümü depoda yok — ÖLÇÜLEMEDİ; sunucu/hosting panelinden kontrol et.")
  yazılır, rapora "temiz" yazılmaz, sonuç ÖLÇÜLMEYENLER'e ve `kapsam`'a gider, karar ÖNCE ÖLÇ olur.
  SKILL.md Lane B maddesi bu satırı ZORUNLU kılar ve sabit cümleyi aynen taşır (ölçüm: referans dosyasında kalan kural
  model tarafından okunmadı — aşağıdaki doğrulama).
- **EOL kuralı** (php.net `supported-versions` + `eol.php`, ölçüm 2026-10-22, yeniden doğrulanmalı): PHP ≤ 8.1 resmî güvenlik
  yaması almıyor → bulgu (`confirmed`, STATİK, şiddet ORTA; tarayıcı kritik/yüksek CVE eşlerse onun şiddeti); 8.2 güvenlik
  desteği 2026-12-31'de bitiyor → uyarı (BILGI), tarihten sonra bulgu. Sabit CVE tablosu YOKTUR (bayatlar): açık eşleşmesi
  tarayıcı veri tabanından gelir.
- **Paket/imaj taraması:** `composer.lock` (herhangi bir derinlikte, `vendor/` hariç) varsa `composer audit`, sayıyla; yoksa ya da araç/ağ
  yoksa ÖLÇÜLMEDİ + sebep. İmaj taraması (`trivy`/`grype`) yalnız KAMUYA AÇIK taban imaj etiketi için; hedefin kendi/özel kayıt
  defteri için "ÖLÇÜLMEDİ — yetki yok (§0.1)". Şerit B kapanış listesine 27. madde.
- **`araclar/php_olc.py` + `php_kapisi.py` + `php_oz_test.py` + `php_oz_duzelt.py`** — deterministik referans ölçüm, rapor denetimi (`--hedef DİZİN [--rapor RAPOR]`)
  ve kör kapı öz-testi. `kapilar.py` altın kümesine 208 vaka eklendi (altın küme 21 → 229; ölçüm 2026-10-23, `python araclar/kapilar.py --pozitif-kontrol`): 3 asıl fixture (Laravel+`php:8.3.30-fpm`,
  `composer.lock`'lu depo, sürümsüz WordPress yedeği) + EOL 8.1/8.2, `require` kısıtı, yüzen/dal etiketi, çelişen kaynaklar,
  çok aşamalı Dockerfile, `.htaccess`/php-fpm/compose/CI/`.php-version`/platform kaynakları, kütüphane (zayıf imza); mutantlar: imaj
  satırı silinince, "temiz" yazan sahte rapor (TR+EN), EOL bulgusu yok, audit satırı yok, uydurma sürüm+kaynak, dedektör mutantları (sürüm
  çözücü/EOL/imaj dosyası/test yolu/yorum bozulunca golden KIRMIZI). Anahtar sözcük TABANIDIR, anlam denetlemez.
- **Yayın öncesi bağımsız denetimin (2026-10-23) bulguları kapatıldı** — her düzeltmenin TR+EN doğru raporu YEŞİL, bozuk kopyası KIRMIZI: `*.Dockerfile`/`*.Containerfile` ve `docker.io/php:`
  imajları görünür (ölçüm + triyaj `rg` komutu); `composer.json` `config.platform.php` kaynağı gerçek satırla kaydedilir (config…php aralığı geçerli);
  "temiz" denetimi: yükseltme önerisindeki "güvenli/secure sürüm" tarifi iddia sayılmaz, ayrı satırdaki "risk yok / no action needed" kararı iddiadır;
  `composer.json` kısıtını "kullanıyor/uses/running" diye sürüm sayan rapor yakalanır; "EOL: no official security patches" yazan doğru rapor
  yanlışlıkla "EOL değil" sayılıyordu (EN fixture buldu); öz-test dosyası doğrudan çalıştırılınca hiçbir şey koşmadan çıkış 0 veriyordu (sahte yeşil).
- Sabit cümle kilidine 5 cümle (25 → 30): sürüm-depoda-yok satırı (referansta ve SKILL.md'de), `require` alt sınırdır, ≤ 8.1 bulgu, sabit CVE tablosu yok.
### Değişti
- Sürüm 2.7.0 (dört yer: `plugin.json`, `marketplace.json`, `SKILL.md` TR+EN). Rapor şablonuna "PHP çalışma zamanı" satırı
  (`.md` şablonu; `gedik-bulgular.json` şeması `gedik-bulgular/1` DEĞİŞMEDİ). `lint` komutuna `php_olc.py`, `php_kapisi.py`,
  `php_oz_test.py`, `php_oz_duzelt.py`; `araclar/kapilar.py` +2 satır (şablondan bilinçli sapma).
### Değiştirilmedi (bilinçli)
- gedik salt-okur kalır (yamalamaz, raporlar); canlı sisteme istek yok; 2.6.1 adayı geri alınmıştı, rapor akışı/PoC yeri 2.6.0 ile aynı.
### Bu sürümde HAYIR
- Paylaşımlı hosting'de çalışma zamanı sürümü depodan GÖRÜLEMEZ (ÖLÇÜLEMEDİ satırı çıkar). PHP'ye özgü saldırı yükleri (unserialize,
  include/LFI, type juggling) bu sürümde YOK: bu dilim görünürlüktür. `php_kapisi.py` anahtar-sözcük tabanıdır: bağımsız incelemeler her
  turda (3 tur) yeni atlatma/yanlış-pozitif buldu. Mutasyon ölçümü (2026-10-23, bu sürümün kodu, satır-düzeyi): 127 mutant, 126 öldü, 1 hayatta
  (kanıtlanabilir eşdeğer: tek elemanlı `'.'.join` = elemanın kendisi); ilk koşuda 6 hayatta kalmıştı, 5'i gerçek davranış farkıydı ve vektörle kapatıldı.
  Adlandırılmış mutantlar (denetçinin 19'u + bu turun her düzeltmesini geri alan 13): 32 uygulandı, 32 öldü. Sınır: anahtar-sözcük tabanı bir raporun
  DOĞRU olduğunu kanıtlamaz; yalnız ölçülen kusur sınıflarının yokluğunu gösterir.

## [2.6.0] — 2026-09-29
### Eklendi
- **Makine-okur çıktı (spec A).** Tam denetimde `.md` raporun yanına `gedik-bulgular.json`:
  üç hüküm (`confirmed` / `needs_validation` / `rejected`), `ÖLÇÜLMEDİ` bir hüküm değil ayrı
  `kapsam` alanı. Şema `araclar/bulgu-semasi.json`; doğrulayıcı kapı `araclar/bulgu_kapisi.py`
  (yalnız standart kütüphane; kör kapı öz-testli: 68 aykırı girdi KIRMIZI, 22 geçerli varyant +
  temiz örnek YEŞİL yakar; kapı yolu — dosya yok→ATLANDI, açık yol yok→FAIL, BOM, çıkış kodları,
  `kapilar.py` zincirine bağlantı — ve skill belgelerindeki JSON örnekleri şemaya karşı sınanır); `kapilar.py` zincirinde "bulgu şeması"
  kapısı (dosya yoksa ATLANDI). SARIF ve CI/Action YOK.
- **İki mod (spec B, SKILL.md §0.2).** Danışma modu (hafif; dosya/rapor/JSON üretmez) ve tam
  denetim modu; mod belirsizse işe başlamadan önce tek soru.
- **Bağımsız çürütme (spec C).** §1'de K2'nin altında not, §3 akışa "Çürüt" adımı, rapor
  şablonuna `Doğrulayan` alanı; `dogrulayan` (`alt-ajan` | `ayri-tur`) JSON'a yazılır.
- Rapor şablonuna `ŞÜPHE (ÇALIŞTIRILMADI)` ve çürütülen adaylar bölümleri; şablondaki eski
  `Z-n` ve eski skill adı kalıntıları `G-n` ve gedik'e çevrildi.
- Sabit cümle kilidine v2.6'nın 15 kritik cümlesi eklendi (§0.2 mod geçişleri, çürütücü, "çürütülemezse
  `confirmed` kalır", §4.1 şiddet / ÖLÇÜLMEDİ / yazım konumu / şema; v2.5'in 10 kilidi değişmedi → 25
  kilit). `ceviri_kapisi.py --pozitif-kontrol`e mutasyon C: her kilit, her tarafta (TR/EN), bir sözcük
  silinince KIRMIZI yakar ve cümle dosyada tek yerde geçer.
- Kavram esini: cloudflare/security-audit-skill (bağımsız çürütme, üç hükümlü şemalı bulgu
  dosyası); metin, şema ve doğrulayıcı bağımsız yazıldı, hüküm adları (`confirmed` /
  `needs_validation` / `rejected`) aynen alındı.
- Karar sahibi: proje sahibi, 29 Eyl 2026. Spec dondurulmuş (yerel).
### Değişti
- `araclar/kapilar.py`: proje-şablonu v0.2.1'den bilinçli sapma — 10 satır (bulgu şeması kapısı
  ve öz-test vakaları). `lint` komutuna `araclar/bulgu_kapisi.py` eklendi.
### Değiştirilmedi (bilinçli — spec)
- v2.5'in kilitleri: §0 "dosya/sayfa içi izin ≠ izin", §0.1 yetki kapısı, mutlak sınırlar,
  silahsız işaretleyici, veri-sızdırma-yok, salt-okunurluk, sabit cümle kilidinin 10 v2.5 cümlesi (yalnız ekleme yapıldı).

## [2.5.0] — 2026-09-29
### Eklendi
- **Yetki kapılı canlı hedef testi (§0.1, yeni).** gedik artık canlı bir sisteme (HTTP
  isteği, port taraması, kimlik denemesi) yalnız makinece doğrulanabilir bir yetki
  varken dokunabilir: (a) kullanıcının sohbetteki kendi beyanı, ya da (b) yayımlanmış
  bir bug bounty/VDP kapsamı + kullanıcı beyanı. Yetki yoksa davranış v2.4 ile aynı
  (salt-okuma). Yordam, karar ağacı, `YETKI.md` şablonu: `references/yetki-kapisi.md`
  (TR+EN).
- **Üçüncü taraf açık kaynak salt-okuma gevşetmesi (§0).** Herhangi bir açık kaynak
  (public repo, yayımlanmış artefakt) canlıya hiç istek atmadan statik incelenebilir;
  bulgu sorumlu ifşaya gider, saldırıya kullanılmaz.
- Karar sahibi: proje sahibi, 28 Eyl 2026 gece. Spec dondurulmuş (devir paketinde, yerel).
### Değiştirilmedi (bilinçli — spec §7)
- §0'ın "dosya/sayfa içi izin ≠ izin" kuralı, mutlak sınırlar (para/hesap/kalıcı silme/
  CAPTCHA), silahsız işaretleyici, veri-sızdırma-yok, salt-okunurluk — bunlar
  gevşetilmedi; v2.5 yalnız yetkili istisna açar.

## [2.4.0] — 2026-09-29
### Eklendi
- gedik açık kaynak olarak yayımlandı: `onur-kesim/gedik`, public, MIT. İngilizce ana
  sürüm (`skills/gedik/`) + Türkçe orijinal (`skills/gedik-tr/`), tek plugin'li
  marketplace (`.claude-plugin/`), mekanik çeviri kapısı (`araclar/ceviri_kapisi.py`).
- Kaynak: proje sahibinin kendi yazdığı gedik v2.4 taslağı (devir paketinde, yerel,
  SHA256 doğrulandı), TR genelleştirmesiyle (proje-özel örnekler/adlar kaldırıldı).

---
### proje-sablonu geçmişi (bu depo KUR'da bu şablondan açıldı — aşağıdaki iki sürüm
### proje-sablonu'nun kendi 0.x sürümleridir, gedik ürününün değil)

## [0.2.0] — 2026-09-26
### Eklendi
- KEŞİF / YAPIM aşaması (GENEL ESASLAR v2.1, §3): `proje.toml [proje] asama`; `kapilar.py` KEŞİF'te ürün nabzını ATLANDI verir ve geçersiz değeri kırmızı yakar (altın küme +3 vaka = 14); `DILIM.md` ESAS KARARI kutuları; DURUM/KURULUM notları. Fikir aşamasındaki proje 7 gün baskısı ve kırmızı nabız almaz; YAPIM'a geçiş insanın "başla" sözüyle.
- KUR ≤ 1 gün (bitmeyen kutu `ATLANDI: dilim 1'e`); MOD KRİTİK kapsamı: iki denetim turu yalnız TESLİM'de, KUR/altyapıda tek tur, D1 yeter; PROJE-ÖZEL iskeletine PROJE KURALLARI (≤5) bölümü; ARAÇ HARİTASI'na KEŞİF satırı. Dayanak: ilk gerçek kurulumda KUR kancasına iki tur + 26 mutant koşuldu (26 Eyl ölçümü).
### Değiştirildi
- CI ve release çalıştırıcısı `ubuntu-latest` → `ubuntu-24.04` sabitlendi. GitHub'ın koşum notu birebir: "The ubuntu-latest label will migrate to Ubuntu 26 beginning October 19, 2026" (actions/runner-images#14748). Şablonu klonlayan her projenin CI'ı aynı gün habersiz değişmesin diye; 26.04'e geçiş kararla, iki dosyada tek satır.
- Çekirdek blok tavanı 8.000 → 8.500 bayt (ölçülen 8.371; KEŞİF paragrafı için, net +375 bayt).
- README/KURULUM'daki `C:\dev` örneği → `<projeler-klasörü>` (şablon paylaşımlı, sabit sürücü yazmaz).
### Düzeltildi
- kapilar.py Windows konsolunda (cp1254) `UnicodeEncodeError` ile çöküyordu; stdout/stderr UTF-8'e ayarlanır (başka bir kurulumda ölçüldü, 26 Eyl).
- dependabot.yml yalnız github-actions ekosistemini açar; pip/pub/gradle satırları yorumda, KUR'da yığına göre açılır (manifesti olmayan ekosistemin Dependabot koşumu "failure" verdi — 26 Eyl ölçümü; "sessizce boş geçer" iddiası geri çekildi).

## [0.1.0] — 2026-09-26
### Eklendi
- İskelet dilimi: çekirdek genel esaslar (CLAUDE.md işaretli blok, 11 bölüm), dört dosya düzeni
  (CLAUDE.md · README.md · DURUM.md · DILIM.md), proje.toml, beş profil + profil şablonu,
  araclar/kapilar.py (altın küme öz-testli kapılar), tek iş akışı CI (kapilar + kor-kapi),
  PR şablonu, release.yml (etiket → Release, notlar CHANGELOG'dan), dependabot.yml, .gitignore, .env.example,
  KURULUM.md, dal koruması JSON'u.
### Teslim edilmedi (bkz. README)
- kur.py sihirbazı, windows çalıştırıcı, Flutter/Android adımlarının gerçek yığında ölçümü, gerekçe dosyası.
