# -*- coding: utf-8 -*-
"""集めた記事に日本語の要約を付ける。

要約するのは「お知らせ」だけ。モデルが出たことは名前と件数で足りるので
LLMに回さない。実測（2026-08-04）でHuggingFace系はmajor率63〜89%あり、
そちらまで要約すると費用も待ち時間も跳ね上がるわりに読む価値が増えない。

要約は派生データで、失敗しても記事そのものは残る。だからこの層の例外は
上へ投げず、書けたぶんだけ書いて次の実行に回す。メール送信の邪魔をしない。
"""
from __future__ import annotations

import json
import re
import urllib.request

# 「読む」もの＝1件ずつ要約する。「見る」もの（モデルの公開）は対象外。
ANNOUNCEMENT_TYPES = frozenset({"rss", "anthropic_news"})

# MarketWatch 側で実績のある順。上から試して、通ったものを使う。
MODELS = ("gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.5-flash-lite")
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TIMEOUT = 60

BATCH_SIZE = 8
# 3行×おおむね40字。超えた分は切る（長い要約は一覧で読まれない）。
MAX_SUMMARY_CHARS = 180
# 暴走したときに課金を焼かないための歯止め。残りは次の実行で拾う。
MAX_ITEMS_PER_RUN = 60

_FENCE_RE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.S)
_ARRAY_RE = re.compile(r"\[.*\]", re.S)


def needs_summary(item: dict, source_types: dict[str, str]) -> bool:
    """まだ要約が無い「お知らせ」なら True。

    source_types は sources.yml から作った {id: type}。そこに無いソース
    （設定から消えた等）は型が分からないので触らない。
    """
    if item.get("summary_ja"):
        return False
    # 説明が空の記事は要約しない。題名しか材料が無いと、埋めようとして
    # 事実でないことを書く（実測＝Sakana の「日本語特化のLLM API」を
    # 「外部サービス連携の仕組み」と書いた）。題名だけ出すほうが正しい。
    if not (item.get("summary") or "").strip():
        return False
    return source_types.get(item.get("source_id", "")) in ANNOUNCEMENT_TYPES


def build_prompt(items: list[dict]) -> str:
    lines = [
        "以下はAI関連の公式発表です。それぞれ日本語で3行の要約を書いてください。",
        "",
        "【要件】",
        "- 最大3行。1行はおおむね40字以内",
        "- 1行目は必ず「何が起きたか」。2行目以降は具体的なことだけを書く",
        "- 具体的なこと＝数字・固有名詞・前との違い・できるようになったこと",
        "- 読者はプログラマーではない会社員。専門用語は短い日本語に言い換える",
        "- 与えられた題名と説明だけを使う。書かれていないことを足さない",
        "- 分からない部分は書かない。行を埋めるために推測しない",
        "",
        "【最重要】書くことが無ければ2行、それも無ければ1行でよい。",
        "誰にでも当てはまる行で埋めないこと。次のような行は書いてはいけない:",
        "-「〜に関係する人に影響」「〜する人に影響」（誰にでも当てはまる）",
        "-「注目される」「話題になりそう」（中身が無い）",
        "-「今後の展開が期待される」（何も言っていない）",
        "",
        "【出力形式】",
        "JSONの配列だけを返す。前後に説明文を付けない。",
        '[{"uid": "元のuid", "summary_ja": "1行目\\n2行目\\n3行目"}]',
        "",
        "【対象】",
    ]
    for item in items:
        lines.append(f"- uid: {item['uid']}")
        lines.append(f"  題名: {item.get('title', '')}")
        summary = (item.get("summary") or "").strip()
        lines.append(f"  説明: {summary or '(説明なし。題名だけから書ける範囲で書く)'}")
    return "\n".join(lines)


def parse_response(text: str, asked_uids: set[str]) -> dict[str, str]:
    """応答から {uid: 要約} を取り出す。読めなければ空を返す。

    頼んでいないuidは捨てる。受け入れると別の記事に他人の要約が付く。
    """
    body = text.strip()
    fenced = _FENCE_RE.search(body)
    if fenced:
        body = fenced.group(1)
    else:
        array = _ARRAY_RE.search(body)
        if array:
            body = array.group(0)

    try:
        parsed = json.loads(body)
    except (ValueError, TypeError):
        return {}
    if not isinstance(parsed, list):
        return {}

    result: dict[str, str] = {}
    for entry in parsed:
        if not isinstance(entry, dict):
            continue
        uid = entry.get("uid")
        summary = entry.get("summary_ja")
        if uid not in asked_uids or not isinstance(summary, str):
            continue
        summary = summary.strip()
        if not summary:
            continue
        result[uid] = summary[:MAX_SUMMARY_CHARS]
    return result


def apply_summaries(items: list[dict], client) -> int:
    """items を直接書き換えて、要約を付けられた件数を返す。

    1バッチが失敗しても残りは続ける。全部捨てると、たまたま落ちた回の
    ぶんが次も同じところで落ちたときに永久に埋まらない。
    """
    targets = items[:MAX_ITEMS_PER_RUN]
    by_uid = {item["uid"]: item for item in targets}
    added = 0

    for start in range(0, len(targets), BATCH_SIZE):
        batch = targets[start:start + BATCH_SIZE]
        try:
            text = client(build_prompt(batch))
        except Exception as error:  # noqa: BLE001 - 1バッチの失敗で全部を捨てない
            print(f"[要約] {len(batch)}件のバッチが失敗: {type(error).__name__}: {error}")
            continue
        for uid, summary in parse_response(text, {i["uid"] for i in batch}).items():
            by_uid[uid]["summary_ja"] = summary
            by_uid[uid]["summary_source"] = "gemini"
            added += 1
    return added


def gemini_client(api_key: str):
    """プロンプトを渡すと本文を返す呼び出し口。ネットワークに触るのはここだけ。"""
    def call(prompt: str) -> str:
        errors = []
        for model in MODELS:
            try:
                return _post(model, api_key, prompt)
            except Exception as error:  # noqa: BLE001 - 次のモデルで試す
                errors.append(f"{model}: {type(error).__name__}")
        raise RuntimeError("Gemini が全モデルで失敗: " + " / ".join(errors))
    return call


def _post(model: str, api_key: str, prompt: str) -> str:
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
    }).encode("utf-8")
    request = urllib.request.Request(
        ENDPOINT.format(model=model),
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
            "User-Agent": "ai-tsukaikata-tracker/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        body = json.loads(response.read())
    candidates = body.get("candidates") or []
    if not candidates:
        raise ValueError("候補が空")
    parts = candidates[0].get("content", {}).get("parts") or []
    return "".join(part.get("text", "") for part in parts)
