"""php_oz_sabit.py — gedik v2.8.0: regex/etiket SABITLERI icin vakalar (mutasyon olcumunun hayatta biraktigi bosluklar).

php_kapisi.TEMIZ yasak sozcukleri · DOSYA_RE/KISIT/BASLIK/ALAN_RE bicim toleransi · SABIT cumle kilidi · php_olc regex sabitleri (HTACCESS_PHP, FROM/ARG/COMPOSE,
IMAJ_DOSYASI, CI_DOSYA, PLATFORM). php_oz_test.oz_test_vakalari() tembel ice aktarir (dosya <= 400 satir kapisi icin ayri modul).
"""
import json
import os
import sys

import php_kapisi as pk
import php_oz_blok as bl
import php_oz_test as t

TEMIZ_SOZ = ['temiz', 'temizdir', 'tertemiz', 'sorunsuz', 'sorunsuzca', 'sorun yok', 'sorun görülmedi', 'sorun bulunmadı', 'güvenli', 'güvenlidir', 'güncel ve yamalı',
             'clean', 'safe', 'secure', 'is patched', 'is fully patched', 'fully patched', 'no issue', 'no issues', 'no known issue', 'no known issues',
             'no vulnerability', 'no vulnerabilities', 'no known vulnerabilities', 'nothing to worry', 'up-to-date', 'up to date', 'looks good', 'looks fine', 'fine',
             'risk yok', 'riski yok', 'no risk', 'no security risk', 'no action', 'no action needed', 'no action required', 'no action is needed', 'no action is required',
             'all good', 'all clear']
TEMIZ_DEGIL = ['unclean', 'cleanup', 'unsafe', 'safely', 'güvenlik', 'securely', 'finest', 'undefined risk', 'noaction']  # sozcuk siniri: iddia degil
FX_A = 'a'


def kod_a(rapor):
    return pk.rapor_kontrol(t.olc_fx(t.FX[FX_A]), rapor)


def temiz_vakalari():
    kotu = [(f'temiz_soz_{n}', 'BLOK_TEMIZ' in kod_a(bl.B(imaj=f'grype 12 · trivy 3 ({s})')[0]), True, f'PHP blokta "{s}" → BLOK_TEMIZ') for n, s in enumerate(TEMIZ_SOZ)]
    iyi = [(f'temiz_degil_{n}', 'BLOK_TEMIZ' in kod_a(bl.B(imaj=f'grype 12 · trivy 3 ({s})')[0]), False, f'PHP blokta "{s}" sözcük sınırı: iddia değil') for n, s in enumerate(TEMIZ_DEGIL)]
    return kotu + iyi


def bicim_vakalari():
    ok = bl.B()
    tr, en = ok

    def yesil(ad, tr_k, et):
        return (f'bicim_{ad}', bool(kod_a(tr_k)), False, f'PHP blok biçimi ({et}): yanlış-pozitif')
    return [yesil('baslik_iki_nokta', tr.replace('### PHP çalışma zamanı', '### PHP çalışma zamanı:'), 'başlık ":"'),
            yesil('baslik_bosluk_sonu', tr.replace('### PHP çalışma zamanı', '### PHP çalışma zamanı   '), 'başlık sonu boşluk'),
            yesil('baslik_dis_bosluk', tr.replace('### PHP çalışma zamanı', '  ### PHP çalışma zamanı'), 'başlık öncesi boşluk'),
            yesil('baslik_iki_bosluk', tr.replace('### PHP çalışma zamanı', '### PHP   çalışma zamanı'), 'başlıkta çift boşluk'),
            yesil('baslik_iki_nokta_oncesi_bosluk', tr.replace('### PHP çalışma zamanı', '### PHP çalışma zamanı :'), 'başlık " :"'),
            yesil('baslik_iki_nokta_sonrasi_bosluk', tr.replace('### PHP çalışma zamanı', '### PHP çalışma zamanı:  '), 'başlık ":" + sonu boşluk'),
            yesil('baslik_diyez_bosluksuz', tr.replace('### PHP çalışma zamanı', '###PHP çalışma zamanı'), '### sonrası boşluksuz'),
            yesil('baslik_seviye', en.replace('### PHP runtime', '#### PHP runtime'), 'başlık seviyesi'),
            yesil('deger_sonu_bosluk', tr.replace('DESTEKLENEN', 'DESTEKLENEN   '), 'değer sonu boşluk'),
            yesil('iki_nokta_oncesi_bosluk', tr.replace('- EOL:', '- EOL :'), '":" öncesi boşluk'),
            yesil('iki_nokta_sonrasi_yok', tr.replace('- EOL: DESTEKLENEN', '- EOL:DESTEKLENEN'), '":" sonrası boşluksuz'),
            yesil('madde_yildiz', tr.replace('- EOL', '* EOL'), '"*" madde işareti'),
            yesil('satir_basi_bosluk', tr.replace('- EOL', '   - EOL'), 'satır başı boşluk'),
            yesil('blok_oncesi_alan_satiri', '- EOL: BULGU\n' + tr, 'başlık ÖNCESİ alan satırı sayılmaz'),
            ('bicim_composer_tekil', bool(pk.rapor_kontrol(t.olc_fx(t.FX['b']), bl.B(composer='1 advisory')[0])), False, 'PHP blok biçimi: "1 advisory" (tekil) kabul'),
            yesil('trivy_iki_hane', tr.replace('trivy ÖLÇÜLEMEDİ', 'trivy 12'), 'trivy iki haneli sayı'),
            yesil('imaj_ayirac_boru', tr.replace(' · ', ' | '), 'imaj ayracı "|"'),
            yesil('imaj_ayirac_virgul', tr.replace(' · ', ', '), 'imaj ayracı ","'),
            yesil('imaj_ayirac_noktalivirgul', tr.replace(' · ', '; '), 'imaj ayracı ";"'),
            yesil('t2_tire', tr.replace('EVET — kanıt', 'EVET - kanıt'), 'T2 tire "-"'),
            yesil('t2_kisa_tire', tr.replace('EVET — kanıt', 'EVET – kanıt'), 'T2 tire "–"'),
            yesil('surum_tire', tr.replace('8.3.30 — kaynak', '8.3.30 - kaynak'), 'sürüm tire "-"')]


def kirmizi_bicim_vakalari():
    ok = bl.B()
    tr, en = ok
    return [('bicim_kirmizi_iki_nokta_yok', 'ALAN_YOK_EOL' in kod_a(tr.replace('- EOL: DESTEKLENEN', '- EOL DESTEKLENEN')), True, 'PHP alan ":" yok → ALAN_YOK_EOL'),
            ('bicim_kirmizi_t2_hayir', 'T2_ALANI' in kod_a(tr.replace('EVET — kanıt', 'HAYIR — kanıt')), True, 'PHP T2 HAYIR + kanıt → T2_ALANI'),
            ('bicim_kirmizi_t2_no', 'T2_ALANI' in kod_a(en.replace('YES — evidence', 'NO — evidence')), True, 'PHP T2 NO + evidence → T2_ALANI'),
            ('bicim_kirmizi_t2_kanitsiz_tire', 'T2_ALANI' in kod_a(tr.replace('EVET — kanıt: composer.json, artisan, Dockerfile', 'EVET —')), True, 'PHP T2 tire ama kanıt yok → T2_ALANI'),
            ('bicim_kirmizi_blok_nokta', 'BLOK_YOK' in kod_a(tr.replace('### PHP çalışma zamanı', '### PHP çalışma zamanı notları')), True, 'PHP başlık "çalışma zamanı notları" blok değil → BLOK_YOK'),
            ('bicim_kirmizi_kaynak_cift_satir', 'SURUM_ALANI' in kod_a(tr.replace('Dockerfile:1', 'Dockerfile:1:2')), True, 'PHP sürüm kaynağı "Dockerfile:1:2" → SURUM_ALANI (artık metin)'),
            ('bicim_kirmizi_yuzen_kisa', 'SURUM_ALANI' in kod_a(tr.replace('8.3.30 — kaynak: Dockerfile:1', '8.3.30 — kaynak:')), True, 'PHP sürüm kaynağı boş → SURUM_ALANI')]


def fixture_vakalari():
    yuzen = lambda surum: pk.rapor_kontrol(t.olc_fx(t.FX['yuzen']), bl.B(surum=surum, yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ')[0])  # noqa: E731
    celiski = lambda surum: pk.rapor_kontrol(t.olc_fx(t.FX['celiski']), bl.B(surum=surum, yama='TAM', eol='BULGU')[0])  # noqa: E731
    return [('yuzen_dosya_dogru_satir_yanlis', 'KAYNAK_UYDURMA' in yuzen('YÜZEN 8-apache — kaynak: Dockerfile:9'), True, 'PHP yüzen: dosya doğru satır yanlış → KAYNAK_UYDURMA'),
            ('yuzen_dosya_yanlis_satir_dogru', 'KAYNAK_UYDURMA' in yuzen('YÜZEN 8-apache — kaynak: compose.yaml:1'), True, 'PHP yüzen: satır doğru dosya yanlış → KAYNAK_UYDURMA'),
            ('yuzen_php_oneki', yuzen('YÜZEN php:8-apache — kaynak: Dockerfile:1') != [], False, 'PHP yüzen: "php:" önekli etiket kabul'),
            ('celiski_ikinci_sahte', 'KAYNAK_UYDURMA' in celiski('8.3.30 — kaynak: Dockerfile:1; 7.4 — kaynak: docker-compose.prod.yml:9'), True, 'PHP çelişki: gerçek + sahte ikinci çift → KAYNAK_UYDURMA'),
            ('celiski_birinci_sahte', 'KAYNAK_UYDURMA' in celiski('8.3.30 — kaynak: Dockerfile:9; 7.4 — kaynak: docker-compose.prod.yml:3'), True, 'PHP çelişki: sahte + gerçek ikinci çift → KAYNAK_UYDURMA')]


def sabit_cumle_vakalari():
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sabit_cumleler.json')
    with open(yol, encoding='utf-8') as f:
        c = next(x for x in json.load(f)['cumleler'] if x['id'] == 'php-surum-depoda-yok')
    return [('sabit_tr_kilit', pk.SABIT_TR == c['tr'], True, 'PHP SABIT_TR = sabit_cumleler.json kilidi (sabit cümle kayarsa KIRMIZI)'),
            ('sabit_en_kilit', pk.SABIT_EN == c['en'], True, 'PHP SABIT_EN = sabit_cumleler.json kilidi')]


def serbest_dosya_vakalari():
    ok = bl.B()[0]
    dosyalar = ['Containerfile', 'php.Dockerfile', 'ci.yml', 'ci.yaml', '.php-version', '.htaccess', 'php-fpm.conf', 'docker-compose.yml', 'composer.json', 'Dockerfile.prod']
    sahte = [(f'serbest_dosya_{n}', 'UYDURMA_KAYNAK' in kod_a(ok + f'PHP 8.9 çalışma zamanı — {f}:77\n'), True, f'PHP serbest metin: sahte {f}:77 → UYDURMA_KAYNAK') for n, f in enumerate(dosyalar)]
    muaf = ['alt sınır', 'lower bound', 'require', 'kısıt', 'constraint', '^8.9', '~8.9', '>=8.9', '>= 8.9']
    iyi = [(f'serbest_kisit_{n}', 'UYDURMA_KAYNAK' in kod_a(ok + f'PHP 8.9 {m} Dockerfile:77\n'), False, f'PHP serbest metin: "{m}" kısıt satırı muaf') for n, m in enumerate(muaf)]
    digerleri = [('serbest_lock_dosyasi', 'UYDURMA_KAYNAK' in kod_a(ok + 'PHP 8.9 — composer.lock:77\n'), False, 'PHP serbest metin: composer.lock sürüm kaynağı sayılmaz'),
                 ('serbest_php_basinda_nokta', 'UYDURMA_KAYNAK' in kod_a(ok + 'x.php 8.9 Dockerfile:77\n'), False, 'PHP serbest metin: "x.php" PHP anısı değil'),
                 ('serbest_tire_php', 'UYDURMA_KAYNAK' in kod_a(ok + 'swagger-php 8.9 Dockerfile:77\n'), False, 'PHP serbest metin: "swagger-php" PHP anısı değil')]
    return sahte + iyi + digerleri


# ---------- php_olc regex sabitleri (golden fixture'lar) ----------
HT = lambda satir: {'.htaccess': satir + '\n'}  # noqa: E731
OLC_FX = {
    'ht_set': (HT('SetHandler "proxy:unix:/run/php/fpm.sock|fcgi://localhost"'), {'php': True, 'isaretler': ['.htaccess (PHP işleyici)']}),
    'ht_xhttpd': (HT('AddType application/x-httpd-php .php'), {'php': True, 'isaretler': ['.htaccess (PHP işleyici)']}),
    'ht_value': (HT('php_value memory_limit 128M'), {'php': True, 'isaretler': ['.htaccess (PHP işleyici)']}),
    'ht_flag': (HT('php_flag display_errors off'), {'php': True, 'isaretler': ['.htaccess (PHP işleyici)']}),
    'ht_addhandler_script': (HT('AddHandler php-script .php'), {'php': True, 'isaretler': ['.htaccess (PHP işleyici)']}),
    'ht_kucuk_harf': (HT('sethandler proxy:fcgi://x php-fpm'), {'php': True}),
    'ht_ea': (HT('AddHandler application/x-httpd-ea-php74 .php'), {'surum': '7.4', 'kaynak': '.htaccess:1'}),
    'ht_alt': (HT('AddHandler application/x-httpd-alt-php81 .php'), {'surum': '8.1', 'kaynak': '.htaccess:1'}),
    'ht_duz': (HT('AddHandler application/x-httpd-php74 .php'), {'surum': '7.4', 'kaynak': '.htaccess:1'}),
    'ht_fpm_soket': (HT('SetHandler "proxy:unix:/run/php/php7.4-fpm.sock|fcgi://x"'), {'surum': '7.4', 'kaynak': '.htaccess:1'}),
    'from_kucuk': ({'Dockerfile': 'from php:8.3.30-fpm\n'}, {'surum': '8.3.30', 'kaynak': 'Dockerfile:1'}),
    'from_girinti': ({'Dockerfile': '  FROM php:8.3.30-fpm\n'}, {'surum': '8.3.30'}),
    'from_platform': ({'Dockerfile': 'FROM --platform=linux/amd64 php:8.3.30-fpm\n'}, {'surum': '8.3.30'}),
    'from_platform_cift_bosluk': ({'Dockerfile': 'FROM --platform=linux/amd64  php:8.3.30-fpm\n'}, {'surum': '8.3.30'}),
    'from_iki_bayrak': ({'Dockerfile': 'FROM --platform=a --x=b php:8.3.30-fpm\n'}, {'surum': '8.3.30'}),
    'arg_kucuk_girinti': ({'Dockerfile': '  arg PHP_VERSION=8.1\nfrom php:${PHP_VERSION}-fpm\n'}, {'surum': '8.1', 'kaynak': 'Dockerfile:2'}),
    'compose_buyuk': ({'docker-compose.yml': 'services:\n  a:\n    IMAGE: php:8.0.30-cli\n'}, {'surum': '8.0.30', 'kaynak': 'docker-compose.yml:3'}),
    'compose_girintisiz': ({'docker-compose.yml': 'image: php:8.0.30-cli\n'}, {'surum': '8.0.30'}),
    'compose_tirnak': ({'docker-compose.yml': 'services:\n  a:\n    image: "php:8.0.30-cli"\n'}, {'surum': '8.0.30'}),
    'compose_adsiz_onek': ({'compose.yml': 'services:\n  a:\n    image: php:8.0.30-cli\n'}, {'surum': '8.0.30', 'kaynak': 'compose.yml:3'}),
    'compose_yaml_uzanti': ({'compose.yaml': 'services:\n  a:\n    image: php:8.0.30-cli\n'}, {'surum': '8.0.30'}),
    'dockerfile_kucuk_ad': ({'dockerfile': 'FROM php:8.3.30-fpm\n'}, {'surum': '8.3.30'}),
    'dockerfile_uzantili': ({'Dockerfile.prod': 'FROM php:8.3.30-fpm\n'}, {'surum': '8.3.30'}),
    'ci_gitlab': ({'.gitlab-ci.yml': 'test:\n  php: 7.4\n', 'index.php': '<?php\n'}, {'yalniz_ci': True, 'ci_surumleri': ['7.4']}),
    'ci_gitlab_alt': ({'backend/.gitlab-ci.yml': 'test:\n  php: 7.4\n', 'index.php': '<?php\n'}, {'ci_surumleri': ['7.4']}),
    'ci_circle': ({'.circleci/config.yml': 'jobs:\n  php: 7.4\n', 'index.php': '<?php\n'}, {'ci_surumleri': ['7.4']}),
    'ci_azure': ({'azure-pipelines.yml': 'steps:\n  php: 7.4\n', 'index.php': '<?php\n'}, {'ci_surumleri': ['7.4']}),
    'ci_bitbucket': ({'bitbucket-pipelines.yml': 'pipelines:\n  php: 7.4\n', 'index.php': '<?php\n'}, {'ci_surumleri': ['7.4']}),
    'ci_nokta': ({'.github/workflows/ci.yml': 'jobs:\n  t:\n    steps:\n      - with:\n          php-version: dev.master\n', 'index.php': '<?php\n'}, {'ci_surumleri': []}),
    'ci_uc_hane': ({'.travis.yml': 'php:\n  - 8.3.30\n', 'index.php': '<?php\n'}, {'ci_surumleri': ['8.3.30']}),
    'platform_tirnaksiz': ({'.platform.app.yaml': 'type: php:8.3\n', 'index.php': '<?php\n'}, {'surum': '8.3'}),
    'platform_tek_tirnak': ({'.platform.app.yaml': "type: 'php:8.3'\n", 'index.php': '<?php\n'}, {'surum': '8.3'}),
    'appyaml_tirnakli': ({'app.yaml': 'runtime: "php83"\n', 'index.php': '<?php\n'}, {'surum': '8.3'}),
    'appyaml_uc_hane_degil': ({'app.yaml': 'runtime: php831\n', 'index.php': '<?php\n'}, {'surum': None}),
    'surum_uc_hane': ({'.php-version': '8.3.300\n', 'index.php': '<?php\n'}, {'php': True}),
}


def olc_vakalari():
    return [(f'olc_{ad}', bool(pk.golden_kontrol(t.olc_fx(dosyalar), beklenen)), False, f'PHP ölçüm regex sabiti: {ad} golden') for ad, (dosyalar, beklenen) in OLC_FX.items()]


def vakalar():
    return temiz_vakalari() + bicim_vakalari() + kirmizi_bicim_vakalari() + fixture_vakalari() + sabit_cumle_vakalari() + serbest_dosya_vakalari() + olc_vakalari()


if __name__ == '__main__':  # dogrudan calistirilinca vakalari KOSAR (sessiz yesil olmasin)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sonuc = vakalar()
    for ad, yakti, beklenen, etiket in sonuc:
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<34} {etiket}")
    sys.exit(0 if all(y == b for _, y, b, _ in sonuc) else 1)
