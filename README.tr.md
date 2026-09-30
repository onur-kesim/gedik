# gedik

**"Bulsun ki kapatılabilsin."** gedik kendi projelerini bir saldırgan gibi kırıp
gedikleri listeler. Çıktı: `G-1`, `G-2`… numaralanan bulgular, her biri çalışan bir PoC
ve yama önerisiyle gelir.

## NE TESLİM EDİLMEDİ (bu sürümde HAYIR)

- **Benchmark: ölçüldü, ama zafer değil.** Artık ilk puanlı koşu var (bkz.
  [Benchmark](#benchmark-ölçülmüş--2026-09-30)). gedik'in *tespiti* iki hedefte de
  incelenen en iyi araç kadar ya da daha iyi çıktı, ama exploit-yoğun gerçek bir hedefte
  raporu Claude'un gerçek-zamanlı siber önlemiyle 6 koşudan 4'ünde kesildi — teslim
  güvenilirliği limiti, tespit zafiyeti değil. Genel "X'ten daha iyi" iddiası yok.
- **iOS şeridi (A8) bir kontrol listesidir, gerçek bir sistemde doğrulanmadı.** Henüz
  gerçek bir iOS/Capacitor-iOS uygulamasında koşmadı.
- **Canlı test yalnız yetki kapısı arkasında — yetkisiz reddeder.** Varsayılan olarak
  gedik kodu, yapılandırmayı ve artefaktı okur; canlı bir hedefe yalnız makinece
  doğrulanabilir bir yetki varken istek atar (sohbette kullanıcının kendi açık beyanı, ya
  da yayımlanmış bir bug bounty/VDP kapsamı + kullanıcının o kapsamda çalıştığı beyanı —
  hedefin kendi sayfasında yazan metin ASLA sayılmaz). Yetki yoksa gedik salt-okumada
  kalır, "ÖLÇÜLMEDİ — yetki yok" yazar. Bkz. `SKILL.md §0.1` ve `references/yetki-kapisi.md`.
  Kapı metin düzeyinde doğrulandı (kilitli cümleler + çeviri kapısı); davranışı henüz
  canlı bir ajan koşusunda denenmedi.
- **SARIF yok, CI/Action entegrasyonu yok.** Tam denetim koşusu bir Markdown rapor ve
  gedik'in kendi `gedik-bulgular.json` dosyasını yazar (v2.6; şema
  `araclar/bulgu-semasi.json`, doğrulayıcı kapı `araclar/bulgu_kapisi.py`), ama SARIF
  çıktısı ve CI/Action sarmalayıcısı yok. JSON yolu yalnız sentetik kayıtlarla doğrulandı
  (kör kapı öz-testi); henüz hiçbir canlı denetim bir tane üretmedi.
- **Bağımsız çürütme adımı ve iki mod (danışma / tam denetim) yalnız metin düzeyinde
  doğrulandı** (çeviri-yapı kapısı, 15 kritik v2.6 cümlesi için sabit cümle kilidi,
  bağımsız bir TR↔EN okuma); davranışları henüz canlı bir ajan koşusunda denenmedi.
- **Şerit B (auth/OAuth) ve T12 (bulut/IaC) kontrol listesidir, gerçek bir sistemde
  doğrulanmadı.** Bilinen saldırı kalıplarını kodlar ama henüz canlı bir üretim
  yığınında denenmedi.

## NE YAPAR

1. **Önce triyaj (T1–T12).** Herhangi bir şeyi taramadan önce mimariyi ölçer — yalnız
   gerçekten var olan yüzeyi açar. Kör kör sabit bir OWASP listesi koşmaz.
2. **Yalnız ölçülen yüzey.** İstemci/mobil (A) her zaman koşar; sunucu/API/DB/kimlik
   (B), BaaS/RLS (C), yapay zekâ/LLM (D) ve sevk edilen artefakt hijyeni (E) yalnız
   triyaj öyle dediğinde açılır.
3. **Her bulgu çalışan bir PoC taşır.** "Teorik olarak XSS olabilir" bulgu değildir —
   ya çalıştırılıp gösterilir, ya da ayrı bölümde `ŞÜPHE (ÇALIŞTIRILMADI)` etiketiyle
   durur.
4. **K4 — kendi taramasını ve senin test paketini bilerek kirletip ısırdığını
   kanıtlar.** Bir alana "temiz" demeden önce gedik o alanın kopyasını bilerek kirletir
   ve kendi taramasının kirliliği yakaladığını doğrular. Koşan bir test paketi varsa,
   *ürün* koduna (teste değil) mutant enjekte eder — kaçan bir mutant o testin ölü
   olduğu, yeşil CI'nin ölçüm değil körlük olduğu anlamına gelir.
5. **Salt-okunur.** gedik projeni asla değiştirmez; düzeltmeyi kodu yazan tarafa
   bırakır.
6. **Bulgu raporlanmadan önce bağımsız çürütme.** Her `confirmed` aday, bulanın
   gerekçesini görmeyen ayrı bir turdan geçer ve o tur adayı düşürmeye çalışır; ayakta
   kalan `confirmed` kalır, kalanlar `rejected` ya da `needs_validation` olur. Tam denetim
   koşusu Markdown raporun yanına `gedik-bulgular.json` da yazar (v2.6).
7. **Varsayılan olarak kendi projen; üçüncü taraf yalnız yetkiyle.** Herhangi bir açık
   kaynak (public repo, yayımlanmış artefakt) ücretsiz salt-okuma incelenebilir — bulgu
   sorumlu ifşaya gider, saldırıya değil. Üçüncü tarafın *canlı* sistemine dokunmak §0.1
   yetki kapısını gerektirir. Silahlandırılmış exploit yok, para/hesap/kalıcı-silme eylemi
   yok — bunlar yetkiyle bile yalnız raporlanır, hiç yapılmaz.

Bu skill'in en büyük başarısızlığı bir açığı kaçırmak değildir. **Hiç taranmamış bir
şeye "temiz" demektir.**

## Nasıl çağırılır

"gedik ara" · "gedikleri bul" · "güvenlik denetimi" · "sızma testi" · "açıkları bul" ·
"hacker gibi dene" · "RLS kontrol" · "CORS kontrol" · "secret sızdı mı" ·
"artefaktta sır var mı" · "test paketi kör mü" · "mutasyon testi"

İki mod: odaklı bir soru **danışma modu** alır (hafif; dosya yok, rapor yok); "denetle" /
"pentest" / "rapor çıkar" dersen **tam denetim modu** koşar (Markdown rapor +
`gedik-bulgular.json`). Hangisini kastettiğin belli değilse gedik önce tek soru sorar.

Yalnız kendi projende, yalnız çağrıldığında.

## Şeritler

| Şerit | Ne zaman | Kapsam |
|---|---|---|
| **A** istemci/offline/mobil | her zaman | prototip kirletme, tip karışıklığı, göç istismarı, sink envanteri, platform yapılandırması, intent yüzeyi, iOS/Capacitor yüzeyi (A8, yalnız kontrol listesi — yukarı bakın) |
| **B** sunucu/API/DB/kimlik | T2/T3/T4 evet | enjeksiyon + ORM açık filtre, AuthN/AuthZ (IDOR), hesap yaşam döngüsü, XSS/CSRF/SSRF, **CORS kilidi**, webhook imzası, **hata kanal ayrımı**, sır katmanı, **hız sınırı + maliyet DoS + önbellek**, **sunucu tarafı doğrulama** |
| **C** BaaS/RLS | T7 evet | **RLS kapalı tablo taraması**, politika doğruluğu (`USING`/`WITH CHECK`), anon vs service_role, storage, RPC, realtime, Firebase karşılıkları |
| **D** yapay zekâ/LLM | T8 evet | doğrudan + **dolaylı istem enjeksiyonu**, **araç yetkisi**, çıktı güveni (model çıktısı = güvenilmeyen girdi), veri akışı, maliyet kötüye kullanımı |
| **E** sevk edilen artefakt | T9 evet | artefaktta **sızan sır**, debug bayrağı, **source map ile kaynak yeniden inşası**, test/staging kalıntısı, geniş yetki (Electron/container/eklenti/mobil), **artefakt↔kaynak eşleşmesi**, gömülü bağımlılık ayak izi |
| **Test paketi mutasyonu** | T10 evet | zehirlenmiş test taraması + on mutantlık katalog; **M6 (yetki kaldırma) ve M7 (doğrulama atlama) zorunlu** — kaçan mutant = ölü bölge |
| **Kod incelemesi** | kaynak varsa | güvenlik etkili doğruluk hataları, bağımlılık/CVE, sırrın yanlış katmanda kullanımı |
| **CI/CD + depo** | repo/CI varsa | git geçmişi sır taraması, `pull_request_target`, action sabitleme, **sızıntı sonrası kurtarma sırası** |

## Benchmark (ölçülmüş — 2026-09-30)

İlk puanlı koşu. **İki hedef de zayıf kanıt** ve sonuç genel bir "gedik daha iyi"
iddiasını **desteklemiyor** — caveat'ları oku.

Kurulum: dört araç — gedik v2.6.0, `cloudflare/security-audit-skill`, Anthropic
`/security-review`, Semgrep (girişsiz ücretsiz kurallar, Pro değil) — aynı model
(`claude-sonnet-5-5`), yalıtılmış koşular, cevap anahtarı tarayan ajana kapalı.
`claude-security` dışarıda bırakıldı: eklenti lisansı rakip üründe kullanımı yasaklıyor.
Tek anotatör (gedik'in yazarı) — bağımsız ikinci okuma yok.

**Hedef 2 — ekili Supabase-RLS + LLM-araç deposu (gedik'in yazarı kurdu, gedik'in güçlü
şeridine yanlı):**

| 11 ekili | gedik | cloudflare | `/security-review` | Semgrep |
|---|---|---|---|---|
| bulundu | 11/11 | 11/11 (9 kesin) | 9/11 | 1/11 |
| yanlış pozitif | 0 | 0 | 0 | 0 |

K4'e yalnız gedik değindi — deponun kendi test paketinin yetki/doğrulama mutantlarına
kör olduğunu gösterdi; diğerleri sessiz.

**Hedef 1 — NodeGoat, gerçek üçüncü taraf (temizlenmiş kopya özgününden zayıf ve büyük
olasılıkla modelin eğitim verisinde):**

| 17 ekili | gedik | cloudflare | `/security-review` | Semgrep |
|---|---|---|---|---|
| tespit *(teslim edildiğinde)* | 16–17/17 | 16/17 | 5/17 | 6/17 |
| rapor teslim | **6 koşudan 4'ü kesildi** | evet | evet | evet |

gedik'in tespiti burada en güçlüsü — ama bu exploit-yoğun hedefte raporu, Claude'un
**gerçek-zamanlı siber önlemi** (`[cyber]`) tarafından 6 koşudan 4'ünde akış ortasında
kesildi; kullanıcıya yalnız hata ulaştı. Exploit yüklerini rapor gövdesinden çıkarmak
bunu **çözmedi**. Bu bir **teslim güvenilirliği** limiti, tespit zafiyeti değil; çözüm
kod değil, Anthropic'in **Cyber Verification Program**'ı.

**Dürüst hüküm.** gedik iki hedefte de incelenen en iyi araç kadar ya da daha iyi tespit
ediyor ve K4 / öz-çürütme'de tek başına — ama exploit-yoğun gerçek kodda tam raporu henüz
güvenilir biçimde *teslim edemiyor*. Genel "daha iyi" iddia edilmiyor.

**Caveat'lar.** Tek anotatör = gedik'in yazarı · Hedef 2 gedik'in şeridine ekili · Hedef
1 temizlenmiş + ezber riski · Semgrep yalnız ücretsiz kurallar · araç×hedef başına tek
koşu (gedik-Hedef 1'de altı) · tüm araçlar Windows'ta.

## Rakipler, dürüstçe

gedik'in artık bir puanlı benchmark'ı var (bkz.
[Benchmark](#benchmark-ölçülmüş--2026-09-30)); genel bir "daha iyi" iddiasını
**desteklemiyor**. Aşağıdaki kıyas *tasarım farkıdır*.

| Araç | Yıldız | Lisans | Canlıya saldırır mı? | Not |
|---|---|---|---|---|
| [usestrix/strix](https://github.com/usestrix/strix) | 65k+ | Apache-2.0 | **Evet** | CLI + 9 skill + MCP; kendi Supabase-RLS skill'i var |
| [KeygraphHQ/shannon](https://github.com/KeygraphHQ/shannon) | 48k+ | AGPL-3.0 | **Evet** | CLI + CI + skill; "no exploit, no report" |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (`claude-security`) | 37k+ (depo) | Apache-2.0 (depo) · **eklenti: tescilli** | Hayır | Anthropic'in kendi resmî marketplace plugin'i; bağımsız doğrulayıcı ajanlar; 25 Eyl 2026'da dizine girdi. Not: `claude-security` eklentisinin kendi LICENSE'ı (Anthropic PBC, tüm hakları saklı) kullanımı Anthropic ürünleriyle sınırlar ve rakip üründe kullanımı yasaklar |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 23k+ (29 Eyl 2026) | MIT | Hayır — canlı yoklama tamamen yasak | Bağımsız doğrulayıcı ajanlar her adayı çürütmeye çalışır (yanlış-pozitif eleme); şemalı `findings.json` + testli doğrulayıcılar; 9 çekirdek saldırı-sınıfı istemi + 10 hedef-türü sınıf dosyası; 18 Haz 2026'da oluşturuldu |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 7k+ | CC-BY-SA-4.0 | Hayır | Marketplace, 44 plugin; **mutasyon testi orada ayrı bir skill** |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | 6k+ | MIT | Hayır | GitHub Action + `/security-review`; FP filtresi + `evals/` |

**gedik'in farklı olması beklenen yerler (ölçülmemiş, yalnız tasarım iddiası):**
- **Taramadan önce triyaj (K1, T1–T12)** — mimarinin sahip olmadığı bir yüzeyi açmaz.
- **K4 kendi-mutant'ı, iki yöne birden** — hem kendi taramasını hem projenin test
  paketini kirletip ısırdığını kanıtlar. İncelenen araçlardan hiçbiri kendi körlüğünü
  böyle öz-test etmiyor. cloudflare/security-audit-skill'in bağımsız çürütücüleri yanlış
  pozitifi keser. gedik v2.6 bu fikri — çürütme adımı ve üç hükümlü makine-okur bulgu —
  metin, şema ve doğrulayıcı bağımsız yazılarak benimsedi (hüküm adları `confirmed` /
  `needs_validation` / `rejected` aynen alındı; metin düzeyinde, ölçülmedi);
  K4 farklı bir mekanizma — taramanın ve projenin testlerinin körlüğünü mutasyonla ölçer.
- **Şerit C (BaaS/RLS — Supabase, Firebase) birinci sınıf bir kolon** — yalnız Strix'te
  benzeri var.
- **Türkçe orijinal** — kanonik metin Türkçe (`skills/gedik-tr/`); İngilizce sürüm,
  mekanik bir çeviri kapısına tabi çeviridir.

**gedik'in dürüstçe geride olduğu yerler (hepsi gerçek, hepsi bugünkü açık):**
- **Asıl açık: exploit-yoğun hedeflerde teslim güvenilirliği.** İlk benchmark'ta gedik
  en iyi araç kadar ya da daha iyi tespit etti (Hedef 1: 16–17/17), ama Claude'un
  `[cyber]` önlemi tam raporu 6 koşudan 4'ünde kesti — çözüm kod değil, Cyber
  Verification Program. İki benchmark hedefi de zayıf kanıt (bkz.
  [Benchmark](#benchmark-ölçülmüş--2026-09-30)).
- **Tasarım gereği canlı exploit yok** — yalnız canlı bir hedefte çalışma zamanında
  ortaya çıkan sınıflara kördür.
- **Makine-okur çıktı yeni ve kanıtsız; SARIF yok, CI/Action entegrasyonu yok.**
  gedik'in kendi `gedik-bulgular.json` + şema + doğrulayıcı kapısı v2.6'dan beri var ama
  henüz hiçbir canlı denetim bir tane üretmedi; cloudflare/security-audit-skill şemalı bir
  `findings.json`'u testli doğrulayıcılarla birlikte sunuyor.
- **Daha dar kapsam:** cloudflare/security-audit-skill'e kıyasla (orada 9 çekirdek
  saldırı-sınıfı istemi + 10 hedef-türü sınıf dosyası var).
- Anthropic'in kendi **resmî** `claude-security` plugin'i platform sahibinden ücretsiz
  olarak benzer bir alanı kapsıyor. gedik'in ona karşı savunduğu şey genişlik değil —
  yukarıdaki K4 ve triyaj disiplini.

## Kurulum

```
/plugin marketplace add onur-kesim/gedik
/plugin install gedik@gedik
```

İngilizce ana sürüm: [`skills/gedik/`](skills/gedik/) · [README.md](README.md)

## Sınırlar

Salt-okunur (düzeltmez, yalnız raporlar) · **yetki kapılı canlı test — kapsam-içi bir
yetki yoksa reddeder** (`SKILL.md §0.1`) · üçüncü taraf açık kaynağı okumak ücretsiz ama
bulgu sorumlu ifşaya gider, saldırıya değil · silahlandırılmış exploit üretmez ·
para/hesap-güvenliği değişikliği ve kalıcı silme yetkiyle bile yalnız raporlanır, hiç
dokunulmaz.

Bu, sınırsız bir saldırı aracı değil — yetkili bir pentest aracıdır.

Emin değilsen gedik'in yazması gereken şey `ÖLÇÜLMEDİ`dir — "temiz" değil.

## Lisans

MIT — bkz. [LICENSE](LICENSE).
