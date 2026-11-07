import subprocess, sys
from pathlib import Path

SRC = Path("/home/user/ai-tsukaikata/docs/evidence/_raw/fresh-easy-row-throws-off-the-stuck-count/out")
SYSTEM_PROMPT = "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。ユーザーの依頼に文章だけで答えてください。"

PROBE = """下は、問い合わせ対応の待ち行列の現在の状態です。週に1回だけ目を通すとして、直近3日以内に新しく届いた行の中で、資料が取得できておらず、このままでは処理されない行はどれですか。該当するものを名前で教えてください。古くから止まっている行は、今回は聞いていません。"""

OUT = Path(__file__).parent / "probe_out"
OUT.mkdir(exist_ok=True)

def call_claude(message: str) -> str:
    proc = subprocess.run(
        ["claude", "--print", "--safe-mode", "--tools", "", "--system-prompt", SYSTEM_PROMPT],
        input=message, capture_output=True, text=True,
        cwd="/tmp/claude_test_empty_qp", timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout

for variant in ("A", "B"):
    state = (SRC / f"{variant}_day10_state.txt").read_text(encoding="utf-8")
    for rep in (1, 2, 3):
        msg = PROBE + "\n\n" + state
        reply = call_claude(msg)
        (OUT / f"{variant}_rep{rep}_sent.txt").write_text(msg, encoding="utf-8")
        (OUT / f"{variant}_rep{rep}_reply.txt").write_text(reply, encoding="utf-8")
        print(f"{variant} rep{rep} done, len={len(reply)}")
