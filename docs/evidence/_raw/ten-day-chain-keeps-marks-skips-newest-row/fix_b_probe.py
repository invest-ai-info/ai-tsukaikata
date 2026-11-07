"""確認日を入れたバージョンのday10状態で、同じ「新旧」の問いを3回試す。"""
import subprocess
from pathlib import Path

SRC = Path("/home/user/ai-tsukaikata/docs/evidence/_raw/fresh-easy-row-throws-off-the-stuck-count/out")
SYSTEM_PROMPT = "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。ユーザーの依頼に文章だけで答えてください。"
OUT = Path(__file__).parent / "out"

day10 = (SRC / "B_day10_state.txt").read_text(encoding="utf-8")

# 実際の発見日（B_day03/06/08のAI返りから）を確認日として追記。長谷川様は未着手のまま日付なし。
dated = day10.replace(
    "  できなかった理由: 資料欄に注文変更の可否に関する情報がなく（取得できませんでした）、回答の根拠がないため処理できませんでした。資料の再取得が必要です。",
    "  できなかった理由: 資料欄に注文変更の可否に関する情報がなく（取得できませんでした）、回答の根拠がないため処理できませんでした。資料の再取得が必要です。（確認日: 2026-11-08）",
).replace(
    "  できなかった理由: 資料欄に在庫の情報がなく（取得できませんでした）、回答の根拠がないため処理できませんでした。資料の再取得が必要です。",
    "  できなかった理由: 資料欄に在庫の情報がなく（取得できませんでした）、回答の根拠がないため処理できませんでした。資料の再取得が必要です。（確認日: 2026-11-06）",
).replace(
    "  できなかった理由: 資料欄に納期の情報がなく（取得できませんでした）、回答の根拠がないため処理できませんでした。資料の再取得が必要です。",
    "  できなかった理由: 資料欄に納期の情報がなく（取得できませんでした）、回答の根拠がないため処理できませんでした。資料の再取得が必要です。（確認日: 2026-11-03）",
)
assert dated.count("確認日: 2026-11-08") == 1
assert dated.count("確認日: 2026-11-06") == 1
assert dated.count("確認日: 2026-11-03") == 1
(OUT / "dated_day10_state.txt").write_text(dated, encoding="utf-8")

PROBE = """下は、問い合わせ対応の待ち行列の現在の状態です。今日は2026-11-10です。週に1回だけ目を通すとして、確認日が直近3日以内（2026-11-08〜2026-11-10）の、止まったままの行はどれですか。確認日が無い行は、別枠で教えてください。"""


def call_claude(message: str) -> str:
    proc = subprocess.run(
        ["claude", "--print", "--safe-mode", "--tools", "", "--system-prompt", SYSTEM_PROMPT],
        input=message, capture_output=True, text=True,
        cwd="/tmp/claude_test_empty_qp", timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr)
    return proc.stdout


for rep in (1, 2, 3):
    msg = PROBE + "\n\n" + dated
    reply = call_claude(msg)
    (OUT / f"datedprobe_rep{rep}_sent.txt").write_text(msg, encoding="utf-8")
    (OUT / f"datedprobe_rep{rep}_reply.txt").write_text(reply, encoding="utf-8")
    print(f"datedprobe rep{rep}: len={len(reply)}")
