import re, sys
from pathlib import Path
SRC = Path("/home/user/ai-tsukaikata/docs/evidence/_raw/fresh-easy-row-throws-off-the-stuck-count/out")
sys.path.insert(0, str(SRC.parent))
from gen import BASELINE

row_re = re.compile(r"^-\s(\[[x! ]\])\s(\S+?)様")

def parse_marks(text):
    marks = {}
    for line in text.splitlines():
        m = row_re.match(line)
        if m:
            marks[m.group(2)] = m.group(1)
    return marks

def load_state(variant, day):
    return (SRC / f"{variant}_day{day:02d}_state.txt").read_text(encoding="utf-8")

for variant in ("A", "B"):
    print(f"\n=== {variant} ===")
    prev = parse_marks(BASELINE)
    discovery = {}
    for day in range(1, 11):
        cur = parse_marks(load_state(variant, day))
        for name, mark in cur.items():
            if mark in ("[x]", "[!]") and prev.get(name) != mark and name not in discovery:
                discovery[name] = (day, mark)
        prev = cur
    for name, (day, mark) in discovery.items():
        print(f"  {name}様: day{day} に確定 ({mark})")
    # final pile order (positions) for blocked rows at day10
    final_text = load_state(variant, 10)
    lines = final_text.splitlines()
    order = []
    for line in lines:
        m = row_re.match(line)
        if m and m.group(1) == "[!]":
            order.append(m.group(2))
    print(f"  day10時点の[!]行の見た目の並び順: {order}")
