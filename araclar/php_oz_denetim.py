"""php_oz_denetim.py — gedik v2.8.0 DUZELT turu: bagimsiz denetimin (2026-10-24, denetim_280/RAPOR.md) Bulgu 1-4 vakalari (TR + EN).

B1 etiket yazim hatasi / YUZEN cift tire · B2 temiz yasagi blok bolgesinin TUM satirlarinda · B3 T2 kaniti hedefte var + imza dosyasi · B4 yanlis alarmlar
(bloktan sonra bos satirla gelen "Notlar:", tarayici-cozumu satiri, imaj alani ÖLÇÜLEMEDİ (sebep), yol-duyarli serbest kaynak).
php_oz_test.oz_test_vakalari() tembel ice aktarir (dosya <= 400 satir kapisi icin ayri modul).
"""
import os
import sys

import php_kapisi as pk
import php_oz_blok as bl
import php_oz_duzelt as d
import php_oz_test as t


def b1_vakalari():
    tr, en = ok = bl.B()
    yuzen = bl.B(surum='YÜZEN 8-apache — kaynak: Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ')
    cift_tire = lambda s: bl.B(surum=s, yama='ÖLÇÜLEMEDİ', eol='ÖLÇÜLEMEDİ')  # noqa: E731
    return (bl.cift('b1_etiket_t2', 'a', ok, (tr.replace('T2 PHP', 'Q2 PHP'), en.replace('T2 PHP', 'Q2 PHP')), 'PHP etiket yazım hatası "Q2 PHP"', 'ALAN_YOK_T2')
            + bl.cift('b1_etiket_composer', 'a', ok, (tr.replace('composer audit', 'Qomposer audit'), en.replace('composer audit', 'Qomposer audit')),
                      'PHP etiket yazım hatası "Qomposer audit"', 'ALAN_YOK_COMPOSER')
            + bl.cift('b1_yuzen_cift_tire', 'yuzen', yuzen, cift_tire('YÜZEN 8-apache--kaynak: Dockerfile:1'), 'PHP YÜZEN etiketle tire arasında boşluk yok (`8-apache--kaynak:`)', 'SURUM_ALANI')
            + bl.cift('b1_yuzen_tire_karisik', 'yuzen', yuzen, cift_tire('YÜZEN 8-apache-—kaynak: Dockerfile:1'), 'PHP YÜZEN etiket + karışık tire bitişik', 'SURUM_ALANI')
            + bl.cift('b1_yuzen_php_oneki', 'yuzen', yuzen, cift_tire('YÜZEN php:8-apache--kaynak: Dockerfile:1'), 'PHP YÜZEN php: önekli çift tire', 'SURUM_ALANI'))


def b2_vakalari():
    tr, en = ok = bl.B()
    pos = lambda ad, tr_k, en_k, et: bl.cift('b2_' + ad, 'a', ok, (tr_k, en_k), et, 'BLOK_TEMIZ')  # noqa: E731
    return (pos('alan_disi_satir', tr + 'Değerlendirme: PHP tarafı temiz.\n', en + 'Assessment: the PHP side is clean.\n', 'PHP bloğun hemen altındaki (boş satırsız) alan-dışı satırda "temiz"')
            + pos('girintili_devam', tr.replace('- EOL: DESTEKLENEN\n', '- EOL: DESTEKLENEN\n  (sürüm güvenli, risk yok)\n'), en.replace('- EOL: SUPPORTED\n', '- EOL: SUPPORTED\n  (version safe, no risk)\n'),
                  'PHP alanın altındaki girintili devam satırında "güvenli/risk yok"')
            + [('b2_bosluktan_sonra_yesil_' + dil, bool(bl.kod('a', r + '\nDeğerlendirme: PHP tarafı temiz.\n')), False, f'PHP boş satırdan SONRAKİ serbest metin blok bölgesi değil ({dil}): yanlış-pozitif')
               for dil, r in zip(('tr', 'en'), ok)]
            + [('b2_baslik_sonrasi_bos_' + dil, bool(bl.kod('a', r.replace(h, h + '\n'))), False, f'PHP başlıktan sonra boş satır, alanlar sonra ({dil}): yanlış-pozitif')
               for dil, r, h in (('tr', tr, '### PHP çalışma zamanı'), ('en', en, '### PHP runtime'))])


def b3_vakalari():
    tr, en = ok = bl.B()
    kanit = lambda k: bl.B(t2='EVET — kanıt: ' + k)  # noqa: E731
    wp = lambda k: bl.B(sonra=bl.sabit(0), **dict(bl.WP, t2='EVET — kanıt: ' + k))[0]  # noqa: E731
    return (bl.cift('b3_uydurma_dosya', 'a', ok, kanit('yok_boyle_dosya.xyz'), 'PHP T2 kanıtı hedefte olmayan dosya', 'T2_ALANI')
            + bl.cift('b3_biri_uydurma', 'a', ok, kanit('composer.json, yok_boyle.xyz'), 'PHP T2 kanıtında bir geçerli + bir uydurma dosya', 'T2_ALANI')
            + bl.cift('b3_satir_parantez', 'a', kanit('composer.json (kök), `Dockerfile:1`'), kanit('composer.json (kök), `Dockerfile:1`, yok.xyz'), 'PHP T2 kanıtı `:satır` ve (parantez) biçimi', 'T2_ALANI')
            + bl.cift('b3_dizin_kanit', 'a', kanit('composer.json, app/Http'), kanit('composer.json, app/Yok'), 'PHP T2 kanıtı dizin öneki', 'T2_ALANI')
            + [('b3_imzasiz_kanit', 'T2_ALANI' in pk.rapor_kontrol(t.olc_fx(t.FX['c']), wp('.htaccess')), True, 'PHP T2 kanıtı var olan ama imza vermeyen dosya (.htaccess) → T2_ALANI'),
               ('b3_imzali_dizin', 'T2_ALANI' in pk.rapor_kontrol(t.olc_fx(t.FX['c']), wp('wp-content')), False, 'PHP T2 kanıtı imza veren dizin (wp-content): yanlış-pozitif'),
               ('b3_noktalivirgul', 'T2_ALANI' in pk.rapor_kontrol(t.olc_fx(t.FX['c']), wp('wp-config.php; index.php')), False, 'PHP T2 kanıtı ";" ayraçlı: yanlış-pozitif'),
               ('b3_imzali_ve_imzasiz', 'T2_ALANI' in pk.rapor_kontrol(t.olc_fx(t.FX['c']), wp('wp-config.php, .htaccess')), False, 'PHP T2 kanıtı: bir imza dosyası + var olan imzasız dosya (any, all değil): yanlış-pozitif'),
               ('b3_baslik_son_satir', 'ALAN_YOK_T2' in pk.rapor_kontrol(t.olc_fx(t.FX['a']), '### PHP çalışma zamanı'), True, 'PHP rapor son satırı başlık (alan yok): çökmez, ALAN_YOK_T2'),
               ('b3_baslik_son_satir_bos', 'ALAN_YOK_T2' in pk.rapor_kontrol(t.olc_fx(t.FX['a']), '### PHP runtime\n\n\n'), True, 'PHP rapor başlıktan sonra yalnız boş satırlar: çökmez, ALAN_YOK_T2'),
               ('b3_bos_oge', 'T2_ALANI' in pk.rapor_kontrol(t.olc_fx(t.FX['c']), wp('wp-config.php,, index.php')), False, 'PHP T2 kanıtında boş öge (",,") atlanır: yanlış-pozitif')])


NOT_TR = ('Notlar:\n- EOL: 8.3 aktif destek 2025-12-31, güvenlik desteği 2027-12-31.\n- İmaj taraması: trivy resmî imajda PHP ikilisini görmedi.\n',
          'Notes:\n- EOL: 8.3 active support 2025-12-31, security support 2027-12-31.\n- Image scan: trivy did not see the PHP binary in the official image.\n')
TARAYICI_SATIR = [('tr1', 'Tarayıcı çözümü: PHP 8.5.12 (yüzen etiket, kaynak Dockerfile:1) — depodan değil.', 'Scanner result: PHP 8.5.12 (floating tag, source Dockerfile:1) — not from the repo.'),
                  ('tr2', 'grype: php-cli 7.4.33, taban Dockerfile:1 (yama düzeyi tarayıcıdan)', 'grype: php-cli 7.4.33, base Dockerfile:1 (patch level from the scanner)'),
                  ('tr3', 'Yama seviyesi tarayıcıdan: 7.4.33 (`Dockerfile:1` etiketinin bugünkü çözümü)', 'PHP 7.4.33 resolved by grype from the image built by Dockerfile:1'),
                  ('tr4', 'trivy: PHP 8.1.5 Dockerfile:1', 'trivy: PHP 8.1.5 Dockerfile:1'), ('tr5', 'syft: PHP 8.1.5 Dockerfile:1', 'syft: PHP 8.1.5 Dockerfile:1'),
                  ('tr6', 'PHP 8.1.5 scanner output Dockerfile:1', 'PHP 8.1.5 scanner output Dockerfile:1'), ('tr7', 'PHP 8.1.5 resolved Dockerfile:1', 'PHP 8.1.5 resolved Dockerfile:1'),
                  ('tr8', 'PHP 8.1.5 çözüldü Dockerfile:1', 'PHP 8.1.5 çözüldü Dockerfile:1'), ('tr9', 'PHP 8.1.5 tarayıcı Dockerfile:1', 'PHP 8.1.5 tarayıcı Dockerfile:1'),
                  ('grype_tek', 'grype: PHP 8.1.5 Dockerfile:1', 'grype: PHP 8.1.5 Dockerfile:1')]  # başka tarayıcı sözcüğü yok: yalnız "grype" kolu muaf eder


def b4_vakalari():
    tr, en = ok = bl.B()
    notlar = [(f'b4_notlar_{n}_{dil}', bool(bl.kod('a', r + '\n' + m)), False, f'PHP bloktan sonra BOŞ SATIRLA gelen "Notlar" alan etiketiyle başlasa da alan sayılmaz ({n}, {dil})')
              for n, i in (('eol_imaj', 0),) for dil, r, m in (('tr', tr, NOT_TR[0]), ('en', en, NOT_TR[1]))]
    notlar_bitisik = [('b4_notlar_bitisik_' + dil, 'ALAN_COK_EOL' in bl.kod('a', r + m), True, f'PHP bloğa BİTİŞİK (boş satırsız) alan etiketli not ALAN_COK_EOL ({dil})')
                      for dil, r, m in (('tr', tr, '- EOL: 8.3 aktif destek\n'), ('en', en, '- EOL: 8.3 active support\n'))]
    tarayici = [(f'b4_tarayici_{ad}_{dil}', bool(bl.kod('a', r + '\n' + m + '\n')), False, f'PHP tarayıcı-çözümü satırı (kaynak anan) UYDURMA_KAYNAK değil ({ad}, {dil})')
                for ad, trm, enm in TARAYICI_SATIR for dil, r, m in (('tr', tr, trm), ('en', en, enm))]
    imaj = (bl.cift('b4_imaj_sebep', 'a', bl.B(imaj='grype NOT MEASURED (no network) · trivy 12'), bl.B(imaj='grype NOT MEASURED (ab) · trivy 12'), 'PHP imaj alanı ÖLÇÜLEMEDİ (sebep) kabul; 2 karakterlik sebep red', 'IMAJ_ALANI')
            + bl.cift('b4_imaj_sebep_trivy', 'a', bl.B(imaj='grype 3 · trivy ÖLÇÜLEMEDİ (ağ yok)'), bl.B(imaj='grype 3 · trivy ÖLÇÜLEMEDİ (ağ (yok)'), 'PHP imaj alanı trivy ÖLÇÜLEMEDİ (sebep); iç içe parantez red', 'IMAJ_ALANI')
            + bl.cift('b4_imaj_sebep_bos', 'a', bl.B(imaj='grype ÖLÇÜLEMEDİ (ağ yok) · trivy ÖLÇÜLEMEDİ (imaj yok)'), bl.B(imaj='grype ÖLÇÜLEMEDİ () · trivy 3'), 'PHP imaj alanı boş sebep red', 'IMAJ_ALANI'))
    yol = [('b4_yol_baska_dizin', 'UYDURMA_KAYNAK' in bl.kod('dosya_df', bl.B(t2='EVET — kanıt: composer.json', surum='7.4 — kaynak: docker/php.Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='BULGU')[0] + '\nPHP 7.4 — baska/php.Dockerfile:1\n'), True,
            'PHP serbest metin başka dizindeki aynı adlı dosya → UYDURMA_KAYNAK (Bulgu 5 tutarsızlığı)'),
           ('b4_yol_gercek_tam', 'UYDURMA_KAYNAK' in bl.kod('dosya_df', bl.B(surum='7.4 — kaynak: docker/php.Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='BULGU')[0] + '\nPHP 7.4 — docker/php.Dockerfile:1\n'), False,
            'PHP serbest metin gerçek tam yol: yanlış-pozitif'),
           ('b4_yol_yalniz_ad', 'UYDURMA_KAYNAK' in bl.kod('dosya_df', bl.B(surum='7.4 — kaynak: docker/php.Dockerfile:1', yama='ÖLÇÜLEMEDİ', eol='BULGU')[0] + '\nPHP 7.4 — php.Dockerfile:1\n'), False,
            'PHP serbest metin yalnız dosya adı (dizinsiz): yanlış-pozitif'),
           ('b4_yol_nokta_slash', 'UYDURMA_KAYNAK' in bl.kod('a', bl.B()[0] + '\nPHP 8.3.30 — ./Dockerfile:1\n'), False, 'PHP serbest metin ./Dockerfile:1 gerçek kaynak: yanlış-pozitif'),
           ('b4_yol_nokta_slash_satir', 'UYDURMA_KAYNAK' in bl.kod('a', bl.B()[0] + '\nPHP 8.3.30 — ./Dockerfile:2\n'), True, 'PHP serbest metin ./Dockerfile:2 yanlış satır → UYDURMA_KAYNAK')]
    return notlar + notlar_bitisik + tarayici + imaj + yol


def b7_vakalari():
    """Kilit: SKILL/ref baslik surumu (§2.1 basligi artik v2.8.0) ve puan.py yol parametresi."""
    kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sonuc = []
    for dil, yol in (('tr', 'skills/gedik-tr/references/kod-inceleme-guvenlik.md'), ('en', 'skills/gedik/references/kod-inceleme-guvenlik.md')):
        with open(os.path.join(kok, *yol.split('/')), encoding='utf-8') as f:
            baslik = next(x for x in f.read().splitlines() if x.startswith('### 2.1'))
        sonuc.append((f'b7_baslik_surum_{dil}', '(v2.8.0)' in baslik and '(v2.7.0)' not in baslik, True, f'PHP §2.1 başlığı güncel sürümü gösterir ({dil})'))
    return sonuc


def g_vakalari():
    """DUZELT-2: G1 tarayici sozcuklu satirda yalniz SURUM muaf (dosya:satir gercek olmali) · G2 blok disi alan etiketli satirlar da `x.y … dosya:satir` denetimine girer."""
    tr, en = ok = bl.B()
    sonuc = []
    for ad, trm, enm, kirmizi in (('g1_sahte_satir', 'PHP 8.1.5 — Dockerfile:2 (trivy)', 'PHP 8.1.5 — Dockerfile:2 (trivy)', True),
                                  ('g1_sahte_dosya', 'PHP 8.1.5 — baska/Dockerfile:1 (grype)', 'PHP 8.1.5 — baska/Dockerfile:1 (grype)', True),
                                  ('g1_gercek_yer_baska_surum', 'PHP 8.5.12 — Dockerfile:1 (trivy çözdü)', 'PHP 8.5.12 — Dockerfile:1 (resolved by trivy)', False),
                                  ('g1_cozul_kokü', 'PHP 8.1.5 — Dockerfile:2 bu açık çözülmeli', 'PHP 8.1.5 — Dockerfile:2 this must be resolved', True),
                                  ('g1_tablo_sutunu', '| php-cli | 8.1.5 | Dockerfile:2 | trivy |', '| php-cli | 8.1.5 | Dockerfile:2 | trivy |', True),
                                  ('g1_sahte_dosya_gercek_satir', 'PHP 8.3.30 — Compose.yaml:1 (syft)', 'PHP 8.3.30 — Compose.yaml:1 (syft)', True)):
        sonuc += [(f'{ad}_{dil}', 'UYDURMA_KAYNAK' in bl.kod('a', r + '\n' + m + '\n'), kirmizi, f'PHP G1 ({ad}, {dil}): ' + ('KIRMIZI' if kirmizi else 'YEŞİL'))
                  for dil, r, m in (('tr', tr, trm), ('en', en, enm))]
    cel = bl.B(surum='8.3.30 — kaynak: Dockerfile:1; 7.4 — kaynak: docker-compose.prod.yml:3', yama='TAM', eol='BULGU')  # iki gerçek kaynak: yer eşleşmesi any (all değil)
    sonuc += [(f'g1_iki_kaynak_biri_gercek_{dil}', 'UYDURMA_KAYNAK' in bl.kod('celiski', r + '\nPHP 8.3.30 — Dockerfile:1 (trivy)\n'), False, f'PHP G1 çelişen iki kaynaktan biri gerçek ({dil}): YEŞİL')
              for dil, r in zip(('tr', 'en'), cel)]
    for ad, trm, enm, kirmizi in (('g2_sahte_surum', '- Sürüm: 8.1.5 — kaynak: Dockerfile:2', '- Version: 8.1.5 — source: Dockerfile:2', True),
                                  ('g2_sahte_dosya', '- Sürüm: 8.3.30 — kaynak: baska/Dockerfile:1', '- Version: 8.3.30 — source: baska/Dockerfile:1', True),
                                  ('g2_gercek_alan_satiri', '- Sürüm: 8.3.30 — kaynak: Dockerfile:1', '- Version: 8.3.30 — source: Dockerfile:1', False),
                                  ('g2_blockquote', '> - Sürüm: 8.1.5 — kaynak: Dockerfile:2', '> - Version: 8.1.5 — source: Dockerfile:2', True),
                                  ('g2_kalin_etiket', '- **Sürüm:** 8.1.5 — kaynak: Dockerfile:2', '- **Version:** 8.1.5 — source: Dockerfile:2', True),
                                  ('g2_deger_celiskisi_siniri', '- EOL: UYARI', '- EOL: WARNING', False)):  # değer çelişkisi kuralı YOK: README sınırı
        sonuc += [(f'{ad}_{dil}', 'UYDURMA_KAYNAK' in bl.kod('a', r + '\n' + m + '\n'), kirmizi, f'PHP G2 blok dışı alan satırı ({ad}, {dil}): ' + ('KIRMIZI' if kirmizi else 'YEŞİL'))
                  for dil, r, m in (('tr', tr, trm), ('en', en, enm))]
    return sonuc


def vakalar():
    if os.environ.get('GEDIK_PHP_ALT'):  # kopya dizinde skills/ yok: b7 atlanir
        return b1_vakalari() + b2_vakalari() + b3_vakalari() + b4_vakalari() + g_vakalari()
    return b1_vakalari() + b2_vakalari() + b3_vakalari() + b4_vakalari() + g_vakalari() + b7_vakalari()


if __name__ == '__main__':  # dogrudan calistirilinca vakalari KOSAR (sessiz yesil olmasin)
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sonuc = vakalar()
    for ad, yakti, beklenen, etiket in sonuc:
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<34} {etiket}")
    sys.exit(0 if all(y == b for _, y, b, _ in sonuc) else 1)
