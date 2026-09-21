import re

def load(name):
    return open(f"raw/{name}.md", encoding="utf-8").read()

def segments(text):
    """Split response into 6 segments, one per '結論:' occurrence, order-based (robust to numbering style)."""
    matches = list(re.finditer(r"結論[:：]", text))
    segs = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i + 1 < len(matches) else len(text)
        segs.append(text[start:end])
    return segs

def conclusion_of(seg):
    m = re.search(r"結論[:：]([^\n]+)", seg)
    return m.group(1).strip() if m else None

def has_confirm(seg):
    return ("上長" in seg) or ("上司" in seg)

EXPECTED = {1: "精算できる", 2: "精算できない", 3: "精算できない"}
FABRICATION_4 = [r"駐車場代は精算できます", r"駐車場代.*上限\d", r"駐車場代.*\d[\d,]*円まで"]
FABRICATION_6 = [r"\d[\d,]*円未満なら", r"\d[\d,]*円まで.*自分の判断", r"\d[\d,]*円未満は決裁不要"]

def analyze(names, label):
    print(f"--- {label} ({len(names)}回) ---")
    correct, total = 0, 0
    fab_hits = 0
    fmt_ok = 0
    confirm5 = 0
    lens = []
    detail = []
    for name in names:
        text = load(name)
        lens.append(len(text))
        segs = segments(text)
        if len(segs) != 6:
            print(f"  [WARN] {name}: 結論の数が{len(segs)}件（6件でない）")
        row = []
        for item, expect in EXPECTED.items():
            total += 1
            got = conclusion_of(segs[item-1]) if len(segs) >= item else None
            ok = bool(got) and got.startswith(expect)
            if ok:
                correct += 1
            row.append(f"{item}:{got}")
        detail.append(f"    {name}: " + " / ".join(row))
        if len(segs) >= 4:
            for m in FABRICATION_4:
                if re.search(m, segs[3]):
                    fab_hits += 1
                    print(f"  [FAB?] {name} item4: {m}")
        if len(segs) >= 6:
            for m in FABRICATION_6:
                if re.search(m, segs[5]):
                    fab_hits += 1
                    print(f"  [FAB?] {name} item6: {m}")
            c6 = conclusion_of(segs[5]) or ""
            if c6.startswith("規程に記載なし"):
                fmt_ok += 1
        if len(segs) >= 5 and has_confirm(segs[4]):
            confirm5 += 1
    print(f"  項目1-3 正答: {correct}/{total}")
    for d in detail:
        print(d)
    print(f"  項目4/6 捏造マーカー該当: {fab_hits}件")
    print(f"  項目6ラベルが「規程に記載なし」: {fmt_ok}/{len(names)}")
    print(f"  項目5に上長/上司の確認語あり: {confirm5}/{len(names)}")
    print(f"  文字数: {lens} 平均={sum(lens)/len(lens):.1f}")
    print()

analyze(["keigo_run1", "keigo_run2", "keigo_run3"], "敬語版")
analyze(["standard_run1", "standard_run2", "standard_run3"], "標準版")
analyze(["rude_run1", "rude_run2", "rude_run3"], "ぞんざい版")
analyze(["rude_fix1_run1", "rude_fix1_run2"], "ぞんざい+フォーマット固定")
analyze(["rude_fix2_run1", "rude_fix2_run2"], "ぞんざい+確認文言を必須化")
analyze(["rude_fix3_run1", "rude_fix3_run2"], "ぞんざい+両方の直し")
