"""php_oz_duzelt.py — gedik v2.7.0 DUZELT turu: bagimsiz denetimin Bulgu 1-5, 7, 8 fixture + vektorleri (TR + EN).

php_oz_test.oz_test_vakalari() bunu tembel ice aktarir (php_oz_test.py <= 400 satir kapisi icin ayri modul). Her duzeltme icin
DOGRU rapor (TR/EN) YESIL, BOZUK kopya (TR/EN) KIRMIZI yakmali; fixture ve dedektor mutantlari golden'i KIRMIZI yakmali.
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

T2, LK, KARS = t.T2, t.LOCKYOK, t.KARS
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
SABIT = (T2 + '- ' + pk.SABIT_TR + '\n' + LK, T2 + '- ' + pk.SABIT_EN + '\n' + LK)  # "sürüm depoda yok" diyen BOZUK rapor
UZAK_TR = '- Not: yalnız statik okuma\n- Not: canlı sisteme istek yok\n- Not: PoC aşağıda\n- PHP 8.1 dalı EOL: resmî güvenlik yaması yok → bulgu\n'
UZAK_EN = '- Note: static read only\n- Note: no live requests\n- Note: PoC below\n- PHP 8.1 branch EOL: no official security patches → finding\n'


def kapi3(fx, rapor):
    return bool(pk.rapor_kontrol(t.olc_fx(FX[fx]), rapor))


def sapma3(fx, dosyalar=None):
    return bool(pk.golden_kontrol(t.olc_fx(dosyalar or FX[fx]), GOLDEN[fx]))


def eol(surum, kaynak, tam=False, ek=('', '')):
    """(TR, EN) EOL dalinda DOGRU rapor; ek = EOL cumlesinin ardina eklenen (TR, EN) metin."""
    yama = ('', '') if tam else (' (yama düzeyi ÖLÇÜLEMEDİ)', ' (patch level NOT MEASURED)')
    return (T2 + f'- PHP çalışma zamanı: {surum} — {kaynak}{yama[0]}; EOL: resmî güvenlik yaması yok → bulgu{ek[0]}\n' + LK,
            T2 + f'- PHP runtime: {surum} — {kaynak}{yama[1]}; EOL: no official security patches → finding{ek[1]}\n' + LK)


def cift(ad, kapi_fn, dogru, kotu, etiket):
    """dogru/kotu = (TR, EN) rapor cifti: dogru YESIL (yakti=False), bozuk kopya KIRMIZI (yakti=True)."""
    return [(f'{ad}_{dil}_{tur}', kapi_fn(rapor), yakti, f'{etiket}: {dil.upper()} ' + ('bozuk kopya KIRMIZI' if yakti else 'doğru rapor YEŞİL'))
            for yakti, raporlar, tur in ((False, dogru, 'dogru'), (True, kotu, 'bozuk')) for dil, rapor in zip(('tr', 'en'), raporlar)]


def sessiz_yesil(kaynak):
    """php_oz_test kaynagini gecici dizinde `python php_oz_test.py` ile kosar -> (cikis, cikti). `__main__` yoksa cikis 0 ama cikti BOS: sahte yesil."""
    yer = os.path.dirname(os.path.abspath(__file__))
    with tempfile.TemporaryDirectory() as d:
        for ad in ('php_olc.py', 'php_kapisi.py', 'php_oz_duzelt.py'):
            shutil.copy(os.path.join(yer, ad), d)
        with open(os.path.join(d, 'php_oz_test.py'), 'w', encoding='utf-8', newline='') as f:
            f.write(kaynak)
        env = dict(os.environ, GEDIK_PHP_ALT='1', PYTHONIOENCODING='utf-8')  # cocuk surec bu vektorleri atlar (sonsuz ozyineleme olmasin)
        try:
            p = subprocess.run([sys.executable, 'php_oz_test.py'], cwd=d, env=env, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            return None, ''
        return p.returncode, p.stdout.decode('utf-8', errors='replace')


def main_vakalari():
    if os.environ.get('GEDIK_PHP_ALT'):
        return []
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'php_oz_test.py'), encoding='utf-8') as f:
        kaynak = f.read()
    gercek, bozuk = sessiz_yesil(kaynak), sessiz_yesil(kaynak.split("\nif __name__ == '__main__':")[0] + '\n')
    sahte = lambda s: not (s[0] == 0 and '✓' in s[1])  # noqa: E731 — kosmadan rc=0 donen ya da kirmizi dosya
    return [('main_kosuyor', sahte(gercek), False, 'PHP öz-test dosyası doğrudan çalıştırılınca vakaları koşar, rc=0 (Bulgu 8)'),
            ('main_yok_sahte_yesil', sahte(bozuk), True, 'PHP öz-test dosyası `__main__` bloğu olmadan: hiçbir şey koşmadan rc=0 → KIRMIZI (Bulgu 8 bozuk kopya)')]


def golden_vakalari():
    ml1 = {'composer.json': '{"config": {"platform": {"php": "8.1.5"}}}\n', 'index.php': '<?php\n'}  # bozuk kopya: tek satir -> kaynak :1
    aralik = [k['aralik'] for k in t.olc_fx(FX['plat_cok'])['kaynaklar']]
    return [(f'golden_{k}', sapma3(k), False, f'PHP DÜZELT golden: {k}') for k in GOLDEN] + [
        ('golden_plat_cok_aralik', aralik != [(4, 6)], False, 'PHP composer.json platform satır aralığı config..php = 4..6 (Bulgu 3)'),
        ('fx_dosya_df_adsiz', sapma3('dosya_df', {'docker/php.df': 'FROM php:7.4-fpm\n', 'index.php': '<?php\n'}), True, 'PHP php.Dockerfile adı bozulunca golden KIRMIZI (Bulgu 1)'),
        ('fx_dockerio_ucuncu', sapma3('dockerio', {'Dockerfile': 'FROM myreg.io/php:8.1-fpm\n', 'index.php': '<?php\n'}), True, 'PHP docker.io yerine üçüncü taraf kayıt: golden KIRMIZI (Bulgu 2)'),
        ('fx_plat_cok_tek_satir', sapma3('plat_cok', ml1), True, 'PHP composer.json tek satıra inince kaynak :1 olur: golden KIRMIZI (Bulgu 3)')]


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
    return [('mutant_imaj_dosyasi_eski', a, True, 'PHP dedektör mutantı: `*.Dockerfile` tanınmıyor → golden KIRMIZI (Bulgu 1)'),
            ('mutant_imaj_etiketi_eski', b, True, 'PHP dedektör mutantı: `docker.io/php:` tanınmıyor → golden KIRMIZI (Bulgu 2)'),
            ('mutant_platform_satiri_1', c, True, 'PHP dedektör mutantı: composer.json platform satırı hep :1 → golden KIRMIZI (Bulgu 3)')]


def rapor_vakalari():
    ra, kisit = t.RAPOR['a'], t.RAPOR['kisit']
    b4a = eol('8.1', 'Dockerfile:1', ek=('; desteklenen güvenli bir dala (8.3+) yükseltin', '; upgrade PHP to a secure, supported version'))
    b4a_kotu = eol('8.1', 'Dockerfile:1', ek=('; güvenli bir sürüm, yükseltmeye gerek yok', '; a secure, supported version, no upgrade needed'))
    b4a_kotu2 = eol('8.1', 'Dockerfile:1', ek=('; güvenli, desteklenen bir sürüm', '; it is a secure, supported version'))
    b5 = (T2 + '- PHP çalışma zamanı: 8.1.20 — Dockerfile:1\n' + LK + UZAK_TR, T2 + '- PHP runtime: 8.1.20 — Dockerfile:1\n' + LK + UZAK_EN)
    b5_kotu = (b5[0].replace(UZAK_TR.splitlines(True)[-1], ''), b5[1].replace(UZAK_EN.splitlines(True)[-1], ''))
    return (cift('b1', lambda r: kapi3('dosya_df', r), eol('7.4', 'docker/php.Dockerfile:1'), SABIT, 'PHP php.Dockerfile içindeki FROM php: görünür (Bulgu 1)')
            + cift('b2', lambda r: kapi3('dockerio', r), eol('8.1', 'Dockerfile:1'), SABIT, 'PHP FROM docker.io/php: görünür (Bulgu 2)')
            + cift('b3', lambda r: kapi3('plat_cok', r), eol('8.1.5', 'composer.json:6 (config.platform.php)', True),
                   eol('8.1.5', 'composer.json:1 (config.platform.php)', True), 'PHP çok satırlı composer.json: gerçek satır (Bulgu 3)')
            + [('b3_platform_satiri', kapi3('plat_cok', eol('8.1.5', 'composer.json:5 (config.platform)', True)[0]), False, 'PHP composer.json platform bloğunun satırı (:5) da geçerli'),
               ('b3_uydurma_satir', kapi3('plat_cok', eol('8.1.5', 'composer.json:99', True)[1]), True, 'PHP composer.json olmayan satır :99 → UYDURMA_KAYNAK')]
            + cift('b4a', lambda r: t.kapi('81', r), b4a, b4a_kotu, 'PHP yükseltme önerisindeki "güvenli/secure" hedef tarifi iddia değil (Bulgu 4a)')
            + cift('b4a2', lambda r: t.kapi('81', r), b4a, b4a_kotu2, 'PHP "güvenli/secure sürüm" iddiası yükseltme fiili olmadan KIRMIZI (Bulgu 4a)')
            + cift('b4b', lambda r: t.kapi('a', r), (ra + '- PHP tarafında "risk yok" denmez; yama düzeyi ÖLÇÜLMEDİ\n', ra + '- Verdict for PHP: I am not saying "no action needed"; patch level NOT MEASURED\n'),
                   (ra + '- PHP tarafında risk yok, güncelleme gerekmiyor\n', ra + '- Verdict for PHP: no action needed, all good.\n'), 'PHP ayrı satırdaki "risk yok / no action needed" kararı (Bulgu 4b)')
            + cift('b5', lambda r: kapi3('v81tam', r), b5, b5_kotu, 'PHP 8.1.20: 4 satır uzaktaki "8.1 dalı EOL" kabul, EOL satırı yoksa KIRMIZI (Bulgu 5)')
            + cift('b7', lambda r: t.kapi('kisit', r), (kisit + '- composer.json: PHP >=7.4 kısıtı (alt sınır; çalışan sürüm değil)\n', kisit + '- composer.json requires PHP >=7.4 (lower bound, not the runtime)\n'),
                   (kisit + '- Proje PHP 7.4 kullanıyor (composer.json).\n', kisit + '- The project uses PHP 7.4 (composer.json).\n'), 'PHP composer.json kısıtı "kullanıyor/uses" ile sürüm sayılır (Bulgu 7)')
            + [('b7_laravel_satiri', t.kapi('kisit', kisit + '- composer.json uses laravel/framework ^11.0\n'), False, 'PHP olmayan composer.json satırı "uses": yanlış-pozitif (Bulgu 7)'),
               ('b9_eol_no_veto', t.kapi('81', t.RAPOR['81'].replace('EOL: resmî güvenlik yaması yok → bulgu', 'EOL: no, still supported')), True, 'PHP "EOL: no, still supported" EOL kanıtı sayılmaz'),
               ('b9_eol_veto_eski', eski_veto(), True, 'PHP eski EOL_VETO "EOL: no official security patches" doğru raporu reddediyordu → KIRMIZI (EN fixture buldu)')])


def eski_veto():
    """EOL_VETO'nun onceki hali ('EOL: no\\b' ardindan sozcuk gelse de veto) ile EN dogru rapor: kapi onu yanlis reddeder (yakti=True)."""
    eski = pk.EOL_VETO
    pk.EOL_VETO = eski.replace(r'eol:?\s*(?:hayır|false|no\b(?!\s+\w))', r'eol:?\s*(hayır|no\b|false)')
    try:
        return kapi3('dockerio', eol('8.1', 'Dockerfile:1')[1])
    finally:
        pk.EOL_VETO = eski


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
    """Mutasyon olcumunun (tur 4) hayatta biraktigi davranis farklari: her biri bir mutanti oldurur."""
    ust = eol('8.1', 'Dockerfile:1', ek=('; gerekiyorsa desteklenen güvenli bir dala yükseltin', '; upgrade PHP to a secure, supported version if needed'))
    return [('major7_tam', [k['tam'] for k in t.olc_fx(t.FX['major7'])['kaynaklar']] != [False], False, 'PHP yüzen etiket (7-apache) tam sürüm sayılmaz'),
            ('b4a_tr_gerekirse', t.kapi('81', ust[0]), False, 'PHP yükseltme önerisi "gerekiyorsa" + güvenli dal tarifi: yanlış-pozitif'),
            ('b4a_en_if_needed', t.kapi('81', ust[1]), False, 'PHP yükseltme önerisi "if needed" + secure version tarifi: yanlış-pozitif'),
            ('bayat_120', bayat_uyari(120), False, 'PHP EOL verisi tam 120 günlük: bayatlık uyarısı yok (sınır > 120)'),
            ('bayat_121', bayat_uyari(121), True, 'PHP EOL verisi 121 günlük: bayatlık uyarısı çıkar'),
            ('cli_json_utf8', 'index.php (kök)' in t.cli_vaka('c', t.RAPOR['c'], cikti=True), True, 'PHP CLI JSON çıktısı Türkçe karakteri kaçışsız yazar (ensure_ascii=False)')]


def vakalar():
    return golden_vakalari() + dedektor_vakalari() + rapor_vakalari() + ek_vakalar() + main_vakalari()
