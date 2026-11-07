import re, sys
from pathlib import Path
SRC = Path("/home/user/ai-tsukaikata/docs/evidence/_raw/fresh-easy-row-throws-off-the-stuck-count/out")
sys.path.insert(0, str(SRC.parent))
from gen import BASELINE

row_re = re.compile(r"^-\s(\[[x! ]\])\s(\S+?)様")

def parse_blocks(text):
    lines = text.splitlines()
    blocks = {}
    order = []
    i = 0
    while i < len(lines):
        m = row_re.match(lines[i])
        if m:
            name = m.group(2)
            block_lines = [lines[i]]
            j = i + 1
            while j < len(lines) and lines[j].startswith("  "):
                block_lines.append(lines[j]); j += 1
            blocks[name] = "\n".join(block_lines)
            order.append(name)
            i = j
        else:
            i += 1
    return blocks, order

def load_state(variant, day):
    return (SRC / f"{variant}_day{day:02d}_state.txt").read_text(encoding="utf-8")

for variant in ("A", "B"):
    print(f"\n=== 変種{variant}：1日ごとに「変わってよいのは1行＋新着1行だけ」を確認 ===")
    prev_blocks, prev_order = parse_blocks(BASELINE)
    all_ok = True
    for day in range(1, 11):
        cur_text = load_state(variant, day)
        cur_blocks, cur_order = parse_blocks(cur_text)
        changed = [name for name in prev_blocks if name in cur_blocks and cur_blocks[name] != prev_blocks[name]]
        new_names = [name for name in cur_blocks if name not in prev_blocks]
        missing = [name for name in prev_blocks if name not in cur_blocks]
        ok = (len(changed) == 1 and len(new_names) == 1 and len(missing) == 0)
        status = "OK" if ok else "★異常"
        if not ok:
            all_ok = False
        print(f"  day{day:2d}: 変化した既存行={changed} 新着={new_names} 消失={missing}  [{status}]")
        prev_blocks, prev_order = cur_blocks, cur_order
    print(f"  => 10日間すべて正常: {all_ok}")
