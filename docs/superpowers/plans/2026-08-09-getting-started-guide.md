# 始め方の指南書（/start/）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 初心者が「自分のPCで動くか」から始められる指南書を `/start/` に置き、トップから導線を張る。

**Architecture:** 記事は `content/pages/start.md`（1枚もの）。frontmatter に `checked:`（確認日）を足し、
**未来日付だけビルドで止める**。古さと外部リンク切れは `tools/check_freshness.py` が週次で見て、
問題があればワークフローを失敗させ GitHub の標準通知で知らせる。**古さでビルドを止めない**のは、
毎晩21:00のレシピ担当が push した記事が巻き添えで公開されなくなるため。

**Tech Stack:** Python 3.12 / Jinja2 / Markdown / PyYAML / pytest / GitHub Actions

**設計書:** `docs/superpowers/specs/2026-08-09-getting-started-guide-design.md`

---

## ファイル構成

| ファイル | 役割 |
|---|---|
| `src/content.py`（変更） | `Article` に `checked: date \| None` を足し、frontmatter から読む |
| `src/validate.py`（変更） | `checked` が未来日付ならビルドを止める |
| `src/render.py`（変更） | `/start/` があるときだけ nav と トップの導線を出す |
| `templates/article.html`（変更） | `checked` があれば確認日を本文の前に出す |
| `templates/index.html`（変更） | ヒーロー直下に導線セクション |
| `static/style.css`（変更） | `.start-section` と `.checked-note` |
| `tools/check_freshness.py`（新規） | 外部リンクの死活・確認日の古さ・`checked` の付け忘れ |
| `.github/workflows/freshness.yml`（新規） | 週次＋手動。問題があれば失敗させる |
| `tools/make_figures.py`（変更） | 図2枚の生成関数 |
| `content/pages/start.md`（新規） | 記事本体 |
| `docs/superpowers/notes/2026-08-09-start-facts.md`（新規） | Task 1 の収集結果。記事の原材料 |

---

### Task 1: 事実を集める（コードは書かない）

**この Task の結果で、記事の厚みが決まる。届かなかったものは推測で埋めない。**

**Files:**
- Create: `docs/superpowers/notes/2026-08-09-start-facts.md`

- [ ] **Step 1: 収集用のディレクトリを作る**

```bash
mkdir -p docs/superpowers/notes
```

- [ ] **Step 2: 公式ページの生テキストを取る**

⚠️ **WebFetch を使わないこと。**要約が返るので、書いてあることが消える（2026-08-05 の実害）。
`tools/check_numbers.py` の `fetch()` は生テキストを返すので、自分で grep する。

```bash
PYTHONUTF8=1 python - <<'PY'
import sys; sys.path.insert(0, 'tools')
from check_numbers import fetch
urls = [
    "https://docs.claude.com/en/docs/claude-code/setup",
    "https://docs.claude.com/en/docs/claude-code/overview",
    "https://nodejs.org/en/download",
    "https://support.anthropic.com/en/articles/8996904",
    "https://help.openai.com/en/articles/6783457",
    "https://support.google.com/gemini/answer/13275745",
]
for url in urls:
    text = fetch(url)
    print("=" * 70)
    print(url, "->", "取得できず" if text is None else f"{len(text)}文字")
    if text:
        print(" ".join(text.split())[:1500])
PY
```

- [ ] **Step 3: 必要なキーワードを生テキストから拾う**

取れたページごとに、次の語の周辺を自分の目で読む。**見つからなければ「記載なし」と記録する。**

`Node.js` / `npm` / `requirements` / `supported` / `browser` / `Windows` / `macOS` / `RAM` / `memory` / `free`

- [ ] **Step 4: この機械の実測構成を取る**

⚠️ **ホスト名・ユーザー名・絶対パスは記録しない**（`validate.py` が `C:\Users\` を機密として弾く）。

```bash
PYTHONUTF8=1 python - <<'PY'
import platform, subprocess
print("OS:", platform.system(), platform.release(), platform.version())
print("CPU:", platform.processor())
mem = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "[math]::Round((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory/1GB,1)"],
    capture_output=True, text=True).stdout.strip()
print("メモリ(GB):", mem)
node = subprocess.run(["node", "--version"], capture_output=True, text=True)
print("Node.js:", node.stdout.strip() or "入っていない")
PY
```

- [ ] **Step 5: 収集結果を書き出す**

`docs/superpowers/notes/2026-08-09-start-facts.md` に、次の形でそのまま書く。
**推測を混ぜない。取れなかった欄は「公式の記載なし」または「取得できず（403等）」と書く。**

```markdown
# /start/ の原材料（2026-08-09 収集）

## 取得できたページ

| URL | 状態 | 拾った記述 |
|---|---|---|
| https://... | 200 | （生テキストから引用） |

## 取得できなかったページ

| URL | 何が起きたか |
|---|---|
| https://... | 403（bot判定） |

## 最低要件の表（図①と記事の表にそのまま使う）

| ツール | 対応OS | メモリ | ターミナル | 支払い |
|---|---|---|---|---|
| ChatGPT（ブラウザ） | | | 不要 | |
| Claude（ブラウザ） | | | 不要 | |
| Gemini（ブラウザ） | | | 不要 | |
| Claude Code | | | **必要** | |

## この記事を書いた機械（比較対象として1行載せる）

OS / メモリ / CPU / Node.js のバージョン
```

- [ ] **Step 6: コミット**

```bash
git add docs/superpowers/notes/2026-08-09-start-facts.md
git commit -m "docs: /start/ の原材料を公式ページから収集する

届かなかったページは埋めずに「取得できず」と記録した。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: `Article` に確認日（`checked`）を足す

**Files:**
- Modify: `src/content.py:31-44`（dataclass）と `src/content.py:129-142`（`parse_article` の return）
- Test: `tests/test_content.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_content.py` の末尾に足す。

```python
def test_checked_is_parsed_as_a_date():
    text = (
        "---\n"
        "title: 題\n"
        "description: 説明\n"
        "category: pages\n"
        "published: 2026-08-09\n"
        "checked: 2026-08-09\n"
        "---\n"
        "本文\n"
    )
    article = parse_article(Path("content/pages/start.md"), text)
    assert article.checked == date(2026, 8, 9)


def test_checked_is_optional():
    text = (
        "---\n"
        "title: 題\n"
        "description: 説明\n"
        "category: pages\n"
        "published: 2026-08-09\n"
        "---\n"
        "本文\n"
    )
    assert parse_article(Path("content/pages/x.md"), text).checked is None


def test_quoted_checked_is_rejected():
    """クォートで囲むと文字列になる。日付形式の揺れを frontmatter で止める。"""
    text = (
        "---\n"
        "title: 題\n"
        "description: 説明\n"
        "category: pages\n"
        "published: 2026-08-09\n"
        'checked: "2026-08-09"\n'
        "---\n"
        "本文\n"
    )
    with pytest.raises(ArticleError):
        parse_article(Path("content/pages/x.md"), text)
```

⚠️ `tests/test_content.py` の import に `ArticleError` と `pytest` と `date` と `Path` が
無ければ足す。

- [ ] **Step 2: 失敗を確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_content.py -k checked -q
```

期待: `AttributeError: 'Article' object has no attribute 'checked'` で3件中2件が FAIL

- [ ] **Step 3: 実装**

`src/content.py` の dataclass に1行足す（`scene` の下）。

```python
    scene: str | None = None
    # 外部の公式ページを見て書いた記事が「いつ時点の話か」。
    # ⚠️ 古いことでビルドは止めない（週次の check_freshness.py が見る）。
    checked: date | None = None
```

`parse_article` の return に1行足す。

```python
        scene=scene,
        checked=_to_date(meta["checked"], "checked") if meta.get("checked") else None,
    )
```

- [ ] **Step 4: 通ることを確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_content.py -q
```

期待: 全件 PASS

- [ ] **Step 5: コミット**

```bash
git add src/content.py tests/test_content.py
git commit -m "feat: 記事に確認日（checked）を持たせる

外部の公式ページを見て書いた記事が、いつ時点の話かを示す。
クォート付きは落とす（日付形式の揺れを frontmatter で1つに固定する）。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: 未来日付の確認日でビルドを止める

**Files:**
- Modify: `src/validate.py`（`_density_errors` の下に関数追加、`validate()` に呼び出し追加）
- Test: `tests/test_validate.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_validate.py` の末尾に足す。

```python
def test_future_checked_date_is_rejected():
    """未来の確認日は書き間違い。書いた本人がその場で直せるので止める。"""
    errors = validate([_article(checked=date(2099, 1, 1))], today=date(2026, 8, 9))
    assert any("未来の日付" in error for error in errors)


def test_past_checked_date_is_fine():
    assert validate([_article(checked=date(2020, 1, 1))], today=date(2026, 8, 9)) == []


def test_missing_checked_is_not_an_error():
    """checked が無いだけでは止めない。全記事に必須にすると既存記事が全部落ちる。"""
    assert validate([_article()], today=date(2026, 8, 9)) == []
```

- [ ] **Step 2: 失敗を確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_validate.py -k checked -q
```

期待: `TypeError: validate() got an unexpected keyword argument 'today'` で FAIL

- [ ] **Step 3: 実装**

`src/validate.py` の import に足す。

```python
from datetime import date
```

`_density_errors` の下に関数を足す。

```python
def _checked_errors(where: str, article: Article, today: date) -> list[str]:
    """確認日の形だけを見る。

    ⚠️ 「古い」ではビルドを止めない。古さは時間が経てば勝手に起きるので、
    止めると毎晩21:00のレシピ担当が push した記事が、指南書の日付を理由に
    公開されなくなる（build.py は「全部通る or 何も出さない」）。
    古さと外部リンク切れは tools/check_freshness.py が週次で見る。

    ここで止めるのは、書いた本人がその場で直せる「未来の日付」だけ。
    """
    if article.checked is None:
        return []
    if article.checked > today:
        return [
            f"{where}: 確認日が未来の日付です"
            f"（checked: {article.checked} / 今日: {today}）"
        ]
    return []
```

`validate()` のシグネチャを変える。

```python
def validate(
    articles: list[Article],
    static_paths: set[str] | None = None,
    today: date | None = None,
) -> list[str]:
```

docstring の下に足す。

```python
    today = today or date.today()
```

`errors += _density_errors(where, article)` の下に足す。

```python
        errors += _checked_errors(where, article, today)
```

- [ ] **Step 4: 通ることを確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_validate.py -q
```

期待: 全件 PASS

- [ ] **Step 5: コミット**

```bash
git add src/validate.py tests/test_validate.py
git commit -m "feat: 確認日が未来の日付ならビルドを止める

古いことでは止めない。古さは勝手に起きるので、止めると毎晩の
レシピ担当の記事が巻き添えで公開されなくなる。止めるのは
書いた本人がその場で直せるものだけ。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 4: 確認日をページに出す

読者が自分で古さを判断できるほうが、こちらの検査より確実に効く。

**Files:**
- Modify: `templates/article.html`（`article-meta` の直後）
- Modify: `static/style.css`（末尾）
- Test: `tests/test_render.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_render.py` の末尾に足す。**既にある `_article(**kwargs)` ヘルパーを使う**
（`Article` を手で組み立てない）。

```python
def test_checked_date_is_shown_on_the_page():
    article = _article(slug="start", category="pages", checked=date(2026, 8, 9))
    html = render_site([article])["start/index.html"]
    assert "2026年8月9日" in html
    assert "確認" in html


def test_no_checked_note_when_the_date_is_missing():
    html = render_site([_article(slug="start", category="pages")])["start/index.html"]
    assert "checked-note" not in html
```

- [ ] **Step 2: 失敗を確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_render.py -k checked -q
```

期待: `assert "確認" in html` で FAIL

- [ ] **Step 3: 実装**

`templates/article.html` の `</p>`（`article-meta` の閉じ）の直後に足す。

```html
  {% if article.checked %}
  <p class="checked-note">この記事の手順は <time datetime="{{ article.checked.isoformat() }}">{{ article.checked | jp_date }}</time> に公式ページで確認したものです。各社の仕様はよく変わります。表示が違っていたら公式のほうを優先してください。</p>
  {% endif %}
```

`static/style.css` の末尾に足す。

```css
/* 確認日。記事が「いつ時点の話か」を読者が自分で判断できるようにする */
.checked-note {
  background: var(--code-bg);
  border-left: 3px solid var(--line);
  border-radius: 4px;
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.7;
  margin: 1rem 0 1.5rem;
  padding: 0.7rem 0.9rem;
}
```

- [ ] **Step 4: 通ることを確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_render.py -q
```

期待: 全件 PASS

- [ ] **Step 5: コミット**

```bash
git add templates/article.html static/style.css tests/test_render.py
git commit -m "feat: 確認日を記事ページに出す

読者が自分で古さを判断できるほうが、こちらの検査より確実に効く。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: `tools/check_freshness.py` を作る

**Files:**
- Create: `tools/check_freshness.py`
- Test: `tests/test_check_freshness.py`

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_check_freshness.py` を新規作成。⚠️ **ネットワークに出ない**（`head` を差し替える）。

```python
# -*- coding: utf-8 -*-
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))

from check_freshness import check_articles, external_links  # noqa: E402

from src.content import Article, render_markdown  # noqa: E402

TODAY = date(2026, 8, 9)


def _article(body, checked=None, slug="start"):
    return Article(
        slug=slug, title="題", description="説明", category="pages",
        published=date(2026, 8, 1), updated=None, tags=(),
        time_required=None, cost=None,
        body_html=render_markdown(body),
        source_path=Path(f"content/pages/{slug}.md"),
        checked=checked,
    )


def _ok(url):
    return 200


def test_external_links_are_found_once_each():
    body = "[A](https://example.com/a) [again](https://example.com/a) [B](https://example.com/b)"
    links = external_links(render_markdown(body))
    assert links == ["https://example.com/a", "https://example.com/b"]


def test_internal_links_are_not_external():
    assert external_links(render_markdown("[中](/recipes/x/)")) == []


def test_article_with_external_links_but_no_checked_is_reported():
    """付け忘れの網。ビルドでは止めないので、ここで拾わないと静かに漏れる。"""
    article = _article("[公式](https://example.com/a)", checked=None)
    problems = check_articles([article], TODAY, head=_ok)
    assert any("checked" in p for p in problems)


def test_fresh_checked_date_is_quiet():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    assert check_articles([article], TODAY, head=_ok) == []


def test_old_checked_date_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 1, 1))
    problems = check_articles([article], TODAY, head=_ok)
    assert any("確認日" in p for p in problems)


def test_dead_link_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles([article], TODAY, head=lambda url: 404)
    assert any("404" in p for p in problems)


def test_unreachable_link_is_reported():
    article = _article("[公式](https://example.com/a)", checked=date(2026, 8, 1))
    problems = check_articles([article], TODAY, head=lambda url: None)
    assert any("開けません" in p for p in problems)


def test_article_without_external_links_and_without_checked_is_quiet():
    """既存記事の大半がこれ。ここで鳴ると一覧が読まれなくなる。"""
    assert check_articles([_article("ふつうの本文")], TODAY, head=_ok) == []
```

- [ ] **Step 2: 失敗を確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_check_freshness.py -q
```

期待: `ModuleNotFoundError: No module named 'check_freshness'` で FAIL

- [ ] **Step 3: 実装**

`tools/check_freshness.py` を新規作成。

```python
# -*- coding: utf-8 -*-
"""外部を参照している記事が腐っていないかを、週次で見る。

⚠️ ビルドには組み込まない。ネットワークに出るのでビルドが不安定になるし、
「古い」は時間が経てば勝手に起きる。ビルドで止めると、毎晩21:00の
レシピ担当が push した記事が、指南書の日付を理由に公開されなくなる
（build.py は「全部通る or 何も出さない」）。止めるのではなく知らせる。

見るのは3つ:
  1. 外部リンクが開けるか
  2. 確認日（checked）が古くなっていないか
  3. 外部リンクを持つのに checked が無い記事はどれか（付け忘れの網）

使い方: python tools/check_freshness.py
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.content import load_articles  # noqa: E402

USER_AGENT = "ai-tsukaikata-checker/1.0"
TIMEOUT = 30
MAX_AGE_DAYS = 90

EXTERNAL_LINK_RE = re.compile(r'href="(https?://[^"]+)"')


def external_links(body_html: str) -> list[str]:
    """本文の外部リンクを、出てきた順で重複なく返す。"""
    found: list[str] = []
    for url in EXTERNAL_LINK_RE.findall(body_html):
        if url not in found:
            found.append(url)
    return found


def head(url: str) -> int | None:
    """状態コードを返す。届かなければ None。

    HEAD を拒む相手がいるので、拒まれたら GET で開き直す。
    """
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(
            url, method=method, headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
                return response.status
        except urllib.error.HTTPError as error:
            if method == "HEAD" and error.code in (403, 405):
                continue
            return error.code
        except Exception:  # noqa: BLE001 - 1件の失敗で全体を止めない
            if method == "HEAD":
                continue
            return None
    return None


def check_articles(articles, today: date, head=head, max_age_days=MAX_AGE_DAYS) -> list[str]:
    """問題を文字列のリストで返す。空なら健康。"""
    problems: list[str] = []
    for article in articles:
        where = str(article.source_path)
        links = external_links(article.body_html)

        if links and article.checked is None:
            problems.append(
                f"{where}: 外部リンクが{len(links)}本あるのに checked: がありません"
                f"（腐っても誰も気づけません）"
            )
        elif article.checked is not None:
            age = (today - article.checked).days
            if age > max_age_days:
                problems.append(
                    f"{where}: 確認日が{age}日前です"
                    f"（{max_age_days}日を超えました。checked: {article.checked}）"
                )

        for url in links:
            status = head(url)
            if status is None:
                problems.append(f"{where}: リンクが開けません（接続できず）: {url}")
            elif status >= 400:
                problems.append(f"{where}: リンクが開けません（{status}）: {url}")
    return problems


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    articles, errors = load_articles(root / "content")
    for error in errors:
        print(f"記事が読めません: {error}")

    problems = check_articles(articles, date.today())
    for problem in problems:
        print(problem)

    if errors or problems:
        print(f"\n{len(errors) + len(problems)}件の問題があります")
        return 1
    print(f"{len(articles)}本を見て、問題はありませんでした")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: 通ることを確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_check_freshness.py -q
```

期待: 9件 PASS

- [ ] **Step 5: 実際に流して、既存記事に何が出るかを見る**

```bash
PYTHONUTF8=1 python tools/check_freshness.py
```

期待: tools記事3本が「checked: がありません」で出る。**これは正しい指摘なので直さない**
（設計書⑥の通り、一覧に出させて次の判断材料にする）。リンク切れが出たら内容を確認する。

- [ ] **Step 6: コミット**

```bash
git add tools/check_freshness.py tests/test_check_freshness.py
git commit -m "feat: 外部を参照している記事の腐りを週次で見る道具

外部リンクの死活・確認日の古さ・checked の付け忘れの3つ。
ビルドには組み込まない（ネットに出る／古さは勝手に起きる）。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: 週次ワークフローを置く

**Files:**
- Create: `.github/workflows/freshness.yml`

- [ ] **Step 1: ワークフローを書く**

```yaml
name: Freshness Check

on:
  # 毎週月曜 JST 9:40（UTC 日曜 0:40）。毎時0分を避ける
  schedule:
    - cron: "40 0 * * 1"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  freshness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7

      - uses: actions/setup-python@v7
        with:
          python-version: "3.12"

      - name: 依存をインストール
        run: pip install -r requirements.txt

      # ⚠️ ここが失敗したら、GitHub の標準の失敗通知メールで気づく形にしてある。
      # 専用の通知コードは足さない（サイトの検査がトラッカーに依存するのを避ける）。
      - name: 鮮度と外部リンクを検査
        run: python tools/check_freshness.py
```

- [ ] **Step 2: YAML として読めることを確認**

```bash
PYTHONUTF8=1 python -c "import yaml,pathlib; yaml.safe_load(pathlib.Path('.github/workflows/freshness.yml').read_text(encoding='utf-8')); print('OK')"
```

期待: `OK`

- [ ] **Step 3: コミット**

⚠️ **`.github/workflows/` を push するには PAT に `workflow` スコープが要る。**
403 で弾かれたらトークンを確認すること。

```bash
git add .github/workflows/freshness.yml
git commit -m "feat: 鮮度検査を週次で回す

問題があればワークフローを失敗させ、GitHubの標準通知で気づく。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: 図を2枚つくる

**Files:**
- Modify: `tools/make_figures.py`（`scope_weight_chart()` の下に追加、`__main__` に登録、枚数を32に）

- [ ] **Step 1: 図①（最低要件の表）を書く**

`scope_weight_chart()` の下に足す。⚠️ **`rows` の中身は Task 1 の
`start-facts.md` の「最低要件の表」からそのまま写す。取れなかった欄は `"公式の記載なし"` を入れる。**

```python
def start_requirements_chart() -> None:
    """4つのツールの最低要件。空欄は推測で埋めず「記載なし」と出す。"""
    # ⚠️ Task 1 の docs/superpowers/notes/2026-08-09-start-facts.md から写す。
    # 推測で埋めない。取れなかった欄は "公式の記載なし" のまま出す。
    rows = [
        ("ChatGPT（ブラウザ）", "", "", "不要", ""),
        ("Claude（ブラウザ）", "", "", "不要", ""),
        ("Gemini（ブラウザ）", "", "", "不要", ""),
        ("Claude Code", "", "", "必要", ""),
    ]
    cols = [18, 200, 330, 450, 570]
    heads = ("ツール", "対応OS", "メモリ", "ターミナル", "支払い")
    top, row_h = 104, 46
    height = top + len(rows) * row_h + 40

    parts = [
        '<text class="t-strong" x="18" y="26">4つのツールが動くのに、何が要るか</text>\n',
        '<text class="t-sm" x="18" y="45">'
        "公式が出している最低要件だけを並べています。</text>\n",
        '<text class="t-sm" x="18" y="64">'
        "空欄は「書いていない」という意味で、こちらの推測では埋めていません。</text>\n",
    ]
    for index, label in enumerate(heads):
        parts.append(f'<text class="t-xs" x="{cols[index]}" y="{top - 12}">{_esc(label)}</text>\n')
    for index, row in enumerate(rows):
        y = top + index * row_h
        cls = "box-accent" if row[0] == "Claude Code" else "box-quiet"
        parts.append(
            f'<rect class="{cls}" x="14" y="{y - 20}" '
            f'width="{WIDTH - 28}" height="{row_h - 8}" rx="4"/>\n'
        )
        for col_index, value in enumerate(row):
            text = value or "公式の記載なし"
            text_cls = "t-strong" if col_index == 0 else ("t" if value else "t-xs")
            parts.append(
                f'<text class="{text_cls}" x="{cols[col_index]}" y="{y + 6}">'
                f"{_esc(text)}</text>\n"
            )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ ブラウザで使う3つは、ブラウザが最新版になるかどうかが実質の分かれ目です。</text>\n"
    )
    alt = (
        "4つのAIツールが動くのに必要なものを並べた表。"
        "ChatGPT・Claude・Gemini のブラウザ版はターミナルが不要で、"
        "Claude Code だけターミナルが必要。"
        "公式が最低要件を書いていない欄は「公式の記載なし」と示している。"
        "ブラウザで使う3つは、ブラウザが最新版になるかどうかが実質の分かれ目になる。"
    )
    (OUT / "start-requirements.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )
```

- [ ] **Step 2: 図②（できることの境界）を書く**

```python
def start_boundary_chart() -> None:
    """ブラウザ版でできること と、Claude Code が要ること の境界。"""
    left_rows = [
        "文章を書かせる・直させる",
        "資料を読ませて要約させる",
        "調べものに付き合わせる",
        "写真や画像を見せて相談する",
    ]
    right_rows = [
        "パソコンのファイルを直接触る",
        "決まった時刻に自動で動かす",
        "このサイトのレシピを実行する",
        "作ったものを動かして確かめる",
    ]
    col_w, gap, pad = 330, 24, 18
    left_x, right_x = pad, pad + col_w + gap
    head_y, first_y, row_h = 84, 114, 34
    rows = max(len(left_rows), len(right_rows))
    box_h = 30 + rows * row_h
    height = first_y + rows * row_h + 40

    parts = [
        '<text class="t-strong" x="18" y="26">'
        "ブラウザだけでできること と、Claude Code が要ること</text>\n",
        '<text class="t-sm" x="18" y="45">'
        "左だけでも、AIの使い方はひととおり身につきます。</text>\n",
        f'<rect class="box-good" x="{left_x}" y="{head_y - 22}" '
        f'width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<rect class="box-accent" x="{right_x}" y="{head_y - 22}" '
        f'width="{col_w}" height="{box_h}" rx="6"/>\n',
        f'<text class="t-good" x="{left_x + 14}" y="{head_y - 2}">ブラウザだけでできる</text>\n',
        f'<text class="t-accent" x="{right_x + 14}" y="{head_y - 2}">Claude Code が要る</text>\n',
    ]
    for index, text in enumerate(left_rows):
        parts.append(
            f'<text class="t" x="{left_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    for index, text in enumerate(right_rows):
        parts.append(
            f'<text class="t" x="{right_x + 14}" y="{first_y + index * row_h}">{_esc(text)}</text>\n'
        )
    parts.append(
        f'<text class="t-xs" x="18" y="{height - 12}">'
        "※ 右が要らないなら、Claude Code は入れなくて構いません。左だけで十分に役に立ちます。</text>\n"
    )
    alt = (
        "ブラウザ版だけでできることと、Claude Code が必要になることを2列で比べた図。"
        "ブラウザだけでできる＝文章を書かせる・直させる、資料を読ませて要約させる、"
        "調べものに付き合わせる、写真や画像を見せて相談する。"
        "Claude Code が要る＝パソコンのファイルを直接触る、決まった時刻に自動で動かす、"
        "このサイトのレシピを実行する、作ったものを動かして確かめる。"
        "右が要らなければ Claude Code は入れなくてよい。"
    )
    (OUT / "start-boundary.svg").write_text(
        _svg(height, alt, "".join(parts)), encoding="utf-8", newline="\n"
    )
```

- [ ] **Step 3: `__main__` に登録して枚数を直す**

```python
    report_split_chart()
    handoff_timing_chart()
    scope_weight_chart()
    start_requirements_chart()
    start_boundary_chart()
    print(f"31枚を {OUT} に出力しました")
```

- [ ] **Step 4: 生成して、座標検査を通す**

```bash
PYTHONUTF8=1 python tools/make_figures.py && PYTHONUTF8=1 python -m src.build
```

期待: `31枚を ... に出力しました` と `ビルド完了`。
崩れがあればビルドが止まるので、止まったら座標を直して再実行。

- [ ] **Step 5: コミット**

```bash
git add tools/make_figures.py static/images/start-requirements.svg static/images/start-boundary.svg
git commit -m "feat: 始め方の図を2枚つくる

最低要件の表は、公式が書いていない欄を推測で埋めず「公式の記載なし」と出す。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: 記事本体を書く

**Files:**
- Create: `content/pages/start.md`

- [ ] **Step 1: 骨格を置く**

⚠️ **中身は Task 1 の `start-facts.md` から書く。取れなかったものは
「公式のここに書いてあります」とリンクだけ置き、確認できなかったと明記する。**

⚠️ **h2 の class は6節すべてに付ける**（`validate.py` は「1つでも付いていれば全部に必要」）。

```markdown
---
title: AIの始め方 — 何を用意して、どこから触るか
description: ChatGPT・Claude・Gemini・Claude Code の始め方を、必要なものとPCの条件から。古いパソコンでも動くのか、動かないときはどうするかまで書いています。
category: pages
published: 2026-08-09
checked: 2026-08-09
---

## 自分のパソコンで動くかを、先に確かめる {: .need }

### 1. まず、自分のパソコンが何なのかを調べる

Windows の手順（設定 → システム → バージョン情報）を、押す場所の名前をそのまま書く。
Task 1 Step 4 で自分で踏んで確かめた通りに書く。

### 2. 分かれ目は「ブラウザを最新版にできるかどうか」

古いパソコンで詰まる本当の原因は、メモリより **OS が古くてブラウザが最新版にならない** ほう。
確かめ方（ブラウザの「バージョン情報」を開く）を書く。

### 3. 公式が出している最低要件

<figure class="figure">
<img src="/static/images/start-requirements.svg" alt="4つのAIツールが動くのに必要なものを並べた表。ChatGPT・Claude・Gemini のブラウザ版はターミナルが不要で、Claude Code だけターミナルが必要。公式が最低要件を書いていない欄は「公式の記載なし」と示している。ブラウザで使う3つは、ブラウザが最新版になるかどうかが実質の分かれ目になる。">
<figcaption>公式が最低要件を書いていないところは、空欄のままにしてあります。</figcaption>
</figure>

### 4. 公式が書いていないものは、書いていないと書く

「公式の最低メモリは存在しない」と明記し、**この記事を書いた機械の構成**（OS／メモリ／CPU／
Node.js のバージョン）を1行だけ添えて、読者が自分と比べられるようにする。
⚠️ **ホスト名・ユーザー名・絶対パスは書かない。**

### 5. 足りないときの逃げ道

- **古いパソコンしかないなら、スマホのほうが速い可能性が高い**（3社ともアプリがある）
- タブを閉じる／軽いブラウザにする
- **Claude Code は諦めてブラウザ版に絞る**のも、はっきり選択肢として書く

## どれから始めるか {: .what }

ブラウザ3つ＝今日5分で触れる。Claude Code＝このサイトのレシピを動かすために要る。
「迷ったらどれか」を1行で言い切る。

## ブラウザで使う3つ {: .ask }

ChatGPT / Claude / Gemini。ツールごとに **入口のURL・必要なもの・無料でできること** を書く。
⚠️ Task 1 で取れなかったものは書かず、公式へのリンクを置いて
「確認できませんでした」と明記する。

## Claude Code を入れる（Windows） {: .ask }

必要なもの → 手順 → **動いたかどうかの確かめ方**（入れて終わりにしない）。
Mac は公式へのリンクのみ。⚠️ **手元で確かめていないので手順を書かない。**

<figure class="figure">
<img src="/static/images/start-boundary.svg" alt="ブラウザ版だけでできることと、Claude Code が必要になることを2列で比べた図。ブラウザだけでできる＝文章を書かせる・直させる、資料を読ませて要約させる、調べものに付き合わせる、写真や画像を見せて相談する。Claude Code が要る＝パソコンのファイルを直接触る、決まった時刻に自動で動かす、このサイトのレシピを実行する、作ったものを動かして確かめる。右が要らなければ Claude Code は入れなくてよい。">
<figcaption>右が要らないなら、Claude Code は入れなくて構いません。</figcaption>
</figure>

## つまずいたときの直し方 {: .fix }

### ブラウザで画面が真っ白になる {: .trouble }

### 日本語で答えてくれない {: .trouble }

### 無料の上限に当たった {: .trouble }

## 次の一手 {: .next }

`start` の場面の記事へ内部リンクを2本以上（Step 2 で実在を確かめたものだけ）。
```

⚠️ **h3 の class は任意。付けるなら `{: .trouble }` だけ**（赤い縦線＋「？」＝困りごとの印）。
`_heading_errors` は h3 に `trouble` 以外が付いていたら落とす。付いていないことは落とさない。
**「調べる」「逃げ道」のような困りごとでない h3 には付けない。**
⚠️ h2 の class（`.what` / `.need` / `.ask` / `.fix` / `.next`）は**全部に付けるか全部に付けないか**の
どちらかで、混ざると落ちる。この記事は付ける側なので6節すべてに要る。

- [ ] **Step 2: 内部リンクを入れる**

`start` の場面の記事へ2本以上。実在するものだけ貼る（存在しないとビルドが落ちる）。

```bash
PYTHONUTF8=1 python -c "
import pathlib, re
for p in sorted(pathlib.Path('content/recipes').glob('*.md')):
    t = p.read_text(encoding='utf-8')
    m = re.search(r'^scene: (\S+)', t, re.M)
    if m and m.group(1) == 'start':
        print('/recipes/' + p.stem + '/')
"
```

- [ ] **Step 3: ビルドで検査を通す**

```bash
PYTHONUTF8=1 python -m src.build
```

期待: `ビルド完了`。落ちたらエラー文の指示に従う（マーカー上限13・見出しclass・alt・リンク実在）。

- [ ] **Step 4: マーカーを拾い読みする**

```bash
PYTHONUTF8=1 python -c "
import re, pathlib
t = pathlib.Path('content/pages/start.md').read_text(encoding='utf-8')
for i, (c, b) in enumerate(re.findall(r'<mark( class=\"warn\")?>(.*?)</mark>', t, re.S), 1):
    print(i, '赤' if c else '黄', ' '.join(b.split()))
"
```

⚠️ **黄色だけ順に読んで意味が通るか**を目で見る。**「最後の一文が大事です」のような
次の文への矢印にマーカーを引かない**（2026-08-08 に実際にすり抜けた型）。

- [ ] **Step 5: コミット**

```bash
git add content/pages/start.md
git commit -m "content: 始め方の指南書を公開する

必要なものとPCの条件から始める。公式が書いていないことは
書かず、届かなかったページは確認できなかったと明記した。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 9: トップとナビに導線を出す

**Files:**
- Modify: `src/render.py:64-70`（nav）
- Modify: `templates/index.html`（ヒーロー直後）
- Modify: `static/style.css`（末尾）
- Test: `tests/test_render.py`

- [ ] **Step 1: 失敗するテストを書く**

```python
def test_start_guide_appears_on_the_top_page_when_it_exists():
    html = render_site([_article(slug="start", category="pages")])["index.html"]
    assert 'href="/start/"' in html


def test_no_start_link_when_the_guide_is_missing():
    """記事が無いのにリンクを出すとリンク切れになる（既存の nav と同じ考え方）。"""
    html = render_site([_article(slug="about", category="pages")])["index.html"]
    assert 'href="/start/"' not in html
```

- [ ] **Step 2: 失敗を確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_render.py -k start -q
```

期待: 1件目が FAIL

- [ ] **Step 3: 実装**

`src/render.py` の nav を組む箇所（`nav = [` の直前）に足す。

```python
    # 指南書は記事があるときだけ出す（無いのにリンクを出すとリンク切れになる）
    has_start = any(a.url == "/start/" for a in articles)
    env.globals["start_url"] = "/start/" if has_start else None

    nav = [{"url": "/start/", "label": "始め方"}] if has_start else []
    nav += [
        {"url": f"/{name}/", "label": config.CATEGORIES[name]["label"]} for name in active
    ]
```

⚠️ 既存の `nav = [...]` の行は上の `nav +=` に置き換わる。二重に定義しないこと。

`templates/index.html` の `</section>`（hero の閉じ）の直後に足す。

```html
{% if start_url %}
<section class="start-section">
  <h2 class="section-title">はじめての人へ</h2>
  <p class="section-lead">どのAIを、何を用意して、どこから触るか。自分のパソコンで動くかどうかから確かめられます。</p>
  <p class="start-more"><a class="hero-link is-primary" href="{{ start_url }}">始め方を読む →</a></p>
</section>
{% endif %}
```

`static/style.css` の末尾に足す。

```css
.start-section { margin-bottom: 2.5rem; }
.start-more { margin: 0; }
```

- [ ] **Step 4: 通ることを確認**

```bash
PYTHONUTF8=1 python -m pytest tests/test_render.py -q && PYTHONUTF8=1 python -m src.build
```

期待: 全件 PASS と `ビルド完了`

- [ ] **Step 5: コミット**

```bash
git add src/render.py templates/index.html static/style.css tests/test_render.py
git commit -m "feat: トップとナビに始め方への導線を出す

記事があるときだけ出す（無いのにリンクを出すとリンク切れになる）。

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 10: 通しで確かめて公開する

**Files:** なし（検証のみ）

- [ ] **Step 1: 全テストとビルド**

```bash
PYTHONUTF8=1 python -m pytest -q && PYTHONUTF8=1 python -m src.build
```

期待: 全件 PASS（Task 2〜9 で足したぶん増える）と `ビルド完了`

- [ ] **Step 2: 鮮度検査を手で流す**

```bash
PYTHONUTF8=1 python tools/check_freshness.py
```

期待: `/start/` は出ない（`checked` が今日なので）。tools記事3本の付け忘れは出てよい。
`/start/` の外部リンクが1本でも開けなければ、その行を記事から外すか確認し直す。

- [ ] **Step 3: プレビューで図の厳密計測**

`tools/measure_figures.js` の中身をブラウザのコンソールに流す
（sitemap から辿るので、足した図も自動で対象に入る）。

期待: `問題: 0`

- [ ] **Step 4: スマホ幅で崩れないかを見る**

`resize_window` で 375px にして `/start/` を開く。期待: 横スクロールが出ない
（図は枠内で横スクロールしてよい）。

- [ ] **Step 5: push してデプロイを確認**

```bash
git pull --rebase && git push
```

`Build & Deploy Site` が success になるまで待ち、本番を実測する。

```bash
PYTHONUTF8=1 python -c "
import urllib.request
for url in ('https://ai-tsukaikata.com/start/',
            'https://ai-tsukaikata.com/static/images/start-requirements.svg',
            'https://ai-tsukaikata.com/static/images/start-boundary.svg'):
    with urllib.request.urlopen(url, timeout=30) as r:
        print(r.status, len(r.read()), url)
"
```

期待: 3本とも200

- [ ] **Step 6: 引き継ぎに書く**

`SESSION_HANDOFF.md` に足す:

- `/start/` を公開したこと（1枚もの。反応を見てツール別に分けるか決める）
- `checked:` の仕組みと、**古さでビルドを止めない理由**
- `tools/check_freshness.py` と週次ワークフロー
- Task 1 で**届かなかったページ**（次に同じことをやる人が同じ壁に当たるため）

```bash
git add SESSION_HANDOFF.md
git commit -m "docs: 始め方の指南書と鮮度検査を引き継ぎに記録

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
git push
```

---

## この計画で意図的にやらないこと

- **ツール別の4ページ** — 1枚ものを出して反応を見てから決める
- **ローカルLLM の導入手順** — 運営者が使っていないので確かめられない。
  「スペックの話を探している人はこれと混同している」ことだけ1段落で切り分ける
- **Mac の手順** — 確かめられないので公式へのリンクのみ
- **既存 tools 記事3本への `checked:` 追加** — 週次の一覧に出させて、次の判断材料にする
- **専用の通知コード** — GitHub の標準通知で足りる
