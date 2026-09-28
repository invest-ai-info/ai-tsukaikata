---
title: GPT-6のSolとLunaは半額——乗り換えは自動でない
description: 2026年9月22日に発表された GPT-6 Sol・Luna について、OpenAI の公式ドキュメント（開発者向けモデルページ・料金ページ・ガイド）に書かれている数字だけを並べました。前世代からの値下げ幅と、Claude Sonnet 5.5 と単価が一致する点を、各社の公式ページで確認しています。
category: tools
scene: choose
published: 2026-09-28
checked: 2026-09-28
tags: [ChatGPT, モデル比較, 料金, AI最新情報]
---

## 何が変わったか

OpenAI は 2026年9月22日に **GPT-6 Sol** と **GPT-6 Luna** を発表しました。API での呼び名はそれぞれ `gpt-6-sol`・`gpt-6-luna` です（出典: <https://developers.openai.com/api/docs/models>）。9月3日に出た最上位モデル **GPT-6 Astra** に続く、中位・下位の2モデルです。これで GPT-6 の3モデルが揃いました。

3行にすると、こうなります。

- <mark>単価は前世代（GPT-5.6 Sol・GPT-5.6 Luna）から、おおむね半額になりました</mark>。Sol は入力・出力とも正確に半額、Luna は入力が半額、出力はそれ以上（58.3%減）下がっています（出典: <https://developers.openai.com/api/docs/models/gpt-6-sol>、<https://developers.openai.com/api/docs/models/gpt-6-luna>）。
- <mark>最上位の GPT-6 Astra には無い「none」（考えずに即答する）設定に、Sol と Luna は対応しています</mark>。公式ガイドに「GPT-6 Astra does not support the none reasoning effort; GPT-6 Sol and Luna do.」と明記されています（出典: <https://developers.openai.com/api/docs/guides/latest-model>）。
- <mark class="warn">前世代の「GPT-5.6 Sol」は消えていません。名前はそのまま、防御的サイバーセキュリティ向けの「Daybreak Blue」の中身として残っています</mark>（出典: <https://developers.openai.com/api/docs/pricing>）。値下げの恩恵を受けるには、モデルIDを自分で `gpt-6-sol` / `gpt-6-luna` に書き換える必要があります。

先に断っておきます。**この記事は運営者がこれらのモデルを試した記録ではありません。**公式ドキュメントに書かれていることを読んで整理したものです。「速かった」「賢くなった」といった使用感は一切書いていません。

**もう1つ、正直に書いておきます。**OpenAI の発表ページ本体（`openai.com/index/introducing-gpt-6-sol-and-luna`）は、この記事を書いた時点で読めませんでした。手元から見に行くと `Cf-Mitigated: challenge` という応答とともに 403 が返ります。先方の自動アクセス対策で、迂回はしていません。そこでこの記事は、[GPT-6 Astra の記事](/tools/gpt-6-astra/)のときと同じく、**読める公式ソースだけ**で書いています。OpenAI の開発者向けドキュメント（`developers.openai.com`）と、OpenAI 公式の RSS 配信（`openai.com/news/rss.xml`）です。RSS には発表の公式要旨が入っています（出典: <https://openai.com/news/rss.xml>。項目タイトル「Introducing GPT-6 Sol and Luna」・要旨「Meet GPT-6 Sol and Luna, two models that bring frontier intelligence to everyday work with different balances of capability and cost.」・掲載日 2026年9月22日18:00 GMT）。

## 前のモデルとの違い

### 単価はどちらも半額、下がり幅はSolとLunaで違う

前世代と新モデルの単価を、公式のモデルページからそのまま並べます。

| モデル（100万トークンあたり） | 入力 | 読み直し（キャッシュ読み取り） | 出力 |
|---|---|---|---|
| GPT-5.6 Sol（前世代） | $4.00 | $0.40 | $20.00 |
| **GPT-6 Sol（新）** | **$2.00** | **$0.20** | **$10.00** |
| GPT-5.6 Luna（前世代） | $0.20 | $0.02 | $1.20 |
| **GPT-6 Luna（新）** | **$0.10** | **$0.01** | **$0.50** |

出典: <https://developers.openai.com/api/docs/models/gpt-5.6-sol>、<https://developers.openai.com/api/docs/models/gpt-5.6-luna>、<https://developers.openai.com/api/docs/models/gpt-6-sol>、<https://developers.openai.com/api/docs/models/gpt-6-luna>

<figure class="figure">
<img src="/static/images/gpt6solluna-price-vs-prev.svg" alt="GPT-5.6 Sol/Luna から GPT-6 Sol/Luna への単価の変化を示す横棒グラフ。100万トークンあたりのドル。薄い灰＝前世代（GPT-5.6）、濃い青＝新モデル（GPT-6）。Sol の入力は4.00ドルから2.00ドルへ50%減、Sol の出力は20.00ドルから10.00ドルへ50%減。Luna の入力は0.20ドルから0.10ドルへ50%減、Luna の出力は1.20ドルから0.50ドルへ58%減。Sol は入力・出力とも正確に半額だが、Luna の出力は半額を超えて下がっている。">
<figcaption>Sol はきっちり半額、Luna の出力はそれ以上下がっています</figcaption>
</figure>

Sol は入力・出力・読み直しの3項目とも、正確に半額です。

- 入力: $4.00 → $2.00
- 出力: $20.00 → $10.00
- 読み直し: $0.40 → $0.20

Luna は入力・読み直しが半額である一方、出力はそれ以上（58.3%減）下がっています。

- 入力: $0.20 → $0.10（半額）
- 読み直し: $0.02 → $0.01（半額）
- 出力: $1.20 → $0.50（58.3%減）

半額よりさらに安くなっているのは、Luna の出力だけです。

学習データの締め切りも新しくなりました。GPT-5.6 Sol・GPT-5.6 Luna はどちらも2026年2月16日でしたが、GPT-6 Sol は2026年4月20日、GPT-6 Luna は2026年5月18日です（出典: 同上）。読める量（105万トークン）・書ける量（12.8万トークン）は4モデルとも変わっていません。

### GPT-6家族の中の位置づけと「none」設定

GPT-6 Astra・Sol・Luna の3モデルを、単価と「none」設定への対応可否で並べます。

| | GPT-6 Astra | GPT-6 Sol | GPT-6 Luna |
|---|---|---|---|
| 位置づけ | 最上位 | 中位 | 下位 |
| 入力 | $10.00 | $2.00 | $0.10 |
| 出力 | $50.00 | $10.00 | $0.50 |
| reasoning.effort の `none` | **非対応** | 対応 | 対応 |

出典: <https://developers.openai.com/api/docs/models>、<https://developers.openai.com/api/docs/guides/latest-model>

<figure class="figure">
<img src="/static/images/gpt6solluna-family.svg" alt="GPT-6の3モデル（Astra・Sol・Luna）の単価と「none」設定への対応可否を示した横棒グラフ。100万トークンあたりのドル。GPT-6 Astra（最上位）は入力10ドル・出力50ドルで、none非対応。GPT-6 Sol（中位）は入力2ドル・出力10ドルで、none対応。GPT-6 Luna（下位）は入力0.1ドル・出力0.5ドルで、none対応。「none」は考えずに即答する設定で、公式ガイドはAstraが非対応・SolとLunaは対応と明記している。">
<figcaption>「none」に対応しているのは、Astra以外の2モデルです</figcaption>
</figure>

<mark class="warn">GPT-6 Astra は「none」（考えずに即答する設定）に対応していません</mark>。公式ガイドは「GPT-6 Astra does not support the none reasoning effort; GPT-6 Sol and Luna do.」と明記しています（出典: <https://developers.openai.com/api/docs/guides/latest-model>）。短い返事を大量に安く回す用途では、Astra ではなく Sol か Luna を選ぶ必要があります。

Using GPT-6 ガイドは、選び方をこう説明しています。「Use gpt-6-astra for our highest level of capability, gpt-6-sol for strong reasoning on demanding tasks, or gpt-6-luna for efficient, repeatable work at scale.」（出典: 同上）。「複雑な推論には Astra、負荷の高い作業には Sol、大量の反復作業には Luna」という位置づけです。

### 旧「GPT-5.6 Sol」は名前ごと別の役目に回った

ここが読み違えやすい点です。<mark class="warn">GPT-5.6 Sol は廃止されていません。モデルカードのページ（`developers.openai.com/api/docs/models/gpt-5.6-sol`）は今も生きていて、$4.00 / $20.00 のままです</mark>（2026年9月28日確認）。

料金ページを見ると、その理由が分かります。GPT-5.6 Sol は現在、**防御的サイバーセキュリティ向けの「Daybreak Blue」のエイリアス（別名）が指す先**になっています。料金ページには「`gpt-daybreak-blue-latest` and `gpt-daybreak-red-latest` are aliases that currently point to `gpt-5.6-sol` and `gpt-5.6-cyber`, respectively.」と明記されています（出典: <https://developers.openai.com/api/docs/pricing>）。モデル一覧の説明も同じです。「Daybreak Blue: An alias for flagship general-purpose models with safeguards for defensive cybersecurity work.」（出典: <https://developers.openai.com/api/docs/models>）。

つまり、<mark>「GPT-5.6 Sol」という名前とモデルIDは残っているものの、一般的な用途の主力という役目は GPT-6 Sol に引き継がれました</mark>。<mark>GPT-5.6 Sol 自体は、防御的サイバーセキュリティの枠に回っています</mark>。**既存のコードで `gpt-5.6-sol` を指定したままだと、今回の値下げの恩恵は受けられません。**新しい単価を使うには、モデルIDを `gpt-6-sol` に書き換える必要があります。

## 他社の最上位モデルとの比較

各社が自社の料金ページに載せている数字だけを並べます。**賢さの比較ではありません。**性能テストは各社が自社で測っていて、測り方も対象も違うので並べても比べられません。

| モデル | 提供元 | 位置づけ | 入力（100万トークン） | 出力（100万トークン） |
|---|---|---|---|---|
| GPT-6 Astra | OpenAI | 最上位 | $10.00 | $50.00 |
| Claude Fable 5.1 | Anthropic | 最上位 | $10 | $50 |
| Gemini 3.1 Pro Preview | Google | 最上位（Preview） | $2.00（20万トークン以下）/ $4.00（超過時） | $12.00（20万トークン以下）/ $18.00（超過時） |
| **GPT-6 Sol** | OpenAI | 中位（この記事） | **$2.00** | **$10.00** |
| **Claude Sonnet 5.5** | Anthropic | 中位 | **$2** | **$10** |

出典: OpenAI は <https://developers.openai.com/api/docs/pricing>、Claude は <https://platform.claude.com/docs/en/about-claude/pricing>、Gemini は <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/gpt6solluna-vendor-match.svg" alt="5つのモデルの単価を並べた横棒グラフ。100万トークンあたり、2026年9月28日時点。GPT-6 Astra（OpenAI・最上位）は入力10ドル・出力50ドル。Claude Fable 5.1（Anthropic・最上位）も入力10ドル・出力50ドルで同じ。Gemini 3.1 Pro Preview（Google・最上位）は入力2ドル・出力12ドル。GPT-6 Sol（OpenAI）は入力2ドル・出力10ドル。Claude Sonnet 5.5（Anthropic）も入力2ドル・出力10ドルで、GPT-6 Solと完全に一致する。各社の公式料金ページに載っている値だけを並べたもので、賢さの比較ではない。">
<figcaption>下2行の単価が、そろって一致しています</figcaption>
</figure>

<mark>GPT-6 Sol と Claude Sonnet 5.5 は、入力 $2・出力 $10 で完全に一致しています</mark>（出典: 同上）。他の項目も並べます（出典: <https://platform.claude.com/docs/en/about-claude/pricing>）。

- 読み直し（キャッシュ読み取り）: GPT-6 Sol $0.20 ／ Claude Sonnet 5.5 $0.20（一致）
- キャッシュ書き込み: GPT-6 Sol $2.50 ／ Claude Sonnet 5.5「5分保持」$2.50（一致）

<mark class="warn">ただし Anthropic には「1時間保持」という選択肢もあり、そちらは $4.00 に上がります</mark>。OpenAI 側には、この1時間保持に相当する行がありません。単純にキャッシュ料金の仕組みそのものが同じというわけではなく、一致しているのは数字のほうです。

最上位どうしを比べると、GPT-6 Astra と Claude Fable 5.1 も入力 $10・出力 $50 で一致しています。Gemini 3.1 Pro Preview は入力が GPT-6 Sol / Claude Sonnet 5.5 と同じ $2.00 ですが、出力は $12.00 で、GPT-6 Sol より 2 ドル高くなっています。

## どういう人に効くか

**すぐに書き換える価値がある人**

- すでに `gpt-5.6-sol` や `gpt-5.6-luna` を使っている人。<mark>モデルIDを `gpt-6-sol` / `gpt-6-luna` に変えるだけで、単価がおおむね半額になります</mark>。挙動が変わるリスクはありますが、まず料金だけなら書き換える価値があります。
- 短い返事を大量に安く回している人。GPT-6 Astra にはない「none」設定が、Sol・Luna では使えます。
- 2026年4月・5月までの出来事を扱わせたい人。学習データの締め切りが前世代より新しくなっています。

**急がなくていい人・確認してから動く人**

- 防御的サイバーセキュリティ用途で `gpt-daybreak-blue-latest`（実体は `gpt-5.6-sol`）を使っている人。この記事の値下げは対象外です。
- 「Sol」「Luna」という名前だけで判断している人。同じ「Sol」でも、`gpt-5.6-sol` と `gpt-6-sol` はまったく別の単価・別の役割です。必ずモデルIDで確認してください。
- Claude Sonnet 5.5 とすでに比較検討している人。単価は完全に一致しているので、選ぶ基準は単価以外（キャッシュの保持期間、対応ツール、読める量など）になります。

**この記事で分からないこと**

日本語での品質、返答までの待ち時間、実際に使ったときの体感。公式ページに数字がなく、運営者も試していないので書けません。ChatGPT（アプリのほう）でいつ誰が使えるようになるかも、この記事では扱っていません。

GPT-6 Astra についての詳しい話は [GPT-6 Astra は勝手に進めない](/tools/gpt-6-astra/) に書いています。Astra に公式が配っている指示文は、Sol・Luna にもそのまま使えるとは限りません。公式ガイド自身が「They address behavior observed with GPT-6 Astra; evaluate them with your chosen model and workload.」（Astra で観測した挙動をもとにした指示文なので、使うモデルと作業で確かめてほしい）と断っています（出典: <https://developers.openai.com/api/docs/guides/latest-model>）。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>
2. GPT-6 Sol のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-6-sol>
3. GPT-6 Luna のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-6-luna>
4. GPT-5.6 Sol のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-5.6-sol>
5. GPT-5.6 Luna のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-5.6-luna>
6. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
7. Using GPT-6（OpenAI 公式ガイド）: <https://developers.openai.com/api/docs/guides/latest-model>
8. OpenAI 公式ニュースの配信（発表の要旨はここから）: <https://openai.com/news/rss.xml>

他社との比較に使った、他社の公式ページです。

9. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
10. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>

**読めなかったページ**（この記事では出典に使っていません）: `openai.com/index/introducing-gpt-6-sol-and-luna`。自動アクセス対策により 403 が返ります。中身を推測して書くことはしていません。

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
