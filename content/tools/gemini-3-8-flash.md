---
title: Gemini 3.8 Flashは値段そのまま——値上げは3世代まとめて来年1月
description: 2026年9月2日に発表された Gemini 3.8 Flash と 3.8 Flash Cyber について、Google の発表ページ・モデルカード・料金ページに書かれている数字だけを並べました。単価は3.6・3.7・3.8の3世代とも同じで、性能の比較表は画像でしか公開されていません。
category: tools
scene: choose
published: 2026-09-06
checked: 2026-09-06
tags: [Gemini, モデル比較, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年9月2日に **Gemini 3.8 Flash** と、サイバーセキュリティに特化した **Gemini 3.8 Flash Cyber** を発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/>）。公式ページとモデルカードに書かれている数字だけを並べます。3行にすると、こうなります。

- **単価は 3.7 Flash とまったく同じです。**入力100万トークンあたり **$0.75**、出力 **$3.75**（出典: 同上）。しかも1つ前の 3.6 Flash も同じ値段で、<mark>3世代連続で導入価格が変わっていません</mark>。
- <mark class="warn">この導入価格は2026年12月31日までで、2027年1月1日から3世代いっせいに $1.50 / $7.50 に上がります</mark>（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。
- 同時に発表された Cyber版は脆弱性の発見と自動修正に特化したモデルですが、<mark class="warn">一般には公開されず、審査を通った組織だけが使える「Fairwind Program」経由でのみ提供されます</mark>（出典: 同上）。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「速かった」「賢くなった」といった使用感は一切書いていません。

前の世代の話は [Gemini 3.7 Flash は何が変わったのか](/tools/gemini-3-7-flash/) に書いています。3週間おきに世代が変わっているので、そちらを読んだ直後の人向けの記事でもあります。

## 単価は3世代連続で同額——上がる日もそろっている

発表ページには「3.7 Flash と同じ導入価格で、入力100万トークンあたり $0.75、出力 $3.75」と書かれています（出典: 同上）。料金ページに実際に書いてある行を、そのまま表にします。

| 使い方 | 2026年12月31日まで | 2027年1月1日から |
|---|---|---|
| 入力（Standard） | $0.75 | $1.50 |
| 出力（Standard） | $3.75 | $7.50 |
| 入力（Batch） | $0.375 | $0.75 |
| 出力（Batch） | $1.875 | $3.75 |
| 入力（Priority） | $1.35 | $2.70 |
| 出力（Priority） | $6.75 | $13.50 |
| 文脈キャッシュ（入力側） | $0.075 | $0.15 |

出典: すべて <https://ai.google.dev/gemini-api/docs/pricing>（100万トークンあたりのドル・有料層）

<figure class="figure">
<img src="/static/images/gemini38-price-three-gens.svg" alt="Gemini 3.6 Flash・3.7 Flash・3.8 Flash の3世代の単価を比べた横棒グラフ。100万トークンあたりのドル、2026年12月31日までの値。3世代とも入力0.75ドル・出力3.75ドルで、バーの長さはまったく同じ。2027年1月1日から、3世代いっせいに入力1.50ドル・出力7.50ドルに上がる。3.8が安いのではなく、3世代とも同じ導入期間の値段であることを示す図。">
<figcaption>3.6・3.7・3.8で、バーの長さがまったく同じです</figcaption>
</figure>

料金ページで 3.6 Flash・3.7 Flash・3.8 Flash の3世代ぶんを見比べると、<mark>3世代ともまったく同じ数字が並んでいます</mark>（出典: 同上）。つまり<mark>Gemini 3.8 Flash が特別に安いわけではなく、「新しい Flash はいまの導入期間中は前の世代と同じ値段で出す」という運用がそのまま3回続いている</mark>ということです。

これは実務上、2つの意味を持ちます。1つめ、いま 3.6 や 3.7 を使っている人が 3.8 に乗り換えても、単価は上がりません。2つめ、「型落ちになる前に急いで乗り換えなきゃ」と焦る必要はありません。値上げのタイミングは世代の新しさとは無関係に、2027年1月1日に3世代いっせいにやってきます。

## 前のモデルとの違い

### 公式が挙げている性能

モデルカードには 3.7 Flash・他社モデルとの比較表があります。ただし<mark class="warn">その比較表は文章ではなく1枚の画像として埋め込まれており、この記事を書いた環境からは画像を配信しているホスト（googleusercontent.com）に到達できませんでした</mark>。そのため、この記事では**本文中に文章として書かれている数字だけ**を使います。

本文に文章として書かれている数字はこれだけです。

- **HLE-Verified で 54.9%**（複数分野にまたがる多段階の推論力を測るテスト。出典: 同上）。ただし3.7 Flashの同テストの点数は本文に書かれておらず、比較はできません。
- DeepSWE v1.1・Vals Finance Agent V2・Harvey's Legal Agent Benchmarkで「3.7 Flashや他の最先端モデルを上回る」と説明されていますが、具体的な点数は本文には書かれていません（出典: 同上）。
- 導入企業Gleanの発言として「Gemini 3.7 Flashの3倍以上のタスクをこなした」という数字がGemini Flashのモデルページに載っています（出典: <https://deepmind.google/models/gemini/flash/>）。ただしこれはGleanの自己申告で、第三者が同じ条件で測ったものではありません。

### 安全性の評価は文字で書かれている

性能の比較表は画像でしたが、**安全性の評価表は文字で書かれています**。3.7 Flashとの差（ポイント）がそのまま載っています。

| 評価項目 | 3.7 Flashとの差 | 良い方向 | 判定 |
|---|---|---|---|
| Text to Text Safety | -0.4pp | 下がるほど良い | 改善 |
| Multilingual Safety | +5.4pp | 下がるほど良い | 悪化 |
| Image to Text Safety | 0.0pp | 下がるほど良い | 変化なし |
| Tone | +0.2pp | 上がるほど良い | 改善 |
| Unjustified-refusals | +1.1pp | 下がるほど良い | 悪化 |

出典: すべて <https://deepmind.google/models/model-cards/gemini-3-8-flash>（自動評価。人手のレッドチーム評価ではない）

<figure class="figure">
<img src="/static/images/gemini38-safety-delta.svg" alt="Gemini 3.8 Flash の自動安全評価が、3.7 Flash と比べて何ポイント動いたかを示す図。Text to Text Safety はマイナス0.4ポイントで改善、Multilingual Safety はプラス5.4ポイントで悪化（この項目は下がるほど良いため）、Image to Text Safety は変化なし、Tone はプラス0.2ポイントで改善（この項目は上がるほど良いため）、Unjustified-refusals はプラス1.1ポイントで悪化（この項目は下がるほど良いため）。モデルカードに記載された自動評価の値で、人手のレッドチーム評価ではない。">
<figcaption>多言語の安全性だけ、はっきり悪化しています</figcaption>
</figure>

公式は「全体としては3.7 Flashと同程度で、非英語圏の安全性はやや後退した」と自ら書いています（出典: 同上）。<mark>5項目中2項目が悪化しています</mark>。<mark class="warn">とくにMultilingual Safetyの+5.4ptは、5項目のうち最大の変化幅です</mark>。「安全性も上がった」と単純にまとめるのは正確ではありません。

### 読める量・書ける量・知識の締め切り

| | Gemini 3.8 Flash |
|---|---|
| 一度に読める量 | 100万トークン |
| 一度に書ける量 | 6.4万トークン |
| 入れられるもの | 文章・画像・音声・動画 |
| 学習データの締め切り | 2026年3月 |

出典: すべて <https://deepmind.google/models/model-cards/gemini-3-8-flash>

前の記事（3.7 Flash）と、読める量・書ける量・締め切りはすべて同じです。<mark>モデルの土台（アーキテクチャ・学習データ）自体を3.7 Flashからそのまま引き継いでいる</mark>と、モデルカードにも明記されています（出典: 同上）。

## サイバー特化版「3.8 Flash Cyber」は一般には配られない

同時に発表された Gemini 3.8 Flash Cyber は、脆弱性の発見と自動修正に特化したモデルです。公式ページに書かれている数字を、そのまま並べます。

- 独自の内部ベンチマーク（20のプログラミング言語にまたがる脆弱性発見）で、**70%を超える成功率**（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/>）。
- 外部ベンチマークCWE-Bench（Collinear運営）でのパッチ修正成功率（pass@1）は**47.2%**。比較対象の「先端の大型モデル」は**47.8%**で、公式は「同等の性能をより低いコストで」と説明しています（出典: 同上）。
- Google社内の実運用として、Chromeセキュリティチームが「主要な商用モデルより**2.6倍**多い正しいパッチを生成した」、Wizが「再現率が7.5%〜9.7%高く、コストは2.3倍〜5.2倍安い」と報告しています（出典: 同上）。
- Google Cloud脆弱性調査チームは、通常なら数か月かかる調査で、重大な脆弱性を**2時間足らず**で発見したと説明しています（出典: 同上）。

これらの数字はすべてGoogle自身が発表ページに書いた、社内利用または限定提供先の実績で、第三者が独立に検証したものではありません。

そして、<mark>このCyber版には、通常モデルにあるはずの「モデルカード」も「料金ページへの掲載」もありません</mark>。実際に確認したところ、モデルカードのURL（`/models/model-cards/gemini-3-8-flash-cyber`）は404で存在せず、料金ページ（ai.google.dev）にも "cyber" の文字列は一度も出てきませんでした。提供先は「信頼できる政府機関、重要インフラの運用者、ソフトウェア開発者」に限られ、申請フォームからの審査を通った組織だけが対象です（出典: 同上）。この記事を読んでいる大半の会社員は、このモデルを使うことができません。

## 他社の最上位モデルとの比較

Gemini 3.8 Flash は Google の「主力・省コスト」モデルで、Google自身の最上位モデルではありません。それでも、OpenAI・Anthropic・Googleの3社それぞれが最上位に置くモデルを、公式料金ページの数字だけで並べます。**賢さの比較ではありません。**

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） |
|---|---|---|---|
| GPT-6 Astra | OpenAI（最上位） | $10.00 | $50.00 |
| Claude Fable 5.1 | Anthropic（最上位） | $10 | $50 |
| Gemini 3.1 Pro Preview | Google（自社の最上位） | $2.00（20万トークン以下）/ $4.00（超過時） | $12.00（20万トークン以下）/ $18.00（超過時） |
| Gemini 3.8 Flash | Google（この記事の対象） | $0.75（年内） | $3.75（年内） |

出典: OpenAIは <https://developers.openai.com/api/docs/pricing>、Claudeは <https://docs.claude.com/en/docs/about-claude/pricing>、Geminiは <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/gemini38-vendor-top-price.svg" alt="GPT-6 Astra・Claude Fable 5.1・Gemini 3.1 Pro Preview・Gemini 3.8 Flash の単価を並べた横棒グラフ。100万トークンあたり。GPT-6 Astra は入力10ドル・出力50ドル、Claude Fable 5.1 も入力10ドル・出力50ドルで同じ。Gemini 3.1 Pro Preview（Google自身の最上位）は入力2ドル・出力12ドルで、20万トークンを超えると入力4ドル・出力18ドルに上がる。この記事の対象である Gemini 3.8 Flash は入力0.75ドル・出力3.75ドルで、他社の最上位はもちろん Google 自身の最上位よりも安い、価格帯が違うモデルであることを示す図。">
<figcaption>Gemini 3.8 Flashは、Google自身の最上位よりさらに安い層です</figcaption>
</figure>

<mark>Gemini 3.8 Flashは、他社の最上位モデルはもちろん、Google自身の最上位モデルよりも安い、そもそも違う価格帯のモデルです</mark>。入力で見ると、GPT-6 AstraやClaude Fable 5.1の約13分の1、Google自身の最上位（3.1 Pro Preview）と比べても約2.7分の1です（この倍率は、上の表の数字からこの記事が計算したものです）。

「Preview」の付いたモデルは値段が変わりえます。Gemini 3.1 Pro Preview は名前のとおり試用版なので、長く使う前提で比べるなら、正式版の値段が出てから見直したほうが安全です。

## どういう人に効くか

**いま動かしてみるといい人**

- 3.7 Flash をすでに使っている人。単価は変わらず、公式は複数のベンチマークで上回ると説明しています。乗り換えて損をする要素が見当たりません。
- 長い工程のソフト開発やドキュメント処理を自動化したい人。DeepSWE v1.1やHLE-Verifiedなど、複数段階の作業に関わるベンチマークで良い数字が挙げられています。

**急がなくていい人**

- 「性能表を見て乗り換えを判断したい」人。肝心の比較表が画像でしか出ておらず、この記事を書いた環境からは中身を確認できませんでした。判断材料が本文の数字だけに限られます。
- 多言語での利用が多い人。安全性評価で唯一はっきり悪化しているのが、この項目です。
- 自動でセキュリティ診断をさせたいと期待した人。その機能を持つCyber版は、一般には提供されていません。

**この記事で分からないこと**

実際に使ったときの体感、日本語での品質、返答が返ってくるまでの待ち時間。性能の比較表（画像）の中身。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 3.8 Flash と 3.8 Flash Cyber の発表（Google・2026年9月2日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/>
   （Google DeepMind側の <https://deepmind.google/blog/introducing-gemini-3-8-flash-and-38-flash-cyber/> を開くと、このページへ転送されます）
2. Gemini 3.8 Flashのモデルカード（Google DeepMind公式）: <https://deepmind.google/models/model-cards/gemini-3-8-flash>
3. Gemini APIの料金（Google公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. Gemini Flashのモデルページ（Google DeepMind公式）: <https://deepmind.google/models/gemini/flash/>
5. 料金（Anthropic公式ドキュメント）: <https://docs.claude.com/en/docs/about-claude/pricing>
6. モデル一覧と仕様（Anthropic公式ドキュメント）: <https://docs.claude.com/en/docs/about-claude/models/overview>
7. APIの料金（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>

Gemini 3.8 Flash Cyberのモデルカードは、この記事を書いた時点では公開されていません（URLは404）。性能の比較表は画像として埋め込まれており、配信元ホストにこの記事を書いた環境から到達できなかったため、中身は確認できていません。

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
