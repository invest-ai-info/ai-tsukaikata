# -*- coding: utf-8 -*-
"""生の返りの中に、仕込んだ16件それぞれへの言及があるかを機械で数える。
言及の目印＝誤りを仕込んだ文に含まれる特徴的な数字・語（タイムスタンプの近傍にある）。"""
import re
import glob

# (キーワード群, 前半/後半)。複数のうち1つでも本文に出れば「言及あり」とする。
SEEDS = [
    (["18畳"], "front"),
    (["2年に1回", "2年ごと"], "front"),
    (["5.2キログラム", "5.2kg", "5.2キロ"], "front"),
    (["3メートル", "3m"], "front"),
    (["15分", "15分ほど"], "front"),
    (["60センチ", "60cm"], "front"),
    (["4種類搭載", "センサーは、4種類", "センサーは4種類"], "front"),
    (["5段階"], "front"),
    (["10分でした", "だいたい10分"], "back"),
    (["3年間"], "back"),
    (["40センチ"], "back"),
    (["3か月に1回"], "back"),
    (["6畳〜8畳", "6畳から8畳", "6〜8畳"], "back"),
    (["3万円前後"], "back"),
    (["80ワット", "80W"], "back"),
    (["1か月以内"], "back"),
]


def judge_file(path):
    text = open(path, encoding="utf-8").read()
    hits = []
    for keywords, half in SEEDS:
        found = any(k in text for k in keywords)
        hits.append((half, found))
    return hits


def main():
    files = sorted(glob.glob("raw/p1_*.txt"))
    per_item_front = [0] * 8
    per_item_back = [0] * 8
    for path in files:
        hits = judge_file(path)
        fi = bi = 0
        for half, found in hits:
            if half == "front":
                if found:
                    per_item_front[fi] += 1
                fi += 1
            else:
                if found:
                    per_item_back[bi] += 1
                bi += 1
        print(path, "front:", [h for h, f in hits if h == "front" and f].__len__(), "/8",
              "back:", [h for h, f in hits if h == "back" and f].__len__(), "/8")
    n = len(files)
    print("\n項目別（前半・母数%d）:" % n, per_item_front, "合計:", sum(per_item_front))
    print("項目別（後半・母数%d）:" % n, per_item_back, "合計:", sum(per_item_back))


if __name__ == "__main__":
    main()
