# サイト内検索 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 全ページのヘッダーに検索窓を置き、`/search/?q=…` で記事（187本）をタイトル・説明文・タグ・見出しから部分一致で探せるようにする。

**Architecture:** ビルド（`python -m src.build`）が記事から `search.json` を書き出し、`/search/` ページの素のJS（`static/js/search.js`）がそれを1回だけ読んで、NFKC＋小文字で正規化した部分一致（AND）で絞り込む。ヘッダーの窓は素のHTMLフォーム（JS無しでも `/search/?q=` へ飛ぶ）。外部サービス・鍵・依存追加は無し。設計書: `docs/superpowers/specs/2026-09-20-site-search-design.md`

**Tech Stack:** Python 3.12（Jinja2 / Markdown / pytest・既存のまま）、素のJavaScript（ES5・`copy.js` と同じ流儀）、CSS（既存の変数）

---

## ファイル構成

| ファイル | 役割 |
|---|---|
| Create `src/search.py` | 記事 → 索引（`build_index` / `search_json`）。見出しの抽出と大きさの予算。ファイルは書かない |
| Modify `src/build.py` | `files["search.json"]` を足す（`collect()` の中） |
| Modify `src/render.py` | `search/index.html` を組む（`hide_header_search=True`） |
| Modify `templates/base.html` | `{% block head %}` の差し込み口＋ヘッダーの検索フォーム |
| Create `templates/search.html` | 検索ページ（大きい窓・結果の器・noscript・noindex・JS読み込み） |
| Modify `static/style.css` | ヘッダーの窓・検索ページの窓と結果の見た目（末尾に1節） |
| Create `static/js/search.js` | 索引の読み込み・正規化・AND部分一致・順位付け・描画・URL同期 |
| Create `tests/test_search.py` | 索引（単体）・実データの予算・検索ページの描画・ヘッダーの窓 |
| Modify `tests/test_build.py` | `search.json` と `search/index.html` が出る・sitemap に `/search/` が無い |
| Modify `tests/test_render.py:165-173` | ヘッダーのテストの docstring（窓は許す） |
| Modify `CLAUDE.md` / `SESSION_HANDOFF.md` | 運用メモ（索引の予算・JSの確かめ方） |

**コマンドの前提:** すべて `C:\Users\info0\ai-tsukaikata` で実行。Python は `PYTHONUTF8=1` を付ける（cp932 対策）。
コミットは `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>` で締める。

---

### Task 1: 索引を作る `src/search.py`

**Files:**
- Create: `src/search.py`
- Test: `tests/test_search.py`

- [x] **Step 1: 失敗するテストを書く**

`tests/test_search.py` を新規作成:

```python
# -*- coding: utf-8 -*-
import json
from datetime import date
from pathlib import Path

from src.content import Article, load_articles, render_markdown
from src.search import INDEX_BUDGET_BYTES, build_index, headings, plain_text, search_json

ROOT = Path(__file__).resolve().parent.parent


def _article(slug="sample", category="recipes", title="題名", body="本文です。", **kwargs):
    defaults = dict(
        slug=slug,
        title=title,
        description="説明文です。",
        category=category,
        published=date(2026, 8, 1),
        updated=None,
        tags=("自動化",),
        time_required="30分" if category == "recipes" else None,
        cost="無料" if category == "recipes" else None,
        body_html=render_markdown(body),
        source_path=Path(f"content/{category}/{slug}.md"),
    )
    defaults.update(kwargs)
    return Article(**defaults)


def test_plain_text_strips_tags_unescapes_and_collapses_spaces():
    assert plain_text("A &amp; B\n  <em>C</em>") == "A & B C"


def test_headings_take_h2_and_h3_text_only():
    body = (
        "## これで何ができるか {: .what }\n\n"
        "### 小見出し `code`\n\n"
        "#### h4 は入れない\n\n"
        "本文\n"
    )
    assert headings(render_markdown(body)) == ["これで何ができるか", "小見出し code"]


def test_build_index_has_one_entry_per_article_with_expected_fields():
    index = build_index([_article(slug="a"), _article(slug="b", category="tools")])
    assert [e["url"] for e in index] == ["/recipes/a/", "/tools/b/"]
    entry = index[0]
    assert set(entry) == {
        "url", "title", "description", "tags", "headings",
        "category", "category_label", "scene", "scene_label", "published",
    }
    assert entry["tags"] == ["自動化"]
    assert entry["headings"] == []
    assert entry["published"] == "2026-08-01"
    assert entry["scene"] is None and entry["scene_label"] is None


def test_index_labels_come_from_config():
    entry = build_index([_article(category="tools", scene="earn")])[0]
    assert entry["category_label"] == "ツール"
    assert entry["scene"] == "earn"
    assert entry["scene_label"] == "副業"


def test_search_json_keeps_japanese_readable_and_round_trips():
    articles = [_article(title="題名テスト")]
    text = search_json(articles)
    assert "題名テスト" in text          # \uXXXX に逃がさない
    assert text.endswith("\n")
    assert json.loads(text) == build_index(articles)


def test_real_content_index_is_within_budget_and_clean():
    """実データの歯止め。索引が黙って重くなったり、見出しにタグが混ざったりしたら落ちる。"""
    articles, errors = load_articles(ROOT / "content")
    assert errors == []
    index = build_index(articles)
    assert {e["url"] for e in index} == {a.url for a in articles}
    for entry in index:
        for heading in entry["headings"]:
            assert "<" not in heading, (entry["url"], heading)
    size = len(search_json(articles).encode("utf-8"))
    assert size <= INDEX_BUDGET_BYTES, f"search.json が {size} バイト（予算 {INDEX_BUDGET_BYTES}）"
```

- [x] **Step 2: 失敗を確かめる**

Run: `PYTHONUTF8=1 python -m pytest -q tests/test_search.py`
Expected: `ModuleNotFoundError: No module named 'src.search'`（収集の時点で落ちる）

- [x] **Step 3: 実装する**

`src/search.py` を新規作成:

```python
# -*- coding: utf-8 -*-
"""サイト内検索の索引。記事から search.json の中身を作る。ファイルは書かない。

探すのはブラウザ側（static/js/search.js）。ここが決めるのは「何を探せる文字に
するか」だけ＝タイトル・説明文・タグ・見出し（h2/h3）。本文は入れない
（索引が10倍になる。実測 2026-09-20: 見出しまで 248KB / 本文全部 2.7MB）。
正規化（全角→半角・小文字）は JS 側で行うので、ここは生の文字だけを入れる
（正規化済みの文字を並べて持つと索引が2倍になる）。
"""
from __future__ import annotations

import html
import json
import re

from . import config
from .content import Article

HEADING_RE = re.compile(r"<h[23]\b[^>]*>(.*?)</h[23]>", re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")

# 索引の大きさの予算（バイト）。実測 248KB（2026-09-20・187本）に5割の余裕。
# 超えたら tests/test_search.py が落ちる＝黙って重くならないための歯止め。
# 記事が増えて超えたら、値を上げる前に「見出しが冗長になっていないか」を見る
INDEX_BUDGET_BYTES = 400 * 1024


def plain_text(fragment: str) -> str:
    """HTML の断片から文字だけを取り出す。タグを剥がし、実体参照を戻し、空白を1つに畳む。"""
    return SPACE_RE.sub(" ", html.unescape(TAG_RE.sub(" ", fragment))).strip()


def headings(body_html: str) -> list[str]:
    """本文の h2/h3 の文字。`{: .what}` は Markdown 変換で class になっているので残らない。"""
    texts = (plain_text(inner) for inner in HEADING_RE.findall(body_html))
    return [text for text in texts if text]


def build_index(articles: list[Article]) -> list[dict]:
    """記事1本を索引1件にする。表示用の札（category_label / scene_label）も config から入れる＝
    JS 側に日本語の対応表を持たせない。"""
    return [
        {
            "url": a.url,
            "title": a.title,
            "description": a.description,
            "tags": list(a.tags),
            "headings": headings(a.body_html),
            "category": a.category,
            "category_label": config.CATEGORIES[a.category]["label"],
            "scene": a.scene,
            "scene_label": config.SCENES[a.scene]["label"] if a.scene else None,
            "published": a.published.isoformat(),
        }
        for a in articles
    ]


def search_json(articles: list[Article]) -> str:
    """search.json の本文。日本語をそのまま書き、区切りは詰める（gzip 後は差が無いが生の大きさが読みやすい）。"""
    return json.dumps(build_index(articles), ensure_ascii=False, separators=(",", ":")) + "\n"
```

- [x] **Step 4: 通ることを確かめる**

Run: `PYTHONUTF8=1 python -m pytest -q tests/test_search.py`
Expected: `6 passed`

- [x] **Step 5: コミット**

```bash
git add src/search.py tests/test_search.py
git commit -m "feat(search): 記事から検索の索引を作る src/search.py（見出し抽出・大きさの予算）"
```

---

### Task 2: ビルドが `search.json` を書き出す

**Files:**
- Modify: `src/build.py`（`collect()`・`files["robots.txt"] = ...` の直後）
- Test: `tests/test_build.py`（末尾に追加）

- [x] **Step 1: 失敗するテストを書く**

`tests/test_build.py` の末尾に追加（`import json` を先頭の import に足す）:

```python
def test_collect_emits_search_index_and_search_page(tmp_path):
    """検索の索引は記事と同じ検証を通った内容から作る。sitemap には入れない（検索結果ページを
    Google に拾わせない）。"""
    files, errors = build.collect(_content_dir(tmp_path))
    assert errors == []
    index = json.loads(files["search.json"])
    assert [entry["url"] for entry in index] == ["/recipes/sample/"]
    assert index[0]["title"] == "テスト記事"
    assert "search/index.html" in files
    assert "/search/" not in files["sitemap.xml"]
```

- [x] **Step 2: 失敗を確かめる**

Run: `PYTHONUTF8=1 python -m pytest -q tests/test_build.py -k search`
Expected: `KeyError: 'search.json'`

- [x] **Step 3: 実装する**

`src/build.py` の import に `search` を足す:

```python
from . import config, feeds, news, render, search
```

`collect()` の `files["robots.txt"] = feeds.build_robots()` の直後に:

```python
    # サイト内検索の索引（2026-09-20）。/search/ を開いたときだけブラウザが読む。
    # 記事と同じ検証を通った内容から作るので、ここより上で errors が出ていれば出ない
    files["search.json"] = search.search_json(articles)
```

⚠️ `section_paths` には `/search/` を**足さない**（sitemap に載せない）。`search/index.html` 自体は Task 3 の
`render_site()` が返す。

- [x] **Step 4: 通ることを確かめる（Task 3 が済むまで `search/index.html` の assert だけ落ちる）**

Run: `PYTHONUTF8=1 python -m pytest -q tests/test_build.py -k search`
Expected: `AssertionError: assert 'search/index.html' in files`（`search.json` の2つの assert は通っている。
Task 3 の Step 4 で全部通る）

- [x] **Step 5: コミット（Task 3 と一緒でもよい）**

```bash
git add src/build.py tests/test_build.py
git commit -m "feat(search): ビルドが search.json を書き出す（sitemap には載せない）"
```

---

### Task 3: 検索ページとヘッダーの窓（テンプレート・render）

**Files:**
- Modify: `templates/base.html`（`<script src="/static/js/copy.js" defer></script>` の直後と `<header>` の中）
- Create: `templates/search.html`
- Modify: `src/render.py`（`pages["index.html"] = ...` の直前）
- Modify: `tests/test_render.py:95-102`（全ページの集合に `search/index.html` を足す）と `:165-173`（docstring）
- Test: `tests/test_search.py`（末尾に追加）

- [x] **Step 1: 失敗するテストを書く**

`tests/test_search.py` の import に `from src.render import render_site` を足し、末尾に追加:

```python
def test_search_page_is_rendered_with_noindex_and_script():
    pages = render_site([_article()])
    html = pages["search/index.html"]
    assert '<meta name="robots" content="noindex">' in html
    assert '<script src="/static/js/search.js" defer></script>' in html
    assert 'id="search-input"' in html and 'id="search-results"' in html
    assert "<noscript>" in html and 'href="/recipes/"' in html
    assert '<link rel="canonical" href="https://ai-tsukaikata.com/search/">' in html


def test_header_search_form_is_on_every_page_except_search():
    pages = render_site([_article()])
    for path in ("index.html", "recipes/index.html", "recipes/sample/index.html"):
        header = pages[path].split("</header>")[0]
        assert 'action="/search/"' in header, path
        assert 'name="q"' in header, path
    header = pages["search/index.html"].split("</header>")[0]
    assert "site-search" not in header      # 同じ窓が2つ並ばない


def test_other_pages_do_not_load_search_js():
    pages = render_site([_article()])
    assert "search.js" not in pages["recipes/sample/index.html"]
    assert "search.js" not in pages["index.html"]
```

- [x] **Step 2: 失敗を確かめる**

Run: `PYTHONUTF8=1 python -m pytest -q tests/test_search.py`
Expected: `KeyError: 'search/index.html'`（noindex のテスト）と `assert 'action="/search/"' in header`（窓のテスト）の
**2 failed, 7 passed**（`test_other_pages_do_not_load_search_js` は実装前から通る＝退行を見張るテスト）

- [x] **Step 3: `templates/base.html` を直す**

`<script src="/static/js/copy.js" defer></script>` の直後に差し込み口を足す:

```html
<script src="/static/js/copy.js" defer></script>
{% block head %}{% endblock %}
```

`<header class="site-header">` の中身を次にする（サイト名は変えない）:

```html
<header class="site-header">
  <a class="site-name" href="/">{{ site.name }}</a>
  {% if not hide_header_search %}
  {# 素のフォーム＝JS無しでも /search/?q=… へ飛ぶ。JS はヘッダーに足さない（2026-09-20） #}
  <form class="site-search" action="/search/" method="get" role="search">
    <input class="site-search-input" type="search" name="q" placeholder="記事を探す" aria-label="記事を探す">
    <button class="site-search-button" type="submit">検索</button>
  </form>
  {% endif %}
</header>
```

- [x] **Step 4: `templates/search.html` を作る**

```html
{% extends "base.html" %}
{% block head %}
<meta name="robots" content="noindex">
<script src="/static/js/search.js" defer></script>
{% endblock %}
{% block content %}
<section class="search-page">
  <h1 class="article-title">記事を探す</h1>
  <form id="search-form" class="search-form" action="/search/" method="get" role="search">
    <input id="search-input" class="search-input" type="search" name="q" placeholder="例: Gmail、副業、GitHub Actions" aria-label="記事を探す" autocomplete="off">
    <button class="search-button" type="submit">検索</button>
  </form>
  <p id="search-status" class="search-status" aria-live="polite">言葉を入れると、タイトル・説明文・タグ・見出しから探します。</p>
  <div id="search-results" class="article-list"></div>
  <noscript><p class="search-noscript">検索には JavaScript が必要です。<a href="/recipes/">レシピ一覧</a>・<a href="/tools/">深掘り記事の一覧</a>から探せます。</p></noscript>
</section>
{% endblock %}
```

- [x] **Step 5: `src/render.py` に検索ページを足す**

`pages["index.html"] = ...` の直前に:

```python
    # サイト内検索（2026-09-20）。記事ではないので /news/ と同じく template から直接組む。
    # noindex＋sitemap 外（build.py の section_paths に入れない）＝検索結果ページを Google に拾わせない
    pages["search/index.html"] = env.get_template("search.html").render(
        page_title="記事を探す",
        description="タイトル・説明文・タグ・見出しから記事を探します。",
        canonical=f"{config.SITE_URL}/search/",
        og_type="website",
        hide_header_search=True,   # 本文の大きい窓だけにする（同じ窓が2つ並ばない）
    )
```

- [x] **Step 6: `tests/test_render.py` を現状に合わせる**

`test_output_paths_use_trailing_slash_structure`（95〜102行）は全ページの集合を固定しているので、検索ページを足す:

```python
def test_output_paths_use_trailing_slash_structure():
    pages = render_site([_article(), _article(slug="about", category="pages")])
    assert set(pages) == {
        "index.html",
        "recipes/index.html",
        "recipes/sample/index.html",
        "about/index.html",
        "search/index.html",   # サイト内検索（2026-09-20）。記事が何本でも必ず出る
    }
```

`test_header_has_no_nav_links` の docstring（165〜167行）:

```python
def test_header_has_no_nav_links():
    """ヘッダーのナビは 2026-08-13 に廃止（カテゴリーボタンと重複するため）。
    ヘッダーに残るのはサイト名のリンクと、2026-09-20 に足した検索の窓（site-search）だけ。"""
```

- [x] **Step 7: 通ることを確かめる**

Run: `PYTHONUTF8=1 python -m pytest -q tests/test_search.py tests/test_build.py tests/test_render.py`
Expected: すべて `passed`（`test_collect_emits_search_index_and_search_page` も通る）

Run: `PYTHONUTF8=1 python -m pytest -q`
Expected: `656 passed`（646＋新規10本）。落ちるものが無いこと

- [x] **Step 8: コミット**

```bash
git add templates/base.html templates/search.html src/render.py src/build.py tests/test_search.py tests/test_build.py tests/test_render.py
git commit -m "feat(search): ヘッダーの検索窓と /search/ ページ（noindex・sitemap外・JSはこのページだけ）"
```

---

### Task 4: 見た目（CSS）

**Files:**
- Modify: `static/style.css`（末尾に1節追加）

CSS に自動テストは無い。ビルドの検査（`python -m src.build`）と Task 6 のブラウザ確認で見る。

- [x] **Step 1: `static/style.css` の末尾に追加**

```css
/* --- サイト内検索（2026-09-20）。ヘッダーの窓は素のフォーム＝JS無しでも /search/ へ飛ぶ --- */

.site-search {
  display: flex;
  gap: 0.4rem;
  align-items: center;
  margin-left: auto;              /* サイト名の右端に寄せる */
}

.site-search-input, .search-input {
  font: inherit;
  color: var(--fg);
  background: var(--card-bg);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 0.35rem 0.6rem;
  min-width: 0;
  -webkit-appearance: none;       /* type=search の丸い既定形を消して他の枠と揃える */
  appearance: none;
}

.site-search-input { width: 11rem; font-size: 0.9rem; }

.site-search-button, .search-button {
  flex: none;
  font: inherit;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--accent);
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 0.35rem 0.8rem;
  cursor: pointer;
}

.site-search-button:hover, .search-button:hover { border-color: var(--accent); }

.site-search-input:focus-visible, .search-input:focus-visible,
.site-search-button:focus-visible, .search-button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

@media (max-width: 640px) {
  .site-search { flex-basis: 100%; margin-left: 0; }   /* 2行目に回す＝横スクロールを作らない */
  .site-search-input { flex: 1; width: auto; }
}

/* 検索ページ */
.search-form { display: flex; gap: 0.5rem; margin: 0 0 0.8rem; }
.search-input { flex: 1; font-size: 1rem; padding: 0.55rem 0.8rem; }
.search-button { font-size: 0.95rem; padding: 0.55rem 1rem; }
.search-status { color: var(--muted); font-size: 0.95rem; margin: 0 0 1rem; }
.search-hint { margin: 0 0 0.6rem; color: var(--muted); font-size: 0.88rem; }
.search-noscript { color: var(--muted); }
```

- [x] **Step 2: ビルドが通ることを確かめる**

Run: `PYTHONUTF8=1 python -m src.build`
Expected: `ビルド完了: 208ファイルを ... に出力しました`（206＋`search.json`＋`search/index.html`）

- [x] **Step 3: コミット**

```bash
git add static/style.css
git commit -m "feat(search): ヘッダーの窓と検索ページの見た目（スマホでは窓を2行目に回す）"
```

---

### Task 5: 検索の JS `static/js/search.js`

**Files:**
- Create: `static/js/search.js`

自動テストは無い（この環境に Node が無い）。Task 6 でブラウザで実際に打って確かめる。

- [x] **Step 1: `static/js/search.js` を作る（前半）**

```javascript
// サイト内検索（/search/ だけで読む）。
//
// 索引は /search.json（ビルドが記事から作る。タイトル・説明文・タグ・見出し）。
// 探し方は「部分一致の AND」。日本語は単語の切れ目が無いので、分かち書きせずに
// 文字列の部分一致で当てるのがいちばん素直。全角・大文字は NFKC と小文字化で揃える
// （索引側は生の文字なので、索引と入力の両方をここで同じ規則に通す）。
// JavaScript が無い環境では <noscript> の案内だけが見える（壊れない）。
(function () {
  "use strict";

  var INDEX_URL = "/search.json";
  var DEBOUNCE_MS = 150;
  // 当たり方の点。タイトル > タグ > 説明文 > 見出し。語ごとに最も高い当たり方を採る
  var WEIGHTS = { title: 4, tags: 3, description: 2, headings: 1 };
  var EMPTY_HINT = "言葉を入れると、タイトル・説明文・タグ・見出しから探します。例: Gmail、副業、GitHub Actions";

  var form = document.getElementById("search-form");
  var input = document.getElementById("search-input");
  var results = document.getElementById("search-results");
  var status = document.getElementById("search-status");
  if (!form || !input || !results || !status) return;

  function normalize(text) {
    return String(text || "").normalize("NFKC").toLowerCase();
  }

  function terms(query) {
    return normalize(query).split(/\s+/).filter(function (t) { return t.length > 0; });
  }

  // 索引1件を正規化済みの「探す文字」に変えておく（入力のたびに正規化しないため）。
  // タグは空白でつなぐ。語は空白を含まないので、2つのタグにまたがって当たることはない
  function prepare(entry) {
    return {
      entry: entry,
      title: normalize(entry.title),
      tags: normalize((entry.tags || []).join(" ")),
      description: normalize(entry.description),
      headings: (entry.headings || []).map(normalize)
    };
  }

  // 1語の当たり方の点。どこにも無ければ 0
  function scoreTerm(item, term) {
    if (item.title.indexOf(term) !== -1) return WEIGHTS.title;
    if (item.tags.indexOf(term) !== -1) return WEIGHTS.tags;
    if (item.description.indexOf(term) !== -1) return WEIGHTS.description;
    for (var i = 0; i < item.headings.length; i++) {
      if (item.headings[i].indexOf(term) !== -1) return WEIGHTS.headings;
    }
    return 0;
  }

  function search(items, words) {
    var hits = [];
    items.forEach(function (item) {
      var total = 0;
      for (var i = 0; i < words.length; i++) {
        var score = scoreTerm(item, words[i]);
        if (score === 0) return;          // AND: 1語でも無ければ外す
        total += score;
      }
      hits.push({ item: item, score: total });
    });
    hits.sort(function (a, b) {
      if (b.score !== a.score) return b.score - a.score;
      // 同点は新しい順（published は YYYY-MM-DD なので文字列の比較でよい）
      if (a.item.entry.published === b.item.entry.published) return 0;
      return a.item.entry.published < b.item.entry.published ? 1 : -1;
    });
    return hits;
  }

  // 見出しだけに当たった語があれば、その見出し（生の文字）を返す。無ければ null
  function matchedHeading(item, words) {
    for (var w = 0; w < words.length; w++) {
      if (scoreTerm(item, words[w]) !== WEIGHTS.headings) continue;
      for (var i = 0; i < item.headings.length; i++) {
        if (item.headings[i].indexOf(words[w]) !== -1) return item.entry.headings[i];
      }
    }
    return null;
  }
```

- [x] **Step 2: `static/js/search.js` の後半（前半の続きに書く。最後の `})();` で閉じる）**

```javascript
  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;   // 索引の文字を HTML として解釈しない
    return node;
  }

  function jpDate(iso) {                 // "2026-09-20" → "2026年9月20日"
    var p = String(iso).split("-");
    if (p.length !== 3) return String(iso);
    return p[0] + "年" + Number(p[1]) + "月" + Number(p[2]) + "日";
  }

  function renderHit(hit, words) {
    var e = hit.item.entry;
    var card = el("article", "card");
    var body = el("div", "card-body");
    var title = el("h2", "card-title");
    var link = el("a", null, e.title);
    link.href = e.url;
    title.appendChild(link);
    body.appendChild(title);
    body.appendChild(el("p", "card-description", e.description));
    var heading = matchedHeading(hit.item, words);
    if (heading) body.appendChild(el("p", "search-hint", "見出し「" + heading + "」に一致"));
    var meta = el("p", "card-meta");
    if (e.category_label) meta.appendChild(el("span", "card-badge", e.category_label));
    if (e.scene && e.scene_label) {
      var scene = el("a", "card-scene sc-" + e.scene, e.scene_label);
      scene.href = "/scenes/" + e.scene + "/";
      meta.appendChild(scene);
    }
    var time = el("time", null, jpDate(e.published));
    time.setAttribute("datetime", e.published);
    meta.appendChild(time);
    body.appendChild(meta);
    card.appendChild(body);
    return card;
  }

  function renderEmpty(query) {
    var p = el("p", "search-noscript", "「" + query + "」に当たる記事は見つかりませんでした。別の言葉で試すか、");
    var recipes = el("a", null, "レシピ一覧");
    recipes.href = "/recipes/";
    var tools = el("a", null, "深掘り記事の一覧");
    tools.href = "/tools/";
    p.appendChild(recipes);
    p.appendChild(document.createTextNode("・"));
    p.appendChild(tools);
    p.appendChild(document.createTextNode("から探してください。"));
    return p;
  }

  function syncUrl(query) {
    if (!window.history || !window.history.replaceState) return;
    var url = query ? "/search/?q=" + encodeURIComponent(query) : "/search/";
    window.history.replaceState(null, "", url);
  }

  function run(items) {
    var query = input.value.trim();
    var words = terms(query);
    syncUrl(query);
    while (results.firstChild) results.removeChild(results.firstChild);
    if (words.length === 0) {
      status.textContent = EMPTY_HINT;
      return;
    }
    var hits = search(items, words);
    if (hits.length === 0) {
      status.textContent = "0件";
      results.appendChild(renderEmpty(query));
      return;
    }
    status.textContent = "「" + query + "」に当たる記事: " + hits.length + "件";
    hits.forEach(function (hit) { results.appendChild(renderHit(hit, words)); });
  }

  function start() {
    var initial = new URLSearchParams(window.location.search).get("q") || "";
    input.value = initial;
    status.textContent = "索引を読み込んでいます…";
    fetch(INDEX_URL).then(function (response) {
      if (!response.ok) throw new Error("HTTP " + response.status);
      return response.json();
    }).then(function (entries) {
      var items = entries.map(prepare);
      var timer = null;
      input.addEventListener("input", function () {
        if (timer) clearTimeout(timer);
        timer = setTimeout(function () { run(items); }, DEBOUNCE_MS);
      });
      form.addEventListener("submit", function (event) {
        event.preventDefault();           // 素のフォームの送信（ページ再読み込み）を止めてその場で絞る
        if (timer) clearTimeout(timer);
        run(items);
      });
      run(items);
      input.focus();
    }).catch(function () {
      // 黙って空にしない。読めなかったことを利用者に見せる
      status.textContent = "検索を読み込めませんでした。ページを再読み込みしてください。";
    });
  }

  start();
})();
```

- [x] **Step 3: 括弧の対応だけ先に確かめる（Node が無いので Python で数える）**

Run: `PYTHONUTF8=1 python -c "t=open('static/js/search.js',encoding='utf-8').read(); print(t.count('{')==t.count('}'), t.count('(')==t.count(')'))"`
Expected: `True True`

- [x] **Step 4: ビルドして static にコピーされることを確かめる**

Run: `PYTHONUTF8=1 python -m src.build && ls build/static/js/ build/search/ && ls -l build/search.json`
Expected: `copy.js  search.js`・`index.html`・`search.json`（約250KB）

- [x] **Step 5: コミット**

```bash
git add static/js/search.js
git commit -m "feat(search): 検索ページのJS（NFKC正規化・AND部分一致・順位付け・URL同期）"
```

---

### Task 6: ブラウザで実際に打って確かめる（JS・CSS の検証）

**Files:** なし（直すものが出たら該当ファイルを直して Task 4/5 のコミットに足す）

プレビューは `.claude/launch.json` の `site`（`python -m http.server 8877 --directory build`）。**`build/` を配信するので、
直したら必ず `python -m src.build` を先に走らせる。**

- [x] **Step 1: ビルドしてプレビューを開く**

Run: `PYTHONUTF8=1 python -m src.build`
そのあと `preview_start {name: "site"}` → `navigate` で `http://localhost:8877/search/?q=Gmail`

- [x] **Step 2: 直リンク `?q=Gmail` で結果が出る**

`read_page` で確かめる: 窓に `Gmail` が入っている／状態行が「「Gmail」に当たる記事: N件」（N ≥ 1）／
結果カードにタイトル・説明文・札（レシピ／ツール）・日付がある。`read_console_messages {onlyErrors: true}` が空。

- [x] **Step 3: 入力で絞り直せる・URL が追従する**

`find` で窓の ref を取り、`triple_click` → `type "副業"` → 状態行が「「副業」に当たる記事: N件」に変わり、
`javascript_tool` で `location.search` が `?q=%E5%89%AF%E6%A5%AD` になっている。

- [x] **Step 4: 正規化と AND**

- `ｇｍａｉｌ`（全角小文字）で Step 2 と同じ件数になる
- `GitHub Actions`（2語）で、両方を含む記事だけが出る（`javascript_tool` で
  `Array.from(document.querySelectorAll('#search-results .card-title')).length` と、1語ずつの件数を比べて 2語 ≤ 各1語）
- `見出しにしか無い言葉`＝索引から見出しだけにある語を1つ選ぶ（`javascript_tool` で `fetch('/search.json')` を読んで、
  title/description/tags に無く headings にだけある語を探す）→ その語で検索して「見出し『…』に一致」の行が出る

- [x] **Step 5: 0件と空欄**

- `zzzzqqqq` → 状態行「0件」＋「見つかりませんでした」＋レシピ一覧／深掘り記事の一覧のリンク
- 窓を空にする（`triple_click` → `key "Backspace"`）→ 状態行が案内文に戻り、結果が消え、URL が `/search/` になる

- [x] **Step 6: ヘッダーの窓（JS無しの経路）**

`navigate` で `http://localhost:8877/recipes/` → ヘッダーの窓に `Gmail` を入れて Enter（`find` で `name="q"` の input →
`type` → `key "Return"`）→ `/search/?q=Gmail` へ遷移し、結果が出る。

- [x] **Step 7: スマホ幅とダークモード**

- `resize_window {preset: "mobile"}` → `/search/?q=Gmail` と `/recipes/` で `javascript_tool`:
  `document.documentElement.scrollWidth <= window.innerWidth`（横スクロール無し）。ヘッダーの窓が2行目に回っている
  （`screenshot` で目視）
- `resize_window {colorScheme: "dark"}` → 窓とボタンの配色が暗い紙に馴染んでいる（`screenshot`）
- 終わったら `resize_window {preset: "desktop"}` に戻す

- [x] **Step 8: 直したものがあればコミット**

```bash
git add static/js/search.js static/style.css templates/search.html
git commit -m "fix(search): ブラウザ確認で見つかった崩れを直す（内容を1行で）"
```

---

### Task 7: 記録・公開・本番確認

**Files:**
- Modify: `CLAUDE.md`（「2段目（サイト本体）」の「できているもの」表の下に短い節）
- Modify: `SESSION_HANDOFF.md`（冒頭の 2026-09-20 節に1項目）

- [x] **Step 1: CLAUDE.md に運用メモを足す**

「### 記事の書き方（2026-08-02 に方針変更）」の直前に:

```markdown
### 🔎 サイト内検索（2026-09-20）

- ヘッダーの窓は素のフォーム（JS無しでも `/search/?q=` へ飛ぶ）。探すのは `/search/` の `static/js/search.js` だけ
- 索引＝`build/search.json`（`src/search.py`。タイトル・説明文・タグ・見出し h2/h3。本文は入れない）。
  **大きさの予算 400KB** は `tests/test_search.py` が実データで見る＝超えたら値を上げる前に見出しの冗長さを疑う
- 正規化は NFKC＋小文字を**JS側だけ**で行う（索引は生の文字）。当たり方の点＝タイトル4・タグ3・説明文2・見出し1、語は AND
- `/search/` は noindex・sitemap 外。ニュースを検索対象に足すなら、索引に同じ形（url/title/description/…）で並べるだけ
- JS に自動テストは無い。直したらプレビュー（`site`・`build/` を配信）で `?q=Gmail`・全角・2語・0件・375px を手で確かめる
```

- [x] **Step 2: SESSION_HANDOFF.md の 2026-09-20 節に1項目**

「- **深掘りの材料切れ**＝…」の項目の後に:

```markdown
- **サイト内検索を作った**（設計 `docs/superpowers/specs/2026-09-20-site-search-design.md`・計画
  `docs/superpowers/plans/2026-09-20-site-search.md`）。ヘッダーの窓＋`/search/`。索引は `search.json`（予算 400KB をテストが見る）
```

- [x] **Step 3: 全部の検査を通す**

Run: `PYTHONUTF8=1 python -m pytest -q`
Expected: 全部 `passed`（656）

Run: `PYTHONUTF8=1 python -m src.build`
Expected: `ビルド完了: 208ファイル`

- [x] **Step 4: コミットして push**

```bash
git add CLAUDE.md SESSION_HANDOFF.md docs/superpowers/plans/2026-09-20-site-search.md
git commit -m "docs: サイト内検索の運用メモと実装計画"
git push origin main
```

- [x] **Step 5: 配信と本番を確かめる**

GitHub API を1回だけ叩く（未認証は60回/時。連打しない）:

Run: `PYTHONUTF8=1 python -c "import urllib.request,json;d=json.load(urllib.request.urlopen(urllib.request.Request('https://api.github.com/repos/invest-ai-info/ai-tsukaikata/actions/runs?per_page=3',headers={'User-Agent':'x'})));[print(r['name'],r['status'],r['conclusion'],r['head_sha'][:7]) for r in d['workflow_runs']]"`
Expected: `Build & Deploy Site completed success <push の sha>`（queued/in_progress なら数分待ってもう1回）

本番: `PYTHONUTF8=1 python -c "import urllib.request;[print(u,urllib.request.urlopen(u).status) for u in ('https://ai-tsukaikata.com/search/?q=Gmail','https://ai-tsukaikata.com/search.json')]"`
Expected: 両方 `200`。ブラウザで `https://ai-tsukaikata.com/search/?q=Gmail` を開いて結果が出る（`navigate` → `read_page`）
