# CHANGELOG
Biçim: Keep a Changelog. Her git etiketi bir bölüm; [Unreleased] altı bir sonraki etiketi bekler.
Sürüm numarası `.claude-plugin/plugin.json`'daki gedik ürün sürümüdür (proje-sablonu'nun
kendi 0.x geçmişi — KUR öncesi, aşağıda — ile karıştırılmaz).

## [Unreleased]

### Belgeler
- **Benchmark güncellemesi (2026-10-01).** README×2: Hedef 1 (NodeGoat) tespit 17/17, yanlış pozitif 0; rapor teslimi Cyber Verification Program onaylı hesapta 3/3, onaysız 2/6 (nedensellik kanıtsız, n=3). Bu satır 2.6.0 dönemine aittir.

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
