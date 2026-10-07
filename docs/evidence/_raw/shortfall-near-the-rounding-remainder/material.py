# -*- coding: utf-8 -*-
"""3回払いの端数あり契約2本。本当の不足額を「端数の大きさと同じ」「端数より
さらに小さい1円」の2段階に振って、AIの入金照合が端数に紛れて見逃すかを試す。

材料1＝`odd-split-still-catches-the-real-shortfall`と同じ構造（端数は最終回に寄せる）。
材料2＝新規（端数は初回に寄せる・端数の大きさを3円にする）。
"""

CONTRACT1 = {"着手金": 33333, "中間金": 33333, "残金": 33335}   # 合計100,001円・端数2円（最終回に+2）
CONTRACT2 = {"着手金": 33336, "中間金": 33333, "残金": 33333}   # 合計100,002円・端数3円（初回に+3）


def apply_shortfall(contract, key, shortfall):
    out = dict(contract)
    out[key] -= shortfall
    return out


# 本当の不足＝端数の大きさと同じ（いちばん紛らわしい）
DEPOSITS1_MAIN = apply_shortfall(CONTRACT1, "残金", 2)     # 残金33,333円（本当の不足2円）
DEPOSITS2_MAIN = apply_shortfall(CONTRACT2, "着手金", 3)   # 着手金33,333円（本当の不足3円）

# 本当の不足＝端数の目安である1円ちょうど（さらに紛らわしい）
DEPOSITS1_1YEN = apply_shortfall(CONTRACT1, "残金", 1)     # 残金33,334円（本当の不足1円）
DEPOSITS2_1YEN = apply_shortfall(CONTRACT2, "着手金", 1)   # 着手金33,335円（本当の不足1円）


def render(contract, deposits, label):
    lines = [f"【{label}・契約書】"]
    for k, v in contract.items():
        lines.append(f"{k}：{v:,}円")
    lines.append(f"合計：{sum(contract.values()):,}円")
    lines.append("")
    lines.append(f"【{label}・入金明細】")
    for k, v in deposits.items():
        lines.append(f"{k}：{v:,}円 入金")
    return "\n".join(lines)


def verify():
    assert sum(CONTRACT1.values()) == 100001
    assert sum(CONTRACT2.values()) == 100002
    assert max(CONTRACT1.values()) - min(CONTRACT1.values()) == 2  # 端数2円
    assert max(CONTRACT2.values()) - min(CONTRACT2.values()) == 3  # 端数3円

    shortfall1_main = sum(CONTRACT1.values()) - sum(DEPOSITS1_MAIN.values())
    shortfall2_main = sum(CONTRACT2.values()) - sum(DEPOSITS2_MAIN.values())
    assert shortfall1_main == 2, shortfall1_main
    assert shortfall2_main == 3, shortfall2_main

    shortfall1_1yen = sum(CONTRACT1.values()) - sum(DEPOSITS1_1YEN.values())
    shortfall2_1yen = sum(CONTRACT2.values()) - sum(DEPOSITS2_1YEN.values())
    assert shortfall1_1yen == 1, shortfall1_1yen
    assert shortfall2_1yen == 1, shortfall2_1yen
    return {
        "material1_main_shortfall": shortfall1_main,
        "material2_main_shortfall": shortfall2_main,
        "material1_1yen_shortfall": shortfall1_1yen,
        "material2_1yen_shortfall": shortfall2_1yen,
    }


if __name__ == "__main__":
    print(verify())
    print()
    print(render(CONTRACT1, DEPOSITS1_MAIN, "材料1（端数は最終回・本当の不足2円）"))
    print()
    print(render(CONTRACT2, DEPOSITS2_MAIN, "材料2（端数は初回・本当の不足3円）"))
