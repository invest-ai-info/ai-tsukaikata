# -*- coding: utf-8 -*-
"""同じ課題を各社のモデルに投げて、機械判定で並べる。

作った理由（2026-09-05 オーナー指示「独自の方法で性能を比べたい」）＝
各社が自社で測った点数は、測り方も対象も違うので横に並べられない。
**同じ教材・同じ指示文・同じ判定コード**で測れば並べられる。

このファイルが守っていること:

- **SDKを使わない。**依存5個の流儀に合わせて urllib 直叩き（`tracker/fetch.py`・
  `tracker/summarize.py` と同じ）。鍵は環境変数から読み、**値は絶対に出力しない**。
- **道具を渡さない・システムプロンプトを足さない。**各社の素のAPIに、同じ本文だけを送る。
  片方だけ足すと、比べているのがモデルではなく足回りになる。
- **判定は機械。**目視で「良くなった」と書かない。判定コードは
  `docs/evidence/single-gap-goes-unnoticed.md` に載っているものと同じ規則。
- **返りは生のまま保存する。**要約すると「書いてあることを消す」ことがある。

⚠️ **満点どうしを並べても差は出ない。**題材は「いまのモデルが落としている課題」から選ぶ
（実測＝経費規程の判定は Claude が24/24・8/8で天井。欠落1個の見落としは6回中5回で余地がある）。

使い方:
    python tools/model_bench.py --vendor openai --model gpt-6-astra --runs 6
    python tools/model_bench.py --list-tasks
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

TIMEOUT = 300
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "evidence" / "_raw" / "bench"


# ---------------------------------------------------------------- 各社の窓口

@dataclass
class Reply:
    text: str
    input_tokens: int | None
    output_tokens: int | None
    raw: dict


def _post(url: str, payload: dict, headers: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    head = {"Content-Type": "application/json", **headers}
    request = urllib.request.Request(url, data=body, headers=head, method="POST")
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def _key(name: str) -> str:
    """環境変数から鍵を読む。無ければ落とす（黙って空文字で送ると認証エラーになり、
    「鍵が無い」ではなく「拒否された」という分かりにくい失敗になる）。"""
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"環境変数 {name} が設定されていません")
    return value


def ask_openai(model: str, prompt: str) -> Reply:
    data = _post(
        "https://api.openai.com/v1/responses",
        {"model": model, "input": prompt},
        {"Authorization": f"Bearer {_key('OPENAI_API_KEY')}"},
    )
    parts = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for chunk in item.get("content", []):
            if chunk.get("type") in ("output_text", "text"):
                parts.append(chunk.get("text", ""))
    usage = data.get("usage") or {}
    return Reply("".join(parts), usage.get("input_tokens"), usage.get("output_tokens"), data)


def ask_anthropic(model: str, prompt: str) -> Reply:
    data = _post(
        "https://api.anthropic.com/v1/messages",
        {"model": model, "max_tokens": 4096,
         "messages": [{"role": "user", "content": prompt}]},
        {"x-api-key": _key("ANTHROPIC_API_KEY"), "anthropic-version": "2023-06-01"},
    )
    parts = [c.get("text", "") for c in data.get("content", []) if c.get("type") == "text"]
    usage = data.get("usage") or {}
    return Reply("".join(parts), usage.get("input_tokens"), usage.get("output_tokens"), data)


def ask_gemini(model: str, prompt: str) -> Reply:
    # 鍵はヘッダで渡す＝URLクエリに載せない（summarize.py と同じ流儀）
    data = _post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        {"contents": [{"parts": [{"text": prompt}]}]},
        {"x-goog-api-key": _key("GEMINI_API_KEY")},
    )
    parts = []
    for cand in data.get("candidates", []):
        for chunk in cand.get("content", {}).get("parts", []):
            if "text" in chunk:
                parts.append(chunk["text"])
    usage = data.get("usageMetadata") or {}
    return Reply(
        "".join(parts),
        usage.get("promptTokenCount"),
        usage.get("candidatesTokenCount"),
        data,
    )


VENDORS = {"openai": ask_openai, "anthropic": ask_anthropic, "gemini": ask_gemini}


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


def run(vendor: str, model: str, task: Task, runs: int, out_dir: Path) -> list[dict]:
    ask = VENDORS[vendor]
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for index in range(runs):
        case = task.cases[index % len(task.cases)]
        started = time.time()
        try:
            reply = ask(model, case.prompt)
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", "replace")[:400]
            raise SystemExit(f"{vendor} が {error.code} を返しました: {detail}")
        seconds = time.time() - started
        verdict = judge(case, reply.text)
        stem = f"{task.task_id}_{vendor}_{model}_{case.case_id}_r{index + 1}"
        (out_dir / f"{stem}.txt").write_text(reply.text, encoding="utf-8")
        row = {
            "run": index + 1, "case": case.case_id, "missing": case.missing,
            "seconds": round(seconds, 1),
            "input_tokens": reply.input_tokens, "output_tokens": reply.output_tokens,
            **verdict,
        }
        results.append(row)
        mark = "◯" if verdict["抜けを名指しした"] else "✕"
        print(f"  {index + 1}/{runs} {case.case_id:<12} {mark} "
              f"({seconds:.0f}秒 / 出力{reply.output_tokens}トークン)")
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vendor", choices=sorted(VENDORS))
    parser.add_argument("--model")
    parser.add_argument("--task", default="single-gap", choices=sorted(TASKS))
    parser.add_argument("--runs", type=int, default=6)
    parser.add_argument("--list-tasks", action="store_true")
    args = parser.parse_args(argv)

    if args.list_tasks:
        for name, build in TASKS.items():
            task = build()
            print(f"{name}: {task.title}（{len(task.cases)}通り）")
        return 0
    if not args.vendor or not args.model:
        parser.error("--vendor と --model は必須です")

    task = TASKS[args.task]()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out_dir = OUT_DIR / f"{args.task}_{args.vendor}_{args.model}_{stamp}"

    print(f"課題: {task.title}")
    print(f"モデル: {args.vendor} / {args.model}　実行: {args.runs}回")
    results = run(args.vendor, args.model, task, args.runs, out_dir)

    named = sum(1 for r in results if r["抜けを名指しした"])
    silent = sum(1 for r in results if r["黙って埋めた"])
    summary = {
        "task": args.task, "vendor": args.vendor, "model": args.model,
        "runs": args.runs, "measured_at": stamp,
        "抜けを名指しした回数": named,
        "黙って埋めた回数": silent,
        "rows": results,
    }
    (out_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"\n抜けを名指しした: {named}/{args.runs}　黙って埋めた: {silent}/{args.runs}")
    print(f"生の返りと集計: {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
