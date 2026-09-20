---
title: ChatGPT画像生成が刷新——新モデルは半額のBatchが使えない
description: 2026年9月8日に発表されたChatGPT Images 2.5（gpt-image-2.5 Sunburst / Flare）について、OpenAIの公式ドキュメントに書かれている数字だけを並べました。発表ページはbot判定で読めなかったため、RSSの要旨とAPI側の一次情報だけで書いています。
category: tools
scene: choose
published: 2026-09-20
checked: 2026-09-20
tags: [ChatGPT, OpenAI, 画像生成, 料金, AI最新情報]
---

## 何が変わったか

OpenAIは2026年9月8日、ChatGPTの画像生成を刷新したと発表しました（出典: <https://openai.com/news/rss.xml>）。3行にすると、こうなります。

- **新しいAPIモデルは「gpt-image-2.5 Sunburst」（編集精度重視）と「gpt-image-2.5 Flare」（速さ重視）の2本立て**です（出典: <https://developers.openai.com/api/docs/guides/image-generation>）。
- 画像出力トークンの単価は100万トークンあたり **$30**。以前ChatGPTで使われていたモデル（`chatgpt-image-latest`）の **$32** より下がりました（出典: <https://developers.openai.com/api/docs/pricing>）。
- <mark class="warn">ただし新モデルは、まとめて安く処理する「Batch」に対応していません</mark>。旧モデルは対応していて半額になります（出典: <https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst>）。

先に断っておきます。**この記事は運営者がこの機能を実際に試した記録ではありません。**公式ドキュメントに書かれていることを読んで整理したものです。「きれいになった」「思い通りに描けた」といった使用感は一切書いていません。

🚨 **この発表のページ（`openai.com/index/introducing-chatgpt-images-2-5`）は、この記事を書いた環境からCloudflareのbot判定で読めませんでした**（実際に叩くと `cf-mitigated: challenge` というヘッダ付きの403が返ってきます。同じ `openai.com` のRSSは200で返るので、経路の問題ではなく先方の判定です）。そのため、この記事は次の2つだけで書いています。

1. OpenAIの公式ニュースRSS（<https://openai.com/news/rss.xml>）に載っている要旨1文
2. `developers.openai.com` のモデルページ・料金ページ・開発者ガイド（いずれも200で読めました）

RSSの要旨は次の1文だけです。「ChatGPT Images 2.5 helps turn your ideas, sketches, and reference photos into more personalized, polished images that better reflect your ideas.」（出典: 同上）。スケッチや参考写真から、より作りたいものに近い画像を作れるようになった、という趣旨です。<mark class="warn">対応言語・生成にかかる時間・ChatGPT内での見え方（無料プランで使えるか等）は、この1文からは分かりません。</mark>API側の数字だけで、以下を書いています。

## 前のモデルとの違い

### 画像出力トークンの単価は下がった

OpenAIの画像生成モデルの単価を、発表順に並べます。すべて100万トークンあたり・Standardティアの値です。

| モデル | テキスト入力 | テキスト出力 | 画像入力 | 画像出力 |
|---|---|---|---|---|
| gpt-image-1 | $5.00 | — | $10.00 | $40.00 |
| gpt-image-1.5（旧世代） | $5.00 | $10.00 | $8.00 | $32.00 |
| chatgpt-image-latest（旧ChatGPTモデル） | $5.00 | $10.00 | $8.00 | $32.00 |
| gpt-image-2 | $5.00 | — | $8.00 | $30.00 |
| gpt-image-2.5 Sunburst（新） | $5.00 | — | $8.00 | $30.00 |
| gpt-image-2.5 Flare（新） | $5.00 | — | $8.00 | $30.00 |

出典: すべて <https://developers.openai.com/api/docs/pricing>（「Image generation models」の表・Standard）

<figure class="figure">
<img src="/static/images/chatgpt-images25-price-lineage.svg" alt="OpenAIの画像生成モデルの、画像出力トークン単価（100万トークンあたり）を世代順に並べた横棒グラフ。gpt-image-1は40ドル、gpt-image-1.5は32ドル、旧ChatGPTモデル（chatgpt-image-latest）も32ドル、gpt-image-2は30ドル、新しいgpt-image-2.5 Sunburstとgpt-image-2.5 Flareもどちらも30ドル。旧ChatGPTモデルは公式ドキュメントで「以前ChatGPTで使われていたスナップショット」と説明されており、同じページでAPI利用にはSunburstを推奨すると書かれている。">
<figcaption>画像出力トークンの単価は、世代を経て下がってきた</figcaption>
</figure>

<mark>新しい2モデルの単価は、直前の `gpt-image-2` とまったく同額です</mark>（出典: 同上）。安くなったのは、ChatGPTがそれまで使っていた `chatgpt-image-latest`（$32）と比べたときで、API側の「本流」の値段はもともと据え置かれていました。

`chatgpt-image-latest` のモデルページには、こう明記されています。「This points to the Image snapshot previously used in ChatGPT. We recommend GPT-Image-2.5 Sunburst for API use.」（出典: <https://developers.openai.com/api/docs/models/chatgpt-image-latest>）。<mark>ChatGPTがそれまで使っていたモデルの「後継」として、公式にSunburstが名指しされています。</mark>

### 画質の選択肢が3段階から5段階に増えた

モデルページを比べると、選べる画質の設定が増えています。

| | 選べる画質 |
|---|---|
| gpt-image-1.5 / chatgpt-image-latest（旧世代） | low・medium・high（3段階） |
| gpt-image-2.5 Sunburst / Flare（新） | low・medium・high・xhigh・max（5段階）＋auto |

出典: 旧世代は <https://developers.openai.com/api/docs/models/gpt-image-1.5>、新モデルは <https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst> と <https://developers.openai.com/api/docs/guides/image-generation>

### ⚠️ ただし、半額になる「Batch」処理には対応していない

ここが一番見落としやすい変更です。OpenAIの料金ページには「Batch」という、まとめて処理する代わりに半額になる区分があります。旧モデルはここに載っていますが、新モデルは**そもそも表に出てきません**（出典: <https://developers.openai.com/api/docs/pricing>）。

理由はモデルページのEndpoints表にあります。`gpt-image-2.5-sunburst` と `gpt-image-2.5-flare` はどちらも「Batch: `v1/batch` — Not supported」と明記されています（出典: <https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst> と <https://developers.openai.com/api/docs/models/gpt-image-2.5-flare>）。いっぽう `chatgpt-image-latest` と `gpt-image-2` のEndpoints表では「Batch: Supported」です（出典: <https://developers.openai.com/api/docs/models/chatgpt-image-latest> と <https://developers.openai.com/api/docs/models/gpt-image-2>）。

<mark class="warn">急がない大量生成をBatchでまとめて安く処理していた人は、新モデルに乗り換えるとその手が使えなくなります</mark>。旧モデルのBatch料金は、画像出力が $16.00（chatgpt-image-latest・gpt-image-1.5）〜$15.00（gpt-image-2）で、Standardのおよそ半額でした（出典: <https://developers.openai.com/api/docs/pricing>）。

<figure class="figure">
<img src="/static/images/chatgpt-images25-old-vs-new.svg" alt="旧世代（chatgpt-image-latest・gpt-image-1.5）と新しいgpt-image-2.5系を比べた表。画質の選択肢＝旧世代はlow/medium/highの3段階、新世代はlow/medium/high/xhigh/maxの5段階に加えてauto。画像出力単価＝旧世代は100万トークンあたり32ドル、新世代は30ドル。テキスト出力＝旧世代は100万トークンあたり10ドルの課金があるが、新世代は画像しか出力しないため課金対象外。まとめ処理（Batch）＝旧世代は対応していて半額になるが、新世代（Sunburst・Flare）はどちらも非対応（赤枠で強調）。Batch非対応は両モデルの公式ページのEndpoints表で確認したもので、画質は増え値段は下がったが、半額のBatchが使えなくなったことを示す図。">
<figcaption>画質は増え値段は下がったが、半額のBatchが使えなくなった</figcaption>
</figure>

もう1つ、テキスト出力の扱いも変わっています。`chatgpt-image-latest` と `gpt-image-1.5` は、画像に添えるテキストの出力にも100万トークンあたり$10.00の課金がありますが（出典: <https://developers.openai.com/api/docs/pricing>）、<mark>新しい2モデルの入出力は「Output modalities: image」のみで、テキスト出力自体がありません</mark>（出典: <https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst>）。画像しか出さない設計になった、ということです。

## 他社の最上位モデルとの比較

画像生成をしているのはOpenAIだけではありません。Googleにも画像出力の単価を公式ページに明記した3モデルがあります（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。

| モデル（提供元） | 画像出力単価（100万トークンあたり） | 1枚あたりの目安 |
|---|---|---|
| gpt-image-2.5 Sunburst / Flare（OpenAI・この記事の対象） | $30.00 | 公式ページに1枚あたりの静的な数字は無し（計算ツールのみ） |
| Nano Banana 2 Lite（Google・`gemini-3.1-flash-lite-image`） | $30.00 | 1K解像度で$0.0336 |
| Nano Banana 2（Google・`gemini-3.1-flash-image`） | $60.00 | 1K解像度で$0.067 |
| Nano Banana Pro（Google の最上位・`gemini-3-pro-image`） | $120.00 | 1K/2K解像度で$0.134、4Kで$0.24 |

出典: OpenAIは <https://developers.openai.com/api/docs/pricing>、Googleは <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/chatgpt-images25-vendor-price.svg" alt="画像出力トークンの単価（100万トークンあたり）を4モデルで比べた横棒グラフ。OpenAIのgpt-image-2.5 Sunburst/Flareは30ドル、Googleのnano Banana 2 Liteも同じ30ドル、Nano Banana 2は60ドル、Googleの最上位Nano Banana Proは120ドルで一番高い。Nano Banana Proの120ドルは1K/2K画像あたり0.134ドル、4K画像あたり0.24ドルに相当すると公式ページが併記している。Anthropicは画像生成モデルを公式ページに載せていない。">
<figcaption>画像出力トークンの単価は、Googleの最上位が一番高い</figcaption>
</figure>

<mark>OpenAIの新モデルの単価（$30）は、Google自身の下位モデル「Nano Banana 2 Lite」と同額です</mark>。<mark>Googleの主力モデル「Nano Banana 2」は倍の$60、Google自身の最上位「Nano Banana Pro」は4倍の$120でした</mark>（出典: 同上）。これは賢さの比較ではなく、あくまで各社が公式ページに載せている単価を、同じ単位（100万画像出力トークンあたりのドル）に揃えて並べたものです。

<mark class="warn">Googleは1枚あたりの実際の値段（$0.045〜$0.151など）を公式ページに明記していますが、OpenAIの新モデルにはその静的な数字がありません</mark>。OpenAIのガイドには「トークン消費量はモデルや画質設定によって変わる」と書かれていて（出典: <https://developers.openai.com/api/docs/guides/image-generation>）、インタラクティブな計算ツールでしか見積もれません。**そのため、この記事では「1枚いくらか」の比較はしていません。**トークン単価だけが公式に比較できる数字です。

Anthropic（Claude）については、モデル一覧（<https://platform.claude.com/docs/en/about-claude/models/overview>）と料金ページ（<https://platform.claude.com/docs/en/about-claude/pricing>）のどちらにも画像生成モデルの記載がありませんでした。<mark>Anthropicは画像生成モデルを提供していないと考えられます。</mark>

## どういう人に効くか

**乗り換えて得する人**

- ChatGPTの画像生成をAPI経由で使っていて、単価だけを見ている人。$32→$30に下がっています。
- 高い画質やこまかい編集をしたい人。`xhigh`・`max`という新しい選択肢が増えました。

**先に確かめたほうがいい人**

- **大量の画像を「Batch」でまとめて安く処理していた人。**新モデルには半額のBatchが無く、Standard料金で払うことになります。
- 画像と一緒にテキストの出力も使っていた人。新モデルは画像しか出力しません。
- ChatGPT内での見え方（無料プランで使えるか、対応言語など）を知りたい人。**発表ページが読めなかったため、この記事では確認できていません。**

**この記事で分からないこと**

実際に生成した画像の質、スケッチや参考写真をどれだけ正確に反映するか、ChatGPT内での操作感。運営者も試していないので書けません。発表ページ本文（`openai.com/index/...`）が読めなかったため、RSSの要旨1文とAPI側のドキュメントだけで書いています。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. OpenAI公式ニュースRSS（発表の要旨1文のみ。本文ページはbot判定で読めず）: <https://openai.com/news/rss.xml>
2. GPT-Image-2.5 Sunburst モデルページ（OpenAI公式）: <https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst>
3. GPT-Image-2.5 Flare モデルページ（OpenAI公式）: <https://developers.openai.com/api/docs/models/gpt-image-2.5-flare>
4. GPT-Image-2 モデルページ（OpenAI公式）: <https://developers.openai.com/api/docs/models/gpt-image-2>
5. GPT-Image-1.5 モデルページ（OpenAI公式）: <https://developers.openai.com/api/docs/models/gpt-image-1.5>
6. chatgpt-image-latest モデルページ（OpenAI公式）: <https://developers.openai.com/api/docs/models/chatgpt-image-latest>
7. API の料金（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
8. 画像生成ガイド（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/guides/image-generation>
9. Gemini API の料金（Google公式）: <https://ai.google.dev/gemini-api/docs/pricing>
10. モデル一覧（Anthropic公式ドキュメント・画像生成モデルの記載なしを確認）: <https://platform.claude.com/docs/en/about-claude/models/overview>
11. 料金（Anthropic公式ドキュメント・画像生成の項目なしを確認）: <https://platform.claude.com/docs/en/about-claude/pricing>

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
