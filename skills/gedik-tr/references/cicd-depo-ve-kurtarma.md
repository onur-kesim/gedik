# CI/CD, Depo Hijyeni ve Sızıntı Sonrası Kurtarma

Kod güvenliyken **onu üreten hat** açık olabilir. Boru hattı sırlara ve üretime
erişir; ele geçirilirse kod incelemesi hiçbir şey ifade etmez.

Bu dosya, kaynak deposuna ve/veya CI yapılandırmasına erişim varsa okunur.

---

## 1. DEPO HİJYENİ

- **Depo görünürlüğü:** public mi private mı? Public ise `.env`, yedek, dökümanda
  gömülü değer, ekran görüntüsündeki token, issue/PR yorumlarındaki sır **herkese açıktır.**
- **`.gitignore` kapsamı:** `.env*` (`.env.local`, `.env.production` dâhil) · `*.pem`
  `*.key` `*.p12` `*.jks` · `*.sqlite` `*.db` · `coverage/` `dist/` `build/` ·
  IDE ve OS artıkları. **Sadece `.env` yazmak yetmez.**
- **Zaten izlenen dosya:** `.gitignore`'a eklemek, önceden commit'lenmiş dosyayı
  takipten çıkarmaz. Ölç: `git ls-files | grep -Ei '\.env|\.pem$|\.key$|\.p12$|\.jks$'`
- **Geçmiş taraması (HEAD yetmez):**
  `git log -p --all -S "<anahtar deseni>" | head -50` ·
  `git rev-list --all --objects | git cat-file --batch-check` ile büyük/şüpheli blob.
  Desenler: `AKIA` (AWS) · `sk_live_` (Stripe) · `ghp_`/`gho_` (GitHub) ·
  `eyJhbGciOi` (JWT) · `-----BEGIN .* PRIVATE KEY-----` · `service_role` ·
  `xox[baprs]-` (Slack) · `AIza` (Google).
- **Fork ve klonlar:** bir sır public depoya girdiyse fork'lar ve önbellekler
  silinemez → **döndürme tek çözümdür** (§3).
- **Büyük dosyalar/yedekler:** repoda veritabanı dökümü, müşteri listesi, log arşivi.

## 2. BORU HATTI (CI/CD)

- **Dal koruması:** ana dala doğrudan push kapalı mı; zorunlu inceleme var mı;
  force-push ve dal silme kısıtlı mı?
- **Fork PR'ında sır erişimi — en tehlikeli tek ayar:** GitHub'da
  `pull_request_target` ve `workflow_run` tetikleyicileri **fork'un kodunu** depo
  sırlarına erişimi olan bağlamda çalıştırabilir. Bu tetikleyicilerden biri varsa
  ve iş akışı `actions/checkout` ile **PR head'ini** çekiyorsa → **KRİTİK**
  (herhangi biri PR açıp sırları çalar).
- **Üçüncü taraf action/adım sabitlemesi:** `uses: bir/action@v3` etiketle mi
  sabitlenmiş, yoksa **tam SHA** ile mi? Etiket taşınabilir; SHA taşınmaz.
- **Sır log'lama:** `set -x`, `echo $SECRET`, hata ayıklama modunda ortam dökümü.
  CI maskesi yalnız tam eşleşmeyi maskeler; base64'lenmiş ya da parçalanmış sır maskelenmez.
- **Self-hosted runner:** paylaşılan/kalıcı runner'da bir iş diğerinin artıklarını
  okuyabilir; fork PR'ları self-hosted runner'da koşmamalı.
- **Dağıtım anahtarı kapsamı:** CI'nin üretim anahtarı ne kadar yetkili — yalnız
  dağıtım mı, tam yönetici mi? Ortam bazlı ayrı anahtar var mı?
- **Artefakt bütünlüğü:** yayımlanan artefakt imzalanıyor mu; sürüm etiketi ile
  commit arasında bağ (provenance) var mı?
- **Bağımlılık kurulumu:** `npm ci` / `--frozen-lockfile` mi, yoksa `npm install` mi
  (sürüm sürüklenmesi)? `postinstall` betikleri kapalı mı (`--ignore-scripts`)?
- **Ortam ayrımı:** staging ile üretim aynı veritabanına mı bakıyor; staging'de
  gerçek PII var mı?

## 3. SIZINTI SONRASI KURTARMA — SIRA ÖNEMLİ

Bir sır sızdıysa **ilk iş dosyadan silmek DEĞİLDİR.** Silmek, sızıntıyı gizler ama
anahtarı geçerli bırakır. Doğru sıra:

1. **İPTAL / DÖNDÜR (önce bu).** Sağlayıcı panelinden anahtarı geçersiz kıl ve
   yenisini üret. Anahtar geçerli olduğu sürece geçmişten silmek işe yaramaz.
2. **Kötüye kullanım kontrolü.** Sağlayıcı erişim log'unda sızıntı tarihinden bu yana
   beklenmedik kullanım var mı: yeni IP/bölge, olağandışı hacim, yeni oluşturulan
   alt-anahtar veya kullanıcı. **Bunu yazılı olarak rapora geç** — "kontrol edildi,
   şu tarihe kadar anormal yok" ya da "ÖLÇÜLMEDİ, log erişimi yok".
3. **Yeni anahtarı dağıt.** Ortam değişkenleri, CI sırları, ekip. Eski anahtarın
   hiçbir yerde kalmadığını doğrula.
4. **Geçmişi temizle (isteğe bağlı, en son).** `git filter-repo` / BFG ile geçmişten
   çıkar, force-push. **Not:** fork'lar, klonlar, CI önbellekleri ve arama motoru
   önbellekleri temizlenmez — bu adım kozmetiktir, 1. adımın yerini TUTMAZ.
5. **Tekrarı engelle.** `.gitignore` düzelt · commit öncesi sır tarayıcı (pre-commit
   hook / CI adımı) ekle · sırrı doğru katmana taşı (bkz. `kod-inceleme-guvenlik.md` §3).
6. **Bildirim gerekiyor mu?** Sızan şey **kişisel veriye erişim** sağlıyorsa KVKK
   kapsamında veri sorumlusunun bildirim yükümlülüğü doğabilir. Bu bir **hukuki
   değerlendirmedir** — teknik rapor "bildirim gerekebilir, hukuki görüş alın" der,
   kendisi karar vermez.

**Rapora yazılacak asgari satır:** ne sızdı · ne zaman girdi (ilk commit tarihi) ·
ne kadar süre açık kaldı · kim erişebilirdi (public/private) · döndürüldü mü
(evet/hayır + tarih) · kötüye kullanım kontrolü sonucu.

---

## 4. DEPENDENCY CONFUSION

İç paket adı public registry'de **claim edilmemiş** → saldırgan public'e yükler, build
iç yerine onu çeker. (typosquat'tan farklı: namespace/scope sahiplenme, iç paket adının
**varlığından** kaynaklanır.)

**Bakılacak imza:** iç/özel paket adları · registry/scope yapılandırması ·
`.npmrc`/`pip.conf` kaynak önceliği (özel registry önce mi taranıyor, yoksa public
önce mi) · scope (`@org/paket`) sahipliği public registry'de teyitli mi.

**PoC/mutant:** iç paket adını public registry'de zararsız bir isim-kontrolüyle ara —
kayıtlı değilse **claim edilebilir** demektir, bulgu. **Şiddet: KRİTİK** (build-time RCE).

## 5. CI OIDC → BULUT GÜVEN YANLIŞ YAPILANDIRMASI

Buluta OIDC ile giren workflow'un trust policy `sub` claim'i **wildcard** (`repo:*`,
`ref:*`) → başka repo/branch bulut rolünü üstlenir.

**Bakılacak imza:** bulut IAM trust policy (`token.actions.githubusercontent.com`) ·
`sub`/`aud` koşulunun darlığı — belirli repo+branch'e mi sabit, yoksa joker mi.
**Şiddet: KRİTİK.**

## 6. KONTEYNER & IaC SERTLEŞTİRME (T12)

- **Konteyner:** root çalışma (`USER` yok) · `latest` etiketi · layer'da sır (`ARG`/`ENV`
  ile gömülü token — imaj katmanında kalır, `docker history` ile okunur) · base imaj CVE ·
  `--privileged` · docker soketi mount · gereksiz capability.
- **IaC:** public S3/bucket · `0.0.0.0/0` security group · IAM `*:*` wildcard ·
  şifresiz disk/DB · public snapshot · log kapalı. **K8s:** privileged pod · `hostPath`
  mount · `allowPrivilegeEscalation` · network policy yok · secret env'de düz.
- **Araç:** `trivy config`, `checkov`, `tfsec`, `kube-score` (mekanik kat —
  `kod-inceleme-guvenlik.md` §5 ile birlikte; çıktı gedik muhakemesinden geçer, K2 korunur).

---

## Hızlı kapanış kontrolü

1. `git ls-files` ile izlenen sır dosyası **yok** olduğu kanıtlandı mı?
2. Geçmiş, en az beş anahtar deseniyle `--all` üzerinden tarandı mı?
3. `pull_request_target` / `workflow_run` var mı; varsa PR head checkout ediliyor mu?
4. Üçüncü taraf action'lar SHA ile mi sabitlenmiş?
5. Ana dal koruması ve zorunlu inceleme açık mı?
6. Bulunan her sır için **döndürüldü mü** sorusu cevaplandı mı (silindi ≠ döndürüldü)?
7. İç paket adları public registry'de claim edilmemiş mi ölçüldü (dependency confusion, §4)?
8. Buluta OIDC ile giren workflow'ların trust policy `sub`/`aud` koşulu dar mı (§5)?
9. T12 EVET ise (IaC/bulut): konteyner root/latest/sır ve IaC (public bucket, IAM
   wildcard, k8s privileged pod) sertleştirmesi ölçüldü mü (§6)?
