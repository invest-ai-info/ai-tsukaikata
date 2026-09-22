import re

SEP_RE = re.compile(r"^-{3,}\s*$", re.MULTILINE)


def extract_body(text):
    seps = list(SEP_RE.finditer(text))
    if len(seps) >= 2:
        return text[seps[0].end():seps[-1].start()]
    if len(seps) == 1:
        return text[seps[0].end():]
    return text


def load_runs(path):
    text = open(path, encoding="utf-8").read()
    blocks = re.split(r"---END---", text)
    runs = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        lines = b.splitlines()
        if lines and lines[0].startswith("==="):
            lines = lines[1:]
        runs.append("\n".join(lines).strip())
    return runs


# 「これまで／従来／現行／以前」等のあとに出てくる時刻・時間量が、
# 新しい値と異なる場合だけを「変更前の値を捏造した」と数える。
BEFORE_CONTEXT = re.compile(
    r"(これまで|従来|現行|以前|閉店時刻（|開店時刻（)[^。]{0,20}?(\d{1,2}(?::\d{2})?\s*時間?|24時間)"
)


def find_fabricated_values(text, new_values):
    body = extract_body(text)
    found = set()
    for m in BEFORE_CONTEXT.finditer(body):
        val = m.group(2)
        if val not in new_values:
            found.add(val)
    return found


def report(label, path, new_values, slots):
    runs = load_runs(path)
    total_fab = 0
    print(f"=== {label} ({slots}枠・{len(runs)}回) ===")
    for i, r in enumerate(runs, 1):
        vals = find_fabricated_values(r, new_values)
        n = min(len(vals), slots)
        total_fab += n
        print(f"  run {i}: fabricated={n} values={vals}")
    print(f"  -> 合計捏造個数 {total_fab}（満点 {slots * len(runs)}）\n")
    return total_fab


t1 = report("parking 1-blank", "runs/parking_1blank_full.txt", {"23時"}, 1)
t2 = report("gym 1-blank", "runs/gym_1blank_full.txt", {"22時"}, 1)
t3 = report("parking 2-blank", "runs/parking_2blank_full.txt", {"23時", "20時"}, 2)
t4 = report("gym 2-blank", "runs/gym_2blank_full.txt", {"22時", "8時"}, 2)

one_blank_total = t1 + t2
two_blank_total = t3 + t4
print(f"1か所条件 合計捏造個数（満点10）＝ {one_blank_total}")
print(f"2か所条件 合計捏造個数（満点20）＝ {two_blank_total}")
print(f"反証条件＝2か所の合計が、1か所の合計×2（={one_blank_total*2}）を下回るなら棄却")
print("→ 棄却" if two_blank_total < one_blank_total * 2 else "→ 支持（棄却されない）")
