"""split_dayNN_* の返りから、抜き出された行の名前集合を取り、真値（資料なしの行の名前集合）と比較する。"""
import re
from pathlib import Path

OUT = Path("out")
NO_MATERIAL = "（取得できませんでした）"


def true_names(n: int) -> set[str]:
    text = (OUT / f"state_day{n:02d}.txt").read_text(encoding="utf-8")
    lines = text.splitlines()
    names = set()
    for i, line in enumerate(lines):
        if line.startswith("- [") and i + 1 < len(lines) and NO_MATERIAL in lines[i + 1]:
            m = re.search(r"([^\s\-\[\]!x ]+)様", line)
            if m:
                names.add(m.group(1))
    return names


def extracted_names(text: str) -> set[str]:
    names = set()
    for line in text.splitlines():
        for m in re.finditer(r"([^\s\-\[\]!x、。：:　]+)様", line):
            names.add(m.group(1))
    return names


def main():
    n = 90
    truth = true_names(n)
    print(f"真値: {len(truth)}件")
    for rnd in (1, 2):
        for rep in (1, 2, 3):
            path = OUT / f"split_day{n:02d}_round{rnd}_rep{rep}.txt"
            text = path.read_text(encoding="utf-8")
            got = extracted_names(text)
            missing = truth - got
            extra = got - truth
            ok = not missing and not extra
            print(
                f"round{rnd} rep{rep}: 抽出{len(got & truth)}/{len(truth)}件 "
                f"欠落={sorted(missing) or '無'} 誤混入={sorted(extra - truth) if (extra - truth) else '無'} "
                f"{'OK' if ok else '★要確認'}"
            )


if __name__ == "__main__":
    main()
