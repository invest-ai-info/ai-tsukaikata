import sys
sys.path.insert(0, ".")
from run import call_claude
from pathlib import Path

REVIEW_INSTRUCTION_2 = """下は、問い合わせ対応の待ち行列です。週に1回だけ目を通すとして、資料の行が「（取得できませんでした）」になっている行だけを数えてください。資料がすでにあって未返信なだけの行や、済・保留の行は数えないでください。"""

for name, day in [("A", "07"), ("A", "10"), ("B", "07"), ("B", "10")]:
    state = Path(f"out/{name}_day{day}_state.txt").read_text(encoding="utf-8")
    msg = REVIEW_INSTRUCTION_2 + "\n\n" + state
    for rep in (1, 2, 3):
        reply = call_claude(msg)
        Path(f"out/review2_{name}_day{day}_rep{rep}_reply.txt").write_text(reply, encoding="utf-8")
        print(f"--- review2 {name} day{day} rep{rep} (先頭300字) ---")
        print(reply[:300])
        print()
