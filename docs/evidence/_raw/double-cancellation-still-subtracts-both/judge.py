# -*- coding: utf-8 -*-
"""生の返りから、各社名と同じ文・同じ行の中だけを見て判定する（台帳★237の教訓）。"""
import re
import glob

TRUTH = {
    "A": {"満月印刷": 4000, "北斎自動車": 0, "たんぽぽ保育園": 28000},
    "B": {"星空クリニック": 2500, "緑風工務店": 0, "朝日整体院": 33000},
}

NEGATION = re.compile(r"不足(なし|はありません|額なし|0円|0\s*円)|一致|✓|✅")
SHORTAGE = re.compile(r"不足")


def split_clauses(text):
    # 文・行の単位に割る（句点・改行・パイプ区切りの表の行も1行ずつ）
    parts = re.split(r"[。\n]", text)
    return [p for p in parts if p.strip()]


def judge_file(path, material):
    text = open(path, encoding="utf-8").read()
    clauses = split_clauses(text)
    truth = TRUTH[material]
    result = {}
    for name, true_amt in truth.items():
        name_clauses = [c for c in clauses if name in c]
        if true_amt == 0:
            false_positive = any(SHORTAGE.search(c) and not NEGATION.search(c) for c in name_clauses)
            result[name] = {"false_positive": false_positive, "clauses": name_clauses}
        else:
            hit = any(str(f"{true_amt:,}") in c.replace(",", f",") or str(true_amt) in c.replace(",", "") for c in name_clauses)
            # シンプルに「同じ節内に正しい金額の数字が出るか」を見る（カンマ有無を正規化）
            hit = any(str(true_amt) in c.replace(",", "") for c in name_clauses)
            result[name] = {"correct_amount_present": hit, "clauses": name_clauses}
    return result


def main():
    summary = {}
    for material in ("A", "B"):
        for kind, pattern in (("naive", f"raw/p0_{material}_*.txt"), ("explicit", f"raw/p1_{material}_*.txt")):
            for path in sorted(glob.glob(pattern)):
                r = judge_file(path, material)
                key = (material, kind)
                summary.setdefault(key, []).append((path, r))

    for key, items in summary.items():
        material, kind = key
        truth = TRUTH[material]
        test_name = [n for n, v in truth.items() if v > 0][0]
        control_name = [n for n, v in truth.items() if v == 0 and n != [k for k in truth if truth[k] == max(truth.values())][0]][0] if False else None
        print(f"=== 材料{material} / {kind} ===")
        for path, r in items:
            print(path, {k: v for k, v in r.items() if k != "clauses"})
        print()


if __name__ == "__main__":
    main()
