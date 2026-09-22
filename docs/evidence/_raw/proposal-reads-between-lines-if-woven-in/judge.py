import re

D1_KEYWORDS = re.compile(r"辞退|内定辞退")
D2_KEYWORDS = re.compile(r"隣のブース|比べ|比較|わかりやすいと言われ|分かりやすいと言われ")


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


SEP_RE = re.compile(r"^-{3,}\s*$", re.MULTILINE)


def extract_proposal_body(text):
    """前置きの注記（『含めていません』等）と、末尾の補足を除いた、
    実際に相手に貼る提案文の本体だけを取り出す。
    区切りは `---` の単独行。1個以上あれば、最初の直後〜最後の直前を本体とみなす。
    区切りが無い場合はテキスト全体を本体として扱う（安全側＝見逃しにくくする）。
    """
    seps = list(SEP_RE.finditer(text))
    if len(seps) >= 2:
        return text[seps[0].end():seps[-1].start()]
    if len(seps) == 1:
        return text[seps[0].end():]
    return text


def judge(text, pattern):
    body = extract_proposal_body(text)
    m = pattern.findall(body)
    return len(m) > 0, m


def report(label, path, pattern):
    runs = load_runs(path)
    hit = 0
    print(f"=== {label}: {len(runs)} runs ===")
    for i, r in enumerate(runs, 1):
        touched, matches = judge(r, pattern)
        if touched:
            hit += 1
        print(f"  run {i}: touched={touched} matches={matches[:3]}")
    print(f"  -> touched in {hit}/{len(runs)}\n")
    return hit, len(runs)


report("D1 no-hint / naive (control)", "runs/d1_nohint_naive.txt", D1_KEYWORDS)
report("D1 woven-hint / naive", "runs/d1_woven_naive_full.txt", D1_KEYWORDS)
report("D1 aside-hint / naive", "runs/d1_aside_naive_full.txt", D1_KEYWORDS)
report("D1 aside-hint / enhanced", "runs/v3_aside_enhanced.txt", D1_KEYWORDS)
report("D2 no-hint / naive (control)", "runs/d2_nohint_naive.txt", D2_KEYWORDS)
report("D2 woven-hint / naive", "runs/d2_woven_naive.txt", D2_KEYWORDS)
report("D2 aside-hint / naive", "runs/d2_aside_naive.txt", D2_KEYWORDS)
