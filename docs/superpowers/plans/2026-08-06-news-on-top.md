# AIアップデート欄（Phase 1）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** トラッカーが集めた `data/tracker/news.json` をトップページの「AIアップデート」欄（直近分）と `/news/` アーカイブ（全件・月別）として公開する。

**Architecture:** 新モジュール `src/news.py` が読み込み（news.json + sources.yml の型表）と整形（お知らせ／モデルの振り分け・ベンダー畳み・月別グルーピング）を担い、`render.py` はテンプレートに渡すだけ、`build.py` は配線だけ。読めない・壊れているときはビルドを止める（「全部通る or 何も出さない」を維持）。

**Tech Stack:** Python 3.12 / Jinja2 / PyYAML / pytest（既存と同じ。依存追加なし）

**設計書:** `docs/superpowers/specs/2026-08-06-warm-redesign-news-design.md` の④。配色は現行のまま（暖色化は Phase 2）。

**表示ルール（決定済み）:**
- お知らせ系（source type が `rss` / `anthropic_news`）＝1件ずつ。日付・ベンダー・major印・タイトル（原文リンク）・3行要約（`summary_ja`、無ければタイトルのみ）
- モデル系（それ以外）＝トップではラベル単位で畳む「Claude Code: 3件（最新: v2.1.223）」。アーカイブでは1件ずつタイトル行
- 型表に無い source_id はお知らせ扱い（隠さない側に倒す。現在は14ソース全部が型表にある）
- トップのお知らせは10件。モデルの畳み窓は「表示中お知らせの最古の published 以降」（お知らせ0件なら最新から14日）
- 日時は JST に変換して表示。鮮度の文言は「1日数回、自動更新」（「毎時」「即時」とは書かない）
- 「要約は自動生成」の注記を欄に明示

**Windows 注意:** pytest・ビルドの実行は `PYTHONUTF8=1` を付ける（コンソールが cp932）。

---

### Task 1: src/news.py — 読み込み層

**Files:**
- Create: `src/news.py`
- Create: `tests/test_news.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_news.py`:

```python
# -*- coding: utf-8 -*-
import json
from pathlib import Path

import pytest

from src import news

SOURCES_YML = """\
sources:
  - id: openai-news
    vendor: OpenAI
    label: OpenAI News
    type: rss
    url: https://example.com/rss
  - id: claude-code
    vendor: Anthropic
    label: Claude Code
    type: github_releases
    url: https://example.com/releases.atom
"""


def _item(uid="a1", source_id="openai-news", title="題", published="2026-08-04T19:00:00+00:00", **kwargs):
    base = {
        "uid": uid,
        "source_id": source_id,
        "title": title,
        "url": "https://example.com/post",
        "vendor": "OpenAI",
        "label": "OpenAI News",
        "importance": "minor",
        "published": published,
        "summary_ja": None,
    }
    base.update(kwargs)
    return base


def _write(tmp_path: Path, items) -> tuple[Path, Path]:
    news_path = tmp_path / "news.json"
    news_path.write_text(json.dumps({"items": items}, ensure_ascii=False), encoding="utf-8")
    sources_path = tmp_path / "sources.yml"
    sources_path.write_text(SOURCES_YML, encoding="utf-8")
    return news_path, sources_path


def test_load_source_types_maps_id_to_type(tmp_path):
    _, sources_path = _write(tmp_path, [])
    assert news.load_source_types(sources_path) == {
        "openai-news": "rss",
        "claude-code": "github_releases",
    }


def test_load_news_returns_items_new_to_old_in_jst(tmp_path):
    news_path, _ = _write(tmp_path, [
        _item(uid="old", published="2026-08-03T15:00:00+00:00"),
        _item(uid="new", published="2026-08-04T19:00:00+00:00"),
    ])
    items = news.load_news(news_path)
    assert [i.uid for i in items] == ["new", "old"]
    # 2026-08-04T19:00Z は JST では 8月5日 4:00
    assert items[0].published.date().isoformat() == "2026-08-05"


def test_load_news_missing_file_raises(tmp_path):
    with pytest.raises(news.NewsError):
        news.load_news(tmp_path / "nothing.json")


def test_load_news_broken_json_raises(tmp_path):
    path = tmp_path / "news.json"
    path.write_text("{壊れている", encoding="utf-8")
    with pytest.raises(news.NewsError):
        news.load_news(path)


def test_load_news_item_without_required_key_raises(tmp_path):
    item = _item()
    del item["published"]
    news_path, _ = _write(tmp_path, [item])
    with pytest.raises(news.NewsError):
        news.load_news(news_path)


def test_load_source_types_broken_yaml_raises(tmp_path):
    path = tmp_path / "sources.yml"
    path.write_text("sources: [壊れ", encoding="utf-8")
    with pytest.raises(news.NewsError):
        news.load_source_types(path)
```

- [ ] **Step 2: 落ちることを確認**

Run: `PYTHONUTF8=1 python -m pytest tests/test_news.py -q`
Expected: FAIL（`ModuleNotFoundError: No module named 'src.news'` 等）

- [ ] **Step 3: 最小実装**

`src/news.py`:

```python
# -*- coding: utf-8 -*-
"""data/tracker/news.json を読んで、トップの「AIアップデート」欄と
/news/ アーカイブに渡す形へ整える。

トラッカーの内部は知らない。知っているのは news.json の項目形式と
「お知らせは読む・モデルは見る」の粒度ルールだけ。読めないときは
NewsError を投げてビルドを止める（半端な欄を公開しないため）。
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

JST = timezone(timedelta(hours=9))

# 要約の対象と同じ線引き（tracker/summarize.py の ANNOUNCEMENT_TYPES と同値）。
# お知らせ＝1件ずつ読む。モデル＝出たことが分かればよいので畳む。
ANNOUNCEMENT_TYPES = frozenset({"rss", "anthropic_news"})

TOP_ANNOUNCEMENTS = 10
MODEL_WINDOW_FALLBACK = timedelta(days=14)

REQUIRED_KEYS = ("uid", "source_id", "title", "url", "importance", "published")


class NewsError(Exception):
    """news.json / sources.yml を読めない・形が違うときに投げる。"""


@dataclass(frozen=True)
class NewsItem:
    uid: str
    source_id: str
    title: str
    url: str
    vendor: str
    label: str
    importance: str
    published: datetime  # JST
    summary_ja: str | None


def load_source_types(path: Path) -> dict[str, str]:
    """sources.yml から {id: type} を作る。お知らせ/モデルの振り分けに使う。"""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        return {s["id"]: s["type"] for s in data["sources"]}
    except (OSError, yaml.YAMLError, KeyError, TypeError) as error:
        raise NewsError(f"{path}: 読めませんでした: {error}") from error


def load_news(path: Path) -> list[NewsItem]:
    """news.json を読み、新しい順の NewsItem にする。published は JST。"""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        raw_items = data["items"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as error:
        raise NewsError(f"{path}: 読めませんでした: {error}") from error

    items: list[NewsItem] = []
    for raw in raw_items:
        missing = [key for key in REQUIRED_KEYS if not raw.get(key)]
        if missing:
            raise NewsError(
                f"{path}: 項目に必須キーがありません: {', '.join(missing)}"
                f"（uid: {raw.get('uid', '?')}）"
            )
        published = datetime.fromisoformat(raw["published"]).astimezone(JST)
        items.append(NewsItem(
            uid=raw["uid"],
            source_id=raw["source_id"],
            title=raw["title"],
            url=raw["url"],
            vendor=raw.get("vendor") or raw.get("label") or raw["source_id"],
            label=raw.get("label") or raw.get("vendor") or raw["source_id"],
            importance=raw["importance"],
            published=published,
            summary_ja=raw.get("summary_ja") or None,
        ))
    items.sort(key=lambda item: (item.published, item.uid), reverse=True)
    return items
```

- [ ] **Step 4: 通ることを確認**

Run: `PYTHONUTF8=1 python -m pytest tests/test_news.py -q`
Expected: PASS（6 passed）

- [ ] **Step 5: コミット**

```bash
git add src/news.py tests/test_news.py
git commit -m "feat: news.json と sources.yml の読み込み層（src/news.py）"
```

---

### Task 2: src/news.py — 整形層（振り分け・畳み・月別）

**Files:**
- Modify: `src/news.py`（末尾に追記）
- Modify: `tests/test_news.py`（末尾に追記）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_news.py` に追記:

```python
SOURCE_TYPES = {"openai-news": "rss", "claude-code": "github_releases"}


def _loaded(tmp_path, items):
    news_path, _ = _write(tmp_path, items)
    return news.load_news(news_path)


def test_split_recent_separates_announcements_and_models(tmp_path):
    items = _loaded(tmp_path, [
        _item(uid="a", source_id="openai-news", published="2026-08-04T19:00:00+00:00",
              summary_ja="1行目\n2行目\n3行目"),
        _item(uid="m1", source_id="claude-code", title="v2.1.222",
              vendor="Anthropic", label="Claude Code",
              published="2026-08-04T22:00:00+00:00"),
        _item(uid="m2", source_id="claude-code", title="v2.1.223",
              vendor="Anthropic", label="Claude Code",
              published="2026-08-06T00:00:00+00:00"),
    ])
    top = news.split_recent(items, SOURCE_TYPES)
    assert [i.uid for i in top["announcements"]] == ["a"]
    assert len(top["model_groups"]) == 1
    group = top["model_groups"][0]
    assert group["label"] == "Claude Code"
    assert group["count"] == 2
    assert group["latest_title"] == "v2.1.223"


def test_split_recent_limits_announcements(tmp_path):
    items = _loaded(tmp_path, [
        _item(uid=f"a{i}", published=f"2026-08-{i:02d}T00:00:00+00:00")
        for i in range(1, 14)
    ])
    top = news.split_recent(items, SOURCE_TYPES, limit=10)
    assert len(top["announcements"]) == 10
    assert top["announcements"][0].uid == "a13"


def test_split_recent_model_window_follows_shown_announcements(tmp_path):
    # 表示中お知らせの最古（8/2）より前のモデル（8/1）は畳みに入らない
    items = _loaded(tmp_path, [
        _item(uid="a1", published="2026-08-02T00:00:00+00:00"),
        _item(uid="a2", published="2026-08-05T00:00:00+00:00"),
        _item(uid="m-in", source_id="claude-code", label="Claude Code",
              published="2026-08-03T00:00:00+00:00"),
        _item(uid="m-out", source_id="claude-code", label="Claude Code",
              published="2026-08-01T00:00:00+00:00"),
    ])
    top = news.split_recent(items, SOURCE_TYPES)
    assert top["model_groups"][0]["count"] == 1


def test_split_recent_unknown_source_counts_as_announcement(tmp_path):
    items = _loaded(tmp_path, [_item(uid="x", source_id="retired-source")])
    top = news.split_recent(items, SOURCE_TYPES)
    assert [i.uid for i in top["announcements"]] == ["x"]


def test_split_recent_empty_is_harmless(tmp_path):
    top = news.split_recent([], SOURCE_TYPES)
    assert top == {"announcements": [], "model_groups": []}


def test_group_by_month_labels_in_japanese(tmp_path):
    items = _loaded(tmp_path, [
        _item(uid="jul", published="2026-07-10T00:00:00+00:00"),
        _item(uid="aug", published="2026-08-04T19:00:00+00:00"),
    ])
    months = news.group_by_month(items)
    assert [label for label, _ in months] == ["2026年8月", "2026年7月"]
    assert [i.uid for i in months[0][1]] == ["aug"]
```

- [ ] **Step 2: 落ちることを確認**

Run: `PYTHONUTF8=1 python -m pytest tests/test_news.py -q`
Expected: FAIL（`AttributeError: module 'src.news' has no attribute 'split_recent'`）

- [ ] **Step 3: 実装**

`src/news.py` 末尾に追記:

```python
def is_announcement(item: NewsItem, source_types: dict[str, str]) -> bool:
    """お知らせ系なら True。型表に無い source_id は隠さない側（お知らせ）に倒す。"""
    return source_types.get(item.source_id, "rss") in ANNOUNCEMENT_TYPES


def split_recent(
    items: list[NewsItem],
    source_types: dict[str, str],
    limit: int = TOP_ANNOUNCEMENTS,
) -> dict:
    """トップ用。お知らせ最新 limit 件と、同期間のモデルのラベル畳み。"""
    announcements = [i for i in items if is_announcement(i, source_types)][:limit]
    models = [i for i in items if not is_announcement(i, source_types)]

    if announcements:
        window_start = announcements[-1].published
    elif items:
        window_start = items[0].published - MODEL_WINDOW_FALLBACK
    else:
        return {"announcements": [], "model_groups": []}

    groups: dict[str, dict] = {}
    for item in models:
        if item.published < window_start:
            continue
        group = groups.setdefault(item.label, {
            "label": item.label,
            "vendor": item.vendor,
            "count": 0,
            "latest_title": item.title,       # items は新しい順なので最初が最新
            "latest_published": item.published,
        })
        group["count"] += 1

    model_groups = sorted(
        groups.values(), key=lambda g: g["latest_published"], reverse=True
    )
    return {"announcements": announcements, "model_groups": model_groups}


def group_by_month(items: list[NewsItem]) -> list[tuple[str, list[NewsItem]]]:
    """/news/ 用。新しい月から順に（「2026年8月」, 項目リスト）を返す。"""
    months: dict[str, list[NewsItem]] = {}
    for item in items:
        label = f"{item.published.year}年{item.published.month}月"
        months.setdefault(label, []).append(item)
    return list(months.items())
```

- [ ] **Step 4: 通ることを確認**

Run: `PYTHONUTF8=1 python -m pytest tests/test_news.py -q`
Expected: PASS（12 passed）

- [ ] **Step 5: コミット**

```bash
git add src/news.py tests/test_news.py
git commit -m "feat: ニュースの振り分け・ベンダー畳み・月別グルーピング"
```

---

### Task 3: テンプレートと render_site

**Files:**
- Modify: `templates/_macros.html`（news_item マクロを追加）
- Modify: `templates/index.html`（AIアップデート欄）
- Create: `templates/news.html`
- Modify: `src/render.py`
- Modify: `tests/test_render.py`（末尾に追記）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_render.py` 末尾に追記:

```python
def _news_top():
    from datetime import datetime
    from src.news import JST, NewsItem
    item = NewsItem(
        uid="n1", source_id="openai-news",
        title="New ways to learn", url="https://example.com/post",
        vendor="OpenAI", label="OpenAI News", importance="major",
        published=datetime(2026, 8, 4, 9, 0, tzinfo=JST),
        summary_ja="1行目\n2行目\n3行目",
    )
    return {
        "top": {
            "announcements": [item],
            "model_groups": [{
                "label": "Claude Code", "vendor": "Anthropic", "count": 2,
                "latest_title": "v2.1.223",
                "latest_published": item.published,
            }],
        },
        "archive": {"months": [("2026年8月", [item])]},
    }


def test_index_shows_news_section():
    pages = render_site([_article()], news=_news_top())
    html = pages["index.html"]
    assert "AIアップデート" in html
    assert "New ways to learn" in html
    assert "1行目" in html
    assert "重要" in html
    assert "Claude Code: 2件（最新: v2.1.223）" in html
    assert "要約は自動生成" in html
    assert 'href="/news/"' in html


def test_news_page_is_rendered_with_months():
    pages = render_site([_article()], news=_news_top())
    html = pages["news/index.html"]
    assert "2026年8月" in html
    assert "New ways to learn" in html
    assert '<link rel="canonical" href="https://ai-tsukaikata.com/news/">' in html


def test_without_news_index_has_no_news_section():
    pages = render_site([_article()])
    assert "AIアップデート" not in pages["index.html"]
    assert "news/index.html" not in pages


def test_news_nav_link_present_only_with_news():
    with_news = render_site([_article()], news=_news_top())
    without = render_site([_article()])
    assert '<a href="/news/">AIアップデート</a>' in with_news["index.html"]
    assert '<a href="/news/">AIアップデート</a>' not in without["index.html"]
```

- [ ] **Step 2: 落ちることを確認**

Run: `PYTHONUTF8=1 python -m pytest tests/test_render.py -q`
Expected: 新規4件が FAIL（`render_site() got an unexpected keyword argument 'news'`）

- [ ] **Step 3: テンプレートを書く**

`templates/_macros.html` 末尾に追記:

```html
{% macro news_item(item) %}
<li class="news-item">
  <p class="news-head">
    <time datetime="{{ item.published.date().isoformat() }}">{{ item.published.date() | jp_date }}</time>
    <span class="news-vendor">{{ item.vendor }}</span>
    {% if item.importance == "major" %}<span class="news-major">重要</span>{% endif %}
  </p>
  <p class="news-title"><a href="{{ item.url }}">{{ item.title }}</a></p>
  {% if item.summary_ja %}
  <p class="news-summary">{{ item.summary_ja }}</p>
  {% endif %}
</li>
{% endmacro %}
```

`templates/index.html` を次の内容に置き換え（hero と 新着 の間に欄を挟む）:

```html
{% extends "base.html" %}
{% block content %}
{% import "_macros.html" as macros %}
<section class="hero">
  <h1>{{ site.name }}</h1>
  <p class="hero-lead">{{ site.description }}</p>
</section>

{% if news %}
<section class="news-section">
  <h2 class="section-title">AIアップデート</h2>
  <p class="section-lead">各社の発表を自動で集めています。1日数回、自動更新。要約は自動生成です。</p>
  <ul class="news-list">
    {% for item in news.announcements %}
    {{ macros.news_item(item) }}
    {% endfor %}
  </ul>
  {% if news.model_groups %}
  <p class="news-models-head">新モデル・新バージョン</p>
  <ul class="news-models">
    {% for group in news.model_groups %}
    <li>{{ group.label }}: {{ group.count }}件（最新: {{ group.latest_title }}）</li>
    {% endfor %}
  </ul>
  {% endif %}
  <p class="news-more"><a href="/news/">すべて見る →</a></p>
</section>
{% endif %}

<section class="article-list">
  <h2 class="section-title">新着</h2>
  {% for article in articles %}
  {{ macros.card(article) }}
  {% endfor %}
</section>
{% endblock %}
```

`templates/news.html` を新規作成:

```html
{% extends "base.html" %}
{% block content %}
{% import "_macros.html" as macros %}
<h1 class="article-title">AIアップデート</h1>
<p class="article-meta">各社の発表とモデルの提供開始を自動で集めた記録です。1日数回、自動更新。要約は自動生成です。</p>
{% for month_label, month_items in news.months %}
<section class="news-month">
  <h2 class="section-title">{{ month_label }}</h2>
  <ul class="news-list">
    {% for item in month_items %}
    {{ macros.news_item(item) }}
    {% endfor %}
  </ul>
</section>
{% endfor %}
{% endblock %}
```

- [ ] **Step 4: render.py を変更**

`src/render.py` の `render_site` を次に置き換え:

```python
def render_site(
    articles: list[Article],
    news: dict | None = None,
    env: Environment | None = None,
) -> dict[str, str]:
    """全ページを組み立てる。キーは build/ からの相対パス。

    news は build.py が src/news.py で作る {"top": ..., "archive": ...}。
    None ならニュース欄も /news/ も出さない（テスト・部分ビルド用）。
    """
    env = env or build_env()

    listed = [a for a in articles if a.category in config.LISTED_CATEGORIES]
    active = [
        name for name in config.LISTED_CATEGORIES
        if any(a.category == name for a in listed)
    ]
    # 記事が1本もないカテゴリはナビにも一覧にも出さない（空ページを作らない）
    nav = [
        {"url": f"/{name}/", "label": config.CATEGORIES[name]["label"]} for name in active
    ]
    if news:
        nav.append({"url": "/news/", "label": "AIアップデート"})
    env.globals["nav"] = nav

    pages: dict[str, str] = {}

    pages["index.html"] = env.get_template("index.html").render(
        page_title=None,
        description=config.SITE_DESCRIPTION,
        canonical=f"{config.SITE_URL}/",
        og_type="website",
        articles=listed[: config.INDEX_MAX_ARTICLES],
        news=news["top"] if news else None,
    )

    if news:
        pages["news/index.html"] = env.get_template("news.html").render(
            page_title="AIアップデート",
            description="AI各社の発表とモデルの提供開始を自動で集めた記録。",
            canonical=f"{config.SITE_URL}/news/",
            og_type="website",
            news=news["archive"],
        )

    for name in active:
        meta = config.CATEGORIES[name]
        pages[f"{name}/index.html"] = env.get_template("list.html").render(
            page_title=meta["label"],
            description=meta["description"],
            canonical=f"{config.SITE_URL}/{name}/",
            og_type="website",
            category_label=meta["label"],
            articles=[a for a in listed if a.category == name],
        )

    article_template = env.get_template("article.html")
    for article in articles:
        meta = config.CATEGORIES[article.category]
        pages[article.output_path] = article_template.render(
            page_title=article.title,
            description=article.description,
            canonical=config.SITE_URL + article.url,
            og_type="article",
            article=article,
            category_label=meta["label"] or None,
            category_url=f"/{article.category}/",
        )

    return pages
```

- [ ] **Step 5: 通ることを確認**

Run: `PYTHONUTF8=1 python -m pytest tests/test_render.py -q`
Expected: PASS（既存含め全件）

- [ ] **Step 6: コミット**

```bash
git add templates/_macros.html templates/index.html templates/news.html src/render.py tests/test_render.py
git commit -m "feat: トップにAIアップデート欄・/news/ アーカイブページ"
```

---

### Task 4: build.py への配線

**Files:**
- Modify: `src/build.py`
- Modify: `tests/test_build.py`（末尾に追記）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_build.py` 末尾に追記:

```python
import json

NEWS_ITEM = {
    "uid": "n1", "source_id": "openai-news",
    "title": "ニューステスト", "url": "https://example.com/post",
    "vendor": "OpenAI", "label": "OpenAI News", "importance": "minor",
    "published": "2026-08-04T19:00:00+00:00", "summary_ja": "要約です",
}

SOURCES_YML = """\
sources:
  - id: openai-news
    vendor: OpenAI
    label: OpenAI News
    type: rss
    url: https://example.com/rss
"""


def _news_files(tmp_path: Path, items=None) -> tuple[Path, Path]:
    news_path = tmp_path / "news.json"
    news_path.write_text(
        json.dumps({"items": items if items is not None else [NEWS_ITEM]}, ensure_ascii=False),
        encoding="utf-8",
    )
    sources_path = tmp_path / "sources.yml"
    sources_path.write_text(SOURCES_YML, encoding="utf-8")
    return news_path, sources_path


def test_collect_with_news_renders_top_and_archive(tmp_path):
    news_path, sources_path = _news_files(tmp_path)
    files, errors = build.collect(
        _content_dir(tmp_path), news_path=news_path, sources_path=sources_path
    )
    assert errors == []
    assert "ニューステスト" in files["index.html"]
    assert "news/index.html" in files
    assert "https://ai-tsukaikata.com/news/</loc>" in files["sitemap.xml"]


def test_collect_with_broken_news_stops_build(tmp_path):
    news_path, sources_path = _news_files(tmp_path)
    news_path.write_text("{壊れている", encoding="utf-8")
    files, errors = build.collect(
        _content_dir(tmp_path), news_path=news_path, sources_path=sources_path
    )
    assert files == {}
    assert any("news.json" in error or "読めません" in error for error in errors)


def test_collect_without_news_paths_keeps_old_behavior(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path))
    assert errors == []
    assert "news/index.html" in files  # 既定は本物の data/tracker/news.json を読む
```

- [ ] **Step 2: 落ちることを確認**

Run: `PYTHONUTF8=1 python -m pytest tests/test_build.py -q`
Expected: 新規3件が FAIL（`collect() got an unexpected keyword argument 'news_path'`）

- [ ] **Step 3: build.py を変更**

`src/build.py` — import 部に1行追加:

```python
from . import config, feeds, news, render
```

（既存の `from . import config, feeds, render` を置き換え）

`collect` を次に置き換え:

```python
NEWS_PATH = ROOT / "data" / "tracker" / "news.json"
SOURCES_PATH = ROOT / "tracker" / "sources.yml"


def collect(
    content_dir: Path,
    static_dir: Path = STATIC_DIR,
    news_path: Path = NEWS_PATH,
    sources_path: Path = SOURCES_PATH,
) -> tuple[dict[str, str], list[str]]:
    """書き出す内容を全部メモリ上で作る。(files, errors) を返す。"""
    articles, errors = load_articles(content_dir)
    errors = errors + validate(articles, static_paths(static_dir))
    errors = errors + figure_errors(static_dir)

    news_data = None
    try:
        source_types = news.load_source_types(sources_path)
        items = news.load_news(news_path)
        news_data = {
            "top": news.split_recent(items, source_types),
            "archive": {"months": news.group_by_month(items)},
        }
    except news.NewsError as error:
        errors = errors + [str(error)]

    if errors:
        return {}, errors

    files = render.render_site(articles, news=news_data)

    section_paths = ("/", "/news/") + tuple(
        f"/{name}/" for name in config.LISTED_CATEGORIES
        if any(a.category == name for a in articles)
    )
    files["feed.xml"] = feeds.build_rss(articles)
    files["sitemap.xml"] = feeds.build_sitemap(articles, section_paths)
    files["robots.txt"] = feeds.build_robots()

    # 生成HTMLをコミットしない方式では、CNAME を artifact に含めないと
    # デプロイのたびに独自ドメインの設定が外れる
    files["CNAME"] = config.CUSTOM_DOMAIN + "\n"

    return files, []
```

- [ ] **Step 4: 通ることを確認（全テスト）**

Run: `PYTHONUTF8=1 python -m pytest -q`
Expected: 全件 PASS（343 + 新規16件前後）

- [ ] **Step 5: コミット**

```bash
git add src/build.py tests/test_build.py
git commit -m "feat: ビルドにニュースを配線（読めなければビルド中止）"
```

---

### Task 5: CSS とローカル確認

**Files:**
- Modify: `static/style.css`（末尾の `@media` の前に追記）

- [ ] **Step 1: CSS を追加**

`static/style.css` の `.tags` ブロックの後・`@media (max-width: 640px)` の前に挿入:

```css
/* --- AIアップデート欄 --- */

.news-section { margin-bottom: 2.5rem; }

.news-list {
  list-style: none;
  margin: 1.1rem 0 0;
  padding: 0;
}

.news-item {
  padding: 0.85rem 0;
  border-bottom: 1px solid var(--line);
}

.news-head {
  margin: 0 0 0.25rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
  color: var(--muted);
  font-size: 0.82rem;
}

.news-vendor {
  padding: 0.05rem 0.55rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--card-bg);
}

.news-major {
  padding: 0.05rem 0.55rem;
  border-radius: 999px;
  background: var(--mark-warn);
  color: var(--mark-warn-fg);
  font-weight: 700;
}

.news-title { margin: 0; font-size: 1rem; line-height: 1.7; }
.news-title a { text-decoration: none; }
.news-title a:hover { text-decoration: underline; }

/* 3行要約。summary_ja の改行をそのまま行にする */
.news-summary {
  margin: 0.3rem 0 0;
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.8;
  white-space: pre-line;
}

.news-models-head {
  margin: 1.2rem 0 0.3rem;
  color: var(--muted);
  font-size: 0.85rem;
  font-weight: 700;
}

.news-models {
  margin: 0;
  padding-left: 1.5rem;
  font-size: 0.92rem;
}

.news-models li { margin: 0.3rem 0; }

.news-more { margin: 1rem 0 0; font-size: 0.95rem; }

.news-month { margin-bottom: 2.5rem; }
```

- [ ] **Step 2: ビルドして目視**

Run: `PYTHONUTF8=1 python -m src.build`
Expected: `ビルド完了: N ファイルを ... に出力しました`（news/index.html が増えている）

プレビュー（`ai-tsukaikata-preview`）で確認する項目:
- トップに「AIアップデート」欄が出て、お知らせ10件＋モデル畳みが見える
- 要約の3行が改行されて表示される
- 「重要」バッジ・ベンダーバッジ・「すべて見る →」リンク
- /news/ で月別に全件出る
- スマホ幅375pxで横スクロールが出ない
- コンソールにエラーが無い

- [ ] **Step 3: コミット**

```bash
git add static/style.css
git commit -m "feat: ニュース欄のスタイル"
```

---

### Task 6: デプロイ設定と本番反映

**Files:**
- Modify: `.github/workflows/build.yml`（`paths:` に2行追加）

- [ ] **Step 1: build.yml の paths に追加**

`on.push.paths` のリストに次の2行を足す（既存の並びに追記）:

```yaml
      - "data/tracker/news.json"
      - "tracker/sources.yml"
```

ニュースが実際に増えたコミットだけがサイトを再デプロイする。seen.json だけの
既読更新では動かない（1日13回の無駄ビルドを防ぐ既存設計を維持）。

- [ ] **Step 2: 最終チェックとプッシュ**

```bash
PYTHONUTF8=1 python -m pytest -q
git add .github/workflows/build.yml
git commit -m "ci: ニュース更新でもサイトを再ビルドする"
git push
```

- [ ] **Step 3: 本番確認**

GitHub Actions の build 実行が緑になるのを待ち、https://ai-tsukaikata.com/ で:
- トップに「AIアップデート」欄
- https://ai-tsukaikata.com/news/ が200
- sitemap.xml に /news/ が入っている

---

## Self-Review 記録

- スペック④の全要件（トップ直近・/news/・major印・注記・鮮度文言・paths 追加・壊れたら停止）に対応するタスクがある
- プレースホルダなし。全ステップに実コード・実コマンド・期待結果を記載
- 型の一貫性: `split_recent` の返り値キー（announcements / model_groups）と group のキー（label / count / latest_title / latest_published）はテンプレート・テストと一致。`render_site(articles, news=, env=)` のシグネチャは Task 3 と 4 で一致
