"""php_oz_test.py — gedik v2.7.0: PHP kapisinin KOR KAPI OZ-TESTI (D1/D2). Fixture'lar satir ici (dosya fixture'i yok), her biri gecici dizine yazilir.

kapilar.py altin kumesi `oz_test_vakalari()` ile [(ad, yakti_mi, beklenen, etiket)] alir; hepsinde yakti == beklenen olmali.
Bozuk vaka KIRMIZI, temiz vaka YESIL yakmali. Dedektor mutantlari (surum cozucu / EOL / imaj dosyasi bozulursa) golden kontrolunu kirmizi yakmali.
"""
import contextlib
import io
import os
import sys
import tempfile
from datetime import date

import php_kapisi as pk
import php_olc

LARAVEL = {'composer.json': '{"require": {"php": "^8.2", "laravel/framework": "^11.0"}}\n', 'artisan': '#!/usr/bin/env php\n<?php\n',
           'app/Http/Controllers/UserController.php': '<?php\nclass UserController {}\n'}
FX = {
    'a': dict(LARAVEL, Dockerfile='FROM php:8.3.30-fpm\nRUN docker-php-ext-install pdo_mysql\n'),
    'b': dict(LARAVEL, Dockerfile='FROM php:8.3.30-fpm\n', **{'composer.lock': '{"packages": []}\n'}),
    'c': {'wp-config.php': '<?php\ndefine("DB_NAME", "x");\n', 'index.php': '<?php\nrequire "wp-blog-header.php";\n',
          'wp-content/themes/t/functions.php': '<?php\n', 'wp-includes/version.php': "<?php\n$wp_version = '6.5';\n",
          '.htaccess': '# BEGIN WordPress\nRewriteEngine On\n# END WordPress\n'},
    '81': dict(LARAVEL, Dockerfile='FROM php:8.1\n'),
    '82': dict(LARAVEL, Dockerfile='FROM php:8.2.28-apache\n'),
    'kisit': {'composer.json': '{"require": {"php": ">=7.4"}}\n', 'index.php': '<?php\n'},
    'plat': {'composer.json': '{"config": {"platform": {"php": "8.1.5"}}, "require": {"php": ">=7.4"}}\n', 'index.php': '<?php\n'},
    'yuzen': dict(LARAVEL, Dockerfile='FROM docker.io/library/php:8-apache\n'),
    'celiski': dict(LARAVEL, Dockerfile='FROM php:8.3.30-fpm\n', **{'docker-compose.prod.yml': 'services:\n  a:\n    image: php:7.4-apache\n'}),
    'asama': dict(LARAVEL, Dockerfile='FROM php:8.1-cli AS build\nFROM php:8.3.30-fpm AS runtime\n'),
    'htaccess': {'.htaccess': 'AddHandler application/x-httpd-ea-php74 .php\n', 'index.php': '<?php\n'},
    'fpm': {'php-fpm.d/www.conf': '[www]\npm = dynamic\n'},
    'compose': {'docker-compose.yml': 'services:\n  a:\n    image: php:8.0.30-cli\n'},
    'ci': {'.github/workflows/ci.yml': 'jobs:\n  t:\n    steps:\n      - uses: shivammathur/setup-php@v2\n        with:\n          php-version: 8.3\n', 'index.php': '<?php\n'},
    'ci_blok': {'.travis.yml': 'language: php\nphp:\n  - 7.4\n  - 8.0\n', 'index.php': '<?php\n'},
    'phpver': {'.php-version': 'php-8.2.4\n', 'index.php': '<?php\n'},
    'platform': {'.platform.app.yaml': 'type: "php:8.3"\n', 'index.php': '<?php\n'},
    'appyaml': {'app.yaml': 'runtime: php83\n', 'index.php': '<?php\n'},
    'yorum': {'Dockerfile': '# FROM php:7.4\nFROM php:8.3.30-fpm # son\n', 'index.php': '<?php\n'},
    'yorum_phpver': {'.php-version': '# eski 7.4\n8.2.4\n', 'index.php': '<?php\n'},
    'arg': {'Dockerfile': 'ARG PHP_VERSION=8.1\nFROM php:${PHP_VERSION}-fpm\n', 'index.php': '<?php\n'},
    'wordpress': {'Dockerfile': 'FROM wordpress:6.5-php8.1-apache\n', 'index.php': '<?php\n'},
    'major7': {'Dockerfile': 'FROM php:7-apache\n', 'index.php': '<?php\n'},
    'ucuncu': {'Dockerfile': 'FROM myorg/php:2.0\n', 'index.php': '<?php\n'},
    'containerfile': {'Containerfile': 'FROM php:8.3.30-cli\n', 'index.php': '<?php\n'},
    'monorepo': {'backend/composer.json': '{}\n', 'backend/composer.lock': '{}\n', 'backend/artisan': '<?php\n', 'backend/Dockerfile': 'FROM php:8.3.30-fpm\n'},
    'bom': {'composer.json': '\ufeff{"config": {"platform": {"php": "8.1.5"}}}\n', 'index.php': '<?php\n'},
    'dev': {'Dockerfile': 'FROM php:8.3.30-fpm\n', 'tests/fixtures/composer.json': '{"config": {"platform": {"php": "7.4.1"}}}\n', 'index.php': '<?php\n'},
    'dev_huge': {'Dockerfile': 'FROM php:' + '9' * 5000 + '.1\n', 'index.php': '<?php\n'},
    'plat_op': {'composer.json': '{"config": {"platform": {"php": ">=8.1.5"}}}\n', 'index.php': '<?php\n'},
    'major7_phpver': {'Dockerfile': 'FROM php:7-apache\n', '.php-version': '8.2.4\n', 'index.php': '<?php\n'},
    'ci_ilk_dash': {'.travis.yml': '  - 7.4\nphp:\n  - 8.0\n', 'index.php': '<?php\n'},
    'htaccess_duz': {'.htaccess': 'RewriteEngine On\nOptions -Indexes\n'},
    'htaccess_yalniz': {'.htaccess': 'AddHandler application/x-httpd-ea-php74 .php\n'},
    'notlar': {'notlar.txt': 'FROM php:8.3.30-fpm\n'},
    'asama_yuzen': {'Dockerfile': 'FROM php:8.1-cli AS build\nFROM php:8-apache\n', 'index.php': '<?php\n'},
    'ayni_dal': {'Dockerfile': 'FROM php:8.3.30-fpm\n', 'docker-compose.yml': 'services:\n  a:\n    image: php:8.3.31-cli\n', 'index.php': '<?php\n'},
    'ci_ilgisiz': {'.travis.yml': 'node_js:\n  - 6.9\n  - 8.1\n', 'index.php': '<?php\n'},
    'ci_blok2': {'.travis.yml': 'php:\n  - 7.4\nnode_js:\n  - 6.9\n', 'index.php': '<?php\n'},
    'kutuphane_plat': {'composer.json': '{"config": {"platform": {"php": "8.3.30"}}}\n', 'src/U.php': '<?php\n'},
    'dal83': dict(LARAVEL, Dockerfile='FROM php:8.3-fpm\n'),
    'float7ci': {'Dockerfile': 'FROM php:7-apache\n', 'index.php': '<?php\n',
                 '.github/workflows/ci.yml': 'jobs:\n  t:\n    steps:\n      - uses: shivammathur/setup-php@v2\n        with:\n          php-version: 8.3\n'},
    'kutuphane': {'composer.json': '{"name": "acme/util", "require": {"php": ">=8.1"}}\n', 'src/Util.php': '<?php\nclass Util {}\n'},
}
GOLDEN = {  # fixture -> olcumun tutmasi gereken alanlar (imaj/kaynak silinince ya da dedektor bozulunca KIRMIZI)
    'a': {'php': True, 'surum': '8.3.30', 'kaynak': 'Dockerfile:1', 'tam': True, 'eol': 'tamam', 'composer_lock': False, 'celiski': False, 'ci_surumleri': []},
    'b': {'surum': '8.3.30', 'composer_lock': True},
    'c': {'php': True, 'surum': None, 'yuzen': None, 'composer_json': False},
    '81': {'surum': '8.1', 'tam': False, 'eol': 'yok_yama'},
    '82': {'surum': '8.2.28', 'eol': 'uyari'},
    'plat': {'surum': '8.1.5', 'kaynak': 'composer.json:1', 'eol': 'yok_yama'},
    'celiski': {'celiski': True, 'surumler': ['7.4', '8.3.30'], 'eol': 'yok_yama'},
    'asama': {'surum': '8.3.30', 'eol': 'tamam'},
    'htaccess': {'surum': '7.4', 'kaynak': '.htaccess:1', 'eol': 'yok_yama'},
    'fpm': {'php': True, 'surum': None},
    'compose': {'surum': '8.0.30', 'kaynak': 'docker-compose.yml:3', 'eol': 'yok_yama'},
    'ci': {'surum': '8.3', 'yalniz_ci': True, 'eol': None},
    'ci_blok': {'surum': '7.4', 'yalniz_ci': True},
    'phpver': {'surum': '8.2.4', 'kaynak': '.php-version:1'},
    'platform': {'surum': '8.3', 'kaynak': '.platform.app.yaml:1'},
    'appyaml': {'surum': '8.3', 'kaynak': 'app.yaml:1'},
    'yorum': {'surum': '8.3.30', 'kaynak': 'Dockerfile:2'},
    'yorum_phpver': {'surum': '8.2.4', 'kaynak': '.php-version:2'},
    'arg': {'surum': '8.1', 'eol': 'yok_yama'},
    'wordpress': {'surum': '8.1', 'eol': 'yok_yama'},
    'major7': {'surum': None, 'eol': 'yok_yama', 'tam': False},
    'ucuncu': {'surum': None, 'yuzen': None},
    'containerfile': {'surum': '8.3.30'},
    'monorepo': {'composer_json': True, 'composer_lock': True, 'surum': '8.3.30'},
    'bom': {'surum': '8.1.5'},
    'dev': {'surum': '8.3.30', 'composer_json': False},
    'plat_op': {'surum': '8.1.5'},
    'major7_phpver': {'eol': 'yok_yama', 'en_eski': '7.x'},
    'ci_ilk_dash': {'ci_surumleri': ['8.0']},
    'htaccess_duz': {'php': False},
    'htaccess_yalniz': {'php': True, 'isaretler': ['.htaccess (PHP işleyici)'], 'surum': '7.4'},
    'notlar': {'php': False},
    'asama_yuzen': {'surum': None, 'yalniz_ci': False, 'ci_surumleri': []},
    'ayni_dal': {'celiski': False, 'surumler': ['8.3.30', '8.3.31']},
    'ci_ilgisiz': {'surum': None, 'ci_surumleri': []},
    'ci_blok2': {'ci_surumleri': ['7.4']},
    'kutuphane_plat': {'guclu': False, 'surum': '8.3.30'},
    'dal83': {'surum': '8.3', 'tam': False, 'eol': 'tamam'},
    'float7ci': {'surum': '8.3', 'yalniz_ci': True, 'eol': 'yok_yama', 'en_eski': '7.x'},
    'kutuphane': {'php': True, 'guclu': False, 'surum': None, 'yuzen': None, 'composer_lock': False},
}
GUCLU_BEKLENEN = {'a': True, 'c': True, 'fpm': True, 'htaccess': True, 'kutuphane': False}  # imza gucu (zayif imza: yalniz composer.json / *.php)
T2 = '- T2 (server code): yes — PHP\n'
LOCKYOK = '- composer.lock yok — composer audit koşmaz, ÖLÇÜLEMEDİ\n'
KARS = ' güncel yamalı sürümle karşılaştırma ÖLÇÜLEMEDİ (tarayıcı yok)'
RAPOR = {
    'a': '- T2 (server code): yes — PHP (Laravel; artisan, composer.json)\n- PHP çalışma zamanı: 8.3.30 — Dockerfile:1;' + KARS + '\n' + LOCKYOK,
    'b': T2 + '- PHP çalışma zamanı: 8.3.30 — Dockerfile:1;' + KARS + '\n- composer audit: 0 advisory (kritik/yüksek 0)\n',
    'c': '- T2 (sunucu kodu): evet — PHP (WordPress)\n- ' + pk.SABIT_TR + '\n- composer.json yok.\n',
    '81': T2 + '- PHP 8.1 — Dockerfile:1 (yama düzeyi ÖLÇÜLEMEDİ);' + KARS + '; EOL: resmî güvenlik yaması yok → bulgu\n' + LOCKYOK,
    '82': T2 + '- PHP 8.2.28 — Dockerfile:1;' + KARS + '; güvenlik desteği 2026-12-31 EOL → uyarı\n' + LOCKYOK,
    'kisit': T2 + '- ' + pk.SABIT_TR + '\n- composer.lock yok — ÖLÇÜLEMEDİ\n',
    'yuzen': T2 + '- PHP çalışma zamanı: php:8-apache — Dockerfile:1 (yüzen etiket; dal/yama düzeyi ÖLÇÜLEMEDİ)\n' + LOCKYOK,
    'celiski': T2 + '- PHP 8.3.30 — Dockerfile:1;' + KARS + '; ÇELİŞKİ: docker-compose.prod.yml:3 php:7.4 — EOL: güvenlik yaması yok → bulgu\n' + LOCKYOK,
    'htaccess': T2 + '- PHP 7.4 — .htaccess:1 (AddHandler; yama düzeyi ÖLÇÜLEMEDİ);' + KARS + '; EOL: güvenlik yaması yok → bulgu\n',
    'dal83': T2 + '- PHP çalışma zamanı: 8.3 — Dockerfile:1 (etiket php:8.3-fpm; eksik düzey ÖLÇÜLMEDİ);' + KARS + '\n' + LOCKYOK,
    'float7ci': T2 + '- PHP 8.3 — ci.yml:6 (CI matrisi; canlı sürüm ÖLÇÜLEMEDİ; yama düzeyi ÖLÇÜLEMEDİ)\n'
                '- Dockerfile:1 php:7-apache (yüzen etiket; düzey ÖLÇÜLEMEDİ); PHP 7: EOL, güvenlik yaması yok → bulgu\n',
    'kutuphane': '- T2 (server code): composer.json + src/Util.php — PHP kütüphanesi, sunucu giriş noktası yok\n' + LOCKYOK,
}


# ---------- yardimcilar ----------
TEST_BUGUN = date(2026, 10, 22)  # deterministik: 2026-12-31 sonrası 8.2 davranışı ayrı vaka (bugun_82_sonrasi)


def olc_fx(dosyalar, bugun=TEST_BUGUN):
    with tempfile.TemporaryDirectory() as t:
        for yol, icerik in dosyalar.items():
            hedef = os.path.join(t, *yol.split('/'))
            os.makedirs(os.path.dirname(hedef), exist_ok=True)
            with open(hedef, 'w', encoding='utf-8', newline='') as f:
                f.write(icerik)
        return php_olc.olc(t, bugun)


def kapi(fx, rapor, bugun=TEST_BUGUN):
    return bool(pk.rapor_kontrol(olc_fx(FX[fx], bugun), rapor))


def kodlar(fx, rapor, bugun=TEST_BUGUN):
    return pk.rapor_kontrol(olc_fx(FX[fx], bugun), rapor)


def sapma(fx, dosyalar=None):
    return bool(pk.golden_kontrol(olc_fx(dosyalar or FX[fx]), GOLDEN[fx]))


@contextlib.contextmanager
def dedektor_mutanti(ad, yeni):
    eski = getattr(php_olc, ad)
    setattr(php_olc, ad, yeni)
    try:
        yield
    finally:
        setattr(php_olc, ad, eski)


def cli(args):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        try:
            return pk.main(args)
        except SystemExit as e:  # argparse hatasi
            return e.code


def cli_cikti(args):
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon), contextlib.redirect_stderr(io.StringIO()):
        kod = pk.main(args)
    return kod, tampon.getvalue()


def cli_vaka(fx, rapor, kodlama='utf-8', cikti=False):
    with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as h:
        for yol, icerik in FX[fx].items():
            hedef = os.path.join(h, *yol.split('/'))
            os.makedirs(os.path.dirname(hedef), exist_ok=True)
            with open(hedef, 'w', encoding='utf-8', newline='') as f:
                f.write(icerik)
        rp = os.path.join(t, 'rapor.md')
        with open(rp, 'wb') as f:
            f.write(rapor.encode(kodlama))
        return cli_cikti(['--hedef', h, '--rapor', rp])[1] if cikti else cli(['--hedef', h, '--rapor', rp])


def golden_vakalari():
    """Her fixture'in olcumu golden'a UYAR (yanlis-pozitif yok); imza gucu (guclu/zayif) ayri dogrulanir."""
    guclu = [(f'guclu_{k}', olc_fx(FX[k])['guclu'] != v, False, f'PHP imza gücü: {k} = {v}') for k, v in GUCLU_BEKLENEN.items()]
    return [(f'golden_{k}', sapma(k), False, f'PHP olçüm golden: {k}') for k in GOLDEN] + guclu


def dedektor_mutantlari():
    """Dedektor bozulursa golden KIRMIZI yakmali (kor kapi degil)."""
    with dedektor_mutanti('surum_coz', lambda e: (None, False, None)):
        a = sapma('a')
    with dedektor_mutanti('eol_durumu', lambda s, a, b: 'tamam'):
        e = sapma('81')
    with dedektor_mutanti('IMAJ_DOSYASI', php_olc.re.compile(r'^$')):
        c = sapma('compose') or sapma('a')
    with dedektor_mutanti('uyari_yolu', lambda y: False):
        d = sapma('dev')
    with dedektor_mutanti('yorumsuz', lambda m: m.splitlines()):
        y = sapma('yorum_phpver')
    return [('mutant_surum_coz', a, True, 'PHP dedektör mutantı: sürüm çözücü bozuk → golden KIRMIZI'),
            ('mutant_eol', e, True, 'PHP dedektör mutantı: EOL hep "tamam" → golden KIRMIZI'),
            ('mutant_imaj_dosyasi', c, True, 'PHP dedektör mutantı: imaj dosyası tanınmıyor → golden KIRMIZI'),
            ('mutant_test_yolu', d, True, 'PHP dedektör mutantı: test yolu kaynak sayılıyor → golden KIRMIZI'),
            ('mutant_yorum', y, True, 'PHP dedektör mutantı: yorum satırı kaynak sayılıyor → golden KIRMIZI')]


def fixture_mutantlari():
    return [('a_imaj_silindi', sapma('a', dict(FX['a'], Dockerfile='RUN docker-php-ext-install pdo_mysql\n')), True, 'PHP (a) imaj satırı silinince KIRMIZI'),
            ('plat_silindi', sapma('plat', {'composer.json': '{"require": {"php": ">=7.4"}}\n', 'index.php': '<?php\n'}), True,
             'PHP platform satırı silinince KIRMIZI (require sürüm sayılmaz)'),
            ('huge_cokmez', bool(olc_fx(FX['dev_huge'])['php']), True, 'PHP 5000 haneli sürüm: ölçüm çökmez'),
            ('imzasiz_atlanir', bool(pk.rapor_kontrol(olc_fx({'main.py': 'print(1)\n'}), 'rapor')), False, 'PHP imzası yok: kapı uygulanmaz'),
            ('bugun_82_sonrasi', olc_fx(FX['82'], date(2027, 1, 2))['eol'] == 'yok_yama', True, 'PHP 8.2 güvenlik desteği bitince EOL=yok_yama'),
            ('bugun_82_son_gun', olc_fx(FX['82'], date(2026, 12, 31))['eol'] != 'uyari', False, 'PHP 8.2: 2026-12-31 dahil hâlâ uyarı'),
            ('buyuk_dosya_kesildi', bool(olc_fx({'Dockerfile': 'FROM php:8.3.30-fpm\n' + '#' * 1_000_100, 'index.php': '<?php\n'})['okunamayan']), True, 'PHP 1 MB üstü dosya: KESİLDİ kaydı'),
            ('tam_sinir_dosya', bool(olc_fx({'Dockerfile': 'FROM php:8.3.30-fpm\n' + '#' * (php_olc.ENC_SINIR - 20), 'index.php': '<?php\n'})['okunamayan']), False, 'PHP tam sınır boyutlu dosya kesilmez: yanlış-pozitif')]


def rapor_vakalari():
    r, a = RAPOR, 'a'
    sil = lambda k, eski, yeni='': r[k].replace(eski, yeni)  # noqa: E731
    return [
        ('a_temiz', kapi(a, r['a']), False, 'PHP (a) rapor: yanlış-pozitif'),
        ('a_surumsuz', kapi(a, sil('a', '8.3.30', 'x')), True, 'PHP (a) rapor sürümü yazmıyor'),
        ('a_sinir', kapi(a, sil('a', '8.3.30', '8.3.3')), True, 'PHP (a) rapor sürümü kısaltıp uyduruyor (8.3.3 ≠ 8.3.30)'),
        ('a_kaynaksiz', kapi(a, sil('a', 'Dockerfile:1', 'yok')), True, 'PHP (a) rapor kaynağı yazmıyor'),
        ('a_t2_yok', kapi(a, sil('a', 'yes — PHP (Laravel; artisan, composer.json)', 'unknown')), True, 'PHP (a) T2 satırı PHP demiyor'),
        ('a_t2_hayir', kapi(a, sil('a', 'yes — PHP', 'no. PHP not used')), True, 'PHP (a) T2 "no" diyor'),
        ('a_temiz_denmis', kapi(a, r['a'] + '- PHP runtime 8.3.30 — Dockerfile:1: clean, fully patched, safe\n'), True, 'PHP (a) çözülü sürümde "clean" iddiası'),
        ('a_temiz_ama', kapi(a, r['a'] + '- PHP çalışma zamanı sürümü ÖLÇÜLEMEDİ ama temiz görünüyor\n'), True, 'PHP (a) "ÖLÇÜLEMEDİ ama temiz" yazılmış'),
        ('a_temiz_olumsuz', kapi(a, r['a'] + '- PHP çalışma zamanı için "temiz" denmiyor (not calling it clean)\n'), False, 'PHP (a) "temiz denmez" yazılmış: yanlış-pozitif'),
        ('a_composer_satirsiz', kapi(a, sil('a', LOCKYOK)), True, 'PHP (a) composer.json var, lock/audit satırı hiç yok'),
        ('a_pencere', kapi(a, sil('a', LOCKYOK, '- composer.lock yok.\n- Paket CVE durumu ÖLÇÜLEMEDİ (composer audit koşmaz).\n')), False, 'PHP (a) lock/ÖLÇÜLEMEDİ bitişik satırlarda: yanlış-pozitif'),
        ('b_temiz', kapi('b', r['b']), False, 'PHP (b) composer.lock + audit sayısı: yanlış-pozitif'),
        ('b_audit_yok', kapi('b', r['a']), True, 'PHP (b) lock var, rapor "lock yok" diyor'),
        ('b_audit_satirsiz', kapi('b', sil('b', '- composer audit: 0 advisory (kritik/yüksek 0)\n')), True, 'PHP (b) audit satırı hiç yok'),
        ('b_audit_olculemedi', kapi('b', sil('b', '0 advisory (kritik/yüksek 0)', 'ÖLÇÜLEMEDİ (composer yok)')), False, 'PHP (b) audit ÖLÇÜLEMEDİ yazılmış: yanlış-pozitif'),
        ('c_temiz', kapi('c', r['c']), False, 'PHP (c) WordPress sürümsüz + sabit satır: yanlış-pozitif'),
        ('c_sahte_temiz', kapi('c', r['c'] + '- PHP çalışma zamanı: temiz\n'), True, 'PHP (c) "temiz" yazan sahte rapor'),
        ('c_sabit_ek', kapi('c', sil('c', pk.SABIT_TR, pk.SABIT_TR + ' Ancak çalışma zamanı temiz görünüyor.')), True, 'PHP (c) sabit satırın ardına "temiz görünüyor" eklenmiş'),
        ('c_satirsiz', kapi('c', sil('c', pk.SABIT_TR, 'PHP not ediliyor')), True, 'PHP (c) sabit ÖLÇÜLEMEDİ satırı yok'),
        ('c_en_satir', kapi('c', sil('c', pk.SABIT_TR, pk.SABIT_EN)), False, 'PHP (c) İngilizce sabit satır: yanlış-pozitif'),
        ('c_kalin', kapi('c', sil('c', pk.SABIT_TR, '**' + pk.SABIT_TR.rstrip('.') + '**')), False, 'PHP (c) kalın/noktasız sabit satır: yanlış-pozitif'),
        ('c_uydurma_surum', kapi('c', r['c'] + '- PHP çalışma zamanı: 8.3.30 — Dockerfile:1\n'), True, 'PHP (c) depoda olmayan sürüm+kaynak uyduruyor'),
        ('a_uydurma_ek', kapi(a, r['a'] + '- PHP 8.4.2 — Dockerfile:9 (en güncel, yamalı)\n'), True, 'PHP (a) gerçek sürümün yanına uydurma ikinci sürüm+kaynak'),
        ('81_bulgu', kapi('81', r['81']), False, 'PHP 8.1 EOL bulgusu yazılmış: yanlış-pozitif'),
        ('81_bulgusuz', kapi('81', sil('81', 'EOL: resmî güvenlik yaması yok → bulgu', 'sürüm bilgisi')), True, 'PHP 8.1 bulgu yoksa KIRMIZI'),
        ('81_eol_degil', kapi('81', sil('81', 'EOL: resmî güvenlik yaması yok → bulgu', 'NOT EOL, still receives security patches')), True, 'PHP 8.1 "EOL değil" yazan sahte rapor'),
        ('81_yama_duzeyi_yok', kapi('81', sil('81', ' (yama düzeyi ÖLÇÜLEMEDİ)')), True, 'PHP 8.1 dal-only etikette yama düzeyi belirsizliği yazılmamış'),
        ('82_uyari', kapi('82', r['82']), False, 'PHP 8.2 uyarısı yazılmış: yanlış-pozitif'),
        ('82_uyarisiz', kapi('82', sil('82', '2026-12-31 EOL → uyarı', 'destekleniyor')), True, 'PHP 8.2 uyarı yoksa KIRMIZI'),
        ('kisit_temiz', kapi('kisit', r['kisit']), False, 'PHP require kısıtı sürüm sayılmadı: yanlış-pozitif'),
        ('kisit_sayilmis', kapi('kisit', r['kisit'] + '- PHP 7.4 çalışma zamanı (composer.json)\n'), True, 'PHP require kısıtı sürüm sayıldı'),
        ('yuzen_temiz', kapi('yuzen', r['yuzen']), False, 'PHP yüzen etiket kaynağıyla yazılmış: yanlış-pozitif'),
        ('yuzen_etiketsiz', kapi('yuzen', sil('yuzen', 'Dockerfile:1', 'x')), True, 'PHP yüzen etiketin kaynağı yazılmamış'),
        ('yuzen_temiz_denmis', kapi('yuzen', r['yuzen'] + '- PHP çalışma zamanı: temiz\n'), True, 'PHP yüzen etikette "temiz" yazan sahte rapor'),
        ('celiski_temiz', kapi('celiski', r['celiski']), False, 'PHP çelişen kaynaklar yazılmış: yanlış-pozitif'),
        ('celiski_gizli', kapi('celiski', sil('celiski', '; ÇELİŞKİ: docker-compose.prod.yml:3 php:7.4 — EOL: güvenlik yaması yok → bulgu')), True, 'PHP çelişen kaynak (7.4) yazılmamış'),
        ('htaccess_temiz', kapi('htaccess', r['htaccess']), False, 'PHP .htaccess işleyici sürümü yazılmış: yanlış-pozitif'),
        ('htaccess_sabit_satir', kapi('htaccess', T2 + '- ' + pk.SABIT_TR + '\n'), True, 'PHP .htaccess sürümü VAR ama "depoda yok" yazılmış'),
        ('ci_etiketsiz', kapi('ci', T2 + '- PHP 8.3 — ci.yml:6 çalışma zamanı\n'), True, 'PHP yalnız-CI sürümü CI olarak belirtilmemiş'),
        ('ci_temiz', kapi('ci', T2 + '- PHP 8.3 — ci.yml:6 (CI matrisi; canlı sürüm ÖLÇÜLEMEDİ; yama düzeyi ÖLÇÜLEMEDİ)\n'), False, 'PHP yalnız-CI sürümü CI olarak yazılmış: yanlış-pozitif'),
    ] + rapor_vakalari_2()


def rapor_vakalari_2():
    """Bagimsiz incelemelerin buldugu atlatma/yanlis-pozitif vektorleri (2. tur) ve gercek model raporlarindan alinan kaliplar."""
    r, a = RAPOR, 'a'
    sil = lambda k, eski, yeni='': r[k].replace(eski, yeni)  # noqa: E731
    return [
        ('a_karsilastirma_yok', kapi(a, sil('a', KARS)), True, 'PHP (a) yamalı sürümle karşılaştırma/tarayıcı satırı yok'),
        ('a_t2_eko_temiz', kapi(a, sil('a', 'yes — PHP (Laravel; artisan, composer.json)', 'YES. composer.json requires laravel/framework; there is an artisan file.')), False, 'PHP (a) T2 satırı PHP yazmadan ekosistemi anlatıyor: yanlış-pozitif'),
        ('htaccess_t2_dogal', kapi('htaccess', sil('htaccess', T2, '| T2 Server code | **Minimal PHP.** `.htaccess` has a PHP handler; there is no `composer.json`, framework, or router. |\n')), False, 'PHP T2 doğal dil tablo satırı: yanlış-pozitif'),
        ('81_tr_sablon', kapi('81', sil('81', '- PHP 8.1 —', '- PHP çalışma zamanı: 8.1 —')), False, 'PHP şablon satırı "çalışma zamanı" + "güvenlik yaması yok": yanlış-pozitif (güvenlik≠güvenli)'),
        ('82_tr_sablon', kapi('82', sil('82', '- PHP 8.2.28 —', '- PHP sürümü: 8.2.28 —')), False, 'PHP sürüm satırı + "güvenlik desteği": yanlış-pozitif'),
        ('a_clean_en', kapi(a, r['a'] + '- PHP runtime 8.3.30 — Dockerfile:1: clean, not vulnerable\n'), True, 'PHP (a) EN "clean, not vulnerable"'),
        ('a_k4_clean_copy', kapi(a, r['a'] + '- K4: the version extractor read PHP 7.4 on the mutant; the clean copy read 8.3.30\n'), False, 'PHP (a) K4 "clean copy" jargonu iddia sayılmaz: yanlış-pozitif'),
        ('a_k4_temiz_surum', kapi(a, r['a'] + '- K4: PHP sürüm okuyucusu temiz sürümde 8.3.30 okudu\n'), False, 'PHP (a) K4 "temiz sürümde" jargonu: yanlış-pozitif'),
        ('a_sorun_degil', kapi(a, r['a'] + '- PHP çalışma zamanı sürümü temiz, sorun değil\n'), True, 'PHP (a) "temiz, sorun değil" (değil ayrı sözcük)'),
        ('a_is_patched', kapi(a, r['a'] + '- PHP 8.3.30 runtime is fully patched\n'), True, 'PHP (a) "is fully patched"'),
        ('c_en_not_but_clean', kapi('c', r['c'] + '- PHP runtime version NOT MEASURED, but the stack looks clean\n'), True, 'PHP (c) EN "NOT MEASURED, but ... clean"'),
        ('c_sonraki_satir', kapi('c', r['c'] + '- PHP çalışma zamanı sürümü ÖLÇÜLEMEDİ\n  Sonuç: temiz\n'), True, 'PHP (c) "temiz" bir sonraki satırda'),
        ('c_not_calling_clean', kapi('c', r['c'] + '- PHP runtime: I am not calling it "clean"\n'), False, 'PHP (c) "not calling it clean": yanlış-pozitif'),
        ('dal83_temiz', kapi('dal83', r['dal83']), False, 'PHP dal etiketi "eksik düzey ÖLÇÜLMEDİ" (SKILL.md sözleşmesi): yanlış-pozitif'),
        ('dal83_en', kapi('dal83', sil('dal83', 'eksik düzey ÖLÇÜLMEDİ', 'the missing level NOT MEASURED')), False, 'PHP dal etiketi EN "missing level NOT MEASURED": yanlış-pozitif'),
        ('dal83_belirsizlik_yok', kapi('dal83', sil('dal83', ' (etiket php:8.3-fpm; eksik düzey ÖLÇÜLMEDİ)')), True, 'PHP dal etiketi: eksik düzey belirtilmemiş'),
        ('b_audit_sorun_yok', kapi('b', sil('b', '0 advisory (kritik/yüksek 0)', 'sorun yok')), True, 'PHP (b) composer audit sayısız "sorun yok"'),
        ('b_audit_sonraki_satir', kapi('b', sil('b', 'composer audit: 0 advisory (kritik/yüksek 0)', 'composer audit:\n  sonuç ÖLÇÜLEMEDİ (composer yok)')), False, 'PHP (b) audit sonucu hemen ardındaki satırda: yanlış-pozitif'),
        ('b_audit_v27', kapi('b', sil('b', 'composer audit: 0 advisory (kritik/yüksek 0)', 'composer audit v2.7 not needed')), True, 'PHP (b) "composer audit v2.7" sürüm numarası sayı sayılmaz'),
        ('ci_golgeler_yuzen7', kapi('float7ci', r['float7ci']), False, 'PHP CI 8.3 + yüzen php:7 yazılmış: yanlış-pozitif'),
        ('ci_golgeler_yuzen7_gizli', kapi('float7ci', sil('float7ci', '- Dockerfile:1 php:7-apache (yüzen etiket; düzey ÖLÇÜLEMEDİ); PHP 7: EOL, güvenlik yaması yok → bulgu\n')), True, 'PHP CI sürümü yüzen php:7 çalışma zamanını gizliyor'),
        ('81_aktif_destek', kapi('81', sil('81', 'EOL: resmî güvenlik yaması yok → bulgu', 'actively receives security patches')), True, 'PHP 8.1 "actively receives security patches" EOL kanıtı sayılmaz'),
        ('81_eol_hayir', kapi('81', sil('81', 'EOL: resmî güvenlik yaması yok → bulgu', 'EOL: hayır, destek sürüyor')), True, 'PHP 8.1 "EOL: hayır" EOL kanıtı sayılmaz'),
        ('eol_baska_madde_safe', kapi('81', r['81'] + '- PHP runtime ayrıntıları aşağıda\n  - Neither state is safe to ship.\n'), False, 'PHP sonraki madde işaretli satırdaki "safe" başka konu: yanlış-pozitif'),
        ('eol_karssiz', kapi('htaccess', sil('htaccess', KARS)), False, 'PHP EOL dalında yamalı-sürüm karşılaştırması istenmez'),
        ('a_t2_ek_satir', kapi(a, r['a'] + '- T2 notu: ayrıntılar aşağıda\n'), False, 'PHP (a) ikinci nötr T2 satırı: yanlış-pozitif'),
        ('a_t2_olumsuz_ek', kapi(a, r['a'] + '- T2 (server code): no PHP in the frontend bundle\n'), True, 'PHP (a) olumsuz T2 satırı muhafazakâr olarak kusur'),
        ('node_temiz', kapi(a, r['a'] + '- Node runtime version is clean\n'), False, 'PHP olmayan satırdaki "clean": yanlış-pozitif'),
        ('php_ini_temiz', kapi(a, r['a'] + '- php.ini ayarı görünür, temiz\n'), False, 'PHP ama çalışma-zamanı-sürümü olmayan satır: yanlış-pozitif'),
        ('a_bitisik_kaynak', kapi(a, sil('a', '8.3.30 — Dockerfile:1;' + KARS, '8.3.30\n  kaynak: Dockerfile:1;' + KARS)), False, 'PHP (a) sürüm ve kaynak bitişik satırlarda: yanlış-pozitif'),
        ('ci_bitisik', kapi('ci', T2 + '- PHP 8.3 — ci.yml:6 (canlı sürüm ÖLÇÜLEMEDİ; yama düzeyi ÖLÇÜLEMEDİ)\n  not: CI matrisi\n'), False, 'PHP CI belirtisi bitişik satırda: yanlış-pozitif'),
        ('eol81_eolsuz_kelime', kapi('81', sil('81', 'EOL: resmî güvenlik yaması yok → bulgu', 'resmî güvenlik yaması yok → bulgu')), False, 'PHP 8.1 "EOL" sözcüğü olmadan da bulgu sayılır'),
        ('eol82_security_support', kapi('82', sil('82', 'güvenlik desteği 2026-12-31 EOL → uyarı', 'security support ends 2026-12-31')), False, 'PHP 8.2 EN uyarı: yanlış-pozitif'),
        ('kod_81_bulgusuz', 'EOL_BULGUSU_YOK' in kodlar('81', sil('81', 'EOL: resmî güvenlik yaması yok → bulgu', 'x')), True, 'PHP 8.1: EOL_BULGUSU_YOK kodu'),
        ('kod_82_uyarisiz', 'EOL_UYARISI_YOK' in kodlar('82', sil('82', '2026-12-31 EOL → uyarı', 'x')), True, 'PHP 8.2: EOL_UYARISI_YOK kodu'),
        ('a_lock_sadece_yok', kapi(a, sil('a', LOCKYOK, '- composer.lock yok.\n')), False, 'PHP (a) yalnız "composer.lock yok": yanlış-pozitif'),
        ('a_alt_sinir_satiri', kapi(a, r['a'] + '- PHP 8.2 lower bound in composer.json:1\n'), False, 'PHP (a) alt-sınır satırı uydurma sayılmaz'),
        ('kutuphane_plat_temiz', kapi('kutuphane_plat', '- T2 (server code): composer.json + src/U.php — PHP library\n- PHP 8.3.30 — composer.json:1 (config.platform.php; çalışan sürüm değil);' + KARS + '\n' + LOCKYOK), False, 'PHP zayıf imza + platform sürümü yazılmış: yanlış-pozitif'),
        ('kutuphane_plat_surumsuz', kapi('kutuphane_plat', '- T2 (server code): composer.json + src/U.php — PHP library\n' + LOCKYOK), True, 'PHP zayıf imza ama sürüm kaynağı VAR: sürüm yazılmamış'),
        ('c_tr_literal', kapi('c', '- T2 (sunucu kodu): evet — PHP (WordPress)\n- PHP çalışma zamanı sürümü depoda yok — ÖLÇÜLEMEDİ; sunucu/hosting panelinden kontrol et.\n'), False, 'PHP (c) sabit TR satırı AYNEN: yanlış-pozitif'),
        ('c_en_literal', kapi('c', '- T2 (server code): yes — PHP (WordPress)\n- PHP runtime version is not in the repository — NOT MEASURED; check it on the server/hosting panel.\n'), False, 'PHP (c) sabit EN satırı AYNEN: yanlış-pozitif'),
        ('kutuphane_temiz', kapi('kutuphane', r['kutuphane']), False, 'PHP kütüphane (zayıf imza): sabit "depoda yok" satırı istenmez'),
        ('kutuphane_composer_satirsiz', kapi('kutuphane', sil('kutuphane', LOCKYOK)), True, 'PHP kütüphane: composer.lock yok satırı yine istenir'),
        ('kutuphane_temiz_denmis', kapi('kutuphane', r['kutuphane'] + '- PHP çalışma zamanı sürümü güvenli\n'), True, 'PHP kütüphane: "güvenli" iddiası yine yakalanır'),
    ]


def cli_vakalari():
    return [('cli_pass', cli_vaka('a', RAPOR['a']) == 0, True, 'PHP CLI: temiz rapor → çıkış 0'),
            ('cli_kusur', cli_vaka('a', RAPOR['a'].replace('8.3.30', 'x')) == 1, True, 'PHP CLI: kusurlu rapor → çıkış 1'),
            ('cli_utf16', cli_vaka('a', RAPOR['a'], 'utf-16') == 0, True, 'PHP CLI: UTF-16 rapor okunur'),
            ('cli_metin_pass', cli_vaka('a', RAPOR['a'], cikti=True).rstrip().endswith('PASS'), True, 'PHP CLI: temiz raporda son satır PASS'),
            ('cli_metin_fail', 'FAIL SURUM_KAYNAK_YOK' in cli_vaka('a', RAPOR['a'].replace('8.3.30', 'x'), cikti=True), True, 'PHP CLI: kusurlu raporda FAIL + kod'),
            ('cli_kisaltma', cli(['--hed', tempfile.gettempdir()]) == 2, True, 'PHP CLI: kısaltılmış bayrak kabul edilmez (allow_abbrev=False)'),
            ('cli_kullanim', cli(['--hedef', os.path.join(tempfile.gettempdir(), 'yok_hedef_dizin_xyz')]) == 2, True, 'PHP CLI: geçersiz hedef → çıkış 2')]


def oz_test_vakalari():
    """kapilar.py altin kumesi icin: [(ad, yakti_mi, beklenen, etiket)]; hepsinde yakti == beklenen olmali."""
    import php_oz_duzelt  # tembel: php_oz_duzelt php_oz_test'i ice aktarir; ayri modul = dosya <= 400 satir kapisi
    vakalar = golden_vakalari() + fixture_mutantlari() + dedektor_mutantlari() + rapor_vakalari() + cli_vakalari() + php_oz_duzelt.vakalar()
    vakalar.append(('php_vaka_sayisi', len(vakalar) >= 100, True, 'PHP öz-test: vaka listesi boşaltılamaz (≥ 100)'))
    return [(f'php_{ad}', yakti, beklenen, etiket) for ad, yakti, beklenen, etiket in vakalar]


def oz_test():
    vakalar = oz_test_vakalari()
    for ad, yakti, beklenen, etiket in vakalar:
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<28} {etiket}")
    return all(y == b for _, y, b, _ in vakalar)


if __name__ == '__main__':  # dogrudan calistirilinca vakalari KOSAR (onceden hicbir sey kosmadan rc=0 donuyordu: sahte yesil)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.exit(0 if oz_test() else 1)
