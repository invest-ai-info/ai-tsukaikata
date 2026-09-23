# -*- coding: utf-8 -*-
"""H22実測の機械採点。

各試行についてAIが返した数式を「対象セル・参照範囲(開始行・終了行)・
絞り込んだグループ(小計なら自グループ、総合計なら None=フィルタ無し)」に
機械的に書き起こし(このファイルの TRIALS)、それをスプレッドシートの
真値と突き合わせて判定する。

判定の規則(実行前に固定):
1. 自己参照チェック＝ 対象セルの行番号が、参照範囲(開始行〜終了行)に
   含まれていたら、範囲・条件式の中身に関わらずFAIL（Excelの循環参照検知は
   条件式の中身を見ず、参照範囲に自セルが含まれるかどうかだけで判定するため。
   SUMIFS等に除外条件を足しても、この構造的な自己参照は消えない）。
2. 自己参照が無ければ、範囲内でグループ条件に一致する行の値を実際に
   合計し、真値と一致するかを見る（範囲の端が1行ずれているだけで
   合計が変わる = 見た目は正しそうでも値が違う、という誤りも拾うため）。
3. 同じセルに複数の候補式が返ってきた場合は「最初に示された式」を使う。
   ただし「推奨」「おすすめ」「最も安全」等、AI自身が明示的に一方を
   優れていると述べたときだけ、その式を使う（本文の考察では他の案にも触れる）。
"""
from __future__ import annotations

# --- 材料の真値（gen_prompts.py と同じ計算） ---
MATERIAL_A = {
    "groups": {
        "渋谷教室": {"rows": (2, 5), "value": 102000},
        "新宿教室": {"rows": (6, 9), "value": 100000},
        "池袋教室": {"rows": (10, 12), "value": 84000},
    },
    "data_rows": (2, 12),
    "sub_rows": {13: "渋谷教室", 14: "新宿教室", 15: "池袋教室"},
    "total_row": 16,
    "grand_total": 286000,
}

MATERIAL_B = {
    "groups": {
        "豆・茶葉": {"rows": (2, 5), "value": 156000},
        "乳製品": {"rows": (6, 8), "value": 57000},
        "食材(パン・スイーツ用)": {"rows": (9, 12), "value": 48000},
    },
    "data_rows": (2, 12),
    "sub_rows": {13: "豆・茶葉", 14: "乳製品", 15: "食材(パン・スイーツ用)"},
    "total_row": 16,
    "grand_total": 261000,
}


def group_value_in_range(material: dict, group: str | None, r1: int, r2: int) -> tuple[int, bool]:
    """[r1,r2] の範囲内で、group条件(Noneなら無条件)に一致する値の合計と、
    その合計がその条件で本来拾うべき行を過不足なく拾えているか(=正しい値か)を返す。
    """
    if group is None:
        # 総合計の「生データを直接合計」パターン: データ行のみを対象にする
        d1, d2 = material["data_rows"]
        lo, hi = max(r1, d1), min(r2, d2)
        covered_rows = set(range(lo, hi + 1)) if lo <= hi else set()
        needed_rows = set(range(d1, d2 + 1))
        total = 0
        for g, info in material["groups"].items():
            gr1, gr2 = info["rows"]
            for row in range(gr1, gr2 + 1):
                if row in covered_rows:
                    total += info["value"] / (gr2 - gr1 + 1)
        return round(total), covered_rows == needed_rows
    else:
        gr1, gr2 = material["groups"][group]["rows"]
        needed_rows = set(range(gr1, gr2 + 1))
        covered_rows = set(range(max(r1, gr1), min(r2, gr2) + 1)) if r1 <= gr2 and r2 >= gr1 else set()
        per_item = material["groups"][group]["value"]
        # 按分せず、行単位で正しく拾えているかだけを見る(値は行数比例と仮定できないので
        # 「対象グループの行を過不足なく含むか」で判定する。値は含めば真値、欠ければ不一致とみなす)
        ok = covered_rows == needed_rows
        return (material["groups"][group]["value"] if ok else -1), ok


def eval_subtotal_row(material: dict, row: int, r1: int, r2: int) -> tuple[bool, str]:
    group = material["sub_rows"][row]
    if r1 <= row <= r2:
        return False, f"自己参照(範囲{r1}:{r2}が自分の{row}行目を含む)"
    val, ok = group_value_in_range(material, group, r1, r2)
    true_val = material["groups"][group]["value"]
    if not ok:
        return False, f"値が誤り(範囲{r1}:{r2}では{group}の行を過不足なく拾えない。真値{true_val})"
    return True, f"正しい({group}={true_val})"


def eval_total_row(material: dict, row: int, r1: int, r2: int, uses_subtotals: bool) -> tuple[bool, str]:
    if r1 <= row <= r2:
        return False, f"自己参照(範囲{r1}:{r2}が自分の{row}行目=総合計欄を含む)"
    if uses_subtotals:
        # SUM(小計セルの範囲) パターン。3つの小計セル(13-15)をちょうど含むか。
        sub_rows = set(material["sub_rows"].keys())
        covered = set(range(r1, r2 + 1))
        if covered != sub_rows:
            return False, f"小計セルの範囲が不正({r1}:{r2}、正しくは13:15)"
        return True, f"正しい(小計3件の合計={material['grand_total']})"
    else:
        val, ok = group_value_in_range(material, None, r1, r2)
        if not ok:
            return False, f"データ範囲が不正({r1}:{r2}。正しいデータ範囲は{material['data_rows']})"
        return True, f"正しい(生データ合計={material['grand_total']})"


# --- 各試行の返答から機械的に書き起こした式(採点の対象) ---
# 形式: "trial_id": {"material": M, "subtotal_range": (r1, r2), "total": None
#                     または {"range": (r1, r2), "uses_subtotals": bool}}
TRIALS = {
    # --- 材料A・1段 ---
    "A_1dan_1": {"material": MATERIAL_A, "subtotal_range": (1, 10**6)},          # SUMIF(A:A,...,C:C)
    "A_1dan_2": {"material": MATERIAL_A, "subtotal_range": (2, 12)},              # $A$2:$A$12
    "A_1dan_3": {"material": MATERIAL_A, "subtotal_range": (2, 12), "growing": True},  # $A$2:A12 growing
    "A_1dan_4": {"material": MATERIAL_A, "subtotal_range": (1, 10**6)},          # SUMIFS(C:C,...)
    "A_1dan_5": {"material": MATERIAL_A, "subtotal_range": (2, 100)},            # SUMPRODUCT $2:$100
    # --- 材料B・1段 ---
    "B_1dan_1": {"material": MATERIAL_B, "subtotal_range": (2, 12), "growing": True},  # $A$2:$A12 growing
    "B_1dan_2": {"material": MATERIAL_B, "subtotal_range": (2, 1000)},           # 推奨=SUMIFS(C2:C1000,...)
    "B_1dan_3": {"material": MATERIAL_B, "subtotal_range": (2, 12), "growing": True},
    "B_1dan_4": {"material": MATERIAL_B, "subtotal_range": (2, 11)},             # 固定(伸びない)。範囲が1行不足
    "B_1dan_5": {"material": MATERIAL_B, "subtotal_range": (2, 12)},
    # --- 材料A・2段 ---
    "A_2dan_1": {"material": MATERIAL_A, "subtotal_range": (2, 100),
                 "total": {"range": (2, 100), "uses_subtotals": False}},
    "A_2dan_2": {"material": MATERIAL_A, "subtotal_range": (2, 100),
                 "total": {"range": (13, 15), "uses_subtotals": True}},
    "A_2dan_3": {"material": MATERIAL_A, "subtotal_range": (1, 10**6),
                 "total": {"range": (13, 15), "uses_subtotals": True}},
    "A_2dan_4": {"material": MATERIAL_A, "subtotal_range": (1, 10**6),
                 "total": {"range": (13, 15), "uses_subtotals": True}},
    "A_2dan_5": {"material": MATERIAL_A, "subtotal_range": (1, 10**6),
                 "total": {"range": (13, 15), "uses_subtotals": True}},
    # --- 材料B・2段 ---
    "B_2dan_1": {"material": MATERIAL_B, "subtotal_range": (2, 14), "growing": True,
                 "total": {"range": (13, 15), "uses_subtotals": True}},
    "B_2dan_2": {"material": MATERIAL_B, "subtotal_range": (1, 10**6),
                 "total": {"range": (2, 11), "uses_subtotals": False}},
    "B_2dan_3": {"material": MATERIAL_B, "subtotal_range": (2, 12),
                 "total": {"range": (2, 12), "uses_subtotals": False}},
    "B_2dan_4": {"material": MATERIAL_B, "subtotal_range": (2, 15),
                 "total": {"range": (2, 11), "uses_subtotals": False}},
    "B_2dan_5": {"material": MATERIAL_B, "subtotal_range": (2, 12),
                 "total": {"range": (13, 15), "uses_subtotals": True}},
}


def grade():
    results = {}
    for trial_id, spec in TRIALS.items():
        material = spec["material"]
        r1, r2 = spec["subtotal_range"]
        sub_oks = []
        sub_reasons = []
        for row in sorted(material["sub_rows"]):
            if spec.get("growing"):
                # 「自分の1つ上まで」に伸びる形。行に応じて終端をrow-1に読み替える
                this_r2 = row - 1
                this_r1 = r1
            else:
                this_r1, this_r2 = r1, r2
            ok, reason = eval_subtotal_row(material, row, this_r1, this_r2)
            sub_oks.append(ok)
            sub_reasons.append(f"C{row}:{reason}")
        subtotal_ok = all(sub_oks)

        total_ok = None
        total_reason = ""
        if "total" in spec:
            tr1, tr2 = spec["total"]["range"]
            total_ok, total_reason = eval_total_row(
                material, material["total_row"], tr1, tr2, spec["total"]["uses_subtotals"]
            )

        results[trial_id] = {
            "subtotal_ok": subtotal_ok,
            "subtotal_detail": " / ".join(sub_reasons),
            "total_ok": total_ok,
            "total_detail": total_reason,
        }
    return results


if __name__ == "__main__":
    results = grade()
    for trial_id in sorted(results):
        r = results[trial_id]
        score = (1 if r["subtotal_ok"] else 0) + (1 if r["total_ok"] else 0 if r["total_ok"] is not None else 0)
        print(f"{trial_id}: 小計={'OK' if r['subtotal_ok'] else 'NG'}"
              + (f" / 総合計={'OK' if r['total_ok'] else 'NG'}" if r["total_ok"] is not None else "")
              )
        print(f"   {r['subtotal_detail']}")
        if r["total_ok"] is not None:
            print(f"   総合計: {r['total_detail']}")

    print("\n=== 集計 ===")
    dan1 = [t for t in results if "1dan" in t]
    dan2 = [t for t in results if "2dan" in t]
    y = sum(1 for t in dan1 if results[t]["subtotal_ok"])
    both = sum(1 for t in dan2 if results[t]["subtotal_ok"] and results[t]["total_ok"])
    print(f"1段条件・小計が直った数(Y) = {y} / {len(dan1)}")
    print(f"2段条件・両方直った数(X) = {both} / {len(dan2)}")
    print(f"反証条件: 2*X({2*both}) >= Y({y}) ? => {'棄却' if 2*both >= y else '生存'}")
