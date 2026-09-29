#!/usr/bin/env python3
"""ic_ad_kapisi.py — public depoya sizan ic proje adi / oturum no / yerel yol kapisi.

Bu depo public'tir (bilincli sapma, DURUM karar gunlugu). Devir paketi, ic proje
adlari, oturum numaralari ve mutlak yerel yollar izlenen (git ls-files) hicbir
dosyaya girmemeli.

Liste: _calisma/ic_adlar.txt (gitignore'lu, listenin kendisi public'e girmez).
Her satir bir ic ad/desen, duz metin (regex degil), buyuk/kucuk harf duyarsiz.

Kullanim:
  python araclar/ic_ad_kapisi.py                 izlenen tum dosyalari tarar
  python araclar/ic_ad_kapisi.py --pozitif-kontrol  kor kapi oz-testi (D1):
                                                     bellekte bir ic ad eklenince
                                                     kapi KIRMIZI yanmali

Yalniz standart kutuphane. Disk uzerinde hicbir dosyayi degistirmez.
"""
import subprocess
import sys
from pathlib import Path

# Windows konsolu (cp1254 vb.) UTF-8 dışı kod sayfasında Türkçe/özel karakterle
# çökebilir (bkz. CLAUDE.md ORTAM MAYINLARI). Çıktıyı UTF-8'e zorla, düşen
# karakteri sessizce değiştir — ölçüm bunun yüzünden yarım kalmasın.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
LISTE = REPO / "_calisma" / "ic_adlar.txt"


def liste_oku():
    if not LISTE.exists():
        return None
    satirlar = [s.strip() for s in LISTE.read_text(encoding="utf-8").splitlines()]
    return [s for s in satirlar if s]


def izlenen_dosyalar():
    try:
        cikti = subprocess.run(
            ["git", "ls-files", "-z"], cwd=REPO, capture_output=True, text=True, check=True
        ).stdout
        return [d for d in cikti.split("\0") if d]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def tara(dosya_icerikleri, desenler):
    """dosya_icerikleri: {yol: metin}. Donus: [(yol, satir_no, desen, satir)]."""
    bulgular = []
    desenler_kucuk = [d.lower() for d in desenler]
    for yol, metin in dosya_icerikleri.items():
        for no, satir in enumerate(metin.splitlines(), 1):
            satir_kucuk = satir.lower()
            for d, dk in zip(desenler, desenler_kucuk):
                if dk in satir_kucuk:
                    bulgular.append((yol, no, d, satir.strip()))
    return bulgular


def dosyalari_oku(yollar):
    icerikler = {}
    for yol in yollar:
        tam = REPO / yol
        try:
            with open(tam, "rb") as f:
                ham = f.read()
            if b"\0" in ham[:8192]:
                continue  # ikili dosya
            icerikler[yol] = ham.decode("utf-8", errors="replace")
        except OSError:
            continue
    return icerikler


def run_real():
    desenler = liste_oku()
    if desenler is None:
        print(f"ATLANDI: {LISTE} yok — iç ad listesi yazılmadan bu kapı ölçüm yapmaz.")
        return 0
    yollar = izlenen_dosyalar()
    if yollar is None:
        print("ATLANDI: git ls-files başarısız (git deposu değil mi?).")
        return 0

    icerikler = dosyalari_oku(yollar)
    bulgular = tara(icerikler, desenler)

    if not bulgular:
        print(f"PASS — {len(yollar)} izlenen dosya, {len(desenler)} desen, 0 eşleşme.")
        return 0

    print(f"FAIL — {len(bulgular)} eşleşme:")
    for yol, no, desen, satir in bulgular:
        print(f"   {yol}:{no}  [{desen}]  {satir[:120]}")
    print("\nSONUC: DUZELT — bu depo public; iç ad/oturum no/yerel yol repoya giremez.")
    return 1


def run_pozitif_kontrol():
    desenler = liste_oku()
    if not desenler:
        print(f"ATLANDI: {LISTE} yok — pozitif kontrol için önce liste gerekir.")
        return 0
    yollar = izlenen_dosyalar()
    if not yollar:
        print("ATLANDI: git ls-files başarısız.")
        return 0

    hedef_yol = next((y for y in yollar if y.endswith("README.md")), yollar[0])
    icerik = (REPO / hedef_yol).read_text(encoding="utf-8", errors="replace")
    kirli = icerik + f"\n<!-- test: {desenler[0]} -->\n"

    bulgular = tara({hedef_yol: kirli}, desenler)
    print(f"POZITIF KONTROL — hedef: {hedef_yol}, eklenen iç ad: {desenler[0]!r}")
    if bulgular:
        print(f"  kapı sonucu: FAIL ({len(bulgular)} eşleşme) — kapı görüyor, kör değil.")
        return 0
    else:
        print("  kapı sonucu: PASS — bilerek eklenen iç ad yakalanmadı. KAPI KÖR.")
        return 1


def main():
    if "--pozitif-kontrol" in sys.argv:
        sys.exit(run_pozitif_kontrol())
    sys.exit(run_real())


if __name__ == "__main__":
    main()
