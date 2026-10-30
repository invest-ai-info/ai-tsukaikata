import sys
from pathlib import Path
sys.path.insert(0, ".")
from run import call_claude
from prompts_split import PROMPT_SPLIT

OUT = Path("out")
n = 90
state = (OUT / f"state_day{n:02d}.txt").read_text(encoding="utf-8")
for rnd in (1, 2):
    for rep in (1, 2, 3):
        out_path = OUT / f"split_day{n:02d}_round{rnd}_rep{rep}.txt"
        msg = PROMPT_SPLIT + "\n\n" + state
        reply = call_claude(msg)
        out_path.write_text(reply, encoding="utf-8")
        print("done", out_path.name, len(reply))
