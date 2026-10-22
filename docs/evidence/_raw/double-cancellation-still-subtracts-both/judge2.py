# -*- coding: utf-8 -*-
"""各社名が出てくる文・行を全部拾い、「不足」に紐づく金額を文中から取り、
最後に出てきた値を最終結論として判定する（台帳★237＝同じ文の中だけを見る、を踏まえつつ
★238の「冒頭と結論が食い違う」パターンに対応するため、最後の値を正とする）。"""
import re
import glob

TRUTH = {
    "A": {"満月印刷": 4000, "北斎自動車": 0, "たんぽぽ保育園": 28000},
    "B": {"星空クリニック": 2500, "緑風工務店": 0, "朝日整体院": 33000},
}
NEGATION = re.compile(r"不足(なし|はありません|額なし|0円|0\s*円)|一致|✓|✅")
SHORTAGE = re.compile(r"不足")


def split_clauses(text):
    parts = re.split(r"[。\n]", text)
    return [p for p in parts if p.strip()]


def amounts_in(clause):
    return [int(x.replace(",", "")) for x in re.findall(r"([\d,]+)\s*円", clause)]


def judge_file(path, material):
    text = open(path, encoding="utf-8").read()
    clauses = split_clauses(text)
    truth = TRUTH[material]
    result = {}
    for name, true_amt in truth.items():
        name_clauses = [c for c in clauses if name in c]
        shortage_clauses = [c for c in name_clauses if SHORTAGE.search(c) or re.search(r"不足", c)]
        if true_amt == 0:
            fp_clauses = [c for c in name_clauses if SHORTAGE.search(c) and not NEGATION.search(c)]
            result[name] = {"false_positive": bool(fp_clauses), "evidence": fp_clauses or name_clauses[:1]}
        else:
            # 不足額を述べた節のうち、最後のものにある金額群から判定
            candidates = shortage_clauses or name_clauses
            last_vals = amounts_in(candidates[-1]) if candidates else []
            correct = true_amt in last_vals
            result[name] = {
                "final_correct": correct,
                "final_clause": candidates[-1] if candidates else None,
                "final_amounts": last_vals,
            }
    return result


def main():
    for material in ("A", "B"):
        for kind, pattern in (
            ("naive", f"raw/p0_{material}_*.txt"),
            ("explicit", f"raw/p1_{material}_*.txt"),
            ("light", f"raw/p2_{material}_*.txt"),
        ):
            print(f"=== {material} / {kind} ===")
            for path in sorted(glob.glob(pattern)):
                r = judge_file(path, material)
                print(path, r)
            print()


if __name__ == "__main__":
    main()
