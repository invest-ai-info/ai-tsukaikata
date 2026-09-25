---
title: Geminiの音声AIに動画の顔——数分限定・企業版のみ
description: 2026年9月24日に発表された Gemini 3.8 Live with Live Avatar について、Google の発表ページ・モデルカード・料金ページに書かれている数字だけを並べました。他社の音声AIとの比較も、各社の公式ページで確認しています。
category: tools
scene: choose
published: 2026-09-25
checked: 2026-09-25
tags: [Gemini, 音声AI, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年9月24日に **Gemini 3.8 Live with Live Avatar** を発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-with-live-avatar/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- **先週発表したばかりの「Gemini 3.8 Live」（音声のみ）に、動画の出力を足した機能です。**公式は「Building on the momentum of last week's Gemini 3.8 Live launch」と説明しています（出典: 同上）。
- <mark>使えるのは Gemini Enterprise 経由だけです</mark>。開発者向けの通常の Gemini API や、一般向けの Gemini アプリでは使えません（出典: 同上・<https://cloud.google.com/blog/products/ai-machine-learning/gemini-3-8-live-with-live-avatar-is-now-generally-available>）。
- <mark class="warn">動画を足すと、一度に書ける出力の上限が64,000トークンから24,000トークンに減ります</mark>（出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>）。

先に断っておきます。**この記事は運営者がこの機能を試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「自然に見えた」「よくできていた」といった使用感は一切書いていません。

前のモデルの話は [Gemini 3.8 Live](/tools/gemini-3-8-live/) に書いています。9日しか間が空いていないので、そちらを読んだ直後の人向けの記事でもあります。

### Live Avatar は何をする機能か

発表ページには、こう書かれています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-with-live-avatar/>）。

- 動画の生成と音声を組み合わせ、**「聞き・見て・話す」動く人物像**を作る
- 口の動きと音声を同期させ、自然な表情とスムーズな会話の切り替えができる
- 想定用途は「カスタマーサービス」「対話型の案内」

<mark>これは音声AIに顔と映像を足した機能で、文章を生成する機能ではありません。</mark>Google Cloud 側の発表では「conversational video agents across web, mobile, and interactive kiosks」（Webサイト・スマホアプリ・案内端末向けの対話動画エージェント）と、より具体的に書かれています（出典: <https://cloud.google.com/blog/products/ai-machine-learning/gemini-3-8-live-with-live-avatar-is-now-generally-available>）。

## 前のモデルとの違い

### 同じ会社の1つ前は「Gemini 3.8 Live」（音声のみ）

前のモデルは、9日前の2026年9月15日に発表された **Gemini 3.8 Live**（音声のみ）です。両方とも同じモデルカード（「Gemini 3.8 Audio」）の中で説明されており、Live Avatar は追加のオプション扱いです（出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>）。

| | Gemini 3.8 Live（音声のみ・9/15） | Gemini 3.8 Live with Live Avatar（9/24） |
|---|---|---|
| 出力の種類 | 音声とテキスト | 音声・動画・テキスト |
| 一度に書ける出力の上限 | 64,000トークン | 24,000トークン |
| 提供経路 | Gemini API・AI Studio・Gemini アプリ・Search Live など | Gemini Enterprise のみ |
| 対応言語の自動切替 | 97言語 | 97言語 |

出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>、<https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-with-live-avatar/>

<figure class="figure">
<img src="/static/images/gemini38avatar-output-budget.svg" alt="アバターを足すと一度に書ける出力トークンの上限がどれだけ減るかを示した横棒グラフ。Live（音声・テキストのみ）は64,000トークン、Live with Avatar（＋動画）は24,000トークン。62.5%の下がり幅はモデルカードの2つの数字からこの記事が計算した値で、ページに直接の記載はない。">
<figcaption>動画を足すと、書ける文字数は半分以下になります</figcaption>
</figure>

<mark class="warn">62.5%という下がり幅は、モデルカードの2つの数字（64,000と24,000）からこの記事が割り算した値です</mark>（1－24,000÷64,000）。ページにこの割合そのものは書かれていません。すでに音声のみの Live を組み込んでいるシステムに、あとから動画を足すと、返ってくる応答の長さの上限が変わることに注意が必要です。

### 動画の出力にも「連続で話せる時間」の上限がある

モデルカードの「既知の制限」には、こう明記されています（出典: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>）。

<mark class="warn">「Live Avatar は、長時間ではなく数分程度の連続対話をサポートする」と書かれています</mark>（原文: "can support a few minutes of continuous interaction, rather than extended hours"）。具体的な分数は公表されていません。**長時間の常時接続を前提にした窓口・受付用途では、この制限を先に確認する必要があります。**

### 料金：動画の出力は、音声どころかテキストより安い

料金は Google Cloud の Agent Platform 料金ページに、テキスト・音声・動画（アバター）の3種類で載っています（出典: <https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing>）。

| 種類 | 単価（100万トークンあたり） |
|---|---|
| 入力（テキスト） | $0.75 |
| 入力（動画・画像） | $1.00 |
| 入力（音声） | $3.00 |
| 出力（テキスト・思考トークン込み） | $4.50 |
| 出力（音声） | $12.00 |
| **出力（動画・アバター）** | **$1.00** |

出典: <https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing>（100万トークンあたりのドル・Non-global リージョン。この6行に期限つきの導入価格の注記は無い）

<figure class="figure">
<img src="/static/images/gemini38avatar-output-price.svg" alt="Gemini 3.8 Live APIの出力単価を3種で比べた横棒グラフ。100万トークンあたりのドル。音声は12.00ドル、テキスト（応答・思考）は4.50ドル、動画（アバター）は1.00ドルで最も安い。この「動画（アバター）」の行はGemini Enterprise向け料金表のみに載っている。">
<figcaption>動画の出力が、いちばん安い区分になっています</figcaption>
</figure>

<mark>動画（アバター）の出力単価は、音声出力の1/12、テキスト出力の1/4.5です</mark>（出典: 同上）。人物の映像を動かす機能のほうが、言葉を返すより単価が低いというのは直感に反しますが、公式の料金表にそのまま書かれている数字です。

<mark class="warn">この「出力（動画・アバター）」の行は、Gemini Enterprise 向けの料金ページにだけ載っています。</mark>開発者向けの通常の Gemini API 料金ページ（<https://ai.google.dev/gemini-api/docs/pricing>）には、この行自体が存在しません（2026年9月25日に確認）。**個人や小規模開発者が、通常の API 経由で同じ機能を使うことはできません。**

### 安全対策

発表ページには、こう書かれています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-with-live-avatar/>）。

- **既製のアバターは、申請なしで使えます。**用意されたアバターの一覧から選ぶだけです。
- <mark>独自の顔写真からアバターを作る機能は、企業のアローリスト（許可リスト）経由でしか使えません。</mark>「Custom avatar creation is currently available only through enterprise allowlisting」と明記されています。
- 出力される音声・動画の両方に **SynthID の電子透かし**が埋め込まれます。AI生成であることを検出できるようにするためと説明されています。

## 他社の最上位モデルとの比較

**Gemini と同じ「リアルタイムで話す音声AI」を、OpenAI・Anthropic の公式ページで確認しました。**

<figure class="figure">
<img src="/static/images/gemini38avatar-vendor-grid.svg" alt="リアルタイム音声モデルの有無・動画アバター出力・独自アバターの作りやすさを3社で比べた表。リアルタイム音声モデル＝Geminiは3.8 Live / 3.8 Live Extended Thinkingあり、GPTはGPT-Live 1あり（頭脳は別モデル）、Claudeは記載なし。動画のアバター出力＝Geminiはあり（Live Avatar・Gemini Enterprise限定）、GPTは記載なし（音声の入出力のみ）、Claudeは—。独自アバターを作れるか＝Geminiは企業の許可制（アローリスト経由のみ）、GPTは—、Claudeは—。「記載なし」「—」は機能が無いと明言されているのではなく、公式ページに書かれていない意味。">
<figcaption>動画のアバターを出せるのは、3社のうちGeminiだけです</figcaption>
</figure>

**OpenAI** の公式モデル一覧には、リアルタイム音声用の専用モデルとして **GPT-Live 1**（$0.05／分・秒単位で課金）と、GPT-Realtime シリーズが載っています（出典: <https://developers.openai.com/api/docs/pricing>、<https://developers.openai.com/api/docs/models>）。<mark>ただし、これらのモデルの入力・出力はテキスト・音声・画像のみで、動画の出力（アバター）は一覧のどこにも出てきません</mark>（出典: 同上・2026年9月25日に確認）。

**Anthropic** の公式モデル一覧には、こう明記されています。「All current models support text and image input, text output, multilingual capabilities, vision, and tool use」（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。<mark>音声・動画への言及は一切なく、リアルタイムで話す音声AI自体が製品として存在しません</mark>（2026年9月25日に確認）。

<mark>3社の公式ページを確認した結果、動画のアバターを出せるのは Gemini だけでした。</mark>ただし前述のとおり、Gemini 側もこの機能を使えるのは Gemini Enterprise 経由に限られます。「音声だけのリアルタイムAI」という土俵では OpenAI の GPT-Live 1 が競合しますが、GPT-Live 1 は分単位の課金（$0.05／分）で、頭脳にあたるモデルの利用料は別途かかると案内されています（出典: <https://developers.openai.com/api/docs/pricing>）。課金の単位そのものが違うため、単純に安い高いは比較できません。

## どういう人に効くか

**次に検討する価値がある人**

- 自社のカスタマーサービスや案内窓口に、顔のある対話型AIを検討している企業の担当者。既製のアバターなら申請不要で試せます。
- 複数言語で問い合わせを受ける窓口を持つ企業。97言語を会話の途中でも自動で切り替えると発表ページに明記されています。
- すでに Gemini Enterprise を契約している企業。追加の営業窓口を通さなくても、既製アバターの範囲なら使い始められます。

**急がなくていい人・見送っていい人**

- 個人でちょっと試してみたい人。<mark>Gemini アプリや無料の Google AI Studio では使えません。</mark>企業契約（Gemini Enterprise）が前提です。
- 長時間の常時接続を想定している人。モデルカードに「数分程度」と明記されており、具体的な分数も公表されていません。
- 自社ブランドの顔を使いたい人。独自アバターの作成は企業のアローリスト経由に限られ、審査を待つ必要があります。

**この記事で分からないこと**

実際に動かしたときの応答の速さ、口の動きの自然さ、日本語での品質。発表ページにはデモ動画へのリンクがありますが、この記事では動画の中身は評価していません。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 3.8 Live with Live Avatar の発表（Google・2026年9月24日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-with-live-avatar/>
   （Google DeepMind 側の <https://deepmind.google/blog/introducing-gemini-38-live-with-live-avatar/> を開くと、このページへ転送されます）
2. 一般提供（GA）の発表（Google Cloud 公式ブログ・2026年9月24日）: <https://cloud.google.com/blog/products/ai-machine-learning/gemini-3-8-live-with-live-avatar-is-now-generally-available>
3. Gemini 3.8 Audio のモデルカード（Google DeepMind 公式）: <https://deepmind.google/models/model-cards/gemini-3-8-audio/>
4. Gemini Enterprise Agent Platform の料金（Google Cloud 公式）: <https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing>
5. Gemini API の料金（Google 公式・動画アバターの行が無いことの確認用）: <https://ai.google.dev/gemini-api/docs/pricing>
6. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
7. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>
8. モデル一覧（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>

料金と提供状況は変わります。実際に導入を検討する前に、必ず上記の公式ページで現在の値を確認してください。
