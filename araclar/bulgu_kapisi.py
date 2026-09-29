#!/usr/bin/env python3
"""bulgu_kapisi.py — gedik-bulgular.json sema kapisi (gedik v2.6, spec A). Yalniz standart kutuphane; dosya yazmaz.

  python araclar/bulgu_kapisi.py                    ./gedik-bulgular.json dogrular; dosya yoksa ATLANDI (sessiz degil)
  python araclar/bulgu_kapisi.py --dosya YOL        acik yolu dogrular; yol yoksa FAIL (ATLANDI yalniz varsayilan aramada)
  python araclar/bulgu_kapisi.py --pozitif-kontrol  kor kapi oz-testi (D1/D2): bozuk kayit KIRMIZI, temiz kayit YESIL yakmali
Cikis: 0 = PASS/ATLANDI · 1 = FAIL ya da oz-test KOR · 2 = kullanim hatasi (tanimayan bayrak, degersiz --dosya).

Sema: araclar/bulgu-semasi.json (JSON Schema draft-07 alt kumesi). Kapi yalniz semanin kullandigi anahtarlari tanir;
tanimadigi bir anahtarda KIRMIZI yakar (sema duzenlemesi kapiyi sessizce kor birakamaz). Sema disi kurallar:
bulgu_id tekildir; kapsam'da her yuzey en fazla bir kez.
"""
import argparse
import contextlib
import io
import json
import os
import re
import sys
import tempfile
from collections import Counter

DOSYA_ADI = 'gedik-bulgular.json'
ARACLAR = os.path.dirname(os.path.abspath(__file__))
SEMA_YOLU = os.path.join(ARACLAR, 'bulgu-semasi.json')
BELGELER = [os.path.join(ARACLAR, '..', 'skills', d, 'references', 'kanit-ve-rapor.md') for d in ('gedik-tr', 'gedik')]
NOT_ANAHTARLARI = {'$schema', '$comment', '$id', 'title', 'description', 'definitions'}
TIPLER = {'object': dict, 'array': list, 'string': str}


# ---------- kucuk dogrulayici (JSON Schema alt kumesi) ----------
def _coz(ref, kok):
    if not ref.startswith('#/'):
        raise ValueError(f'desteklenmeyen $ref: {ref!r}')
    d = kok
    for parca in ref[2:].split('/'):
        d = d[parca]
    return d


def _secenek(d, kural, s, kok, yol):
    return [] if d in kural else [f'{yol}: {d!r} gecersiz (izinli: {" | ".join(kural)})']


def _desen(d, kural, s, kok, yol):
    """ECMA-262'de '$' yalniz girdi sonunda eslesir; Python'da sondaki '\\n' oncesinde de eslesir → '\\Z'."""
    if not isinstance(d, str) or re.search(re.sub(r'(?<!\\)\$', r'\\Z', kural), d):
        return []
    return [f'{yol}: bos ya da bicim uygun degil ({kural})']


def _zorunlu(d, kural, s, kok, yol):
    if not isinstance(d, dict):
        return []
    return [f'{yol}: zorunlu alan yok: {k}' for k in kural if k not in d]


def _ozellikler(d, kural, s, kok, yol):
    hatalar = []
    for ad, alt in (kural.items() if isinstance(d, dict) else ()):
        if ad in d:
            hatalar += dogrula(d[ad], alt, kok, f'{yol}.{ad}')
    return hatalar


def _ek_ozellik(d, kural, s, kok, yol):
    if kural is not False:
        raise ValueError('additionalProperties yalniz false desteklenir')
    if not isinstance(d, dict):
        return []
    return [f'{yol}: bilinmeyen alan: {k}' for k in d if k not in s.get('properties', {})]


def _ogeler(d, kural, s, kok, yol):
    hatalar = []
    for i, oge in enumerate(d if isinstance(d, list) else ()):
        hatalar += dogrula(oge, kural, kok, f'{yol}[{i}]')
    return hatalar


def _eger(d, kural, s, kok, yol):
    kosul = dogrula(d, kural, kok, yol)
    sema_hatasi = [h for h in kosul if h.startswith('SEMA:')]
    if sema_hatasi:
        return sema_hatasi  # koşul alt-semasindaki tanimsiz anahtar 'kosul saglanmadi' diye yutulmaz
    dal = s.get('else' if kosul else 'then')
    return dogrula(d, dal, kok, yol) if dal is not None else []


ISLEYICILER = {  # (deger, kural, ust_sema, kok_sema, yol) -> hata listesi
    'type': lambda d, k, s, kok, y: [] if isinstance(d, TIPLER[k]) else [f'{y}: {k} olmali'],
    'const': lambda d, k, s, kok, y: [] if d == k else [f'{y}: {k!r} olmali'],
    'minItems': lambda d, k, s, kok, y: [f'{y}: en az {k} oge gerekir'] if isinstance(d, list) and len(d) < k else [],
    'allOf': lambda d, k, s, kok, y: [h for alt in k for h in dogrula(d, alt, kok, y)],
    'then': lambda *a: [], 'else': lambda *a: [],  # 'if' isleyicisi okur
    'enum': _secenek, 'pattern': _desen, 'required': _zorunlu, 'properties': _ozellikler,
    'additionalProperties': _ek_ozellik, 'items': _ogeler, 'if': _eger,
}


def dogrula(d, s, kok=None, yol='$'):
    """d degerini s semasina karsi dogrular; hata satirlari listesi (bos = uygun)."""
    kok = s if kok is None else kok
    if isinstance(s, bool):
        return [] if s else [f'{yol}: bu alan bu hukumde YASAK']
    if '$ref' in s:
        return dogrula(d, _coz(s['$ref'], kok), kok, yol)
    hatalar = []
    for anahtar, kural in s.items():
        if anahtar in NOT_ANAHTARLARI:
            continue
        isleyici = ISLEYICILER.get(anahtar)
        if isleyici is None:
            hatalar.append(f'SEMA: desteklenmeyen anahtar {anahtar!r} ({yol}) — kapi bunu dogrulayamaz')
        else:
            hatalar += isleyici(d, kural, s, kok, yol)
    return hatalar


# ---------- anlamsal kurallar + dosya kapisi ----------
def anlamsal(veri):
    """Semanin ifade edemedigi kurallar: bulgu_id tekildir; kapsam'da her yuzey en fazla bir kez."""
    hatalar = []
    for anahtar, alan in (('bulgular', 'bulgu_id'), ('kapsam', 'yuzey')):
        liste = veri.get(anahtar) if isinstance(veri, dict) else None
        degerler = [o.get(alan) for o in liste if isinstance(o, dict)] if isinstance(liste, list) else []
        sayac = Counter(x for x in degerler if isinstance(x, str))
        hatalar += [f'$.{anahtar}: {alan} yinelenmis: {k}' for k, n in sorted(sayac.items()) if n > 1]
    return hatalar


def kontrol(veri, sema):
    return dogrula(veri, sema) + anlamsal(veri)


def _tekil_anahtar(ciftler):
    """JSON'da yinelenen anahtar (ör. iki 'hukum') sessizce son degeri kazandirir; bu kapida reddedilir."""
    sonuc = {}
    for k, v in ciftler:
        if k in sonuc:
            raise ValueError(f'yinelenen anahtar: {k}')
        sonuc[k] = v
    return sonuc


def yukle(metin):
    return json.loads(metin, object_pairs_hook=_tekil_anahtar)


def sema_yukle():
    with open(SEMA_YOLU, 'rb') as f:
        return yukle(f.read().decode('utf-8-sig'))


def kapi(kok, yol=None):
    """Dondurur: (PASS | FAIL | ATLANDI, kanit). kapilar.py bunu zincirine katar. ATLANDI yalniz varsayilan aramada."""
    acik = yol is not None
    if not acik:
        yol = os.path.join(kok, DOSYA_ADI)
    if not os.path.isfile(yol):
        return ('FAIL', f'belirtilen dosya yok: {yol}') if acik else ('ATLANDI', f'{DOSYA_ADI} yok — bu koşumda bulgu dosyası üretilmemiş')
    try:
        sema = sema_yukle()
        with open(yol, 'rb') as f:
            veri = yukle(f.read().decode('utf-8-sig'))
        hatalar = kontrol(veri, sema)
    except (OSError, ValueError, KeyError, RecursionError) as e:  # json.JSONDecodeError ValueError alt sinifidir
        return 'FAIL', f'okunamadı/çözümlenemedi: {type(e).__name__} {str(e)[:80]}'
    if hatalar:
        return 'FAIL', f'{len(hatalar)} ihlal · {hatalar[0][:100]}'
    return 'PASS', f"{len(veri['bulgular'])} kayıt, {len(veri['kapsam'])} kapsam satırı şemaya uygun"


# ---------- kor kapi oz-testi (D1/D2): sema disi ikinci kayit; bilerek bozuk kayitlar KIRMIZI, temizler YESIL yakmali ----------
def temiz_ornek():
    return {
        'sema': 'gedik-bulgular/1',
        'bulgular': [
            {'bulgu_id': 'G-1', 'serit': 'B', 'hukum': 'confirmed', 'siddet': 'KRITIK',
             'etkilenen': 'api/orders.js:42 (no ownership check)',
             'poc_girdi': 'GET /orders/1002 (session: user A)',
             'gozlenen': 'HTTP 200, 1 row, fields: id, owner_id, total',
             'tekrar_uretim': '1) sign in as A 2) GET /orders/1002 3) response belongs to B',
             'yama': 'add owner_id = :uid to the query', 'dogrulayan': 'alt-ajan'},
            {'bulgu_id': 'G-2', 'serit': 'C', 'hukum': 'needs_validation',
             'etkilenen': 'supabase/migrations/0003.sql',
             'cozulmemis_olgu': 'is RLS enabled on the live project? only the migration was read'},
            {'bulgu_id': 'G-3', 'serit': 'A', 'hukum': 'rejected', 'dogrulayan': 'ayri-tur',
             'eleme_nedeni': 'sink is fed only by a constant template (origin traced)'},
        ],
        'kapsam': [
            {'yuzey': 'A', 'durum': 'olculdu'}, {'yuzey': 'B', 'durum': 'olculdu'},
            {'yuzey': 'C', 'durum': 'olculmedi', 'sebep': 'no live authorization'},
            {'yuzey': 'D', 'durum': 'mimari-yok'},
        ],
    }


IDX = {'confirmed': 0, 'needs_validation': 1, 'rejected': 2}  # temiz_ornek()'teki kayit sirasi
BEKLENEN = {  # spec A'nin SEMADAN BAGIMSIZ kaydi: hukum -> (zorunlu, yasak); sema gevserse ya da siklasirsa oz-test kirmizi yakar
    'confirmed': (('siddet', 'etkilenen', 'poc_girdi', 'gozlenen', 'tekrar_uretim', 'yama', 'dogrulayan'), ('cozulmemis_olgu', 'eleme_nedeni')),
    'needs_validation': (('cozulmemis_olgu',), ('siddet', 'eleme_nedeni')),
    'rejected': (('eleme_nedeni',), ('siddet', 'cozulmemis_olgu')),
}
GECERLI = {'siddet': 'ORTA'}  # yasak-alan vakalarinda alanin kendi enum'una uyan deger: kirmizi yalniz YASAK yuzunden yanmali
METIN_ALANLARI = ('etkilenen', 'poc_girdi', 'gozlenen', 'tekrar_uretim', 'yama', 'cozulmemis_olgu', 'eleme_nedeni')
YUZEYLER = ('A', 'B', 'C', 'D', 'E', 'TEST', 'KOD', 'CICD')
YAPI_BOZUKLARI = [  # (ad, temiz ornegi bozan degisiklik) — her biri KIRMIZI yakmali
    ('hukum_olculmedi', lambda d: d['bulgular'][1].update(hukum='OLCULMEDI')),
    ('hukum_yok', lambda d: d['bulgular'][1].pop('hukum')),
    ('hukum_null', lambda d: d['bulgular'][1].update(hukum=None)),
    ('bulgu_id_yok', lambda d: d['bulgular'][0].pop('bulgu_id')),
    ('serit_yok', lambda d: d['bulgular'][0].pop('serit')),
    ('bulgu_id_satirsonu', lambda d: d['bulgular'][2].update(bulgu_id='G-3\n')),
    ('bulgu_id_yinelenen', lambda d: d['bulgular'][2].update(bulgu_id='G-1')),
    ('bulgu_ek_alan', lambda d: d['bulgular'][0].update(severity='HIGH')),
    ('bulgu_nesne_degil', lambda d: d['bulgular'].append(5)),
    ('kapsam_bos', lambda d: d.update(kapsam=[])),
    ('kapsam_oge_nesne_degil', lambda d: d['kapsam'].append(5)),
    ('kapsam_olculmedi_sebepsiz', lambda d: d['kapsam'][2].pop('sebep')),
    ('kapsam_sebep_bos', lambda d: d['kapsam'][2].update(sebep='  ')),
    ('kapsam_yuzey_yinelenen', lambda d: d['kapsam'].append({'yuzey': 'A', 'durum': 'olculdu'})),
] + [(f'bulgu[0].{a}={v!r}', lambda d, a=a, v=v: d['bulgular'][0].update({a: v})) for a, v in (
    ('serit', 'Z'), ('siddet', 'HIGH'), ('siddet', 'KRİTİK'), ('dogrulayan', 'bulan'),
    ('bulgu_id', 'Z-1'), ('bulgu_id', 'G-0'), ('bulgu_id', 'G-01'), ('bulgu_id', 1))
] + [(f'kok.{k}={v!r}', lambda d, k=k, v=v: d.update({k: v})) for k, v in (
    ('bulgular', 'x'), ('kapsam', {}), ('tarih', '2026-09-29'), ('sema', 'baska/9'))
] + [(f'kok.{k}_yok', lambda d, k=k: d.pop(k)) for k in ('sema', 'bulgular', 'kapsam')
] + [(f'kapsam[0].{k}={v!r}', lambda d, k=k, v=v: d['kapsam'][0].update({k: v})) for k, v in (
    ('durum', 'temiz'), ('yuzey', 'Z'), ('not_', 'x'))
] + [(f'kapsam[0].{k}_yok', lambda d, k=k: d['kapsam'][0].pop(k)) for k in ('yuzey', 'durum')]
KOK_BOZUKLARI = (('kok_dizi', []), ('kok_dizge', 'x'), ('kok_null', None))  # tum belge nesne degil
TEMIZ_VARYANTLAR = [  # (ad, temiz ornegi degistiren GECERLI degisiklik) — hicbiri yakmamali (aksi sikilasma/yanlis-pozitif)
    ('bulgu_yok', lambda d: d.update(bulgular=[])),
    ('needs_validation_etkilenensiz', lambda d: d['bulgular'][1].pop('etkilenen')),
    ('needs_validation+dogrulayan', lambda d: d['bulgular'][1].update(dogrulayan='alt-ajan')),
    ('rejected_dogrulayansiz', lambda d: d['bulgular'][2].pop('dogrulayan')),
    ('rejected+etkilenen', lambda d: d['bulgular'][2].update(etkilenen='api/orders.js:42')),
    ('kapsam_olculdu+sebep', lambda d: d['kapsam'][0].update(sebep='tam tarandi')),
    ('tum_yuzeyler', lambda d: d.update(kapsam=[{'yuzey': y, 'durum': 'olculdu'} for y in YUZEYLER])),
] + [(f'siddet_{s}', lambda d, s=s: d['bulgular'][0].update(siddet=s)) for s in ('KRITIK', 'YUKSEK', 'ORTA', 'DUSUK', 'BILGI')
] + [(f'serit_{y}', lambda d, y=y: d['bulgular'][0].update(serit=y)) for y in YUZEYLER
] + [(f'dogrulayan_{v}', lambda d, v=v: d['bulgular'][0].update(dogrulayan=v)) for v in ('alt-ajan', 'ayri-tur')]


def bozuk_vakalar():
    """YAPI_BOZUKLARI + BEKLENEN tablosundan uretilen (zorunlu eksik / yasak fazla) + metin alanlarinda tip/bosluk ihlalleri."""
    v = list(YAPI_BOZUKLARI)
    for hukum, (zorunlu, yasak) in BEKLENEN.items():
        i = IDX[hukum]
        v += [(f'{hukum}-{f}_yok', lambda d, i=i, f=f: d['bulgular'][i].pop(f)) for f in zorunlu]
        v += [(f'{hukum}+{f}', lambda d, i=i, f=f: d['bulgular'][i].update({f: GECERLI.get(f, 'x')})) for f in yasak]
    for i, kayit in enumerate(temiz_ornek()['bulgular']):
        for f in (f for f in kayit if f in METIN_ALANLARI):
            v.append((f'{f}[{i}]=sayi', lambda d, i=i, f=f: d['bulgular'][i].update({f: 123})))
            v.append((f'{f}[{i}]=bosluk', lambda d, i=i, f=f: d['bulgular'][i].update({f: '  '})))
    return v


def _bozan_yakiyor(vakalar, sema, yakmali):
    """Degisiklik uygulanmis temiz ornekte kontrol() sonucu beklenene uymayan vakalarin adlari."""
    yanlis = []
    for ad, degistir in vakalar:
        d = temiz_ornek()
        degistir(d)
        if bool(kontrol(d, sema)) != yakmali:
            yanlis.append(ad)
    return yanlis


def _ornek_hatasi(md, sema):
    """md metnindeki ilk ```json blogu yoksa ya da semaya uymuyorsa True."""
    m = re.search(r'```json\n(.*?)\n```', md, re.S)
    try:
        return not m or bool(kontrol(yukle(m.group(1)), sema))
    except ValueError:
        return True


def _belge_ornekleri(sema):
    """Skill belgelerindeki (TR+EN) JSON ornegi semaya uymali; sema degisirse belge sessizce eskimesin."""
    yanlis = []
    for yol in BELGELER:
        try:
            with open(yol, encoding='utf-8') as f:
                if _ornek_hatasi(f.read(), sema):
                    yanlis.append(os.path.basename(os.path.dirname(os.path.dirname(yol))))
        except OSError:
            yanlis.append('okunamadi')
    return yanlis


def _sessiz(fonk, *arg):
    with contextlib.redirect_stdout(io.StringIO()):
        return fonk(*arg)


def _atar(fonk, *arg):
    try:
        fonk(*arg)
    except ValueError:
        return True
    return False


def _ek(liste):
    return f' — {liste[:4]}' if liste else ''


def _dogrulayici_sorunlari(sema):
    """Dogrulayicinin kendi sozlesmeleri: tanimadigi anahtari yutmaz, $ref/additionalProperties sinirlari, belge-ornegi kontrolu kor degil."""
    sorun = []
    if not dogrula({}, {'oneOf': []}) or not dogrula({}, {'if': {'minProperties': 1}, 'then': {}}):
        sorun.append('taninmayan_sema_anahtari_yutuldu')
    if dogrula(1, True) or not dogrula(1, False) or not _atar(dogrula, {}, {'$ref': 'http://x'}) or not _atar(dogrula, {}, {'additionalProperties': True}):
        sorun.append('dogrulayici_temel')
    if not _ornek_hatasi('```json\n{}\n```', sema) or not _ornek_hatasi('yok', sema):
        sorun.append('belge_ornek_kontrolu_kor')
    return sorun


def _kapi_yolu_sorunlari(sema):
    """kapi()/main() sozlesmesi + kapilar zincirine baglanti: dosya yok → ATLANDI; acik yol yok → FAIL; bozuk/derin/yinelenen-anahtar → FAIL; BOM'lu temiz → PASS."""
    with tempfile.TemporaryDirectory() as t:
        def yaz(ad, metin):
            with open(os.path.join(t, ad), 'w', encoding='utf-8') as f:
                f.write(metin)
            return os.path.join(t, ad)
        temiz, bozuk = json.dumps(temiz_ornek()), temiz_ornek()
        bozuk['bulgular'][1]['siddet'] = 'ORTA'
        vakalar = [
            ('dosya_yok_ATLANDI', kapi(t)[0], 'ATLANDI'),
            ('acik_yol_yok_FAIL', kapi(t, os.path.join(t, 'yok.json'))[0], 'FAIL'),
            ('temiz_PASS', kapi(t, yaz('a.json', temiz))[0], 'PASS'),
            ('bom_PASS', kapi(t, yaz('f.json', '\ufeff' + temiz))[0], 'PASS'),
            ('bozuk_FAIL', kapi(t, yaz('b.json', json.dumps(bozuk)))[0], 'FAIL'),
            ('json_bozuk_FAIL', kapi(t, yaz('c.json', '{"sema": '))[0], 'FAIL'),
            ('cift_anahtar_FAIL', kapi(t, yaz('d.json', temiz.replace('"sema": "gedik-bulgular/1"', '"sema": "gedik-bulgular/1", "sema": "gedik-bulgular/1"', 1)))[0], 'FAIL'),
            ('derin_yapi_FAIL', kapi(t, yaz('e.json', '[' * 5000 + ']' * 5000))[0], 'FAIL'),
            ('main_acik_yol_yok_1', _sessiz(main, ['--dosya', os.path.join(t, 'yok.json')]), 1),
            ('main_temiz_0', _sessiz(main, ['--dosya', os.path.join(t, 'a.json')]), 0),
        ]
        yaz(DOSYA_ADI, json.dumps(bozuk))
        try:
            import kapilar  # gec ice aktarma: kapilar.py bu modulu ice aktarir, dongu olmaz
            zincir = [(ad, sonuc) for ad, sonuc, _ in kapilar.kapilari_kos(t, {})]
        except ImportError:
            zincir = []
    return [ad for ad, sonuc, beklenen in vakalar if sonuc != beklenen] + ([] if ('bulgu şeması', 'FAIL') in zincir else ['zincir_bagli_degil'])


def oz_test_vakalari():
    """kapilar.py altin kumesi icin: [(ad, yakti_mi, beklenen, etiket)]; hepsinde yakti == beklenen olmali."""
    try:
        sema = sema_yukle()
        kacan = _bozan_yakiyor(bozuk_vakalar(), sema, True) + [ad for ad, kok in KOK_BOZUKLARI if not kontrol(kok, sema)]
        yanlis_pozitif = _bozan_yakiyor(TEMIZ_VARYANTLAR + [('temiz_ornek', lambda d: None)], sema, False) + _belge_ornekleri(sema)
        kapi_sorunu = _kapi_yolu_sorunlari(sema) + _dogrulayici_sorunlari(sema)
    except (OSError, ValueError, KeyError) as e:
        return [('bulgu_sema_okunamadi', True, False, f'G şema/oz-test çalıştırılamadı: {type(e).__name__}')]
    return [('bozuk_bulgu', not kacan, True, 'G bulgu şeması: aykırı kayıt KIRMIZI' + _ek(kacan)),
            ('temiz_bulgu', bool(yanlis_pozitif), False, 'G yanlış-pozitif / belge örneği' + _ek(yanlis_pozitif)),
            ('bulgu_kapi_yolu', not kapi_sorunu, True, 'G kapı yolu: dosya→hüküm, çıkış kodu' + _ek(kapi_sorunu))]


def oz_test():
    vakalar = oz_test_vakalari()
    for ad, yakti, beklenen, etiket in vakalar:
        print(f"  {'✓' if yakti == beklenen else '✗'} {ad:<16} {etiket}")
    return all(yakti == beklenen for _, yakti, beklenen, _ in vakalar)


def main(argv):
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(prog='bulgu_kapisi.py', allow_abbrev=False, description='gedik-bulgular.json şema kapısı')
    ap.add_argument('--dosya', help='doğrulanacak dosya (yoksa FAIL); verilmezse ./gedik-bulgular.json, yoksa ATLANDI')
    ap.add_argument('--pozitif-kontrol', action='store_true', help='kör kapı öz-testi')
    a = ap.parse_args(argv)  # tanınmayan bayrak / değersiz --dosya: çıkış 2
    if a.pozitif_kontrol:
        gecti = oz_test()
        print('KAPI GÖRÜYOR' if gecti else 'KAPI KÖR — ölçüm reddedilir')
        return 0 if gecti else 1
    sonuc, kanit = kapi(os.getcwd(), a.dosya)
    print(f'{sonuc} {kanit}')
    return 1 if sonuc == 'FAIL' else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
