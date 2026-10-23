"""php_olc.py — gedik v2.7.0: PHP olcumu (deterministik referans). Yalniz standart kutuphane; hedefe YAZMAZ.

Kural kaynagi: skills/gedik*/references/kod-inceleme-guvenlik.md §2.1 (sabit CVE tablosu YOKTUR; yalniz EOL dali kurali sabittir ve
EOL_OLCUM_TARIHI ile yazilidir). Bu modul yalniz DEPODAN gorulebileni olcer; okunamayani `okunamayan`/`kesildi` listesine yazar,
sessizce temiz saymaz. php_kapisi.py raporu bu olcume karsi denetler; php_oz_test.py kor kapi oz-testidir.
"""
import json
import os
import re
from datetime import date

ATLA = {'.git', 'node_modules', 'vendor', '__pycache__', '.venv'}
UYARI_YOLU = {'test', 'tests', 'spec', '__tests__', 'fixtures', 'fixture', 'example', 'examples', 'docs', 'doc'}  # kok kaynagi sayilmaz
EOL_OLCUM_TARIHI = '2026-10-22'  # php.net supported-versions + eol.php; YENIDEN DOGRULA (bayatlar)
EOL_8_2 = date(2026, 12, 31)
ONCELIK = {'imaj': 0, 'php-version': 1, 'composer-platform': 2, 'ci': 3, 'platform': 4}
CALISAN = ('imaj', 'php-version', 'composer-platform', 'platform')
ENC_SINIR = 1_000_000
SURUM = r'\d{1,3}\.\d{1,3}(?:\.\d{1,3})?'
HTACCESS_PHP = re.compile(r'(?:Add|Set)Handler[^\n]*php|x-httpd[^\n]*php|php_(?:value|flag)', re.I)
FROM_RE = re.compile(r'^\s*FROM\s+(?:--\S+\s+)*(\S+)', re.I)
ARG_RE = re.compile(r'^\s*ARG\s+(\w+)=(\S+)', re.I)
COMPOSE_RE = re.compile(r'^\s*image:\s*[\'"]?([^\s\'"]+)', re.I)
IMAJ_DOSYASI = re.compile(r'^((.*[.\-_])?(Dockerfile|Containerfile)(\..*)?|(docker-)?compose[\w.\-]*\.ya?ml)$', re.I)  # php.Dockerfile dahil; composer.json compose DEĞİLDİR
CI_DOSYA = re.compile(r'(^|/)(\.github/workflows/[^/]+\.ya?ml|\.gitlab-ci\.yml|\.circleci/config\.yml|azure-pipelines\.yml|\.travis\.yml|bitbucket-pipelines\.yml)$')
PLATFORM = {'.platform.app.yaml': r'type:\s*[\'"]?php:(' + SURUM + ')', 'app.yaml': r'runtime:\s*[\'"]?php(\d)(\d)(?!\d)',
            '.htaccess': r'x-httpd-(?:ea-|alt-)?php(\d)(\d)|php(\d)\.(\d)-fpm'}
GUCLU = {'artisan', 'symfony.lock', 'wp-config.php', 'wp-content/', 'index.php (kök)', 'php-fpm havuz dosyası', '.htaccess (PHP işleyici)', 'FROM php: / image: php'}
KOK_IMZA = {'index.php': 'index.php (kök)', 'wp-config.php': 'wp-config.php'}
HER_YERDE = {'composer.json': 'composer.json', 'artisan': 'artisan', 'symfony.lock': 'symfony.lock'}


# ---------- dosya erisimi (cokmez; okunamayani/kesileni kaydeder) ----------
def dosyalar(kok):
    sonuc, hata = [], []
    for dizin, altlar, adlar in os.walk(kok, onerror=lambda e: hata.append(str(e.filename))):
        altlar[:] = sorted(a for a in altlar if a not in ATLA)
        sonuc += [os.path.relpath(os.path.join(dizin, a), kok).replace(os.sep, '/') for a in sorted(adlar)]
    return sonuc, hata


def oku(kok, yol, sorun):
    """Metin; duz dosya degilse ya da okunamazsa '' ve sorun listesine yazar; ENC_SINIR'i asan dosya KESILDI diye isaretlenir."""
    tam = os.path.join(kok, *yol.split('/'))
    try:
        if not os.path.isfile(tam):
            sorun.append(f'{yol}: düz dosya değil')
            return ''
        with open(tam, 'rb') as f:
            ham = f.read(ENC_SINIR + 1)
    except OSError:
        sorun.append(f'{yol}: okunamadı')
        return ''
    if len(ham) > ENC_SINIR:
        sorun.append(f'{yol}: {ENC_SINIR} bayttan sonrası KESİLDİ')
    return ham[:ENC_SINIR].decode('utf-8-sig', errors='replace')


def yorumsuz(metin):
    return [re.sub(r'(^|\s)#.*$', '', s) for s in metin.splitlines()]


def uyari_yolu(yol):
    return any(p.lower() in UYARI_YOLU for p in yol.split('/')[:-1])


# ---------- surum cozumleme ----------
def surum_coz(etiket):
    """(surum, tam, ana): '8.3.30-fpm' -> ('8.3.30', True, 8); '8.1' -> ('8.1', False, 8); '7-apache' -> (None, False, 7); 'latest' -> (None, False, None)."""
    etiket = re.sub(r'^(php-?|v)', '', (etiket or '').strip().lstrip('^~>=<! '), flags=re.I)
    m = re.match(r'(\d{1,3})\.(\d{1,3})(\.\d{1,3})?', etiket)
    if m:
        return m.group(0), bool(m.group(3)), int(m.group(1))
    m = re.match(r'(\d{1,3})(?![\d.])', etiket)
    return None, False, (int(m.group(1)) if m else None)


def kayit(tur, kaynak, etiket, calisan=True, aralik=None):
    s, tam, ana = surum_coz(etiket)
    return {'tur': tur, 'kaynak': kaynak, 'surum': s, 'tam': tam, 'ana': ana, 'etiket': etiket, 'calisan': calisan, 'aralik': aralik}


def eol_durumu(surum, ana, bugun):
    """<= 8.1 yama yok · 8.2 uyari (2026-12-31'e kadar; sonra yok_yama) · digeri tamam; yalniz ana<=7 bilinirse yok_yama. Olcum EOL_OLCUM_TARIHI."""
    if not surum:
        return 'yok_yama' if ana is not None and ana <= 7 else None
    a, b = (int(x) for x in surum.split('.')[:2])
    if (a, b) <= (8, 1) or ((a, b) == (8, 2) and bugun > EOL_8_2):
        return 'yok_yama'
    return 'uyari' if (a, b) == (8, 2) else 'tamam'


# ---------- kaynaklar ----------
def imaj_etiketi(imaj):
    """Resmi php imaji ('php:', 'library/php:', 'docker.io/php:', 'docker.io/library/php:') ya da wordpress:*-phpX.Y -> etiket; ucuncu taraf imaj -> None."""
    m = re.match(r'^(?:(?:[\w.\-]+(?::\d+)?/)*library/|(?:index\.)?docker\.io/)?php[:@](.*)$', imaj, re.I)
    if m:
        return m.group(1)
    m = re.search(r'(?:^|/)wordpress:\S*?-php(\d+\.\d+)', imaj, re.I)
    return m.group(1) if m else None


def imaj_kaynaklari(yol, metin):
    satirlar, sonuc, args = yorumsuz(metin), [], {}
    dockerfile = not re.search(r'\.ya?ml$', os.path.basename(yol), re.I)  # compose = yml; php.Dockerfile compose sayılmaz
    for i, satir in enumerate(satirlar, 1):
        a = ARG_RE.match(satir)
        args.update({a.group(1): a.group(2)} if a else {})
        m = (FROM_RE if dockerfile else COMPOSE_RE).match(satir)
        imaj = re.sub(r'\$\{?(\w+)\}?', lambda x: args.get(x.group(1), x.group(0)), m.group(1)) if m else ''
        etiket = imaj_etiketi(imaj) if imaj else None
        if etiket is not None:
            sonuc.append(kayit('imaj', f'{yol}:{i}', etiket))
    for k in sonuc[:-1] if dockerfile else []:
        k['calisan'] = False  # çok aşamalı Dockerfile: yalnız SON aşama çalışma zamanıdır
    return sonuc


def ci_kaynaklari(yol, metin):
    sonuc, blok = [], False
    for i, satir in enumerate(yorumsuz(metin), 1):
        m = re.search(r'\bphp(?:-version)?s?:\s*(.*)$', satir, re.I)
        blok = (not m.group(1).strip()) if m else (blok and bool(re.match(r'\s*-\s*', satir)))
        degerler = re.findall(SURUM, m.group(1) if m else satir) if (m or blok) else []
        sonuc += [kayit('ci', f'{yol}:{i}', t) for t in degerler]
    return sonuc


def platform_kaynaklari(yol, metin):
    kalip = PLATFORM.get(os.path.basename(yol).lower())
    sonuc = []
    for i, satir in enumerate(yorumsuz(metin), 1):
        m = re.search(kalip, satir, re.I) if kalip else None
        if m:
            parcalar = [g for g in m.groups() if g]
            sonuc.append(kayit('platform', f'{yol}:{i}', '.'.join(parcalar) if len(parcalar) > 1 else parcalar[0]))
    return sonuc


def tekil_kaynaklar(yol, metin):
    ad = os.path.basename(yol).lower()
    if ad == '.php-version':
        ilk = next(((i, s.strip()) for i, s in enumerate(yorumsuz(metin), 1) if s.strip()), None)
        return [kayit('php-version', f'{yol}:{ilk[0]}', ilk[1])] if ilk else []
    if ad != 'composer.json':
        return []
    try:
        plat = (json.loads(metin).get('config') or {}).get('platform') or {}  # 'require.php' SAYILMAZ
    except (ValueError, AttributeError):
        return []
    anahtar = 'php' if isinstance(plat, dict) and plat.get('php') else 'php-64bit'
    deger = plat.get(anahtar) if isinstance(plat, dict) else None
    if not deger:
        return []
    bas, son = platform_satiri(metin, anahtar)
    return [kayit('composer-platform', f'{yol}:{son}', str(deger), aralik=(bas, son))]


def platform_satiri(metin, anahtar):
    """(config satiri, platform.<anahtar> satiri): metinde sirayla "config" > "platform" > "<anahtar>" aranir; bulunamazsa 1 (tek satirlik json dahil)."""
    satirlar, i, ilk = metin.lstrip('﻿').splitlines(), 0, None
    for kalip in ('config', 'platform', anahtar):
        j = next((n for n in range(i, len(satirlar)) if re.search(r'"' + kalip + r'"\s*:', satirlar[n])), None)
        ilk = j if ilk is None else ilk
        i = i if j is None else j
    return (ilk or 0) + 1, i + 1


def kaynaklar(kok, liste, sorun):
    sonuc = []
    for yol in liste:
        ad = os.path.basename(yol)
        if uyari_yolu(yol):
            continue
        ilgili = IMAJ_DOSYASI.match(ad) or CI_DOSYA.search(yol) or ad.lower() in ('.php-version', 'composer.json', *PLATFORM)
        metin = oku(kok, yol, sorun) if ilgili else ''
        if IMAJ_DOSYASI.match(ad):
            sonuc += imaj_kaynaklari(yol, metin)
        elif CI_DOSYA.search(yol):
            sonuc += ci_kaynaklari(yol, metin)
        elif ilgili:
            sonuc += tekil_kaynaklar(yol, metin) + platform_kaynaklari(yol, metin)
    return sorted(sonuc, key=lambda k: ONCELIK[k['tur']])


# ---------- imzalar ----------
def dosya_imzasi(kok, yol, sorun):
    ad, alt = os.path.basename(yol).lower(), yol.lower()
    imza = {HER_YERDE[ad]} if ad in HER_YERDE else set()
    imza |= {KOK_IMZA[alt]} if alt in KOK_IMZA else set()
    imza |= {'wp-content/'} if alt.startswith('wp-content/') else set()
    if re.match(r'php-fpm.*\.conf$', ad) or 'php-fpm.d/' in alt:
        imza.add('php-fpm havuz dosyası')
    if re.search(r'\.(php|phtml|php5|php7)$', ad):
        imza.add('*.php dosyası')
    if ad == '.htaccess' and HTACCESS_PHP.search(oku(kok, yol, sorun)):
        imza.add('.htaccess (PHP işleyici)')
    if IMAJ_DOSYASI.match(os.path.basename(yol)) and imaj_kaynaklari(yol, oku(kok, yol, sorun)):
        imza.add('FROM php: / image: php')
    return imza


def imzalar(kok, liste, sorun):
    imza = set()
    for yol in liste:
        imza |= set() if uyari_yolu(yol) else dosya_imzasi(kok, yol, sorun)
    return sorted(imza)


# ---------- olcum ----------
def _anahtar(k):
    if k['surum']:
        a, b = k['surum'].split('.')[:2]
        return int(a), int(b)
    return k['ana'] or 99, 99


def _secim(kay):
    """(calisan kaynaklar, cozulen, yalniz_ci, yuzen): cozulen = CI HARIC ilk surumlu kaynak; yuzen = surumsuz ama kaynagi var."""
    calisan = [k for k in kay if k['tur'] in CALISAN and k['calisan']]
    cozulen = next((k for k in calisan if k['surum']), None)
    yalniz_ci = None if cozulen else next((k for k in kay if k['tur'] == 'ci' and k['surum']), None)
    yuzen = None if cozulen else next((k for k in calisan if not k['surum']), None)  # CI surumu yuzen calisma zamanini GOLGELEMEZ
    return calisan, cozulen, yalniz_ci, yuzen


def _composer(liste):
    adlar = {y: os.path.basename(y).lower() for y in liste if not uyari_yolu(y)}
    return 'composer.json' in adlar.values(), 'composer.lock' in adlar.values()


def _eol_alanlari(calisan, yalniz_ci, bugun):
    """(eol, en_eski): EOL, CALISAN kaynaklarin EN ESKISINE uygulanir (CI matrisi calisma zamani degildir; EOL'u dogurmaz ama gizlemez)."""
    eski = [k for k in calisan if k['surum'] or (k['ana'] is not None and k['ana'] <= 7)]
    en = min(eski, key=_anahtar, default=None)
    ad = en and (en['surum'] or f"{en['ana']}.x")
    return eol_durumu(en and en['surum'], en and en['ana'], bugun), ad


def _celiski(surumler):
    return len({s.rsplit('.', 1)[0] if s.count('.') == 2 else s for s in surumler}) > 1


def olc(kok, bugun=None):
    bugun = bugun or date.today()
    liste, hata = dosyalar(kok)
    sorun = [f'dizin okunamadı: {h}' for h in hata]
    imza, kay = imzalar(kok, liste, sorun), kaynaklar(kok, liste, sorun)
    calisan, cozulen, yalniz_ci, yuzen = _secim(kay)
    secili = cozulen or yalniz_ci or {}
    eol, en_eski = _eol_alanlari(calisan, yalniz_ci, bugun)
    surumler = sorted({k['surum'] for k in calisan if k['surum']})
    cj, cl = _composer(liste)
    return {'php': bool(imza), 'guclu': bool(GUCLU & set(imza)), 'isaretler': imza, 'kaynaklar': kay, 'surum': secili.get('surum'), 'yuzen': yuzen,
            'tam': bool(secili.get('tam')), 'kaynak': secili.get('kaynak'), 'yalniz_ci': bool(yalniz_ci),
            'surumler': surumler, 'ci_surumleri': sorted({k['surum'] for k in kay if k['tur'] == 'ci'}), 'celiski': _celiski(surumler),
            'eol': eol, 'en_eski': en_eski,
            'eol_olcum_tarihi': EOL_OLCUM_TARIHI, 'composer_json': cj, 'composer_lock': cl, 'okunamayan': sorun}
