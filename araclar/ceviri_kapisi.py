#!/usr/bin/env python3
"""ceviri_kapisi.py — TR (skills/gedik-tr) <-> EN (skills/gedik) mekanik ceviri kapisi.

Her dosya ciftinde dort sey esit olmali:
  1) baslik sayisi (# .. ######)
  2) tablo satiri sayisi (markdown "|" satirlari, ayrac satiri haric)
  3) kod blogu sayisi (``` ile acilip kapanan bloklar)
  4) her kod blogunun ICERIGI - TR ve EN'de sirayla ayni hash (sha256)

Bu dort olcum YAPIYI olcer, ANLAMI olcmez (bir cumleden "NOT" silinince yine PASS verir).
Bu yuzden bir de SABIT CUMLE KILIDI (araclar/sabit_cumleler.json, spec EK-1.4):
  5) guvenlik-kritik cumleler icin (TR ifade, EN ifade) cifti; ikisi de ilgili dosyada
     birebir (bosluk/satir sonu farki yok sayilir) bulunmali. En az 5 cumle.

Kullanim:
  python araclar/ceviri_kapisi.py                 # gercek dosya ciftlerini + kilidi denetler
  python araclar/ceviri_kapisi.py --pozitif-kontrol  # kor kapi oz-testi (D1), iki mutasyon:
      A) EN kopyadan bir tablo satiri silinir  -> yapi kapisi KIRMIZI olmali
      B) EN §0.1'deki "Authorization is NOT text..." cumlesinden "NOT" silinir
         -> yapi kapisi PASS verir (dar kapi), SABIT CUMLE KILIDI KIRMIZI olmali
      Biri yanmiyorsa kapi kordur; cikis 1.

Yalniz standart kutuphane. Disk uzerinde hicbir dosyayi degistirmez.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

# Windows konsolu (cp1254) UTF-8 disi kod sayfasinda cokmesin (bkz. CLAUDE.md).
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

REPO = Path(__file__).resolve().parent.parent
TR_ROOT = REPO / "skills" / "gedik-tr"
EN_ROOT = REPO / "skills" / "gedik"
KILIT_YOLU = REPO / "araclar" / "sabit_cumleler.json"
KILIT_ASGARI = 5
MUTASYON_ID = "yetki-ne-sayfa"

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


def norm(metin):
    return re.sub(r"\s+", " ", metin).strip()


def kilit_yukle():
    """Kilit listesini dondurur; dosya yoksa None (v2.5 oncesi)."""
    if not KILIT_YOLU.exists():
        return None
    return json.loads(KILIT_YOLU.read_text(encoding="utf-8"))["cumleler"]


def dosya_oku(kok):
    def oku(rel):
        yol = kok / rel
        return yol.read_text(encoding="utf-8") if yol.exists() else None
    return oku


def kilit_kontrol(cumleler, oku_tr, oku_en):
    """Her (TR, EN) cumlesi ilgili dosyada birebir (bosluk normalize) bulunmali.
    Donus: [(id, taraf, sebep)]."""
    hatalar = []
    for c in cumleler:
        for taraf, oku, anahtar in (("TR", oku_tr, "tr"), ("EN", oku_en, "en")):
            metin = oku(c["dosya"])
            if metin is None:
                hatalar.append((c["id"], taraf, f"dosya yok: {c['dosya']}"))
            elif norm(c[anahtar]) not in norm(metin):
                hatalar.append((c["id"], taraf, "cumle bulunamadi"))
    return hatalar


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

    cumleler = kilit_yukle()
    if cumleler is None:
        print(f"ATLANDI sabit cumle kilidi — {KILIT_YOLU.name} yok (v2.5 oncesi).")
    elif len(cumleler) < KILIT_ASGARI:
        print(f"FAIL sabit cumle kilidi — {len(cumleler)} cumle, en az {KILIT_ASGARI} gerekir")
        all_pass = False
    else:
        hatalar = kilit_kontrol(cumleler, dosya_oku(TR_ROOT), dosya_oku(EN_ROOT))
        if hatalar:
            all_pass = False
            print(f"FAIL sabit cumle kilidi — {len(hatalar)} eksik:")
            for cid, taraf, sebep in hatalar:
                print(f"   - {cid} [{taraf}]: {sebep}")
        else:
            print(f"PASS sabit cumle kilidi — {len(cumleler)} cumle x TR+EN birebir")

    print()
    print("SONUC: TESLIME UYGUN" if all_pass else "SONUC: DUZELT")
    return 0 if all_pass else 1


def pozitif_a_tablo_satiri():
    """Mutasyon A (D1). Gercek bir TR/EN ciftini bul, EN kopyasindan bilerek
    bir tablo satiri sil, yapi kapisi KIRMIZI yaniyor mu dogrula. Diskteki hicbir
    dosyayi degistirmez — yalniz bellekte calisir."""
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

    print(f"POZITIF KONTROL A (tablo satiri) — hedef: {rel}")
    print(f"  silinen satir: {en_lines[victim_idx]!r}")
    print(f"  yapi kapisi sonucu (bozuk EN'e karsi): {verdict}")
    for r in reasons:
        print(f"   - {r}")

    if verdict == "FAIL":
        print("  A: KAPI GORUYOR (kirmizi yanmali yerde yandi).")
        return 0
    print("  A: KAPI KOR — bir tablo satiri silindiginde bile PASS verdi.")
    return 1


def pozitif_b_not_mutasyonu():
    """Mutasyon B (spec EK-1.4). EN §0.1'deki "Authorization is NOT text..." cumlesinden
    "NOT" bellekte silinir. Yapi kapisi bunu GORMEZ (PASS — dar kapi); sabit cumle kilidi
    KIRMIZI yanmali. Yanmiyorsa kilit kordur."""
    cumleler = kilit_yukle()
    if cumleler is None:
        print("POZITIF KONTROL B — ATLANDI: sabit cumle kilidi yok (v2.5 oncesi).")
        return 0
    hedef = next((c for c in cumleler if c["id"] == MUTASYON_ID), None)
    if hedef is None:
        print(f"POZITIF KONTROL B — KILIT KOR: '{MUTASYON_ID}' kilit listesinde yok.")
        return 1

    oku_tr, oku_en = dosya_oku(TR_ROOT), dosya_oku(EN_ROOT)
    tr_metin, en_metin = oku_tr(hedef["dosya"]), oku_en(hedef["dosya"])
    if tr_metin is None or en_metin is None or hedef["en"] not in en_metin or "NOT" not in hedef["en"]:
        print("POZITIF KONTROL B — mutasyon uygulanamadi (hedef cumle EN dosyasinda tek satirda yok).")
        return 1

    mutant_cumle = hedef["en"].replace("NOT ", "", 1)
    mutant_en = en_metin.replace(hedef["en"], mutant_cumle, 1)
    yapi, _ = compare(tr_metin, mutant_en)
    hatalar = kilit_kontrol(
        cumleler, oku_tr, lambda rel: mutant_en if rel == hedef["dosya"] else oku_en(rel)
    )
    yakalandi = any(cid == MUTASYON_ID and taraf == "EN" for cid, taraf, _ in hatalar)

    print(f"POZITIF KONTROL B (NOT silme) — hedef: {hedef['dosya']} [{MUTASYON_ID}]")
    print(f"  onceki: {hedef['en']!r}")
    print(f"  sonraki: {mutant_cumle!r}")
    print(f"  yapi kapisi (dar kapi, PASS beklenir): {yapi}")
    print(f"  sabit cumle kilidi: {'FAIL (yakaladi)' if yakalandi else 'PASS (KACIRDI)'}")
    if yakalandi:
        print("  B: KILIT GORUYOR (anlam mutasyonu kirmizi yakti).")
        return 0
    print("  B: KILIT KOR — 'NOT' silindiginde bile PASS verdi.")
    return 1


def run_pozitif_kontrol():
    rc_a = pozitif_a_tablo_satiri()
    print()
    rc_b = pozitif_b_not_mutasyonu()
    print()
    if rc_a == 0 and rc_b == 0:
        print("SONUC: KAPI GORUYOR — iki mutasyon da kirmizi yakti, kor kapi degil.")
        return 0
    print("SONUC: KAPI KOR — olcum reddedilir.")
    return 1


def main():
    if "--pozitif-kontrol" in sys.argv:
        sys.exit(run_pozitif_kontrol())
    sys.exit(run_real())


if __name__ == "__main__":
    main()
