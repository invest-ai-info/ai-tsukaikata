"""30日・90日の状態それぞれに、開いた質問／資料の中身を条件にした質問を
新規セッションで複数回投げる。2回転（round=1,2）× 3回ずつ。"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from prompts import PROMPT_OPEN, PROMPT_FIXED, SYSTEM_PROMPT

HERE = Path(__file__).parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
EMPTY_CWD = "/tmp/claude-0/-home-user-ai-tsukaikata/0efc3433-0f6e-5546-8df3-2b79ef2ff331/scratchpad/claude_test_empty"


def call_claude(message: str) -> str:
    proc = subprocess.run(
        ["claude", "--print", "--safe-mode", "--tools", "", "--system-prompt", SYSTEM_PROMPT],
        input=message,
        capture_output=True,
        text=True,
        cwd=EMPTY_CWD,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude failed: {proc.stderr}")
    return proc.stdout


def main():
    scales = (30, 90)
    prompt_variants = {"open": PROMPT_OPEN, "fixed": PROMPT_FIXED}
    rounds = (1, 2)
    reps = (1, 2, 3)

    for n in scales:
        state = (OUT / f"state_day{n:02d}.txt").read_text(encoding="utf-8")
        for pname, ptext in prompt_variants.items():
            for rnd in rounds:
                for rep in reps:
                    msg = ptext + "\n\n" + state
                    out_path = OUT / f"{pname}_day{n:02d}_round{rnd}_rep{rep}.txt"
                    if out_path.exists():
                        print(f"skip (exists): {out_path.name}")
                        continue
                    reply = call_claude(msg)
                    out_path.write_text(reply, encoding="utf-8")
                    print(f"done: {out_path.name} ({len(reply)} chars)")


if __name__ == "__main__":
    main()
