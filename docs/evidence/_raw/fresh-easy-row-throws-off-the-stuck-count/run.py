"""10日分を1日ずつ、claude CLIへ新規プロセスで投げて連鎖させる。"""
import subprocess
import sys
import re
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from gen import BASELINE, arrival_line
from prompts import INSTRUCTION_A, INSTRUCTION_B, SYSTEM_PROMPT

OUT = Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)


def call_claude(message: str) -> str:
    proc = subprocess.run(
        ["claude", "--print", "--safe-mode", "--tools", "", "--system-prompt", SYSTEM_PROMPT],
        input=message,
        capture_output=True,
        text=True,
        cwd="/tmp/claude_test_empty",
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"claude failed: {proc.stderr}")
    return proc.stdout


QUEUE_LINE_RE = re.compile(r"^- \[[x!  ]\]", re.MULTILINE)


def extract_queue(reply: str) -> str:
    """返りの中から、待ち行列の全文（- [x]/- [!]/- [ ] で始まる行とその資料行）だけを取り出す。"""
    lines = reply.splitlines()
    out_lines = []
    in_queue = False
    for line in lines:
        stripped = line.strip()
        if re.match(r"^-\s\[[x! ]\]", stripped):
            out_lines.append(line.rstrip())
            in_queue = True
        elif in_queue and (stripped.startswith("資料:") or stripped.startswith("理由:") or (line.startswith("  ") and stripped and not stripped.startswith("#"))):
            out_lines.append(line.rstrip())
        elif in_queue and stripped == "":
            # 空行はキュー終端の可能性があるが、資料行が続くこともあるので保留せず続行判定は次行で
            continue
        elif in_queue and not re.match(r"^-\s\[[x! ]\]", stripped):
            # キュー行でも資料行でもない本文に当たったら終端
            if not (stripped.startswith("資料") or stripped.startswith("理由")):
                break
    return "\n".join(out_lines)


def run_variant(name: str, instruction: str):
    print(f"=== 変種{name} ===")
    state = BASELINE
    log = []
    for day in range(1, 11):
        arrival = arrival_line(day)
        state_with_arrival = state + "\n" + arrival
        message = instruction + "\n\n" + state_with_arrival
        reply = call_claude(message)
        (OUT / f"{name}_day{day:02d}_sent.txt").write_text(message, encoding="utf-8")
        (OUT / f"{name}_day{day:02d}_reply.txt").write_text(reply, encoding="utf-8")
        new_state = extract_queue(reply)
        if not new_state.strip():
            print(f"  day{day}: 抽出失敗。生の返りを確認してください -> {name}_day{day:02d}_reply.txt")
            new_state = state_with_arrival  # フォールバック（記事には使わない。異常検知用）
        (OUT / f"{name}_day{day:02d}_state.txt").write_text(new_state, encoding="utf-8")
        lines = new_state.splitlines()
        done = sum(1 for l in lines if l.startswith("- [x]"))
        blocked = sum(1 for l in lines if l.startswith("- [!]"))
        pending = sum(1 for l in lines if l.startswith("- [ ]"))
        total = done + blocked + pending
        print(f"  day{day:2d}: 行数={len(lines)//2 if len(lines)%2==0 else '?'} 済={done} 止={blocked} 未={pending} 計マーク={total}")
        log.append({"day": day, "done": done, "blocked": blocked, "pending": pending})
        state = new_state
    (OUT / f"{name}_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("A", "both"):
        run_variant("A", INSTRUCTION_A)
    if which in ("B", "both"):
        run_variant("B", INSTRUCTION_B)
