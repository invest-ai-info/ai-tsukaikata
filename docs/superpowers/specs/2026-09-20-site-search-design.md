# サイト内検索の設計 — ヘッダーの窓と `/search/` ページ

作成: 2026-09-20 JST（オーナーの依頼「そろそろ検索窓を作りましょう」）
状態: **設計承認済み（2026-09-20 オーナー承認・案A＝自前）**。実装はこれから

対象: サイト本体（`src/` `templates/` `static/`）。トラッカー側は触らない。

## 0. 決めたこと（オーナーの選択・2026-09-20）

| 問い | 選択 | 退けた案 |
|---|---|---|
| 探せる対象 | **記事だけ**（187本＝レシピ・深掘り・固定ページ） | AIアップデート／メディアニュースは後から足せる作りにする |
| 置き場所と結果 | **全ページのヘッダーに窓＋結果は `/search/`** | ドロップダウン／トップだけ |
| 引っかかる文字 | **タイトル＋説明文＋タグ＋見出し（h2/h3）** | 指示文の本文（gzip 約170KB）／本文全部（約700KB） |
| 作り方 | **案A＝ビルドで索引JSONを生成＋素のJS** | 案B Google プログラム検索（広告・遅延・外部スクリプト）／案C Pagefind（バイナリが増える） |

🔑 **外部サービス無し・鍵無し・依存追加無し。**`copy.js` と同じ流儀（素のJS・JSが無くても壊れない）。

## 1. 索引 — `src/search.py` → `build/search.json`

- `build_index(articles) -> list[dict]` が記事ごとに
  `{"url", "title", "description", "tags", "headings", "category", "scene", "published"}` を返す。
  `search_json(articles) -> str` がそれを JSON（`ensure_ascii=False`・区切りは詰める）にする
- **見出し**＝`body_html` の `<h2>`/`<h3>` の文字だけ（タグを剥がし、実体参照を戻し、空白を1つに畳む）。
  `{: .what}` のような印は Markdown 変換の時点で class になっているので文字には残らない
- **生の文字だけ入れる。**正規化（§4）は表示側で行う。索引を2倍にしないため。
  `published` は `YYYY-MM-DD` の文字列、`scene` は無ければ `null`、`tags`/`headings` は空でも配列
- 全カテゴリを入れる（`pages` の about/privacy/start も）。特別扱いの分岐を作らない
- 実測（2026-09-20・187本）: 248KB・gzip 約70KB。**検索ページを開いたときだけ読む**ので他のページは重くならない
- `build.py` の `collect()` が `files["search.json"]` に足す（検証エラーがあれば他と同じく何も出さない）

## 2. 検索ページ — `/search/`

- `render_site()` が `templates/search.html` を `search/index.html` に組む（`/news/` と同じ扱い。記事ではない）
- ページの中身: 見出し「記事を探す」・大きい窓（`<form role="search">`＋`<input type="search" name="q">`）・
  結果を入れる `<div id="search-results">`・件数の行・`<noscript>`（「検索には JavaScript が必要です。
  レシピ一覧／深掘り一覧から探せます」とリンク）
- `<meta name="robots" content="noindex">` を付け、**sitemap に入れない**（`section_paths` に足さない）。
  検索結果ページを Google に拾わせないため
- `static/js/search.js` を**このページだけ**で読む（`base.html` には足さない）。差し込み口として `base.html` に
  `{% block head %}{% endblock %}` を1つ足し、`search.html` がそこに noindex と `<script defer>` を入れる
- 動き: 開いたら URL の `?q=` を窓に入れて結果を出す → `fetch("/search.json")` は1回だけ → 入力のたび（150ms の間引き）に
  絞り直し、`history.replaceState` で `?q=` を書き換える（共有できるURL）
- 結果は一覧ページのカードと同じ見た目（タイトル・説明文・カテゴリー／場面・日付）。DOM は `textContent` で組む
  （索引の文字を HTML として解釈しない）。**見出しだけに当たった記事**は「見出し『…』に一致」を1行添える
- `/search/` ではヘッダーの窓を出さない（テンプレート変数 `hide_header_search`）。同じ窓が2つ並ばないように

## 3. ヘッダーの窓 — `templates/base.html`

- サイト名の右に `<form class="site-search" action="/search/" role="search">` ＋
  `<input type="search" name="q" placeholder="記事を探す" aria-label="記事を探す">` ＋ `<button>検索</button>`
- **素のHTMLのフォーム**＝JS無しでも `/search/?q=…` へ飛ぶ。ヘッダーに JS は足さない
- CSS: `.site-header` は既に `flex-wrap`。窓は `margin-left: auto` で右に寄せ、スマホ幅（既存の 782行付近の
  `@media`）では `flex-basis: 100%` で2行目に回す。**横スクロールを作らない**（375px で確認）
- ダークモードは既存の変数（`--bg` `--fg` `--line` `--accent`）で配色する

## 4. 検索の決まり（JS 側）

- 正規化＝`String.prototype.normalize("NFKC")` → `toLowerCase()`。「ＧＭａｉｌ」「github」「Gmail」が同じに当たる。
  全角空白は NFKC で半角空白になる
- 語＝空白で区切る。**すべての語を含む記事だけ**（AND）。1文字でも検索できる（漢字1字が意味を持つ）
- 当たり判定は部分一致（日本語は単語の切れ目が無いため。辞書も分かち書きも要らない）
- 順位＝語ごとに タイトル 4点・タグ 3点・説明文 2点・見出し 1点（最大の当たり方を採る）を合計。同点は `published` の新しい順
- 0件＝「見つかりませんでした」＋レシピ一覧／深掘り一覧へのリンク。空欄＝「例: Gmail、副業、GitHub Actions」の案内
- 索引の読み込みに失敗したら「検索を読み込めませんでした。ページを再読み込みしてください」と出す（黙って空にしない）

## 5. 壊れ方の防止

- `tests/test_search.py`（Python）:
  - 全記事が索引に入る（`url` の集合が一致）／`headings` にタグ（`<`）が混ざらない／`tags` は配列
  - JSON として読み戻せる・`ensure_ascii=False` で日本語がそのまま
  - **索引の大きさに予算＝400KB**（超えたら落ちる。黙って重くならないため。実測 248KB＋5割）
  - `render_site()` の出力に `search/index.html` があり `noindex` を含む／sitemap に `/search/` が無い
  - `base.html` の窓が全ページに出て、`/search/` には出ない
- JS は自動テストが無い（この環境に Node が無い）。**ブラウザのプレビューで実際に打って確かめる**:
  「Gmail」「副業」「GitHub Actions」「ｇｍａｉｌ」（全角）・0件・空欄・`?q=` 直リンク・375px の横スクロール無し・
  ダークモード・コンソールエラー無し
- `build.yml` の `paths:` は `src/**` `templates/**` `static/**` を含むので push でそのまま配信される

## 6. やらないこと（今回）

- ニュースの検索（索引は `[{url,title,description,...}]` の並びなので、後で news の項目を同じ形で足せる）
- 指示文・本文全文の検索／候補のドロップダウン／当たり箇所の色付け／外部サービス
- ヘッダーの JS（窓は素のフォームのまま）

## 7. 完了の定義

1. `python -m pytest -q` 全部通る（新テスト込み）
2. `python -m src.build` が `search.json` と `search/index.html` を出す
3. プレビューで §5 の手動確認が全部通る
4. push → Build & Deploy 成功 → 本番の `/search/?q=Gmail` で結果が出る
