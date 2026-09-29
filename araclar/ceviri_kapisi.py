#!/usr/bin/env python3
"""ceviri_kapisi.py — TR (skills/gedik-tr) <-> EN (skills/gedik) mekanik ceviri kapisi.

Her dosya ciftinde dort sey esit olmali:
  1) baslik sayisi (# .. ######)
  2) tablo satiri sayisi (markdown "|" satirlari, ayrac satiri haric)
  3) kod blogu sayisi (``` ile acilip kapanan bloklar)
  4) her kod blogunun ICERIGI - TR ve EN'de sirayla ayni hash (sha256)

Kullanim:
  python araclar/ceviri_kapisi.py                 # gercek dosya ciftlerini denetler
  python araclar/ceviri_kapisi.py --pozitif-kontrol  # kor kapi oz-testi (D1): EN kopyadan
                                                      # bir tablo satiri silinince kapi
                                                      # KIRMIZI yanmali; yanmiyorsa kapi kordur.

Yalniz standart kutuphane. Disk uzerinde hicbir dosyayi degistirmez.
"""
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TR_ROOT = REPO / "skills" / "gedik-tr"
EN_ROOT = REPO / "skills" / "gedik"

HEADER_RE = re.compile(r"^#{1,6}\s")
FENCE_RE = re.compile(r"^```")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
# ayrac satiri: | --- | :---: | ... | (yalniz -, :, |, bosluk)
TABLE_SEP_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")


def analyze(text):
    """Metni satir satir okuyup (baslik_sayisi, tablo_satiri_sayisi, kod_bloklari) dondurur.
    kod_bloklari: [(sha256_hex, satir_sayisi), ...] sirayla.
    """
    lines = text.splitlines()
    header_count = 0
    table_row_count = 0
    code_blocks = []
    in_fence = False
    fence_buf = []
    in_table = False

    for line in lines:
        if FENCE_RE.match(line):
            if not in_fence:
                in_fence = True
                fence_buf = []
            else:
                in_fence = False
                content = "\n".join(fence_buf)
                h = hashlib.sha256(content.encode("utf-8")).hexdigest()
                code_blocks.append((h, len(fence_buf)))
            continue
        if in_fence:
            fence_buf.append(line)
            continue
        if HEADER_RE.match(line):
            header_count += 1
        if TABLE_ROW_RE.match(line):
            if TABLE_SEP_RE.match(line):
                in_table = True  # ayrac satiri tabloyu dogrular ama satir sayilmaz
                continue
            table_row_count += 1
            in_table = True
        else:
            in_table = False

    return {
        "header_count": header_count,
        "table_row_count": table_row_count,
        "code_block_count": len(code_blocks),
        "code_blocks": code_blocks,
    }


def compare(tr_text, en_text):
    """Iki metni karsilastirir; (PASS/FAIL, [sebep, ...]) dondurur."""
    tr = analyze(tr_text)
    en = analyze(en_text)
    reasons = []

    if tr["header_count"] != en["header_count"]:
        reasons.append(
            f"baslik sayisi farkli: TR={tr['header_count']} EN={en['header_count']}"
        )
    if tr["table_row_count"] != en["table_row_count"]:
        reasons.append(
            f"tablo satiri sayisi farkli: TR={tr['table_row_count']} EN={en['table_row_count']}"
        )
    if tr["code_block_count"] != en["code_block_count"]:
        reasons.append(
            f"kod blogu sayisi farkli: TR={tr['code_block_count']} EN={en['code_block_count']}"
        )
    else:
        for i, ((tr_hash, tr_n), (en_hash, en_n)) in enumerate(
            zip(tr["code_blocks"], en["code_blocks"]), start=1
        ):
            if tr_hash != en_hash:
                reasons.append(
                    f"kod blogu #{i} icerigi farkli (TR {tr_n} satir, EN {en_n} satir, hash uyusmuyor)"
                )

    return ("PASS" if not reasons else "FAIL"), reasons


def find_pairs():
    if not TR_ROOT.is_dir() or not EN_ROOT.is_dir():
        return []
    pairs = []
    for tr_path in sorted(TR_ROOT.rglob("*.md")):
        rel = tr_path.relative_to(TR_ROOT)
        en_path = EN_ROOT / rel
        pairs.append((rel, tr_path, en_path))
    return pairs


def run_real():
    pairs = find_pairs()
    if not pairs:
        print(f"ATLANDI: {TR_ROOT} ya da {EN_ROOT} yok.")
        return 0  # kapi atlandi, kirmizi degil (henuz Dilim 2 kosmamis olabilir)

    all_pass = True
    for rel, tr_path, en_path in pairs:
        if not en_path.exists():
            print(f"FAIL {rel} — EN karsiligi yok: {en_path}")
            all_pass = False
            continue
        tr_text = tr_path.read_text(encoding="utf-8")
        en_text = en_path.read_text(encoding="utf-8")
        verdict, reasons = compare(tr_text, en_text)
        if verdict == "PASS":
            print(f"PASS {rel}")
        else:
            all_pass = False
            print(f"FAIL {rel}")
            for r in reasons:
                print(f"   - {r}")

    print()
    print("SONUC: TESLIME UYGUN" if all_pass else "SONUC: DUZELT")
    return 0 if all_pass else 1


def run_pozitif_kontrol():
    """Kor kapi oz-testi (D1). Gercek bir TR/EN ciftini bul, EN kopyasindan bilerek
    bir tablo satiri sil, kapi KIRMIZI yaniyor mu dogrula. Diskteki hicbir dosyayi
    degistirmez — yalniz bellekte calisir."""
    pairs = find_pairs()
    target = None
    for rel, tr_path, en_path in pairs:
        if not en_path.exists():
            continue
        en_text = en_path.read_text(encoding="utf-8")
        if any(
            TABLE_ROW_RE.match(l) and not TABLE_SEP_RE.match(l)
            for l in en_text.splitlines()
        ):
            target = (rel, tr_path, en_path)
            break

    if target is None:
        print(
            "ATLANDI: pozitif kontrol icin tablo satiri iceren bir TR/EN cifti bulunamadi "
            "(Dilim 2 henuz kosmamis olabilir)."
        )
        return 0

    rel, tr_path, en_path = target
    tr_text = tr_path.read_text(encoding="utf-8")
    en_lines = en_path.read_text(encoding="utf-8").splitlines()

    victim_idx = next(
        i
        for i, l in enumerate(en_lines)
        if TABLE_ROW_RE.match(l) and not TABLE_SEP_RE.match(l)
    )
    corrupted_lines = en_lines[:victim_idx] + en_lines[victim_idx + 1 :]
    corrupted_text = "\n".join(corrupted_lines)

    verdict, reasons = compare(tr_text, corrupted_text)

    print(f"POZITIF KONTROL — hedef: {rel}")
    print(f"  silinen satir: {en_lines[victim_idx]!r}")
    print(f"  kapi sonucu (bozuk EN'e karsi): {verdict}")
    for r in reasons:
        print(f"   - {r}")

    if verdict == "FAIL":
        print("\nSONUC: KAPI GORUYOR (kirmizi yanmali yerde yandi) — kor kapi degil.")
        return 0
    else:
        print(
            "\nSONUC: KAPI KOR — bir tablo satiri silindiginde bile PASS verdi. "
            "Olcum reddedilir."
        )
        return 1


def main():
    if "--pozitif-kontrol" in sys.argv:
        sys.exit(run_pozitif_kontrol())
    sys.exit(run_real())


if __name__ == "__main__":
    main()
