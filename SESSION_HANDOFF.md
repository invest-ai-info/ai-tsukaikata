# SESSION_HANDOFF — AIの使い方（ai-tsukaikata.com）

最終更新: 2026-08-01 22:51 JST

---

## 現在地

3段構えの**1段目が稼働中**。**2段目はコードと記事が完成し、`site` ブランチで人間のレビュー待ち**。

| 段 | 内容 | 状態 |
|---|---|---|
| 1 | AI更新情報トラッカー | ✅ **稼働中**（2026-08-01〜） |
| 2 | サイト本体 ai-tsukaikata.com | 🟡 **実装完了・未公開**。`site` ブランチ。次は下の3手 |
| 3 | 使い分けマップ | ⬜ 保留（トラッカーがデータを貯めてから） |

---

## 次のセッションでやること（2段目の公開）

コードも記事5本も完成している。残りは**人間にしかできない3手**。

1. **記事5本を読んで事実確認する**（← これが最優先）
   ローカルでプレビューできる: `python -m src.build` してから、Claude に「ai-tsukaikata-preview を開いて」と頼む（`http://localhost:8791`）
2. **`site` ブランチを `main` にマージして push**
3. **GitHub側の設定**（下の「公開に必要な設定」を順に）

記事は実物（`tracker/` 配下、marketwatch の `health-check.yml` / `generate_youtube_summary.py`、`.claude` のメモリ）を読んで書いてあるが、**言い過ぎ・事実誤認の最終ゲートは人間**。設計書 §5 ④のとおり完全自動公開はしない。

---

## 環境

| | |
|---|---|
| 作業フォルダ | `C:\Users\info0\ai-tsukaikata`（**OneDrive外**。同期が `.git` を壊すため） |
| GitHub | `invest-ai-info/ai-tsukaikata`（public） |
| ドメイン | `ai-tsukaikata.com`（2026-08-01 取得済み。GitHub Pages への接続は2段目の作業） |
| Python | 3.12.10。依存は `requirements.txt`（feedparser / PyYAML / pytest / Jinja2 / Markdown） |
| テスト | `python -m pytest -q` → 220 passed（トラッカー142 + サイト78） |

**Windows の注意:** ローカルで `python -m tracker.run` を叩くときは `$env:PYTHONUTF8=1` を付ける。コンソールが cp932 なので、日本語の出力で `UnicodeEncodeError` になることがある。

**marketwatch-ai とは運用が違う。** あちらは OneDrive 内・git リポジトリではなく API 同期で「SYNC禁忌」ルールがある。こちらは**普通の git リポジトリ**なので、その手の制約は一切ない。混同しないこと。

---

## 1段目（稼働中のトラッカー）

### 動いているもの

- 毎時 `:17` に `--mode check` — 15ソースを取得し、major は即メール、minor は溜める
- 毎朝 `07:22 JST` に `--mode digest` — 溜まった minor と死活警告を1通で送る
- 状態は `data/tracker/seen.json`（git にコミットされる。**生成物ではなく状態**）

### 設計上、触ると壊れるところ

- **`--mode check` は `--mode bootstrap` の後でしか走らせない。** `main()` にガードがあり、状態ファイルが無ければ exit 1 で止まる。これが無いと初回に1000通超のメールが飛ぶ（OpenAI のフィードだけで1105件）
- **ワークフローのコミットステップに `if: always()` を付けない。** 送信失敗時に状態をコミットしないことで「既読にしたのに届いていない」を防いでいる。付けると送信失敗が永久のデータ損失になる
- **`load_state` が壊れたファイルで例外を投げるのを「握り潰して空状態にフォールバック」しない。** 全 uid が新着に戻り、過去の major まで再送されて溢れる。落ちて人間に気づかせるのが正しい
- **`record_result` には生の取得件数を渡す。** `select_unseen` 後の新着件数を渡すと、更新の少ないソースが3時間で死亡扱いになる
- **`notify.py` の送信は `store.save_state` より前に呼ぶ。** 逆にすると送信失敗時に更新が失われる

### 既知の課題（調整期間の主題）

- **HuggingFace 系の major 率が高い**（実測: DeepSeek 87% / Kimi 89% / GLM 77% / Qwen 63%）。研究成果物リポジトリ（`eagle3_*`、`SAE-Res-*` 等）や同日の `-Base`/`-Instruct` 兄弟が多いため。**1時間に1通が上限**なので暴走はしないが、うるさければ派生除外ルールを足すか OpenRouter 経由（実際に提供開始されたモデルだけ）へ置き換える
- **`qwen-blog` は最新記事が約10ヶ月前**で実質休止。記事は返るので死活警告には出ない。Qwen の動きは `hf-qwen` で拾えている
- **`hf-xai` はモデル2件・2025年8月が最新**で実質死んでいる。Grok は `openrouter-xai` で追っているので実害はない。整理するなら `hf-xai` は外してよい

### ソース構成（15件）

`tracker/sources.yml` が単一ソース。追加はこのファイルに数行足すだけでコード変更不要。

種別は4つ: `rss` / `github_releases` / `huggingface`（`org` 指定） / `openrouter`（`org` = ベンダー接頭辞）。

⚠️ **HuggingFace の org 名は大文字小文字が効く。** `moonshotai`・`zai-org` は動くが `MoonshotAI`・`THUDM` は0件を返す。

⚠️ **x.ai は 403 で bot ブロックされている。User-Agent の偽装で迂回しない。** OpenRouter 経由が唯一の実測済みルート。

---

## 2段目（サイト本体・`site` ブランチ）

### できているもの

| | |
|---|---|
| 生成 | `python -m src.build` → `build/` に13ファイル。`build/` は `.gitignore` 済み |
| プレビュー | `ai-tsukaikata-preview`（`http://localhost:8791`）。設定は `.claude/launch.json` |
| 記事 | レシピ5本 + about / privacy。すべて実運用中の自動化から執筆 |
| 図 | `static/images/` に18枚（手描きSVG）。記事に `<figure>` で埋め込み |
| 記事の型 | **プロンプト中心**（2026-08-02 改訂）。プロンプト63個・コードブロック2個 |
| コピー | `static/js/copy.js` が指示文にコピーボタンを足す。JSが無くても指示文は読める |
| 配信 | `.github/workflows/build.yml` — push で テスト → ビルド → Pages |

### 記事の書き方（2026-08-02 に方針変更）

**コードではなくプロンプトを主役にする。**初版はPythonとYAMLが並んでいて、読者定義（「Excelマクロは触ったことがある程度の会社員」）と矛盾していた。運営者自身がコードを手で書いていない以上、公開する資産は「頼んだ言葉」のほう。

5ブロック構成のうち3番と4番が変わった。

1. これで何ができるか
2. 前提（**プログラミング不要**を明記）
3. **AIへの頼み方** — 指示文＋「なぜこの言い方か」
4. **うまくいかないときの言い直し方**
5. 応用・次の一手

**コードを残す基準:** 読者が自分で打つものは残す。AIが書くものは載せない。

指示文は生HTMLで書く。**Markdownの引用（`>`）は使わない**（コピーしたとき原文どおりになるように）。

```html
<div class="prompt">指示文をそのまま書く。
改行はそのまま出る。</div>
```

**「なぜこの言い方か」を必ず添える。**指示文だけ並べても真似できない。効く理由（「実際に開いて確認して」を付けないと存在しないURLを書いてくる、など）が本体。

### 図の足し方

`static/images/` にSVGを置き、記事に生HTMLで書くだけ。

```html
<figure class="figure">
<img src="/static/images/なにか.svg" alt="読み上げでも意味が通る説明">
<figcaption>キャプション</figcaption>
</figure>
```

- **参照先の実在と `alt` は `validate.py` が強制する。** 存在しない画像を貼るとビルドが落ちる
- SVGには `width`/`height`/`viewBox` を全部書く（無いとレイアウトシフトする）
- SVGに `<style>` を持たせ、`@media (prefers-color-scheme: dark)` を入れる。`<img>` 経由でもダークモードは効く。**外部CSSは当たらない**ので配色はSVGの中に持つ
- viewBox幅は720で揃えてある。CSSが `min-width: 600px` を効かせるので、スマホでは枠内で横スクロールする（縮めると図中の文字が5px相当になって読めない）
- **文字のはみ出しは目視では分からない。** 追加したらブラウザで `getBBox()` を測って viewBox 内に収まっているか確認する（実際に2枚はみ出していた）

計画書: `docs/superpowers/plans/2026-08-01-ai-tsukaikata-site.md`

### 設計上、触ると壊れるところ

- **`validate.py` のチェックを「うるさいから」で外さない。** これは機密漏れをコードで止める唯一の層で、記事化のたびに人間の注意力に頼らないためにある。誤検知が出たら**除外条件を精密にする**（例: 穴埋め語の許可リストに足す）。チェック自体を消さない
- **`build.py` は「全部通る or 何も出さない」。** 検証エラーが1件でもあれば `build/` に一切触らず exit 1 する。「エラーの記事だけ飛ばして続行」にしない。直った記事だけ新しく、壊れた記事だけ古い、という状態が公開に出る
- **`build.yml` の `paths:` フィルタを外さない。** トラッカーが毎時 `data/tracker/seen.json` を push するので、外すとサイトが1日24回リビルドされる
- **`build/CNAME` の生成を消さない。** 生成HTMLをコミットしない方式では、artifact に CNAME が無いとデプロイのたびに独自ドメインが外れる
- **記事の内部リンクは実在チェックが効く。** まだ書いていない記事へリンクするとビルドが落ちる。書いてから貼る

### 公開に必要な設定（運営者の作業・未実施）

1. `site` ブランチを `main` にマージして push
2. `Settings → Pages → Source` を **GitHub Actions** に変更（初期値の "Deploy from a branch" のままだと deploy が失敗する）
3. `Actions → Build & Deploy Site → Run workflow` で手動実行し、両ジョブが緑になるのを確認
4. レジストラで DNS を設定（GitHub Pages の Apex 用 A レコード4本 + `www` の CNAME → `invest-ai-info.github.io`）。**IPは[公式ドキュメント](https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site)で現行値を確認してから入れる**
5. `Settings → Pages → Custom domain` に `ai-tsukaikata.com` を入れて Save。DNS伝播後に `Enforce HTTPS`
6. Google Search Console に登録し、`https://ai-tsukaikata.com/sitemap.xml` を送信

### 既知のノイズ: テストがたまに赤くなる

`test_digest_sends_when_only_dead_sources_exist` が **全テスト実行の約3%** で `PermissionError` で落ちる（`load_state` の読み込み）。

- **コードの問題ではない。** 図の追加前のコミットで70回回して2回落ちる、同じ再現率。単体では 0/400 で再現しない
- この環境の **Norton 360** が `os.replace` 直後のファイルを掴む競合が濃厚（`.bat` を消される・requests のSSLが落ちる、と同系統）
- **GitHub Actions（ubuntu-latest）とプロダクションには影響しない**
- 直すなら `load_state` に短いリトライ。「壊れたファイルを握り潰すな」には抵触しない（JSONの破損は従来どおり落ちる）。稼働中の1段目に触るので未実施
- **赤くなったらまず1回再実行する。** 同じテストが同じ理由で落ちているだけなら、これ

### 検証済みであること（2026-08-01〜02）

- 230 passed
- 実弾テスト: 機密（GitHubトークン・生メールアドレス・`C:\Users\` 絶対パス）とリンク切れ・広告表記漏れを含む記事を `content/` に置いてビルド → **5件すべてを一度に検出して中止し、`build/` は1バイトも変わらなかった**
- ローカルプレビューで、CSS適用・スマホ幅375pxで横スクロールなし・コードブロックが各自の枠内で横スクロール（12個中10個）・コンソールエラーなし を確認
- 図18枚すべてで、参照先が200・`viewBox`あり・`width`/`height`あり・ダークモード対応あり・`alt`は最短94文字 を確認
- 図中テキストの `getBBox()` を全18枚で実測し、viewBox からのはみ出しゼロ（当初2枚はみ出していたので2行に分割して修正済み）
- スマホ幅375pxでは図が枠内で横スクロールし、図中の最小文字は約9.6px。デスクトップ1280pxではスクロールなし
- 指示文のコピー: Markdown原文 → 生成HTML → コピーされる文字列が**14個すべて完全一致**。実クリックで本物のクリップボードに入ることも確認（`is-done` 付与を観測）
- JSを剥がした状態でも指示文が読めて選択できることを確認

### 次に書く記事

`content/_ideas.md` に置いてある。AdSense申請は**記事20本を超えてから**なので、あと13本。

---

## 運用メモ

### 手動実行

```
https://github.com/invest-ai-info/ai-tsukaikata/actions
```
各ワークフローの「Run workflow」から。両方 `workflow_dispatch` 対応済み。

### GitHub 側の設定（済み）

- Workflow permissions = **Read and write**（これが読み取り専用だと `seen.json` の push が 403 で落ちる）
- Secrets = `GMAIL_USER` / `GMAIL_APP_PASSWORD`（`ALERT_RECIPIENT` は未設定＝送信元と同じ宛先に届く）

### 検証済みであること

2026-08-01 に end-to-end で実証済み。既読から Grok 2件を意図的に外して再検出させ、**メールが実際に届くこと**と **`github-actions[bot]` が `seen.json` をコミットできること**の両方を確認した（`ee3fbd6` → run #3 → `5e19d7d`）。

---

## 収益化の位置づけ

このサイトは [[project_monetization_strategy]] の「収益の第2の柱」。読者は**自動化したい非エンジニア**。

- AdSense 申請は**記事20本を超えてから**（不合格理由の1位はコンテンツ不足）
- AIツール分野は YMYL ではないので、投資サイトより審査は通りやすい
- アフィリエイトを入れたら「広告」または「PR」表記が法的に必須。サイト側の `validate.py` でコードから強制する設計になっている（2段目で実装）
