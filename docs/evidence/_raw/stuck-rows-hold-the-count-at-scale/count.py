"""返りの中から報告された件数を取り、真値（資料が「（取得できませんでした）」の行数）と機械照合する。"""
import re
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "out"

TRUE_COUNT = {30: 11, 90: 31}


def extract_count(text: str) -> int | None:
    """最終的な結論の件数を取る。自己訂正があれば訂正後の数を優先する。"""
    corrections = re.findall(r"正しくは\s*(\d+)\s*件", text)
    if corrections:
        return int(corrections[-1])
    matches = re.findall(r"(\d+)\s*件", text)
    return int(matches[0]) if matches else None


def main():
    scales = (30, 90)
    variants = ("open", "fixed")
    rounds = (1, 2)
    reps = (1, 2, 3)

    print("| 版 | 規模 | 正解 | round1 (3回) | round2 (3回) | 合計 |")
    print("|---|---|---|---|---|---|")
    summary = {}
    for variant in variants:
        for n in scales:
            true_n = TRUE_COUNT[n]
            round_results = {}
            for rnd in rounds:
                results = []
                for rep in reps:
                    path = OUT / f"{variant}_day{n:02d}_round{rnd}_rep{rep}.txt"
                    text = path.read_text(encoding="utf-8")
                    reported = extract_count(text)
                    ok = reported == true_n
                    results.append((rep, reported, ok))
                round_results[rnd] = results
            all_results = round_results[1] + round_results[2]
            hits = sum(1 for _, _, ok in all_results if ok)
            summary[(variant, n)] = (hits, len(all_results), round_results)
            r1 = "/".join(str(r) for _, r, _ in round_results[1])
            r2 = "/".join(str(r) for _, r, _ in round_results[2])
            print(f"| {variant} | {n}日 | {true_n} | {r1} | {r2} | {hits}/{len(all_results)} |")

    print()
    print("=== 詳細 ===")
    for (variant, n), (hits, total, round_results) in summary.items():
        print(f"\n--- {variant} / {n}日 (正解{TRUE_COUNT[n]}) ---")
        for rnd in rounds:
            for rep, reported, ok in round_results[rnd]:
                mark = "OK" if ok else "★ずれ"
                print(f"  round{rnd} rep{rep}: 報告={reported} {mark}")
        print(f"  合計: {hits}/{total}")


if __name__ == "__main__":
    main()
