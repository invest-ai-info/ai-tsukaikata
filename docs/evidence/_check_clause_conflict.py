import re

RESPONSES = {
    "材料A・1回目": """第6条（支払条件）に基づくと、支払期限は検収完了日（2026年10月21日)から30日以内、つまり2026年11月20日です。なお、文書の末尾にある「特記事項」には、納品日（2026年10月12日）から45日後、つまり2026年11月26日を支払期限とする記載もあり、第6条の内容と一致していません。""",
    "材料A・2回目": """文書の末尾の「特記事項」には、納品日（2026年10月12日）から45日後に支払うと書かれており、これに従うと2026年11月26日が入金予定日になります。一方で第6条（支払条件）では、検収完了日（2026年10月21日）から30日以内に支払うとされており、この基準では2026年11月20日が期限になります。""",
    "材料A・3回目": """- 第6条（支払条件）：検収完了日（2026年10月21日）から30日以内 → 2026年11月20日\n- 特記事項：納品日（2026年10月12日）から45日後 → 2026年11月26日\n\nこの契約書の記載だけでは入金予定日を一つに決めることができません。""",
    "材料B・1回目": """第5条（支払条件）により、検収完了日（2026年11月3日）から20日以内に支払うとされているため、支払期限は2026年11月23日です。ただし、特記事項には納品日（2026年10月2日）から60日後、つまり2026年12月1日を支払期限とする記載もあり""",
    "材料B・2回目": """特記事項の記載に基づくと、納品日（2026年10月2日）から60日後が支払期限となり、2026年12月1日が入金予定日です。なお、第5条（支払条件）には、検収完了日（2026年11月3日）から20日以内、つまり2026年11月23日を期限とする別の記載もあります。""",
    "材料B・3回目": """- 第5条（支払条件）：検収完了日（2026年11月3日）から20日以内 → 2026年11月23日\n- 特記事項：納品日（2026年10月2日）から60日後 → 2026年12月1日\n\n入金予定日を一つに決めることができません。""",
}

# 材料ごとの候補日付→基準名
BASIS = {
    "材料A": {"2026年11月20日": "支払条件(検収完了基準)", "2026年11月26日": "特記事項(納品日基準)"},
    "材料B": {"2026年11月23日": "支払条件(検収完了基準)", "2026年12月1日": "特記事項(納品日基準)"},
}

UNDECIDED_MARK = "一つに決めることができません"


def classify(label: str, text: str) -> tuple[bool, str, str]:
    material = "材料A" if label.startswith("材料A") else "材料B"
    candidates = BASIS[material]
    noticed = all(date in text for date in candidates)
    if UNDECIDED_MARK in text:
        return noticed, "両方・未定", ""
    # 最初に出現する候補日付を「先頭基準」とする
    positions = {date: text.find(date) for date in candidates if date in text}
    first_date = min(positions, key=positions.get)
    return noticed, candidates[first_date], first_date


if __name__ == "__main__":
    tally = {"支払条件(検収完了基準)": 0, "特記事項(納品日基準)": 0, "両方・未定": 0}
    noticed_count = 0
    for label, text in RESPONSES.items():
        noticed, basis, date = classify(label, text)
        noticed_count += noticed
        tally[basis] += 1
        line = f"{label}: 気づき={noticed}  先頭基準={basis}"
        if date:
            line += f"  日付={date}"
        print(line)
    print()
    print("素朴に聞いた6回の内訳:")
    print(f"  気づき（両方の日付に触れた）: {noticed_count}/6")
    for basis, count in tally.items():
        print(f"  先頭基準＝{basis}: {count}回")
