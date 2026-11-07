import re
from pathlib import Path

SRC = Path("/home/user/ai-tsukaikata/docs/evidence/_raw/fresh-easy-row-throws-off-the-stuck-count/out")

def load_state(variant, day):
    return (SRC / f"{variant}_day{day:02d}_state.txt").read_text(encoding="utf-8")

def parse_blocks(text):
    """Return list of (name, mark, block_text) where block_text is the full 2-3 line block for that row."""
    lines = text.splitlines()
    blocks = []
    i = 0
    row_re = re.compile(r"^-\s(\[[x! ]\])\s(\S+?)様")
    while i < len(lines):
        m = row_re.match(lines[i])
        if m:
            mark = m.group(1)
            name = m.group(2)
            block_lines = [lines[i]]
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                block_lines.append(lines[j])
                j += 1
            blocks.append((name, mark, "\n".join(block_lines)))
            i = j
        else:
            i += 1
    return blocks

def main():
    for variant in ("A", "B"):
        print(f"\n===== 変種{variant}：10日間の連鎖で、確定済みの行が書き換わらないか =====")
        baseline_path = Path("/home/user/ai-tsukaikata/docs/evidence/_raw/fresh-easy-row-throws-off-the-stuck-count/out")
        prev_blocks = {}
        # day0 = baseline (from gen.py BASELINE, reconstruct via day01's unprocessed tail is unreliable; load from gen.py import instead)
        import sys
        sys.path.insert(0, str(SRC.parent))
        from gen import BASELINE
        prev_text = BASELINE
        prev_blocks = {name: (mark, block) for name, mark, block in parse_blocks(prev_text)}
        total_mismatches = 0
        total_checked_rows = 0
        row_count_report = []
        for day in range(1, 11):
            cur_text = load_state(variant, day)
            cur_blocks_list = parse_blocks(cur_text)
            cur_blocks = {name: (mark, block) for name, mark, block in cur_blocks_list}
            # 1) every row finalized (x or !) in prev day must still exist, unchanged, in current day
            mismatches_today = []
            for name, (mark, block) in prev_blocks.items():
                if mark in ("[x]", "[!]"):
                    if name not in cur_blocks:
                        mismatches_today.append((name, "行が消失"))
                        continue
                    cur_mark, cur_block = cur_blocks[name]
                    if cur_block != block:
                        mismatches_today.append((name, f"内容が変化: 旧={block!r} 新={cur_block!r}"))
                    total_checked_rows += 1
            total_mismatches += len(mismatches_today)
            # 2) row count: should grow by exactly 1 (new arrival) each day
            prev_n = len(prev_blocks)
            cur_n = len(cur_blocks_list)
            row_count_report.append((day, prev_n, cur_n, cur_n - prev_n))
            if mismatches_today:
                print(f"  day{day:2d}: ★不一致 {mismatches_today}")
            prev_blocks = cur_blocks
            prev_text = cur_text
        print(f"  確定済み行の突き合わせ件数: {total_checked_rows} / 不一致: {total_mismatches}")
        print(f"  行数の増分（前日比）: {[d[3] for d in row_count_report]}")

if __name__ == "__main__":
    main()
