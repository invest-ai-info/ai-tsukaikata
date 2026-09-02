# -*- coding: utf-8 -*-
"""sources.yml を読み、各ソースから Update を取得する。ネットワークに触る唯一の層。

bot ブロックを迂回するための User-Agent 偽装はしない。403 を返すソースは
別ルートを使うか追わない。
"""
from __future__ import annotations

import json
import re
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import yaml

from .models import Update, make_uid

USER_AGENT = "ai-tsukaikata-tracker/1.0"
TIMEOUT = 20
MAX_ENTRIES = 30
HF_API = "https://huggingface.co/api/models"
OPENROUTER_API = "https://openrouter.ai/api/v1/models"
ANTHROPIC_SITE_BASE = "https://www.anthropic.com"
ANTHROPIC_NEWS_BASE = ANTHROPIC_SITE_BASE + "/news/"


def load_sources(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("sources", [])


def _http_get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        return response.read()


def _to_utc(value: str) -> datetime | None:
    """RFC822 と ISO8601 の両方を受け付けて UTC に正規化する。"""
    if not value:
        return None
    parsed = None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        parsed = None
    if parsed is None:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_feed(source: dict, raw: bytes) -> list[Update]:
    """RSS / Atom のバイト列を Update のリストにする。"""
    feed = feedparser.parse(raw)
    updates = []
    for entry in feed.entries[:MAX_ENTRIES]:
        published = _to_utc(entry.get("published") or entry.get("updated") or "")
        link = entry.get("link", "")
        if published is None or not link:
            continue
        updates.append(Update(
            uid=make_uid(source["id"], entry.get("id") or link),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=(entry.get("title") or "").strip(),
            url=link,
            published=published,
            summary=entry.get("summary", "") or entry.get("description", ""),
        ))
    return updates


def parse_huggingface(source: dict, raw: bytes) -> list[Update]:
    """HuggingFace models API の JSON を Update のリストにする。"""
    models = json.loads(raw)
    updates = []
    for model in models[:MAX_ENTRIES]:
        model_id = model.get("modelId") or model.get("id") or ""
        created = _to_utc(model.get("createdAt", ""))
        if not model_id or created is None:
            continue
        updates.append(Update(
            uid=make_uid(source["id"], model_id),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=model_id,
            url=f"https://huggingface.co/{model_id}",
            published=created,
            summary=f"HuggingFace に新しいモデル {model_id} が公開されました。",
        ))
    return updates


def parse_openrouter(source: dict, raw: bytes) -> list[Update]:
    """OpenRouter models API の JSON を Update のリストにする。

    org には OpenRouter のベンダー接頭辞を入れる（xAI なら "x-ai"）。
    x.ai は403でbotブロックされ、HuggingFace の xai-org も更新が止まって
    いるため、Grok の新モデルを追える唯一の実測済みルート。

    created は他のソースと違い ISO 文字列ではなく Unix 秒。
    """
    models = json.loads(raw).get("data", [])
    prefix = f"{source['org']}/"
    matched = [m for m in models if str(m.get("id", "")).startswith(prefix)]
    matched.sort(key=lambda m: m.get("created") or 0, reverse=True)

    updates = []
    for model in matched[:MAX_ENTRIES]:
        model_id = model.get("id", "")
        created = model.get("created")
        if not model_id or not created:
            continue
        updates.append(Update(
            uid=make_uid(source["id"], model_id),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=model_id,
            url=f"https://openrouter.ai/{model_id}",
            published=datetime.fromtimestamp(created, tz=timezone.utc),
            summary=model.get("description") or "",
        ))
    return updates


# Anthropic 公式news は RSS を出していない（/rss.xml・/news/rss.xml とも404を実測）。
# ただしページ自体は素の User-Agent で 200 を返すので、埋め込みデータから拾う。
#
# ⚠️ CSSのクラス名では拾わないこと。実物は CSS Modules のハッシュ付き
# （PublicationList-module-scss-module__KxYrHG__date）で、ビルドのたびに変わる。
# クラス名を頼ると次のデプロイで静かに0件になる。記事データは Next.js の
# RSCペイロードに Sanity CMS のオブジェクトとして入っており、そちらは
# publishedOn / slug / title というアプリ側の名前なので、見た目の変更では動かない。
_RSC_CHUNK_RE = re.compile(r'self\.__next_f\.push\(\[\d+,("(?:[^"\\]|\\.)*")\]\)')

_JSON_STR = r'(?:[^"\\]|\\.)*'
_NEWS_ITEM_RE = re.compile(
    r'"publishedOn":"(?P<published>[^"]+)"'
    r',"slug":\{"_type":"slug","current":"(?P<slug>[^"]+)"\}'
    r'(?P<middle>.{0,4000}?)'
    rf'"title":"(?P<title>{_JSON_STR})"',
    re.S,
)
_SUMMARY_RE = re.compile(rf'"summary":"(?P<summary>{_JSON_STR})"')

# /news/ の外にある目玉発表は post として出てこない。2026-09-01 の
# 「Introducing Claude Fable 5.1 and Claude Mythos 5.1」は URL が
# /claude-fable-and-mythos-5-1 で、newsページ上では featuredGridLink という
# オブジェクトとして1回だけ現れた（date / subject / summary / title / url）。
# post だけ拾うと目玉発表ほど落ちる。
# ⚠️ 実物は {"_key":"73aded5a605c","_type":"featuredGridLink",...} と _type の前に
# _key が付く。先頭の波括弧に _type を密着させると0件になる（2026-09-02 に実際に踏んだ）。
# フィールドの並び順に依存しないよう「入れ子の無いオブジェクトで、本体のどこかに
# _type=featuredGridLink があるもの」を切り出してから、フィールドを個別に拾う。
_GRID_LINK_RE = re.compile(
    rf'\{{(?P<body>(?:"{_JSON_STR}"|[^{{}}"])*?"_type":"featuredGridLink"'
    rf'(?:"{_JSON_STR}"|[^{{}}"])*)\}}'
)
_GRID_FIELD_RES = {
    name: re.compile(rf'"{name}":"(?P<value>{_JSON_STR})"')
    for name in ("date", "title", "url", "summary")
}


def _json_unescape(text: str) -> str:
    """JSON文字列としての復号。壊れていたら元をそのまま返す。"""
    try:
        return json.loads(f'"{text}"')
    except ValueError:
        return text


def _grid_link_key_and_url(url: str) -> tuple[str, str] | None:
    """featuredGridLink の url から（重複判定キー, 絶対URL）を作る。

    /news/<slug> なら post と同じ slug をキーにして、同じ記事が両方に
    出たときに畳めるようにする。それ以外はパス全体がキー。
    サイト外へのリンクは対象外（None）。
    """
    if url.startswith(ANTHROPIC_SITE_BASE):
        url = url[len(ANTHROPIC_SITE_BASE):]
    if not url.startswith("/"):
        return None
    path = url.split("?", 1)[0].split("#", 1)[0].strip("/")
    if not path:
        return None
    key = path[len("news/"):] if path.startswith("news/") else path
    return key, f"{ANTHROPIC_SITE_BASE}/{path}"


def _grid_link_field(body: str, name: str) -> str:
    found = _GRID_FIELD_RES[name].search(body)
    return _json_unescape(found.group("value")).strip() if found else ""


def parse_anthropic_news(source: dict, raw: bytes) -> list[Update]:
    """公式newsページの埋め込みデータを Update のリストにする。

    1件も取れないときは例外を投げる。空リストを返すと「取得はできたが
    中身が無い」と区別がつかず、静かに0件を返し続ける壊れ方になるため。
    呼び出し側（fetch_source）が握って死活記録に落とす。
    """
    text = raw.decode("utf-8", "replace")
    parts = []
    for chunk in _RSC_CHUNK_RE.findall(text):
        try:
            parts.append(json.loads(chunk))
        except ValueError:
            continue  # 1チャンクの破損で全部を捨てない
    if not parts:
        raise ValueError("埋め込みデータが見つからない（サイト構造の変更を疑う）")

    payload = "".join(parts)
    # key -> (published, title, summary, url)
    items: dict[str, tuple[datetime, str, str, str]] = {}
    for match in _NEWS_ITEM_RE.finditer(payload):
        published = _to_utc(match.group("published"))
        slug = match.group("slug")
        title = _json_unescape(match.group("title")).strip()
        if published is None or not slug or not title:
            continue
        found = _SUMMARY_RE.search(match.group("middle"))
        summary = _json_unescape(found.group("summary")) if found else ""
        # 同じ記事が「注目」と一覧の両方に入るので重複する。先勝ちで一意にする。
        items.setdefault(slug, (published, title, summary, f"{ANTHROPIC_NEWS_BASE}{slug}"))

    for match in _GRID_LINK_RE.finditer(payload):
        body = match.group("body")
        published = _to_utc(_grid_link_field(body, "date"))
        title = _grid_link_field(body, "title")
        resolved = _grid_link_key_and_url(_grid_link_field(body, "url"))
        if published is None or not title or resolved is None:
            continue
        key, url = resolved
        # post 側が先勝ち（同じ記事が /news/ の一覧と目玉枠の両方に出る）
        items.setdefault(key, (published, title, _grid_link_field(body, "summary"), url))

    if not items:
        raise ValueError("埋め込みデータはあるが記事が0件（サイト構造の変更を疑う）")

    updates = [
        Update(
            uid=make_uid(source["id"], slug),
            source_id=source["id"],
            vendor=source["vendor"],
            label=source["label"],
            title=title,
            url=url,
            published=published,
            summary=summary,
        )
        for slug, (published, title, summary, url) in items.items()
    ]
    updates.sort(key=lambda u: u.published, reverse=True)
    return updates[:MAX_ENTRIES]


def fetch_source(source: dict) -> tuple[list[Update], str | None]:
    """1ソースを取得する。(updates, error) を返し、例外は投げない。

    1ソースの失敗で全体を止めないため。失敗は呼び出し側が記録する。
    """
    try:
        if source["type"] == "anthropic_news":
            return parse_anthropic_news(source, _http_get(source["url"])), None
        if source["type"] == "openrouter":
            return parse_openrouter(source, _http_get(OPENROUTER_API)), None
        if source["type"] == "huggingface":
            url = (
                f"{HF_API}?author={source['org']}"
                f"&sort=createdAt&direction=-1&limit={MAX_ENTRIES}"
            )
            return parse_huggingface(source, _http_get(url)), None
        return parse_feed(source, _http_get(source["url"])), None
    except Exception as error:  # noqa: BLE001 - 全ソースを止めないため握る
        return [], f"{type(error).__name__}: {str(error)[:80]}"
