import re, glob

def first_verdict(text):
    first_line = text.strip().splitlines()[0]
    first_line = first_line.strip("*# ")
    if "不適切" in first_line:
        return "不適切"
    if "適切" in first_line:
        return "適切"
    return "不明:" + first_line

for label in ["A_v1", "A_v2", "B_v1", "B_v2"]:
    files = sorted(glob.glob(f"out_{label}_t*.txt"))
    verdicts = [first_verdict(open(f, encoding="utf-8").read()) for f in files]
    print(label, verdicts, "-> 適切:", verdicts.count("適切"), "/", len(verdicts))
