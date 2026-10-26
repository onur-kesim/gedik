"""php_oz_duzelt.py — gedik v2.8.0: PHP olcumu (php_olc) golden/dedektor-mutant vakalari + oz-test dosyalarinin `__main__` vakalari.

php_oz_test.oz_test_vakalari() bunu tembel ice aktarir (php_oz_test.py <= 400 satir kapisi icin ayri modul). Fixture ve dedektor mutantlari
golden'i KIRMIZI yakmali; rapor BLOGU vakalari php_oz_blok.py'de.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import php_kapisi as pk
import php_olc
import php_oz_test as t

ML = '{\n  "name": "acme/app",\n  "require": {"php": ">=7.4"},\n  "config": {\n    "platform": {\n      "php": "8.1.5"\n    }\n  }\n}\n'  # platform.php = 6. satir
FX = {
    'dosya_df': dict(t.LARAVEL, **{'docker/php.Dockerfile': 'FROM php:7.4-fpm\n'}),
    'dockerio': dict(t.LARAVEL, Dockerfile='FROM docker.io/php:8.1-fpm\n'),
    'plat_cok': {'composer.json': ML, 'index.php': '<?php\n'},
    'v81tam': dict(t.LARAVEL, Dockerfile='FROM php:8.1.20-fpm\n'),
    'plat64': {'composer.json': '{\n "config": {\n  "platform": {\n   "php-64bit": "8.1.5"\n  }\n }\n}\n', 'index.php': '<?php\n'},
    'plat_str': {'composer.json': '{"config": {"platform": "x"}}\n', 'index.php': '<?php\n'},
}
GOLDEN = {
    'plat64': {'surum': '8.1.5', 'kaynak': 'composer.json:4', 'eol': 'yok_yama'},
    'plat_str': {'php': True, 'surum': None, 'yuzen': None},
    'dosya_df': {'php': True, 'surum': '7.4', 'kaynak': 'docker/php.Dockerfile:1', 'eol': 'yok_yama'},
    'dockerio': {'surum': '8.1', 'kaynak': 'Dockerfile:1', 'eol': 'yok_yama'},
    'plat_cok': {'surum': '8.1.5', 'kaynak': 'composer.json:6', 'eol': 'yok_yama'},
    'v81tam': {'surum': '8.1.20', 'tam': True, 'eol': 'yok_yama', 'en_eski': '8.1.20'},
}
OZ_DOSYALARI = ('php_oz_test', 'php_oz_duzelt', 'php_oz_blok', 'php_oz_sabit', 'php_oz_denetim', 'php_oz_denetci', 'php_oz_gerileme')  # her biri doğrudan çalıştırılınca vakaları KOŞAR (sessiz yeşil yok)


def sapma3(fx, dosyalar=None):
    return bool(pk.golden_kontrol(t.olc_fx(dosyalar or FX[fx]), GOLDEN[fx]))


def sessiz_yesil(modul, kaynak):
    """`modul`un kaynagini gecici dizinde `python <modul>.py` ile kosar -> (cikis, cikti). `__main__` yoksa cikis 0 ama cikti BOS: sahte yesil."""
    yer = os.path.dirname(os.path.abspath(__file__))
    with tempfile.TemporaryDirectory() as d:
        for ad in ('php_olc.py', 'php_kapisi.py', 'sabit_cumleler.json', *(m + '.py' for m in OZ_DOSYALARI)):
            shutil.copy(os.path.join(yer, ad), d)
        with open(os.path.join(d, modul + '.py'), 'w', encoding='utf-8', newline='') as f:
            f.write(kaynak)
        env = dict(os.environ, GEDIK_PHP_ALT='1', PYTHONIOENCODING='utf-8')  # cocuk surec bu vektorleri atlar (sonsuz ozyineleme olmasin)
        try:
            p = subprocess.run([sys.executable, modul + '.py'], cwd=d, env=env, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            return None, ''
        return p.returncode, p.stdout.decode('utf-8', errors='replace')


def main_vakalari():
    if os.environ.get('GEDIK_PHP_ALT'):
        return []
    sahte = lambda s: not (s[0] == 0 and '✓' in s[1])  # noqa: E731 — kosmadan rc=0 donen ya da kirmizi dosya
    sonuc = []
    for modul in OZ_DOSYALARI:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), modul + '.py'), encoding='utf-8') as f:
            kaynak = f.read()
        bozuk = kaynak.split("\nif __name__ == '__main__':")[0] + '\n'
        sonuc += [(f'main_kosuyor_{modul}', sahte(sessiz_yesil(modul, kaynak)), False, f'PHP öz-test dosyası {modul} doğrudan çalıştırılınca vakaları koşar, rc=0'),
                  (f'main_yok_{modul}', sahte(sessiz_yesil(modul, bozuk)), True, f'PHP öz-test dosyası {modul} `__main__` bloğu olmadan: hiçbir şey koşmadan rc=0 → KIRMIZI')]
    return sonuc


def golden_vakalari():
    ml1 = {'composer.json': '{"config": {"platform": {"php": "8.1.5"}}}\n', 'index.php': '<?php\n'}  # bozuk kopya: tek satir -> kaynak :1
    aralik = [k['aralik'] for k in t.olc_fx(FX['plat_cok'])['kaynaklar']]
    return [(f'golden_{k}', sapma3(k), False, f'PHP DÜZELT golden: {k}') for k in GOLDEN] + [
        ('golden_plat_cok_aralik', aralik != [(4, 6)], False, 'PHP composer.json platform satır aralığı config..php = 4..6'),
        ('fx_dosya_df_adsiz', sapma3('dosya_df', {'docker/php.df': 'FROM php:7.4-fpm\n', 'index.php': '<?php\n'}), True, 'PHP php.Dockerfile adı bozulunca golden KIRMIZI'),
        ('fx_dockerio_ucuncu', sapma3('dockerio', {'Dockerfile': 'FROM myreg.io/php:8.1-fpm\n', 'index.php': '<?php\n'}), True, 'PHP docker.io yerine üçüncü taraf kayıt: golden KIRMIZI'),
        ('fx_plat_cok_tek_satir', sapma3('plat_cok', ml1), True, 'PHP composer.json tek satıra inince kaynak :1 olur: golden KIRMIZI')]


def dedektor_vakalari():
    def eski_etiket(imaj):
        m = re.match(r'^(?:(?:[\w.\-]+(?::\d+)?/)*library/)?php[:@](.*)$', imaj, re.I)
        return m.group(1) if m else None
    with t.dedektor_mutanti('IMAJ_DOSYASI', re.compile(r'^(Dockerfile.*|Containerfile.*|(docker-)?compose[\w.\-]*\.ya?ml)$', re.I)):
        a = sapma3('dosya_df')
    with t.dedektor_mutanti('imaj_etiketi', eski_etiket):
        b = sapma3('dockerio')
    with t.dedektor_mutanti('platform_satiri', lambda metin, anahtar: (1, 1)):
        c = sapma3('plat_cok')
    return [('mutant_imaj_dosyasi_eski', a, True, 'PHP dedektör mutantı: `*.Dockerfile` tanınmıyor → golden KIRMIZI'),
            ('mutant_imaj_etiketi_eski', b, True, 'PHP dedektör mutantı: `docker.io/php:` tanınmıyor → golden KIRMIZI'),
            ('mutant_platform_satiri_1', c, True, 'PHP dedektör mutantı: composer.json platform satırı hep :1 → golden KIRMIZI')]


def bayat_uyari(gun):
    """EOL verisi `gun` gunlukken bayatlik_uyarisi dolu mu; pk.date gecici olarak sabitlenir."""
    bugun = date.fromisoformat(php_olc.EOL_OLCUM_TARIHI) + timedelta(days=gun)

    class Sabit(date):
        @classmethod
        def today(cls):
            return bugun
    eski, pk.date = pk.date, Sabit
    try:
        return bool(pk.bayatlik_uyarisi({'eol_olcum_tarihi': php_olc.EOL_OLCUM_TARIHI}))
    finally:
        pk.date = eski


def ek_vakalar():
    """Mutasyon olcumunun hayatta biraktigi davranis farklari: her biri bir mutanti oldurur."""
    return [('major7_tam', [k['tam'] for k in t.olc_fx(t.FX['major7'])['kaynaklar']] != [False], False, 'PHP yüzen etiket (7-apache) tam sürüm sayılmaz'),
            ('bayat_120', bayat_uyari(120), False, 'PHP EOL verisi tam 120 günlük: bayatlık uyarısı yok (sınır > 120)'),
            ('bayat_121', bayat_uyari(121), True, 'PHP EOL verisi 121 günlük: bayatlık uyarısı çıkar'),
            ('cli_json_utf8', 'index.php (kök)' in t.cli_vaka('c', 'x', cikti=True), True, 'PHP CLI JSON çıktısı Türkçe karakteri kaçışsız yazar (ensure_ascii=False)')]


def vakalar():
    return golden_vakalari() + dedektor_vakalari() + ek_vakalar() + main_vakalari()


if __name__ == '__main__':  # dogrudan calistirilinca vakalari KOSAR (sessiz yesil olmasin)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sonuc = vakalar()
    for ad, yakti, beklenen, etiket in sonuc:
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<34} {etiket}")
    sys.exit(0 if all(y == b for _, y, b, _ in sonuc) else 1)
