# 設計書: AI更新情報トラッカー

作成日: 2026-08-01
ステータス: 設計承認済み・実装計画待ち
関連: [ai-tsukaikata.com サイト設計書](2026-08-01-ai-tsukaikata-site-design.md)

---

## 1. これは何か

主要AIツール（Claude / Claude Code、ChatGPT、Gemini、Grok、中国系、日本系）の新機能・新モデルの発表を自動で捕捉し、重要度に応じてメールで通知する仕組み。

**まず運営者個人用に作る。** 公開ページ化は実運用でソースとノイズを調整してから。

### 全体の中での位置づけ

3段構えの1段目にあたる。

1. **本設計書: 更新情報トラッカー**（自分用・最短で動く）
2. サイト本体 ai-tsukaikata.com（別設計書）
3. 使い分けマップ（トラッカーがデータを貯めてから着手）

トラッカーを先に作る理由:

- 自分用なのでデザインもコンプラ審査も不要。既存の資産を配線するだけで動く
- 動いた瞬間に「AIの最新情報を自動で集める仕組み」というレシピ記事が1本生まれ、サイトの初回5本の1本になる
- 稼働させておくとサイトの記事ネタが自動で湧き続ける。サイトを先に作るとネタ探しが手動のまま残る

3段目の使い分けマップをいま作らないのは、根拠となる使用実績がまだ無いためである。受け売りの比較表を作っても価値がない。

### 流用できる既存資産（marketwatch-jp.com、実在を確認済み）

| 資産 | 場所 | 使い方 |
|---|---|---|
| Gmail SMTP送信 | `email_weekly_zone.py`（`GMAIL_USER` / `GMAIL_APP_PASSWORD` / `ALERT_RECIPIENT`） | 同じパターンで通知を送る |
| RSS取得と公開日パース | `fetch_political_news.py`（feedparser使用） | 取得処理の下敷き |
| `feedparser` 6.0.12 | 導入済み | 追加インストール不要 |

新規に書くのは「どのソースを見るか」と「何を重要と判定するか」のみ。

---

## 2. 決定事項

| 項目 | 決定 |
|---|---|
| 受け皿 | まず運営者個人へのメール通知。公開は後 |
| 通知粒度 | 重要度で分ける。major=即時メール / minor=毎朝のダイジェスト |
| チェック間隔 | 毎時（cron `17 * * * *`。混雑する毎時0分を避ける） |
| ダイジェスト | 毎朝 JST 7:22（cron `22 22 * * *` UTC） |
| 置き場所 | サイトと同一リポジトリの `tracker/` 配下。ワークフローは分離 |
| リポジトリ公開設定 | public（Actions実行時間が無制限、GitHub Pages無料枠も使えるため） |
| 判定に迷った場合 | minor に倒す（ダイジェストには必ず載るので見逃しは発生しない） |

---

## 3. ソース設計

### 3種別に正規化する

| 種別 | 対象 | 取得方法 |
|---|---|---|
| `rss` | 公式ブログ・ニュース | feedparser |
| `github_releases` | リリースを切っているOSS | `releases.atom` を feedparser |
| `huggingface` | 新モデルの公開 | `https://huggingface.co/api/models?author=<org>&sort=createdAt&direction=-1` |

**HuggingFace API が背骨になる。** 認証不要のJSON APIで、組織ごとの新モデルを作成日順に返す。GitHubにリリースを切らない中国系・日本系ベンダーの新モデル検知はこれが最も速く確実である。

### 実測結果（2026-08-01 時点）

到達性を実際に叩いて確認した。机上のURL推測は使わない。

| ソース | 結果 |
|---|---|
| Claude Code releases（`anthropics/claude-code`） | ✅ 10件 |
| Anthropic SDK releases（`anthropics/anthropic-sdk-python`） | ✅ 10件 |
| OpenAI news RSS（`openai.com/news/rss.xml`） | ✅ 1105件 |
| Google AI blog（`blog.google/technology/ai/rss/`） | ✅ 20件 |
| DeepMind blog（`deepmind.google/blog/rss.xml`） | ✅ 100件 |
| QwenLM blog（`qwenlm.github.io/blog/index.xml`） | ✅ 44件 |
| Sakana AI（`sakana.ai/feed.xml`） | ✅ 10件 |
| PFN技術ブログ（`tech.preferred.jp/ja/blog/feed/`） | ✅ 30件 |
| ELYZA note（`note.com/elyza/rss`） | ✅ 25件 |
| DeepSeek GitHub releases | ✅ |
| HuggingFace API（`deepseek-ai` / `Qwen`） | ✅ JSON取得成功 |
| Anthropic 公式news RSS | ❌ 404（`/news/rss.xml`・`/rss.xml`・`/engineering/rss.xml` の3パターンとも。RSSを提供していない） |
| xAI（`x.ai/news/rss.xml`） | ❌ 403（botブロック） |
| Qwen / Kimi の GitHub releases・tags | ⚠️ 0件（リリースを切っていない） |

### 取れなかったソースの扱い

- **Anthropic公式news** — Claude Code releases と SDK releases で実質的にカバーする（両方とも実測で稼働確認済み）。公式ニュースそのものは取得手段がないため、初回スコープでは追わない。
- **xAI (Grok)** — 403 で明示的にブロックされているため、HuggingFace の xAI 組織を見る形にする。**User-Agent を偽装してブロックを迂回することはしない。**
- **Qwen / Kimi** — GitHub releases が空なので HuggingFace API と公式ブログRSSで代替する。

### `sources.yml` の形

```yaml
sources:
  - id: claude-code
    vendor: Anthropic
    label: Claude Code
    type: github_releases
    url: https://github.com/anthropics/claude-code/releases.atom

  - id: openai-news
    vendor: OpenAI
    label: OpenAI News
    type: rss
    url: https://openai.com/news/rss.xml

  - id: hf-deepseek
    vendor: DeepSeek
    label: DeepSeek 新モデル
    type: huggingface
    org: deepseek-ai
```

ソースの追加はこのファイルに数行足すだけで済む。コードの変更を要しない。

---

## 4. アーキテクチャ

```
tracker/
├─ sources.yml     # 追跡対象の定義
├─ fetch.py        # 3種別 → Update に正規化
├─ classify.py     # 重要度判定
├─ store.py        # 既読管理
├─ notify.py       # メール本文の組み立てと送信
└─ run.py          # エントリポイント（--check / --digest / --bootstrap）
data/tracker/seen.json
```

サイト本体と同じ設計思想を取る。ネットワークとファイルとメールに触るのは `fetch.py` / `store.py` / `notify.py` の外殻だけで、`classify.py` は純粋関数にする。

| モジュール | 入力 → 出力 | 外部に触るか |
|---|---|---|
| `fetch.py` | sources.yml → `Update` のリスト | ネットワーク |
| `classify.py` | Update → importance を付けた Update | 触らない |
| `store.py` | Update のリスト → 未通知のみ抽出 / 既読を記録 | ファイル |
| `notify.py` | Update のリスト → メール本文、送信 | SMTP |
| `run.py` | 上記を繋ぐ | — |

### `Update` の形

```python
@dataclass(frozen=True)
class Update:
    uid: str              # 重複判定キー（source_id + エントリID のハッシュ）
    source_id: str
    vendor: str
    label: str
    title: str
    url: str
    published: datetime   # tz-aware UTC に正規化
    summary: str          # 200文字上限（後述の著作権対策）
    importance: str       # "major" | "minor"
```

---

## 5. 重要度の判定（`classify.py`）

ルールベースで実装する。LLMは使わない（毎時走るのでコストと遅延が乗り、かつ判定がぶれてテストできなくなるため）。

### major と判定する条件

いずれかに該当する場合。

- タイトルに発表を示す語を含む
  - 英語: `introducing` / `launch` / `launching` / `announcing` / `now available` / `unveil`
  - 日本語: 「発表」「提供開始」「リリース」「公開しました」「新モデル」
- `github_releases` でバージョンの major または minor が上がった（`v1.2.0` は major扱い、`v1.2.3` の patch は minor）
- `huggingface` で新しいベースモデルが出た

### HuggingFace の派生モデルを除外する

HuggingFace の組織は量子化版や形式違いを大量に公開するため、そのまま扱うと通知が溢れる。モデル名が以下のいずれかの接尾辞を持つ場合は派生とみなし minor に落とす。

`-GGUF` / `-AWQ` / `-GPTQ` / `-int4` / `-int8` / `-FP8` / `-hf` / `-bnb`

実測時に取得した `Qwen/Qwen3-ForcedAligner-0.6B-hf` はこの規則により minor になる。

### 判定に迷う場合は minor に倒す

minor もダイジェストには必ず載るため、**誤判定で情報を失うことはない。最大24時間遅れるだけである。** 逆に major に倒すと通知が溢れて全部読まなくなり、そちらのほうが実害が大きい。

---

## 6. 既読管理と取りこぼし防止（`store.py`）

`data/tracker/seen.json` に通知済み `uid` と初回検出時刻を記録する。

```json
{ "uids": { "<uid>": "2026-08-01T17:12:00+00:00" } }
```

- **取りこぼしはゼロ。** 判定は「seen.json に無いもの＝新着」なので、GitHub Actions の cron が遅延・スキップしても、次に走ったときに必ず拾う。遅れるだけで失われない。
- 90日を超えた `uid` は掃除する（ファイルが無限に肥大しないように）
- **初回起動時は通知しない。** `--bootstrap` モードで全件を seen に記録するだけにする。これをしないと初回に1000通以上（OpenAI news だけで1105件）のメールが飛ぶ。

---

## 7. 通知（`notify.py`）

- **major**: 検出した実行の中でまとめて即時1通。1件ごとに送らない
- **minor**: 毎朝のダイジェストに1通でまとめる
- 該当なしの場合は**送らない**（「新着なし」メールは通知疲れの元）
- 本文はプレーンテキストとHTMLの両方。既存の `email_weekly_zone.py` のパターンを踏襲
- 各項目は「ベンダー名 / タイトル / 公開日 / 出典URL / 要約（200文字以内）」

### ソースのサイレント死を検知する

フィードURLは予告なく変わる。**3回連続で取得失敗または0件だったソースは、警告としてダイジェストの末尾に載せる。** これがないと「静かに情報が来なくなっていたことに数ヶ月気づかない」という最悪の壊れ方をする。marketwatch側の `automation-health.yml` と同じ発想である。

---

## 8. 著作権とコンプラ

ニュース記事の本文転載は著作権侵害にあたる。安全な形は「見出し＋出典リンク＋自分の一言コメント」であり、この形から外れられないようコードで縛る。

| 規則 | 実装 |
|---|---|
| 本文を保存しない | `Update` に本文フィールドを持たせない |
| 要約は短く | `summary` を200文字で機械的に切る。上限はコード側で強制 |
| 出典を必ず示す | `url` を必須項目とし、欠けた場合は取り込まない |
| bot ブロックを迂回しない | User-Agent の偽装をしない。403 のソースは別ルートを使うか諦める |

自分用の通知に留まる間は公衆送信にあたらないが、**公開フェーズでそのまま出せる形で最初から作る**。後から作り直さないためである。

本設計書は法的助言ではない。公開フェーズに進む際は専門家の確認を経ること。

---

## 9. CI

| ワークフロー | cron | 内容 |
|---|---|---|
| `tracker.yml` | `17 * * * *` + `workflow_dispatch` | 毎時チェック。major があれば即メール。seen.json を更新してコミット |
| `tracker-digest.yml` | `22 22 * * *`（JST 7:22）+ `workflow_dispatch` | minor をまとめてダイジェスト送信。ソースの死活も報告 |

- **毎時0分を避ける。** GitHub Actions の cron は毎時0分に負荷が集中し、遅延・スキップが起きやすい
- `workflow_dispatch` を必ず付ける。手動実行できないと詰まったときに手が出せない
- Secrets は `GMAIL_USER` / `GMAIL_APP_PASSWORD` / `ALERT_RECIPIENT` をリポジトリに登録し、ワークフローの `env` でまとめて渡す
- seen.json の更新コミットは `data/` 配下なので、サイトビルド側のパスフィルタ（`content/` `templates/` `static/` `src/`）に掛からず、**ビルドを誤起動しない**

---

## 10. テスト

ネットワークに出ない。固定のサンプルXML/JSONを `tests/fixtures/` に置いて検証する。

| テスト | 検証内容 |
|---|---|
| `test_fetch.py` | 3種別それぞれのパース、日付のtz正規化、壊れたフィードで落ちない |
| `test_classify.py` | 英語・日本語の発表語、バージョン番号のmajor/minor、HF派生モデルの除外。**ここが最も厚い** |
| `test_store.py` | 既読判定、bootstrapで通知が出ないこと、90日掃除 |
| `test_notify.py` | 本文の組み立て、200文字上限が効くこと、該当なしで送信しないこと。送信自体はモック |

---

## 11. スコープ外

- 公開ページ化（実運用でソースとノイズを調整してから）
- 使い分けマップ（3段目。トラッカーがデータを貯めてから）
- X / Twitter の監視（API有料。従量課金のみに改定済みのため見送り）
- Anthropic 公式news の取得（RSS未提供。releases 2本で代替）
- LLMによる要約生成（毎時走るためコストと遅延が乗る。必要になってから検討）

---

## 12. 次のアクション

| # | 内容 | 担当 |
|---|---|---|
| 1 | 実装計画の作成（writing-plans） | Claude |
| 2 | GitHubに新規リポジトリ `ai-tsukaikata`（public）を作成 | 運営者 or Claude（PAT経由） |
| 3 | Secrets 3件を登録（`GMAIL_USER` / `GMAIL_APP_PASSWORD` / `ALERT_RECIPIENT`） | 運営者 |
| 4 | 実装とテスト | Claude |
| 5 | `--bootstrap` で初期化し、cron稼働開始 | Claude |
| 6 | 1週間運用してノイズを見てソースと判定を調整 | 両方 |

---

## 13. リスクと対応

| リスク | 対応 |
|---|---|
| 初回に大量メールが飛ぶ | `--bootstrap` で初回は記録のみ（§6） |
| 通知が多すぎて読まなくなる | 迷ったらminor + ダイジェスト集約 + 該当なしは送らない（§5, §7） |
| フィードURLが変わり静かに情報が止まる | 3回連続失敗のソースをダイジェストで警告（§7） |
| Actions cron の遅延・スキップ | seen.json基準なので取りこぼしゼロ。遅れるだけ（§6） |
| 著作権侵害 | 本文を保存せず200文字上限をコードで強制（§8） |
| HuggingFace APIのレート制限 | 毎時1回・組織数分のみのアクセスに留める。認証なしで足りる想定だが、429が出たら間隔を空ける |
| xAI のように取得できないベンダーが増える | HuggingFace 組織で代替。それも無理なら追わない。ブロック迂回はしない（§8） |
