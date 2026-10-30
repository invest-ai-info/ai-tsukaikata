"""out/ の生データから docs/evidence/stuck-rows-hold-the-count-at-scale.md を機械的に組み立てる。
手で転記すると「記事と同一文字列」の要件が崩れるので、プロンプト文字列は prompts.py から直接引く。
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")
from prompts import PROMPT_OPEN, PROMPT_FIXED, SYSTEM_PROMPT  # noqa: E402
from prompts_split import PROMPT_SPLIT  # noqa: E402

HERE = Path(__file__).parent
OUT = HERE / "out"
TRUE_COUNT = {30: 11, 90: 31}


def reply_block(variant: str, n: int, rnd: int, rep: int) -> str:
    path = OUT / f"{variant}_day{n:02d}_round{rnd}_rep{rep}.txt"
    text = path.read_text(encoding="utf-8").rstrip("\n")
    return f"#### round{rnd} rep{rep}\n\n```\n{text}\n```\n"


def main():
    lines = []
    lines.append("# 試した証拠 — stuck-rows-hold-the-count-at-scale\n")
    lines.append(
        "実測日: 2026-10-30。実測の相手＝`claude --print --safe-mode --tools \"\" "
        f"--system-prompt \"{SYSTEM_PROMPT}\"`"
        "（CLAUDE.md・skills・plugins・履歴を全部無効化した新規プロセス。呼び出しごとに完全に独立した"
        "プロセス。リポジトリの外の空のディレクトリで実行）。\n"
    )
    lines.append(
        "🔑 **続編の対象＝[`fresh-easy-row-throws-off-the-stuck-count`]"
        "(fresh-easy-row-throws-off-the-stuck-count.md)が明記した未測定事項**"
        "（「資料が永久に届かない行が、1か月・3か月でどこまで積み上がるかは測っていません」）。"
        "前作は10日間・詰んだ行3〜4件までしか実測していない。この記事は、同じ到着パターン"
        "（3日に1回・資料なし）を30日・90日まで機械的に延長し、詰んだ行が11件・31件に増えたときに、"
        "**前作と同じ2つの指示文**の正答率がどうなるかを見る。\n"
    )
    lines.append(
        "⚠️ **連鎖実行（claude CLIを1日ずつ繋ぐ）は、30日・90日ぶん再実行していない。**"
        "前作が10日間・0%の行方不明／印の破損で実証した「毎日1件ずつ処理し、処理できない行は資料なしの"
        "まま残る」という挙動を前提に、到着パターンをコード（`gen.py`）でそのまま延長した"
        "（決定的な生成。到着ログを機械で検算済み）。**実際にclaude CLIを呼んでいるのは、この生成済みの"
        "状態に対する「週次カウント」の質問そのもの**——本調査の主題はそこの正答率であって、連鎖の"
        "メカニズムは前作で確認済みのため再実験の対象にしていない。\n"
    )
    lines.append(
        "判定は機械照合。正しい件数（資料が「（取得できませんでした）」になっている行の数）は、"
        "生成時にコードで検算している（`gen.py` の `assert`）。生成・実行・判定のコードは "
        "`docs/evidence/_raw/stuck-rows-hold-the-count-at-scale/`"
        "（`gen.py` が状態生成、`prompts.py` が指示文、`run.py` が新規セッションでの質問の送信、"
        "`count.py` が集計）。生の送信・返りは同ディレクトリの `out/` に全回ぶんある。\n"
    )
    lines.append("---\n")

    # 教材
    lines.append("## 教材（架空データ）\n")
    lines.append(
        "⚠️ **仕込みのルール**＝3日に1回（3の倍数日）の到着は資料なし＝永久に処理不能。"
        "残りの到着（資料あり）のうち、4件に1件は「まだ未着手」のまま積み残る"
        "（到着が処理より速い、よくある現実の想定）。ベースラインは前作と同じ10行"
        "（済4・保留2・処理済みに回った3・最初から資料なしの山本様1）。\n"
    )
    for n in (30, 90):
        text = (OUT / f"state_day{n:02d}.txt").read_text(encoding="utf-8")
        stuck_true = TRUE_COUNT[n]
        lines.append(f"### {n}日後の状態（真の詰んだ行＝{stuck_true}件）\n")
        lines.append(f"```\n{text}\n```\n")

    lines.append("---\n")

    # 指示文1: 開いた質問
    lines.append("## 指示文1（記事の2番＝開いた質問）\n")
    lines.append("### 送った指示文（記事と同一文字列）\n")
    lines.append(f"```\n{PROMPT_OPEN}\n```\n")
    lines.append(
        "実際の送信は、この指示文の直後に改行2つを挟んで該当する日数の状態全文を続けた。\n"
    )
    for n in (30, 90):
        lines.append(f"### 返ってきたもの（生・{n}日後・2回転×3回＝6回）\n")
        for rnd in (1, 2):
            for rep in (1, 2, 3):
                lines.append(reply_block("open", n, rnd, rep))

    lines.append("### 照合（機械）\n")
    lines.append("```\n")
    import subprocess

    result = subprocess.run(["python3", "count.py"], cwd=str(HERE), capture_output=True, text=True)
    lines.append(result.stdout)
    lines.append("```\n")
    lines.append(
        "### 判定\n\n"
        "**落とした**（記事には「うまくいかないときの言い直し方」の対照として載せる）。"
        "30日後・90日後とも6/6ずれた。6回とも報告された件数は、真の詰んだ行数＋資料ありの未着手行数"
        "（30日後11+5=16件、90日後31+15=46件）に一致し、ゆらぎは無かった。前作（10日後・12回中7回ずれ）"
        "では「隣にいた無関係の行を巻き込む」という位置依存のゆらぎがあったが、規模が大きくなると"
        "位置に関係なく「資料ありの未着手行も含めて数える」という一貫した解釈に落ち着いた"
        "（複数の返りが、資料なしの行と資料ありの未着手行を別の見出しで正しく分けて提示したうえで、"
        "見出しの先頭で両方の合計を「今すぐ動かないと止まる件数」として報告していた）。\n"
    )

    lines.append("---\n")

    # 指示文2: 固定質問
    lines.append("## 指示文2（記事の4番＝資料の中身を条件にした質問）\n")
    lines.append("### 送った指示文（記事と同一文字列）\n")
    lines.append(f"```\n{PROMPT_FIXED}\n```\n")
    for n in (30, 90):
        lines.append(f"### 返ってきたもの（生・{n}日後・2回転×3回＝6回）\n")
        for rnd in (1, 2):
            for rep in (1, 2, 3):
                lines.append(reply_block("fixed", n, rnd, rep))

    lines.append(
        "### 判定\n\n"
        "**採用**。30日後（正解11件）・90日後（正解31件）とも6/6で正しい件数に合った。"
        "前作の10日後（12回中12回）と合わせて、詰んだ行が3件→4件→11件→31件まで増える4水準すべてで"
        "崩れていない。\n"
    )

    lines.append("---\n")

    # 指示文3: 詰んだ行だけ別出し
    lines.append("## 指示文3（記事の5番＝詰んだ行だけを別の一覧に抜き出す）\n")
    lines.append("### 送った指示文（記事と同一文字列）\n")
    lines.append(f"```\n{PROMPT_SPLIT}\n```\n")
    lines.append("### 返ってきたもの（生・90日後・2回転×3回＝6回）\n")
    for rnd in (1, 2):
        for rep in (1, 2, 3):
            path = OUT / f"split_day90_round{rnd}_rep{rep}.txt"
            text = path.read_text(encoding="utf-8").rstrip("\n")
            lines.append(f"#### round{rnd} rep{rep}\n\n```\n{text}\n```\n")

    lines.append("### 照合（機械）\n")
    lines.append("```\n")
    result = subprocess.run(["python3", "count_split.py"], cwd=str(HERE), capture_output=True, text=True)
    lines.append(result.stdout)
    lines.append("```\n")
    lines.append(
        "### 判定\n\n"
        "**採用**。90日後（詰んだ行31件／全99行）という、前作の約8倍の規模でも、6回とも"
        "31件を1件の欠落・1件の誤混入もなく抜き出した。書式（`- [!] ◯◯様：...` と次の行の`資料:`行）も"
        "6回とも保たれていた。\n"
    )

    lines.append("---\n")
    lines.append(
        "## この記事から出た教訓（`content/_lessons.md` へ）\n\n"
        "1. ★91（実測の相手を立てられない）とは別に、**カウント系の誤りの性質は規模で変わることがある**："
        "小さい規模では「ときどき外れる」（10日後12回中7回）、大きい規模では「毎回同じ分だけ外れる」"
        "（30/90日後6回中6回）。番人や検査を作るときは「エラー率」だけでなく「ズレの大きさが一定か」も"
        "見ると、原因（たまたまの巻き込み／定義の取り方そのもの）を区別できる。\n"
    )

    (HERE.parent.parent / "stuck-rows-hold-the-count-at-scale.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print("wrote", HERE.parent.parent / "stuck-rows-hold-the-count-at-scale.md")


if __name__ == "__main__":
    main()
