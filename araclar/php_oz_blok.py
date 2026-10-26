"""php_oz_blok.py — gedik v2.8.0: PHP rapor BLOGU kapisinin vakalari (TR + EN). Her alan icin DOGRU blok YESIL, bozuk kopya KIRMIZI yakmali.

php_oz_test.oz_test_vakalari() bunu tembel ice aktarir (dosya <= 400 satir kapisi icin ayri modul). EN blok, TR blogun bu dosyadaki TR_EN
cevirisiyle uretilir: ceviri yanlissa EN "dogru" vakasi KIRMIZI yanar (gorulur).
"""
import os
import sys
import tempfile

import php_kapisi as pk
import php_oz_duzelt as d
import php_oz_test as t

TR_EN = [('### PHP çalışma zamanı', '### PHP runtime'), ('Yama düzeyi', 'Patch level'), ('İmaj taraması', 'Image scan'), ('Sürüm', 'Version'),
         ('kanıt:', 'evidence:'), ('kaynak:', 'source:'), ('ÖLÇÜLEMEDİ', 'NOT MEASURED'), ('DESTEKLENEN', 'SUPPORTED'), ('UYARI', 'WARNING'),
         ('BULGU', 'FINDING'), ('EVET', 'YES'), ('HAYIR', 'NO'), ('TAM', 'FULL'), ('danışma', 'advisories'), ('UYGULANMAZ', 'N/A'),
         ('composer.lock yok', 'no composer.lock'), ('YÜZEN', 'FLOATING'), ('YOK', 'NONE')]
ETK = (('t2', 'T2 PHP'), ('surum', 'Sürüm'), ('yama', 'Yama düzeyi'), ('eol', 'EOL'), ('composer', 'composer audit'), ('imaj', 'İmaj taraması'))
TEMEL = dict(t2='EVET — kanıt: composer.json, artisan, Dockerfile', surum='8.3.30 — kaynak: Dockerfile:1', yama='TAM', eol='DESTEKLENEN',
             composer='UYGULANMAZ (composer.lock yok)', imaj='grype 12 · trivy ÖLÇÜLEMEDİ')
PLAT = dict(surum='8.1.5 — kaynak: composer.json:6', yama='TAM', eol='BULGU')
WP = dict(t2='EVET — kanıt: wp-config.php, wp-content', surum='YOK', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ')
LIB = dict(t2='EVET — kanıt: composer.json, src/Util.php', surum='YOK', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ')


def cevir(metin):
    for tr, en in TR_EN:
        metin = metin.replace(tr, en)
    return metin


def B(once='', sonra='', baslik=True, **alan):
    """(TR, EN) rapor: `alan` TEMEL'i ezer; deger None ise alan satiri yazilmaz. once/sonra = dil-bagimsiz serbest metin."""
    a = dict(TEMEL, **alan)
    govde = '\n'.join(f'- {et}: {a[k]}' for k, et in ETK if a[k] is not None)
    tr = once + ('### PHP çalışma zamanı\n' if baslik else '') + govde + '\n' + sonra
    return tr, cevir(tr)


KANIT_TEMEL = 'composer.json, artisan, Dockerfile'
KANIT_FX = {'ci': 'index.php', 'plat_cok': 'index.php, composer.json', 'dosya_df': 'composer.json, artisan, php.Dockerfile'}  # TEMEL kanitinin hedefte VAR olmadigi fixture'lar


def kod(fx, rapor):
    """fx fixture'inda rapor_kontrol; TEMEL T2 kaniti hedefte yoksa o fixture'in gercek dosyalariyla degistirilir (kanit denetimi B3)."""
    return pk.rapor_kontrol(t.olc_fx(dict(t.FX, **d.FX)[fx]), rapor.replace(KANIT_TEMEL, KANIT_FX.get(fx, KANIT_TEMEL)))


def cift(ad, fx, dogru, kotu, etiket, kod_ara=None):
    """dogru/kotu = (TR, EN): dogru YESIL (yakti=False); bozuk KIRMIZI (yakti=True, kod_ara verilmisse o kod da listede olmali)."""
    sonuc = []
    for dil, d, k in zip(('tr', 'en'), dogru, kotu):
        sonuc.append((f'{ad}_{dil}_dogru', bool(kod(fx, d)), False, f'{etiket}: {dil.upper()} doğru blok YEŞİL'))
        yakti = (kod_ara in kod(fx, k)) if kod_ara else bool(kod(fx, k))
        sonuc.append((f'{ad}_{dil}_bozuk', yakti, True, f'{etiket}: {dil.upper()} bozuk kopya KIRMIZI' + (f' ({kod_ara})' if kod_ara else '')))
    return sonuc


def sabit(dil):
    return (pk.SABIT_TR if dil == 0 else pk.SABIT_EN) + '\n'


def alan_vakalari():
    ok = B()
    return (cift('surum_uydurma', 'a', ok, B(surum='8.4.2 — kaynak: Dockerfile:1'), 'PHP sürüm uydurma', 'SURUM_ALANI')
            + cift('surum_kisaltma', 'a', ok, B(surum='8.3.3 — kaynak: Dockerfile:1'), 'PHP sürüm kısaltma 8.3.3 ≠ 8.3.30', 'SURUM_ALANI')
            + cift('kaynak_satir', 'a', ok, B(surum='8.3.30 — kaynak: Dockerfile:9'), 'PHP kaynak satırı uydurma', 'KAYNAK_UYDURMA')
            + cift('kaynak_dosya', 'a', ok, B(surum='8.3.30 — kaynak: compose.yaml:1'), 'PHP kaynak dosyası uydurma', 'KAYNAK_UYDURMA')
            + cift('kaynak_buyuk_harf', 'a', ok, B(surum='8.3.30 — kaynak: DOCKERFILE:1'), 'PHP kaynak dosya adı büyük harf (denetçi kör noktası)', 'KAYNAK_UYDURMA')
            + cift('surum_yok_ama_var', 'a', ok, B(surum='YOK'), 'PHP sürüm var ama YOK yazılmış', 'SURUM_ALANI')
            + cift('surum_kaynaksiz', 'a', ok, B(surum='8.3.30'), 'PHP sürüm kaynaksız', 'SURUM_ALANI')
            + cift('surum_ekstra', 'a', ok, B(surum='8.3.30 — kaynak: Dockerfile:1; 8.4.2'), 'PHP sürüm alanında kaynaksız ikinci sürüm', 'SURUM_ALANI')
            + cift('t2_hayir', 'a', ok, B(t2='HAYIR'), 'PHP imzası var ama T2 PHP: HAYIR', 'T2_ALANI')
            + cift('t2_kanitsiz', 'a', ok, B(t2='EVET'), 'PHP T2 kanıtsız', 'T2_ALANI')
            + cift('yama_olculemedi', 'a', ok, B(yama='ÖLÇÜLEMEDİ'), 'PHP tam sürüm var ama yama düzeyi ÖLÇÜLEMEDİ yazılmış', 'YAMA_ALANI')
            + cift('yama_tam_dal', '81', B(surum='8.1 — kaynak: Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='BULGU'), B(surum='8.1 — kaynak: Dockerfile:1', yama='TAM', eol='BULGU'),
                   'PHP dal etiketi yama düzeyi TAM diyemez', 'YAMA_ALANI')
            + cift('eol_bulgu_yok', '81', B(surum='8.1 — kaynak: Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='BULGU'), B(surum='8.1 — kaynak: Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='DESTEKLENEN'),
                   'PHP 8.1 EOL: DESTEKLENEN diyemez', 'EOL_ALANI')
            + cift('eol_uyari', '82', B(surum='8.2.28 — kaynak: Dockerfile:1', eol='UYARI'), B(surum='8.2.28 — kaynak: Dockerfile:1', eol='DESTEKLENEN'), 'PHP 8.2 UYARI olmalı', 'EOL_ALANI')
            + cift('eol_abartili', 'a', ok, B(eol='BULGU'), 'PHP 8.3 EOL: BULGU diyemez', 'EOL_ALANI')
            + cift('eol_ci', 'ci', B(surum='8.3 — kaynak: .github/workflows/ci.yml:6', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ'),
                   B(surum='8.3 — kaynak: .github/workflows/ci.yml:6', yama='ÖLÇÜLEMEDİ', eol='DESTEKLENEN'), 'PHP yalnız-CI sürümü: EOL ÖLÇÜLEMEDİ', 'EOL_ALANI')
            + cift('ci_yama', 'ci', B(surum='8.3 — kaynak: .github/workflows/ci.yml:6', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ'),
                   B(surum='8.3 — kaynak: .github/workflows/ci.yml:6', yama='TAM', eol='ÖLÇÜLEMEDİ'), 'PHP yalnız-CI sürümü: yama TAM diyemez', 'YAMA_ALANI'))


def composer_vakalari():
    lock = dict(composer='0 danışma')
    return (cift('composer_lock_yok_sayi', 'a', B(), B(composer='0 danışma'), 'PHP composer.lock yok ama audit sayısı yazılmış', 'COMPOSER_ALANI')
            + cift('composer_lock_var_uygulanmaz', 'b', B(**lock), B(composer='UYGULANMAZ (composer.lock yok)'), 'PHP composer.lock var ama UYGULANMAZ', 'COMPOSER_ALANI')
            + cift('composer_sayisiz', 'b', B(**lock), B(composer='sorun yok'), 'PHP composer audit sonucu sayısız (denetçi: RAPOR KUSURU)', 'COMPOSER_ALANI')
            + cift('composer_sebepsiz', 'b', B(composer='ÖLÇÜLEMEDİ (composer yok)'), B(composer='ÖLÇÜLEMEDİ'), 'PHP ÖLÇÜLEMEDİ sebepsiz', 'COMPOSER_ALANI')
            + cift('composer_uyari_sozcugu', 'b', B(composer='1 danışma'), B(composer='1 uyarı'), 'PHP "1 uyarı" blokta kabul edilmez (sayı + danışma)', 'COMPOSER_ALANI')
            + cift('composer_yok_sebepsiz', 'a', B(), B(composer='UYGULANMAZ'), 'PHP UYGULANMAZ sebepsiz', 'COMPOSER_ALANI')
            + cift('imaj_bicim', 'a', B(), B(imaj='grype temiz · trivy 0'), 'PHP imaj alanı sayı/ÖLÇÜLEMEDİ değil', 'IMAJ_ALANI')
            + cift('imaj_eksik', 'a', B(), B(imaj='grype 12'), 'PHP imaj alanında trivy yok', 'IMAJ_ALANI')
            + cift('imaj_olculemedi', 'a', B(imaj='grype ÖLÇÜLEMEDİ · trivy ÖLÇÜLEMEDİ'), B(imaj='grype ÖLÇÜLEMEDİ · trivy yok'), 'PHP imaj alanı ÖLÇÜLEMEDİ biçimi', 'IMAJ_ALANI'))


def sekil_vakalari():
    ok = B()
    tr, en = ok
    cift2 = lambda ad, tr_k, en_k, et, kod_ara: cift(ad, 'a', ok, (tr_k, en_k), et, kod_ara)  # noqa: E731
    return (cift('blok_yok', 'a', ok, B(baslik=False), 'PHP blok başlığı yok', 'BLOK_YOK')
            + cift('blok_cok', 'a', ok, (tr + '\n' + tr, en + '\n' + en), 'PHP blok iki kez', 'BLOK_COK')
            + cift2('blok_bos_satirla_bolunmus', tr.replace('\n- EOL', '\n\n- EOL'), en.replace('\n- EOL', '\n\n- EOL'), 'PHP blok ilk boş satırda biter (sonrası alan sayılmaz)', 'ALAN_YOK_EOL')
            + cift2('alan_yok_eol', tr.replace('- EOL: DESTEKLENEN\n', ''), en.replace('- EOL: SUPPORTED\n', ''), 'PHP EOL alanı yok', 'ALAN_YOK_EOL')
            + cift2('alan_yok_imaj', tr.replace('- İmaj taraması: grype 12 · trivy ÖLÇÜLEMEDİ\n', ''), en.replace('- Image scan: grype 12 · trivy NOT MEASURED\n', ''), 'PHP imaj alanı yok', 'ALAN_YOK_IMAJ')
            + cift2('alan_cok_eol', tr + '- EOL: BULGU\n', en + '- EOL: FINDING\n', 'PHP EOL alanı iki kez', 'ALAN_COK_EOL')
            + cift2('alan_kucuk_harf', tr.replace('- Sürüm:', '- sürüm:'), en.replace('- Version:', '- version:'), 'PHP etiket küçük harf (sabit etiket)', 'ALAN_YOK_SURUM')
            + cift2('deger_kucuk_harf', tr.replace('DESTEKLENEN', 'Destekleniyor'), en.replace('SUPPORTED', 'Supported'), 'PHP EOL değeri sabit sözcük değil', 'EOL_ALANI')
            + cift('temiz_blokta', 'a', ok, B(imaj='grype 12 · trivy 3 (temiz görünüyor)'), 'PHP blokta "temiz" iddiası', 'BLOK_TEMIZ')
            + cift2('temiz_blokta_en', tr + '- İmaj taraması: görüntü temiz görünüyor\n', en + '- Image scan: the image looks clean\n', 'PHP blokta EN "clean" (ikinci alan)', 'BLOK_TEMIZ')
            + tolerans_vakalari())


def tolerans_vakalari():
    tr, en = B()
    kalin = (tr.replace('- Sürüm:', '- **Sürüm:**').replace('Dockerfile:1', '`Dockerfile:1`'), en.replace('- Version:', '- **Version:**').replace('Dockerfile:1', '`Dockerfile:1`'))
    bos = (tr.replace('- ', ''), en.replace('- ', ''))
    arada = (tr.replace('\n- EOL', '\nserbest metin\n- EOL'), en.replace('\n- EOL', '\nfree text\n- EOL'))  # bos satirsiz serbest satir: bolge devam eder
    sonra = (tr + '## Bulgular\n- EOL: BULGU\n', en + '## Findings\n- EOL: FINDING\n')  # sonraki bolum blok disi
    alinti = (''.join('> ' + x + '\n' for x in tr.splitlines()), ''.join('> ' + x + '\n' for x in en.splitlines()))  # SKILL.md sablonu blockquote
    return [(f'tolerans_{ad}_{dil}', bool(kod('a', r)), False, f'PHP blok biçim toleransı ({ad}, {dil}): yanlış-pozitif')
            for ad, ikili in (('kalin_backtick', kalin), ('madde_isaretsiz', bos), ('arada_metin', arada), ('sonraki_bolum', sonra), ('blockquote', alinti)) for dil, r in zip(('tr', 'en'), ikili)]


def sablon_vakalari():
    """SKILL.md (TR+EN) blok SABLONU kapiyla ayni etiketleri/sozcukleri kullanir (sablon kayarsa KIRMIZI). Kopya dizinde (skills/ yok) atlanir."""
    if os.environ.get('GEDIK_PHP_ALT'):
        return []
    kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sonuc = []
    for dil, i, yol in (('tr', 0, 'skills/gedik-tr/SKILL.md'), ('en', 1, 'skills/gedik/SKILL.md')):
        with open(os.path.join(kok, *yol.split('/')), encoding='utf-8') as f:
            satirlar = [x[2:] for x in f.read().splitlines() if x.startswith('> ')]
        blok = next((satirlar[n:n + 7] for n, x in enumerate(satirlar) if pk.BASLIK.match(x)), [])
        degerler = {x.split(':')[0].lstrip('- '): x.split(':', 1)[1].strip() for x in blok[1:] if ':' in x}
        eol = {v.strip() for v in degerler.get(pk.ETIKET['eol'][i], '').split('|')}
        yama = {v.strip() for v in degerler.get(pk.ETIKET['yama'][i], '').split('|')}
        sonuc += [(f'sablon_{dil}_etiketler', len(blok) == 7 and all(pk.ALAN_RE.match(x) for x in blok[1:]), True, f'PHP SKILL.md ({dil}) şablonu 6 alan etiketini kapıyla aynı yazıyor'),
                  (f'sablon_{dil}_eol', eol == {v[i] for v in pk.EOL_ESLE.values()}, True, f'PHP SKILL.md ({dil}) EOL değer sözcükleri = kapı sözcükleri'),
                  (f'sablon_{dil}_yama', yama == {v[i] for v in pk.YAMA_ESLE.values()}, True, f'PHP SKILL.md ({dil}) yama değer sözcükleri = kapı sözcükleri')]
    return sonuc


def fixture_vakalari():
    wp = B(sonra=sabit(0), **WP)[0], B(sonra=sabit(1), **WP)[1]
    yuzen = B(surum='YÜZEN 8-apache — kaynak: Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ')
    celiski = B(surum='8.3.30 — kaynak: Dockerfile:1; 7.4 — kaynak: docker-compose.prod.yml:3', yama='TAM', eol='BULGU')
    celiski_eksik = B(surum='8.3.30 — kaynak: Dockerfile:1', yama='TAM', eol='BULGU')
    plat = B(**PLAT)
    return (cift('wp_sabit', 'c', wp, B(**WP), 'PHP sürümsüz WordPress: sabit ÖLÇÜLEMEDİ cümlesi şart', 'SABIT_SATIR_YOK')
            + cift('wp_uydurma', 'c', wp, B(sonra=sabit(0), **dict(WP, surum='8.3.30 — kaynak: Dockerfile:1')), 'PHP WordPress depoda olmayan sürüm uyduruyor', 'SURUM_ALANI')
            + cift('kutuphane', 'kutuphane', B(**LIB), B(**dict(LIB, surum='8.1')), 'PHP kütüphane: sürüm YOK, sabit cümle istenmez', 'SURUM_ALANI')
            + cift('yuzen', 'yuzen', yuzen, B(surum='YÜZEN 8-fpm — kaynak: Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ'), 'PHP yüzen etiket yanlış', 'SURUM_ALANI')
            + cift('yuzen_yok', 'yuzen', yuzen, B(surum='YOK', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ'), 'PHP yüzen etiket kaynağı var, YOK yazılmış', 'SURUM_ALANI')
            + cift('celiski', 'celiski', celiski, celiski_eksik, 'PHP çelişen kaynaklardan biri yazılmamış', 'SURUM_ALANI')
            + cift('platform_satir', 'plat_cok', plat, B(**dict(PLAT, surum='8.1.5 — kaynak: composer.json:99')), 'PHP composer.json platform satırı uydurma', 'KAYNAK_UYDURMA')
            + cift('platform_araligi', 'plat_cok', B(**dict(PLAT, surum='8.1.5 — kaynak: composer.json:5')), B(**dict(PLAT, surum='8.1.5 — kaynak: composer.json:7')),
                   'PHP platform aralığı (4..6) dışı satır', 'KAYNAK_UYDURMA')
            + cift('dosya_df', 'dosya_df', B(surum='7.4 — kaynak: docker/php.Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='BULGU'),
                   B(surum='7.4 — kaynak: docker/php.Dockerfile:2', yama='ÖLÇÜLEMEDİ', eol='BULGU'), 'PHP yol+dosya kaynağı', 'KAYNAK_UYDURMA')
            + [('imzasiz_atlanir', bool(pk.rapor_kontrol(t.olc_fx({'main.py': 'print(1)\n'}), 'rapor')), False, 'PHP imzası yok: blok istenmez')])


def serbest_vakalari():
    """Blok doğruyken serbest metin: v2.7.1 yanlış alarm cümleleri YEŞİL; denetçi kör nokta satırları (uydurma kaynak) KIRMIZI."""
    ok = B()
    yesil = [('eol_kapsamli', 'EOL kuralına göre sorun yok (8.3, 8.1 ve altı değil). Ama sürüm güncel yama düzeyinin gerisinde (G-1).', 'No EOL issue; but the version is behind the current patch level (G-1).'),
             ('uyari_sozcugu', '| composer audit | 1 uyarı: CVE-2026-109413 |', '| composer audit | 1 warning: CVE-2026-109413 |'),
             ('yama_seviyesi', 'Yama seviyesi: 7.4.33 (grype `php-cli 7.4.33`, imaj digest sha256:18b3).', 'The patch level resolved by grype is 7.4.33 (`php-cli 7.4.33`, image digest sha256:18b3).'),
             ('varsayim', 'Bu ikinci yöntem olmasaydı G-1 "temiz" yazılacaktı.', 'Without the second method G-1 would have been written "clean".'),
             ('swagger', 'swagger-php 4.11.1 (`vulnerabilities/api/composer.lock:278-279`) bağımlılığı', 'swagger-php 4.11.1 (`vulnerabilities/api/composer.lock:278-279`) dependency'),
             ('gen_openapi', '`gen_openapi.php` yalnız yerel kullanır (8.4 değil) Dockerfile:5 civarı', '`gen_openapi.php` is used locally only (not 8.4) around Dockerfile:5'),
             ('gercek_kaynak', 'PHP 8.3.30 çalışma zamanı — Dockerfile:1 (yukarıdaki blokla aynı)', 'PHP 8.3.30 runtime — Dockerfile:1 (same as the block above)'),
             ('dal_oneki', '| PHP EOL | 8.3 → SUPPORTED | `Dockerfile:1`, EOL kuralı (2026-10-22 ölçümü) |', '| PHP EOL | 8.3 → SUPPORTED | `Dockerfile:1`, EOL rule (measured 2026-10-22) |'),
             ('alt_sinir', 'composer.json: php ^8.2 alt sınır (lower bound), Dockerfile:3 değil', 'composer.json: php ^8.2 lower bound, not Dockerfile:3')]
    kirmizi = [('php_cli_tablo', '| php-cli | 8.1.5 | Dockerfile:2 |', '| php-cli | 8.1.5 | Dockerfile:2 |'),
               ('php_fpm', 'PHP-FPM 8.1.5 çalışma zamanı — Dockerfile:2', 'PHP-FPM 8.1.5 runtime — Dockerfile:2'),
               ('buyuk_harf_dosya', 'PHP 8.3.30 çalışma zamanı — DOCKERFILE:1', 'PHP 8.3.30 runtime — DOCKERFILE:1'),
               ('php_ini', 'php.ini 8.1.5 ayarı — Dockerfile:9', 'php.ini 8.1.5 setting — Dockerfile:9'),
               ('dal_baska', '| PHP EOL | 8.4 → SUPPORTED | `Dockerfile:1` |', '| PHP EOL | 8.4 → SUPPORTED | `Dockerfile:1` |'),
               ('dal_baska_satir', '| PHP EOL | 8.3 → SUPPORTED | `Dockerfile:9` |', '| PHP EOL | 8.3 → SUPPORTED | `Dockerfile:9` |'),
               ('dal_8_30', '| PHP EOL | 8.30 → SUPPORTED | `Dockerfile:1` |', '| PHP EOL | 8.30 → SUPPORTED | `Dockerfile:1` |'),
               ('dal_uc_parca_onek', '| PHP EOL | 8.3.3 → SUPPORTED | `Dockerfile:1` |', '| PHP EOL | 8.3.3 → SUPPORTED | `Dockerfile:1` |'),
               ('compose_uydurma', 'PHP 7.4.1 — docker-compose.yml:3', 'PHP 7.4.1 — docker-compose.yml:3')]
    sonuc = []
    for ad, trm, enm in yesil:
        sonuc += [(f'serbest_{ad}_{dil}', bool(kod('a', rapor + '\n' + m + '\n')), False, f'PHP serbest metin ({ad}, {dil}): blok doğruysa YEŞİL')
                  for dil, rapor, m in (('tr', ok[0], trm), ('en', ok[1], enm))]
    for ad, trm, enm in kirmizi:
        sonuc += [(f'serbest_{ad}_{dil}', 'UYDURMA_KAYNAK' in kod('a', rapor + '\n' + m + '\n'), True, f'PHP serbest metin ({ad}, {dil}): uydurma kaynak KIRMIZI')
                  for dil, rapor, m in (('tr', ok[0], trm), ('en', ok[1], enm))]
    return sonuc


def cli_vakalari():
    ok = B()
    return [('cli_pass', t.cli_vaka('a', ok[0]) == 0, True, 'PHP CLI: doğru blok → çıkış 0'),
            ('cli_kusur', t.cli_vaka('a', B(surum='8.4.2 — kaynak: Dockerfile:1')[0]) == 1, True, 'PHP CLI: kusurlu blok → çıkış 1'),
            ('cli_utf16', t.cli_vaka('a', ok[0], 'utf-16') == 0, True, 'PHP CLI: UTF-16 rapor okunur'),
            ('cli_metin_pass', t.cli_vaka('a', ok[1], cikti=True).rstrip().endswith('PASS'), True, 'PHP CLI: doğru EN blokta son satır PASS'),
            ('cli_metin_fail', 'FAIL BLOK_YOK' in t.cli_vaka('a', 'blok yok', cikti=True), True, 'PHP CLI: blok yok → FAIL BLOK_YOK'),
            ('cli_sebep_satiri', all(x in t.cli_vaka('a', ok[0] + 'PHP 8.4 → Dockerfile:1\n', cikti=True) for x in ('sebep UYDURMA_KAYNAK: rapor satır 8', "('8.4', 'Dockerfile', '1')")),
             True, 'PHP CLI: UYDURMA_KAYNAK sebep satırı (satır no + üçlü) basılır'),
            ('cli_kisaltma', t.cli(['--hed', tempfile.gettempdir()]) == 2, True, 'PHP CLI: kısaltılmış bayrak kabul edilmez (allow_abbrev=False)'),
            ('cli_kullanim', t.cli(['--hedef', tempfile.gettempdir() + '/yok_hedef_dizin_xyz']) == 2, True, 'PHP CLI: geçersiz hedef → çıkış 2')]


def vakalar():
    return alan_vakalari() + composer_vakalari() + sekil_vakalari() + fixture_vakalari() + serbest_vakalari() + sablon_vakalari() + cli_vakalari()


if __name__ == '__main__':  # dogrudan calistirilinca vakalari KOSAR (sessiz yesil olmasin)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    hata = [ad for ad, yakti, beklenen, _ in vakalar() if yakti != beklenen]
    for ad, yakti, beklenen, etiket in vakalar():
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<34} {etiket}")
    sys.exit(1 if hata else 0)
