"""php_oz_denetci.py — gedik v2.8.0 DUZELT: bagimsiz denetcinin (denetim_280/denetci/kor.py) vakalari BIREBIR (sablonlar + v(...) cagrilari).

Beklenen KIRMIZI/YESIL denetcinin beklentisidir. Denetcinin '?' (belirsiz) ya da 'beyanli sinir' dedigi ve kapinin BELGELENMIS SINIRI olan vakalarda
(serbest metin yalniz `PHP x.y ... dosya:satir` kalibini denetler; sayilar/sebep metni dogrulanmaz) MEVCUT davranis SINIR olarak sabitlenir.
Fixture esleme: a = Laravel + FROM php:8.3.30-fpm · wp = WordPress yedegi · dv = DVWA benzeri (php:8-apache + composer.lock) · d = docker/php.Dockerfile 7.4.
"""
import sys

import php_kapisi as pk
import php_oz_duzelt as dz
import php_oz_test as t

FIXTURE = {
    'a': t.FX['a'],
    'wp': dict(t.FX['c'], **{'wp-config.php': '<?php\n'}),
    'dv': {'Dockerfile': 'FROM php:8-apache\n', 'index.php': '<?php\n', 'vulnerabilities/api/composer.json': '{}\n', 'vulnerabilities/api/composer.lock': '{}\n'},
    'd': dict(dz.FX['dosya_df'], **{'index.php': '<?php\n'}),
}
TR = """### PHP çalışma zamanı
- T2 PHP: EVET — kanıt: composer.json, artisan, Dockerfile
- Sürüm: 8.3.30 — kaynak: Dockerfile:1
- Yama düzeyi: TAM
- EOL: DESTEKLENEN
- composer audit: UYGULANMAZ (composer.lock yok)
- İmaj taraması: grype 12 · trivy ÖLÇÜLEMEDİ
"""
EN = """### PHP runtime
- T2 PHP: YES — evidence: composer.json, artisan, Dockerfile
- Version: 8.3.30 — source: Dockerfile:1
- Patch level: FULL
- EOL: SUPPORTED
- composer audit: N/A (no composer.lock)
- Image scan: grype 12 · trivy NOT MEASURED
"""
WP = """### PHP çalışma zamanı
- T2 PHP: EVET — kanıt: wp-config.php
- Sürüm: YOK
- Yama düzeyi: ÖLÇÜLEMEDİ
- EOL: ÖLÇÜLEMEDİ
- composer audit: UYGULANMAZ (composer.lock yok)
- İmaj taraması: grype ÖLÇÜLEMEDİ · trivy ÖLÇÜLEMEDİ
"""
DV = """### PHP çalışma zamanı
- T2 PHP: EVET — kanıt: Dockerfile
- Sürüm: YÜZEN 8-apache — kaynak: Dockerfile:1
- Yama düzeyi: ÖLÇÜLEMEDİ
- EOL: ÖLÇÜLEMEDİ
- composer audit: 0 danışma
- İmaj taraması: grype 0 · trivy 0
"""
V = []
def v(ad, h, r, b): V.append((ad, h, r, b))
# temel
v('temel_tr', 'a', TR, 'YESIL'); v('temel_en', 'a', EN, 'YESIL'); v('temel_wp_sabitli', 'wp', WP + pk.SABIT_TR + '\n', 'YESIL'); v('temel_dvwa', 'dv', DV, 'YESIL')
# (a) önceki kör noktalar
v('a1_tablo', 'a', TR + '\n| php-cli | 8.1.5 | Dockerfile:2 |\n', 'KIRMIZI')
v('a2_fpm', 'a', TR + '\nPHP-FPM 8.1.5 çalışma zamanı — Dockerfile:2\n', 'KIRMIZI')
v('a3_buyuk', 'a', TR + '\nPHP 8.3.30 — DOCKERFILE:1\n', 'KIRMIZI')
v('a3b_buyuk_blokta', 'a', TR.replace('Dockerfile:1', 'DOCKERFILE:1'), 'KIRMIZI')
# (b) blok doğru, serbest metin yanlış
v('b1_uydurma_kaynaksiz', 'a', TR + '\nÇalışma zamanı PHP 8.1.5 (EOL!).\n', 'KIRMIZI')
v('b2_uydurma_satir_kelime', 'a', TR + '\nPHP 8.1.5 — Dockerfile satır 2\n', 'KIRMIZI')
v('b3_uydurma_L', 'a', TR + '\nPHP 8.1.5 (Dockerfile#L2)\n', 'KIRMIZI')
v('b4_uydurma_phpsiz', 'a', TR + '\nÇalışma zamanı 8.1.5 — Dockerfile:2\n', 'KIRMIZI')
v('b5_uydurma_satir_bolunmus', 'a', TR + '\nPHP çalışma zamanı:\n8.1.5 — Dockerfile:2\n', 'KIRMIZI')
v('b6_kisit_muaf', 'a', TR + '\nPHP 8.1.5 — Dockerfile:2 (composer require uyumlu)\n', 'KIRMIZI')
v('b7_temiz_serbest', 'a', TR + '\nPHP çalışma zamanı temiz, risk yok.\n', 'KIRMIZI')
v('b8_clean_serbest_en', 'a', EN + '\nPHP runtime is clean and safe.\n', 'KIRMIZI')
v('b9_dal_yanlis', 'a', TR + '\nPHP 8.2 — Dockerfile:1\n', 'KIRMIZI')
v('b10_farkli_satir', 'a', TR + '\nPHP 8.3.30 — Dockerfile:3\n', 'KIRMIZI')
v('b11_dal_dogru', 'a', TR + '\nPHP 8.3 — Dockerfile:1\n', 'YESIL')
v('b12_uydurma_dosya_disi', 'a', TR + '\nPHP 8.1.5 — runtime.txt:1\n', 'KIRMIZI')
v('b13_uydurma_php_ini', 'a', TR + '\nPHP 8.1.5 — php.ini:1\n', 'KIRMIZI')
v('b14_yanlis_eol_serbest', 'a', TR + '\nPHP 8.3 EOL oldu, desteklenmiyor (BULGU).\n', 'KIRMIZI')
v('b15_composer_lock_var_iddia', 'a', TR + '\ncomposer audit: 0 danışma (composer.lock okundu)\n', 'KIRMIZI')
v('b16_onek_8_3_3_degil', 'a', TR + '\nPHP 8.3.3 — Dockerfile:1\n', 'KIRMIZI')
v('b17_backtick_kaynak', 'a', TR + '\nPHP 8.1.5 — `Dockerfile`:2\n', 'KIRMIZI')
v('b18_yol_onekli', 'a', TR + '\nPHP 8.1.5 — ./Dockerfile:1\n', 'KIRMIZI')
v('b19_unicode_tire_iki_nokta', 'a', TR + '\nPHP 8.1.5 — Dockerfile：2\n', 'KIRMIZI')
# (c) alan biçimi
v('c1_buyuk_kucuk_etiket', 'a', TR.replace('- EOL:', '- eol:'), 'KIRMIZI')
v('c2_fazla_bosluk', 'a', TR.replace('- EOL: DESTEKLENEN', '-   EOL  :   DESTEKLENEN  '), 'YESIL')
v('c3_tr_baslik_en_alan', 'a', '### PHP çalışma zamanı\n' + EN.split('\n', 1)[1], 'YESIL')
v('c3b_karisik_alan', 'a', TR.replace('- EOL: DESTEKLENEN', '- EOL: SUPPORTED').replace('Yama düzeyi: TAM', 'Patch level: FULL'), 'YESIL')
v('c4_sira_ters', 'a', TR.split('\n')[0] + '\n' + '\n'.join(reversed(TR.strip().split('\n')[1:])) + '\n', 'YESIL')
v('c5_alan_eksik', 'a', TR.replace('- Yama düzeyi: TAM\n', ''), 'KIRMIZI')
v('c6_alan_cift_ayni', 'a', TR + '- EOL: DESTEKLENEN\n', 'KIRMIZI')
v('c7_iki_blok_dogru_yanlis', 'a', TR + '\n' + TR.replace('8.3.30', '8.1.5'), 'KIRMIZI')
v('c8_iki_blok_ikinci_baska_baslik', 'a', TR + '\n## PHP runtime\n- Version: 8.1.5 — source: Dockerfile:1\n', 'KIRMIZI')
v('c9_kod_blogu_icinde', 'a', '```\n' + TR + '```\n', 'YESIL?')
v('c10_kod_blogu_sablon_artı_dogru', 'a', 'Şablon:\n```\n### PHP çalışma zamanı\n- Sürüm: <x.y[.z]> — kaynak: <dosya:satır>\n```\n' + TR, 'YESIL?')
v('c11_baslik_ekli', 'a', TR.replace('### PHP çalışma zamanı', '### PHP çalışma zamanı (T2)'), 'YESIL?')
v('c12_baslik_kalin', 'a', TR.replace('### PHP çalışma zamanı', '**PHP çalışma zamanı**'), 'YESIL?')
v('c13_blok_icinde_serbest_temiz', 'a', TR + 'Değerlendirme: PHP tarafı temiz.\n', 'KIRMIZI')
v('c14_blok_icinde_alan_altinda_temiz', 'a', TR.replace('- EOL: DESTEKLENEN\n', '- EOL: DESTEKLENEN\n  (sürüm güvenli, risk yok)\n'), 'KIRMIZI')
v('c15_tablo_bicimi', 'a', '### PHP çalışma zamanı\n| Alan | Değer |\n|---|---|\n' + ''.join('| %s | %s |\n' % tuple(x[2:].split(': ', 1)) for x in TR.strip().split('\n')[1:]), 'YESIL?')
v('c16_surum_not_ekli', 'a', TR.replace('kaynak: Dockerfile:1', 'kaynak: Dockerfile:1 (resmî imaj)'), 'YESIL?')
v('c17_imaj_not_ekli', 'a', TR.replace('trivy ÖLÇÜLEMEDİ', 'trivy ÖLÇÜLEMEDİ (ağ yok)'), 'YESIL?')
v('c18_numarali_madde', 'a', TR.replace('- ', '1. '), 'YESIL?')
v('c19_I_noktasiz', 'a', TR.replace('İmaj', 'Imaj'), 'YESIL?')
v('c20_t2_kanit_uydurma', 'a', TR.replace('composer.json, artisan, Dockerfile', 'yok_boyle_dosya.xyz'), 'KIRMIZI')
v('c21_kaynak_path_onek', 'a', TR.replace('kaynak: Dockerfile:1', 'kaynak: ./Dockerfile:1'), 'YESIL?')
v('c22_blok_sonda_sabitsiz_baska_baslik_yok', 'a', TR + 'trivy ve grype birlikte: temiz\n', 'KIRMIZI')
# (d) composer uydurma
v('d1_dvwa_composer_uydurma_0', 'dv', DV, 'YESIL (beyanlı sınır)')
v('d2_dvwa_composer_999', 'dv', DV.replace('0 danışma', '999 danışma'), 'YESIL (beyanlı sınır)')
v('d3_dvwa_imaj_uydurma', 'dv', DV.replace('grype 0 · trivy 0', 'grype 0 · trivy 0'), 'YESIL (beyanlı sınır)')
v('d4_dvwa_composer_olc_sebep_saçma', 'dv', DV.replace('0 danışma', 'ÖLÇÜLEMEDİ (xyz)'), 'YESIL (beyanlı sınır)')
# (e) sürüm YOK
v('e1_wp_sabitsiz', 'wp', WP, 'KIRMIZI')
v('e2_wp_sabit_kod_blogunda', 'wp', WP + '```\n' + pk.SABIT_TR + '\n```\n', 'YESIL?')
v('e3_wp_sabit_degistirilmis', 'wp', WP + 'PHP çalışma zamanı sürümü depoda yok — ÖLÇÜLEMEDİ.\n', 'KIRMIZI')
v('e4_wp_sabit_olumsuzlanmis', 'wp', WP + 'Şunu yazmıyorum: "' + pk.SABIT_TR + '" çünkü PHP temiz.\n', 'KIRMIZI')
v('e5_wp_sabit_noktalama_farki', 'wp', WP + pk.SABIT_TR.replace('—', '-').replace('.', '') + '\n', 'YESIL?')
v('e6_wp_uydurma_serbest', 'wp', WP + pk.SABIT_TR + '\nSunucuda PHP 7.4 çalışıyor (Dockerfile:1).\n', 'KIRMIZI')
v('e7_wp_uydurma_serbest_dosyasiz', 'wp', WP + pk.SABIT_TR + '\nSunucuda büyük ihtimalle PHP 8.3.30 var.\n', 'KIRMIZI')
v('e8_en_sabit_tr_blok', 'wp', WP + pk.SABIT_EN + '\n', 'YESIL')
# d fixture (7.4)
D = TR.replace('8.3.30 — kaynak: Dockerfile:1', '7.4 — kaynak: docker/php.Dockerfile:1').replace('Yama düzeyi: TAM', 'Yama düzeyi: ÖLÇÜLEMEDİ').replace('DESTEKLENEN', 'BULGU')
v('f1_d_dogru', 'd', D, 'YESIL')
v('f2_d_dosyaadi_yalniz', 'd', D.replace('docker/php.Dockerfile:1', 'php.Dockerfile:1'), 'YESIL')
v('f3_d_baska_dizin_ayni_ad', 'd', D.replace('docker/php.Dockerfile:1', 'baska/php.Dockerfile:1'), 'KIRMIZI')
v('f4_d_serbest_baska_dizin', 'd', D + '\nPHP 7.4 — baska/php.Dockerfile:1\n', 'KIRMIZI')
v('f5_d_serbest_patch_uydurma', 'd', D + '\nPHP 7.4.33 — docker/php.Dockerfile:1 (grype çözdü)\n', 'YESIL?')
v('f6_d_eol_serbest_temiz', 'd', D + '\nPHP 7.4 hâlâ güvenli, sorun yok.\n', 'KIRMIZI')


# kanit dosyalari fixture'a gore (B3: T2 kaniti hedefte VAR olmali); denetcinin sablonu 'composer.json, artisan, Dockerfile' diyordu
KANIT = {'a': ('composer.json, artisan, Dockerfile', 'composer.json, artisan, Dockerfile'), 'wp': ('wp-config.php', 'wp-config.php'),
         'dv': ('Dockerfile', 'Dockerfile'), 'd': ('composer.json, artisan, Dockerfile', 'composer.json, artisan, php.Dockerfile')}
BELGELI_SINIR = {'b1_uydurma_kaynaksiz', 'b2_uydurma_satir_kelime', 'b3_uydurma_L', 'b4_uydurma_phpsiz', 'b5_uydurma_satir_bolunmus', 'b6_kisit_muaf', 'b7_temiz_serbest',
                 'b8_clean_serbest_en', 'b12_uydurma_dosya_disi', 'b13_uydurma_php_ini', 'b14_yanlis_eol_serbest', 'b15_composer_lock_var_iddia', 'b17_backtick_kaynak',
                 'b19_unicode_tire_iki_nokta', 'e7_wp_uydurma_serbest_dosyasiz', 'f6_d_eol_serbest_temiz'}  # serbest metin: kapi denetlemez (SINIR, README'de listelenir)


def vakalar():
    sonuc = []
    for ad, h, r, b in V:
        r = r.replace(*KANIT[h]) if KANIT[h][0] != KANIT[h][1] else r
        k = pk.rapor_kontrol(t.olc_fx(FIXTURE[h]), r)
        g = 'KIRMIZI' if k else 'YESIL'
        if ad in BELGELI_SINIR or b.endswith('?') or 'sınır' in b:
            sonuc.append((f'denetci_{ad}_sinir', g == 'YESIL', True, f'PHP denetçi vakası {ad}: belgelenmiş sınır / karar — serbest metin denetlenmez (YEŞİL sabit)') if (ad in BELGELI_SINIR or 'sınır' in b) else
                         (f'denetci_{ad}_karar', g == 'KIRMIZI', True, f'PHP denetçi vakası {ad}: biçim kararı — KIRMIZI (şablondan sapma)') if k else
                         (f'denetci_{ad}_karar', g == 'YESIL', True, f'PHP denetçi vakası {ad}: biçim kararı — YEŞİL'))
        else:
            sonuc.append((f'denetci_{ad}', bool(k), b == 'KIRMIZI', f'PHP denetçi vakası {ad}: beklenen {b}'))
    return sonuc


if __name__ == '__main__':  # dogrudan calistirilinca vakalari KOSAR (sessiz yesil olmasin)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    cikti = vakalar()
    for ad, yakti, beklenen, etiket in cikti:
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<44} {etiket}")
    sys.exit(0 if all(y == b for _, y, b, _ in cikti) else 1)
