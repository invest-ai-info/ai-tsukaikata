---
title: Gemini 3.7 Flash は何が変わったのか（3週間で世代交代・半額は年内まで）
description: 2026年8月13日に発表された Gemini 3.7 Flash について、Google の発表ページ・モデルカード・料金ページに書かれている数字だけを並べました。Google が比較相手に挙げた他社モデルの単価は、各社の公式ページで突き合わせています。
category: tools
scene: choose
published: 2026-08-14
checked: 2026-08-14
tags: [Gemini, モデル比較, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年8月13日に **Gemini 3.7 Flash** を発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- **前の Gemini 3.6 Flash が出てから3週間しか経っていません**。公式も「3.6 Flash のちょうど3週間後」と書いています（出典: 同上）。
- 単価は入力100万トークンあたり **$0.75**、出力 **$3.75**。<mark class="warn">ただしこれは2026年12月31日までの導入価格で、2027年1月1日から $1.50 / $7.50 になります</mark>（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。
- 公式は、プログラムを書く作業と書類を読む作業の点数が上がったと説明しています。例＝DeepSWE v1.1 が 48.6% から 65.3% へ、GDP.pdf が 22.0% から 34.0% へ（出典: <https://deepmind.google/models/model-cards/gemini-3-7-flash>）。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「速かった」「賢くなった」といった使用感は一切書いていません。

前の世代の話は [Gemini 3.6 Flash と 3.5 Flash-Lite](/tools/gemini-3-6-flash/) に書いています。3週間しか間が空いていないので、そちらを読んだ直後の人向けの記事でもあります。

## 「半額」が何の半額なのか

発表ページには「100万トークンあたり、もとの 3.6 Flash の半分の導入価格で」と書かれています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/>）。ここは読み違えやすいので、料金ページに実際に書いてある行をそのまま表にします。

| 使い方 | 2026年12月31日まで | 2027年1月1日から |
|---|---|---|
| 入力（Standard） | $0.75 | $1.50 |
| 出力（Standard） | $3.75 | $7.50 |
| 入力（Batch・Flex） | $0.375 | $0.75 |
| 出力（Batch・Flex） | $1.875 | $3.75 |
| 入力（Priority） | $1.35 | $2.70 |
| 出力（Priority） | $6.75 | $13.50 |
| 文脈キャッシュ（入力側） | $0.075 | $0.15 |

出典: すべて <https://ai.google.dev/gemini-api/docs/pricing>（100万トークンあたりのドル・有料層）

<figure class="figure">
<img src="/static/images/gemini37-price-window.svg" alt="Gemini 3.7 Flash の単価が期間で変わることを示した横棒グラフ。100万トークンあたりのドル。Standard の入力は2026年12月31日まで0.75ドル、2027年1月1日から1.50ドル。Standard の出力は3.75ドルから7.50ドル。まとめ処理（Batch）の入力は0.375ドルから0.75ドル、出力は1.875ドルから3.75ドル。いずれも2027年1月1日に2倍になる。前の世代の Gemini 3.6 Flash も、いまは同じ0.75ドルと3.75ドルで、半額なのは3.7だからではなく導入期間だから。">
<figcaption>いま見えている値段は、年明けに2倍になります</figcaption>
</figure>

ここで料金ページをもう少し下まで読むと、大事なことが1つ分かります。<mark>同じ料金ページで、前の世代の 3.6 Flash も $0.75 / $3.75 になっています</mark>（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。3.6 Flash の行にも「2026年12月31日まで」「2027年1月1日から $1.50 / $7.50」と、まったく同じ但し書きが付いています。

つまり<mark>半額なのは 3.7 だからではなく、いまが導入期間だからです</mark>。「新しいほうに乗り換えると安くなる」ではありません。いま 3.6 Flash を使っている人の請求も、すでに同じところまで下がっています。

急がない仕事なら、<mark>まとめて流す使い方（Batch）でさらに半額になります</mark>。Google は料金ページで「Batch API（50% のコスト削減）」と説明しています（出典: 同上）。夜のうちに投げて朝に受け取る使い方なら、年内は $0.375 / $1.875 です。

## 前のモデルとの違い

### 公式が挙げている点数

モデルカードには、3.7 Flash・3.6 Flash・他社3モデルを並べた比較表があります。まず前の世代との2列だけを抜き出します。

| 何のテストか | 3.6 Flash | 3.7 Flash |
|---|---|---|
| FrontierCode 1.1 Main（実用的なコードの品質） | 34.4% | 43.6% |
| DeepSWE v1.1（長い工程のソフト開発） | 48.6% | 65.3% |
| Terminal-bench 2.1（端末での自動作業） | 78.0% | 85.8% |
| Terminal-bench 3.0（自動作業の総合力） | 5.4% | 14.9% |
| AutomationBench（社内業務の自動化） | 17.0% | 30.4% |
| GDP.pdf（難しいPDFの読み取り） | 22.0% | 34.0% |
| Harvey LAB-AA（複雑な法務の作業） | 85.1% | 90.7% |
| LVBench（長い動画の理解） | 84.2% | 85.4% |
| GDM-MRCR v2（長い文脈からの探し出し） | 91.8% | 97.0% |
| CharXiv Reasoning（図表の読み取り・道具なし） | 85.2% | 84.5% |
| CharXiv Reasoning（同・道具あり） | 89.4% | 88.7% |

出典: すべて <https://deepmind.google/models/model-cards/gemini-3-7-flash>

<figure class="figure">
<img src="/static/images/gemini37-vs-36.svg" alt="Gemini 3.6 Flash と 3.7 Flash の点数を比べた横棒グラフ。FrontierCode 1.1 は34.4％から43.6％、DeepSWE v1.1 は48.6％から65.3％、Terminal-bench 2.1 は78.0％から85.8％、AutomationBench は17.0％から30.4％、GDP.pdf は22.0％から34.0％へ上がった。いっぽう CharXiv（道具なし）だけは85.2％から84.5％へ下がっている。いずれも Google のモデルカードに載っている値で、テストの中身も測り方も別々のため平均は取れない。">
<figcaption>上がった項目だけを見ないでください。下がった項目もあります</figcaption>
</figure>

<mark>ほとんどの項目は上がっていますが、図表の読み取り（CharXiv）だけは下がっています</mark>。道具なしで 85.2% から 84.5%、道具ありで 89.4% から 88.7% です（出典: 同上）。差はわずかですが、「全部よくなった」ではないことは、公式の表にそう書いてあります。

もう1つ、確かめていて見つかったことがあります。<mark class="warn">同じ会社が同じ日に出した2ページで、3.6 Flash の DeepSWE の点数が違います</mark>。発表ページは 49.0%、モデルカードは 48.6% と書いています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/> と <https://deepmind.google/models/model-cards/gemini-3-7-flash>）。どちらが正しいのかは公表されていないので、この記事では両方書いておきます。

### 読める量・書ける量・知識の締め切り

| | Gemini 3.7 Flash |
|---|---|
| 一度に読める量 | 100万トークン |
| 一度に書ける量 | 6.4万トークン |
| 入れられるもの | 文章・画像・音声・動画 |
| 学習データの締め切り | 2026年3月 |

出典: すべて <https://deepmind.google/models/model-cards/gemini-3-7-flash>

**前の記事では「公表されていない」と書いた学習データの締め切りが、今回はモデルカードに書かれています**。ただし読み方に注意が必要です。<mark class="warn">モデルカードは「分野によっては2025年1月までの知識にとどまることがある」と但し書きしています</mark>（出典: 同上）。2026年3月というのは一番新しいところの話で、全部がそこまで新しいわけではない、という意味です。

## 他社のモデルとの比較

Google はモデルカードの比較表に、**Claude Sonnet 5**（Anthropic）・**GPT-5.6 Terra**（OpenAI）・**Muse Spark 1.2**（Meta）を並べています。ここでやったのは、**その表に書かれた他社の単価を、その会社自身の公式ページで突き合わせる**ことです。

| モデル | Google の表の値 | 提供元の公式ページ | 結果 |
|---|---|---|---|
| Claude Sonnet 5 | 入力 $2.00 / 出力 $10.00 | 入力 $2 / 出力 $10 | 一致 |
| GPT-5.6 Terra | 入力 $2.00 / 出力 $12.00 | 入力 $2 / 出力 $12（短い入力） | 一致 |
| Muse Spark 1.2 | 入力 $1.25 / 出力 $4.25 | 開けなかった | 確認できず |

出典: Google の表は <https://deepmind.google/models/model-cards/gemini-3-7-flash>、Claude は <https://platform.claude.com/docs/en/about-claude/pricing>、GPT は <https://developers.openai.com/api/docs/pricing>

<mark>Google が表に載せた他社の単価は、Anthropic と OpenAI の公式ページと一致しました</mark>。他社を不利に見せるために値をいじってはいません。いっぽう Muse Spark 1.2 の提供元の公式ページは、この記事を書いた環境からは開けませんでした。二次情報の数字を写すことはしないので、この1行だけ「確認できず」のままにしてあります。

仕様も並べておきます。

| モデル | 入力（100万トークン） | 出力（100万トークン） | 一度に読める量 | 一度に書ける量 | 学習データの締め切り |
|---|---|---|---|---|---|
| Gemini 3.7 Flash | $0.75（年内） | $3.75（年内） | 100万トークン | 6.4万トークン | 2026年3月 |
| Claude Sonnet 5 | $2 | $10 | 100万トークン | 12.8万トークン | 2026年1月 |
| GPT-5.6 Terra | $2（短）/ $4.00（長） | $12（短）/ $18.00（長） | 105万トークン | 12.8万トークン | 2026年2月16日 |
| Muse Spark 1.2 | 確認できず | 確認できず | 確認できず | 確認できず | 確認できず |

出典: Gemini は <https://deepmind.google/models/model-cards/gemini-3-7-flash> と <https://ai.google.dev/gemini-api/docs/pricing>、Claude は <https://platform.claude.com/docs/en/about-claude/models/overview> と <https://platform.claude.com/docs/en/about-claude/pricing>、GPT は <https://developers.openai.com/api/docs/models> と <https://developers.openai.com/api/docs/pricing>

<figure class="figure">
<img src="/static/images/gemini37-four-prices.svg" alt="Google が自社のモデルカードで比較相手に選んだ4モデルの単価を比べた横棒グラフ。100万トークンあたりのドル。Gemini 3.7 Flash は入力0.75ドル・出力3.75ドル、Claude Sonnet 5 は入力2.00ドル・出力10.00ドル、GPT-5.6 Terra は入力2.00ドル・出力12.00ドル、Muse Spark 1.2 は入力1.25ドル・出力4.25ドル。ただし Gemini の値は2026年12月31日までの導入価格で、2027年1月1日から1.50ドルと7.50ドルになる。GPT-5.6 Terra は短い入力のときの値段。Muse Spark 1.2 だけ提供元の公式ページを確認できていない。">
<figcaption>単価だけを並べたところ。ここから先が本題です</figcaption>
</figure>

**この表は、そのまま「どれが安いか」の表としては読めません。**理由を3つ書きます。

**1つめ。Gemini の安さには期限があります。**$0.75 / $3.75 は2026年12月31日までです。年明けに $1.50 / $7.50 になると、出力は Claude Sonnet 5 の $10 との差が縮みます。**いまの単価で立てた予算は、年明けにそのまま2倍になります**。

**2つめ。トークンの数え方が会社ごとに違います。**Anthropic の料金ページには、Claude 4.7 以降のモデルは新しい数え方を使っていて、**同じ文章でおよそ30%多いトークンになる**と書かれています（出典: <https://platform.claude.com/docs/en/about-claude/pricing>）。同じ会社の中でも世代でずれるので、他社との間ではもっとずれます。単価表の並び順と、月末の請求額の並び順は一致しません。

**3つめ。一度に書ける量が倍違います。**<mark>Claude Sonnet 5 と GPT-5.6 Terra は一度に12.8万トークンまで書けますが、Gemini 3.7 Flash は6.4万トークンです</mark>（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>、<https://developers.openai.com/api/docs/models>、<https://deepmind.google/models/model-cards/gemini-3-7-flash>）。長い文書を一度に書かせる使い方だと、単価の前にここで選択肢が決まります。

### 同じ表の中で、3.7 Flash が一番だったのは何項目か

モデルカードの比較表には、単価の2行を除くと20項目のテストが載っています。この記事で1行ずつ数えました。

<figure class="figure">
<img src="/static/images/gemini37-not-first.svg" alt="Google のモデルカードの比較表で、Gemini 3.7 Flash が最高値だった項目の数を示した図。20項目のうち9項目で最高、残り11項目は他社か前の世代のほうが上だった。上だった例として、DeepSWE v1.1 は3.7 Flash の65.3％に対し GPT-5.6 Terra が69.6％、Terminal-bench 3.0 は14.9％に対し GPT-5.6 Terra が20.8％、GDPVal-AA v2 は Elo 1525 に対し Muse Spark 1.2 が1628、Agent's Last Exam は26.3％に対し Claude Sonnet 5 が33.3％、CharXiv（道具あり）は88.7％に対し前の世代の Gemini 3.6 Flash が89.4％。表を作ったのは Google であり、相手の会社が同じ条件で測った値ではない。">
<figcaption>自社の発表に載せた表でも、全項目で勝っているわけではありません</figcaption>
</figure>

<mark>20項目のうち、3.7 Flash が最高値だったのは9項目です</mark>。残り11項目は、他社か前の世代のほうが上でした（出典: <https://deepmind.google/models/model-cards/gemini-3-7-flash>）。とくに GPT-5.6 Terra は DeepSWE v1.1 で 69.6%、Terminal-bench 2.1 で 87.4%、Terminal-bench 3.0 で 20.8% と、自動作業の系統で 3.7 Flash より上に出ています。

<mark class="warn">ただし、この表を作ったのは Google です</mark>。他社が同じ条件で同じテストを測った値ではありません。Muse Spark 1.2 は測っていない項目のほうが多く、表では「—」になっています。勝ち負けを数えるときも、その空欄は数に入れていません。

## どういう人に効くか

**いま動かしてみるといい人**

- 3.6 Flash をすでに使っている人。点数はほとんどの項目で上がり、単価は同じです。値段が上がる要素が見当たりません。
- 難しいPDFや長い動画を読ませたい人。GDP.pdf は 22.0% から 34.0%、LVBench は 84.2% から 85.4% と公式は説明しています。
- 急がない大量処理をしている人。**年内はまとめ処理（Batch）で $0.375 / $1.875 です**。

**急がなくていい人**

- 単価だけで乗り換え先を決めたい人。安いのは2026年12月31日までです。年明けの $1.50 / $7.50 で計算し直してから決めても遅くありません。
- 一度に長い文章を書かせたい人。6.4万トークンで足りるかを先に確かめてください。
- 図表の読み取りが仕事の中心の人。CharXiv だけは 3.6 Flash のほうが高い点でした。

**この記事で分からないこと**

実際に使ったときの体感、日本語での品質、返答が返ってくるまでの待ち時間。発表ページには利用企業の声として「3.6 Flash より35%安く済んだ」といった数字も載っていますが、どういう作業を何回測った値なのかは書かれていないため、この記事では比較に使っていません。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 3.7 Flash の発表（Google・2026年8月13日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/>
   （Google DeepMind 側の <https://deepmind.google/blog/introducing-gemini-3-7-flash/> を開くと、このページへ転送されます）
2. Gemini 3.7 Flash のモデルカード（Google DeepMind 公式）: <https://deepmind.google/models/model-cards/gemini-3-7-flash>
3. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. Gemini Flash のモデルページ（Google DeepMind 公式）: <https://deepmind.google/models/gemini/flash/>
5. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
6. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>
7. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
8. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>

Muse Spark 1.2 の提供元（Meta）の公式ドキュメントには、この記事を書いた環境から到達できませんでした。そのため単価も仕様も「確認できず」と書いてあります。

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
