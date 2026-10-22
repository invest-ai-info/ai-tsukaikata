# -*- coding: utf-8 -*-
"""機械の下準備（一次スクリーニング）。⚠️ 否定表現（「不自然ではない」「誤変換ではない」
「矛盾しません」等）を判定できないため、ヒットした箇所は必ず人が生の文を読み直して
最終判定した（台帳12番＝計測器のほうが間違っていることがある）。
最終的に採用した数字は docs/evidence/long-caption-position-bias.md に記載の、
人が確認した値であり、このスクリプトの出力そのものではない。"""
import re, glob, sys

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

def run(pattern, label):
    files = sorted(glob.glob(pattern))
    if not files:
        return
    table = {name: [] for name, _, _ in ITEMS}
    for path in files:
        text = open(path, encoding="utf-8").read()
        for name, kws, half in ITEMS:
            table[name].append(1 if flagged(text, kws) else 0)

    print(f"\n=== {label}（一次スクリーニング・否定表現は未処理） ===")
    print(f"{'項目':14s} {'half':6s} " + " ".join(f"run{i+1}" for i in range(len(files))) + "  合計")
    for name, kws, half in ITEMS:
        row = table[name]
        print(f"{name:14s} {half:6s} " + "  ".join(str(x) for x in row) + f"   {sum(row)}/{len(files)}")

    front_items = [n for n, _, h in ITEMS if h == "front"]
    back_items = [n for n, _, h in ITEMS if h == "back"]
    front_total = sum(sum(table[n]) for n in front_items)
    back_total = sum(sum(table[n]) for n in back_items)
    print(f"前半(8項目×{len(files)}回={8*len(files)}): 一次スクリーニング合計 {front_total}")
    print(f"後半(8項目×{len(files)}回={8*len(files)}): 一次スクリーニング合計 {back_total}")


if __name__ == "__main__":
    run("raw/full_*.txt", "通し（10分の全体を1回で）")
    run("raw/front_*.txt", "分割・前半のみ")
    run("raw/back_*.txt", "分割・後半のみ")
