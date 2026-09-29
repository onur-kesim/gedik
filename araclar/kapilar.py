#!/usr/bin/env python3
"""kapilar.py — proje.toml'u okur, kapıları sırayla koşar. Önce KENDİNİ kanıtlar (altın küme).

Kullanım (depo kökünde):
  python araclar/kapilar.py                  öz-test + tüm kapılar; çıkış 0 = FAIL yok
  python araclar/kapilar.py --pozitif-kontrol yalnız öz-test (CI'daki kor-kapi işi)
  python araclar/kapilar.py --yigin          'yigin=<ad>' basar (CI koşullu kurulum adımları)
  python araclar/kapilar.py --oz-test-atla   öz-testi atlar; sonuç GÜVENİLMEZ, "temiz" yazılmaz
Yalnız standart kütüphane. Python >= 3.11 (tomllib). Kör kapı ilkesi: öz-test geçmezse ölçüm yapılmaz.
"""
import ast
import fnmatch
import os
import re
import subprocess
import sys
import time

KOD_UZANTI = {'.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.dart', '.kt', '.kts', '.java',
              '.go', '.rs', '.swift', '.cs', '.rb', '.php', '.c', '.cc', '.cpp', '.h', '.hpp',
              '.vue', '.svelte'}
SIR_DESENLERI = [
    ('AWS erişim anahtarı', re.compile(r'\bAKIA[0-9A-Z]{16}\b')),
    ('özel anahtar bloğu', re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----')),
    ('GitHub token', re.compile(r'\bgh[pousr]_[A-Za-z0-9]{36,}\b')),
    ('sk- türü API anahtarı', re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b')),
    ('Slack token', re.compile(r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b')),
    ('Google API anahtarı', re.compile(r'\bAIza[0-9A-Za-z_-]{35}\b')),
    ('genel sır ataması', re.compile(r'(?i)\b(api[_-]?key|secret|passwd|password|token)\b\s*[:=]\s*[\'"][^\'"\s]{8,}[\'"]')),
]
SIR_HARIC = ['.env.example', 'araclar/altin_kume/*']
ATLA_KLASOR = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'build', 'dist', 'out', '.dart_tool', '.gradle'}


# ---------- yardımcılar ----------
def rel(yol, kok):
    return os.path.relpath(yol, kok).replace(os.sep, '/')


def eslesir(rel_yol, desenler):
    return any(fnmatch.fnmatch(rel_yol, d) for d in desenler)


def dosyalar(kok):
    """İzlenen dosyalar: git varsa git ls-files, yoksa yürüyüş (atlanan klasörler hariç)."""
    try:
        cikti = subprocess.run(['git', 'ls-files', '-z'], cwd=kok, capture_output=True, text=True, check=True).stdout
        return [d for d in cikti.split('\0') if d and os.path.isfile(os.path.join(kok, d))]
    except (subprocess.CalledProcessError, FileNotFoundError):
        sonuc = []
        for dizin, altlar, adlar in os.walk(kok):
            altlar[:] = [a for a in altlar if a not in ATLA_KLASOR]
            sonuc.extend(rel(os.path.join(dizin, a), kok) for a in adlar)
        return sonuc


def metin_oku(yol):
    """Metin dosyasını okur; ikili dosya (ilk 8 KB'de NUL) boş sayılır."""
    try:
        with open(yol, 'rb') as f:
            ham = f.read()
        if b'\0' in ham[:8192]:
            return ''
        return ham.decode('utf-8', errors='replace')
    except OSError:
        return ''


def toml_oku(kok):
    try:
        import tomllib
    except ImportError:
        return None, 'python >= 3.11 gerekli (tomllib yok)'
    yol = os.path.join(kok, 'proje.toml')
    if not os.path.exists(yol):
        return None, 'proje.toml yok'
    with open(yol, 'rb') as f:
        return tomllib.load(f), None


# ---------- kapı fonksiyonları (saf: girdi → bulgu listesi) ----------
def sir_tara(metin):
    """Metindeki sır desenlerini döndürür: [(ad, satır_no)]."""
    bulgular = []
    for no, satir in enumerate(metin.splitlines(), 1):
        for ad, desen in SIR_DESENLERI:
            if desen.search(satir):
                bulgular.append((ad, no))
    return bulgular


def satir_sayisi(metin):
    return len(metin.splitlines())


def _dugum_agirligi(d):
    if isinstance(d, (ast.If, ast.For, ast.While, ast.AsyncFor, ast.ExceptHandler, ast.IfExp, ast.Assert)):
        return 1
    if isinstance(d, ast.BoolOp):
        return len(d.values) - 1
    if isinstance(d, ast.comprehension):
        return 1 + len(d.ifs)
    if isinstance(d, ast.match_case):
        return 1
    return 0


def python_karmasiklik(metin):
    """En karmaşık fonksiyonu döndürür: (ad, karmaşıklık). Çözümlenemezse (None, -1)."""
    try:
        agac = ast.parse(metin)
    except SyntaxError:
        return None, -1
    en = ('', 0)
    for f in ast.walk(agac):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            k = 1 + sum(_dugum_agirligi(d) for d in ast.walk(f))
            if k > en[1]:
                en = (f.name, k)
    return en


def belge_kod_orani(belge_satir, kod_satir):
    if kod_satir == 0:
        return None
    return belge_satir / kod_satir


def nabiz_gun(log_metni, desenler, simdi):
    """git log --pretty=format:%ct --name-only çıktısından son ürün commit'inin yaşını (gün) döndürür."""
    zaman = None
    for satir in log_metni.splitlines():
        satir = satir.strip()
        if not satir:
            continue
        if satir.isdigit():
            zaman = int(satir)
        elif zaman is not None and eslesir(satir, desenler):
            return (simdi - zaman) / 86400
    return None


# ---------- altın küme: araç önce kendini kanıtlar ----------
def altin_kume():
    """Bilerek bozuk ve temiz girdilerle her kapının ısırdığını ölçer. Dönüş: (gecti, satırlar)."""
    vakalar = []  # sır örnekleri join ile parçalı: derleyici sabitleri birleştirmesin, tarayıcı kendini ısırmasın
    uzun = '\n'.join(['x = 1'] * 401)
    kisa = 'x = 1\ny = 2\n'
    karmasik = 'def f(a):\n' + ''.join(f'    if a == {i}:\n        return {i}\n' for i in range(16))
    vakalar.append(('bozuk_sir', bool(sir_tara('AWS_KEY=' + ''.join(['AK', 'IA', 'IOSFODNN7EXAMPLE']) + '\n')), True, 'A1 sır'))
    vakalar.append(('bozuk_ozel_anahtar', bool(sir_tara(''.join(['-----BEGIN RSA ', 'PRIVATE', ' KEY-----']) + '\n')), True, 'A1 sır'))
    vakalar.append(('temiz_sir', bool(sir_tara('Parola politikası: en az 12 karakter.\n')), False, 'A1 yanlış-pozitif'))
    vakalar.append(('bozuk_uzun', satir_sayisi(uzun) > 400, True, 'B4 satır'))
    vakalar.append(('temiz_kisa', satir_sayisi(kisa) > 400, False, 'B4 yanlış-pozitif'))
    vakalar.append(('bozuk_karmasik', python_karmasiklik(karmasik)[1] > 15, True, 'B4 karmaşıklık'))
    vakalar.append(('temiz_basit', python_karmasiklik(kisa)[1] > 15, False, 'B4 yanlış-pozitif'))
    vakalar.append(('bozuk_oran', (belge_kod_orani(300, 100) or 0) > 1.0, True, 'B2 belge/kod'))
    vakalar.append(('temiz_oran', (belge_kod_orani(50, 100) or 0) > 1.0, False, 'B2 yanlış-pozitif'))
    simdi = 1_800_000_000
    log = f'{simdi - 9 * 86400}\nsrc/a.py\n\n{simdi - 20 * 86400}\nREADME.md\n'
    vakalar.append(('bozuk_nabiz', (nabiz_gun(log, ['src/*'], simdi) or 0) > 7, True, 'D nabız'))
    log2 = f'{simdi - 1 * 86400}\nsrc/a.py\n'
    vakalar.append(('temiz_nabiz', (nabiz_gun(log2, ['src/*'], simdi) or 0) > 7, False, 'D yanlış-pozitif'))
    vakalar.append(('bozuk_yapim_nabiz', nabiz_hukmu('yapim', 30, 7) == 'FAIL', True, 'D nabız YAPIM 30 gün'))
    vakalar.append(('kesif_nabiz_yakmaz', nabiz_hukmu('kesif', 30, 7) == 'FAIL', False, 'D KEŞİF yanlış-pozitif'))
    vakalar.append(('kesif_atlandi', nabiz_hukmu('kesif', 30, 7) == 'ATLANDI', True, 'D KEŞİF: ATLANDI, PASS değil'))
    satirlar, gecti = [], True
    for ad, sonuc, beklenen, etiket in vakalar:
        ok = sonuc == beklenen
        gecti &= ok
        satirlar.append(f"  {'✓' if ok else '✗'} {ad:<20} {etiket}{'' if ok else ' — KÖR: beklenen bulgu ÇIKMADI' if beklenen else ' — YANLIŞ-POZİTİF'}")
    return gecti, satirlar


# ---------- kapıların projeye uygulanması ----------
def kapi_komut(ad, komut, kok):
    if not komut:
        return (ad, 'ATLANDI', 'proje.toml’da boş')
    try:
        p = subprocess.run(komut, shell=True, cwd=kok, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        return (ad, 'FAIL', '30 dk zaman aşımı')
    son = [s for s in (p.stdout + p.stderr).splitlines() if s.strip() and set(s.strip()) != {'═'}][-1:] or ['']
    return (ad, 'PASS' if p.returncode == 0 else 'FAIL', f'çıkış {p.returncode} · {son[0][:80]}')


def kapi_kod_sagligi(kok, izlenen, desenler, cfg):
    tavan_s = cfg.get('dosya_satir_tavan', 400)
    tavan_k = cfg.get('karmasiklik_tavan', 15)
    taban = cfg.get('taban_dosya_ihlal', 0)
    ihlal, olculemedi = [], 0
    for d in izlenen:
        if os.path.splitext(d)[1] not in KOD_UZANTI or not eslesir(d, desenler):
            continue
        metin = metin_oku(os.path.join(kok, d))
        if satir_sayisi(metin) > tavan_s:
            ihlal.append(f'{d} {satir_sayisi(metin)} satır')
        if d.endswith('.py'):
            ad, k = python_karmasiklik(metin)
            if k > tavan_k:
                ihlal.append(f'{d}:{ad} karmaşıklık {k}')
        else:
            olculemedi += 1
    kanit = f'{len(ihlal)} ihlal (taban {taban})' + (f' · {olculemedi} dosyada karmaşıklık ÖLÇÜLEMEDİ (yalnız Python ölçülür)' if olculemedi else '')
    if ihlal:
        kanit += ' · ' + '; '.join(ihlal[:5])
    return ('kod sağlığı', 'FAIL' if len(ihlal) > taban else 'PASS', kanit)


def kapi_sir(kok, izlenen):
    bulgular = []
    for d in izlenen:
        if eslesir(d, SIR_HARIC):
            continue
        for ad, no in sir_tara(metin_oku(os.path.join(kok, d))):
            bulgular.append(f'{d}:{no} {ad}')
    return ('gizli anahtar', 'FAIL' if bulgular else 'PASS', '; '.join(bulgular[:5]) or f'{len(izlenen)} dosya tarandı, sır yok')


def kapi_oran(kok, izlenen, urun, cfg):
    tavan = cfg.get('belge_kod_oran_tavan', 1.0)
    if not tavan:
        return ('belge/kod oranı', 'ATLANDI', 'tavan 0: bu projenin ürünü belge')
    belge = sum(satir_sayisi(metin_oku(os.path.join(kok, d))) for d in izlenen if eslesir(d, urun.get('belge_desen', ['*.md'])))
    kod = sum(satir_sayisi(metin_oku(os.path.join(kok, d))) for d in izlenen
              if os.path.splitext(d)[1] in KOD_UZANTI and eslesir(d, urun.get('desen', [])))
    oran = belge_kod_orani(belge, kod)
    if oran is None:
        return ('belge/kod oranı', 'ÖLÇÜLEMEDİ', 'kod satırı 0')
    return ('belge/kod oranı', 'FAIL' if oran > tavan else 'PASS', f'{belge} belge / {kod} kod = {oran:.2f} (tavan {tavan})')


def nabiz_hukmu(asama, gun, tavan):
    """KEŞİF'te nabız ölçülmez (fikir aşaması süresizdir; K1-K2-K8 işlemez); YAPIM'da tavanı aşan gün FAIL."""
    if asama == 'kesif':
        return 'ATLANDI'
    return 'FAIL' if gun > tavan else 'PASS'


def kapi_nabiz(kok, urun, cfg, asama='yapim'):
    tavan = cfg.get('nabiz_gun_tavan', 7)
    if asama == 'kesif':
        return ('ürün nabzı', 'ATLANDI', 'KEŞİF aşaması: süre tavanı yok (proje.toml [proje] asama)')
    try:
        log = subprocess.run(['git', 'log', '--pretty=format:%ct', '--name-only'], cwd=kok,
                             capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ('ürün nabzı', 'ÖLÇÜLEMEDİ', 'git yok ya da commit yok')
    gun = nabiz_gun(log, urun.get('desen', []), time.time())
    if gun is None:
        return ('ürün nabzı', 'ÖLÇÜLEMEDİ', 'ürün deseniyle eşleşen commit yok')
    return ('ürün nabzı', nabiz_hukmu(asama, gun, tavan), f'son ürün commit’i {gun:.1f} gün önce (tavan {tavan})')


def kapi_kanit(izlenen, urun):
    kanit = [d for d in izlenen if d.startswith('kanit/')]
    urun_sayisi = sum(1 for d in izlenen if eslesir(d, urun.get('desen', [])))
    return ('kanıt < ürün', 'FAIL' if kanit and len(kanit) >= urun_sayisi else 'PASS', f'{len(kanit)} kanıt / {urun_sayisi} ürün dosyası')


def kapilari_kos(kok, cfg):
    izlenen = dosyalar(kok)
    urun = cfg.get('urun', {})
    k = cfg.get('kapilar', {})
    komutlar = cfg.get('komutlar', {})
    asama = cfg.get('proje', {}).get('asama', 'yapim')
    sonuclar = [('aşama', 'PASS' if asama in ('kesif', 'yapim') else 'FAIL', f'proje.toml [proje] asama = {asama!r} (kesif | yapim)')]
    sonuclar += [kapi_komut(ad, komutlar.get(ad, ''), kok) for ad in ('kur', 'test', 'lint', 'build')]
    sonuclar.append(kapi_kod_sagligi(kok, izlenen, urun.get('desen', []), k))
    sonuclar.append(kapi_sir(kok, izlenen))
    sonuclar.append(kapi_oran(kok, izlenen, urun, k))
    sonuclar.append(kapi_nabiz(kok, urun, k, asama))
    sonuclar.append(kapi_kanit(izlenen, urun))
    return sonuclar


# ---------- rapor ----------
def yazdir_rapor(sonuclar, guvenilir):
    print('┌─ KAPILAR' + ('' if guvenilir else '  (öz-test atlandı → sonuç GÜVENİLMEZ)'))
    for ad, sonuc, kanit in sonuclar:
        isaret = {'PASS': '✓', 'FAIL': '✗', 'ATLANDI': '–', 'ÖLÇÜLEMEDİ': '?'}[sonuc]
        print(f'│  {isaret}  {ad:<16} {sonuc:<11} {kanit}')
    say = {s: sum(1 for _, x, _ in sonuclar if x == s) for s in ('PASS', 'FAIL', 'ATLANDI', 'ÖLÇÜLEMEDİ')}
    print(f"└─ ÖZET: {say['PASS']} PASS · {say['FAIL']} FAIL · {say['ATLANDI']} ATLANDI · {say['ÖLÇÜLEMEDİ']} ÖLÇÜLEMEDİ")
    print('   Bu betiğin 0 dönmesi teslime hazır olduğunu KANITLAMAZ; yalnız ölçülebilen kusur sınıflarının bulunmadığını gösterir.')
    print('   ÖLÇÜLEMEDİ temiz değildir; teslimde NE ÖLÇÜLEMEDİ bölümüne yazılır.')


def main(argv):
    for akis in (sys.stdout, sys.stderr):  # Windows konsolu (cp1254) '✓' basamaz; başka bir kurulumda ölçüldü, 26 Eyl
        try:
            akis.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass
    kok = os.getcwd()
    if '--yigin' in argv:
        cfg, hata = toml_oku(kok)
        print(f"yigin={(cfg or {}).get('yigin', {}).get('ad', 'yok')}")
        return 0 if not hata else 2
    print('═' * 72 + '\nALTIN KÜME ÖZ-TESTİ — araç önce kendini kanıtlar')
    gecti, satirlar = altin_kume()
    print('\n'.join(satirlar))
    if not gecti and '--oz-test-atla' not in argv:
        print('✗ ÖZ-TEST KALDI — denetim REDDEDİLDİ. Kör bir kapıyla ölçüm yapılmaz.')
        return 2
    print(('✓ Öz-test geçti' if gecti else '! Öz-test kaldı, atlandı') + '\n' + '═' * 72)
    if '--pozitif-kontrol' in argv:
        return 0 if gecti else 2
    cfg, hata = toml_oku(kok)
    if hata:
        print(f'ÖLÇÜLEMEDİ — {hata}')
        return 2
    sonuclar = kapilari_kos(kok, cfg)
    yazdir_rapor(sonuclar, gecti)
    return 1 if any(s == 'FAIL' for _, s, _ in sonuclar) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
