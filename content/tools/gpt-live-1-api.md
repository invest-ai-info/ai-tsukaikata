---
title: GPT-Live 1は秒単位課金——頭脳代は別料金
description: 2026年9月10日に発表されたOpenAIの音声対話モデル「GPT-Live 1」について、発表ページ本体がbot判定で読めなかったため、公式のRSS要旨とdevelopers.openai.comのモデル・料金・ガイドページに書かれている数字だけを並べました。電話（SIP）にもつながりますが、音声セッションの料金（分あたり$0.05）には頭脳役の別モデルの代金が含まれていません。
category: tools
scene: choose
published: 2026-09-21
checked: 2026-09-21
tags: [OpenAI, 音声AI, 料金, AI最新情報]
---

## 何が変わったか

OpenAI は 2026年9月10日、音声で会話するためのモデル **GPT-Live 1** を発表しました（出典: RSS要旨。下記）。3行にすると、こうなります。

- **音声のやり取りだけを、1分$0.05・秒単位で課金します。**発表と同時に会話の中身を考える「頭脳」役は別モデルで、**その代金はこの$0.05には含まれていません**（出典: <https://developers.openai.com/api/docs/models/gpt-live-1>）。
- <mark>電話（SIP）にもつながります。</mark>WebRTC・WebSocketに加えて、電話回線からの音声を直接つなげる仕組みが公式ガイドに明記されています（出典: <https://developers.openai.com/api/docs/guides/live>）。
- **同時に開ける通話の数は、契約Tierで25本から500本まで広がります。**ただし無料プランではそもそも使えません（出典: 同上）。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「自然に話せた」といった使用感は一切書いていません。

🚨 **発表ページ本体（`openai.com/index/introducing-gpt-live-1-in-the-api`）は、この記事を書いた環境からは読めませんでした。**応答ヘッダに `cf-mitigated: challenge` が付く403で、これは先方のbot判定です（許可リストを足しても直りません・UA偽装での迂回はしていません）。同じ `openai.com` のRSSは200で返るため、経路の問題ではなく先方の判定だと確認できます。代わりに、公式RSSの要旨と `developers.openai.com` のモデル・料金・ガイドページ（すべて200で取得）だけを使って書いています。

## 前のモデルとの違い

### OpenAIにとって「1つ前」は、音声とテキストを1つのモデルでこなす Realtime API

GPT-Live 1には、直接のバージョン違い（GPT-Live 0のようなもの）はありません。かわりにOpenAI公式ドキュメント「Voice agents」は、音声エージェントの作り方を3つのアーキテクチャに分けて説明しています（出典: <https://developers.openai.com/api/docs/guides/voice-agents>）。

<figure class="figure">
<img src="/static/images/gptlive1-architecture-grid.svg" alt="GPT-Live・Realtime API・連結パイプラインという3つの音声アーキテクチャを比べた表。向いている場面＝GPT-Liveは全二重の会話+別モデルの頭脳、Realtime APIは音声・思考・道具を1セッションで完結、連結パイプラインは各段階を自分で検査・置換したい時。選ぶ理由＝GPT-Liveは既存の処理はそのまま頭脳だけ選べる、Realtime APIは1つのモデルが音声のまま応答、連結パイプラインは中間のテキストを検査・置換できる。出典はOpenAI公式ドキュメント「Voice agents」の比較表。">
<figcaption>「音声」と「頭脳」を分けたのが、GPT-Liveがこれまでと違う点です</figcaption>
</figure>

<mark>これまでOpenAIの音声対話といえば Realtime API（`gpt-realtime-2.1` 等）でした。1つのモデルが音声を聞き取り、考え、音声で答えます。</mark>いっぽうGPT-Live 1は、会話を聞いて話す役割だけを持ち、考える作業（推論・道具の実行）は**別に選んだバックエンドのモデル**に投げます（出典: <https://developers.openai.com/api/docs/guides/live>）。バックエンドはOpenAIが用意した「Responses delegation」を使うか、自前のエージェントを接続する「client delegation」を選べます（出典: 同上）。

仕様を並べます。

| | GPT-Live 1 | Realtime API（`gpt-realtime-2.1`） |
|---|---|---|
| 対応エンドポイント | `v1/live/sessions` のみ | `v1/realtime` のみ（`v1/live/sessions` は非対応） |
| 入力の種類 | 音声・テキスト | 音声・テキスト・画像 |
| 出力の種類 | 音声・テキスト | 音声・テキスト |
| 頭脳（推論・道具実行） | 別モデルに委任 | 同じモデルの中で完結 |
| 学習データの締め切り | 2025年7月31日 | 2024年9月30日 |

出典: GPT-Live 1は<https://developers.openai.com/api/docs/models/gpt-live-1>、`gpt-realtime-2.1`は<https://developers.openai.com/api/docs/models/gpt-realtime-2.1>

<mark class="warn">2つは接続する窓口（エンドポイント）自体が別です。</mark>GPT-Live 1のモデルページでは `v1/realtime` が「Not supported」、逆に `gpt-realtime-2.1` のモデルページでは `v1/live/sessions` が「Not supported」と明記されています（出典: 同上の2ページ）。既存のRealtime API向けコードをそのままGPT-Live 1に差し替えることはできません。

### 料金は「音声セッション」と「頭脳」で別会計

GPT-Live 1のモデルページには、こう明記されています。「Voice sessions cost $0.05 per minute, billed per second. Backend model and tool usage is billed separately.」（出典: <https://developers.openai.com/api/docs/models/gpt-live-1>）。

| 項目 | 単価 |
|---|---|
| 音声セッション（GPT-Live 1） | $0.05／分（秒単位課金、切り上げなし） |
| バックエンドのモデル・道具の実行 | 別料金（選んだモデルの通常単価） |

出典: <https://developers.openai.com/api/docs/models/gpt-live-1>

たとえばバックエンドに `gpt-realtime-2.1` を選んだ場合、その利用分はこの単価が別途かかります（出典: <https://developers.openai.com/api/docs/pricing>）。

| 種類 | 入力 | キャッシュ入力 | 出力 |
|---|---|---|---|
| 音声（100万トークンあたり） | $32.00 | $0.40 | $64.00 |
| テキスト（100万トークンあたり） | $4.00 | $0.40 | $24.00 |
| 画像（100万トークンあたり） | $5.00 | $0.50 | — |

出典: <https://developers.openai.com/api/docs/pricing>（2026年9月21日に確認）

<mark class="warn">「1分$0.05」だけを見て予算を組むと、実際の請求はそれより高くなります。</mark>会話が長引くほど、また頭脳側でトークンを多く使うツール呼び出しをするほど、バックエンド側の料金が上乗せされます。**バックエンド側は「1分あたり」に統一された公式の換算値が無いため、この記事では合算額を計算していません。**

### 同時通話数はTierで20倍広がるが、無料プランは対象外

<figure class="figure">
<img src="/static/images/gptlive1-concurrent-tiers.svg" alt="GPT-Live 1の同時セッション数を契約Tierごとに比べた横棒グラフ。Tier 1は25セッション、Tier 2は50セッション、Tier 3は200セッション、Tier 4は300セッション、Tier 5は500セッションで、上位ほど枠が広がる。Freeプランはそもそも利用できない。バックエンド（頭脳役）のモデル呼び出しはこれとは別のレート制限に従う。">
<figcaption>いちばん下のTierでも25本、同時に会話できます</figcaption>
</figure>

| Tier | 同時セッション数 |
|---|---|
| Tier 1 | 25 |
| Tier 2 | 50 |
| Tier 3 | 200 |
| Tier 4 | 300 |
| Tier 5 | 500 |

出典: <https://developers.openai.com/api/docs/models/gpt-live-1>

<mark>Freeプランは「Unsupported usage tiers: Free」と明記されており、そもそも使えません</mark>（出典: 同上）。試すだけでも有料プランへの登録が要ります。

### 電話（SIP）とパートナー連携

<mark>GPT-Live 1は、WebRTC・WebSocketに加えて「Telephony and SIP」という接続方法を公式にサポートしています</mark>（出典: <https://developers.openai.com/api/docs/guides/live>）。SIPの通話音声はSRTPで暗号化され、WebSocket経由でも電話回線でよく使われるG.711（μ-law/A-law・8kHz）の音声をそのまま扱えると明記されています（出典: <https://developers.openai.com/api/docs/guides/voice-sip>）。LiveKit・Twilio・Telnyx・Daily/Pipecatとの連携ガイドも用意されています（出典: 同上）。

なお発表の要旨には「custom voices（独自の声）」という言葉もありますが、GPT-Live 1自身のガイドにこの言葉の説明は見当たりませんでした。見つかったのはRealtime API向けの別ガイドで、「Custom Voices are available only to approved customers（承認された顧客のみ利用可）」と書かれています（出典: <https://developers.openai.com/api/docs/guides/voice-prompting>）。**これがGPT-Live 1にもそのまま当てはまるのか、誰でも使える標準機能なのかは、公式ページからは確認できませんでした。**

## 他社のモデルとの比較

音声対話専用のモデルを持っているのは、いまのところ Google と OpenAI だけです。

<figure class="figure">
<img src="/static/images/gptlive1-vendor-voice-price.svg" alt="GPT-Live 1のセッション料金と、Gemini 3.8 Liveの音声単価を比べた横棒グラフ。1分あたりのドル。GPT-Live 1（音声のみ・頭脳代は別）は0.05ドル、Gemini 3.8 Liveの音声入力は0.005ドル、音声出力は0.018ドル。GPT-Live 1の0.05ドルは音声のやり取りだけの値段で、頭脳役の別モデルの代金は含まれていない。Geminiは音声も頭脳も1つの料金にまとまっており、課金の仕組みが違うため単純比較はできない。">
<figcaption>頭脳代を足す前から、GPT-Live 1のほうが高くつきます</figcaption>
</figure>

| | GPT-Live 1（OpenAI） | Gemini 3.8 Live（Google） |
|---|---|---|
| 音声の値段 | $0.05／分（音声のやり取りのみ） | 入力$0.005／分・出力$0.018／分 |
| 頭脳（推論）の値段 | 別料金（選んだバックエンドモデルの単価） | 同じ料金に含まれる |
| 電話（SIP）対応 | 明記あり | この記事では未確認 |
| 言語の自動切替 | 記載なし | 97言語（会話の途中でも自動検出） |

出典: GPT-Live 1は<https://developers.openai.com/api/docs/models/gpt-live-1>、Geminiは<https://ai.google.dev/gemini-api/docs/pricing>と[Gemini 3.8 Liveの記事](/tools/gemini-3-8-live/)（2026年9月21日に再確認）

<mark class="warn">単位も仕組みも違うので、この2つをそのまま「安い・高い」とは比べられません。</mark>Geminiは音声のやり取りと頭脳の働きが同じ料金にまとまっているのに対し、GPT-Live 1は音声のやり取りだけの値段で、頭脳役のモデルはここに別料金で乗ります。<mark>それでも、頭脳代を足す前の$0.05という時点で、すでにGeminiの音声入力（$0.005）・音声出力（$0.018）のどちらよりも高い値段になっています。</mark>

Anthropicの公式モデル一覧には、音声対話（voice / real-time audio）についての記載が見当たりませんでした（出典: <https://platform.claude.com/docs/en/models/overview>・2026年9月21日に確認）。<mark>3社のうち、音声対話専用のモデルを持たないのはAnthropicだけのようです。</mark>「提供していない」と断定できる公式の否定文は見つけられなかったため、この記事では「記載が見当たらない」という書き方にとどめています。

## どういう人に効くか

**気になっていい人**

- 電話（コールセンター・予約受付など）にAIの音声応対をつなげたい人。**SIPでの接続が公式にサポートされています。**
- 既存のテキストベースのエージェント（業務ロジック・ツール）をそのまま活かしつつ、音声の窓口だけ足したい人。<mark>頭脳役のモデルを、いま使っているものからそのまま選べます。</mark>
- 複数の通話を同時にさばく必要がある人。**Tier 5まで上げれば500本まで同時に開けます。**

**急がなくていい人**

- 予算を1分$0.05だけで見積もっている人。<mark class="warn">実際の請求には、バックエンドのモデル・ツール利用の料金が別途乗ります。</mark>
- まず無料で試したい人。**Freeプランはそもそも対象外です。**
- 「custom voices」を目当てにしている人。承認された顧客限定という記載しか見つかっていません。

**この記事で分からないこと**

実際に話しかけたときの応答の速さ、聞き取りの精度、電話回線越しの音質。バックエンド側の料金を含めた「1通話あたりの実費」も、公式にモデルの組み合わせごとの目安が出ていないため、この記事では計算していません。運営者も試していないので書けません。

## 出典一覧

発表ページ本体はbot判定で読めなかったため、公式RSSの要旨と developers.openai.com のドキュメントを中心に使っています。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. GPT-Live 1 発表の要旨（OpenAI公式RSS・2026年9月10日）: <https://openai.com/news/rss.xml>（該当item: "Build more natural voice experiences with GPT‑Live‑1 in the API"）
2. GPT-Live 1 モデルページ（OpenAI公式）: <https://developers.openai.com/api/docs/models/gpt-live-1>
3. GPT-Live のはじめ方ガイド（OpenAI公式）: <https://developers.openai.com/api/docs/guides/live>
4. Voice agents（アーキテクチャの比較・OpenAI公式）: <https://developers.openai.com/api/docs/guides/voice-agents>
5. GPT-Live の電話・SIP接続ガイド（OpenAI公式）: <https://developers.openai.com/api/docs/guides/voice-sip>
6. Voice models のプロンプトガイド（Custom Voicesの記載・OpenAI公式）: <https://developers.openai.com/api/docs/guides/voice-prompting>
7. `gpt-realtime-2.1` モデルページ（OpenAI公式）: <https://developers.openai.com/api/docs/models/gpt-realtime-2.1>
8. API の料金（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
9. Gemini API の料金（Google公式）: <https://ai.google.dev/gemini-api/docs/pricing>
10. モデル一覧と仕様（Anthropic公式ドキュメント）: <https://platform.claude.com/docs/en/models/overview>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
