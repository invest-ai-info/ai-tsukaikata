"""評価レビューの返りから、報告された件数と正しい件数を機械照合する。"""
import re
from pathlib import Path

OUT = Path(__file__).parent / "out"

# 真値（資料が「（取得できませんでした）」になっている行の数。読者への到着順）
TRUE_COUNT = {"07": 3, "10": 4}


def extract_count(text: str) -> int | None:
    """最終的な結論の件数を取る。自己訂正があれば訂正後の数を優先する
    （例: 「4件です」の後に「正しくは5件です」と訂正した回）。"""
    corrections = re.findall(r"正しくは\s*(\d+)\s*件", text)
    if corrections:
        return int(corrections[-1])
    matches = re.findall(r"(\d+)\s*件", text)
    return int(matches[0]) if matches else None


def main() -> None:
    print("=== 開いた質問（review_*）===")
    hits = 0
    total = 0
    for variant in ("A", "B"):
        for day in ("07", "10"):
            reps = [""] + ["_rep2", "_rep3"]
            for suffix in reps:
                path = OUT / f"review_{variant}_day{day}{suffix}_reply.txt"
                if not path.exists():
                    continue
                text = path.read_text(encoding="utf-8")
                n = extract_count(text)
                true_n = TRUE_COUNT[day]
                ok = n == true_n
                hits += int(ok)
                total += 1
                print(f"  {variant} day{day}{suffix or '_rep1'}: 報告={n}件 正解={true_n}件 {'OK' if ok else '★ずれ'}")
    print(f"開いた質問: {hits}/{total}")

    print("=== 資料の中身を条件にした質問（review2_*）===")
    hits2 = 0
    total2 = 0
    for variant in ("A", "B"):
        for day in ("07", "10"):
            for rep in (1, 2, 3):
                path = OUT / f"review2_{variant}_day{day}_rep{rep}_reply.txt"
                if not path.exists():
                    continue
                text = path.read_text(encoding="utf-8")
                n = extract_count(text)
                true_n = TRUE_COUNT[day]
                ok = n == true_n
                hits2 += int(ok)
                total2 += 1
                print(f"  {variant} day{day}_rep{rep}: 報告={n}件 正解={true_n}件 {'OK' if ok else '★ずれ'}")
    print(f"資料の中身を条件にした質問: {hits2}/{total2}")


if __name__ == "__main__":
    main()
