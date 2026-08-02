# AIの使い方（サイト本体） Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `ai-tsukaikata.com` を Python製ミニSSGで生成し、トップ + レシピ記事5本 + 固定ページ2本を GitHub Pages に公開する。

**Architecture:** `src/` パッケージ。ファイルを**書く**のは `build.py` だけで、`content.py` / `render.py` / `feeds.py` / `validate.py` は入力を受けて値を返すだけ。テストはディスクをほぼ触らずに済む。検証に1件でもエラーがあれば何も書かずに終了する（「全部通る or 何も出さない」）。GitHub Actions が push のたびに テスト → ビルド → Pages 配信 を行う。

**Tech Stack:** Python 3.12 / Jinja2 / Markdown（python-markdown） / PyYAML（導入済み） / pytest / GitHub Actions / GitHub Pages

**設計書:** [2026-08-01-ai-tsukaikata-site-design.md](../specs/2026-08-01-ai-tsukaikata-site-design.md)

**設計書からの差分（意図的）:**

1. **`src/config.py` を追加する。** 設計書のモジュール表には無いが、サイト名・URL・カテゴリ定義を `render.py` と `feeds.py` の両方が必要とする。定数を両方に書くと片方だけ直して不整合になるため、1箇所にまとめる。
2. **slug 重複ではなく URL 重複を検査する。** 設計書 §6 は「slug 重複」だが、`content/pages/recipes.md` は slug が一意でも `/recipes/` とぶつかる。URL で見ればこの事故も同時に捕まる。
3. **空のカテゴリの一覧ページは生成しない。** 初回公開時点で `tools` は0本。空の一覧ページはSEO上もAdSense審査上も不利なので、記事が1本もないカテゴリはナビからも消す。
4. **`build/CNAME` をビルド時に生成する。** 生成HTMLをリポジトリにコミットしない方式では、`CNAME` を artifact に含めないと独自ドメインが毎回外れる。

---

## File Structure

| ファイル | 責務 | 外界に触るか |
|---|---|---|
| `src/config.py` | サイト名・URL・カテゴリ定義 | しない |
| `src/content.py` | frontmatter + Markdown → `Article` | 読むだけ |
| `src/validate.py` | `Article` のリスト → エラー文字列のリスト | しない |
| `src/render.py` | `Article` のリスト → `{出力パス: HTML}` | テンプレを読むだけ |
| `src/feeds.py` | `Article` のリスト → RSS / sitemap / robots | しない |
| `src/build.py` | 上記を呼び `build/` に書き出す | **書く（ここだけ）** |
| `templates/base.html` | 共通レイアウト（head・ヘッダ・フッタ） | — |
| `templates/_macros.html` | 記事カード（トップと一覧で共用） | — |
| `templates/index.html` | トップ | — |
| `templates/list.html` | カテゴリ一覧 | — |
| `templates/article.html` | 記事ページ | — |
| `static/style.css` | 唯一のCSS | — |
| `.github/workflows/build.yml` | テスト → ビルド → Pages 配信 | — |

生成物 `build/` は `.gitignore` 済み（既存の `.gitignore` 4行目）。追記は不要。

---

### Task 1: 土台（依存・パッケージ・定数）

**Files:**
- Modify: `requirements.txt`
- Create: `src/__init__.py`
- Create: `src/config.py`

- [ ] **Step 1: 依存を追加する**

`requirements.txt`（全文）:
```
feedparser>=6.0.11
PyYAML>=6.0.1
pytest>=8.0.0
Jinja2>=3.1.4
Markdown>=3.6
```

- [ ] **Step 2: 依存をインストールする**

Run: `pip install -r requirements.txt`
Expected: Jinja2 と Markdown（と MarkupSafe）がインストールされる。既存3件はスキップ

- [ ] **Step 3: パッケージと定数を作る**

`src/__init__.py`: 空ファイル

`src/config.py`:
```python
# -*- coding: utf-8 -*-
"""サイト全体の定数。サイト名やURLを変えるときはここだけを触る。

render.py と feeds.py の両方が同じ値を必要とするため、両方に書かず
ここに集約する。
"""
from __future__ import annotations

SITE_NAME = "AIの使い方"
SITE_URL = "https://ai-tsukaikata.com"
CUSTOM_DOMAIN = "ai-tsukaikata.com"
SITE_DESCRIPTION = "プログラマーでなくても動かせる、実際に運用している自動化の手順書。"
SITE_LANG = "ja"

# 一覧ページを持つカテゴリ。pages（about等）は一覧に出さない
LISTED_CATEGORIES = ("recipes", "tools")

CATEGORIES = {
    "recipes": {
        "label": "レシピ",
        "description": "実際に動かしている自動化を、コピペできる手順にしたものです。",
    },
    "tools": {
        "label": "ツール",
        "description": "自分で使っているAIツールの使い方と、向き不向き。",
    },
    "pages": {"label": "", "description": ""},
}

INDEX_MAX_ARTICLES = 12
```

- [ ] **Step 4: import できることを確認する**

Run: `python -c "from src import config; print(config.SITE_NAME)"`
Expected: `AIの使い方`

- [ ] **Step 5: 既存テストが壊れていないことを確認する**

Run: `python -m pytest -q`
Expected: PASS（142 passed。トラッカーのテストに影響しない）

- [ ] **Step 6: Commit**

```bash
git add requirements.txt src/__init__.py src/config.py
git commit -m "chore: サイト生成の土台（依存・srcパッケージ・サイト定数）を追加"
```

---

### Task 2: `content.py` — frontmatter と Markdown

Markdown 1本を `Article` にする。壊れた記事は例外にせず**エラーを集めて返す**。1本直して再実行、の往復を避けるため。

**Files:**
- Create: `src/content.py`
- Test: `tests/test_content.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_content.py`:
````python
# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path

import pytest

from src.content import (
    Article,
    ArticleError,
    load_articles,
    parse_article,
    render_markdown,
    split_frontmatter,
)

RECIPE = """---
title: テスト記事
description: これはテストです。
category: recipes
published: 2026-08-01
tags: [GitHub Actions, 自動化]
time_required: 30分
cost: 無料
---

本文です。
"""

PAGE = """---
title: このサイトについて
description: 運営者と方針。
category: pages
published: 2026-08-01
---

固定ページの本文。
"""


def _write(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_split_frontmatter_returns_meta_and_body():
    meta, body = split_frontmatter(RECIPE)
    assert meta["title"] == "テスト記事"
    assert body.strip() == "本文です。"


def test_split_frontmatter_without_frontmatter_raises():
    with pytest.raises(ArticleError):
        split_frontmatter("いきなり本文が始まる記事")


def test_split_frontmatter_with_broken_yaml_raises():
    with pytest.raises(ArticleError):
        split_frontmatter("---\ntitle: [壊れた\n---\n本文\n")


def test_parse_article_reads_all_fields():
    article = parse_article(Path("content/recipes/sample.md"), RECIPE)
    assert article.title == "テスト記事"
    assert article.description == "これはテストです。"
    assert article.category == "recipes"
    assert article.published == date(2026, 8, 1)
    assert article.updated is None
    assert article.tags == ("GitHub Actions", "自動化")
    assert article.time_required == "30分"
    assert article.cost == "無料"
    assert "本文です。" in article.body_html


def test_parse_article_slug_comes_from_filename():
    article = parse_article(Path("content/recipes/my-slug.md"), RECIPE)
    assert article.slug == "my-slug"


def test_recipe_url_and_output_path():
    article = parse_article(Path("content/recipes/my-slug.md"), RECIPE)
    assert article.url == "/recipes/my-slug/"
    assert article.output_path == "recipes/my-slug/index.html"


def test_page_url_is_top_level():
    article = parse_article(Path("content/pages/about.md"), PAGE)
    assert article.url == "/about/"
    assert article.output_path == "about/index.html"


def test_missing_required_field_raises():
    text = RECIPE.replace("description: これはテストです。\n", "")
    with pytest.raises(ArticleError, match="description"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_recipe_without_time_required_raises():
    text = RECIPE.replace("time_required: 30分\n", "")
    with pytest.raises(ArticleError, match="time_required"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_page_does_not_require_time_required():
    article = parse_article(Path("content/pages/about.md"), PAGE)
    assert article.time_required is None


def test_unknown_category_raises():
    text = RECIPE.replace("category: recipes", "category: blog")
    with pytest.raises(ArticleError, match="カテゴリ"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_non_url_safe_slug_raises():
    with pytest.raises(ArticleError, match="ファイル名"):
        parse_article(Path("content/recipes/日本語.md"), RECIPE)


def test_quoted_date_raises():
    text = RECIPE.replace("published: 2026-08-01", 'published: "2026年8月1日"')
    with pytest.raises(ArticleError, match="published"):
        parse_article(Path("content/recipes/sample.md"), text)


def test_updated_is_parsed_when_present():
    text = RECIPE.replace("published: 2026-08-01", "published: 2026-08-01\nupdated: 2026-08-10")
    article = parse_article(Path("content/recipes/sample.md"), text)
    assert article.updated == date(2026, 8, 10)


def test_render_markdown_makes_fenced_code_block():
    html = render_markdown("```bash\npip install foo\n```")
    assert "<code>" in html
    assert "pip install foo" in html


def test_render_markdown_makes_table():
    html = render_markdown("| a | b |\n|---|---|\n| 1 | 2 |")
    assert "<table>" in html


def test_render_markdown_escapes_raw_html_characters_in_code():
    html = render_markdown("```\n<script>alert(1)</script>\n```")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_load_articles_collects_errors_without_raising(tmp_path):
    _write(tmp_path / "recipes", "good.md", RECIPE)
    _write(tmp_path / "recipes", "bad.md", "frontmatterがない")
    articles, errors = load_articles(tmp_path)
    assert [a.slug for a in articles] == ["good"]
    assert len(errors) == 1
    assert "bad.md" in errors[0]


def test_load_articles_sorts_newest_first(tmp_path):
    _write(tmp_path / "recipes", "old.md", RECIPE.replace("2026-08-01", "2026-07-01"))
    _write(tmp_path / "recipes", "new.md", RECIPE)
    articles, errors = load_articles(tmp_path)
    assert errors == []
    assert [a.slug for a in articles] == ["new", "old"]


def test_load_articles_skips_underscore_files(tmp_path):
    _write(tmp_path, "_ideas.md", "記事ネタのメモ")
    articles, errors = load_articles(tmp_path)
    assert articles == []
    assert errors == []
````

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_content.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.content'`

- [ ] **Step 3: 実装する**

`src/content.py`:
```python
# -*- coding: utf-8 -*-
"""content/ の Markdown を読んで Article にする。

テンプレートもHTMLの組み立ても知らない。ここが知っているのは
「frontmatter付きMarkdownという入力形式」だけ。
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml

from .config import CATEGORIES

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")

REQUIRED_FIELDS = ("title", "description", "category", "published")
RECIPE_REQUIRED_FIELDS = ("time_required", "cost")
MARKDOWN_EXTENSIONS = ["fenced_code", "tables", "sane_lists", "attr_list"]


class ArticleError(Exception):
    """記事1本を Article にできないときに投げる。"""


@dataclass(frozen=True)
class Article:
    slug: str
    title: str
    description: str
    category: str
    published: date
    updated: date | None
    tags: tuple[str, ...]
    time_required: str | None
    cost: str | None
    body_html: str
    source_path: Path

    @property
    def url(self) -> str:
        """公開URL。末尾スラッシュ形式に統一する。"""
        if self.category == "pages":
            return f"/{self.slug}/"
        return f"/{self.category}/{self.slug}/"

    @property
    def output_path(self) -> str:
        return self.url.strip("/") + "/index.html"


def split_frontmatter(text: str) -> tuple[dict, str]:
    """先頭の --- で囲まれたYAMLと本文に分ける。"""
    match = FRONTMATTER_RE.match(text.lstrip("\ufeff"))
    if not match:
        raise ArticleError("先頭に --- で囲まれた frontmatter がありません")
    try:
        meta = yaml.safe_load(match.group(1))
    except yaml.YAMLError as error:
        raise ArticleError(f"frontmatter のYAMLが壊れています: {error}") from error
    if not isinstance(meta, dict):
        raise ArticleError("frontmatter が「項目: 値」の形になっていません")
    return meta, match.group(2)


def render_markdown(body: str) -> str:
    return markdown.markdown(body, extensions=MARKDOWN_EXTENSIONS, output_format="html")


def _to_date(value, field: str) -> date:
    """PyYAML が日付として解釈した値だけを受け付ける。

    クォートで囲むと文字列になり、ここで落ちる。日付形式の揺れを
    frontmatter の時点で1つに固定するため。
    """
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    raise ArticleError(f"{field} は YYYY-MM-DD 形式で書いてください（今の値: {value!r}）")


def parse_article(source_path: Path, text: str) -> Article:
    """Markdown 1本を Article にする。ディスクには触らない。"""
    source_path = Path(source_path)
    slug = source_path.stem
    if not SLUG_RE.match(slug):
        raise ArticleError(
            f"ファイル名は半角小文字・数字・ハイフンだけにしてください（URLになります）: {slug}"
        )

    meta, body = split_frontmatter(text)

    missing = [field for field in REQUIRED_FIELDS if not meta.get(field)]
    if missing:
        raise ArticleError("必須項目がありません: " + ", ".join(missing))

    category = str(meta["category"])
    if category not in CATEGORIES:
        raise ArticleError(
            f"知らないカテゴリです: {category}（{' / '.join(CATEGORIES)} のいずれか）"
        )

    if category == "recipes":
        missing = [field for field in RECIPE_REQUIRED_FIELDS if not meta.get(field)]
        if missing:
            raise ArticleError("レシピの必須項目がありません: " + ", ".join(missing))

    tags = meta.get("tags") or []
    if not isinstance(tags, list):
        raise ArticleError("tags は [A, B] のリスト形式で書いてください")

    return Article(
        slug=slug,
        title=str(meta["title"]),
        description=str(meta["description"]),
        category=category,
        published=_to_date(meta["published"], "published"),
        updated=_to_date(meta["updated"], "updated") if meta.get("updated") else None,
        tags=tuple(str(tag) for tag in tags),
        time_required=str(meta["time_required"]) if meta.get("time_required") else None,
        cost=str(meta["cost"]) if meta.get("cost") else None,
        body_html=render_markdown(body),
        source_path=source_path,
    )


def load_articles(content_dir: Path) -> tuple[list[Article], list[str]]:
    """content/ 以下を全部読む。

    1本壊れていても止めずに最後まで読み、エラーを集めて返す。
    直して再実行、を1往復で済ませるため。
    """
    articles: list[Article] = []
    errors: list[str] = []
    for path in sorted(Path(content_dir).rglob("*.md")):
        if path.name.startswith("_"):
            continue
        try:
            articles.append(parse_article(path, path.read_text(encoding="utf-8")))
        except ArticleError as error:
            errors.append(f"{path}: {error}")
    articles.sort(key=lambda article: (article.published, article.slug), reverse=True)
    return articles, errors
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_content.py -q`
Expected: PASS（20 passed）

- [ ] **Step 5: Commit**

```bash
git add src/content.py tests/test_content.py
git commit -m "feat: frontmatter付きMarkdownをArticleにする読み込みを追加"
```

---

### Task 3: `validate.py` — 公開前チェック

このサイト最大のリスクは**機密の混入**。記事化のたびに人間の注意力に頼る運用は必ず事故を起こすので、コードで止める。ここはテストを厚くする。

**Files:**
- Create: `src/validate.py`
- Test: `tests/test_validate.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_validate.py`:
```python
# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path

import pytest

from src.content import Article, render_markdown
from src.validate import validate


def _article(body="ふつうの本文です。", slug="sample", category="recipes", title="題名", **kwargs):
    defaults = dict(
        slug=slug,
        title=title,
        description="説明文です。",
        category=category,
        published=date(2026, 8, 1),
        updated=None,
        tags=(),
        time_required="30分" if category == "recipes" else None,
        cost="無料" if category == "recipes" else None,
        body_html=render_markdown(body),
        source_path=Path(f"content/{category}/{slug}.md"),
    )
    defaults.update(kwargs)
    return Article(**defaults)


def test_clean_article_has_no_errors():
    assert validate([_article()]) == []


# 検査用のダミー。接頭辞と本体を分けて組み立てる。完全な形で書くと、
# 偽物でもGitHubのシークレット検出に引っかかって push が拒否される。
FAKE_TOKENS = [
    "ghp_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "github_" + "pat_11ABCDEFG0abcdefghijklmnopqrstuvwxyz012345",
    "sk-" + "ant-api03-AbCdEfGhIjKlMnOpQrStUvWxYz0123456789",
    "AKIA" + "IOSFODNN7EXAMPLE",
    "xoxb-" + "1234567890-abcdefghijklmnop",
]


@pytest.mark.parametrize("secret", FAKE_TOKENS)
def test_token_shaped_string_is_detected(secret):
    errors = validate([_article(body=f"設定値は {secret} です。")])
    assert len(errors) == 1


def test_credential_assignment_is_detected():
    errors = validate([_article(body="api_key=8Kd93jfMs02nfLq1")])
    assert any("認証情報" in error for error in errors)


def test_placeholder_credential_is_allowed():
    assert validate([_article(body="api_key=your-api-key-here")]) == []


def test_github_actions_secrets_reference_is_allowed():
    body = "```yaml\nenv:\n  GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}\n```"
    assert validate([_article(body=body)]) == []


def test_raw_email_is_detected():
    errors = validate([_article(body="連絡先は taro.yamada@gmail.com です。")])
    assert any("メールアドレス" in error for error in errors)


@pytest.mark.parametrize("address", [
    "you@example.com",
    "41898282+github-actions[bot]@users.noreply.github.com",
])
def test_safe_email_domain_is_allowed(address):
    assert validate([_article(body=f"宛先には {address} を使います。")]) == []


def test_local_windows_path_is_detected():
    errors = validate([_article(body=r"作業場所は C:\Users\taro\project です。")])
    assert any("絶対パス" in error for error in errors)


def test_placeholder_windows_path_is_allowed():
    assert validate([_article(body=r"作業場所は C:\Users\<ユーザー名>\project です。")]) == []


def test_secret_in_title_is_detected():
    errors = validate([_article(title=f"{FAKE_TOKENS[0]} の使い方")])
    assert len(errors) == 1


def test_duplicate_url_is_detected():
    errors = validate([_article(slug="same"), _article(slug="same")])
    assert any("重複" in error for error in errors)


def test_page_slug_colliding_with_category_is_detected():
    page = _article(slug="recipes", category="pages")
    errors = validate([page])
    assert any("予約" in error for error in errors)


def test_category_not_matching_directory_is_detected():
    article = _article(category="recipes", source_path=Path("content/tools/sample.md"))
    errors = validate([article])
    assert any("置き場所" in error for error in errors)


def test_broken_internal_link_is_detected():
    errors = validate([_article(body="[これ](/recipes/nothing-here/)を見てください。")])
    assert any("リンク先" in error for error in errors)


def test_valid_internal_link_passes():
    target = _article(slug="target")
    source = _article(slug="source", body="[あれ](/recipes/target/)を見てください。")
    assert validate([target, source]) == []


def test_link_to_category_list_passes():
    assert validate([_article(body="[一覧](/recipes/)を見てください。")]) == []


def test_link_to_static_file_passes():
    assert validate([_article(body="[CSS](/static/style.css)")]) == []


def test_external_link_is_not_checked():
    assert validate([_article(body="[GitHub](https://github.com/nothing/here)")]) == []


def test_affiliate_link_without_disclosure_is_detected():
    errors = validate([_article(body="[商品](https://px.a8.net/svt/ejp?a8mat=abc)")])
    assert any("広告" in error for error in errors)


def test_affiliate_link_with_disclosure_passes():
    body = "この記事には広告が含まれます。\n\n[商品](https://px.a8.net/svt/ejp?a8mat=abc)"
    assert validate([_article(body=body)]) == []


def test_all_errors_are_collected_not_just_the_first():
    body = (
        "連絡は taro.yamada@gmail.com へ。\n\n"
        r"作業場所は C:\Users\taro です。" + "\n\n"
        "[これ](/recipes/nothing-here/)も見てください。\n"
    )
    errors = validate([_article(body=body)])
    assert len(errors) == 3
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_validate.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.validate'`

- [ ] **Step 3: 実装する**

`src/validate.py`:
```python
# -*- coding: utf-8 -*-
"""公開前チェック。何も書かず、エラー文字列のリストを返すだけ。

最初のエラーで止めず全部集める。1個直して再実行、の往復を避けるため。

広告表記のチェックは景表法のステマ規制対応で、法的に必須の項目。
人間の記憶ではなくここで強制する。（本ファイルは法的助言ではない）
"""
from __future__ import annotations

import html
import re

from . import config
from .content import Article

TOKEN_PATTERNS = (
    (re.compile(r"ghp_[A-Za-z0-9]{20,}"), "GitHubのトークン"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "GitHubのトークン"),
    (re.compile(r"sk-ant-[A-Za-z0-9\-_]{20,}"), "AnthropicのAPIキー"),
    (re.compile(r"sk-[A-Za-z0-9]{32,}"), "OpenAIのAPIキー"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AWSのアクセスキー"),
    (re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}"), "Slackのトークン"),
)

CREDENTIAL_RE = re.compile(
    r"(?i)(password|passwd|api[_\- ]?key|secret[_\- ]?key|access[_\- ]?token)"
    r"\s*[=:]\s*[\"']?([A-Za-z0-9/+_\-]{8,})"
)

# ダミー値まで落とすと記事が書けなくなるので、明らかな穴埋め語は通す
PLACEHOLDER_HINTS = (
    "your", "xxx", "dummy", "example", "sample", "here",
    "changeme", "placeholder", "secrets.", "env.",
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-\[\]]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
SAFE_EMAIL_DOMAINS = (
    "example.com", "example.org", "example.net", "users.noreply.github.com",
)

# C:\Users\<ユーザー名> のような穴埋めは通し、実在しそうな名前だけ落とす
LOCAL_PATH_RE = re.compile(r"C:\\Users\\(?![<%{＜])")

AFFILIATE_PATTERNS = (
    re.compile(r"a8\.net"),
    re.compile(r"moshimo\.com"),
    re.compile(r"valuecommerce\."),
    re.compile(r"accesstrade\."),
    re.compile(r"amzn\.to"),
    re.compile(r"hb\.afl\.rakuten"),
    re.compile(r"amazon\.co\.jp/[^\s\"')]*[?&]tag="),
)
DISCLOSURE_WORDS = ("広告", "PR", "アフィリエイト", "プロモーション")

INTERNAL_LINK_RE = re.compile(r'href="(/[^"]*)"')
ALWAYS_VALID_PATHS = ("/", "/feed.xml", "/sitemap.xml", "/robots.txt")


def _looks_like_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(hint in lowered for hint in PLACEHOLDER_HINTS)


def _secret_errors(where: str, text: str) -> list[str]:
    """機密らしきものを探す。トークンの中身はエラー文に出さない。"""
    errors: list[str] = []

    for pattern, label in TOKEN_PATTERNS:
        if pattern.search(text):
            errors.append(f"{where}: {label}らしき文字列が含まれています")

    for match in CREDENTIAL_RE.finditer(text):
        if _looks_like_placeholder(match.group(2)):
            continue
        errors.append(f"{where}: 認証情報らしき代入があります（{match.group(1)}=…）")

    for match in EMAIL_RE.finditer(text):
        address = match.group(0)
        if address.lower().endswith(SAFE_EMAIL_DOMAINS):
            continue
        errors.append(f"{where}: メールアドレス {address} が本文に含まれています")

    if LOCAL_PATH_RE.search(text):
        errors.append(f"{where}: ローカルの絶対パス（C:\\Users\\…）が含まれています")

    return errors


def _has_affiliate_link(text: str) -> bool:
    return any(pattern.search(text) for pattern in AFFILIATE_PATTERNS)


def _link_errors(where: str, body_html: str, valid_paths: set[str]) -> list[str]:
    errors = []
    for raw in INTERNAL_LINK_RE.findall(body_html):
        path = raw.split("#")[0].split("?")[0]
        if not path or path.startswith("/static/"):
            continue
        if path in valid_paths:
            continue
        errors.append(f"{where}: リンク先 {raw} が存在しません")
    return errors


def validate(articles: list[Article]) -> list[str]:
    """全記事を検査してエラー文字列のリストを返す。空なら公開してよい。"""
    errors: list[str] = []

    reserved = {"/"} | {f"/{name}/" for name in config.LISTED_CATEGORIES}
    valid_paths = set(ALWAYS_VALID_PATHS) | reserved | {a.url for a in articles}
    taken: dict[str, str] = {}

    for article in articles:
        where = str(article.source_path)
        text = html.unescape(article.body_html)

        errors += _secret_errors(where, text)
        errors += _secret_errors(where, f"{article.title} {article.description}")

        if article.source_path.parent.name != article.category:
            errors.append(
                f"{where}: 置き場所とカテゴリが食い違っています"
                f"（category: {article.category} / フォルダ: {article.source_path.parent.name}/）"
            )

        if article.url in reserved:
            errors.append(f"{where}: {article.url} はサイトが使う予約済みURLです")
        elif article.url in taken:
            errors.append(f"{where}: URL {article.url} が {taken[article.url]} と重複しています")
        else:
            taken[article.url] = where

        errors += _link_errors(where, article.body_html, valid_paths)

        if _has_affiliate_link(text) and not any(word in text for word in DISCLOSURE_WORDS):
            errors.append(
                f"{where}: アフィリエイトリンクがあるのに「広告」「PR」の表記がありません"
            )

    return errors
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_validate.py -q`
Expected: PASS（26 passed）

- [ ] **Step 5: Commit**

```bash
git add src/validate.py tests/test_validate.py
git commit -m "feat: 機密混入・URL重複・リンク切れ・広告表記の公開前チェックを追加"
```

---

### Task 4: テンプレートと `render.py`

**Files:**
- Create: `templates/base.html`
- Create: `templates/_macros.html`
- Create: `templates/index.html`
- Create: `templates/list.html`
- Create: `templates/article.html`
- Create: `src/render.py`
- Test: `tests/test_render.py`

- [ ] **Step 1: 共通レイアウトを作る**

`templates/base.html`:
```html
<!DOCTYPE html>
<html lang="{{ site.lang }}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% if page_title %}{{ page_title }} | {{ site.name }}{% else %}{{ site.name }}{% endif %}</title>
<meta name="description" content="{{ description }}">
<link rel="canonical" href="{{ canonical }}">
<meta property="og:type" content="{{ og_type }}">
<meta property="og:title" content="{% if page_title %}{{ page_title }}{% else %}{{ site.name }}{% endif %}">
<meta property="og:description" content="{{ description }}">
<meta property="og:url" content="{{ canonical }}">
<meta property="og:site_name" content="{{ site.name }}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/rss+xml" title="{{ site.name }}" href="{{ site.url }}/feed.xml">
<link rel="stylesheet" href="/static/style.css">
</head>
<body>
<header class="site-header">
  <a class="site-name" href="/">{{ site.name }}</a>
  <nav class="site-nav">
    {% for item in nav %}
    <a href="{{ item.url }}">{{ item.label }}</a>
    {% endfor %}
  </nav>
</header>

<main class="site-main">
{% block content %}{% endblock %}
</main>

<footer class="site-footer">
  <nav class="footer-nav">
    <a href="/about/">このサイトについて</a>
    <a href="/privacy/">プライバシーポリシー</a>
    <a href="/feed.xml">RSS</a>
  </nav>
  <p class="copyright">© {{ site.name }}</p>
</footer>
</body>
</html>
```

- [ ] **Step 2: 記事カードのマクロを作る**

`templates/_macros.html`:
```html
{% macro card(article) %}
<article class="card">
  <h2 class="card-title"><a href="{{ article.url }}">{{ article.title }}</a></h2>
  <p class="card-description">{{ article.description }}</p>
  <p class="card-meta">
    <time datetime="{{ article.published.isoformat() }}">{{ article.published | jp_date }}</time>
    {% if article.time_required %}<span class="card-badge">{{ article.time_required }}</span>{% endif %}
    {% if article.cost %}<span class="card-badge">{{ article.cost }}</span>{% endif %}
  </p>
</article>
{% endmacro %}
```

- [ ] **Step 3: トップ・一覧・記事のテンプレートを作る**

`templates/index.html`（`{% import %}` はブロックの**中**に置く。Jinja2 では子テンプレートのトップレベルで定義した名前がブロック内から見えないことがあるため）:
```html
{% extends "base.html" %}
{% block content %}
{% import "_macros.html" as macros %}
<section class="hero">
  <h1>{{ site.name }}</h1>
  <p class="hero-lead">{{ site.description }}</p>
  <p class="hero-note">ここに載っているのは、運営者が自分で毎日動かしているものだけです。動かしていないものは書きません。</p>
</section>

<section class="article-list">
  <h2 class="section-title">新着</h2>
  {% for article in articles %}
  {{ macros.card(article) }}
  {% endfor %}
</section>
{% endblock %}
```

`templates/list.html`:
```html
{% extends "base.html" %}
{% block content %}
{% import "_macros.html" as macros %}
<section class="article-list">
  <h1 class="section-title">{{ category_label }}</h1>
  <p class="section-lead">{{ description }}</p>
  {% for article in articles %}
  {{ macros.card(article) }}
  {% endfor %}
</section>
{% endblock %}
```

`templates/article.html`:
```html
{% extends "base.html" %}
{% block content %}
<article class="article">
  {% if category_label %}
  <p class="breadcrumb"><a href="/">ホーム</a> › <a href="{{ category_url }}">{{ category_label }}</a></p>
  {% endif %}

  <h1 class="article-title">{{ article.title }}</h1>

  <p class="article-meta">
    <time datetime="{{ article.published.isoformat() }}">{{ article.published | jp_date }} 公開</time>
    {% if article.updated %}
    <time datetime="{{ article.updated.isoformat() }}">{{ article.updated | jp_date }} 更新</time>
    {% endif %}
  </p>

  {% if article.time_required or article.cost %}
  <dl class="recipe-meta">
    {% if article.time_required %}
    <div><dt>かかる時間</dt><dd>{{ article.time_required }}</dd></div>
    {% endif %}
    {% if article.cost %}
    <div><dt>費用</dt><dd>{{ article.cost }}</dd></div>
    {% endif %}
  </dl>
  {% endif %}

  <div class="article-body">{{ article.body_html | safe }}</div>

  {% if article.tags %}
  <p class="tags">{% for tag in article.tags %}<span class="tag">{{ tag }}</span>{% endfor %}</p>
  {% endif %}
</article>
{% endblock %}
```

- [ ] **Step 4: 失敗するテストを書く**

`tests/test_render.py`:
```python
# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path

from src.content import Article, render_markdown
from src.render import render_site


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


def test_index_contains_site_name_and_article_titles():
    pages = render_site([_article(title="レシピ1")])
    assert "AIの使い方" in pages["index.html"]
    assert "レシピ1" in pages["index.html"]


def test_article_page_contains_title_and_body():
    pages = render_site([_article(title="固有の題名", body="固有の本文")])
    html = pages["recipes/sample/index.html"]
    assert "固有の題名" in html
    assert "固有の本文" in html


def test_article_page_has_canonical_and_ogp():
    pages = render_site([_article()])
    html = pages["recipes/sample/index.html"]
    assert '<link rel="canonical" href="https://ai-tsukaikata.com/recipes/sample/">' in html
    assert 'property="og:url" content="https://ai-tsukaikata.com/recipes/sample/"' in html
    assert 'property="og:type" content="article"' in html


def test_title_is_escaped():
    pages = render_site([_article(title="A <script>alert(1)</script> B")])
    html = pages["recipes/sample/index.html"]
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_body_html_is_not_escaped():
    pages = render_site([_article(body="**強調**")])
    assert "<strong>強調</strong>" in pages["recipes/sample/index.html"]


def test_recipe_meta_is_shown():
    pages = render_site([_article()])
    html = pages["recipes/sample/index.html"]
    assert "かかる時間" in html
    assert "30分" in html


def test_page_has_no_recipe_meta():
    pages = render_site([_article(slug="about", category="pages")])
    html = pages["about/index.html"]
    assert "かかる時間" not in html


def test_list_page_is_generated_for_non_empty_category():
    pages = render_site([_article()])
    assert "recipes/index.html" in pages


def test_list_page_is_not_generated_for_empty_category():
    pages = render_site([_article()])
    assert "tools/index.html" not in pages


def test_nav_omits_empty_category():
    pages = render_site([_article()])
    assert 'href="/recipes/"' in pages["index.html"]
    assert 'href="/tools/"' not in pages["index.html"]


def test_pages_are_not_listed_on_index():
    pages = render_site([_article(slug="about", category="pages", title="固定ページの題名")])
    assert "固定ページの題名" not in pages["index.html"]
    assert 'href="/about/"' in pages["index.html"]  # フッタのリンクとしては出る


def test_output_paths_use_trailing_slash_structure():
    pages = render_site([_article(), _article(slug="about", category="pages")])
    assert set(pages) == {
        "index.html",
        "recipes/index.html",
        "recipes/sample/index.html",
        "about/index.html",
    }


def test_japanese_date_format():
    pages = render_site([_article(published=date(2026, 8, 1))])
    assert "2026年8月1日" in pages["recipes/sample/index.html"]
```

- [ ] **Step 5: テストが失敗することを確認する**

Run: `python -m pytest tests/test_render.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.render'`

- [ ] **Step 6: 実装する**

`src/render.py`:
```python
# -*- coding: utf-8 -*-
"""Article のリストを {出力パス: HTML} にする。ファイルは書かない。

autoescape を有効にしてあるので、記事タイトルにHTMLが混ざっても
そのままタグとして解釈されることはない。本文だけは Markdown 変換済みの
信頼できるHTMLなので | safe を通す。
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import config
from .content import Article

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


def jp_date(value: date) -> str:
    """2026年8月1日 の形にする。strftime の %-m は Windows で使えないため自前で組む。"""
    return f"{value.year}年{value.month}月{value.day}日"


def build_env(templates_dir: Path = TEMPLATES_DIR) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir), encoding="utf-8"),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["jp_date"] = jp_date
    env.globals["site"] = {
        "name": config.SITE_NAME,
        "url": config.SITE_URL,
        "description": config.SITE_DESCRIPTION,
        "lang": config.SITE_LANG,
    }
    return env


def render_site(articles: list[Article], env: Environment | None = None) -> dict[str, str]:
    """全ページを組み立てる。キーは build/ からの相対パス。"""
    env = env or build_env()

    listed = [a for a in articles if a.category in config.LISTED_CATEGORIES]
    active = [
        name for name in config.LISTED_CATEGORIES
        if any(a.category == name for a in listed)
    ]
    # 記事が1本もないカテゴリはナビにも一覧にも出さない（空ページを作らない）
    env.globals["nav"] = [
        {"url": f"/{name}/", "label": config.CATEGORIES[name]["label"]} for name in active
    ]

    pages: dict[str, str] = {}

    pages["index.html"] = env.get_template("index.html").render(
        page_title=None,
        description=config.SITE_DESCRIPTION,
        canonical=f"{config.SITE_URL}/",
        og_type="website",
        articles=listed[: config.INDEX_MAX_ARTICLES],
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

- [ ] **Step 7: テストが通ることを確認する**

Run: `python -m pytest tests/test_render.py -q`
Expected: PASS（13 passed）

- [ ] **Step 8: Commit**

```bash
git add templates/ src/render.py tests/test_render.py
git commit -m "feat: Jinja2テンプレートとHTML生成を追加"
```

---

### Task 5: `static/style.css`

読者は非エンジニアで、スマホで読む割合が高い。手順書としてコードブロックが読めることを最優先にする。

**Files:**
- Create: `static/style.css`

- [ ] **Step 1: CSSを書く**

`static/style.css`:
```css
/* AIの使い方 — 手順書として読めることを最優先にした最小限のCSS */

:root {
  --bg: #ffffff;
  --fg: #1f2328;
  --muted: #616b76;
  --line: #e3e6ea;
  --accent: #1a56b8;
  --code-bg: #f5f7f9;
  --card-bg: #fbfcfd;
  --max: 46rem;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14171a;
    --fg: #e6e9ec;
    --muted: #9aa4ae;
    --line: #2a2f35;
    --accent: #7ab0ff;
    --code-bg: #1c2126;
    --card-bg: #191d21;
  }
}

* { box-sizing: border-box; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Hiragino Sans",
    "Noto Sans JP", Meiryo, sans-serif;
  font-size: 17px;
  line-height: 1.9;
  -webkit-text-size-adjust: 100%;
}

a { color: var(--accent); }

/* --- ヘッダ / フッタ --- */

.site-header {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.25rem;
  align-items: baseline;
  max-width: var(--max);
  margin: 0 auto;
  padding: 1.25rem 1.1rem;
  border-bottom: 1px solid var(--line);
}

.site-name {
  font-weight: 700;
  font-size: 1.1rem;
  text-decoration: none;
  color: var(--fg);
}

.site-nav a {
  margin-right: 1rem;
  font-size: 0.95rem;
  text-decoration: none;
}

.site-nav a:hover, .site-name:hover { text-decoration: underline; }

.site-main {
  max-width: var(--max);
  margin: 0 auto;
  padding: 1.5rem 1.1rem 3rem;
}

.site-footer {
  max-width: var(--max);
  margin: 0 auto;
  padding: 1.5rem 1.1rem 3rem;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.9rem;
}

.footer-nav a { margin-right: 1rem; }
.copyright { margin: 0.75rem 0 0; }

/* --- トップ --- */

.hero { margin-bottom: 2.5rem; }
.hero h1 { font-size: 1.6rem; margin: 0 0 0.5rem; }
.hero-lead { margin: 0 0 0.5rem; font-size: 1.05rem; }
.hero-note { margin: 0; color: var(--muted); font-size: 0.92rem; }

.section-title {
  font-size: 1.15rem;
  margin: 0 0 0.25rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--line);
}

.section-lead { color: var(--muted); font-size: 0.95rem; margin: 0.5rem 0 1.5rem; }

/* --- 記事カード --- */

.card {
  padding: 1.1rem 1.2rem;
  margin: 1.1rem 0;
  background: var(--card-bg);
  border: 1px solid var(--line);
  border-radius: 10px;
}

.card-title { font-size: 1.1rem; margin: 0 0 0.4rem; line-height: 1.6; }
.card-title a { text-decoration: none; }
.card-title a:hover { text-decoration: underline; }
.card-description { margin: 0 0 0.6rem; color: var(--fg); font-size: 0.97rem; }

.card-meta {
  margin: 0;
  color: var(--muted);
  font-size: 0.85rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.card-badge {
  padding: 0.1rem 0.55rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: var(--bg);
}

/* --- 記事本文 --- */

.breadcrumb { color: var(--muted); font-size: 0.87rem; margin: 0 0 0.75rem; }

.article-title { font-size: 1.5rem; line-height: 1.55; margin: 0 0 0.6rem; }
.article-meta { color: var(--muted); font-size: 0.87rem; margin: 0 0 1.5rem; }
.article-meta time { margin-right: 1rem; }

.recipe-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 2rem;
  margin: 0 0 2rem;
  padding: 0.9rem 1.1rem;
  background: var(--card-bg);
  border: 1px solid var(--line);
  border-radius: 10px;
}

.recipe-meta div { display: flex; gap: 0.6rem; align-items: baseline; }
.recipe-meta dt { color: var(--muted); font-size: 0.85rem; margin: 0; }
.recipe-meta dd { margin: 0; font-weight: 600; }

.article-body h2 {
  font-size: 1.25rem;
  margin: 2.75rem 0 0.9rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--line);
}

.article-body h3 { font-size: 1.08rem; margin: 2rem 0 0.7rem; }
.article-body p { margin: 1.1rem 0; }
.article-body ul, .article-body ol { padding-left: 1.5rem; }
.article-body li { margin: 0.4rem 0; }

.article-body blockquote {
  margin: 1.5rem 0;
  padding: 0.2rem 1.1rem;
  border-left: 3px solid var(--line);
  color: var(--muted);
}

.article-body img { max-width: 100%; height: auto; }

/* コードは手順書の本体。折り返さず横スクロールさせる（コピペを壊さないため） */
.article-body pre {
  margin: 1.3rem 0;
  padding: 0.95rem 1.1rem;
  background: var(--code-bg);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow-x: auto;
  line-height: 1.7;
}

.article-body code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.88em;
}

.article-body p > code, .article-body li > code, .article-body td > code {
  padding: 0.12em 0.4em;
  background: var(--code-bg);
  border: 1px solid var(--line);
  border-radius: 4px;
}

.article-body pre code { padding: 0; background: none; border: none; }

.article-body table {
  width: 100%;
  margin: 1.3rem 0;
  border-collapse: collapse;
  font-size: 0.95rem;
  display: block;
  overflow-x: auto;
}

.article-body th, .article-body td {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--line);
  text-align: left;
}

.article-body th { background: var(--code-bg); }

.tags { margin: 2.5rem 0 0; display: flex; flex-wrap: wrap; gap: 0.5rem; }

.tag {
  padding: 0.15rem 0.65rem;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--muted);
  font-size: 0.82rem;
}

@media (max-width: 640px) {
  body { font-size: 16px; }
  .article-title { font-size: 1.32rem; }
  .site-header { padding: 1rem 0.9rem; }
  .site-main, .site-footer { padding-left: 0.9rem; padding-right: 0.9rem; }
}
```

- [ ] **Step 2: CSSが壊れていないことを目視で確認する**

Run: `python -c "print(len(open('static/style.css', encoding='utf-8').read().split('}')) - 1, 'ルール')"`
Expected: ルール数が表示される（`}` の対応が取れている目安。50前後）

- [ ] **Step 3: Commit**

```bash
git add static/style.css
git commit -m "feat: スタイルシートを追加。コードブロックは折り返さず横スクロール"
```

---

### Task 6: `feeds.py` — RSS / sitemap / robots

標準ライブラリの `xml.etree.ElementTree` で組み立てる。文字列連結で組むとタイトル中の `&` や `<` で壊れるため。

**Files:**
- Create: `src/feeds.py`
- Test: `tests/test_feeds.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_feeds.py`:
```python
# -*- coding: utf-8 -*-
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET

from src.content import Article, render_markdown
from src.feeds import build_robots, build_rss, build_sitemap

SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


def _article(slug="sample", category="recipes", title="題名", published=date(2026, 8, 1), **kwargs):
    defaults = dict(
        slug=slug,
        title=title,
        description="説明文です。",
        category=category,
        published=published,
        updated=None,
        tags=(),
        time_required="30分" if category == "recipes" else None,
        cost="無料" if category == "recipes" else None,
        body_html=render_markdown("本文です。"),
        source_path=Path(f"content/{category}/{slug}.md"),
    )
    defaults.update(kwargs)
    return Article(**defaults)


def test_rss_parses_as_xml():
    root = ET.fromstring(build_rss([_article()]))
    assert root.tag == "rss"
    assert root.find("channel/title").text == "AIの使い方"


def test_rss_uses_absolute_urls():
    root = ET.fromstring(build_rss([_article()]))
    assert root.find("channel/item/link").text == "https://ai-tsukaikata.com/recipes/sample/"


def test_rss_excludes_pages():
    xml = build_rss([_article(slug="about", category="pages", title="このサイトについて")])
    assert ET.fromstring(xml).find("channel/item") is None


def test_rss_limits_item_count():
    articles = [_article(slug=f"a{i}", published=date(2026, 7, 1)) for i in range(30)]
    root = ET.fromstring(build_rss(articles))
    assert len(root.findall("channel/item")) == 20


def test_rss_pubdate_is_rfc822():
    root = ET.fromstring(build_rss([_article()]))
    assert root.find("channel/item/pubDate").text.startswith("Sat, 01 Aug 2026")


def test_rss_escapes_special_characters():
    xml = build_rss([_article(title="A & B <C>")])
    assert ET.fromstring(xml).find("channel/item/title").text == "A & B <C>"


def test_sitemap_contains_article_and_section_urls():
    xml = build_sitemap([_article()], ("/", "/recipes/"))
    locs = [e.text for e in ET.fromstring(xml).iter(f"{SITEMAP_NS}loc")]
    assert "https://ai-tsukaikata.com/" in locs
    assert "https://ai-tsukaikata.com/recipes/" in locs
    assert "https://ai-tsukaikata.com/recipes/sample/" in locs


def test_sitemap_includes_pages():
    xml = build_sitemap([_article(slug="about", category="pages")], ("/",))
    locs = [e.text for e in ET.fromstring(xml).iter(f"{SITEMAP_NS}loc")]
    assert "https://ai-tsukaikata.com/about/" in locs


def test_sitemap_lastmod_prefers_updated():
    article = _article(published=date(2026, 8, 1), updated=date(2026, 8, 20))
    xml = build_sitemap([article], ("/",))
    lastmods = [e.text for e in ET.fromstring(xml).iter(f"{SITEMAP_NS}lastmod")]
    assert "2026-08-20" in lastmods


def test_robots_allows_all_and_points_to_sitemap():
    text = build_robots()
    assert "User-agent: *" in text
    assert "Disallow:" not in text
    assert "Sitemap: https://ai-tsukaikata.com/sitemap.xml" in text
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_feeds.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.feeds'`

- [ ] **Step 3: 実装する**

`src/feeds.py`:
```python
# -*- coding: utf-8 -*-
"""RSS / sitemap.xml / robots.txt を文字列で作る。標準ライブラリだけ。

文字列連結ではなく ElementTree で組む。記事タイトルに & や < が入ったとき、
手組みだと壊れたXMLを配信してしまうため。
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from email.utils import format_datetime
from xml.etree import ElementTree as ET

from . import config
from .content import Article

JST = timezone(timedelta(hours=9))
RSS_MAX_ITEMS = 20
XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\n'


def _published_at(article: Article) -> datetime:
    """日付しか持たない記事に、RSS用の時刻（JST 9:00）を与える。"""
    return datetime.combine(article.published, time(9, 0), tzinfo=JST)


def build_rss(articles: list[Article]) -> str:
    items = [a for a in articles if a.category in config.LISTED_CATEGORIES][:RSS_MAX_ITEMS]

    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:atom": "http://www.w3.org/2005/Atom",
    })
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = config.SITE_NAME
    ET.SubElement(channel, "link").text = f"{config.SITE_URL}/"
    ET.SubElement(channel, "description").text = config.SITE_DESCRIPTION
    ET.SubElement(channel, "language").text = config.SITE_LANG
    ET.SubElement(channel, "atom:link", {
        "href": f"{config.SITE_URL}/feed.xml",
        "rel": "self",
        "type": "application/rss+xml",
    })

    for article in items:
        url = config.SITE_URL + article.url
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = article.title
        ET.SubElement(item, "link").text = url
        ET.SubElement(item, "guid", {"isPermaLink": "true"}).text = url
        ET.SubElement(item, "description").text = article.description
        ET.SubElement(item, "pubDate").text = format_datetime(_published_at(article))

    return XML_HEADER + ET.tostring(rss, encoding="unicode")


def build_sitemap(articles: list[Article], section_paths: tuple[str, ...] = ("/",)) -> str:
    urlset = ET.Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    latest = max((a.updated or a.published for a in articles), default=None)

    for path in section_paths:
        node = ET.SubElement(urlset, "url")
        ET.SubElement(node, "loc").text = config.SITE_URL + path
        if latest is not None:
            ET.SubElement(node, "lastmod").text = latest.isoformat()

    for article in articles:
        node = ET.SubElement(urlset, "url")
        ET.SubElement(node, "loc").text = config.SITE_URL + article.url
        ET.SubElement(node, "lastmod").text = (article.updated or article.published).isoformat()

    return XML_HEADER + ET.tostring(urlset, encoding="unicode")


def build_robots() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {config.SITE_URL}/sitemap.xml\n"
    )
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_feeds.py -q`
Expected: PASS（10 passed）

- [ ] **Step 5: Commit**

```bash
git add src/feeds.py tests/test_feeds.py
git commit -m "feat: RSS・sitemap.xml・robots.txt の生成を追加"
```

---

### Task 7: `build.py` — 配線と書き出し

**「全部通る or 何も出さない」を守る。** 検証エラーが1件でもあれば、`build/` には一切触らずに exit 1 する。書き出す内容は全部メモリ上で作り切ってから書く。

**Files:**
- Create: `src/build.py`
- Test: `tests/test_build.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_build.py`:
```python
# -*- coding: utf-8 -*-
from pathlib import Path

from src import build

RECIPE = """---
title: テスト記事
description: これはテストです。
category: recipes
published: 2026-08-01
time_required: 30分
cost: 無料
---

本文です。
"""


def _content_dir(tmp_path: Path, text: str = RECIPE) -> Path:
    content = tmp_path / "content" / "recipes"
    content.mkdir(parents=True)
    (content / "sample.md").write_text(text, encoding="utf-8")
    return tmp_path / "content"


def test_collect_returns_all_expected_files(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path))
    assert errors == []
    assert set(files) >= {
        "index.html",
        "recipes/index.html",
        "recipes/sample/index.html",
        "feed.xml",
        "sitemap.xml",
        "robots.txt",
        "CNAME",
    }


def test_collect_writes_cname_for_custom_domain(tmp_path):
    files, _ = build.collect(_content_dir(tmp_path))
    assert files["CNAME"].strip() == "ai-tsukaikata.com"


def test_collect_returns_errors_and_no_files_when_invalid(tmp_path):
    broken = RECIPE.replace("本文です。", r"作業場所は C:\Users\taro です。")
    files, errors = build.collect(_content_dir(tmp_path, broken))
    assert files == {}
    assert len(errors) == 1


def test_collect_reports_unreadable_article(tmp_path):
    files, errors = build.collect(_content_dir(tmp_path, "frontmatterがない"))
    assert files == {}
    assert any("frontmatter" in error for error in errors)


def test_write_creates_directory_structure(tmp_path):
    build_dir = tmp_path / "build"
    build.write({"recipes/sample/index.html": "<p>x</p>"}, build_dir, tmp_path / "missing-static")
    assert (build_dir / "recipes" / "sample" / "index.html").read_text(encoding="utf-8") == "<p>x</p>"


def test_write_copies_static_directory(tmp_path):
    static = tmp_path / "static"
    static.mkdir()
    (static / "style.css").write_text("body{}", encoding="utf-8")
    build_dir = tmp_path / "build"
    build.write({"index.html": "<p>x</p>"}, build_dir, static)
    assert (build_dir / "static" / "style.css").read_text(encoding="utf-8") == "body{}"


def test_write_clears_previous_output(tmp_path):
    build_dir = tmp_path / "build"
    build_dir.mkdir()
    (build_dir / "stale.html").write_text("古い", encoding="utf-8")
    build.write({"index.html": "<p>x</p>"}, build_dir, tmp_path / "missing-static")
    assert not (build_dir / "stale.html").exists()


def test_main_writes_nothing_when_validation_fails(tmp_path, monkeypatch, capsys):
    broken = RECIPE.replace("本文です。", r"作業場所は C:\Users\taro です。")
    build_dir = tmp_path / "build"
    monkeypatch.setattr(build, "CONTENT_DIR", _content_dir(tmp_path, broken))
    monkeypatch.setattr(build, "BUILD_DIR", build_dir)

    assert build.main() == 1
    assert not build_dir.exists()
    assert "ビルド中止" in capsys.readouterr().err


def test_main_builds_successfully(tmp_path, monkeypatch):
    build_dir = tmp_path / "build"
    monkeypatch.setattr(build, "CONTENT_DIR", _content_dir(tmp_path))
    monkeypatch.setattr(build, "BUILD_DIR", build_dir)

    assert build.main() == 0
    assert (build_dir / "index.html").exists()
    assert (build_dir / "static" / "style.css").exists()
```

- [ ] **Step 2: テストが失敗することを確認する**

Run: `python -m pytest tests/test_build.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'src.build'`

- [ ] **Step 3: 実装する**

`src/build.py`:
```python
# -*- coding: utf-8 -*-
"""全体をつなぐ。ファイルを書くのはこのモジュールだけ。

検証エラーが1件でもあれば build/ に一切触らず exit 1 する。
「壊れた記事が1本あるせいで、直った記事だけ古いまま公開され続ける」
という中途半端な状態を作らないため。
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

from . import config, feeds, render
from .content import load_articles
from .validate import validate

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
STATIC_DIR = ROOT / "static"
BUILD_DIR = ROOT / "build"


def collect(content_dir: Path) -> tuple[dict[str, str], list[str]]:
    """書き出す内容を全部メモリ上で作る。(files, errors) を返す。"""
    articles, errors = load_articles(content_dir)
    errors = errors + validate(articles)
    if errors:
        return {}, errors

    files = render.render_site(articles)

    section_paths = ("/",) + tuple(
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


def write(files: dict[str, str], build_dir: Path, static_dir: Path) -> None:
    """build/ を作り直して書き出す。消えた記事の残骸を残さないため毎回消す。"""
    build_dir = Path(build_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    for relative, text in files.items():
        path = build_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    if Path(static_dir).exists():
        shutil.copytree(static_dir, build_dir / "static")


def main(argv=None) -> int:
    files, errors = collect(CONTENT_DIR)
    if errors:
        print(f"ビルド中止: {len(errors)}件の問題があります", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    write(files, BUILD_DIR, STATIC_DIR)
    print(f"ビルド完了: {len(files)}ファイルを {BUILD_DIR} に出力しました")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: テストが通ることを確認する**

Run: `python -m pytest tests/test_build.py -q`
Expected: PASS（9 passed）

- [ ] **Step 5: 全テストを通す**

Run: `python -m pytest -q`
Expected: PASS（合計 220 passed）

- [ ] **Step 6: Commit**

```bash
git add src/build.py tests/test_build.py
git commit -m "feat: ビルドの配線を追加。検証エラーがあれば何も書かずに落とす"
```

---

### Task 8: GitHub Actions（テスト → ビルド → Pages配信）

**Files:**
- Create: `.github/workflows/build.yml`

- [ ] **Step 1: ワークフローを作る**

`.github/workflows/build.yml`:
```yaml
name: Build & Deploy Site

on:
  push:
    branches: [main]
    # data/ は毎時トラッカーが書き換える。paths を絞らないとサイトが
    # 1日24回リビルドされる
    paths:
      - "content/**"
      - "templates/**"
      - "static/**"
      - "src/**"
      - "requirements.txt"
      - ".github/workflows/build.yml"
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: 依存をインストール
        run: pip install -r requirements.txt

      # テストが落ちたらここで止まる。壊れたものは公開に到達しない
      - name: テスト
        run: python -m pytest -q

      - name: ビルド
        run: python -m src.build

      - uses: actions/configure-pages@v5

      - uses: actions/upload-pages-artifact@v3
        with:
          path: build

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: YAMLが妥当か確認する**

Run: `python -c "import yaml,pathlib; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in pathlib.Path('.github/workflows').glob('*.yml')]; print('YAML OK')"`
Expected: `YAML OK`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/build.yml
git commit -m "ci: テスト→ビルド→Pages配信のワークフローを追加"
```

---

### Task 9: 固定ページ（about / privacy）とネタ置き場

固定ページは一覧に出ないが、AdSense審査では**運営者情報とプライバシーポリシーの有無が見られる**ので初回から置く。

**Files:**
- Create: `content/pages/about.md`
- Create: `content/pages/privacy.md`
- Create: `content/_ideas.md`

- [ ] **Step 1: このサイトについて**

`content/pages/about.md`:
```markdown
---
title: このサイトについて
description: 「AIの使い方」の方針と、記事の書き方のルール。実際に動かしていないものは書きません。
category: pages
published: 2026-08-01
---

## 何を書いているサイトか

**プログラマーではないが、AIに仕事を任せたい人**に向けて、実際に動いている自動化の手順を公開しています。

読み手として想定しているのは、こういう人です。

- Excelのマクロくらいは触ったことがある
- ChatGPT や Claude は使っているが、「自動で動かす」ところまでは行けていない
- 毎朝の情報収集や定型作業を、できれば機械にやらせたい

## 書き方のルール

このサイトの記事は、次の3つを守って書いています。

**1. 自分で動かしているものだけを書く**

ここに載っている自動化は、すべて運営者が実際に本番で毎日動かしているものです。公式ドキュメントを読んで書き写した記事は載せません。

**2. つまずいた点を必ず書く**

うまくいった手順だけを並べても、その通りにやって動かなかったときに詰みます。実際にどこで詰まって、どう直したかを毎回書いています。ここがこのサイトで一番役に立つ部分だと思っています。

**3. かかる時間と費用を先に書く**

読み始めてから「クレジットカードが必要でした」と分かるのは最悪なので、記事の先頭に必ず書いています。

## 運営者

個人で運営しています。投資情報サイトを1つ運営しており、そちらでGitHub Actionsのワークフローを十数本、毎日自動で動かしています。その実運用で分かったことを、こちらのサイトで手順として公開しています。

## 免責

記事の内容には正確を期していますが、AIサービスの仕様や料金は頻繁に変わります。実行する前に必ず公式の情報をご確認ください。記事の内容を実行したことによる損害について、責任を負いかねます。

お問い合わせは [プライバシーポリシー](/privacy/) のページに記載の方法でお願いします。
```

- [ ] **Step 2: プライバシーポリシー**

`content/pages/privacy.md`:
```markdown
---
title: プライバシーポリシー
description: 当サイトのアクセス解析・広告・著作権・免責事項についての方針。
category: pages
published: 2026-08-01
---

## 個人情報の取り扱い

当サイトは、閲覧するだけであれば氏名・メールアドレスなどの個人情報の入力を求めることはありません。

## アクセス解析

当サイトでは、サイトの改善のためにアクセス状況を把握することがあります。その際に使用するツールはCookieを利用してデータを収集する場合がありますが、この情報に個人を特定するものは含まれません。

Cookieの使用を望まない場合は、お使いのブラウザの設定で無効にすることができます。

## 広告について

当サイトでは、第三者配信の広告サービスを利用する場合があります。広告配信事業者は、ユーザーの興味に応じた広告を表示するためにCookieを使用することがあります。

広告やアフィリエイトリンクを掲載する記事には、その旨を記事内に明記します。

## 著作権

当サイトに掲載しているコード・文章の著作権は運営者に帰属します。記事中のコードは、ご自身の環境で自由にお使いいただいて構いません。

記事の内容を引用される場合は、出典として当サイトへのリンクを添えてください。

外部サービスの名称・ロゴ等は、各権利者に帰属します。

## 免責事項

当サイトに掲載する情報は、掲載時点で運営者が実際に動作を確認したものですが、AIサービスや外部ツールの仕様・料金は予告なく変更されます。実行前に必ず公式の情報をご確認ください。

当サイトの情報を利用したことにより生じた損害について、運営者は一切の責任を負いません。

## お問い合わせ

当サイトのGitHubリポジトリのIssueからご連絡ください。

## 改定

本ポリシーは予告なく変更する場合があります。変更後の内容は当ページに掲載した時点で有効となります。
```

- [ ] **Step 3: 記事ネタの置き場を作る**

`content/_ideas.md`（ファイル名が `_` で始まるのでビルド対象外）:
```markdown
# 記事ネタ

思いついたら1行だけ足す。整形はしない。

## 次に書く候補

- 無料でメールリストを作り、全ページに自動で設置する
- 静的サイトを自動でビルドして公開する（このサイト自身の作り方）
- GitHub Actions のcronが「走らない・遅れる」ときの調べ方

## 貯めておくもの

- トラッカーが拾った更新のうち、実際に使って良かったもの
- 詰まって解決したこと（解決した直後に1行書く。あとで思い出せない）
```

- [ ] **Step 4: ビルドが通ることを確認する**

Run: `python -m src.build`
Expected: `ビルド完了: 7ファイルを ...\build に出力しました`（index / about / privacy / feed.xml / sitemap.xml / robots.txt / CNAME）

> 記事が recipes に1本もない状態では `recipes/index.html` は作られない。これは意図した挙動（空の一覧ページを作らない）。

- [ ] **Step 5: 出力を目視で確認する**

Run: `python -c "import pathlib; [print(p) for p in sorted(pathlib.Path('build').rglob('*')) if p.is_file()]"`
Expected: `build/CNAME` `build/about/index.html` `build/index.html` `build/privacy/index.html` `build/robots.txt` `build/sitemap.xml` `build/feed.xml` `build/static/style.css` が並ぶ

- [ ] **Step 6: Commit**

```bash
git add content/
git commit -m "content: 固定ページ（このサイトについて・プライバシーポリシー）と記事ネタ置き場を追加"
```

---

### Task 10: レシピ①「AIの最新情報を自動で集めて、重要なものだけメールで受け取る」

**このリポジトリの `tracker/` と `.github/workflows/tracker*.yml` を実際に読んでから書く。** 記憶や一般論から書くとこのサイト唯一の武器（実際に動かしている裏付け）を失う。

**Files:**
- Create: `content/recipes/ai-news-auto-collect.md`

- [ ] **Step 1: 実物を読む**

読むファイル:
- `tracker/sources.yml` — ソース定義の実際の書式
- `tracker/run.py` — 3モードの実際の挙動と出力メッセージ
- `tracker/classify.py` — major/minor の実際の判定語
- `.github/workflows/tracker.yml` / `tracker-digest.yml` — cron の時刻・permissions・コミットステップ
- `docs/superpowers/specs/2026-08-01-ai-update-tracker-design.md` §3 — 到達性の実測結果
- `SESSION_HANDOFF.md` §「設計上、触ると壊れるところ」「既知の課題」 — 記事の「つまずいた点」の原料

- [ ] **Step 2: 記事を書く**

`content/recipes/ai-news-auto-collect.md` を作る。frontmatter:

```yaml
---
title: AIの最新情報を自動で集めて、重要なものだけメールで受け取る
description: 15の公式ソースを毎時チェックし、重大な発表だけ即メール・それ以外は毎朝1通にまとめる仕組みを、サーバー代0円で作ります。
category: recipes
published: 2026-08-01
tags: [GitHub Actions, 自動化, 無料, 情報収集]
time_required: 1時間
cost: 無料
---
```

本文は設計書 §3 の5ブロック構成を守る。各ブロックに入れる内容:

1. **これで何ができるか** — 3行 + 届くメールの実際の見た目（件名と本文の抜粋）
2. **前提** — 1時間 / 無料 / 必要なもの（GitHubアカウント、Gmailアプリパスワード、Python 3.12）
3. **手順** — GitHubリポジトリ作成 → コード配置 → `sources.yml` の書き方 → Gmailアプリパスワードの取得 → Secretsの登録 → **bootstrap（重要）** → ワークフロー設置 → 手動実行での確認
4. **つまずいた点と直し方** — 以下を必ず全部入れる（すべて実際に起きたこと）
   - 初回にいきなり毎時チェックを走らせると1000通超のメールが飛ぶ（OpenAIのフィードだけで1105件）。だから `--mode bootstrap` を先に走らせて全部既読にする
   - Workflow permissions が Read only だと状態ファイルのpushが403で落ちる
   - コミットステップに `if: always()` を付けてはいけない。送信失敗時に既読にすると「既読なのに届いていない」記事が永久に失われる
   - HuggingFace の org 名は大文字小文字が効く（`moonshotai` は動くが `MoonshotAI` は0件）
   - x.ai は403でbotブロックされる。User-Agentを偽装して迂回しない（規約とマナーの問題）。別ルートを使う
   - cronは毎時0分を避ける（混雑で遅延・スキップが起きる）。このサイトの例では毎時17分
   - Windowsのコンソールで日本語の出力が `UnicodeEncodeError` になる → `PYTHONUTF8=1`
5. **応用・次の一手** — ソースの追加はYAMLに数行足すだけ / Slackやメール以外への通知 / 集めた更新を公開ページにする

⚠️ 本文に書かないもの: 実際のメールアドレス、アプリパスワード、ローカルの絶対パス。`validate.py` が落とすので、書いてしまってもビルドで止まる。

- [ ] **Step 3: ビルドと検証を通す**

Run: `python -m src.build`
Expected: `ビルド完了: 9ファイル…`（recipes/index.html と recipes/ai-news-auto-collect/index.html が増える）。エラーが出たら内容に従って直す

- [ ] **Step 4: 出力HTMLを目視で確認する**

Run: `python -c "import pathlib,webbrowser; webbrowser.open(pathlib.Path('build/recipes/ai-news-auto-collect/index.html').resolve().as_uri())"`
Expected: ブラウザで記事が開く。コードブロックが横スクロールし、見出しの階層が崩れていないことを確認する

> ローカルでは `/static/style.css` が絶対パスなのでCSSが当たらない。レイアウトの最終確認は公開後に行う。ここで見るのは**本文の構造**（見出し・コードブロック・表）だけでよい。

- [ ] **Step 5: Commit**

```bash
git add content/recipes/ai-news-auto-collect.md
git commit -m "content: レシピ「AIの最新情報を自動で集めてメールで受け取る」を追加"
```

---

### Task 11: レシピ②「GitHub Actionsで毎日決まった時刻に自動実行する」

**Files:**
- Create: `content/recipes/github-actions-daily-cron.md`

- [ ] **Step 1: 実物を読む**

読むファイル:
- `C:\Users\<ユーザー名>\.claude\skills\github-actions-cron-best-practice\SKILL.md`（運営者のスキル。cron混雑回避・遅延前提設計・`workflow_dispatch` 必須・PATのworkflow scope・二重実行抑制）
- このリポジトリの `.github/workflows/tracker.yml`（実際に動いている最小のcronワークフロー）
- marketwatch側の `.github/workflows/update-market-news.yml`（毎日動いている実例）

- [ ] **Step 2: 記事を書く**

frontmatter:
```yaml
---
title: GitHub Actionsで「毎日決まった時刻に自動実行」を無料で作る
description: cronの書き方から、「走らない・遅れる」で消耗しないための設計まで。サーバーを1台も借りずに定時実行を用意します。
category: recipes
published: 2026-08-01
tags: [GitHub Actions, cron, 自動化, 無料]
time_required: 30分
cost: 無料
---
```

5ブロック構成。「つまずいた点」に必ず入れる内容:

- **cronはUTCで書く。** JST 7:00 は `0 22 * * *`（前日22時UTC）。日付がずれるので手で確認する
- **毎時0分・毎日0時は避ける。** 世界中のジョブが集中して遅延・スキップが起きる。17分・22分のような半端な分にする
- **GitHubのスケジュールは遅れる前提で作る。** 数分〜十数分の遅れは正常。「その時刻ちょうどに動く」ことに依存した処理を書かない
- **`workflow_dispatch` を必ず付ける。** 手動実行できないワークフローは、詰まったときに手が出せない
- **60日間リポジトリに動きがないとスケジュールが自動停止する。** 定期的にコミットがあるリポジトリなら問題にならない
- **リポジトリにコミットするワークフローには `permissions: contents: write` が要る。** 無いとpushが403で落ちる
- **ローカルの `.bat` と Actions の両方で同じ処理を動かすと二重に走る。** どちらか一方に寄せる

- [ ] **Step 3: ビルドと検証を通す**

Run: `python -m src.build`
Expected: エラーなくビルドが通る

- [ ] **Step 4: Commit**

```bash
git add content/recipes/github-actions-daily-cron.md
git commit -m "content: レシピ「GitHub Actionsで毎日決まった時刻に自動実行」を追加"
```

---

### Task 12: レシピ③「YouTube動画を毎晩自動で要約させる」

**Files:**
- Create: `content/recipes/youtube-auto-summary.md`

- [ ] **Step 1: 実物を読む**

読むファイル（marketwatch側。パスは `C:\Users\<ユーザー名>\OneDrive\デスクトップ\新しいフォルダー\`）:
- `.github/workflows/update-youtube-summary.yml` — 実際のスケジュールと手順
- 同ワークフローが呼んでいるPythonスクリプト — 取得方法・要約の投げ方・出力先
- 運営者のメモリ `project_youtube_automation.md` — 対象11チャンネル・毎晩20:30生成という実運用の事実

- [ ] **Step 2: 記事を書く**

frontmatter:
```yaml
---
title: YouTubeの動画を毎晩自動で要約させて、見る前に中身を知る
description: 追いかけているチャンネルの新着を毎晩まとめて要約させます。動画を開く前に「見る価値があるか」が分かります。
category: recipes
published: 2026-08-01
tags: [YouTube, 自動化, 要約, GitHub Actions]
time_required: 1時間
cost: 無料〜（AIの利用料のみ）
---
```

5ブロック構成。「つまずいた点」には実際に起きたことだけを書く。実物を読んで確認できないことは書かない。

⚠️ **APIキーを本文に書かない。** 環境変数・Secrets経由の書き方だけを示す。

- [ ] **Step 3: ビルドと検証を通す**

Run: `python -m src.build`
Expected: エラーなくビルドが通る

- [ ] **Step 4: Commit**

```bash
git add content/recipes/youtube-auto-summary.md
git commit -m "content: レシピ「YouTube動画を毎晩自動で要約」を追加"
```

---

### Task 13: レシピ④「サイトやサービスの異常を自動検知して通知する」

**Files:**
- Create: `content/recipes/auto-health-check.md`

- [ ] **Step 1: 実物を読む**

読むファイル（marketwatch側）:
- `.github/workflows/health-check.yml` — 実際の検知スケジュール
- `check_site_health.py` — 何を「異常」と判定しているか（更新が止まっている / ページが落ちている 等）
- `.github/workflows/automation-health.yml` — 自動化そのものの死活監視

このリポジトリ側の実例:
- `tracker/store.py` の `record_result` / `dead_sources` — 「3回連続で失敗したら警告」の実装

- [ ] **Step 2: 記事を書く**

frontmatter:
```yaml
---
title: サイトやサービスが静かに壊れたのを、自動で見つけて知らせる
description: 「落ちていないか」ではなく「更新が止まっていないか」を見張ります。自動化で一番怖い、静かな故障を捕まえる仕組みです。
category: recipes
published: 2026-08-01
tags: [監視, 自動化, GitHub Actions, 無料]
time_required: 45分
cost: 無料
---
```

「これで何ができるか」の核: **自動化で一番怖いのはエラーで止まることではなく、エラーを出さずに古いデータを配り続けること。** 死活監視はそこを見る。

「つまずいた点」に必ず入れる:
- **「取得できた件数」ではなく「生の取得件数」で死活を判定する。** 重複除去後の新着件数で判定すると、更新の少ないソースが数時間で「死亡」扱いになって誤報が出る（トラッカーで実際にやらかした）
- **1回の失敗で通知しない。** 3回連続してから鳴らす。一時的なネットワークエラーで毎回鳴ると、本当の故障を無視するようになる
- **監視する側が死んだら気づけない。** 監視ワークフロー自体の死活も別に見る

- [ ] **Step 3: ビルドと検証を通す**

Run: `python -m src.build`
Expected: エラーなくビルドが通る

- [ ] **Step 4: Commit**

```bash
git add content/recipes/auto-health-check.md
git commit -m "content: レシピ「サービスの異常を自動検知して通知」を追加"
```

---

### Task 14: レシピ⑤「Claude Codeに記憶を持たせて毎回説明し直さなくする」

**Files:**
- Create: `content/recipes/claude-code-memory.md`

- [ ] **Step 1: 実物を読む**

読むファイル:
- `C:\Users\<ユーザー名>\.claude\projects\<プロジェクト>\memory\MEMORY.md` — 索引の実際の形（1行1メモリ・リンク形式）
- 同ディレクトリのメモリファイル数本 — frontmatter（`name` / `description` / `metadata.type`）の実際の書式
- このリポジトリの `SESSION_HANDOFF.md` — セッションをまたぐ引き継ぎメモの実例

- [ ] **Step 2: 記事を書く**

frontmatter:
```yaml
---
title: Claude Codeに「記憶」を持たせて、毎回同じ説明をしなくて済むようにする
description: 前提・好み・過去の判断をファイルに置いて、新しい会話でも引き継がせます。説明の手間が毎回消えます。
category: recipes
published: 2026-08-01
tags: [Claude Code, AI, 効率化]
time_required: 20分
cost: 無料
---
```

5ブロック構成。この記事の核は「何を記憶させ、何を記憶させないか」。

「つまずいた点」に必ず入れる:
- **リポジトリを読めば分かることは書かない。** コード構造や過去の修正履歴を書くと、コードが変わったときに記憶のほうが嘘になる
- **相対日付を書かない。** 「先週」「来月」は、読み返す時点でずれる。絶対日付で書く
- **1ファイル1事実にする。** 1つのファイルに詰め込むと、一部が古くなったときに全体が信用できなくなる
- **索引ファイルには中身を書かない。** 索引は1行のリンクだけにする。中身を書くと毎回全部読み込むことになる

- [ ] **Step 3: ビルドと検証を通す**

Run: `python -m src.build`
Expected: エラーなくビルドが通る

- [ ] **Step 4: 全テストとビルドを通す**

Run: `python -m pytest -q`
Expected: PASS（220 passed）

Run: `python -m src.build`
Expected: `ビルド完了: 13ファイル…`（index / recipes一覧 / レシピ5本 / about / privacy / feed.xml / sitemap.xml / robots.txt / CNAME）

- [ ] **Step 5: Commit**

```bash
git add content/recipes/claude-code-memory.md
git commit -m "content: レシピ「Claude Codeに記憶を持たせる」を追加"
```

---

### Task 15: 公開（運営者の作業を含む）

ここは人間の作業が混ざる。**DNSレコードとPages設定は運営者が行う。**

- [ ] **Step 1: pushする**

```bash
git push
```

- [ ] **Step 2: Pages のソースを GitHub Actions に切り替える（運営者の作業）**

`Settings → Pages → Build and deployment → Source` を **GitHub Actions** にする。

> 初期値の "Deploy from a branch" のままだと、`upload-pages-artifact` で上げた成果物が使われず、`deploy-pages` が失敗する。

- [ ] **Step 3: ワークフローを手動実行する**

`Actions → Build & Deploy Site → Run workflow`

Expected: build と deploy の両方が成功し、deploy のログに `https://invest-ai-info.github.io/ai-tsukaikata/` 形式のURLが出る

- [ ] **Step 4: DNSレコードを設定する（運営者の作業）**

ドメインのレジストラの管理画面で、`ai-tsukaikata.com` に以下を設定する。

| 種別 | ホスト | 値 |
|---|---|---|
| A | @ | 185.199.108.153 |
| A | @ | 185.199.109.153 |
| A | @ | 185.199.110.153 |
| A | @ | 185.199.111.153 |
| CNAME | www | invest-ai-info.github.io |

> 上記のIPは GitHub Pages の Apex ドメイン用アドレス。設定前に [GitHub の公式ドキュメント](https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site) で現行の値を確認すること。

- [ ] **Step 5: カスタムドメインを設定する（運営者の作業）**

`Settings → Pages → Custom domain` に `ai-tsukaikata.com` を入れて Save する。DNSの伝播後、`Enforce HTTPS` にチェックを入れる。

> `build/CNAME` をビルドで生成しているので、以後のデプロイでこの設定が外れることはない。

- [ ] **Step 6: 公開を確認する**

以下をブラウザで開いて確認する。

- `https://ai-tsukaikata.com/` — トップにレシピ5本のカードが出る。CSSが当たっている
- `https://ai-tsukaikata.com/recipes/ai-news-auto-collect/` — 記事が読める。コードブロックが横スクロールする
- `https://ai-tsukaikata.com/feed.xml` — RSSリーダーで購読できる
- `https://ai-tsukaikata.com/sitemap.xml` — 全URLが入っている
- スマホ幅（開発者ツールの375px）で崩れていない

- [ ] **Step 7: Search Console に登録する（運営者の作業）**

Google Search Console で `ai-tsukaikata.com` を登録し、`https://ai-tsukaikata.com/sitemap.xml` を送信する。

- [ ] **Step 8: 引き継ぎメモを更新する**

`SESSION_HANDOFF.md` の表で2段目を ✅ 稼働中 にし、次の一手（記事を20本まで増やしてAdSense申請 / 3段目の使い分けマップ）を書く。

```bash
git add SESSION_HANDOFF.md
git commit -m "docs: 2段目（サイト本体）の公開を反映"
git push
```

---

## 完了条件

- [ ] `python -m pytest -q` が全て通る（220 passed）
- [ ] `python -m src.build` が13ファイルを出力する
- [ ] 機密パターンを含む記事を置くとビルドが失敗し、`build/` が書き換わらない
- [ ] `https://ai-tsukaikata.com/` が独自ドメインで表示される
- [ ] レシピ5本すべてが「つまずいた点と直し方」を持っている（実際に起きたことだけ）
- [ ] `feed.xml` がRSSリーダーで購読できる

---

## 次の段階（この計画のスコープ外）

- 記事を20本まで増やしてから AdSense を申請する
- トラッカー（1段目）が集めた更新を公開ページにする
- 使い分けマップ（3段目）— トラッカーが数週間データを貯めてから
- タグページ・検索・関連記事 — 記事数が増えてから
