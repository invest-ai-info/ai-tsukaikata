# 進化ループ Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 記事を書くたびに教訓が蓄積→コード昇格→読者データで方向修正される3つの輪を導入し、キューを枯らさない。

**Architecture:** 設計書＝`docs/superpowers/specs/2026-08-11-evolution-loop-design.md`。
台帳（`content/_lessons.md`）と証拠（`docs/evidence/`）はファイル、昇格先は `validate.py`・型・図部品。
**フェーズA（8/11）は今夜21:00の実行に影響しない変更だけ**（キュー先頭3件の下への補充・docs）。
フェーズB（8/12）で担当の義務が変わる。`validate.py` はディスクを読まない設計なので、
証拠の読み込みは `build.py` 側で行い dict で渡す。

**Tech Stack:** Python 3.12・pytest・既存の validate/build/check_freshness の流儀に従う。LLM不使用（決定的検査のみ）。

---

## フェーズA — 8/11（今夜に影響しない）

### Task 1: サジェスト総当たりの再実行（種を増やして）

**Files:**
- Create: `<scratchpad>/suggest_sweep2.py`（使い捨て・リポジトリに入れない）
- Modify: `docs/superpowers/notes/2026-08-10-demand-research.md`（末尾に「2026-08-11 再実行」節を追記）

- [ ] **Step 1: スクリプトを書く**（前回コードの拡張。種に「作業」を足す）

```python
# -*- coding: utf-8 -*-
"""2026-08-10 の930クエリの続き。種を足して再実行する。
前回の種: ツール(ChatGPT/Claude/Gemini/生成AI/AI) x 作業11 x 文脈4。
今回は「作業」を15語足す。語尾32種は前回と同一。
"""
import json, time, urllib.parse, urllib.request

def suggest(q):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox&hl=ja&"
           + urllib.parse.urlencode({"q": q}))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode("utf-8"))[1]

TOOLS = ["chatgpt", "claude", "gemini", "生成ai", "ai"]
NEW_WORKS = ["要約", "スライド", "資料作成", "企画書", "報告書", "議事録 まとめ",
             "献立", "家計簿", "旅行 計画", "勉強法", "プレゼン", "読書",
             "スケジュール", "整理", "お礼 メール"]
TAILS = list("あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほ") [:28] + ["方法", "コツ", "例", "やり方"]

results = {}
for tool in TOOLS:
    for work in NEW_WORKS:
        for tail in ["", *TAILS]:
            q = f"{tool} {work} {tail}".strip()
            try:
                for s in suggest(q):
                    results.setdefault(s, q)
            except Exception:
                pass
            time.sleep(0.12)
print(len(results))
with open("sweep2.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=0)
```

⚠️ 語尾を全部回すと 5×15×33=2,475 クエリ ≒ 6分。多すぎるなら語尾を
`["", "方法", "コツ", "例", "やり方"] + ひらがな10種` に絞ってよい（前回の実測で
ひらがな語尾の当たりは偏る）。

- [ ] **Step 2: 実行して収集**（`$env:PYTHONUTF8=1; python suggest_sweep2.py`）
- [ ] **Step 3: 突き合わせ** — 収集語を前回と同じ除外（とは/料金/口コミ/求人/資格/株/危険/規制）で
  落とし、テーマに束ね、**既存23本＋キュー未処理13件に無いテーマ**を抽出する。
  判定は `grep -il <語幹> content/recipes/*.md content/_recipe_queue.md` で機械的に
- [ ] **Step 4: notes に追記** — 「2026-08-11 再実行」節＝種・件数・新規テーマ・キューに入れた件数

### Task 2: キュー補充（先頭3件の下に足す）

**Files:**
- Modify: `content/_recipe_queue.md`（「検索需要から入れたもの」節の**末尾**＝勉強・校正・スライドの**下**）

- [ ] **Step 1: 補充を書く** — Task 1 の結果＋確定済みの2件。確定済み2件の文面:

```markdown
### 補充（2026-08-11・進化ループ輪3の初回）

- [ ] 長い文書を、落としてはいけない情報ごと要約させる
  - 需要: 「ai 要約」系 **265語**（2026-08-10調査の最大テーマ）。既存の「あり」判定は
    語の一致だけの雑な判定で、要約を主役にした記事は実は無い
  - ⚠️ `stop-filler-sentences`（行数固定の埋め草）と「長い資料を読ませて聞きたいことだけ
    引き出す」（Q&A型・キュー内）と切り分けること。こちらは**要約という成果物**を作らせて、
    落ちた情報を検査する型
- [ ] 表の表記ゆれ（全角半角・社名の揺れ・日付形式）をAIに直させる
  - 需要: 表計算テーマ **135語** の一部。`batch-instead-of-repeat`（同じ処理の繰り返し）と
    `odd-numbers-in-tables`（異常値の検出）のどちらとも違う「正規化」の型
  - ⚠️ 直させた結果の検証（件数が合うか・直しすぎていないか）まで書くこと
```

Task 1 で新規テーマが出たら同じ形式（需要語数＋切り分け注意）で続ける。

- [ ] **Step 2: 検査** — `python -m pytest -q`（435 passed）と `python -m src.build`（45ファイル）
- [ ] **Step 3: コミット＆push**

```bash
git add content/_recipe_queue.md docs/superpowers/notes/2026-08-10-demand-research.md
git commit -m "content: キューを需要データから補充する（進化ループ輪3の初回）"
git push origin main
```

⚠️ **21:00 より前に push を終えること。**間に合わないなら翌朝に回す（中途半端な
時刻に push すると、実行中の担当と衝突する）。

---

## フェーズB — 8/12（今夜の結果を見てから）

### Task 3: 今夜の結果を読む（実装の前提）

- [ ] **Step 1:** `git pull` して 8/11 21:00 台のコミットを数える（3本あるか・1本ごとに分かれているか）
- [ ] **Step 2:** 報告メール（またはコミットの Claude-Session からセッション）で
  「何本公開したか」の報告があるかを確認（新プロンプトの検証）
- [ ] **Step 3:** 3本の切り口がかぶっていないかを見出しで確認
- [ ] **Step 4:** 結果を SESSION_HANDOFF の項目0に1行で記録。
  **想定と違ったら（0本・同時刻1コミット等）このフェーズを止めて原因を先に見る**
  （手順は「まず実際に送られた指示文を読む」＝Claude-Session トレーラ）

### Task 4: 台帳 `content/_lessons.md` を作る（種7件入り）

**Files:**
- Create: `content/_lessons.md`

- [ ] **Step 1: ファイルを書く**（全文）

```markdown
# 書き方の台帳（まだコードになっていない教訓だけを置く）

毎晩の担当は**書く前にここを全部読む**。学んだことがあれば足す（**ノルマではない**）。
形式＝「日付／出た記事／事実／次からどう書くか」。証拠があればリンクする。

⚠️ **ここは待合室であって住所録ではない。**2回出た教訓・全題材に効く教訓は
週次（月曜）で `validate.py`・記事の型・`tools/make_figures.py` へ昇格し、
下の「昇格済み」へ移す。生きている教訓が15件を超えたら整理する。
⚠️ 夜の担当は**追記のみ**。既存の教訓と「昇格済み」欄を書き換えない。

## 生きている教訓

- [2026-08-10 / translate-for-internal-use] AIは出現回数を数え間違える（workspace 4回を
  5回と申告）。**集計値を言わせず、照合可能な形（初出の文を原文のまま引用）で出させる**
- [2026-08-10 / translate-for-internal-use] 「2文に割って」は3文で返る。
  **個数の指定より上限の指定（「60字以内」）のほうが守られる**
- [2026-08-10 / translate-for-internal-use] 時差・夏時間の換算を実際に1時間間違えた。
  **換算・計算をさせるときは、使った前提（時差・夏時間の有無）を並記させる**＝誤りが
  結果の上で見える
- [2026-08-10 / translate-for-internal-use] 「原文に無いことを足さない」と「専門用語に
  言い換えを添える」は正面衝突する。**相反しうる指示は優先順位と印の形（〔 〕）まで指定する**
- [2026-08-08 / mail-needs-reply] 単一条件の抽出（「返信が要るものだけ」）は、隣接する
  カテゴリ（経費精算・アンケート督促）が**静かに落ちる**。**全件をどれかに割り当てる
  分類にするとモレが見える**
- [2026-08-08 / mail-needs-reply] 試した結果、題材の切り口自体が間違いと分かったら、
  **題材を組み替えてよい**（キューの題を変えて、変えた理由を記録する）
- [2026-08-09 / odd-numbers-in-tables] 統計っぽい指示（「平均から3.5倍離れた」）は
  少数データで破綻する（誤入力自体が平均を動かす・12個では届かない）。
  **閾値は実データに当てて確かめてから記事に載せる**

## 昇格済み（コード・型へ移った）

（まだ無い。移すときは「何へ・いつ」を1行で残す）
```

- [ ] **Step 2:** `python -m pytest -q` と `python -m src.build`（`_` 始まりなので件数不変=45）

### Task 5: 証拠の様式 `docs/evidence/TEMPLATE.md`

**Files:**
- Create: `docs/evidence/TEMPLATE.md`

- [ ] **Step 1: ファイルを書く**（全文）

```markdown
# 試した証拠 — <slug>（この行を書き換える）

記事に載せる指示文**すべて**についてこの形式で残す。⚠️ **返ってきたものは生のまま**
（要約すると「書いてあることを消す」— 2026-08-05 の教訓）。長すぎる返りは先頭と、
判定に使った部分を残して `…(中略)…` でよい。

## 指示文1

### 入力（架空データ。使ったものをそのまま）
### 送った指示文（記事と同一文字列）
### 返ってきたもの（生）
### 判定
採用 ／ 直した（→直後の指示文へ） ／ 落とした。理由を1行。
```

- [ ] **Step 2:** `python -m src.build`（docs/ はビルド対象外＝件数不変を確認）

### Task 6: キューに2条を足す

**Files:**
- Modify: `content/_recipe_queue.md`（「担当が守ること」の 8番の後ろ）

- [ ] **Step 1: 2条を追記**

```markdown
9. **書く前に `content/_lessons.md`（書き方の台帳）を全部読んで適用する。**
   過去の担当が実際に試して踏んだ失敗の蓄積で、ここを読まないと同じ穴に落ちる。
   新しく学んだことがあれば台帳の「生きている教訓」に足す（**ノルマではない**。
   追記のみ。既存の教訓と「昇格済み」欄は書き換えない）
10. **試した記録を `docs/evidence/<slug>.md` に残す**（様式＝`docs/evidence/TEMPLATE.md`）。
   記事に載せる指示文すべてについて「入力・送った指示文（記事と同一文字列）・
   返ってきたもの（生）・判定」。⚠️ `content/` の中に置かない（記事として拾われる）
```

- [ ] **Step 2:** `python -m pytest -q`・`python -m src.build`

### Task 7: キュー残量の床（週次メールで知らせる）— TDD

**Files:**
- Modify: `tools/check_freshness.py`
- Test: `tests/test_check_freshness.py`

- [ ] **Step 1: 失敗するテストを書く**（`tests/test_check_freshness.py` に追記）

```python
from tools.check_freshness import queue_shortage


def test_queue_shortage_fires_below_floor():
    queue = "\n".join(["- [ ] 題材A", "- [x] 済み", "- [!] 止めた", "- [ ] 題材B"])
    problem = queue_shortage(queue, floor=6)
    assert problem is not None
    assert "2件" in problem  # 未処理は [ ] だけを数える（[x] も [!] も違う）


def test_queue_shortage_quiet_at_or_above_floor():
    queue = "\n".join(f"- [ ] 題材{i}" for i in range(6))
    assert queue_shortage(queue, floor=6) is None
```

- [ ] **Step 2:** `python -m pytest tests/test_check_freshness.py -q` → FAIL（ImportError）
- [ ] **Step 3: 実装**（`check_freshness.py` の `check_articles` の後ろに追加し、`main()` から呼ぶ）

```python
QUEUE_PATH = "content/_recipe_queue.md"
QUEUE_FLOOR = 6  # 2晩ぶん。3本/晩で消化するので、ここを切ったら補充が最優先
UNPROCESSED_RE = re.compile(r"^- \[ \]", re.M)


def queue_shortage(queue_text: str, floor: int = QUEUE_FLOOR) -> str | None:
    """レシピの待ち行列が枯れかけていたら知らせる文字列を返す。

    ⚠️ 静かに枯れると、毎晩の担当が「題材が無い」で止まり始めてから気づくことになる。
    未処理は `- [ ]` だけ。`- [x]`（済み）も `- [!]`（止めた）も数えない。
    """
    count = len(UNPROCESSED_RE.findall(queue_text))
    if count < floor:
        return (
            f"{QUEUE_PATH}: 待ち行列の未処理が{count}件です"
            f"（床は{floor}件=2晩ぶん。補充が最優先です。"
            f"再実行の手順は docs/superpowers/notes/2026-08-10-demand-research.md）"
        )
    return None
```

`main()` の `report = check_articles(...)` の直後に:

```python
    queue_file = root / "content" / "_recipe_queue.md"
    shortage = queue_shortage(queue_file.read_text(encoding="utf-8"))
    if shortage:
        report.problems.append(shortage)
```

- [ ] **Step 4:** `python -m pytest tests/test_check_freshness.py -q` → PASS
- [ ] **Step 5:** 本番データで1回流す＝`python tools/check_freshness.py`（鳴り方を見る。
  現在13件なので鳴らないはず。⚠️ ネットワークに出るので数分かかる）

### Task 8: フェーズBのコミット・push・記録

- [ ] **Step 1:** 設計書 §8 の「教訓（8件）」を「教訓7件」に直す（実数）
- [ ] **Step 2:** SESSION_HANDOFF 項目0b に「v1導入済み（8/12）」と今夜の結果を記録
- [ ] **Step 3:** `python -m pytest -q`・`python -m src.build` 全通過を確認
- [ ] **Step 4:**

```bash
git add content/_lessons.md docs/evidence/TEMPLATE.md content/_recipe_queue.md \
  tools/check_freshness.py tests/test_check_freshness.py \
  docs/superpowers/specs/2026-08-11-evolution-loop-design.md SESSION_HANDOFF.md
git commit -m "feat: 進化ループv1（台帳・証拠様式・キュー2条・残量の床）"
git push origin main
```

---

## フェーズC — 8/14頃（証拠が2〜3晩たまってから）

### Task 9: 証拠照合を validate.py に足す — TDD・較正つき

**Files:**
- Modify: `src/validate.py`・`src/build.py`
- Test: `tests/test_validate.py`

**設計制約:** `validate()` はディスクを読まない（static_paths と同じ流儀）。
`build.py` が `docs/evidence/*.md` を読んで `evidence: dict[slug, str]` を渡す。
対象＝ `published >= date(2026, 8, 12)` のレシピだけ（**slug名指しの除外は作らない**。
日付は線であって名前ではない＝`FIGURE_EXEMPT_SLUGS` の教訓と両立）。

- [ ] **Step 1: 実物で較正** — 8/12〜13 の証拠ファイルに対して、記事の
  `PROMPT_RE.findall` の各文字列（`html.unescape` + `strip`）が完全一致で
  含まれるかを使い捨てスクリプトで測る。**一致率が100%でないなら、その原因
  （改行・空白の揺れ）を先に見てから正規化ルールを決める**
- [ ] **Step 2: 失敗するテストを書く**（`tests/test_validate.py`）

```python
def test_recipe_after_evidence_era_requires_evidence():
    article = _article(category="recipes", published=date(2026, 8, 12))
    errors = validate([article], evidence={})
    assert any("証拠" in e for e in errors)


def test_recipe_prompts_must_appear_in_evidence():
    article = _article(category="recipes", published=date(2026, 8, 12),
                       body_html='<div class="prompt">これを試す</div>' * 6 + FILLER)
    ok = validate([article], evidence={article.slug: "…これを試す…"})
    ng = validate([article], evidence={article.slug: "別の文だけ"})
    assert not [e for e in ok if "証拠" in e]
    assert [e for e in ng if "証拠" in e]


def test_old_recipes_are_exempt_by_date_not_by_name():
    article = _article(category="recipes", published=date(2026, 8, 1))
    assert not [e for e in validate([article], evidence={}) if "証拠" in e]
```

（`_article()` は既存のテストヘルパ。`FILLER` は密度下限を満たす既存の定型）

- [ ] **Step 3:** FAIL を確認 → 実装（`_evidence_errors(where, article, evidence)` を
  `_density_errors` の隣に。`EVIDENCE_SINCE = date(2026, 8, 12)` 定数。
  `validate(..., evidence: dict[str, str] | None = None)`＝None なら検査しない）
- [ ] **Step 4:** `build.py` で `docs/evidence` を読んで渡す（ディレクトリが無ければ空 dict）
- [ ] **Step 5:** 全テスト・ビルド・**既存記事が1本も落ちない**ことを確認 → コミット

---

## フェーズD — 8/17（月）: 週次1回目（実装ではなく運用）

- [ ] 台帳の昇格判定（2回出たものは？）／拾い読み1種／見える改善1件（バックログから）／
  キュー残量。SESSION_HANDOFF に「週次の型」として結果を1段落で記録

---

## Self-Review（済）

- 仕様網羅: 輪1=T4/T5/T6、輪2=T7+D、輪3=T1/T2、v1.5=T9、キュー床=T7、導入順=フェーズ構成 ✅
- プレースホルダ: 無し（全コード実文）✅
- 型整合: `queue_shortage` の名は T7 内で一貫。`evidence` 引数は T9 内で一貫 ✅
- スコープ: 単一計画で可（フェーズは日付ゲートであり別サブシステムではない）✅
