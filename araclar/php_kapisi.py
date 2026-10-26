#!/usr/bin/env python3
"""php_kapisi.py — gedik v2.8.0: PHP rapor BLOGU kapisi (alan-tabanli; rapor denetimi + CLI). Yalniz standart kutuphane; hedefe ve rapora YAZMAZ.

  python araclar/php_kapisi.py --hedef DIZIN                 hedefin PHP olcumunu basar (imza, surum+kaynak, EOL, composer)
  python araclar/php_kapisi.py --hedef DIZIN --rapor RAPOR   rapordaki `### PHP çalışma zamanı` / `### PHP runtime` BLOGUNU olcume karsi denetler
  python araclar/php_kapisi.py --pozitif-kontrol             kor kapi oz-testi (D1/D2): bozuk fixture/rapor KIRMIZI, dogrular YESIL
Cikis: 0 = PASS/uygulanmaz · 1 = kusur ya da oz-test KOR · 2 = kullanim hatasi.

Olcum: php_olc.py · oz-test: php_oz_test.py + php_oz_duzelt.py · kural kaynagi: skills/gedik*/SKILL.md (blok sablonu) ve references/kod-inceleme-guvenlik.md §2.1.
v2.8.0: serbest-metin anahtar-sozcuk avi KALKTI (4 tur, her turda yeni okuma hatasi). Model SABIT ALANLI bir blogu doldurur; kapi her alani
php_olc olcumuyle BIREBIR karsilastirir. Kapinin DOGRULAYAMADIGI: (1) sayilarin (composer N, tarayici N) gercekligi · (2) ÖLÇÜLEMEDİ/UYGULANMAZ parantez SEBEP metninin icerigi (yalniz ≥3 karakter) ·
(3) serbest metnin TAMAMI — yalniz `PHP x.y … dosya:satir` kalibi denetlenir (kaynaksiz surum, "Dockerfile satir 2", php sozcuksuz satir, kisit sozcuklu satir kacar; tarayici sozcuklu satirda yalniz SURUM muaf, dosya:satir gercek olmali;
blok disi ALAN ETIKETLI satirlar da bu kalibi tasir ama alan DEGERI celiskisi — orn. bolge disi `EOL: DESTEKLENEN` — denetlenmez).
Blok bolgesi: basliktan ilk bos satira (ya da sonraki basliga) kadar; altindaki "Notlar:" alan sayilmaz. Blok bolgesinin TUM satirlarinda "temiz/guvenli/risk yok" yasak.
Sabit CVE tablosu YOKTUR (bayatlar); yalniz EOL dali kurali (php_olc) sabittir.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import date

import php_olc

SABIT_TR = 'PHP çalışma zamanı sürümü depoda yok — ÖLÇÜLEMEDİ; sunucu/hosting panelinden kontrol et.'
SABIT_EN = 'PHP runtime version is not in the repository — NOT MEASURED; check it on the server/hosting panel.'
BASLIK = re.compile(r'^[\s>]*#{1,6}\s*PHP\s+(?:çalışma zamanı|runtime)\s*:?\s*$')
HERHANGI_BASLIK = re.compile(r'^[\s>]*#{1,6}\s')
ETIKET = {'t2': ('T2 PHP', 'T2 PHP'), 'surum': ('Sürüm', 'Version'), 'yama': ('Yama düzeyi', 'Patch level'), 'eol': ('EOL', 'EOL'),
          'composer': ('composer audit', 'composer audit'), 'imaj': ('İmaj taraması', 'Image scan')}
ALAN_RE = re.compile(r'^[\s>]*(?:[-*]\s*)?(' + '|'.join(re.escape(e) for ikili in ETIKET.values() for e in dict.fromkeys(ikili)) + r')\s*:\s*(.*?)\s*$')
ETIKET_ANAHTAR = {e: k for k, ikili in ETIKET.items() for e in ikili}
TIRE = '[—–-]+'
OLC_DEGER = r'(?:ÖLÇÜLEMEDİ|NOT MEASURED)'
KAYNAK = r'(?:kaynak|source):\s*([^\s;,]+?):(\d+)'
SURUM_CIFTI = re.compile(r'(\d+\.\d+(?:\.\d+)?)\s*' + TIRE + r'\s*' + KAYNAK)
YUZEN_CIFTI = re.compile(r'(?:YÜZEN|FLOATING)\s+(\S+)\s+' + TIRE + r'\s*' + KAYNAK)  # etiket ile tire arasi bosluk ZORUNLU: `8-apache--kaynak:` reddedilir (belirsiz ayrisma)
T2_RE = re.compile(r'(EVET|YES|HAYIR|NO)(?:\s*' + TIRE + r'\s*(?:kanıt|evidence):\s*(\S.*))?')
COMPOSER_SAYI = re.compile(r'(\d+)\s+(?:danışma|advisor(?:y|ies))')
COMPOSER_OLC = re.compile(OLC_DEGER + r'\s*\((.{3,})\)')
COMPOSER_YOK = re.compile(r'(?:UYGULANMAZ|N/A)\s*\((.{3,})\)')
IMAJ_DEGER = r'(?:\d+|' + OLC_DEGER + r'(?:\s*\([^()]{3,}\))?)'  # sayi | ÖLÇÜLEMEDİ [(sebep)]
IMAJ_RE = re.compile(r'grype\s+' + IMAJ_DEGER + r'\s*[·|,;]\s*trivy\s+' + IMAJ_DEGER)
TARAYICI = r'grype|trivy|syft|tarayıcı|scanner|resolved|çözül'  # tarayicinin cozdugu duzey satiri (SKILL: blok disi serbest metin) UYDURMA_KAYNAK'tan muaf
EOL_ESLE = {'tamam': ('DESTEKLENEN', 'SUPPORTED'), 'uyari': ('UYARI', 'WARNING'), 'yok_yama': ('BULGU', 'FINDING'), None: ('ÖLÇÜLEMEDİ', 'NOT MEASURED')}
YAMA_ESLE = {'TAM': ('TAM', 'FULL'), 'OLC': ('ÖLÇÜLEMEDİ', 'NOT MEASURED')}
TEMIZ = (r'\b(?:temiz\w*|tertemiz|sorunsuz\w*|sorun (?:yok|görülmedi|bulunmadı)|güvenli(?!k)\w*|güncel ve yamalı|clean|safe|secure|'
         r'is patched|fully patched|no (?:known )?(?:issues?|vulnerabilit\w+)|nothing to worry|up[- ]to[- ]date|looks good|fine|'  # "looks fine" ⊂ fine; "is fully patched" ⊂ fully patched
         r'riski? yok|no (?:security )?risk|no action|all (?:good|clear))\b')  # "no action needed/is required" ⊂ no action
DOSYA_RE = (r'[\w.-]*[Dd]ockerfile[\w.-]*|Containerfile[\w.-]*|\.php-version|\.htaccess|[\w.-]+\.ya?ml|'
            r'composer\.json|[\w.-]+\.conf')  # TAM ad (`composer.lock` ≠ compose); buyuk/kucuk harf DUYARSIZ eslesir, kaynakla karsilastirma DUYARLI
PHP_ANISI = r'(?<![\w/.-])php'  # php, php-fpm, PHP-CLI, php.ini · swagger-php / gen_openapi.php degil
KISIT = r'alt sınır|lower bound|require|kısıt|constraint|[\^~>]=?\s*\d'


# ---------- rapor okuma / normalizasyon ----------
def rapor_oku(yol):
    with open(yol, 'rb') as f:
        ham = f.read(5_000_000)
    if ham[:2] in (b'\xff\xfe', b'\xfe\xff'):
        metin = ham.decode('utf-16', errors='replace')
    else:
        try:
            metin = ham.decode('utf-8-sig')
        except UnicodeDecodeError:
            metin = ham.decode('cp1254', errors='replace')
    return unicodedata.normalize('NFC', metin)


def duz(metin):
    """Karsilastirma icin: kucuk harf, biçim/noktalama ve tire farklari yok sayilir."""
    return re.sub(r'\s+', ' ', re.sub(r'[*_`"\'.]|[—–-]', ' ', unicodedata.normalize('NFC', metin).lower())).strip()


# ---------- blok ----------
def bos_satir(s):
    return not re.sub(r'[>\s]', '', s)  # "" ya da yalniz blockquote isareti


def blok_oku(rapor):
    """(baslik_sayisi, {alan: [deger,...]}, bolge_satirlari): ILK blok bolgesi = basliktan sonra (bastaki bos satirlar atlanir) ilk bos satira ya da
    sonraki basliga kadar olan satirlar. Alan satirlari bu bolgeden okunur (`**`/`` ` `` bicimi atilir); bolgenin TUM satirlari temiz-yasagina tabidir."""
    satirlar, alanlar, bolge, sayi, i = rapor.splitlines(), {}, [], 0, 0
    while i < len(satirlar):
        if not BASLIK.match(satirlar[i]):
            i += 1
            continue
        sayi += 1
        bas = i + 1
        while bas < len(satirlar) and bos_satir(satirlar[bas]):
            bas += 1
        son = bas
        while son < len(satirlar) and not bos_satir(satirlar[son]) and not HERHANGI_BASLIK.match(satirlar[son]):
            son += 1
        bolge = bolge if sayi > 1 else satirlar[bas:son]
        i = son
    for s in bolge:
        m = ALAN_RE.match(s.replace('**', '').replace('`', ''))
        if m:
            alanlar.setdefault(ETIKET_ANAHTAR[m.group(1)], []).append(m.group(2))
    return sayi, alanlar, bolge


def gercek_kaynaklar(o):
    """{(dosya_yolu, dosya_adi, satir, surum)}; composer.json platform kaynaginda config..platform.php satir araligindaki HER satir gecerlidir."""
    sonuc = set()
    for k in o['kaynaklar']:
        yol, satir = k['kaynak'].rsplit(':', 1)
        bas, son = k['aralik'] or (int(satir), int(satir))
        sonuc |= {(yol, os.path.basename(yol), str(n), k['surum']) for n in range(bas, son + 1)}
    return sonuc


def dosya_ayni(g, dosya):
    """Yazilan dosya gercek kaynakla ayni mi: `./` atilir; `dizin/ad` yazildiysa TAM yol, yalniz `ad` yazildiysa dosya adi (buyuk/kucuk harf DUYARLI)."""
    dosya = dosya[2:] if dosya.startswith('./') else dosya
    return dosya == g[0] or ('/' not in dosya and dosya == g[1])


def gercek_mi(gercek, surum, dosya, satir, onek=False):
    """onek=True (serbest metin): `x.y` dali, AYNI dosya:satirdaki gercek surumun oneki ise kabul (8.3 ← 8.3.30); baska dal/satir kabul degil."""
    uyar = lambda g: g[3] == surum or (onek and surum.count('.') == 1 and (g[3] or '').startswith(surum + '.'))  # noqa: E731
    return any(uyar(g) and g[2] == satir and dosya_ayni(g, dosya) for g in gercek)


def kanit_gecerli(o, kanit):
    """T2 kaniti: virgul/noktalivirgulle ayrilan HER oge hedefte VAR olmali (dosya yolu, dosya adi ya da dizin; `:satir` ve (parantez) atilir) ve en az biri
    PHP imza dosyasi olmali (php_olc imza listesi). Uydurma dosya adi → T2_ALANI."""
    ogeler = [x for x in (re.sub(r':\d+$', '', re.sub(r'\([^)]*\)', '', y)).strip(' `/') for y in re.split(r'[,;]', kanit)) if x]
    liste, imza = o['dosya_listesi'], o['imza_dosyalari']
    var = lambda x, l: any(f == x or f.endswith('/' + x) or f.startswith(x + '/') for f in l)  # noqa: E731
    return bool(ogeler) and all(var(x, liste) for x in ogeler) and any(var(x, imza) for x in ogeler)


# ---------- alan kontrolleri (kod listesi dondurur; bos = tamam) ----------
def kontrol_t2(o, deger):
    m = T2_RE.fullmatch(deger)
    ok = bool(m) and m.group(1) in ('EVET', 'YES') and bool(m.group(2)) and kanit_gecerli(o, m.group(2))  # PHP imzasi olculdu → EVET + hedefte var olan kanit sart
    return [] if ok else ['T2_ALANI']


def kontrol_surum(o, deger, rapor):
    gercek = gercek_kaynaklar(o)
    if o['surum']:
        ciftler = SURUM_CIFTI.findall(deger)
        artik = SURUM_CIFTI.sub('', deger).strip(' ;,')
        gerekli = {o['surum'], *o['surumler']}
        kod = [] if ciftler and not artik and gerekli <= {c[0] for c in ciftler} else ['SURUM_ALANI']
        return kod + (['KAYNAK_UYDURMA'] if any(not gercek_mi(gercek, *c) for c in ciftler) else [])
    if o['yuzen']:
        m = YUZEN_CIFTI.fullmatch(deger)
        y, (dosya, satir) = o['yuzen'], o['yuzen']['kaynak'].rsplit(':', 1)
        ok = bool(m) and re.sub(r'^php:', '', m.group(1)) == re.sub(r'^php:', '', y['etiket'])
        if not ok:
            return ['SURUM_ALANI']
        return [] if m.group(3) == satir and m.group(2) in (dosya, os.path.basename(dosya)) else ['KAYNAK_UYDURMA']
    yok = deger in ('YOK', 'NONE')
    sabit = not o['guclu'] or duz(SABIT_TR) in duz(rapor) or duz(SABIT_EN) in duz(rapor)  # sürüm hiçbir yerde yok: sabit satır (kütüphane hariç)
    return (['SURUM_ALANI'] if not yok else []) + (['SABIT_SATIR_YOK'] if yok and not sabit else [])


def kontrol_yama(o, deger):
    beklenen = YAMA_ESLE['TAM' if (o['surum'] and o['tam'] and not o['yalniz_ci']) else 'OLC']
    return [] if deger in beklenen else ['YAMA_ALANI']


def kontrol_eol(o, deger):
    return [] if deger in EOL_ESLE[o['eol']] else ['EOL_ALANI']


def kontrol_composer(o, deger):
    if o['composer_lock']:
        ok = COMPOSER_SAYI.fullmatch(deger) or COMPOSER_OLC.fullmatch(deger)
    else:
        ok = COMPOSER_YOK.fullmatch(deger)
    return [] if ok else ['COMPOSER_ALANI']


def kontrol_imaj(deger):
    return [] if IMAJ_RE.fullmatch(deger) else ['IMAJ_ALANI']


def uydurma_sebepleri(o, satirlar):
    """Serbest metinde 'PHP x.y[.z] ... Dosya:satir' iddiasi olcumdeki bir kaynakla (dosya+satir+surum) ESLESMIYORSA [(satir_no, (surum, dosya, satir), satir_metni)].
    Kisit satirlari muaf; `x.y` dali ayni dosya:satirdaki gercek surumun oneki ise kabul. Tarayici sozcuklu satirda yalniz SURUM muaf (tarayici imajdan baska
    surum cozebilir) — `dosya:satir` yine gercek bir kaynak olmali (G1). PHP anisi yerine ALAN ETIKETLI satirlar da denetlenir: blok bolgesi disina kacan
    `- Surum: 8.1.5 — kaynak: Dockerfile:2` satiri kapiyi atlatamaz (G2); alan DEGERI celiskisi (EOL/yama/T2) denetlenmez — README siniri."""
    gercek, sonuc = gercek_kaynaklar(o), []
    for no, s in enumerate(satirlar, 1):
        alan = ALAN_RE.match(s.replace('**', '').replace('`', ''))
        if not (re.search(PHP_ANISI, s, re.I) or alan) or re.search(KISIT, s, re.I):
            continue
        tarayici = re.search(TARAYICI, s, re.I)
        for v, f, n in re.findall(r'(?<![\d.])(\d+\.\d+(?:\.\d+)?)\b[^\n]{0,80}?([\w.\-/]+):(\d+)', s):
            yer_var = any(g[2] == n and dosya_ayni(g, f) for g in gercek)
            if re.fullmatch(DOSYA_RE, os.path.basename(f), re.I) and not (yer_var if tarayici else gercek_mi(gercek, v, f, n, onek=True)):
                sonuc.append((no, (v, f, n), s.strip()))
    return sonuc


def kusur_uydurma(o, satirlar):
    return ['UYDURMA_KAYNAK'] if uydurma_sebepleri(o, satirlar) else []


def alan_kontrol(o, alanlar, rapor):
    kod = []
    for anahtar in ETIKET:
        if anahtar not in alanlar:
            kod.append('ALAN_YOK_' + anahtar.upper())
        elif len(alanlar[anahtar]) > 1:
            kod.append('ALAN_COK_' + anahtar.upper())
    if kod:
        return kod
    a = {k: v[0] for k, v in alanlar.items()}
    return (kontrol_t2(o, a['t2']) + kontrol_surum(o, a['surum'], rapor) + kontrol_yama(o, a['yama']) + kontrol_eol(o, a['eol'])
            + kontrol_composer(o, a['composer']) + kontrol_imaj(a['imaj']))


def rapor_kontrol(o, rapor):
    """Olcume (php_olc.olc() ciktisi) gore rapordaki kusur kodlari; bos = kusur yok. PHP imzasi yoksa kapi uygulanmaz."""
    if not o['php']:
        return []
    sayi, alanlar, bolge = blok_oku(rapor)
    if sayi == 0:
        return ['BLOK_YOK']
    if sayi > 1:
        return ['BLOK_COK']
    kod = alan_kontrol(o, alanlar, rapor)
    kod += ['BLOK_TEMIZ'] if re.search(TEMIZ, '\n'.join(bolge), re.I) else []
    return kod + kusur_uydurma(o, rapor.splitlines())


def golden_kontrol(o, beklenen):
    """Fixture olcumu beklenen alanlardan sapiyorsa sapma listesi (imaj satiri silinince burasi yanar)."""
    return [f'{k}: beklenen {v!r}, olculen {o.get(k)!r}' for k, v in beklenen.items() if o.get(k) != v]


# ---------- CLI ----------
def bayatlik_uyarisi(o):
    gun = (date.today() - date.fromisoformat(o['eol_olcum_tarihi'])).days
    return f"UYARI: EOL verisi {gun} günlük (ölçüm {o['eol_olcum_tarihi']}) — php.net'ten yeniden doğrula" if gun > 120 else ''


def main(argv):
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(prog='php_kapisi.py', allow_abbrev=False, description='gedik PHP rapor bloğu kapısı')
    ap.add_argument('--hedef', help='denetlenen hedef dizin')
    ap.add_argument('--rapor', help='gedik raporu (md/metin); verilirse ölçüme karşı denetlenir')
    ap.add_argument('--pozitif-kontrol', action='store_true', help='kör kapı öz-testi')
    a = ap.parse_args(argv)
    if a.pozitif_kontrol:
        import php_oz_test
        gecti = php_oz_test.oz_test()
        print('KAPI GÖRÜYOR' if gecti else 'KAPI KÖR — ölçüm reddedilir')
        return 0 if gecti else 1
    if not a.hedef or not os.path.isdir(a.hedef) or (a.rapor and not os.path.isfile(a.rapor)):
        print('--hedef DİZİN (ve varsa --rapor DOSYA) gerekli', file=sys.stderr)
        return 2
    o = php_olc.olc(a.hedef)
    print(json.dumps({k: v for k, v in o.items() if k not in ('dosya_listesi', 'imza_dosyalari')}, ensure_ascii=False, indent=1, default=str), bayatlik_uyarisi(o), sep='\n')
    if not a.rapor:
        return 0
    rapor_metni = rapor_oku(a.rapor)
    kusur = rapor_kontrol(o, rapor_metni)
    kismi = f" · ÖLÇÜLEMEDİ (kısmi): {len(o['okunamayan'])} dosya okunamadı/kesildi" if o['okunamayan'] else ''
    for no, uclu, satir in (uydurma_sebepleri(o, rapor_metni.splitlines()) if o['php'] else []):
        print(f'  sebep UYDURMA_KAYNAK: rapor satır {no}: (sürüm, dosya, satır) = {uclu} ölçümde yok → {satir[:160]}')
    print(('PASS' if not kusur else 'FAIL ' + ', '.join(kusur)) + ('' if o['php'] else ' (PHP imzası yok → uygulanmaz)') + kismi)
    return 1 if kusur else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
