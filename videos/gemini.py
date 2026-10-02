# -*- coding: utf-8 -*-
"""Gemini に YouTube 動画そのものを見せて、日本語の要約を作る。

- SDK は使わない（このプロジェクトの流儀＝urllib 直叩き。tracker/summarize.py と同じ）
- キーはヘッダ（x-goog-api-key）で渡す。URL に載せない
- 公開動画の URL を渡すだけ。無料枠は YouTube 動画が1日8時間ぶん（2026-10-02 公式ドキュメント）。
  だから**最初の30分だけ**を見せる（END_OFFSET）
- 呼び方は2通り試す。2026年の公式ドキュメントは interactions API に移っているが、
  tracker/summarize.py が使う generateContent も動いているので、駄目なら後者で取り直す
"""
from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone

MODELS = ("gemini-3.8-flash", "gemini-3.7-flash", "gemini-2.5-flash")
BASE = "https://generativelanguage.googleapis.com/v1beta"
TIMEOUT = 300           # 動画は読むのに時間がかかる
END_OFFSET = 1800       # 最初の30分だけ見る（秒）
USER_AGENT = "ai-tsukaikata-videos/1.0"

CATEGORIES = ("tech", "earn", "news")
SUMMARY_MAX = 80
FOR_WHOM_MAX = 60
CAUTION_MAX = 120


class ReplyError(Exception):
    """返事が決めた形の JSON になっていない。"""


class QuotaError(Exception):
    """枠を使い切った（429）。動画のせいではないので、失敗回数に数えない。"""


def build_prompt(video: dict, today: str | None = None) -> str:
    """today は「今日の日付」。Gemini は学習より後のモデル名・出来事を知らないので、
    渡さないと「架空の未来のモデル」と注意書きを付ける（2026-10-02 の初回実行で実際に起きた）。"""
    today = today or datetime.now(timezone.utc).date().isoformat()
    description = video.get("description", "").strip() or "（なし）"
    return f"""あなたは、AIで仕事を自動化したい日本の会社員向けサイトの編集者です。
渡したYouTube動画を見て、次のJSONだけを返してください。説明や前置きは書かないでください。

{{"is_ai": true, "category": "tech", "summary": ["1行目", "2行目", "3行目"], "for_whom": "こんな人向け", "caution": ""}}

決まり:
- is_ai: 動画の主題がAI（生成AI・AIツール・AIの使い方・AIで稼ぐ・AIのニュース）なら true。関係なければ false
- category: 次の3つから1つ
  - "tech" = AIの仕組みや使い方・設定・自動化の手順を解説している
  - "earn" = AIを使ってお金を稼ぐ方法（副業・仕事の受注・販売・収益化）が主題
  - "news" = 新しいモデル・新機能・会社の発表など、AIの最新の出来事が主題
  （このチャンネルの普段の分類は "{video.get("default_category", "")}" です。動画の中身で決めてください）
- summary: 動画で実際に言っていることを、日本語の短い文で3つ。1つ{SUMMARY_MAX}字以内。
  動画に出てこない数字・名前・評価を足さない。「〜と説明している」「〜を紹介している」のように、
  誰の主張かが分かる書き方にする
- for_whom: どんな人に役立つかを日本語で1つ。{FOR_WHOM_MAX}字以内
- caution: 視聴者が気をつけるべき点を日本語で1つ。無ければ空文字 ""。{CAUTION_MAX}字以内。必ず書くのは次のとき:
  - 収入・売上の金額を示しているが、根拠（画面の明細など）が示されていない
  - 「誰でも簡単」「放置で稼げる」のように、手間やリスクを小さく見せている
  - 有料講座・コミュニティ・LINE登録などへ誘導している（下の概要欄も見ること）
  金額を書くときは「出演者の主張」であることが分かるように書く
- 動画が長いときは、最初の30分の内容だけで要約してよい
- 今日は {today} です。動画に出てくるAIのモデル名・製品名・出来事は、あなたが知らないものでも
  実在するものとして扱ってください。「架空」「未来の想定」「思考実験」のように書かない

動画の題: {video.get("title", "")}
チャンネル: {video.get("channel_name", "")}
概要欄:
{description}
"""


def parse_reply(text: str) -> dict:
    """返事から JSON を取り出して検査する。形が違えば ReplyError。"""
    match = re.search(r"\{.*\}", text or "", re.S)
    if not match:
        raise ReplyError("JSON がありません")
    try:
        data = json.loads(match.group(0))
    except json.JSONDecodeError as error:
        raise ReplyError(f"JSON として読めません（{error}）") from error
    if not isinstance(data, dict):
        raise ReplyError("JSON がオブジェクトではありません")

    is_ai = data.get("is_ai")
    if not isinstance(is_ai, bool):
        raise ReplyError("is_ai が true / false ではありません")
    if not is_ai:
        return {"is_ai": False}

    category = data.get("category")
    if category not in CATEGORIES:
        raise ReplyError(f"category が想定外です（{category!r}）")
    summary = data.get("summary")
    if not isinstance(summary, list):
        raise ReplyError("summary が一覧ではありません")
    lines = [str(line).strip()[:SUMMARY_MAX] for line in summary if str(line).strip()]
    if not lines:
        raise ReplyError("summary が空です")
    for_whom = str(data.get("for_whom") or "").strip()[:FOR_WHOM_MAX]
    caution = str(data.get("caution") or "").strip()[:CAUTION_MAX]
    return {
        "is_ai": True,
        "category": category,
        "summary": lines[:3],
        "for_whom": for_whom,
        "caution": caution,
    }


def _post(url: str, api_key: str, payload: dict) -> dict:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
            "User-Agent": USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return json.loads(response.read())


def interactions_text(body: dict) -> str:
    """interactions API の返事から本文を取り出す（steps[].content[].text）。"""
    parts = []
    for step in body.get("steps") or []:
        if step.get("type") not in (None, "model_output"):
            continue
        for content in step.get("content") or []:
            if content.get("type") in (None, "text") and content.get("text"):
                parts.append(content["text"])
    if not parts and body.get("output_text"):
        parts.append(body["output_text"])
    return "".join(parts)


def generate_text(body: dict) -> str:
    """generateContent の返事から本文を取り出す（candidates[0].content.parts[].text）。"""
    candidates = body.get("candidates") or []
    if not candidates:
        return ""
    parts = candidates[0].get("content", {}).get("parts") or []
    return "".join(part.get("text", "") for part in parts)


def _via_interactions(model: str, api_key: str, video_url: str, prompt: str, post) -> str:
    body = post(f"{BASE}/interactions", api_key, {
        "model": model,
        "store": False,
        "input": [
            {"type": "video", "uri": video_url,
             "processing": {"type": "static", "end_offset": END_OFFSET}},
            {"type": "text", "text": prompt},
        ],
    })
    return interactions_text(body)


def _via_generate(model: str, api_key: str, video_url: str, prompt: str, post) -> str:
    body = post(f"{BASE}/models/{model}:generateContent", api_key, {
        "contents": [{"parts": [
            {"file_data": {"file_uri": video_url},
             "video_metadata": {"end_offset": f"{END_OFFSET}s"}},
            {"text": prompt},
        ]}],
    })
    return generate_text(body)


def client(api_key: str, post=_post):
    """動画（dict）を渡すと (本文, 使ったモデル) を返す呼び出し口。

    最初に本文が返ってきた呼び方で止める（形が悪くても別のモデルで取り直さない＝
    動画30分ぶんの枠を二重に使わないため。形の悪い返事は次の回にもう一度試す）。
    """
    def call(video: dict) -> tuple[str, str]:
        prompt = build_prompt(video)
        errors = []
        quota_hit = False
        for model in MODELS:
            for name, way in (("interactions", _via_interactions),
                              ("generateContent", _via_generate)):
                try:
                    text = way(model, api_key, video["url"], prompt, post)
                except Exception as error:  # noqa: BLE001 - 次の呼び方で試す
                    code = getattr(error, "code", "")
                    quota_hit = quota_hit or code == 429
                    errors.append(f"{model}/{name}: {type(error).__name__} {code}".strip())
                    continue
                if text.strip():
                    return text, model
                errors.append(f"{model}/{name}: 本文が空")
        if quota_hit:
            raise QuotaError("Gemini の枠を使い切りました: " + " / ".join(errors))
        raise RuntimeError("Gemini が全部失敗: " + " / ".join(errors))
    return call
