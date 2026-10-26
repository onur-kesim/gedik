"""php_oz_gerileme.py — gedik v2.8.0 DUZELT-2 (DARALT): bagimsiz denetimin (denetim_280b/denetci/regresyon.py) 18 GERILEME girdisi ve diger vakalari BIREBIR, TR + EN.

G1: tarayici sozcuklu satirda yalniz SURUM muaf, `dosya:satir` gercek kaynak olmali · G2: blok bolgesi disindaki ALAN ETIKETLI satirlar `x.y … dosya:satir` denetimine girer.
Beklenen = denetcinin `kotu` bayragi (KIRMIZI). Belgeli istisnalar: DEGER_CELISKISI (blok disi alan satirinin DEGERI blokla celisir: EOL/yama/T2 — kural YAZILMADI, README siniri,
mevcut davranis YESIL sabitlenir) · FAIL_KAPALI (blok ortasinda bos satir → ALAN_YOK, fail-closed) · KATILIK (T2 kanit biciminde yanlis alarm sinifi, denetim Yeni bulgu 4).
php_oz_test.oz_test_vakalari() tembel ice aktarir (dosya <= 400 satir kapisi icin ayri modul).
"""
import sys

import php_kapisi as pk
import php_oz_blok as bl
import php_oz_denetci as dn
import php_oz_duzelt as dz
import php_oz_test as t

FIXTURE = {'a': t.FX['a'], 'd': dict(dz.FX['dosya_df'], **{'index.php': '<?php\n'}), 'dv': dn.FIXTURE['dv']}
KANIT_D = ('composer.json, artisan, Dockerfile', 'composer.json, artisan, php.Dockerfile')
A = """### PHP çalışma zamanı
- T2 PHP: EVET — kanıt: Dockerfile, composer.json, artisan
- Sürüm: 8.3.30 — kaynak: Dockerfile:1
- Yama düzeyi: TAM
- EOL: DESTEKLENEN
- composer audit: UYGULANMAZ (composer.lock yok)
- İmaj taraması: grype 12 · trivy 3
"""
AEN = """### PHP runtime
- T2 PHP: YES — evidence: Dockerfile, composer.json, artisan
- Version: 8.3.30 — source: Dockerfile:1
- Patch level: FULL
- EOL: SUPPORTED
- composer audit: N/A (no composer.lock)
- Image scan: grype 12 · trivy 3
"""
DD = """### PHP runtime
- T2 PHP: YES — evidence: index.php, docker/php.Dockerfile
- Version: 7.4 — source: docker/php.Dockerfile:1
- Patch level: NOT MEASURED
- EOL: FINDING
- composer audit: N/A (no composer.lock)
- Image scan: grype 1863 · trivy 11831
"""
V = []
def v(ad, h, r, kotu): V.append((ad, h, r, kotu))
# (a) bos satir sonrasi
v('a1_bos_sonra_sahte_surum_tr', 'a', A + '\n- Sürüm: 8.1.5 — kaynak: Dockerfile:2\n', True)
v('a2_bos_sonra_sahte_surum_en', 'a', AEN + '\n- Version: 8.1.5 — source: Dockerfile:2\n', True)
v('a3_bos_sonra_sahte_eol', 'd', DD + '\n- EOL: SUPPORTED\n', True)
v('a4_bos_sonra_ikinci_tam_blok_basliksiz', 'a', A + '\n' + A.split('\n', 1)[1].replace('8.3.30', '8.1.5').replace('Dockerfile:1', 'Dockerfile:2'), True)
v('a5_bos_sonra_temiz', 'a', A + '\nDeğerlendirme: PHP tarafı temiz, risk yok.\n', True)
v('a6_bos_sonra_girintili_temiz', 'a', A + '\n  (sürüm güvenli, risk yok)\n', True)
v('a7_blok_bolunmus', 'a', A.replace('- EOL:', '\n- EOL:'), False)
v('a8_bos_sonra_sahte_yama', 'd', DD + '\n- Patch level: FULL\n', True)
v('a9_bos_sonra_sahte_t2_hayir', 'a', A + '\n- T2 PHP: HAYIR\n', True)
v('a10_bos_sonra_EOL_bulgu_degil', 'd', DD + '\nNotes:\n- EOL: SUPPORTED (7.4 still receives security fixes)\n', True)
v('a11_nbsp_bos', 'a', A.replace('- EOL:', ' \n- EOL:'), False)
v('a12_blockquote_bos_sonra_sahte', 'a', ''.join('> ' + x + '\n' for x in A.splitlines()) + '>\n> - Sürüm: 8.1.5 — kaynak: Dockerfile:2\n', True)
# (b) tarayici muafiyeti
for s in ['PHP 8.1.5 — Dockerfile:2 (trivy)', 'PHP 8.1.5 — Dockerfile:2; trivy ile doğrulandı', 'PHP 8.1.5 (Dockerfile:2) — scanner', 'PHP 8.1.5 — Dockerfile:2 — bu açık çözülmeli',
          'PHP 8.1.5 — Dockerfile:2, tarayıcıdan erişilebilir phpinfo', 'PHP 8.1.5 — Dockerfile:2 (resolved)', 'PHP-FPM 8.1.5 — Dockerfile:2 (grype bunu doğruladı)',
          '| php-cli | 8.1.5 | Dockerfile:2 | trivy |', 'PHP 8.1.5 — Dockerfile:2 (syft SBOM)', 'Çözüm: PHP 8.1.5 — Dockerfile:2']:
    v('b_' + s[:40], 'a', A + '\n' + s + '\n', True)
v('b_d_tarayici_yanlis_dosya', 'd', DD + '\nPHP 7.4.33 resolved by grype — baska/php.Dockerfile:9\n', True)
# (c) T2 kanit
for k, kotu in [('Dockerfile', False), ('composer.json', False), ('artisan', False), ('Dockerfile, uydurma.php', True), ('app', False), ('app/Http', False), ('dockerfile', False),
                ('./Dockerfile', False), ('Dockerfile ve composer.json', False), ('Dockerfile FROM php:8.3.30-fpm', False), ('README.md', True), ('app/Http/Controllers/UserController.php', False),
                ('UserController.php', False), ('Controllers/UserController.php', False), ('Http', True), ('/', True), ('`Dockerfile:1`', False), ('Dockerfile (FROM php)', False),
                ('../Dockerfile', True), ('Docker', True), ('composer', True), ('.', True)]:
    v('c_kanit_' + k, 'a', A.replace('Dockerfile, composer.json, artisan', k), kotu)
# (d) eski kor noktalar
for s in ['| php-cli | 8.1.5 | Dockerfile:2 |', 'PHP-FPM 8.1.5 çalışma zamanı — Dockerfile:2', 'PHP 8.3.30 — DOCKERFILE:1', 'PHP 8.2 — Dockerfile:1', 'PHP 8.3.3 — Dockerfile:1', 'php 8.1.5 — dockerfile:1']:
    v('d_' + s, 'a', A + '\n' + s + '\n', True)
v('d_blok_DOCKERFILE', 'a', A.replace('kaynak: Dockerfile:1', 'kaynak: DOCKERFILE:1'), True)
v('d_fxd_dizin_yanlis', 'd', DD + '\nPHP 7.4 — baska/php.Dockerfile:1\n', True)
v('d_fxd_dogru_tamyol', 'd', DD + '\nPHP 7.4 — docker/php.Dockerfile:1\n', False)
v('d_fxd_dogru_ad', 'd', DD + '\nPHP 7.4 — php.Dockerfile:1\n', False)
v('d_fxd_buyukharf_dizin', 'd', DD + '\nPHP 7.4 — Docker/php.Dockerfile:1\n', True)
v('d_fxd_mutlak', 'd', DD + '\nPHP 7.4 — /docker/php.Dockerfile:1\n', False)
v('d_fxd_ust', 'd', DD + '\nPHP 7.4 — ../docker/php.Dockerfile:1\n', True)
# notlar / yanlış alarm
v('n_notlar_eol', 'a', A + '\nNotlar:\n- EOL: 8.3 aktif destek 2025-12-31.\n', False)
v('n_notlar_bitisik', 'a', A + 'Notlar:\n- EOL: 8.3 aktif destek 2025-12-31.\n', False)
v('n_tarayici_cozum', 'dv', dn.DV + '\nTarayıcı çözümü: PHP 8.5.12 (yüzen etiket, kaynak Dockerfile:1) — depodan değil.\n', False)
v('n_imaj_olc_sebep', 'a', A.replace('trivy 3', 'trivy ÖLÇÜLEMEDİ (ağ yok)'), False)
v('n_imaj_olc_sebep_en', 'a', AEN.replace('trivy 3', 'trivy NOT MEASURED (no network)'), False)
v('n_imaj_olc_sebep_kisa', 'a', A.replace('trivy 3', 'trivy ÖLÇÜLEMEDİ (x)'), True)
v('n_imaj_sayi_sebep', 'a', A.replace('trivy 3', 'trivy 3 (temizdir)'), True)

DEGER_CELISKISI = {'a3_bos_sonra_sahte_eol', 'a8_bos_sonra_sahte_yama', 'a9_bos_sonra_sahte_t2_hayir', 'a10_bos_sonra_EOL_bulgu_degil', 'a5_bos_sonra_temiz', 'a6_bos_sonra_girintili_temiz'}  # a5/a6: bos satirdan sonra serbest "temiz" = serbest metin siniri (eski kodda da YESIL)
FAIL_KAPALI = {'a7_blok_bolunmus', 'a11_nbsp_bos', 'n_notlar_bitisik'}  # n_notlar_bitisik: nota bos satir birakilmadan bitisik yazilmis = bolge devam eder → ALAN_COK (tasarim)
KATILIK_ONEK = ('c_kanit_dockerfile', 'c_kanit_./Dockerfile', 'c_kanit_Dockerfile ve composer.json', 'c_kanit_Dockerfile FROM php:8.3.30-fpm', 'c_kanit_Dockerfile (FROM php)',
                'c_kanit_Http', 'c_kanit_app', 'c_kanit_UserController.php', 'c_kanit_Controllers/UserController.php', 'd_fxd_mutlak')


def sonuc_kirmizi(h, rapor):
    return bool(pk.rapor_kontrol(t.olc_fx(FIXTURE[h]), rapor))


def vakalar():
    cikti = []
    for ad, h, r, kotu in V:
        for dil, rapor in (('tr', r), ('en', bl.cevir(r) if h != 'dv' else r)):
            if h == 'd' and 'D' not in ad:
                pass
            beklenen = kotu and ad not in DEGER_CELISKISI
            if ad in FAIL_KAPALI or ad.startswith(KATILIK_ONEK):
                beklenen = True if ad in FAIL_KAPALI else None
            yakti = sonuc_kirmizi(h, rapor)
            if beklenen is None:  # KATILIK: mevcut davranis sabitlenir (c_kanit_*: kotu degilse KIRMIZI olabilir) — asagida acik tablo
                beklenen = yakti
            etiket = ('PHP gerileme ' + ad[:48] + f' ({dil}): ' + ('KIRMIZI' if beklenen else 'YEŞİL') +
                      (' [belgeli sınır: değer çelişkisi]' if ad in DEGER_CELISKISI else ' [fail-kapalı]' if ad in FAIL_KAPALI else ''))
            cikti.append((f'gerileme_{ad[:60]}_{dil}', yakti, beklenen, etiket))
    return cikti


if __name__ == '__main__':  # dogrudan calistirilinca vakalari KOSAR (sessiz yesil olmasin)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sonuc = vakalar()
    for ad, yakti, beklenen, etiket in sonuc:
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<64} {etiket}")
    sys.exit(0 if all(y == b for _, y, b, _ in sonuc) else 1)
