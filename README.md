# proje-sablonu — her tür proje için standart: çekirdek + profil, kör kapılı CI

> Yeni projede bu README projenin kendisi için yeniden yazılır; **başlık düzeni kalır**: önce NE TESLİM EDİLMEDİ, sonra RAKİP/ÖNCÜL, kurulum tek komut, BİTTİ LİSTESİ.

## NE TESLİM EDİLMEDİ (bu sürümde HAYIR ya da sonraki dilim)
- `kur.py` sihirbazı — profil seçimi, hesap ölçümü, dal korumasını otomatik açma: **sonraki dilim**; bugün KURULUM.md'deki elle adımlar.
- Windows çalıştırıcı (`[yigin] os = "windows"`): CI'da **ölçülmedi**, alan proje.toml'da var, iş akışı henüz okumuyor.
- Flutter ve Android kurulum adımları CI'da var ama gerçek bir mobil projede **ölçülmedi** (ÖLÇÜLEMEDİ).
- Kod sağlığı karmaşıklık ölçümü yalnız Python için; diğer dillerde dosya uzunluğu ölçülür, karmaşıklık ÖLÇÜLEMEDİ yazılır.
- Ürün nabzı skill'inin `[urun] desen` okuması: skill'e taşınmadı; `kapilar.py` nabzı kendisi hesaplar.
- Genel esasların gerekçe dosyası (hangi kural hangi ölçümden doğdu): şablonda değil, sahibinin arşivinde.
- KEŞİF aşamasının otomatik kapısı yok: ESAS KARARI kutuları elle kapanır; `kapilar.py` yalnız `asama` değerini doğrular ve nabzı atlar.

## RAKİP / ÖNCÜL
GitHub'ın kendi şablon depoları, `cookiecutter`, `copier` ve çeşitli "Claude Code starter" depoları proje iskeleti verir. Buradaki katkı iskelet değil, **işleyiş**: her tür projeye (yazılım, araştırma, koçluk, iş, tasarım) aynı dört dosya ve aşama-kapı düzeni; kapıların kendini kanıtlaması (altın küme); teslim tanımının "dışarı çıktı" şartı; yapay zekâ asistanıyla iş bölümü (Code üretir, Cowork denetler). Yalnız iskelet istiyorsan `cookiecutter` daha zengindir.

## KURULUM VE ÇALIŞTIRMA (tek komut — CI'daki komutla aynı)
```
cd <projeler-klasörü>; gh repo create <hesap>/<proje> --template onur-kesim/proje-sablonu --private --clone
cd <projeler-klasörü>/<proje>; python -B araclar/kapilar.py
```
Ayrıntı: `KURULUM.md`. İşleyişin tamamı: `CLAUDE.md` (çekirdek blok, 11 bölüm).

## BİTTİ LİSTESİ (ölçülmüş, teslim edilmiş)
- Dört dosya düzeni: `CLAUDE.md` (çekirdek + profil + proje-özel) · `README.md` · `DURUM.md` · `DILIM.md`.
- KEŞİF / YAPIM aşaması (v2.1): `proje.toml [proje] asama`. KEŞİF'te (fikir, araştırma, danışma, tasarım) süre tavanı yok, K1-K2-K8 işlemez, ürün nabzı kapısı ATLANDI (PASS değil); çıkışı `DILIM.md` ESAS KARARI kutuları + insanın "başla" sözü. Altın kümede 3 vaka: YAPIM 30 gün FAIL, KEŞİF 30 gün yakmaz, KEŞİF ATLANDI.
- KUR ≤ 1 gün; MOD KRİTİK'in iki denetim turu yalnız TESLİM'de (KUR/altyapıda tek tur, D1 yeter); PROJE-ÖZEL iskeletinde PROJE KURALLARI (≤5). Dayanak: ilk gerçek kurulumda KUR kancasına iki tur + 26 mutant koşuldu (26 Eyl ölçümü).
- `proje.toml`: yığın, komutlar, ürün deseni, profil, kapı eşikleri — CI ve araç tek kaynaktan okur.
- `araclar/kapilar.py`: 14 vakalık altın küme öz-testi (geçmezse ölçüm reddedilir) → kur/test/lint/build → kod sağlığı (400 satır, karmaşıklık 15, dondurulmuş taban) → gizli anahtar taraması → belge/kod oranı → ürün nabzı (git log) → kanıt < ürün. Yalnız standart kütüphane, Python ≥ 3.11.
- `.github/workflows/ci.yml`: tek iş akışı, yığına göre koşullu kurulum; `kapilar` + `kor-kapi` işleri; çalıştırıcı `ubuntu-24.04` sabit (`ubuntu-latest` 19 Ekim 2026'da Ubuntu 26'ya taşınıyor — GitHub koşum notu; 26.04'e geçiş kararla).
- Beş profil + profil şablonu (`profiller/`): yazılım · araştırma · eğitim-koçluk · iş-strateji · tasarım; sekiz başlık, ≤2.000 bayt.
- PR şablonu: DOĞRULA + TESLİM kutuları, DENETİM raporu, NE ÖLÇÜLEMEDİ.
- `.github/workflows/release.yml`: `v*` etiketi → GitHub Release, notlar CHANGELOG'un aynı sürüm bölümünden (üçüncü taraf action yok).
- `.github/dependabot.yml`: GitHub Actions güncelleyici açık; npm/pip/pub/gradle satırları yorumda, KUR'da yığına göre açılır (manifesti olmayan ekosistem koşumu kırmızı yapıyor — 26 Eyl ölçümü).
- `.gitignore`, `.env.example`, `LICENSE` (MIT), `CHANGELOG.md`, `KURULUM.md`, `araclar/dal-korumasi.json`.
