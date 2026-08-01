# SESSION_HANDOFF — AIの使い方（ai-tsukaikata.com）

最終更新: 2026-08-01 22:12 JST

---

## 現在地

3段構えの**1段目が完了・本番稼働中**。次は2段目。

| 段 | 内容 | 状態 |
|---|---|---|
| 1 | AI更新情報トラッカー | ✅ **稼働中**（2026-08-01〜） |
| 2 | サイト本体 ai-tsukaikata.com | ⬜ **次はここ**。設計書あり・実装計画から |
| 3 | 使い分けマップ | ⬜ 保留（トラッカーがデータを貯めてから） |

---

## 次のセッションでやること

**2段目（サイト本体）の実装計画を作り、実装する。**

1. 設計書 `docs/superpowers/specs/2026-08-01-ai-tsukaikata-site-design.md` を読む
2. `superpowers:writing-plans` で実装計画を作る（1段目と同じ流れ）
3. `superpowers:subagent-driven-development` で実装する

設計は承認済みなので、ブレインストーミングからやり直す必要はない。

**初回5本の記事の1本目「AIの最新情報を自動で集めて、重要なものだけメールで受け取る」は、1段目で作ったトラッカーそのものが原料になる。** 実物（`tracker/` 配下と `.github/workflows/`）を読んで書けば、実運用の裏付けがある記事になる。記憶や一般論から書かないこと。

---

## 環境

| | |
|---|---|
| 作業フォルダ | `C:\Users\info0\ai-tsukaikata`（**OneDrive外**。同期が `.git` を壊すため） |
| GitHub | `invest-ai-info/ai-tsukaikata`（public） |
| ドメイン | `ai-tsukaikata.com`（2026-08-01 取得済み。GitHub Pages への接続は2段目の作業） |
| Python | 3.12.10。依存は `requirements.txt`（feedparser / PyYAML / pytest） |
| テスト | `python -m pytest -q` → 142 passed |

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
