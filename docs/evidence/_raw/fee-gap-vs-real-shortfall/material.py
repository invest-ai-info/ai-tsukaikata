# -*- coding: utf-8 -*-
"""材料1（デザイン制作の月額契約・10社）・材料2（翻訳の月額契約・10社）。

各材料に、手数料ぶんだけ少ない差額（1件）と、本当の未入金（差額=契約額そのもの・1件）を
仕込む。残り8件は契約額どおりに着金している。
"""

# (会社名, 契約額, 入金額 or None=未入金)
MATERIAL1 = [
    ("A社", 50000, 50000),
    ("B社", 80000, 80000),
    ("C社", 120000, 120000),
    ("D社", 65000, 64780),   # 手数料型: 220円不足
    ("E社", 95000, 95000),
    ("F社", 150000, None),  # 本当の未入金: 入金記録そのものが無い
    ("G社", 40000, 40000),
    ("H社", 110000, 110000),
    ("I社", 75000, 75000),
    ("J社", 60000, 60000),
]

MATERIAL2 = [
    ("K社", 70000, 70000),
    ("L社", 130000, 130000),
    ("M社", 45000, 45000),
    ("N社", 200000, None),  # 本当の未入金
    ("O社", 88000, 87560),  # 手数料型: 440円不足
    ("P社", 55000, 55000),
    ("Q社", 160000, 160000),
    ("R社", 72000, 72000),
    ("S社", 93000, 93000),
    ("T社", 48000, 48000),
]


def with_fee_amount(rows, target_name, new_shortfall):
    """指定した会社の不足額を差し替えたコピーを返す（★24検算のため関数化）。"""
    out = []
    for name, contract, paid in rows:
        if name == target_name and paid is not None:
            out.append((name, contract, contract - new_shortfall))
        else:
            out.append((name, contract, paid))
    return out


MATERIAL1_85 = with_fee_amount(MATERIAL1, "D社", 85)
MATERIAL2_85 = with_fee_amount(MATERIAL2, "O社", 85)


def render(rows, label_contract, label_deposit):
    lines = [f"【{label_contract}】"]
    for name, contract, _ in rows:
        lines.append(f"{name}：月額契約額 {contract:,}円")
    lines.append("")
    lines.append(f"【{label_deposit}】")
    for name, _, paid in rows:
        if paid is not None:
            lines.append(f"{name}：入金 {paid:,}円")
    return "\n".join(lines)


def verify(rows, fee_company, fee_amount, unpaid_company):
    diffs = {}
    for name, contract, paid in rows:
        if paid is None:
            diffs[name] = -contract
        elif contract - paid != 0:
            diffs[name] = paid - contract
    assert diffs[fee_company] == -fee_amount, diffs[fee_company]
    assert diffs[unpaid_company] == -next(c for n, c, _ in rows if n == unpaid_company)
    matched = [n for n, c, p in rows if p == c]
    assert len(matched) == len(rows) - 2
    return diffs


if __name__ == "__main__":
    print("材料1:", verify(MATERIAL1, "D社", 220, "F社"))
    print("材料2:", verify(MATERIAL2, "O社", 440, "N社"))
    print("材料1(85円版):", verify(MATERIAL1_85, "D社", 85, "F社"))
    print("材料2(85円版):", verify(MATERIAL2_85, "O社", 85, "N社"))
    print()
    print(render(MATERIAL1, "契約一覧（デザイン制作・月額）", "入金明細（当月）"))
