"""言い直し方で出した2つの新しい指示文を、実際に試して確かめる。"""
import subprocess, sys, re
from pathlib import Path

SRC = Path("/home/user/ai-tsukaikata/docs/evidence/_raw/fresh-easy-row-throws-off-the-stuck-count/out")
sys.path.insert(0, str(SRC.parent))
from gen import arrival_line

SYSTEM_PROMPT = "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。ユーザーの依頼に文章だけで答えてください。"
OUT = Path(__file__).parent / "out"

def call_claude(message: str) -> str:
    proc = subprocess.run(
        ["claude", "--print", "--safe-mode", "--tools", "", "--system-prompt", SYSTEM_PROMPT],
        input=message, capture_output=True, text=True,
        cwd="/tmp/claude_test_empty_qp", timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout

# ===== テスト(a): 「止まった行も1件に数える」を足すと、1件で止まるか =====
# B_day05_state（既存データ）+ day6到着（前田・bad）を入力に、改良指示文で2回試す。
FIX_INSTRUCTION_A = """下は、毎朝1件ずつ処理している待ち行列です。未処理のものを1件だけ処理して、済の印を付けてください。処理した中身と、更新後の待ち行列の全文を書いてください。

印は「- [x] 」で始まる形に固定してください。ほかの行は1文字も変えないでください。

処理できなかった行は、待ち行列のいちばん下に移してください。できなかった理由を、その行の下に書いてください。

止まった行に「できなかった理由」を付けることも1件に数えてください。その日に2件以上は進めないでください。"""

day5_state = (SRC / "B_day05_state.txt").read_text(encoding="utf-8")
arrival6 = arrival_line(6)
state_with_arrival = day5_state + "\n" + arrival6

for rep in (1, 2):
    msg = FIX_INSTRUCTION_A + "\n\n" + state_with_arrival
    reply = call_claude(msg)
    (OUT / f"fixA_rep{rep}_sent.txt").write_text(msg, encoding="utf-8")
    (OUT / f"fixA_rep{rep}_reply.txt").write_text(reply, encoding="utf-8")
    print(f"fixA rep{rep}: len={len(reply)}")

# ===== テスト(b1): 「できなかった理由」に確認日を書かせる指示文 =====
FIX_INSTRUCTION_B = """下は、毎朝1件ずつ処理している待ち行列です。未処理のものを1件だけ処理して、済の印を付けてください。処理した中身と、更新後の待ち行列の全文を書いてください。

印は「- [x] 」で始まる形に固定してください。ほかの行は1文字も変えないでください。

処理できなかった行は「- [!] 」にして、次の行に「理由: ◯◯（確認日: 2026-11-07）」の形で書いてください。処理できなかった行を「- [x] 」にはしないでください。"""

day2_state = (SRC / "A_day02_state.txt").read_text(encoding="utf-8")  # 山本様が先頭の未処理
for rep in (1, 2, 3):
    msg = FIX_INSTRUCTION_B + "\n\n" + day2_state
    reply = call_claude(msg)
    (OUT / f"fixB_rep{rep}_sent.txt").write_text(msg, encoding="utf-8")
    (OUT / f"fixB_rep{rep}_reply.txt").write_text(reply, encoding="utf-8")
    print(f"fixB rep{rep}: len={len(reply)}")
