# -*- coding: utf-8 -*-
"""材料A・材料Bの請求一覧を生成し、仕込みを検算する。
H50: 1社の備考に異なる2件分の曖昧なキャンセル（確定額は書かれていない）を仕込み、
計算手順を明示した指示文で両方を正しく引けるかを見る。"""
import re

MATERIAL_A = {
    "name": "Webサイト保守契約",
    "clients": [
        # (社名, 基本月額, 備考, 確定請求額, 実際の入金額)
        ("青山システム", 36000, "", 36000, 36000),
        ("ひばり工房", 29000, "", 29000, 29000),
        ("丸山設計", 41000, "", 41000, 41000),
        ("港南商事", 53000, "", 53000, 53000),
        ("若葉堂", 23000, "", 23000, 23000),
        ("大地物産", 39000, "", 39000, 39000),
        ("白鳥クリニック", 61000, "", 61000, 61000),
        ("旭フーズ", 32000, "", 32000, 32000),
        ("虹ケ丘会計", 46000, "", 46000, 46000),
        # 真の未入金：備考なし・入金0
        ("たんぽぽ保育園", 28000, "", 28000, 0),
        # 正当なキャンセル：確定額まで明記。入金は確定額どおり（対照）
        ("北斎自動車", 53000, "今月はオプションの多言語対応（13,000円）をキャンセルされたため、請求額を40,000円に修正済みです。", 40000, 40000),
        # 曖昧な二重キャンセル：2件分のキャンセル額だけ書かれ、確定額は書かれていない
        ("満月印刷", 49000, "今月はオプションA（年末休業対応・3,000円）とオプションB（深夜対応・2,000円）の両方をキャンセルされたとの連絡があり、返金対応済みです。", None, 40000),
    ],
}

MATERIAL_B = {
    "name": "SNS運用代行契約",
    "clients": [
        ("あかね接骨院", 34000, "", 34000, 34000),
        ("フローラ花店", 27000, "", 27000, 27000),
        ("やよい行政書士事務所", 45000, "", 45000, 45000),
        ("みなと珈琲", 30000, "", 30000, 30000),
        ("桃山動物病院", 56000, "", 56000, 56000),
        ("ひかり学習塾", 38000, "", 38000, 38000),
        ("green terrace", 25000, "", 25000, 25000),
        ("大手町不動産", 59000, "", 59000, 59000),
        ("さくら接骨院", 31000, "", 31000, 31000),
        # 真の未入金
        ("朝日整体院", 33000, "", 33000, 0),
        # 正当なキャンセル（対照）
        ("緑風工務店", 47000, "追加の動画広告オプション（11,000円）をキャンセルされたため、請求額を36,000円に修正済みです。", 36000, 36000),
        # 曖昧な二重キャンセル
        ("星空クリニック", 51000, "今月はストーリーズ投稿オプション（4,000円）と、ハイライト編集オプション（1,500円）の両方をキャンセルされたとの連絡があり、返金対応済みです。", None, 43000),
    ],
}


def verify(material):
    print(f"=== {material['name']} ===")
    for name, base, memo, confirmed, paid in material["clients"]:
        billed = confirmed if confirmed is not None else base
        gap = billed - paid
        tag = f"  <-- 差額 {gap}円" if gap != 0 else ""
        print(f"{name:12s} 基本{base:>7}円 確定{billed if confirmed is not None else '(未確定)':>7} 入金{paid:>7}円{tag}")
    print(f"行数: {len(material['clients'])}")
    print()


def assertions(material):
    rows = {name: (base, memo, confirmed, paid) for name, base, memo, confirmed, paid in material["clients"]}

    normal = [n for n, (b, m, c, p) in rows.items() if m == "" and p == b]
    assert len(normal) == 9, len(normal)

    missing = [n for n, (b, m, c, p) in rows.items() if m == "" and p == 0]
    assert len(missing) == 1, missing

    legit = [n for n, (b, m, c, p) in rows.items() if m != "" and c is not None]
    assert len(legit) == 1, legit
    for n in legit:
        b, m, c, p = rows[n]
        assert p == c, (n, p, c)
        assert c < b, (n, c, b)

    ambiguous = [n for n, (b, m, c, p) in rows.items() if m != "" and c is None]
    assert len(ambiguous) == 1, ambiguous
    for n in ambiguous:
        b, m, c, p = rows[n]
        amts = [int(x.replace(",", "")) for x in re.findall(r"（[^（）]*?([\d,]+)円）", m)]
        assert len(amts) == 2, (n, amts, m)
        true_confirmed = b - sum(amts)
        shortfall = true_confirmed - p
        assert shortfall > 0, (n, shortfall)
        print(f"  二重キャンセル {n}: 基本{b} - ({amts[0]}+{amts[1]}) = 確定{true_confirmed} / 入金{p} / 本当の不足{shortfall}")

    print("検算OK\n")


if __name__ == "__main__":
    for mat in (MATERIAL_A, MATERIAL_B):
        verify(mat)
        assertions(mat)
