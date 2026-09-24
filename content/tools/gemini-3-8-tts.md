---
title: Gemini新TTSは出力単価が最大70%減——2027年に2倍に戻る
description: 2026年9月23日にGoogleが発表した音声合成モデル「Gemini 3.8 Flash TTS」「Gemini 3.8 Flash-Lite TTS」について、公式発表ページ・料金ページ・開発者ドキュメントに書かれている数字だけを並べました。前世代より出力単価が最大70%下がった一方、2027年1月1日に2倍へ戻ります。声の複製が使えない地域や、OpenAIの唯一のTTSモデルとの比較も含めます。
category: tools
scene: choose
published: 2026-09-24
checked: 2026-09-24
tags: [Gemini, 音声AI, 料金, AI最新情報]
---

## 結論：使い方ごとに、こうなります

Google は 2026年9月23日、新しい音声合成（TTS）モデル **Gemini 3.8 Flash TTS** と **Gemini 3.8 Flash-Lite TTS** を発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/>）。前世代の Gemini 3.1 Flash TTS Preview にも動きがあります。モデル一覧ページで「Legacy（レガシー）」表記に変わりました（出典: <https://ai.google.dev/gemini-api/docs/models>）。

| どんな使い方か | やること | どうなるか |
|---|---|---|
| **声優なしでキャラクターボイスを作りたい** | Gemini 3.8 Flash TTS を使う（AI Studio か API） | 自然文の指示で声を作れる。前世代より出力単価が**55%安い** |
| **大量のダビング・音声コンテンツを効率よく作りたい** | Gemini 3.8 Flash-Lite TTS を使う | 出力単価は前世代より**最大70%安い**、100万トークンあたり$6.00 |
| **自分の声を複製して使いたい** | 30秒の同意録音を用意して AI Studio か API で複製 | イリノイ・テキサス・EEA・UK・スイス・インドでは、AI Studio 上の複製が使えない |

一言でいうと、<mark>単価は下がり、声の複製は誰でも申請なしで使える</mark>。ただし<mark class="warn">その安い単価は2027年1月1日に2倍へ戻り、複製機能には使えない地域がある</mark>。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**公式ページと開発者ドキュメントに書かれていることを読んで、使い方ごとに整理したものです。

ここから下は、表の3行がなぜそうなるのかの説明です。

## なぜそうなるのか

### 出力単価が最大70%下がった理由

理由は「新モデルの単価そのものが安い」の1点です。前世代との差を、料金ページの生の数字で並べます。

| 100万トークンあたり（Standard・導入価格） | Gemini 3.1 Flash TTS Preview（旧） | Gemini 3.8 Flash TTS（新） | Gemini 3.8 Flash-Lite TTS（新） |
|---|---|---|---|
| 入力（テキスト） | $1.00 | $0.50 | $0.50 |
| 出力（音声） | $20.00 | $9.00 | $6.00 |

出典: <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/gemini38tts-price-old-vs-new.svg" alt="3つのGemini音声合成モデルの単価を比べた横棒グラフ。100万トークンあたりのドル。Gemini 3.1 Flash TTS Preview（旧世代・レガシー）は入力1.00ドル・出力20.00ドル、Gemini 3.8 Flash TTS（新・スタジオ品質）は入力0.50ドル・出力9.00ドル、Gemini 3.8 Flash-Lite TTS（新・高効率）は入力0.50ドル・出力6.00ドル。新2モデルの値は2026年12月31日までの導入価格。下がり幅は入力50%、出力はFlash TTSが55%・Flash-Lite TTSが70%（この記事の計算）。3.1 Flash TTS Previewは新モデルの登場と同時にモデル一覧で「Legacy」表記になった。">
<figcaption>入力は半額、出力はモデルによって55〜70%安くなりました</figcaption>
</figure>

入力はどちらの新モデルも50%安くなりました。出力は Flash TTS が55%、Flash-Lite TTS が70%安くなっています（いずれもこの記事の計算）。<mark>前世代の Gemini 3.1 Flash TTS Preview は、モデル一覧ページで乗り換えを勧める表記に変わっています</mark>。原文は「Legacy TTS preview model. We recommend updating to Gemini 3.8 Flash TTS or Gemini 3.8 Flash-Lite TTS.」です（出典: 同上）。

ただし、この安さには期限があります。料金ページには「2026年12月31日まで」と明記されており、2027年1月1日からは入力・出力とも2倍になります。

| 100万トークンあたり | 2026年12月31日まで | 2027年1月1日から |
|---|---|---|
| 入力（Flash TTS / Flash-Lite TTS 共通） | $0.50 | $1.00 |
| 出力（Flash TTS） | $9.00 | $18.00 |
| 出力（Flash-Lite TTS） | $6.00 | $12.00 |

出典: <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/gemini38tts-price-doubles.svg" alt="Gemini 3.8 Flash TTSとFlash-Lite TTSの単価が期間で変わることを示した横棒グラフ。100万トークンあたりのドル。入力（両モデル共通）は2026年12月31日まで0.50ドル、2027年1月1日から1.00ドル。出力はFlash TTSが9.00ドルから18.00ドル、Flash-Lite TTSが6.00ドルから12.00ドル。いずれも2027年1月1日に2倍になる。前世代の3.1 Flash TTS Previewには導入期間の但し書きが無く、1.00ドル／20.00ドルのまま。">
<figcaption>導入価格は2027年1月1日に2倍になります</figcaption>
</figure>

前世代の Gemini 3.1 Flash TTS Preview の料金には、こうした期間の但し書きがありません（出典: 同上）。「導入期間」という区切り自体が、新しい2モデルだけの仕組みです。2027年1月1日以降は、新モデルの単価と前世代の単価の差がさらに縮みます。年明け以降の費用で予算を組む場合は、いまの安い単価をそのまま使わないよう注意が必要です。

### 何ができるようになったか

発表ページによると、2つのモデルは役割が分かれています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/>）。

- **Gemini 3.8 Flash TTS**：ゲーム・オーディオブック・ポッドキャストなど、深い演出が要る場面向け
- **Gemini 3.8 Flash-Lite TTS**：大量のダビングや音声エージェントなど、高効率・低コストの量産向け

共通機能として、次の4つが挙げられています（出典: 同上）。

- **声を自然文で作る。**「怒った口調のドラゴン」のような指示から、既製の声とは別の新しい声を作れる
- **1行ごとに演技を指示できる。**間の取り方・訛り・相づち（「うんうん」のような相槌）まで台本で制御
- **数時間の長さでも声質が崩れにくい。**ポッドキャストやオーディオブック向けの長時間生成に対応
- **2人の会話を1つの台本から作れる。**両者の声を自然な間合いで区別して生成

声の数は2,000種類以上です。<mark>対応言語は、モデル一覧ページに Flash TTS が130言語、Flash-Lite TTS が101言語と明記されています</mark>（出典: <https://ai.google.dev/gemini-api/docs/models>）。発表ページ本文の表現は「100以上の言語と方言」で、やや幅があります。この記事では、モデルごとの言語数が書かれているモデル一覧ページの数字を使いました。

開発者ドキュメントには、宣伝文句には出てこない具体的な上限も書かれています（出典: <https://ai.google.dev/gemini-api/docs/speech-generation>）。

- <mark class="warn">1回のリクエストで複数の声を演じさせられるのは、既製の声を使う場合で最大2人まで</mark>です。自分で作った声や複製した声を使った多人数の会話は、1人ずつ別々に生成してつなぎ合わせる必要があります
- カスタム音声（自分で作った声・複製した声）の保存は、**プロジェクトあたり最大200個・保存期間1年**です。保存しない一時利用（voice key）は7日間で消えます
- 既定の出力は44バイトのヘッダーが付いた WAV 形式です

性能面では、Google は第三者機関のベンチマークを引用しています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/>）。<mark>Gemini 3.8 Flash TTS は Hume AI の Voice Design Benchmark で総合1位（71.4点）、訛りの再現でも1位（60.8点）</mark>だとGoogleは説明しています。Overall Quality Index でも Flash TTS が1位、Flash-Lite TTS が2位だと書かれています。これらはGoogleが引用した第三者の評価で、この記事では独自に検証していません。

### 声を複製できない地域がある理由

声の複製は、他人になりすました音声（ディープフェイク音声）を作れてしまう機能です。そのため発表ページには、安全対策が具体的に書かれています（出典: 同上）。

- 複製には、声の持ち主が読み上げた**同意の録音**が必要（本人の許可なく複製できない仕組み）
- 生成した音声すべてに **SynthID** という電子透かしを埋め込む（AI生成音声だと検知できるようにする）
- **C2PA** という来歴情報の規格にも対応

そのうえで、発表ページの注記には次のように書かれています（出典: 同上）。

> Voice replication through AI Studio is not available in Illinois, Texas, EEA, UK, Switzerland, and India.
>（AI Studio 経由の声の複製は、イリノイ州・テキサス州・EEA（欧州経済領域）・英国・スイス・インドでは利用できません）

この注記は「AI Studio 経由」と明記されています。API 経由での扱いが同じかどうかは、確認した範囲の発表ページには書かれていません。<mark>日本はこの制限の一覧に含まれていません</mark>が、料金・提供地域は変わるものなので、実際に使う前に公式ページで確認してください。

## 他社の最上位モデルと比べると

**同じ「文章から音声を作る」機能**を、OpenAI と Anthropic の公式ページで確認しました。

<figure class="figure">
<img src="/static/images/gemini38tts-vendor-grid.svg" alt="音声合成（TTS）モデルを3社で比べた表。専用のTTSモデル＝Geminiは2機種（Flash TTS / Flash-Lite TTS）、GPTは1機種（GPT-4o Mini TTS）、Claudeは記載なし。自分の声を複製＝Geminiは誰でも申請なしで使える（要30秒の同意録音）、GPTは限定顧客のみで要営業への問い合わせ、Claudeは—。対応言語＝Geminiは130言語（Flash-Liteは101言語）、GPTは明記なし（声は英語向けに最適化）、Claudeは—。出力の単価（100万トークンあたり）＝Geminiは6.00〜9.00ドルで2027年に2倍、GPTは12.00ドルで期限の記載なし、Claudeは—。「記載なし」「—」は機能が無いと明言されているのではなく、公式ページに書かれていない意味。">
<figcaption>声の複製が申請なしで使えるのは、3社のうちGeminiだけです</figcaption>
</figure>

OpenAI のモデル一覧には、音声合成専用のモデルが **GPT-4o Mini TTS** の1機種だけ載っています（出典: <https://developers.openai.com/api/docs/models>）。料金は入力（テキスト）$0.60、出力（音声）$12.00で、いずれも100万トークンあたりです（出典: <https://developers.openai.com/api/docs/models/gpt-4o-mini-tts>）。<mark class="warn">このモデルの最大入力トークン数は2,000トークンと明記されています</mark>（出典: 同上）。数時間の長時間生成に対応するGeminiとは、想定する使い方の規模が異なります。

| モデル | 提供元 | 入力（音声を出す文章） | 出力（音声） | 最大入力 |
|---|---|---|---|---|
| Gemini 3.8 Flash TTS | Google | $0.50（年内） | $9.00（年内） | 数時間の長文に対応 |
| Gemini 3.8 Flash-Lite TTS | Google | $0.50（年内） | $6.00（年内） | 数時間の長文に対応 |
| GPT-4o Mini TTS | OpenAI | $0.60 | $12.00 | 2,000トークン |

出典: Gemini は <https://ai.google.dev/gemini-api/docs/pricing>、OpenAI は <https://developers.openai.com/api/docs/models/gpt-4o-mini-tts>

声の複製についても、両社の扱いは対照的です。OpenAI の公式ガイドには「Custom voices are limited to eligible customers. Contact our sales team to learn more.」と書かれています（出典: <https://developers.openai.com/api/docs/guides/custom-voices>）。<mark>OpenAI の声の複製は誰でも使えるわけではなく、対象は限定顧客のみで、利用には営業への問い合わせが必要</mark>です。制約は「組織あたり最大20声」「参照音声は30秒以下」です（出典: 同上）。この30秒という長さは、Gemini の複製に必要な参照音声の長さと同じです。

OpenAI の一般向け Text to Speech API の組み込み音声の数は、ページの章によって書き方が違います（出典: <https://developers.openai.com/api/docs/guides/text-to-speech>）。

- ガイド本文：「11の組み込み音声」
- Voice options の節：「13の組み込み音声」

同じページには「Voices are currently optimized for English」ともあります。声は今のところ英語向けに最適化されている、という意味です。対応言語数そのものは、確認した範囲では明記されていません。

Anthropic の公式モデル一覧には「All current models support text and image input, text output, multilingual capabilities, vision, and tool use.」と書かれています。<mark>audio（音声）や speech（発話）という言葉は一度も出てきません</mark>（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。**「記載なし」は「対応していないと明言されている」という意味ではありません。**公式ページに書かれていないので、この記事では確認できなかったこととして扱っています。

## どういう人に効くか

**いま動かしてみるといい人**

- ゲームやオーディオブック向けに、既製の声とは違う独自キャラクターの声を作りたい人。自然文の指示で声を作れます。
- ポッドキャストやナレーションを大量に量産したい人。Flash-Lite TTS の出力単価は前世代より最大70%安くなりました。
- 自分の声（や許可を得た声）を複製して使いたい人。日本を含む多くの地域で、AI Studio か API から申請なしで使えます。

**急がなくていい人**

- 3人以上が同時に話す場面を、1回のリクエストで作りたい人。既製の声どうしの会話でも上限は2人です。
- 来年以降の費用を今の単価で見積もりたい人。**2027年1月1日に単価が2倍になります**。
- イリノイ州・テキサス州・EEA・英国・スイス・インドから声の複製（AI Studio 経由）を使いたい人。公式に利用対象外と明記されています。

**この記事で分からないこと**

- 実際に生成した音声の自然さ、日本語での聞こえ方
- API 経由でも声の複製に地域制限があるかどうか（発表ページの注記は「AI Studio 経由」とだけ書かれています）
- 声の細かな調整機能「Voice remixing」の中身（発表ページに "Coming soon" とあり、まだ提供されていません）

どれも運営者が試していないので、体感としては書けません。

同じ Gemini の音声系モデルには、ほかに関連記事があります。用途に応じて使い分けが必要です。

- [Gemini 3.8 Live](/tools/gemini-3-8-live/)（対話向け）
- [Gemini 3.5 Transcribe](/tools/gemini-3-5-transcribe/)（音声を文字にする）

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 3.8 Flash TTS / Flash-Lite TTS の発表（Google・2026年9月23日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/>
   （Google DeepMind 側の <https://deepmind.google/blog/say-hello-to-gemini-38-text-to-speech/> を開くと、このページへ転送されます）
2. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
3. Gemini のモデル一覧（Google 公式）: <https://ai.google.dev/gemini-api/docs/models>
4. Text-to-speech generation（TTS）のガイド（Google 公式ドキュメント）: <https://ai.google.dev/gemini-api/docs/speech-generation>
5. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>
6. GPT-4o Mini TTS のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-4o-mini-tts>
7. Text to speech のガイド（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/guides/text-to-speech>
8. Custom voices のガイド（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/guides/custom-voices>
9. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
