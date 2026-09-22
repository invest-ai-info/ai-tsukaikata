---
title: 97言語を自動で切り替える——知識は2025年1月で止まったまま
description: 2026年9月15日に発表された Gemini 3.8 Live・3.8 Live Extended Thinking について、Google の発表ページ・モデルカード・料金ページに書かれている数字だけを並べました。料金は前世代の Gemini 3.1 Flash Live Preview とまったく同じ価格の行にまとめられています。
category: tools
scene: choose
published: 2026-09-15
checked: 2026-09-15
tags: [Gemini, 音声AI, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年9月15日に、音声で会話するための2つのモデルを発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/>）。

- **Gemini 3.8 Live**
- **Gemini 3.8 Live Extended Thinking**
公式の発表ページ・モデルカード・料金ページに書かれている数字だけを並べます。3行にすると、こうなります。

- **会話の途中でも、97言語を自動で認識して切り替えます。**発表ページに「97 supported languages」と明記されています（出典: 同上）。
- **料金は、前世代の「Gemini 3.1 Flash Live Preview」とまったく同じ価格の行にまとめられています。**値上げも値下げもありません（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。
- <mark class="warn">モデルカードには、学習データの締め切りが2026年1月と明記されています</mark>（出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>）。発表は今日ですが、知識は1年8か月前で止まっています。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「自然に話せた」「賢くなった」といった使用感は一切書いていません。

## 前のモデルとの違い

### 同じ会社の1つ前は「Gemini 3.1 Flash Live Preview」

Gemini の音声対話モデルは、これまで **Gemini 3.1 Flash Live Preview**（プレビュー版）が最新でした。Google 自身のドキュメントに「Gemini 3.8 Live を、ほとんどの低遅延な音声エージェント用途でのデフォルトに更新することを推奨する」と書かれており（出典: <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview>）、この2つが前後の関係にあることは公式に確認できます。

<mark>いちばん大きな変化は、性能や値段ではなく「プレビューから正式版になった」ことです。</mark>3.1 Flash Live Preview のドキュメントには "legacy preview model" と書かれていますが、3.8 Live / 3.8 Live Extended Thinking のドキュメントは "Stable" と表示されています（出典: <https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live>）。

| | Gemini 3.1 Flash Live Preview（旧） | Gemini 3.8 Live / 3.8 Live Extended Thinking（新） |
|---|---|---|
| 提供状況 | Preview（legacy preview model） | Stable |
| 入力できる量 | 131,072トークン | 131,072トークン |
| 出力できる量 | 65,536トークン | 65,536トークン |
| 入力の種類 | テキスト・画像・音声・動画 | テキスト・画像・音声・動画 |
| 出力の種類 | テキストと音声 | テキストと音声 |
| 最終更新 | 2026年3月 | 2026年9月 |

出典: <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview>、<https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live>、<https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking>

<mark>一度に読める量・書ける量は、前世代からまったく変わっていません。</mark>入力13万トークンあまり・出力6.5万トークンあまりという数字は、両方のドキュメントに同じ値で載っています。

モデルカードには「Gemini 3.8 Audio is based on Gemini 3 Pro」とも書かれています（出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>）。音声専用にゼロから作られたモデルではなく、テキスト向けの Gemini 3 Pro をもとにしたものです。

### 料金も、同じ行にまとめられている

料金ページを見ると、もっとはっきりします。**`gemini-3.1-flash-live-preview`・`gemini-3.8-live`・`gemini-3.8-live-extended-thinking` の3つのモデルIDが、同じ価格表の1行にまとめて書かれています**（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。

| 使い方 | 単価 |
|---|---|
| 入力（テキスト） | $0.75 |
| 入力（音声） | $3.00（または $0.005／分） |
| 入力（画像・動画） | $1.00（または $0.002／分） |
| 出力（テキスト・思考トークン込み） | $4.50 |
| 出力（音声・思考トークン込み） | $12.00（または $0.018／分） |

出典: <https://ai.google.dev/gemini-api/docs/pricing>（100万トークンあたりのドル・有料層。3.1 Flash Live Preview を含む3モデル共通）

<figure class="figure">
<img src="/static/images/gemini38live-price-same.svg" alt="Gemini 3.1 Flash Live Preview（旧世代・プレビュー版）と Gemini 3.8 Live / 3.8 Live Extended Thinking（新世代・正式版）の、テキストの単価を比べた横棒グラフ。100万トークンあたりのドル。どちらも入力0.75ドル・出力4.50ドルで、バーの長さは2つとも同じ。料金ページでは3つのモデルIDが同じ価格の行にまとめられている。音声の単価も分あたり換算（入力0.005ドル・出力0.018ドル毎分）で同額。">
<figcaption>プレビューから正式版になっても、値段は動いていません</figcaption>
</figure>

<mark>「正式版に格上げされた」のに、値段は1円も動いていません。</mark>読める量・書ける量も同じなので、この記事に書ける違いは「プレビューが取れたこと」と、次に挙げる新しい機能のほうです。

### 新しく明記された機能

発表ページには、3.1 Flash Live Preview には無かった機能がいくつか挙げられています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/>）。

- <mark>97言語を、会話の途中でも自動で検出して切り替えます。</mark>発表ページに「automatically detects and transitions between 97 supported languages mid-conversation」と明記されています。
- **道具を使う処理をバックグラウンドで進めながら、会話を止めない。**「executes tools and API calls in the background while continuing the conversation」。
- **Gemini 3.8 Live Extended Thinking は、答えながら同時に考える。**"Let me check that…" のような相づちを挟みつつ、複数手順の作業を進行中に音声で説明すると書かれています。

これらは Google の発表ページに書かれている仕様であり、この記事の運営者が実際に試した感想ではありません。「自然に感じた」かどうかは書いていません。

提供場所も発表ページに書かれています（出典: 同上）。3.8 Live は本日から、開発者向けに Gemini API と Google AI Studio で、一般向けには Search Live で使えます。3.8 Live Extended Thinking はこれに加えて Gemini アプリで使え、Google AI Pro・Ultra の契約者は Docs で、Google AI の契約者全般は Gmail と Keep で使えると明記されています。<mark>企業向けの Gemini Enterprise 経由は、両モデルとも「private preview」（限定的な先行提供）にとどまります。</mark>

### 安全性の評価は、前の音声モデルではなく3.7 Flashと比べている

モデルカードのFrontier Safety（危険な能力がないかの評価）の項目には、こう書かれています。「Gemini 3.7 Flash（テキスト系のモデル）を評価した結果、追跡対象の危険な能力レベルに達していないことを確認した。Gemini 3.8 Live や 3.8 Live Extended Thinking は、3.7 Flash と比べて意味のある新しい能力や、性能の大きな向上を持たないと判断したため、3.7 Flash の評価結果をもとに、これらも危険な能力レベルに達していないと確信している」（出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>・意訳）。

<mark>つまり、安全性の比較対象は前の音声モデル（3.1 Flash Live Preview）ではなく、別系統のテキストモデル（3.7 Flash）です。</mark>発表ページは「知性の大幅な向上」とうたっていますが、公式の安全性評価の根拠は「3.7 Flash と大差ない」という前提に立っています。どちらも Google 自身の公式文書に書かれていることで、この記事ではどちらか一方だけを採用せず、両方をそのまま書いています。

## 他社のモデルとの比較

### ベンチマークの値

発表ページには、第三者機関による評価結果が挙げられています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/>）。

<figure class="figure">
<img src="/static/images/gemini38live-benchmarks.svg" alt="Gemini 3.8 Live / 3.8 Live Extended Thinking の発表ページにある第三者ベンチマーク5つを箱で並べた図。Speech to Speech Quality Indexは82.6で総合1位（Artificial Analysis調べ）、τ-Voiceは68.6%、τ-Voice-banking（Sierra調べ）は35.1%、Big Bench Audioは97.7%——この4つはいずれも3.8 Live Extended Thinkingの値。Speech Agent Arenaは2位で、こちらはExtended Thinkingではない3.8 Liveの値。指数・％・順位が混在し満点や測り方も指標ごとに違うため、値をそのまま並べており、足し引きや平均はしていない。評価したのは第三者だが、この記事では独自に検証していない。">
<figcaption>5つの指標は、満点も測り方もバラバラです</figcaption>
</figure>

<mark class="warn">この5つは指数・パーセント・順位が混在していて、満点も測り方も違うため、合計したり平均を取ったりできません。</mark>Google が発表ページで引用しているだけで、このサイトが独自に測定・検証したものではありません（このサイトの方針として、AIモデル同士の性能を自前で測ることはしていません）。

### 音声対話モデルを持っているのはGoogleとOpenAIだけ

<figure class="figure">
<img src="/static/images/gemini38live-vendor-grid.svg" alt="音声対話モデルの有無を3社で比べた表。音声対話モデル＝Geminiは3.8 Live / 3.8 Live Extended Thinkingあり、GPTはGPT-Live 1あり（頭脳は別モデル）、Claudeは記載なし。課金の単位＝Geminiはトークン単位（音声は分換算も併記）、GPTは音声は分単位で頭脳のモデルは別課金、Claudeは—。言語の自動切替＝Geminiは97言語（会話の途中でも自動検出）、GPTは記載なし、Claudeは—。「記載なし」「—」は機能が無いと明言されているのではなく、公式ページに書かれていない意味。">
<figcaption>音声対話の専用モデルを持たないのは、3社のうちAnthropicだけです</figcaption>
</figure>

OpenAI にも音声対話専用のモデル **GPT-Live 1** があります（出典: <https://developers.openai.com/api/docs/models>）。ただし課金の仕組みがGeminiとは違います。

| | Gemini 3.8 Live 系列（Google） | GPT-Live 1（OpenAI） |
|---|---|---|
| 音声のやり取り自体の値段 | 入力$0.005／分・出力$0.018／分（音声の分あたり換算） | $0.05／分（セッション料金） |
| 会話の中身を考える「頭脳」の値段 | 同じ料金に含まれる | 別料金（バックエンドのモデルをトークン単位で別途課金） |

出典: Gemini は<https://ai.google.dev/gemini-api/docs/pricing>、OpenAI は<https://developers.openai.com/api/docs/pricing>

<mark class="warn">単位も仕組みも違うので、この2つの金額をそのまま「安い・高い」とは比べられません。</mark>Gemini は音声も頭脳も1つの料金にまとまっているのに対し、GPT-Live 1 は音声のやり取り自体の代金で、実際に会話の中身を作るバックエンドのモデル（たとえば `gpt-realtime-2.1` など）はここに別料金で乗ります。参考までに、その `gpt-realtime-2.1` の単価は音声入力100万トークンあたり$32.00・出力$64.00、廉価版の `gpt-realtime-2.1-mini` は入力$10.00・出力$20.00です（出典: <https://developers.openai.com/api/docs/pricing>）。この2つも音声課金ではなくトークン課金なので、Geminiの分あたり価格とは単位が違い、表を分けています。

Anthropic の公式モデル一覧には、音声・音声対話（voice / real-time audio）についての記載が見当たりませんでした（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。<mark>Claude には、Gemini や GPT-Live に相当する音声対話専用のモデルは無いようです。</mark>「提供していない」と断定できる公式の否定文は見つけられなかったため、この記事では「記載が見当たらない」という書き方にとどめています。

## どういう人に効くか

**気になっていい人**

- 複数の言語がまざる会議や接客を、AIに音声でサポートさせたい人。**97言語を会話の途中でも自動で切り替える**という仕様は、他社の発表ページにはここまで明記されたものが見当たりませんでした。
- すでに Gemini 3.1 Flash Live Preview を API で使っている人。**乗り換えても値段は変わらず**、プレビューの不安定さから外れて正式版になります。

**急がなくていい人**

- 企業向けの Gemini Enterprise 経由で使いたい人。発表ページには「private preview」（限定的な先行提供）と明記されており（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/>）、まだ全社に開かれた提供ではありません。
- 2026年1月以降の出来事についてAIに音声で質問したい人。<mark class="warn">学習データの締め切りは2026年1月です</mark>（出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>）。今日発表されたモデルでも、知識はそこで止まっています。

**この記事で分からないこと**

実際に話しかけたときの反応の速さ、日本語での聞き取りやすさ、97言語の切り替えがどの程度スムーズか。発表ページには利用企業の声として「latency, fluidity, and tool-calling capabilities」への評価が紹介されていますが、具体的な数値は書かれていないため比較に使っていません。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 3.8 Live・3.8 Live Extended Thinking の発表（Google・2026年9月15日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-gemini-3-8-live-extended-thinking/>
   （Google DeepMind 側の <https://deepmind.google/blog/introducing-gemini-3-8-live-and-3-8-live-extended-thinking/> を開くと、このページへ転送されます）
2. Gemini 3.8 Audio（Live, Live Extended Thinking）のモデルカード（Google DeepMind 公式）: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>
3. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. Gemini 3.8 Live のモデルページ（Google 公式）: <https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live>
5. Gemini 3.8 Live Extended Thinking のモデルページ（Google 公式）: <https://ai.google.dev/gemini-api/docs/models/gemini-3.8-live-extended-thinking>
6. Gemini 3.1 Flash Live Preview のモデルページ（Google 公式）: <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-live-preview>
7. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
8. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>
9. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
