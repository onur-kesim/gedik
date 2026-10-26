"""php_oz_test.py — gedik v2.8.0: PHP kapisinin KOR KAPI OZ-TESTI (D1/D2). Fixture'lar satir ici (dosya fixture'i yok), her biri gecici dizine yazilir.

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


def oz_test_vakalari():
    """kapilar.py altin kumesi icin: [(ad, yakti_mi, beklenen, etiket)]; hepsinde yakti == beklenen olmali."""
    import php_oz_gerileme
    import php_oz_denetci
    import php_oz_denetim
    import php_oz_sabit
    import php_oz_blok  # tembel: php_oz_duzelt/php_oz_blok php_oz_test'i ice aktarir; ayri modul = dosya <= 400 satir kapisi
    import php_oz_duzelt
    vakalar = golden_vakalari() + fixture_mutantlari() + dedektor_mutantlari() + php_oz_blok.vakalar() + php_oz_sabit.vakalar() + php_oz_denetim.vakalar() + php_oz_denetci.vakalar() + php_oz_gerileme.vakalar() + php_oz_duzelt.vakalar()
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
