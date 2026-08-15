---
title: Gemini 3.6 Flash と 3.5 Flash-Lite は何が変わったのか（安いモデル同士で比べる）
description: 2026年7月21日に発表された Gemini 3.6 Flash・3.5 Flash-Lite・3.5 Flash Cyber について、Google・Anthropic・OpenAI の公式発表と公式料金ページに書かれている数字だけを並べました。旗艦モデルではなく、ふだん使いの安いモデル同士の比較です。
category: tools
scene: choose
published: 2026-08-05
checked: 2026-08-05
tags: [Gemini, モデル比較, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年7月21日に **Gemini 3.6 Flash**・**Gemini 3.5 Flash-Lite**・**Gemini 3.5 Flash Cyber** の3つを同時に発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- Gemini 3.6 Flash の単価は入力100万トークンあたり **$1.50**、出力 **$7.50**。<mark>入力は前の 3.5 Flash と同じで、出力だけ $9.00 から下がりました</mark>（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。
- 公式は 3.6 Flash について、Artificial Analysis Index で <mark>3.5 Flash より出力トークンの使用量が17%少ない</mark>、DeepSWE では最大65%少ないと説明しています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>）。
- いっぽう Gemini 3.5 Flash-Lite は入力 **$0.30** / 出力 **$2.50** で、<mark>前の 3.1 Flash-Lite（入力$0.25 / 出力$1.50）より高くなっています</mark>（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。

先に断っておきます。**この記事は運営者がこれらのモデルを試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「速かった」「賢くなった」といった使用感は一切書いていません。

もう1つ。この記事はいわゆる最上位モデル（Gemini 3.1 Pro や Claude Opus 5）の話ではありません。**毎日の定型作業に使う、安いほうのモデル**を並べています。要約・分類・書類の読み取りといった作業なら、こちらのほうが実際に使う相手です。

## 3つは用途が別々です

値段を並べる前に、何のためのモデルなのかを分けます。同じ日に出たので3つとも同じ棚に見えますが、公式の説明を読むと役割が違います。

| モデル | 公式の位置づけ | 提供状況 |
|---|---|---|
| Gemini 3.6 Flash | 主力（ワークホース）。コーディング・知識作業・複数種類のデータの扱いを強化し、エージェントの土台にする | Gemini API、Google AI Studio、Google Antigravity、Gemini Enterprise、Gemini アプリなどで提供中 |
| Gemini 3.5 Flash-Lite | 待ち時間が短く、大量に流す用途向け。検索や書類処理などの作業に合わせた | Gemini API、Google AI Studio、Gemini Enterprise Agent Platform、Gemini アプリ、Google 検索へ展開中 |
| Gemini 3.5 Flash Cyber | セキュリティの弱点の検出と修正に特化。CodeMender という仕組みと組で提供 | 政府機関と一部の相手への限定パイロットとして近日提供予定 |

出典: すべて <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>

<figure class="figure">
<img src="/static/images/gemini36-lineup.svg" alt="2026年7月21日に同時発表された3つのモデルの用途を並べた図。Gemini 3.6 Flash は主力で、コーディングと知識作業、エージェントの土台、3.5 Flash の置き換え。入力100万トークンあたり1.50ドル、出力7.50ドル。一般提供中。Gemini 3.5 Flash-Lite は速さと量が持ち味で、低遅延・大量処理向け、検索や書類の処理、3.1 Flash-Lite の後継。入力0.30ドル、出力2.50ドル。一般提供中。Gemini 3.5 Flash Cyber は安全の点検用で、脆弱性の検出と修正、CodeMender と組で提供、政府と一部の相手のみ。料金の記載はなく、限定パイロットで近日提供。">
<figcaption>同じ日に出た3つですが、選ぶ場面は重なりません</figcaption>
</figure>

**Cyber は申し込めば使えるものではありません**。公式は「政府機関と信頼できるパートナーへの限定アクセスのパイロットプログラム」と書いており、料金ページにも行がありません（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。この記事でこれ以上書けることはありません。

## 前のモデルとの違い

### 料金

| | 前の世代 | 新しい世代 |
|---|---|---|
| Flash の入力（100万トークン） | 3.5 Flash: $1.50 | 3.6 Flash: $1.50 |
| Flash の出力（100万トークン） | 3.5 Flash: $9.00 | 3.6 Flash: **$7.50** |
| Flash のまとめ処理（Batch）入力 / 出力 | 3.5 Flash: $0.75 / $4.50 | 3.6 Flash: $0.75 / **$3.75** |
| Flash-Lite の入力（100万トークン） | 3.1 Flash-Lite: $0.25（音声は $0.50） | 3.5 Flash-Lite: **$0.30**（音声も同じ） |
| Flash-Lite の出力（100万トークン） | 3.1 Flash-Lite: $1.50 | 3.5 Flash-Lite: **$2.50** |
| Flash-Lite のまとめ処理（Batch）入力 / 出力 | 3.1 Flash-Lite: $0.125（音声 $0.25）/ $0.75 | 3.5 Flash-Lite: **$0.15 / $1.25** |

出典: すべて <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/gemini36-generation.svg" alt="世代交代で単価がどう動いたかを比べた横棒グラフ。100万トークンあたりのドル。Flash の入力は 3.5 Flash の1.50ドルから 3.6 Flash も1.50ドルで据え置き。Flash の出力は9.00ドルから7.50ドルへ下がった。Flash-Lite の入力（テキスト）は 3.1 Flash-Lite の0.25ドルから 3.5 Flash-Lite の0.30ドルへ上がり、出力は1.50ドルから2.50ドルへ上がった。世代が新しいほど安いとは限らない。">
<figcaption>下がったのは Flash の出力だけです</figcaption>
</figure>

**世代が新しいほど安い、ではありません。**Flash は出力が $9.00 から $7.50 へ下がりましたが、Flash-Lite は入力も出力も上がっています。出力にいたっては 1.67倍です。まとめ処理（Batch）でも同じ向きで、Flash は $4.50 → $3.75 と下がり、Flash-Lite は $0.75 → $1.25 と上がっています。

ただし Flash-Lite には逆向きの変化もあります。3.1 Flash-Lite は音声の入力だけ $0.50 と別料金でしたが、<mark>3.5 Flash-Lite はテキストも画像も動画も音声も一律 $0.30 です</mark>（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。音声を大量に読ませる使い方なら、こちらは安くなります。

もう1つ、公式が繰り返し書いているのは「1トークンの値段」ではなく「使うトークンの数」のほうです。3.6 Flash は同じ仕事を少ない出力で終える、という説明です。単価が同じでも、出力が17%少なければ支払いは17%減ります。ただし17%というのは Artificial Analysis Index という外部の指標での平均値で、あなたの作業でそうなるとは書かれていません（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>）。

### 公式が挙げている点数

まず 3.6 Flash（相手は 3.5 Flash）です。

| 何のテストか | 3.5 Flash | 3.6 Flash |
|---|---|---|
| DeepSWE | 37% | 49% |
| MLE Bench | 49.7% | 63.9% |
| OSWorld-Verified | 78.4% | 83.0% |
| GDPval-AA v2 | 1349 | 1421 |

出典: すべて <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>

<figure class="figure">
<img src="/static/images/gemini36-bench.svg" alt="Gemini 3.5 Flash と 3.6 Flash の点数を比べた横棒グラフ。DeepSWE は37％から49％、MLE Bench は49.7％から63.9％、OSWorld-Verified は78.4％から83.0％。いずれも Google が自社で測った値で、テストの中身も測り方も3つで別々のため平均は取れない。何回試した値なのかは発表ページに書かれていない。">
<figcaption>％で出ている3つだけ並べました。GDPval-AA v2 は目盛りが違うので入れていません</figcaption>
</figure>

次に 3.5 Flash-Lite です。相手が2種類あるので分けます。

| 何のテストか | 相手 | 相手の点 | 3.5 Flash-Lite |
|---|---|---|---|
| Terminal-Bench 2.1 | 3.1 Flash-Lite | 31% | 54% |
| GDM-MRCR v2 | 3.1 Flash-Lite | 60.1% | 72.2% |
| GDPval-AA v2 | 3.1 Flash-Lite | 642 | 1140 |
| SWE-Bench Pro | Gemini 3 Flash | 49.6% | 54.2% |
| OSWorld-Verified | Gemini 3 Flash | 65.1% | 74.0% |

出典: すべて <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>

公式は速さについても「毎秒350の出力トークン」と書いています（出典: 同上）。<mark class="warn">ただし、どんな長さの入力で・どの地域から・何回測った値なのかは書かれていません</mark>。速さは測り方で大きく変わるので、この数字をそのまま自分の環境に当てはめることはできません。

<mark class="warn">ここに並んだ点数はすべて Google 自身が公表したものです</mark>。他社が同じテストを同じ条件で測った値ではありません。表を横に読んで「だから他社より上」と言うことはできません。

## 他社の安いモデルとの比較

各社の公式ドキュメントから直接取った数字だけを並べます。相手は Anthropic の Claude Haiku 4.5 と、OpenAI の中で費用を抑える向けとされている GPT-5.6 Luna です。

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | 一度に読める量 | 一度に書ける量 | 学習データの締め切り |
|---|---|---|---|---|---|---|
| Gemini 3.6 Flash | Google | $1.50 | $7.50 | 100万トークン | 6.4万トークン | 公表されていない |
| Gemini 3.5 Flash-Lite | Google | $0.30 | $2.50 | 100万トークン | 6.4万トークン | 公表されていない |
| Claude Haiku 4.5 | Anthropic | $1.00 | $5.00 | 20万トークン | 6.4万トークン | 2025年7月 |
| GPT-5.6 Luna | OpenAI | $0.20（短）/ $0.40（長） | $1.20（短）/ $1.80（長） | 105万トークン | 12.8万トークン | 2026年2月16日 |

出典: Gemini の料金は <https://ai.google.dev/gemini-api/docs/pricing>、Gemini の読める量と書ける量は <https://deepmind.google/models/gemini/flash/> と <https://deepmind.google/models/gemini/flash-lite/>、Claude は <https://platform.claude.com/docs/en/about-claude/pricing> と <https://platform.claude.com/docs/en/about-claude/models/overview>、GPT は <https://developers.openai.com/api/docs/pricing> と <https://developers.openai.com/api/docs/models>

<figure class="figure">
<img src="/static/images/gemini36-cheap-price.svg" alt="安いモデル4つの単価を比べた横棒グラフ。100万トークンあたりのドル。Gemini 3.6 Flash は入力1.50ドル・出力7.50ドル、Gemini 3.5 Flash-Lite は入力0.30ドル・出力2.50ドル、Claude Haiku 4.5 は入力1.00ドル・出力5.00ドル、GPT-5.6 Luna は短い入力のとき入力0.20ドル・出力1.20ドル。ただし会社ごとにトークンの数え方も読める量も違うため、単価の安さは支払額の安さを意味しません。">
<figcaption>単価だけを並べたところ。ここから先が本題です</figcaption>
</figure>

**この表は、そのまま「どれが安いか」の表としては読めません。**理由を4つ書きます。

**1つめ。トークンの数え方が会社ごとに違います。**Anthropic の料金ページには、Claude 4.7 以降のモデルは新しい数え方を使っていて、**同じ文章でおよそ30%多いトークンになる**と書かれています（出典: <https://platform.claude.com/docs/en/about-claude/pricing>）。この表に入れた Claude Haiku 4.5 は前の数え方のほうです。同じ会社の中でも世代でずれるということは、他社との間ではもっとずれます。<mark class="warn">単価表の並び順と、月末の請求額の並び順は一致しません</mark>。

**2つめ。読める量が5倍違います。**<mark>Claude Haiku 4.5 だけ一度に読めるのが20万トークンで、他の3つは100万トークン以上です</mark>（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>、<https://deepmind.google/models/gemini/flash/>、<https://developers.openai.com/api/docs/models>）。長い資料を丸ごと渡す使い方だと、単価の前に「そもそも入るか」で選択肢が消えます。

**3つめ。GPT-5.6 Luna の「長い入力」の境目が公表されていません。**Luna には短い入力と長い入力で2段の値段がありますが、<mark class="warn">何トークンから「長い」になるのかが料金ページに書かれていません</mark>（出典: <https://developers.openai.com/api/docs/pricing>）。書いていない以上、この記事にも書けません。$0.20 で計算していたら $0.40 だった、が起こり得ます。

**4つめ。Gemini は学習データの締め切りを公表していません。**Claude Haiku 4.5 は2025年7月、GPT-5.6 Luna は2026年2月16日と明記されていますが、<mark>Gemini の2つは料金ページにもモデルページにも締め切りの記載がありません</mark>。「いつまでの出来事を知っているか」で選びたい場合、Gemini は比較の土俵に載りません。

まとめ処理（Batch）を使う場合の単価も、公式ページに載っている範囲で並べておきます。

| モデル | Batch 入力 | Batch 出力 |
|---|---|---|
| Gemini 3.6 Flash | $0.75 | $3.75 |
| Gemini 3.5 Flash-Lite | $0.15 | $1.25 |
| Claude Haiku 4.5 | $0.50 | $2.50 |
| GPT-5.6 Luna | $0.10（短） | $0.60（短） |

出典: <https://ai.google.dev/gemini-api/docs/pricing>、<https://platform.claude.com/docs/en/about-claude/pricing>、<https://developers.openai.com/api/docs/pricing>

急がない仕事なら、どの会社もおおむね半額になります。夜のうちに流して朝に受け取る使い方が向いています。

## どういう人に効くか

**乗り換えを検討していい人**

- Gemini 3.5 Flash をそのまま使っている人。入力の単価は同じで、出力の単価は下がり、公式は出力の量も減ると説明しています。値段が上がる要素が見当たりません。
- 大量の音声をテキストにして処理している人。3.1 Flash-Lite で $0.50 だった音声入力が、3.5 Flash-Lite では $0.30 になっています。
- 長い資料を1回で読ませたい人。Gemini の2つと GPT-5.6 Luna は100万トークン以上入ります。

**急がなくていい人**

- Gemini 3.1 Flash-Lite を大量に流していて、費用がぎりぎりの人。<mark>3.5 Flash-Lite は入力で1.2倍、出力で1.67倍になります</mark>。点数は上がっていますが、支払いも増えます。
- 「いつまでの知識を持っているか」で選びたい人。Gemini 側にその記載がないので、比べようがありません。
- セキュリティ点検に Cyber を使いたい人。一般には提供されていません。

**この記事で分からないこと**

実際に使ったときの体感、日本語での品質、返答が返ってくるまでの待ち時間。毎秒350トークンという数字は公表されていますが、測った条件が書かれていないため、自分の環境での速さの目安にはできません。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. 3モデルの発表（Google・2026年7月21日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/>
   （Google DeepMind 側の <https://deepmind.google/blog/introducing-gemini-3-6-flash-3-5-flash-lite-and-3-5-flash-cyber/> を開くと、このページへ転送されます）
2. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
3. Gemini Flash のモデルページ（Google DeepMind 公式）: <https://deepmind.google/models/gemini/flash/>
4. Gemini Flash-Lite のモデルページ（Google DeepMind 公式）: <https://deepmind.google/models/gemini/flash-lite/>
5. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
6. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>
7. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
8. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
