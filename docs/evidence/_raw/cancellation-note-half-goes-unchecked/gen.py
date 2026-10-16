# -*- coding: utf-8 -*-
"""材料A・材料Bの請求一覧・入金明細を生成し、仕込みを検算する。"""

MATERIAL_A = {
    "name": "Webサイト保守契約",
    "service_label": "保守内容",
    "clients": [
        # (社名, 基本月額, 備考, 確定請求額, 実際の入金額)
        ("山田商会", 35000, "", 35000, 35000),
        ("さくら工房", 28000, "", 28000, 28000),
        ("高橋設計事務所", 42000, "", 42000, 42000),
        ("みなと食品", 50000, "", 50000, 50000),
        ("緑風堂", 22000, "", 22000, 22000),
        ("大地興業", 38000, "", 38000, 38000),
        ("青空クリニック", 60000, "", 60000, 60000),
        ("富士フーズ", 31000, "", 31000, 31000),
        ("虹の会計事務所", 45000, "", 45000, 45000),
        # 真の未入金：備考なし・入金0
        ("ひまわり保育園", 27000, "", 27000, 0),
        # 正当なキャンセル：備考に元額・キャンセル額・確定額を明記。入金は確定額どおり
        ("北斗自動車", 52000, "今月はオプションの多言語対応（12,000円）をキャンセルされたため、請求額を40,000円に修正済みです。", 40000, 40000),
        # 曖昧なキャンセル：キャンセルの事実だけ書かれ、確定額は書かれていない。実際の入金は「元額−キャンセル額」より少ない
        ("月光印刷", 48000, "今月は年末休業オプション（3,000円）分をキャンセルされたとの連絡があり、返金対応済みです。", None, 41000),
    ],
}

MATERIAL_B = {
    "name": "SNS運用代行契約",
    "service_label": "運用内容",
    "clients": [
        ("あおば接骨院", 33000, "", 33000, 33000),
        ("フラワーショップ結", 26000, "", 26000, 26000),
        ("やまと行政書士事務所", 44000, "", 44000, 44000),
        ("湊カフェ", 29000, "", 29000, 29000),
        ("桜坂動物病院", 55000, "", 55000, 55000),
        ("のぞみ学習塾", 37000, "", 37000, 37000),
        ("green garden", 24000, "", 24000, 24000),
        ("丸の内不動産", 58000, "", 58000, 58000),
        ("たなか接骨院", 30000, "", 30000, 30000),
        # 真の未入金
        ("ひので整体院", 32000, "", 32000, 0),
        # 正当なキャンセル：確定額まで明記、入金は確定額どおり
        ("みどり工務店", 46000, "今月は追加の動画広告オプション（10,000円）をキャンセルされたため、請求額を36,000円に修正済みです。", 36000, 36000),
        # 曖昧なキャンセル：確定額は書かれていない。実際の入金は「元額−キャンセル額」より少ない
        ("星野クリニック", 50000, "今月はストーリーズ投稿オプション（4,000円）分をキャンセルされたとの連絡があり、返金対応済みです。", None, 44000),
    ],
}


def verify(material):
    print(f"=== {material['name']} ===")
    total_invoice = 0
    total_paid = 0
    for name, base, memo, confirmed, paid in material["clients"]:
        billed = confirmed if confirmed is not None else base
        gap = billed - paid
        total_invoice += billed
        total_paid += paid
        tag = ""
        if gap != 0:
            tag = f"  <-- 差額 {gap}円"
        print(f"{name:12s} 基本{base:>7}円 確定{billed if confirmed is not None else '(未確定)':>7} 入金{paid:>7}円{tag}")
    print(f"行数: {len(material['clients'])}")
    print()


def assertions(material):
    rows = {name: (base, memo, confirmed, paid) for name, base, memo, confirmed, paid in material["clients"]}

    # 正常9社：確定額どおりに入金されている
    normal = [n for n, (b, m, c, p) in rows.items() if m == "" and p == b]
    assert len(normal) == 9, len(normal)
    for n in normal:
        b, m, c, p = rows[n]
        assert p == b, (n, p, b)

    # 真の未入金：備考なし・入金0
    missing = [n for n, (b, m, c, p) in rows.items() if m == "" and p == 0]
    assert len(missing) == 1, missing

    # 正当なキャンセル：確定額が明記され、入金が確定額と一致（不足ゼロ）
    legit = [n for n, (b, m, c, p) in rows.items() if m != "" and c is not None]
    assert len(legit) == 1, legit
    for n in legit:
        b, m, c, p = rows[n]
        assert p == c, (n, p, c)
        assert c < b, (n, c, b)

    # 曖昧なキャンセル：確定額が書かれていない。備考のキャンセル額を引いた金額より、実際の入金はさらに少ない
    ambiguous = [n for n, (b, m, c, p) in rows.items() if m != "" and c is None]
    assert len(ambiguous) == 1, ambiguous
    for n in ambiguous:
        b, m, c, p = rows[n]
        # 備考からキャンセル額を抜き出して、本当の確定額を計算する（記事側の真値）
        import re
        amt = re.search(r"（([\d,]+)円）", m)
        cancel_amt = int(amt.group(1).replace(",", ""))
        true_confirmed = b - cancel_amt
        shortfall = true_confirmed - p
        assert shortfall > 0, (n, shortfall)
        print(f"  曖昧キャンセル {n}: 基本{b} - キャンセル{cancel_amt} = 確定{true_confirmed} / 入金{p} / 本当の不足{shortfall}")

    print("検算OK\n")


if __name__ == "__main__":
    for mat in (MATERIAL_A, MATERIAL_B):
        verify(mat)
        assertions(mat)
