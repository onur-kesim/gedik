# gedik

**"Bulsun ki kapatılabilsin."** gedik kendi projelerini bir saldırgan gibi kırıp
gedikleri listeler. Çıktı: `G-1`, `G-2`… numaralanan bulgular, her biri çalışan bir PoC
ve yama önerisiyle gelir.

## NE TESLİM EDİLMEDİ (bu sürümde HAYIR)

- **Henüz benchmark yok.** gedik hiçbir zaman puanlanmış bir hedefe karşı ölçülmedi.
  Bu depoda hiçbir yerde "X'ten daha iyi" iddiası yok — bkz.
  [Rakipler, dürüstçe](#rakipler-dürüstçe).
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
- **Makine-okur çıktı yok.** Rapor yalnız Markdown — SARIF/JSON yok, CI/Action
  entegrasyonu yok.
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
6. **Varsayılan olarak kendi projen; üçüncü taraf yalnız yetkiyle.** Herhangi bir açık
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

## Rakipler, dürüstçe

gedik hiç benchmark'lanmadı. Aşağıdaki kıyas *tasarım farkıdır*, ölçülmüş üstünlük
değil — her "önde" iddiasını hipotez say, sonuç değil.

| Araç | Yıldız | Lisans | Canlıya saldırır mı? | Not |
|---|---|---|---|---|
| [usestrix/strix](https://github.com/usestrix/strix) | 65k+ | Apache-2.0 | **Evet** | CLI + 9 skill + MCP; kendi Supabase-RLS skill'i var |
| [KeygraphHQ/shannon](https://github.com/KeygraphHQ/shannon) | 48k+ | AGPL-3.0 | **Evet** | CLI + CI + skill; "no exploit, no report" |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) (`claude-security`) | 37k+ (depo) | Apache-2.0 | Hayır | Anthropic'in kendi resmî marketplace plugin'i; bağımsız doğrulayıcı ajanlar; 25 Eyl 2026'da dizine girdi |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 23k+ (29 Eyl 2026) | MIT | Hayır — canlı yoklama tamamen yasak | Bağımsız doğrulayıcı ajanlar her adayı çürütmeye çalışır (yanlış-pozitif eleme); şemalı `findings.json` + testli doğrulayıcılar; 9 çekirdek saldırı-sınıfı istemi + 10 hedef-türü sınıf dosyası; 18 Haz 2026'da oluşturuldu |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 7k+ | CC-BY-SA-4.0 | Hayır | Marketplace, 44 plugin; **mutasyon testi orada ayrı bir skill** |
| [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | 6k+ | MIT | Hayır | GitHub Action + `/security-review`; FP filtresi + `evals/` |

**gedik'in farklı olması beklenen yerler (ölçülmemiş, yalnız tasarım iddiası):**
- **Taramadan önce triyaj (K1, T1–T12)** — mimarinin sahip olmadığı bir yüzeyi açmaz.
- **K4 kendi-mutant'ı, iki yöne birden** — hem kendi taramasını hem projenin test
  paketini kirletip ısırdığını kanıtlar. İncelenen araçlardan hiçbiri kendi körlüğünü
  böyle öz-test etmiyor. cloudflare/security-audit-skill'in bağımsız çürütücüleri yanlış
  pozitifi keser; K4 farklı bir mekanizma — taramanın ve projenin testlerinin körlüğünü
  mutasyonla ölçer.
- **Şerit C (BaaS/RLS — Supabase, Firebase) birinci sınıf bir kolon** — yalnız Strix'te
  benzeri var.
- **Türkçe orijinal** — kanonik metin Türkçe (`skills/gedik-tr/`); İngilizce sürüm,
  mekanik bir çeviri kapısına tabi çeviridir.

**gedik'in dürüstçe geride olduğu yerler (hepsi gerçek, hepsi bugünkü açık):**
- **Ölçülmüş bir skor yok.** Anthropic'in ve
  [agamm/claude-code-owasp](https://github.com/agamm/claude-code-owasp)'nin araçlarında
  `evals/` var; Shannon ve PentestGPT sayı veriyor. En büyük açık bu.
- **Tasarım gereği canlı exploit yok** — yalnız canlı bir hedefte çalışma zamanında
  ortaya çıkan sınıflara kördür.
- **Makine-okur çıktı yok** (SARIF/JSON), CI/Action entegrasyonu yok —
  cloudflare/security-audit-skill şemalı bir `findings.json`'u testli doğrulayıcılarla
  birlikte sunuyor.
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
