# -*- coding: utf-8 -*-
import re, glob

ITEMS = [
    ("F1_18畳", ["18畳"], "front"),
    ("F2_2年に1回", ["2年に1回", "2年ごと"], "front"),
    ("F3_5.2kg", ["5.2キログラム", "5.2kg", "5.2キロ"], "front"),
    ("F4_3m", ["3メートル", "3m"], "front"),
    ("F5_15分", ["15分"], "front"),
    ("F6_60cm", ["60センチ", "60cm"], "front"),
    ("F7_4種類", ["4種類"], "front"),
    ("F8_5段階", ["5段階"], "front"),
    ("B1_10分", ["10分"], "back"),
    ("B2_3年間", ["3年間"], "back"),
    ("B3_40cm", ["40センチ", "40cm"], "back"),
    ("B4_3か月に1回", ["3か月に1回", "3ヶ月に1回"], "back"),
    ("B5_6-8畳", ["6畳", "8畳向け", "6〜8畳", "6畳〜8畳"], "back"),
    ("B6_3万円", ["3万円"], "back"),
    ("B7_80W", ["80ワット", "80W"], "back"),
    ("B8_1か月以内", ["1か月以内", "1ヶ月以内"], "back"),
]

def flagged(text, keywords):
    # 数字が出現し、かつ疑い・不自然・誤変換等の語がその近傍(200字)にあるか
    for kw in keywords:
        for m in re.finditer(re.escape(kw), text):
            seg = text[max(0, m.start()-250):m.end()+250]
            if re.search(r"不自然|誤変換|聞き取り|聞き間違い|疑わし|唐突|可能性|ズレ|食い違|矛盾|怪しい|気になる箇所|引っかか", seg):
                return True
    return False

files = sorted(glob.glob("raw/p1_*.txt"))
table = {name: [] for name, _, _ in ITEMS}
for path in files:
    text = open(path, encoding="utf-8").read()
    for name, kws, half in ITEMS:
        table[name].append(1 if flagged(text, kws) else 0)

print(f"{'項目':14s} {'half':6s} " + " ".join(f"run{i+1}" for i in range(len(files))) + "  合計")
front_sum = [0]*len(files)
back_sum = [0]*len(files)
for name, kws, half in ITEMS:
    row = table[name]
    print(f"{name:14s} {half:6s} " + "  ".join(str(x) for x in row) + f"   {sum(row)}/{len(files)}")
    if half == "front":
        front_sum = [a+b for a, b in zip(front_sum, row)]
    else:
        back_sum = [a+b for a, b in zip(back_sum, row)]

front_items = [n for n, _, h in ITEMS if h == "front"]
back_items = [n for n, _, h in ITEMS if h == "back"]
front_total = sum(sum(table[n]) for n in front_items)
back_total = sum(sum(table[n]) for n in back_items)
print(f"\n前半(8項目×{len(files)}回={8*len(files)}): 合計検出 {front_total}")
print(f"後半(8項目×{len(files)}回={8*len(files)}): 合計検出 {back_total}")
