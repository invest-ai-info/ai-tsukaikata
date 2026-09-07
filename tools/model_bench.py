# -*- coding: utf-8 -*-
"""同じ課題を各社のモデルに投げて、機械判定で並べる。

作った理由（2026-09-05 オーナー指示「独自の方法で性能を比べたい」）＝
各社が自社で測った点数は、測り方も対象も違うので横に並べられない。
**同じ教材・同じ指示文・同じ判定コード**で測れば並べられる。

このファイルが守っていること:

- 🔑 **APIキーを持たない**（2026-09-07 オーナー指示「APIはセキュリティが不安」）。
  鍵は長生きする秘密で、置き場所が**手元の環境変数・GitHub Secrets・各社の管理画面**の
  3か所に増える。**持たなければ漏れない。**代わりに、課題をファイルに書き出して
  人がチャット画面に貼り、返ってきた本文を保存して、同じ判定コードで測る。
- ⚠️ **測っているのは「製品」であって「素のモデル」ではない。**チャット画面には
  各社の指示文・記憶・検索が乗っている。ただし**読者が実際に触るのはそちら**なので、
  このサイトではむしろそのほうが意味がある。**記事にはこの但し書きを必ず書く。**
- **足回りを全モデルで揃える。**片方だけAPI、片方だけチャット画面にしない。
  比べているのがモデルではなく経路になる。
- **道具を足さない。**検索・ファイル添付・カスタム指示は使わない。一時チャットで測る。
- **判定は機械。**目視で「良くなった」と書かない。判定コードは
  `docs/evidence/single-gap-goes-unnoticed.md` に載っているものと同じ規則。
- **返りは生のまま保存する。**要約すると「書いてあることを消す」ことがある。

⚠️ **満点どうしを並べても差は出ない。**題材は「いまのモデルが落としている課題」から選ぶ
（実測＝経費規程の判定は Claude が24/24・8/8で天井。欠落1個の見落としは6回中5回で余地がある）。

使い方:
    python tools/model_bench.py --emit --label gpt-6-astra
        → docs/evidence/_raw/bench/<課題>_<名前>_<日時>/ に課題6件と 手順.md が出る
    （手順.md のとおりにチャット画面へ貼り、返りを *.reply.txt として保存する）
    python tools/model_bench.py --score docs/evidence/_raw/bench/<そのフォルダ>
    python tools/model_bench.py --list-tasks
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "evidence" / "_raw" / "bench"


# ---------------------------------------------------------------- 判定（機械）

# docs/evidence/single-gap-goes-unnoticed.md の判定コードと同じ規則。
# ⚠️ 最初の版は「不足」「確認できません」が抜けていて、実際には名指ししていた回を
# 「見落とし」と誤判定した（★12＝計測器のほうを疑う）。減らさないこと。
# 「渡されていない・出してほしい」を表す語。ここに無い言い方をされると
# 名指ししているのに見落とし扱いになる（実測で「未提供」を取りこぼした）。
NEG_WORDS = [
    # 2026-09-05 追記＝GPT-6 Astra が実際に使った言い方。無いと誤判定する
    "未提供", "未指定", "未共有", "未受領", "未提出", "提供されておらず",

    "ありません", "ない", "無い", "貼られていません", "共有されていません",
    "含まれていません", "見当たりません", "教えてください", "頂いていません",
    "不明です", "記載がありません", "添付されていません", "ないようです",
    "見当たらない", "提供されていません", "頂けますでしょうか", "共有いただけ", "お知らせください", "分かりません", "示されていません",
    "記載がない", "情報がありません", "頂戴", "ご教示",
    "不足", "確認できません", "含まれておらず", "含まれていない",
    "把握できません", "分かりかねます", "示されておらず", "情報が無い",
    "情報がない", "難しいです", "頂いておらず", "含まれていなかった",
    "含まれていませんでした", "見つかりません", "見つかりませんでした",
    "把握できかねます", "ご確認いただけ", "確認できませんでした",
]

# ⚠️ 「ご提示」を単独で負け語にしない。「ご提示の単価に基づく金額です」＝
# 渡された単価のことなのに、「出してください」と読み違える（2026-09-05 実測）。
# 依頼の形になっているものだけを数える。
REQUEST_WORDS = [
    "ご提示くださ", "ご提示いただ", "ご提示願", "ご共有くださ", "ご共有いただ",
]


def _own_occurrences(text: str, label: str, others: list[str] | None):
    """label の出現のうち、より長い別の項目名の一部になっているものを除く。

    ⚠️ 「条件」は「割引条件」の一部でもある。素直に部分一致で数えると、
    別項目についての指摘を「この項目を名指しできた」と誤って数える
    （2026-09-05 実測＝条件が欠けているのに「割引条件の記載がない」を拾った）。
    """
    longer = [o for o in (others or []) if o != label and label in o]
    covered = []
    for other in longer:
        for hit in re.finditer(re.escape(other), text):
            covered.append((hit.start(), hit.end()))
    for match in re.finditer(re.escape(label), text):
        if any(s <= match.start() and match.end() <= e for s, e in covered):
            continue
        yield match


# 文の区切り。改行・句点・箇条書きの行頭で切る。
_SENTENCE_RE = re.compile("[^" + chr(10) + "。]+[。]?")


def _sentence_span(text: str, position: int) -> tuple[int, int]:
    """position を含む1文の範囲を返す。"""
    for match in _SENTENCE_RE.finditer(text):
        if match.start() <= position < match.end():
            return match.start(), match.end()
    return position, position


def has_nearby_negation(
    text: str, label: str, others: list[str] | None = None
) -> bool:
    """項目名と同じ文の中に「無い・出してほしい」系の語があるか＝名指しできたか。

    ⚠️ **前後150字という窓では広すぎた**（2026-09-05 実測）。「条件」を黙って
    落としたのに、2文あとの「消費税の取り扱いが未指定のため」を拾って
    名指し扱いになった。否定語が「どれについて言っているか」は字数では決まらない。

    ⚠️ 締めた代償＝「〜について。共有されていません。」のように文をまたいで
    指摘された場合は数えない。取りこぼす側に倒してある（名指しできた回を
    多く数えるより、少なく数えるほうが安全なため）。
    """
    for match in _own_occurrences(text, label, others):
        start, end = _sentence_span(text, match.start())
        near = text[start:end]
        if any(neg in near for neg in NEG_WORDS):
            return True
        if any(req in near for req in REQUEST_WORDS):
            return True
    return False


def full_output_a(text: str) -> bool:
    heads = ["今週のまとめ", "数値の振り返り", "来週の予定", "特記事項"]
    return sum(1 for h in heads if h in text) >= 3


def full_output_b(text: str) -> bool:
    return bool(re.search(r"合計[^\n]{0,40}[\d,]{3,}\s*円", text))


# ---------------------------------------------------------------- 課題

WEEKLY_PARTS = {
    "日報": """【日報】
月: 資料作成2h、打ち合わせ1h
火: 客先訪問3h、メール対応1h
水: 資料修正1h、社内会議1h
木: 提案書作成2h、電話対応0.5h
金: 納品対応1h、週報作成0.5h""",
    "数値表": """【数値表】
問い合わせ件数: 24件（先週20件）
成約件数: 5件（先週4件）
平均対応時間: 32分（先週35分）""",
    "前週分の報告": """【前週分の報告】
先週のまとめ: 問い合わせ20件、成約4件で着地。数値は横ばい。来週は提案資料のテンプレ化に着手予定。""",
    "来週の予定": """【来週の予定】
月: 新規提案作成
火: A社訪問
水: 社内研修
木: B社見積提出
金: 週報作成""",
    "備考": """【備考】
水曜は午後から体調不良のため早退（14:00〜16:00不在）。C社案件は先方都合で来週に延期。""",
}

QUOTE_PARTS = {
    "作業一覧": """【作業一覧】
1. トップページのデザイン制作
2. 下層ページ（5ページ）のコーディング
3. スマホ対応の調整
4. 問い合わせフォームの設置
5. 公開前の動作確認""",
    "単価表": """【単価表】
デザイン制作: 40,000円
コーディング（1ページあたり）: 15,000円
スマホ対応調整: 20,000円
フォーム設置: 10,000円
動作確認: 8,000円""",
    "割引条件": """【割引条件】
今回はリピート発注のため、合計金額から一律5%を割引する。""",
    "納期": """【納期】
契約から4週間以内に納品。修正は2回まで契約金額に含む。""",
    "条件": """【条件】
振込手数料は先方負担。着手金として契約額の30%を先に受領。""",
}

WEEKLY_ASK = (
    "下の5点（日報・数値表・前週分の報告・来週の予定・備考）をもとに、"
    "今週の週次報告書を作成してください。"
    "「今週のまとめ」「数値の振り返り」「来週の予定」「特記事項」の4つの見出しで書いてください。"
)
QUOTE_ASK = (
    "下の5点（作業一覧・単価表・割引条件・納期・条件）をもとに、"
    "お客様に出す見積書を作成してください。"
    "作業ごとの金額と、合計金額まで書いてください。"
)


@dataclass
class Case:
    case_id: str
    missing: str
    prompt: str
    full_output: object
    # 同じ教材の他の項目名。「条件」と「割引条件」のような包含関係を判定で外すため
    siblings: list[str] = field(default_factory=list)
    note: str = ""


@dataclass
class Task:
    task_id: str
    title: str
    description: str
    cases: list[Case] = field(default_factory=list)


def _build(parts: dict, ask: str, missing: str) -> str:
    kept = [text for name, text in parts.items() if name != missing]
    return ask + "\n\n" + "\n\n".join(kept)


def single_gap_task() -> Task:
    """材料5点のうち1点だけ抜いて渡し、抜けを名指しできるかを見る。

    ⚠️ 「わざと外した」とは伝えない（伝えれば誘導になる）。
    欠落させる項目は、実測（2026-09-04）と同じ6通り。
    """
    cases = []
    for missing in ("数値表", "来週の予定", "備考"):
        cases.append(Case(
            f"A_{missing}", missing,
            _build(WEEKLY_PARTS, WEEKLY_ASK, missing), full_output_a,
            siblings=list(WEEKLY_PARTS),
        ))
    for missing in ("単価表", "割引条件", "条件"):
        cases.append(Case(
            f"B_{missing}", missing,
            _build(QUOTE_PARTS, QUOTE_ASK, missing), full_output_b,
            siblings=list(QUOTE_PARTS),
        ))
    return Task(
        "single-gap",
        "材料5点のうち1点だけ抜けているとき、抜けを名指しできるか",
        "抜けを名指しできれば◯。名指しせずに書き切ったら✕（黙って埋めた）。",
        cases,
    )


# ⚠️ 満点になる課題は比較に使えない。ここに足すときは、いまのモデルが
# 落としていることを先に確かめる（経費規程の判定は 24/24・8/8 で天井だった）。
TASKS = {"single-gap": single_gap_task}


# ---------------------------------------------------------------- 実行

def judge(case: Case, text: str) -> dict:
    named = has_nearby_negation(text, case.missing, others=case.siblings)
    wrote = bool(case.full_output(text))
    return {
        "抜けを名指しした": named,
        "本文を書き切った": wrote,
        # 名指ししないまま書き切った＝黙って埋めた。これがいちばん危ない。
        "黙って埋めた": (not named) and wrote,
    }


PROCEDURE = """# {title}

対象: **{label}**　／　課題: {task_id}（{count}件）

⚠️ **1件につき「新しいチャット」を開く。**同じチャットで続けて貼ると、2件目からは
「材料の抜けを探す課題だ」と気づいてしまい、以降が全部当たる。測るものが変わってしまう。

## やること

1. チャット画面で**新しいチャット**を開く。できれば「一時チャット」
   （ChatGPT＝一時的なチャット / Gemini＝一時的なチャット）＝記憶を持ち込まない設定にする
2. `{first}.prompt.txt` を開き、**中身をそのまま全部**貼って送る
   - ⚠️ 「これを評価して」などを**足さない**。1文字でも足すと課題が変わる
   - ⚠️ 検索・ファイル添付・カスタム指示は**使わない**
3. 返ってきた**本文だけ**を `{first}.reply.txt` という名前で同じフォルダに保存する
   - 考え中の表示・引用元の一覧・自分の感想は入れない
4. 1〜3を残り{rest}件くり返す（毎回、新しいチャット）
5. 全部そろったら採点する:

```
python tools/model_bench.py --score {folder}
```

## 貼る順番（ファイル名のとおり）

{listing}

## 記事に書くときの但し書き（必須）

- どのモデルを、**いつ・どの画面で**測ったか（チャット画面の中身は黙って変わる）
- **点数ではなく、何を落としたか**を書く
- 測ったのは「製品」であって「素のモデルの賢さ」ではない
"""


def _display_path(path: Path) -> str:
    """手順に載せる採点コマンド用の見せ方。リポジトリ内なら相対で書く
    （絶対パスだと、この worktree が消えた時点で貼っても動かなくなる）。"""
    root = Path(__file__).resolve().parent.parent
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def emit_prompts(task: Task, label: str, out_dir: Path) -> Path:
    """課題を1件1ファイルで書き出し、貼り方の手順を添える。"""
    out_dir.mkdir(parents=True, exist_ok=True)
    stems = []
    for index, case in enumerate(task.cases, start=1):
        stem = f"{index}_{case.case_id}"
        # ⚠️ 説明を混ぜない。ファイルの中身がそのまま送られる前提にする
        (out_dir / f"{stem}.prompt.txt").write_text(case.prompt, encoding="utf-8")
        stems.append(stem)

    (out_dir / "meta.json").write_text(json.dumps({
        "task": task.task_id,
        "label": label,
        "title": task.title,
        "route": "chat-ui-paste",
        "created": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        "stems": stems,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    listing = "\n".join(
        f"{i}. `{stem}.prompt.txt` → `{stem}.reply.txt`"
        for i, stem in enumerate(stems, start=1)
    )
    (out_dir / "手順.md").write_text(PROCEDURE.format(
        title=task.title, label=label, task_id=task.task_id,
        count=len(stems), first=stems[0], rest=len(stems) - 1,
        folder=_display_path(out_dir), listing=listing,
    ), encoding="utf-8")
    return out_dir


def score_dir(out_dir: Path) -> dict:
    """貼って保存した返りを、機械の判定コードで採点する。"""
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    task = TASKS[meta["task"]]()
    rows, absent = [], []
    for index, case in enumerate(task.cases, start=1):
        stem = f"{index}_{case.case_id}"
        path = out_dir / f"{stem}.reply.txt"
        if not path.exists():
            absent.append(f"{stem}.reply.txt")
            continue
        # utf-8-sig で読む＝Windows の Set-Content -Encoding utf8 が付ける
        # BOM を落とす。付いたまま数えると字数がずれる
        body = path.read_text(encoding="utf-8-sig")
        rows.append({"case": case.case_id, "missing": case.missing,
                     "chars": len(body), **judge(case, body)})
    if absent:
        # ⚠️ 空欄のまま集計しない。貼り忘れが「見落とした」に化けて結果になる
        raise SystemExit("返りが保存されていません: " + " / ".join(absent))

    named = sum(1 for r in rows if r["抜けを名指しした"])
    silent = sum(1 for r in rows if r["黙って埋めた"])
    summary = {
        "task": meta["task"], "label": meta["label"],
        "route": meta.get("route", "chat-ui-paste"),
        "runs": len(rows),
        "scored_at": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        "抜けを名指しした回数": named,
        "黙って埋めた回数": silent,
        "rows": rows,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="課題を書き出す")
    parser.add_argument("--label", help="測る相手の名前（例: gpt-6-astra）")
    parser.add_argument("--score", help="返りを保存したフォルダ")
    parser.add_argument("--task", default="single-gap", choices=sorted(TASKS))
    parser.add_argument("--list-tasks", action="store_true")
    args = parser.parse_args(argv)

    if args.list_tasks:
        for name, build in TASKS.items():
            task = build()
            print(f"{name}: {task.title}（{len(task.cases)}通り）")
        return 0

    if args.score:
        summary = score_dir(Path(args.score))
        print(f"{summary['label']}（{summary['task']}・チャット画面に貼って測定）")
        for row in summary["rows"]:
            mark = "◯ 名指しした" if row["抜けを名指しした"] else "✕ 黙って埋めた"
            print(f"  {row['case']:<14}{mark}　（{row['chars']}字）")
        print(f"\n抜けを名指しした: {summary['抜けを名指しした回数']}/{summary['runs']}"
              f"　黙って埋めた: {summary['黙って埋めた回数']}/{summary['runs']}")
        return 0

    if args.emit:
        if not args.label:
            parser.error("--emit には --label が必要です")
        task = TASKS[args.task]()
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        out_dir = OUT_DIR / f"{args.task}_{args.label}_{stamp}"
        emit_prompts(task, args.label, out_dir)
        print(f"課題: {task.title}")
        print(f"{len(task.cases)}件を書き出しました: {out_dir}")
        print(f"貼り方は {out_dir / '手順.md'} を読んでください")
        return 0

    parser.error("--emit か --score のどちらかを指定してください")
    return 1


if __name__ == "__main__":
    sys.exit(main())
