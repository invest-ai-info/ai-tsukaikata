# 稼ぎ方研究の実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 金額目安を「出典＋計算式＋免責」の型でしか書けないようにコードで強制し、その型に沿った研究パックを毎日供給する専任担当を新設する。

**Architecture:** 3層。①`src/validate.py` に `money-note` ブロックの整合検査と禁止文字列検査を足す（ビルドで止める）②`tools/check_freshness.py` に heartbeat と鮮度の番人を足す（週次で知らせる・止めない）③手順書2本（`content/_earn_research.md` 新設・`content/_recipe_queue.md` 追記）とCSS。最後に研究パックを手で2〜3本作って型を実地検証してから、クラウドルーティンを登録する。

**Tech Stack:** Python 3（標準ライブラリ＋既存の `src.content.Article`）、pytest、Jinja2テンプレート、素のCSS。新規依存なし。

**設計書:** `docs/superpowers/specs/2026-08-14-earn-evolution-design.md`

---

## 前提の確認（実装前に1回だけ）

- [ ] **Step 0: 最新を取る**

```bash
cd /c/Users/info0/ai-tsukaikata && git checkout main && git pull origin main
```

- [ ] **Step 0b: 既存テストが全部通ることを確かめる**

Run: `python -m pytest -q`
Expected: 全部 pass（8/14 夜の実測は485 passed。記事が増えているので数は増える）

⚠️ ここが赤いなら、実装を始める前に原因を調べる。**赤いまま進めない。**

---

## Task 1: 金額ブロックの整合検査（validate.py）

**Files:**
- Modify: `src/validate.py`（`_checked_errors` の下、`_heading_errors` の上に足す）
- Test: `tests/test_validate.py`（末尾に足す）

**何を作るか:** 記事に `<div class="money-note">` があれば、その中に①出典リンク（`http` で始まる href）②確認日（YYYY-MM-DD）③免責文「収益を保証するものではありません」——の3点が揃っているかを見る。1つでも欠けたらエラー文字列を返す。

⚠️ **ブロックが無い記事は素通しにする**（金額を書かない記事のほうが多い。ブロックを必須にはしない）。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_validate.py` の末尾に足す:

```python
# --- 金額目安ブロック（2026-08-14 稼ぎ方研究の設計）---
#
# 金額は money-note ブロックの中だけに書く。ブロックの外に書かれた収入金額は
# 機械では見ない（「月3,000円のツール」＝価格 と「月3万円稼げる」＝収入 を
# 確実に区別できず、誤検知は検査全体の信用を殺す）。人が見る＝確認担当の観点5。

MONEY_OK = (
    '<div class="money-note">\n'
    "金額の目安: 月1〜6万円（副業帯）\n"
    '根拠: 文字単価0.5〜3円（出典: <a href="https://example.com/price">○○公表価格</a>・'
    "2026-08-15確認）× 月2万字の場合\n"
    "この金額は目安であり、収益を保証するものではありません。\n"
    "</div>"
)


def test_money_note_with_all_three_passes():
    assert validate([_article(body=MONEY_OK)]) == []


def test_money_note_without_disclaimer_is_detected():
    body = MONEY_OK.replace("この金額は目安であり、収益を保証するものではありません。\n", "")
    errors = validate([_article(body=body)])
    assert any("収益を保証するものではありません" in e for e in errors)


def test_money_note_without_source_link_is_detected():
    body = MONEY_OK.replace(
        '<a href="https://example.com/price">○○公表価格</a>', "○○公表価格"
    )
    errors = validate([_article(body=body)])
    assert any("出典" in e for e in errors)


def test_money_note_without_checked_date_is_detected():
    body = MONEY_OK.replace("・2026-08-15確認", "")
    errors = validate([_article(body=body)])
    assert any("確認日" in e for e in errors)


def test_article_without_money_note_passes():
    assert validate([_article(body="金額の話をしない記事です。")]) == []
```

- [ ] **Step 2: 失敗することを確かめる**

Run: `python -m pytest tests/test_validate.py -k money -q`
Expected: FAIL（4本が落ちる。`test_article_without_money_note_passes` だけは今も通る）

- [ ] **Step 3: 最小の実装を書く**

`src/validate.py` の定数部（`RECIPE_MIN_FIGURES = 1` の下あたり）に足す:

```python
# --- 金額目安ブロック（2026-08-14 稼ぎ方研究の設計）---
#
# 金額は「出典つき単価 × 明示した前提」でしか出さない、という型を機械で守る。
# ⚠️ ここで見るのはブロックの中身の3点だけ。ブロックの外に書かれた金額は
# 見ない（価格と収入を機械で区別できないため。誤検知は検査全体の信用を殺す）。
MONEY_NOTE_RE = re.compile(r'<div class="money-note">(.*?)</div>', re.DOTALL)
MONEY_DISCLAIMER = "収益を保証するものではありません"
MONEY_SOURCE_RE = re.compile(r'href="https?://')
MONEY_CHECKED_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
```

`_checked_errors` の下に関数を足す:

```python
def _money_note_errors(where: str, body_html: str) -> list[str]:
    """金額目安ブロックの中身を検査する。

    ブロックが無ければ何も言わない（金額を書かない記事のほうが多い）。
    あるなら、出典・確認日・免責の3点が揃っていること。
    """
    errors = []
    for index, match in enumerate(MONEY_NOTE_RE.finditer(body_html), start=1):
        block = match.group(1)
        where_block = f"{where}: 金額ブロック{index}"
        if MONEY_DISCLAIMER not in block:
            errors.append(
                f"{where_block}に「{MONEY_DISCLAIMER}」の一文がありません"
            )
        if not MONEY_SOURCE_RE.search(block):
            errors.append(f"{where_block}に出典のリンクがありません")
        if not MONEY_CHECKED_RE.search(block):
            errors.append(
                f"{where_block}に確認日（YYYY-MM-DD）がありません"
            )
    return errors
```

`validate()` の本体、`errors += _checked_errors(where, article, today)` の下に1行足す:

```python
        errors += _money_note_errors(where, article.body_html)
```

- [ ] **Step 4: テストが通ることを確かめる**

Run: `python -m pytest tests/test_validate.py -k money -q`
Expected: 5 passed

- [ ] **Step 5: 既存テストが壊れていないことを確かめる**

Run: `python -m pytest -q`
Expected: 全部 pass（Step 0b の数＋5）

- [ ] **Step 6: コミット**

```bash
git add src/validate.py tests/test_validate.py && git commit -m "feat: 金額目安ブロックの整合をビルドで強制する（出典・確認日・免責の3点）"
```

---

## Task 2: 禁止文字列の検査（validate.py）

**Files:**
- Modify: `src/validate.py`（Task 1 で足した `_money_note_errors` の下）
- Test: `tests/test_validate.py`（末尾）

**何を作るか:** 収益を保証する断定表現の**完全一致**を見る。⚠️ 2つ誤検知してはいけないものがある:

1. **免責文自身**（「収益を保証するものではありません」）——語を選んで避ける
2. 🚨 **詐欺を防ぐ場面（`scene: safety`）の引用**——この場面は**詐欺の勧誘文句を引用するのが仕事**。
   既に `too-good-offer-checklist.md` が「AIで稼げる」を引用している。
   safety記事が「必ず稼げます」を例示した瞬間にビルドが止まる設計にはしない。
   **場面で除外する**（この家の「誤検知は検査全体の信用を殺す」の型）

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_validate.py` の末尾に足す:

```python
@pytest.mark.parametrize(
    "phrase",
    ["必ず稼げます", "確実に稼げる方法", "絶対に稼げます", "誰でも稼げる", "月30万円保証"],
)
def test_income_guarantee_phrase_is_detected(phrase):
    errors = validate([_article(body=f"この方法なら{phrase}。")])
    assert any("稼げる" in e or "保証" in e for e in errors)


def test_disclaimer_itself_is_not_flagged():
    # 免責文は「保証」を含むが、これは検出してはいけない（自分の型を自分で殺す）
    assert validate([_article(body=MONEY_OK)]) == []


def test_normal_earning_talk_passes():
    assert validate([_article(body="副業の作業をAIに手伝わせる話です。")]) == []


def test_safety_scene_may_quote_scam_phrases():
    # 🚨 詐欺を防ぐ場面は、詐欺の勧誘文句を引用するのが仕事。
    # ここで止めると、既存の too-good-offer-checklist の系列が書けなくなる。
    article = _article(
        body="広告に「必ず稼げます」とあったら、判定させずに確かめる手順に変えます。",
        scene="safety",
    )
    assert validate([article]) == []
```

- [ ] **Step 2: 失敗することを確かめる**

Run: `python -m pytest tests/test_validate.py -k "guarantee or disclaimer or normal_earning or safety_scene" -q`
Expected: FAIL（`test_income_guarantee_phrase_is_detected` の5パターンが落ちる。
`test_safety_scene_may_quote_scam_phrases` は実装前なので今は通る＝**実装後も通り続けることが要件**）

- [ ] **Step 3: 最小の実装を書く**

`src/validate.py` の定数部（Task 1 の定数の下）に足す:

```python
# 収益を保証する断定。earn の黒レーン（2026-08-13）をコードにしたもの。
# ⚠️ 完全一致の少数だけにする。日本語の断定を正規表現で広く追うと誤検知が出て、
# validate 全体の信用が落ちる（このサイトの判断済みの型）。
BANNED_INCOME_PHRASES = (
    "必ず稼げ",
    "確実に稼げ",
    "絶対に稼げ",
    "誰でも稼げ",
    "円保証",
    "収入保証",
)
# 🚨 詐欺を防ぐ場面は、詐欺の勧誘文句を引用するのが仕事なので除外する。
# ここを除外しないと、うちの safety 記事（「AIで稼げる」を引用している）の
# 系列が書けなくなる＝番人が本来の仕事を邪魔する形になる。
INCOME_PHRASE_EXEMPT_SCENES = frozenset({"safety"})
```

`_money_note_errors` の下に関数を足す:

```python
def _income_phrase_errors(where: str, article: Article) -> list[str]:
    """収益を保証する断定を見つける。

    ⚠️ 誤検知してはいけないものが2つある:
    ①免責文（「収益を保証するものではありません」）＝語を選んで避けてある
     （「円保証」「収入保証」は免責文と一致しない）
    ②詐欺を防ぐ場面の引用＝場面ごと除外する
    """
    if article.scene in INCOME_PHRASE_EXEMPT_SCENES:
        return []
    return [
        f"{where}: 収益を保証する書き方があります（「{phrase}」）"
        for phrase in BANNED_INCOME_PHRASES
        if phrase in article.body_html
    ]
```

`validate()` の本体、Task 1 で足した行の下に1行足す:

```python
        errors += _income_phrase_errors(where, article)
```

- [ ] **Step 4: テストが通ることを確かめる**

Run: `python -m pytest tests/test_validate.py -k "guarantee or disclaimer or normal_earning or safety_scene" -q`
Expected: 8 passed

- [ ] **Step 5: 既存の記事が全部通ることを確かめる**

Run: `python -m pytest -q && python -m src.build`
Expected: テスト全部 pass ＋ ビルド成功。⚠️ **既存記事がここで引っかかったら、記事のほうを直す**（検査を緩めない＝キューの縛りと同じ）

- [ ] **Step 6: コミット**

```bash
git add src/validate.py tests/test_validate.py && git commit -m "feat: 収益を保証する断定をビルドで止める（earnの黒レーンをコードに）"
```

---

## Task 3: money-note のCSS

**Files:**
- Modify: `static/style.css`（`.article-body .prompt` の定義の下＝454行目付近）

**何を作るか:** 金額ブロックの見た目。既存の `.prompt` と同じ書き方（変数を使う・ダークは変数側で切り替わる）に合わせる。

- [ ] **Step 1: CSSを足す**

`static/style.css` の `.article-body .prompt + .prompt { margin-top: -0.4rem; }` の下に足す:

```css
/* 金額の目安（2026-08-14）。出典・計算式・免責がひとかたまりで見えること。
   指示文（.prompt）より控えめにする＝主役はあくまで手順のほう */
.article-body .money-note {
  margin: 1.4rem 0;
  padding: 0.9rem 1.1rem;
  background: var(--prompt-bg);
  border: 1px solid var(--line);
  border-left: 4px solid var(--muted);
  border-radius: 8px;
  font-size: 0.95rem;
  line-height: 1.8;
}
```

- [ ] **Step 2: 両テーマで見た目を確かめる**

Run: `python -m src.build`
そのあとブラウザで金額ブロックのある記事を開き、ライト／ダークの両方で読めることを目で見る（Task 6 の手動記事ができてからでよい。ここでは変数が未定義でないことだけ確かめる）

Expected: `--prompt-bg` `--line` `--muted` はいずれも既存の定義済み変数なので、黒塗りは起きない

- [ ] **Step 3: コミット**

```bash
git add static/style.css && git commit -m "style: 金額目安ブロックの見た目を足した"
```

---

## Task 4: 研究担当の heartbeat（check_freshness.py）

**Files:**
- Modify: `tools/check_freshness.py`（`earn_queue_shortage` の下）
- Test: `tests/test_check_freshness.py`（末尾）

**何を作るか:** `content/_earn_research.md` の最終更新が48時間を超えたら知らせる。**沈黙禁止（0件の日も1行書く）とセットで意味を持つ**＝担当が止まればログが止まり、ここが鳴る。

⚠️ ファイルの mtime ではなく **git の最終コミット日時**で見る（クローンし直すと mtime は当てにならない）。テストしやすいように、日時は引数で受け取る形にする。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_check_freshness.py` の末尾に足す:

⚠️ **import の書き方に注意**＝このテストは `from check_freshness import ...`（`tools.` を付けない。
ファイル冒頭で sys.path に `tools/` を足してある）。冒頭の import を次のように直す:

```python
from datetime import date, datetime, timedelta, timezone   # ← timedelta と datetime と timezone を足す
```

既存の `from check_freshness import (` の括弧の中に `earn_research_heartbeat` を足す。
そのうえで末尾に足す:

```python
def _dt(hours_ago, now):
    return now - timedelta(hours=hours_ago)


def test_earn_research_fresh_is_silent():
    now = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)
    assert earn_research_heartbeat(_dt(20, now), now) is None


def test_earn_research_silent_too_long_is_detected():
    now = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)
    message = earn_research_heartbeat(_dt(50, now), now)
    assert message is not None
    assert "_earn_research.md" in message


def test_earn_research_missing_file_is_detected():
    now = datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc)
    message = earn_research_heartbeat(None, now)
    assert message is not None
    assert "見つかりません" in message
```


- [ ] **Step 2: 失敗することを確かめる**

Run: `python -m pytest tests/test_check_freshness.py -k earn_research -q`
Expected: FAIL with "cannot import name 'earn_research_heartbeat'"

- [ ] **Step 3: 最小の実装を書く**

`tools/check_freshness.py` の `earn_queue_shortage` の下に足す:

```python
# --- 稼ぎ方研究担当の heartbeat（2026-08-14 稼ぎ方研究の設計）---
#
# 担当は0件の日も1行書く（沈黙禁止）。だから「ログが止まった＝担当が止まった」。
# ⚠️ ATには automation-health 相当のページがまだ無いので、当面はここが
# 稼働登録を兼ねる（相当物ができたらそちらにも登録する）。
EARN_RESEARCH_PATH = "content/_earn_research.md"
EARN_RESEARCH_MAX_HOURS = 48  # 1日休んでも鳴らない。2日黙ったら鳴る


def earn_research_heartbeat(last_commit, now, max_hours=EARN_RESEARCH_MAX_HOURS):
    """稼ぎ方研究担当の作業ログが止まっていたら、知らせる文字列を返す。

    last_commit は最終コミット日時（tz付き）。ファイルが無ければ None を渡す。
    """
    if last_commit is None:
        return (
            f"{EARN_RESEARCH_PATH} が見つかりません。"
            f"稼ぎ方研究担当の作業ログです（沈黙禁止＝0件の日も1行書く設計）"
        )
    hours = (now - last_commit).total_seconds() / 3600
    if hours > max_hours:
        return (
            f"{EARN_RESEARCH_PATH}: 最後の追記から{hours:.0f}時間たっています"
            f"（上限{max_hours}時間）。稼ぎ方研究担当（毎日15:30 JST）が"
            f"止まっている可能性があります"
        )
    return None
```

- [ ] **Step 4: テストが通ることを確かめる**

Run: `python -m pytest tests/test_check_freshness.py -k earn_research -q`
Expected: 3 passed

- [ ] **Step 5: コミット**

```bash
git add tools/check_freshness.py tests/test_check_freshness.py && git commit -m "feat: 稼ぎ方研究担当の heartbeat（48時間の沈黙で鳴る）"
```

---

## Task 5: 金額の鮮度の番人（check_freshness.py）

**Files:**
- Modify: `tools/check_freshness.py`（Task 4 の下）
- Test: `tests/test_check_freshness.py`（末尾）

**何を作るか:** 記事の金額ブロックに書かれた確認日が180日を超えたら、週次の再確認リストに出す。**単価も規約も変わるから。**⚠️ ビルドは止めない（既存 `_checked_errors` と同じ思想＝古さで公開を止めない）。

- [ ] **Step 1: 失敗するテストを書く**

`tests/test_check_freshness.py` の末尾に足す:

既存の `from check_freshness import (` の括弧の中に `money_note_staleness` を足す。
記事の偽物は、既にこのファイルが import している `SimpleNamespace` を使う（既存の型に合わせる）:

```python
def _FakeArticle(slug, body_html):
    return SimpleNamespace(slug=slug, body_html=body_html)


def _money_body(checked):
    return (
        '<div class="money-note">金額の目安: 月1〜6万円\n'
        f'根拠: 出典 <a href="https://example.com">価格表</a>・{checked}確認\n'
        "この金額は目安であり、収益を保証するものではありません。</div>"
    )


def test_fresh_money_note_is_silent():
    articles = [_FakeArticle("a", _money_body("2026-08-01"))]
    assert money_note_staleness(articles, date(2026, 9, 1)) == []


def test_stale_money_note_is_listed():
    articles = [_FakeArticle("a", _money_body("2026-01-01"))]
    problems = money_note_staleness(articles, date(2026, 9, 1))
    assert len(problems) == 1
    assert "a" in problems[0]


def test_article_without_money_note_is_silent():
    articles = [_FakeArticle("a", "<p>金額を書かない記事</p>")]
    assert money_note_staleness(articles, date(2026, 9, 1)) == []
```

- [ ] **Step 2: 失敗することを確かめる**

Run: `python -m pytest tests/test_check_freshness.py -k money_note -q`
Expected: FAIL with "cannot import name 'money_note_staleness'"

- [ ] **Step 3: 最小の実装を書く**

`tools/check_freshness.py` の Task 4 の下に足す:

```python
# 金額ブロックの鮮度。単価も規約も変わるので、古い金額は再確認に回す。
# ⚠️ ビルドは止めない（古さで公開を止めない＝validate の _checked_errors と同じ思想）。
MONEY_NOTE_RE = re.compile(r'<div class="money-note">(.*?)</div>', re.S)
MONEY_DATE_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
MONEY_MAX_AGE_DAYS = 180


def money_note_staleness(articles, today: date, max_age_days=MONEY_MAX_AGE_DAYS):
    """金額ブロックの確認日が古い記事を挙げる。"""
    problems = []
    for article in articles:
        for block in MONEY_NOTE_RE.findall(article.body_html):
            found = MONEY_DATE_RE.search(block)
            if not found:
                continue
            checked = date(int(found.group(1)), int(found.group(2)), int(found.group(3)))
            age = (today - checked).days
            if age > max_age_days:
                problems.append(
                    f"{article.slug}: 金額の確認日が{age}日前です"
                    f"（{checked}・上限{max_age_days}日）。単価と規約を見直すこと"
                )
    return problems
```

- [ ] **Step 4: テストが通ることを確かめる**

Run: `python -m pytest tests/test_check_freshness.py -k money_note -q`
Expected: 3 passed

- [ ] **Step 5: main() に両方をつなぐ**

`tools/check_freshness.py` の `main()` の、弁護士ゲートの呼び出しの下に足す:

```python
    # 稼ぎ方研究担当の heartbeat と金額の鮮度（2026-08-14 稼ぎ方研究の設計）
    research_file = root / "content" / "_earn_research.md"
    last_commit = _last_commit_time(root, research_file)
    heartbeat = earn_research_heartbeat(last_commit, datetime.now(timezone.utc))
    if heartbeat:
        report.problems.append(heartbeat)
    report.problems.extend(money_note_staleness(articles, date.today()))
```

同じファイルの `money_note_staleness` の下に、git を見る小さな関数を足す:

```python
def _last_commit_time(root: Path, path: Path):
    """path の最後のコミット日時を返す。無ければ None。

    ⚠️ mtime ではなく git を見る（クローンし直すと mtime は当てにならない）。
    """
    if not path.exists():
        return None
    result = subprocess.run(
        ["git", "log", "-1", "--format=%cI", "--", str(path.relative_to(root))],
        cwd=root,
        capture_output=True,
        text=True,
    )
    stamp = result.stdout.strip()
    if not stamp:
        return None
    return datetime.fromisoformat(stamp)
```

ファイル先頭の import を直す（**既存行の置き換え**。重複行を作らない）:

- 26行目 `import re` の下に `import subprocess` を足す（アルファベット順）
- 30行目 `from datetime import date` → `from datetime import date, datetime, timezone` に**置き換える**

- [ ] **Step 6: 週次チェックを実際に流す**

Run: `python -m tools.check_freshness`
Expected: `content/_earn_research.md が見つかりません` が出る（Task 6 でファイルを作るので、ここではこれが正しい）。それ以外の新規エラーが出ないこと

- [ ] **Step 7: コミット**

```bash
git add tools/check_freshness.py tests/test_check_freshness.py && git commit -m "feat: 金額の鮮度（180日）の番人と、週次への接続"
```

---

## Task 6: 手順書2本（研究担当の作業ログとキューの追記）

**Files:**
- Create: `content/_earn_research.md`
- Modify: `content/_recipe_queue.md`（冒頭の型の説明の並びに足す）
- Modify: `content/_review_log.md`（観点を1つ足す）

**何を作るか:** 担当が読む手順書。**コードで強制できないもの（判断の型）だけを書く**——検査で守るものは書かない（二重記載は腐る）。

- [ ] **Step 1: `content/_earn_research.md` を作る**

以下をそのまま書く（設計書§3の内容）:

```markdown
# 稼ぎ方研究の作業ログ（稼ぎ方研究担当が使う）

**編集者向けの内部メモ。サイトには出ない**（ファイル名が `_` で始まるのでビルド対象外）。

毎日 15:30 JST に「稼ぎ方研究担当」が追記する。**採った研究パックは
`content/_recipe_queue.md` の `### 副業` 節に入れ、ここには根拠と見送り理由を残す。**

## この担当の役目

書き手（21:00）は**キューの上から書く**。研究の深さは、書く仕事とは別の仕事なので分けた。
🔑 **研究担当は「調べて設計する」、書き手は「試して書く」。**
⚠️ **研究担当が実測を代行しない**——書き手の縛り1「公開する指示文は必ず自分で試す」が
伝言ゲームで形骸化する。研究担当が渡すのは「何を測れば主張が立つか」まで。

## 🔥 進化の型（この担当の本体）

**古い情報をそのまま紹介しない。**世に出回っている稼ぎ方を、現行のAIで
「工程のどこが変わるか」まで進めてから渡す。

| | |
|---|---|
| 入口 | 「この稼ぎ方は昔からこう紹介されている」（**主張は一般化して扱う**） |
| 中身 | 現行AIだと工程のここが変わる → **どこまで変わるかを実測で示す**（実測は書き手がやる） |
| 出口 | 金額の目安（出典＋計算式＋免責）と、崩れどころの言い直し方 |

**最新化リサーチを必ず通す**＝現行モデル・ツール・プラットフォーム規約の確認。
確認した日付を研究パックに書く（記事の金額ブロックにそのまま入る）。

## 研究パックの様式（8点・全部書けないものは採らない）

1. **仮の題**（キューに入れる文そのもの）
2. **根拠**（源の番号＋実際の言い回し・語数・記事名。URLがあれば日付つき）
3. **実測の芯**＝この記事で何を測れば主張が立つか（測れないなら採らない）。
   🆕 **何回試すかもここに書く**（下の「試行回数を本文に書く」）
4. **既存との切り分け**（🔒 どの記事と隣接し、何が違うか）
   🚨 **earn の3本が既に同型**＝`listing-only-what-you-checked`／
   `proposal-without-inflating`／`client-reply-without-softening` は
   **「AIに書かせると、素材／条件に無いものが入り、あるものが落ちる」**という
   同じ発見を、扱う文書（フリマ説明文・提案文・取引先メール）だけ変えて3本並べている。
   **4本目を同じ型で書くと重複になる**（2026-08-15 の確認担当の指摘）
5. **節の縛り**（副業なら「必ず稼げる」を書かない、等）
6. 🆕 **単価の出典**＝URL＋確認日（YYYY-MM-DD）。
   プラットフォーム公表値・公的統計・大手調査に限る。
   🚨 **AIに相場を聞いて書かない。実在するページを開いて確かめる。**
   —— うちの記事[自分の棚卸しを売り物に変える](/recipes/sell-what-you-already-do/)が
   **実測で出した結論がこれ**＝「私は何で稼げますか」と聞くと、頼んでもいない
   金額が3〜4件返り、**どれにも出どころが書いていない**。金額を禁じると0件になり、
   代わりに自分で確かめる手順が返った。⚠️ **AIに相場を聞いて金額ブロックに書くのは、
   自分のサイトが実測で否定した型をそのままやることになる**
7. 🆕 **計算式**＝出典つき単価 × 明示した前提 → レンジ
   （例: 文字単価0.5〜3円 × 月2万字 = 月1〜6万円）。
   計算が立たない題材は調査データの直引き。**どちらも無ければ金額欄なしで出す**
   （🚨 金額のために出典をでっち上げない）
8. 🆕 **帯の判定**（下の3帯のどれか）

## 3帯

| 帯 | レンジ | 追加の縛り |
|---|---|---|
| 副業帯 | 月数万円 | 標準の型どおり |
| 準本業帯 | 月数十万円 | ＋**作業量の前提を必ず明示**（週何時間相当か） |
| 事業帯 | 月百万円超〜 | 具体額は**出典があるときだけ**。**構造の解説として書く**（「あなたも到達できる」とは書かない）＋**「この帯に到達するのはごく一部」を必ず明記**（生存者バイアス） |

🔑 **「本業でも通用する」の実装＝構造の進化を書く。**
自分が作業する（副業帯）→ AIで検品と段取りを仕組み化（準本業帯）→
人に任せて自分は判断に回る（事業帯）。**金額の夢ではなく構造の解説**で上の帯を扱う。

## 候補の源4つ（毎回すべて見る）

| # | 源 | 注意 |
|---|---|---|
| 1 | **定番副業の台帳**（ライティング／翻訳／画像／データ整理／代行系…） | 消化済みを下の台帳で管理する |
| 2 | **AI副業系の新刊・定説** | 源②の5縛りをそのまま適用（本文を写さない・書名を出して否定しない・未読の中身を評価しない・アフィリ禁止・書評を書かない） |
| 3 | **既存記事の隣接** | 「既出に乗らない核は何か」を1文で書けないものは落とす |
| 4 | **検索需要**（`docs/topic-candidates/` の最新） | ⚠️ 語数の多い順に採らない |

## コンプラ照合（パックごとに通す）

⚠️ **これは法的リスクの整理であって、法的助言ではない。**

- **黒4項目に非該当**: ①収益保証の断定 ②投資・トレードで稼ぐ系
  ③プラットフォーム規約に反するAI量産手口 ④情報商材の紹介
- **グレーの条件充足**: 収益額は金額ブロックの型でのみ／規約の引用は確認日つき／
  確定申告・税務は下ごしらえのみ（判断させない＋税理士でない旨）
- **帯の縛り**（上の表）

## GSCフィードバック（休眠中）

表示データが最低母数を超えたら、表示上位の隣接題材を優先する。
**いまは母数不足（表示17回）＝判定持ち越し。**母数が立ったらここを起こす。

## 🚨 沈黙禁止

**0件の日も必ず1行書く。**「今日は採れなかった」と書いてあることと、
担当が止まっていることは、見た目が同じでは困る。
（番人＝`tools/check_freshness.py` の `earn_research_heartbeat()`・48時間）

---

## 消化済みの定番副業（源①の台帳）

まだ無し。

## 作業ログ
```

- [ ] **Step 2: `content/_recipe_queue.md` に型の説明を足す**

「## 🔥 「定説を実測する」型」の節の**下**に、以下を足す:

```markdown
## 💰 稼ぎ方の記事を書くとき（2026-08-14 稼ぎ方研究の設計）

**金額は `money-note` ブロックの中だけに書く。**素の文で「月◯万円稼げる」と書かない。

    <div class="money-note">
    金額の目安: 月1〜6万円（副業帯）
    根拠: 文字単価0.5〜3円（出典: <a href="...">○○公表価格</a>・2026-08-15確認）× 月2万字の場合
    この金額は目安であり、収益を保証するものではありません。
    </div>

3点（出典リンク・確認日・免責の一文）が揃っていないと **`validate.py` がビルドを止める**。
出典と計算式は研究パックに書いてあるので、**そのまま写す**（自分で調べ直さない）。

**3帯の縛り**＝副業帯（月数万円）は標準どおり／準本業帯（月数十万円）は
**作業量の前提を明示**（週何時間相当か）／事業帯（月百万円超〜）は
**構造の解説として書く**＋**「到達するのはごく一部」を必ず明記**。

🚨 **収益を保証する断定は書かない**（「必ず稼げ」「確実に稼げ」等は検査で止まる）。
🚨 **投資・トレードで稼ぐ系は書かない**（黒レーン）。

## 🔢 試行回数を本文に書く（2026-08-15 確認担当の🚩5への回答・オーナー判断）

**「実測では」「こう返ります」と断定するなら、何回試したか(n)を本文に書く。**

確認担当の初回（2026-08-15）で、**独立の目9本が全員この点を最初に挙げた**＝
9本のうち回数を本文に書いているのは一部だけで、残りは現在形で断定しているのに
n が読めない。⚠️ **証拠ファイルには回数がある。無いのは記事の側。読者は証拠を開けない。**

🔑 **金額ブロックとまったく同じ型**＝根拠を記事の側に置く。

| 書き方 | 例 |
|---|---|
| ✅ | 「**3回試して3回とも**、線引きは書かれませんでした」 |
| ✅ | 「**1回だけの結果です**が、〜が落ちました」（1回なら1回と書く） |
| ❌ | 「そのまま頼むと、線引きは1行も書かれません」（全称。根拠は引用1つ） |

**適用は新しい記事から**（既存記事の遡及はしない＝手が回らない）。
⚠️ **機械検査は作らない**——日本語の断定を正規表現で追うと誤検知が出て、
`validate.py` 全体の信用が落ちる（このサイトの判断済みの型）。
**見るのは確認担当の観点**（`_review_log.md` の手順2-3）。
```

- [ ] **Step 3: `content/_review_log.md` に観点を1つ足す**

確認担当が見る4つの並びに、5つ目として足す:

```markdown
5. **金額の型**（2026-08-14 追加）
   - 金額ブロックの3点（出典リンク・確認日・免責）が揃っているか
     ※機械も見ているが、**リンク先が本当に単価の根拠か**は人しか見られない
   - **ブロックの外に収入金額が書かれていないか**（機械は見ていない＝ここが人の担当。
     「月3,000円のツール」は価格なのでよい。「月3万円稼げる」が素の文にあったら🚩）
   - **計算が再現できるか**（単価×前提＝レンジになっているか。桁が合っているか）

6. **試行回数(n)が本文にあるか**（2026-08-15 追加・初回の🚩5への回答）
   - 「実測では」「こう返ります」と**断定しているのに n が本文に無い**なら指摘する
   - 1回なら「1回だけの結果ですが」と書いてあればよい（回数の多さは要件ではない）
   - ⚠️ **適用は新しい記事から**（既存記事の遡及はしない）
   - ⚠️ 機械検査は無い＝ここが唯一の見張り
```

- [ ] **Step 4: 週次チェックが静かになることを確かめる**

```bash
git add content/_earn_research.md content/_recipe_queue.md content/_review_log.md && git commit -m "docs: 稼ぎ方研究の手順書（研究担当・キュー・確認担当の観点5）"
```

Run: `python -m tools.check_freshness`
Expected: `_earn_research.md が見つかりません` が**消える**（コミットしたので `_last_commit_time` が日時を返す）

- [ ] **Step 5: 全部通ることを確かめる**

Run: `python -m pytest -q && python -m src.build`
Expected: テスト全部 pass ＋ ビルド成功

---

## Task 7: 研究パックを手で2〜3本作って型を実地検証する

**Files:**
- Modify: `content/_earn_research.md`（作業ログに追記）
- Modify: `content/_recipe_queue.md`（`### 副業` 節にパックを追加）

**何を作るか:** ⚠️ **ルーティン登録の前に、型が回ることを実物で確かめる**（8/14 の自動化担当と同じSOP）。ここは人間セッションの仕事。

- [ ] **Step 1: 定番副業から2〜3件選び、最新化リサーチをする**

WebSearch で以下を確認する（**推測で単価を書かない**）:
- その副業の現在の相場（プラットフォーム公表値・公的統計・大手調査）
- 現行AIで工程のどこが変わるか
- プラットフォームのAI利用規約（変わりやすい＝確認日必須）

- [ ] **Step 2: 8点を全部書いて `### 副業` 節に足す**

様式は `content/_earn_research.md` の「研究パックの様式」に従う。
⚠️ **8点のどれか1つでも書けないものは採らない**（金額欄なしで出すのは可）。

- [ ] **Step 3: 見送ったものと理由も作業ログに残す**

**同じ源をまた引かないため。**

- [ ] **Step 4: コミット**

```bash
git add content/_earn_research.md content/_recipe_queue.md && git commit -m "content: 稼ぎ方の研究パック（初回・手動で型を検証）" && git push origin main
```

- [ ] **Step 5: 書き手が実際に書けたかを翌日確かめる**

21:00 の書き手がこのパックから記事を書き、`validate.py` が通ってサイトに出たことを確かめる。
⚠️ **ここで詰まったら、ルーティンを登録する前に手順書を直す。**

---

## Task 8: クラウドルーティンの登録（Task 7 の検証が通ってから）

**Files:**
- Modify: `SESSION_HANDOFF.md`（ルーティン一覧に追加）

**何を作るか:** 毎日15:30 JST の「稼ぎ方研究担当」。

⚠️ **Task 7 で型が回ることを確かめてから登録する。**

- [ ] **Step 1: プロンプトを書く**

**本数・型の定義はプロンプトに書かない**（キューと手順書が単一ソース。二重記載は腐る＝2026-08-10 の実測）。以下をそのまま使う:

```
あなたは ai-tsukaikata.com の「稼ぎ方研究担当」です。

手順0: 作業フォルダで `git pull origin main` を実行し、最新を取ってから始める。

手順1: `content/_earn_research.md` を最初に全部読む。ここがあなたの手順書で、
様式・縛り・帯の定義はすべてそこにある（このプロンプトには書いていない。
2か所に書くと必ず片方が古くなるため）。

手順2: 手順書の「候補の源4つ」をすべて当たり、研究パックを作る。
件数は決めない——8点の様式を全部満たせるものだけを出す。
🚨 単価はAIに聞かず、実在するページを開いて確かめること（手順書の6番）。

手順3: 採ったパックを `content/_recipe_queue.md` の「### 副業」節に足す。
根拠と、見送ったものの理由を `content/_earn_research.md` の作業ログに残す。

手順4: コミットして origin の main に push する。
🚨 0件だった日も「今日は採れなかった」と1行書いてコミットする（沈黙禁止）。
ログが空だと、担当が止まったのか採れなかったのかが区別できなくなる。

最後の報告に必ず書くこと: 何件採ったか／見送った理由／詰まったところ。
```

- [ ] **Step 2: schedule スキルで登録する**

`/schedule` を使い、毎日 15:30 JST・model=opus-5 で作る。
⚠️ **保存後に読み直して、貼れているか目で確かめる**（台帳14番＝プロンプトが
保存されていないことが実際に起きた）。

- [ ] **Step 3: `SESSION_HANDOFF.md` のルーティン一覧に足す**

「いまの1日（ai-tsukaikata のクラウドルーティン5本）」の表に行を足し、**6本**に直す。
trigger ID も書く。

- [ ] **Step 4: コミット**

```bash
git add SESSION_HANDOFF.md && git commit -m "docs: 稼ぎ方研究担当をルーティン一覧に追加（6本目）" && git push origin main
```

- [ ] **Step 5: 初回の翌日、実際に動いたかを確かめる**

```bash
git log origin/main --oneline -5 && python -m tools.check_freshness
```

Expected: 15:30台に研究担当のコミットがある。heartbeat が鳴っていない

---

## 完了の定義

- [ ] `python -m pytest -q` が全部 pass（新規テスト19件を含む＝Task1:5・Task2:8・Task4:3・Task5:3）
- [ ] `python -m src.build` が成功する
- [ ] `python -m tools.check_freshness` に新規の問題が出ない
- [ ] 金額ブロックのある記事が実際に公開され、ライト／ダーク両方で読める
- [ ] 研究パックから書き手が記事を書けた（Task 7 Step 5）
- [ ] ルーティンが登録され、初回が動いた（Task 8 Step 5）
