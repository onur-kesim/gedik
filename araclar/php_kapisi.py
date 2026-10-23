#!/usr/bin/env python3
"""php_kapisi.py — gedik v2.7.0: PHP gorunurlugu kapisi (rapor denetimi + CLI). Yalniz standart kutuphane; hedefe ve rapora YAZMAZ.

  python araclar/php_kapisi.py --hedef DIZIN                 hedefin PHP olcumunu basar (imza, surum+kaynak, EOL, composer)
  python araclar/php_kapisi.py --hedef DIZIN --rapor RAPOR   gedik raporunu o olcume karsi denetler (cikis 1 = kusur)
  python araclar/php_kapisi.py --pozitif-kontrol             kor kapi oz-testi (D1/D2): bozuk fixture/rapor KIRMIZI, temizler YESIL
Cikis: 0 = PASS/uygulanmaz · 1 = kusur ya da oz-test KOR · 2 = kullanim hatasi.

Olcum: php_olc.py · oz-test: php_oz_test.py · kural kaynagi: skills/gedik*/references/kod-inceleme-guvenlik.md §2.1.
Bu bir ANAHTAR-SOZCUK TABANIDIR: rapor dili serbest oldugundan varligi/yoklugu ve bitisik satirlari (pencere) denetler, ANLAMI
denetlemez; gecmesi raporun dogru oldugunu KANITLAMAZ (bagimsiz incelemeler her turda yeni atlatma/yanlis-pozitif buldu — bkz. KRITER).
Sabit CVE tablosu YOKTUR (bayatlar); yalniz EOL dali kurali sabittir.
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
OLC = r'ÖLÇÜLEMEDİ|ÖLÇÜLMEDİ|NOT MEASURED|NOT RUN|UNMEASURED|not installed|cannot run|could not|did not run|not run|koşmaz|koşamadı|kurulu değil|çalıştırılamadı|ulaşılamadı'
PATCH_BELIRSIZ = (r'yama düzeyi|patch[- ]level|floating|yüzen|exact patch|latest patch|düzey\w*[^\n]{0,25}(ÖLÇÜL|NOT MEASURED)|level[^\n]{0,25}NOT MEASURED|'
                  r'(actual|real|gerçek)[^\n.]{0,25}(version|sürüm)[^\n.]{0,40}(NOT MEASURED|ÖLÇÜL)')
KARSILASTIRMA = (r'karşılaştırma|comparison|compar|latest (patch|release)|current(ly)? patched|patched (version|release)|güncel yama|yamalı sürüm|'
                 r'CVE-\d|trivy|grype|osv|scanner|tarayıcı|advisor')
EOL_KW = (r'\bEOL\b|end[- ]of[- ]life|(no|without)\s+(official\s+)?(security\s+)?(patch|fix|update)\w*|unpatched|'
          r'güvenlik (yaması|güncellemesi) (yok|almıyor|verilmiyor)|resmî (güvenlik )?yama(sı)? yok|yama almıyor|'
          r'(security|güvenlik) (support|desteği) (has |had )?(ended|bitti|sona erdi|bitiyor|ends)')
EOL_VETO = (r"not (yet )?(eol|end[- ]of[- ]life)|no eol|isn'?t (eol|end)|eol:?\s*(?:hayır|false|no\b(?!\s+\w))|eol (değil|yok)|"
            r"(still|actively|currently)\s+(receives?|supported|maintained)|supported until|fully supported|destekleniyor|destek sürüyor|aktif (olarak )?(destek|güncelle)")
TEMIZ = (r'\b(?:temiz\w*|tertemiz|sorunsuz\w*|sorun (?:yok|görülmedi|bulunmadı)|güvenli(?!k)\w*|güncel ve yamalı|clean|safe|secure|'
         r'is (?:fully )?patched|fully patched|no (?:known )?(?:issues?|vulnerabilit\w+)|nothing to worry|up[- ]to[- ]date|looks (?:good|fine)|fine)\b')
TEMIZ_KARAR = (r'\b(?:risk(?:i)? yok|no (?:security )?risk|no action(?: is)?(?: needed| required)?|(?:güncelleme|yükseltme|eylem|aksiyon|işlem) (?:gerekmiyor|gerekmez|gerekli değil)|'
               r'(?:no|not) (?:upgrade|update)s? (?:is |are )?(?:needed|required|necessary)|(?:upgrade|update)s? (?:is |are )?not (?:needed|required|necessary)|no need to (?:upgrade|update)|'
               r'gerek yok|all (?:good|clear)|nothing to (?:do|fix|worry))\b')  # "risk yok / no action needed" kararı (çalışma zamanı satırı olmasa da PHP satırında iddiadır)
YUKSELT = r'yükselt\w*|upgrad\w*|migrat\w*|geçin\b|geçiş|güncelleyin|taşıyın|update to|move to|switch to|bump|öner\w*|recommend\w*'  # yükseltme ÖNERİSİ bağlamı
YUKSELT_YOK = r"gerek(?:miyor|siz| yok)|needn'?t|no need|not needed|no action|no (?:upgrade|update)|unnecessary|değil|not required"
HEDEF_SURUM = (r'(?:güvenli|secure|safe|patched|yamalı)\W+(?:(?:desteklenen|supported|güncel|maintained)\W+)*(?:bir\W+|a\W+|an\W+)?'
               r'(?:dal\w*|sürüm\w*|versiyon\w*|release\w*|version\w*|branch\w*)')  # "güvenli bir dala yükseltin": hedef tarifi, mevcut sürüm iddiası değil
TEMIZ_ONCE = r"(?:not|never|n't|asla|without|unverified|cannot)\W+(?:\w+\W+){0,2}$"
TEMIZ_SONRA = r'\W*(?:değil|denmez|denmiyor|denemez|yazılmaz|yazılmıyor|demiyorum|diyemem|yazmıyorum|söylenemez)\b'
EOL_CUMLE = (r'güvenlik (?:yaması|desteği|güncellemesi)|security (?:patch|fix|support|update)s?|'  # EOL cümleleri + K4 "temiz kopya" jargonu muaf
             r'\bclean (?:copy|version|tree|baseline|run|build|checkout|mutant)\b|temiz (?:kopya\w*|sürüm\w*|ağaç\w*)|(?:working tree|git status) clean')
LOCK_YOK = r'(composer\.lock\s*(yok|is\s+missing|missing|absent|not\s+(found|present|committed)|does not exist))|no composer\.lock'
SAYI = (r'\b\d+\b\s*(?:advisor|vulnerab|zafiyet|açık|issues?|critical|high|kritik|yüksek|finding|bulgu|found)|(?:critical|high|kritik|yüksek)\W{0,3}\d+|'
        r'no (?:security )?(?:vulnerability )?advisories|advisories? found')
ECO = r'\bphp\b|laravel|symfony|wordpress|composer|artisan|wp-config|wp-content|\.php\b|\.htaccess'
POZ = r'\b(?:yes|evet|var|present|found|signature|imza)\b'
NEG = (r'\b(?:no|none|not|hayır|yok|unknown|bilinmiyor)\b[^|.\n]{0,25}\b(?:php|server code|sunucu kodu)\b|\bphp\b[^|.\n]{0,25}\b(?:not used|absent|yok|none)\b|'
       r'(?:server code|sunucu kodu)[^|\n]{0,15}\b(?:no|none|unknown|hayır|yok)\b')


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


def vr(v):
    """Surum sinirli eslesme: 8.3.3 yazisi 8.3.30'a ya da 18.3.3'e uymaz."""
    return r'(?<![\d.])' + re.escape(v) + r'(?!\.?\d)'


def satir_bul(satirlar, *kaliplar, yok=None):
    return next((s for s in satirlar if all(re.search(k, s, re.I) for k in kaliplar) and not (yok and re.search(yok, s, re.I))), None)


def pencere(satirlar, ana, *diger, gen=3, yok=None):
    """`ana` kaliplarini iceren bir satir VAR ve +-gen satirlik penceresi `diger` kaliplarin hepsini iceriyor mu (LLM raporu olguyu
    bitisik satirlara yayar). `yok` verilmisse eslesen ana satirlar elenir. TABANDIR: anlam denetlemez."""
    for i, satir in enumerate(satirlar):
        blok = ' '.join(satirlar[max(0, i - gen):i + gen + 1])
        if all(re.search(k, satir, re.I) for k in ana) and all(re.search(k, blok, re.I) for k in diger) and not (yok and re.search(yok, satir, re.I)):
            return True
    return False


# ---------- kusur kontrolleri ----------
def kusur_t2(satirlar):
    t2 = [s for s in satirlar if re.search(r'\bT2\b|server code|sunucu kodu', s, re.I)]
    iyi = any(re.search(ECO, s, re.I) or re.search(POZ, s, re.I) for s in t2)
    return [] if iyi and not any(re.search(NEG, s, re.I) for s in t2) else ['T2_PHP_YOK']


def temiz_iddiasi(satir):
    """'temiz/guvenli/clean...' iddiasi; yakin olumsuzlama (once: not/never/asla ≤2 sozcuk · sonra: degil/denmez) muaf."""
    metin = re.sub(re.escape(SABIT_TR) + '|' + re.escape(SABIT_EN) + '|' + EOL_CUMLE, ' ', satir, flags=re.I)
    if re.search(YUKSELT, metin, re.I) and not re.search(YUKSELT_YOK, metin, re.I):
        metin = re.sub(HEDEF_SURUM, ' ', metin, flags=re.I)  # yükseltme önerisinin hedef tarifi muaf; "yükseltmeye gerek yok" ile birlikte muaf DEĞİL
    for m in re.finditer(TEMIZ + '|' + TEMIZ_KARAR, metin, re.I):
        once, sonra = metin[max(0, m.start() - 40):m.start()], metin[m.end():m.end() + 25]
        if not (re.search(TEMIZ_ONCE, once, re.I) or re.match(TEMIZ_SONRA, sonra, re.I)):
            return True
    return False


def kusur_temiz(satirlar):
    """PHP calisma zamani satirinda (ve hemen ardindaki satirda) 'temiz' iddiasi; calisma zamani sozcuksuz PHP satirinda yalniz KARAR iddiasi ("risk yok")."""
    for i, s in enumerate(satirlar):
        if not re.search(r'\bphp\b', s, re.I):
            continue
        if re.search(r'çalışma zamanı|runtime|sürüm|version', s, re.I):
            devam = [x for x in satirlar[i + 1:i + 2] if re.match(r'\s{2,}(?![-*|\d])\S', x)]  # girintili DEVAM satiri (madde isareti yok)
            if any(temiz_iddiasi(x) for x in [s] + devam):
                return ['TEMIZ_DENMIS']
        elif re.search(TEMIZ_KARAR, s, re.I) and not re.search(r'composer|audit|advisor|paket|package', s, re.I) and temiz_iddiasi(s):
            return ['TEMIZ_DENMIS']
    return []


def kusur_surum(o, satirlar):
    ad = os.path.basename(o['kaynak'].rsplit(':', 1)[0])
    if not pencere(satirlar, [vr(o['surum'])], re.escape(ad), gen=1):
        return ['SURUM_KAYNAK_YOK']
    kusur = []
    if o['yalniz_ci'] and not pencere(satirlar, [vr(o['surum'])], r'\bCI\b(?![.\w])|matrix|matris|workflow\b', gen=1):
        kusur.append('CI_KAYNAGI_BELIRTILMEMIS')
    if not o['yalniz_ci'] and o['eol'] != 'yok_yama' and not satir_bul(satirlar, KARSILASTIRMA):  # EOL dalinda yamali surum yoktur
        kusur.append('YAMALI_SURUM_KARSILASTIRMASI_YOK')  # tarayici sayisi/CVE ya da "karsilastirma ÖLÇÜLEMEDİ" satiri sart
    if not o['tam'] and not pencere(satirlar, [vr(o['surum']), re.escape(ad)], PATCH_BELIRSIZ):
        kusur.append('YAMA_DUZEYI_BELIRSIZ')
    eksik = [v for v in o['surumler'] if o['celiski'] and not re.search(vr(v), '\n'.join(satirlar))]
    return kusur + (['CELISKI_YAZILMAMIS'] if eksik else [])


def kusur_yuzen(o, satirlar):
    y = o['yuzen']
    ana = [re.escape(os.path.basename(y['kaynak'].rsplit(':', 1)[0])), re.escape(y['etiket'].split('@')[0])]
    return [] if pencere(satirlar, ana, OLC) else ['YUZEN_ETIKET_YAZILMAMIS']


def kusur_surumsuz(o, rapor, satirlar):
    if o['yuzen']:
        return kusur_yuzen(o, satirlar)
    ok = duz(SABIT_TR) in duz(rapor) or duz(SABIT_EN) in duz(rapor)
    kisit = satir_bul(satirlar, r'composer\.json', r'\bphp\b', php_olc.SURUM, r'çalışma zamanı|runtime|kullan\w*|\buses?\b|\busing\b|running|\bruns\b|çalış\w*',
                      yok=r"alt sınır|lower bound|kısıt|constraint|sayılmaz|not count|does not|\bnot\b|n't|değil|NOT MEASURED|ÖLÇÜLEMEDİ|ÖLÇÜLMEDİ")
    return ([] if ok else ['SABIT_SATIR_YOK']) + (['KISIT_SURUM_SAYILMIS'] if kisit else [])


def kusur_eol(o, satirlar):
    v = o['en_eski'] or ''
    dal = v[:-2] if v.endswith('.x') else (v.rsplit('.', 1)[0] if v.count('.') == 2 else v)
    kal = r'\b' + re.escape(dal) + r'\b' if v.endswith('.x') else r'(?<![\d.])' + re.escape(dal) + r'(?:\.\d+)?(?!\d)'
    anahtar = EOL_KW if o['eol'] == 'yok_yama' else r'\bEOL\b|2026-12-31|end[- ]of[- ]life|security support'
    ok = pencere(satirlar, [kal], anahtar, yok=EOL_VETO)
    return [] if ok else ['EOL_BULGUSU_YOK' if o['eol'] == 'yok_yama' else 'EOL_UYARISI_YOK']


def kusur_composer(o, satirlar):
    if not o['composer_lock']:
        ok = satir_bul(satirlar, r'composer', OLC) or satir_bul(satirlar, LOCK_YOK)
        return [] if ok else ['COMPOSER_LOCK_OLCULEMEDI_YOK']
    audit = [i for i, s in enumerate(satirlar) if 'composer audit' in s.lower()]
    ok = any(re.search(SAYI + '|' + OLC, ' '.join(satirlar[i:i + 2]), re.I) for i in audit)  # ayni satir ya da hemen ardindaki satir (onceki satir DEGIL)
    return (['LOCK_VAR_YOK_DENMIS'] if satir_bul(satirlar, LOCK_YOK) else []) + ([] if ok else ['COMPOSER_AUDIT_YOK'])


def gercek_kaynaklar(o):
    """{(dosya, satir, etiket)}; composer.json platform kaynaginda config..platform.php satir araligindaki HER satir gecerlidir."""
    sonuc = set()
    for k in o['kaynaklar']:
        yol, satir = k['kaynak'].rsplit(':', 1)
        bas, son = k['aralik'] or (int(satir), int(satir))
        sonuc |= {(os.path.basename(yol), str(n), k['etiket']) for n in range(bas, son + 1)}
    return sonuc


def kusur_uydurma(o, satirlar):
    """'PHP x.y[.z] ... Dosya:satir' biçiminde, olcumdeki bir kaynakla (dosya+satir+surum) ESLESMEYEN surum+kaynak iddiasi. Kisit satirlari muaf."""
    gercek = gercek_kaynaklar(o)
    dosya = r'Dockerfile|Containerfile|compose|\.php-version|\.htaccess|\.ya?ml|composer\.json|\.conf'
    for s in satirlar:
        if not re.search(r'\bphp\b', s, re.I) or re.search(r'alt sınır|lower bound|require|kısıt|constraint|[\^~>]=?\s*\d', s, re.I):
            continue
        for v, f, n in re.findall(r'(?<![\d.])(\d+\.\d+(?:\.\d+)?)\b[^\n]{0,80}?([\w.\-]+):(\d+)', s):
            if re.search(dosya, f, re.I) and not any(f == g[0] and n == g[1] and g[2].startswith(v) for g in gercek):
                return ['UYDURMA_KAYNAK']
    return []


def rapor_kontrol(o, rapor):
    """Olcume (php_olc.olc() ciktisi) gore rapordaki kusur kodlari; bos = kusur yok. PHP imzasi yoksa kapi uygulanmaz.
    Yalniz ZAYIF imza (yalniz composer.json / *.php: kutuphane olabilir) ve surum kaynagi yoksa surum/sabit-satir denetimi uygulanmaz."""
    if not o['php']:
        return []
    satirlar = rapor.splitlines()
    kusur = kusur_t2(satirlar) + kusur_temiz(satirlar) + kusur_uydurma(o, satirlar)
    if o['surum'] or o['yuzen'] or o['guclu']:
        kusur += kusur_surum(o, satirlar) if o['surum'] else kusur_surumsuz(o, rapor, satirlar)
        kusur += kusur_yuzen(o, satirlar) if (o['surum'] and o['yalniz_ci'] and o['yuzen']) else []
    kusur += kusur_eol(o, satirlar) if o['eol'] in ('yok_yama', 'uyari') else []
    kusur += kusur_composer(o, satirlar) if (o['composer_json'] or o['composer_lock']) else []
    return kusur


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
    ap = argparse.ArgumentParser(prog='php_kapisi.py', allow_abbrev=False, description='gedik PHP görünürlüğü kapısı')
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
    print(json.dumps(o, ensure_ascii=False, indent=1, default=str), bayatlik_uyarisi(o), sep='\n')
    if not a.rapor:
        return 0
    kusur = rapor_kontrol(o, rapor_oku(a.rapor))
    kismi = f" · ÖLÇÜLEMEDİ (kısmi): {len(o['okunamayan'])} dosya okunamadı/kesildi" if o['okunamayan'] else ''
    print(('PASS' if not kusur else 'FAIL ' + ', '.join(kusur)) + ('' if o['php'] else ' (PHP imzası yok → uygulanmaz)') + kismi)
    return 1 if kusur else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
