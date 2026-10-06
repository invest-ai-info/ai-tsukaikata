---
title: 声も動画も検索できるGemma——無料だが動かすのは自分の環境
description: 2026年10月6日に発表された EmbeddingGemma 2 について、Google のモデルカード・発表ページに書かれている数字だけを並べました。文章・画像・動画・音声をまとめて検索できる埋め込みモデルで、商用利用も含めて無料です。ただしOpenAIの有料API、Anthropicが公式に紹介するVoyage AIとは売り方（提供形態）そのものが違うため、単純な安い高いでは比較していません。
category: tools
scene: choose
published: 2026-10-06
checked: 2026-10-06
tags: [Gemma, 埋め込みモデル, Google, AI最新情報]
---

## 何が変わったか

2026年10月6日、Google は **EmbeddingGemma 2** を発表しました（出典: <https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/>）。公式ページに書かれている数字だけで3行にまとめます。

- <mark>文章だけでなく画像・動画・音声も、1つの768次元のベクトル空間にまとめて検索できるモデルです</mark>。前世代（EmbeddingGemma、2025年9月発表）は文章専用でした（出典: 同上）。
- <mark>商用利用も含めて、無料で使えます</mark>。パラメータ（モデルの重み）そのものを、Hugging Face と Kaggle から無料でダウンロードできます（出典: 同上）。
- パラメータは合計7.4億。文章だけで使うなら2.7億パラメータで動き、画像用（1.7億）・音声用（3.0億）のエンコーダーは必要なときだけ追加する構成です（出典: 同上）。

先に断っておきます。**この記事は運営者がこのモデルを動かした記録ではありません。**公式ページとモデルカードに書かれていることを読んで整理したものです。実際に動かしたときの速さや精度は書いていません。

## 前のモデルとの違い

### 数字で見る変化

| | EmbeddingGemma（2025年9月発表） | EmbeddingGemma 2（2026年10月6日発表） |
|---|---|---|
| モダリティ | テキストのみ | テキスト・画像・動画・音声 |
| パラメータ（テキスト専用の構成） | 3.00億 | 2.70億 |
| 読める長さ（コンテキスト） | 2,048トークン | 8,192トークン（4倍） |
| 出力の次元 | 768（512/256/128に切り詰め可） | 768（512/256/128に切り詰め可） |
| MTEBコード（NDCG@10） | 68.76 | 78.68 |
| MTEB多言語（v2・平均） | 61.15 | 61.36 |
| ライセンス | Gemma利用規約（使用制限あり） | Apache 2.0（制限条項なし） |

出典: EmbeddingGemma 2 モデルカード（<https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2>。比較表に旧モデルの数値も載っています）、EmbeddingGemma（v1）モデルカード（<https://ai.google.dev/gemma/docs/embeddinggemma/model_card>）、Gemma利用規約（<https://ai.google.dev/gemma/terms>）

<figure class="figure">
<img src="/static/images/embeddinggemma2-v1-vs-v2.svg" alt="EmbeddingGemmaからEmbeddingGemma 2への変化を示した表。モダリティはテキストのみからテキスト・画像・動画・音声へ拡大。テキスト専用の構成のパラメータ数は3.00億から2.70億へ減少。読める長さは2,048トークンから8,192トークンへ4倍に拡大。MTEBコード（NDCG@10）は68.76から78.68に上昇。MTEB多言語は61.15から61.36とほぼ変わらず。ライセンスは使用制限のあるGemma利用規約から、制限条項のないApache 2.0に変わった。">
<figcaption>増えたのはモダリティ、軽くなったのはテキスト専用時の構成</figcaption>
</figure>

<mark>読める長さは前世代の4倍（2,048→8,192トークン）に広がりました</mark>。音声や動画をまとめて渡せるのは、この広がりが前提になっています（出典: 同上）。

コードの検索精度も上がりました。<mark>MTEBコード（NDCG@10）の点数は68.76から78.68に上がった一方、MTEB多言語（v2・平均）は61.15から61.36とほとんど変わっていません</mark>（出典: 同上）。**全部の指標が同じだけ良くなったわけではありません。**

この同じコードの点数を、Googleは2つの公式ページで違う言い方で説明しています。

- 発表ページ：「9.92点の改善」
- モデルカード：「約14%の改善」

9.92÷68.76は約14.4%なので、どちらも同じ結果の言い方です（出典: <https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/> と <https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2>）。読む場所によって印象が変わるので、両方の書き方をそのまま残しておきます。

もう1つ、見つけた変化があります。**ライセンスです。**<mark>前世代は「Gemma利用規約」で、禁止用途ポリシーや再配布時の表記義務など使用制限が付いていました。EmbeddingGemma 2のモデルカードには、独立した「License: Apache 2.0」という表記があります</mark>（出典: <https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2> と <https://ai.google.dev/gemma/terms>）。Apache 2.0はGoogle独自の使用制限を持たない、一般的なオープンソースライセンスです。

### 使うときの注意点

モデルカードには、使い方を誤ると静かに結果が崩れる注意が2つ書かれています。開発者に伝える・依頼するときに役立つ内容です。

<mark class="warn">float16で動かすと、NaN（非数）か、静かに劣化した埋め込みが返ってきます。エラーにはなりません</mark>（出典: 同上）。bfloat16かfloat32を使うよう、モデルカードは明記しています。

<mark class="warn">768次元から切り詰めたあと、正規化（normalize）をしないと、検索の精度が静かに落ちます</mark>。見た目はそれっぽいスコアが返るので、エラーでは気づけません（出典: 同上）。`truncate_dim` と `normalize_embeddings` を同時に指定するよう、モデルカードは勧めています。

## 他社の最上位モデルとの比較

ここからが、この記事でいちばん断っておきたい点です。<mark>EmbeddingGemma 2には「単価」がありません。重みを無料で公開していて、動かすのは自分のパソコンやサーバーだからです</mark>。OpenAIとAnthropicは、そもそも埋め込みモデルの売り方（提供形態）が違います（出典: 同上）。まず提供形態を並べます。

<figure class="figure">
<img src="/static/images/embeddinggemma2-vendor-shape.svg" alt="埋め込みモデルの提供形態を3社で比べた表。提供形態＝Googleは重みを無料公開して自分の環境で動かす、OpenAIは有料のAPI（従量課金）、Anthropicは自社モデルが無くVoyage AIを紹介。テキストの単価（100万トークン）＝Googleは無料（計算は自己負担）、OpenAIは0.02〜0.13ドル、Anthropic（Voyage AI）は確認できず（経路遮断）。対応モダリティ＝Googleはテキスト・画像・動画・音声、OpenAIはテキストのみ、Anthropic（Voyage AI）はテキスト・画像・動画（音声には対応していない）。">
<figcaption>無料の重みと、2種類の有料APIが並ぶ</figcaption>
</figure>

Anthropicの公式ドキュメントには「Anthropicは自社の埋め込みモデルを提供していない」と明記されています。代わりに紹介されているのが、MongoDB傘下のVoyage AIです（出典: <https://platform.claude.com/docs/en/docs/build-with-claude/embeddings>）。

OpenAIは自社で埋め込みモデルを3つ提供しています。単価は次のとおりです。

| モデル | 単価（100万トークンあたり） | MTEB（OpenAI自身の評価） | 最大入力 |
|---|---|---|---|
| text-embedding-3-small | $0.02 | 62.3% | 8,192トークン |
| text-embedding-3-large | $0.13 | 64.6% | 8,192トークン |
| text-embedding-ada-002（旧世代） | $0.10 | 61.0% | 8,192トークン |

出典: すべて <https://developers.openai.com/api/docs/guides/embeddings>（料金ページ <https://developers.openai.com/api/docs/pricing> の数字とも一致）

text-embedding-3-largeの$0.13は、料金ページの画面には表として出ますが、ページの生データ（埋め込みJSON）では`$`記号の付かない`0.13`という数値で持たれています。要約させずにこの生データを直接確認しました。

<mark>OpenAIの3モデルはいずれもテキストのみです。画像・動画・音声は埋め込みの入力にできません</mark>（出典: 同上。ガイドに画像・音声入力の記載はありません）。

Anthropicが紹介しているVoyage AIには、マルチモーダル対応のモデルもあります。読める長さと次元を3社で比べました。

| | EmbeddingGemma 2 | text-embedding-3-large（OpenAI） | voyage-multimodal-3.5（Voyage AI） |
|---|---|---|---|
| 提供元 | Google（自社） | OpenAI（自社） | MongoDB傘下。Anthropicが紹介 |
| 対応モダリティ | テキスト・画像・動画・音声 | テキストのみ | テキスト・画像・動画（音声は非対応） |
| 読める長さ | 8,192トークン | 8,192トークン | 32,000トークン |
| 出力の次元（既定） | 768 | 3,072 | 1,024 |
| 単価（テキスト・100万トークン） | 無料（自分の環境で動かす） | $0.13 | 確認できず |

出典: EmbeddingGemma 2 は <https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2>、OpenAIは <https://developers.openai.com/api/docs/guides/embeddings> と <https://developers.openai.com/api/docs/pricing>、Voyage AIの仕様はAnthropic公式ドキュメント <https://platform.claude.com/docs/en/docs/build-with-claude/embeddings> 掲載の一覧

<figure class="figure">
<img src="/static/images/embeddinggemma2-context-dims.svg" alt="読める長さ（コンテキスト）と埋め込みの次元を3社の公式ページの数字で比べた横棒グラフ。読める長さはEmbeddingGemma 2が8,192トークン、text-embedding-3-large（OpenAI）も同じ8,192トークン、voyage-multimodal-3.5（Anthropicが紹介）は32,000トークンで最大。埋め込みの次元（既定値）はEmbeddingGemma 2が768次元、text-embedding-3-largeが3,072次元、voyage-multimodal-3.5が1,024次元。いずれも各社公式ページに書かれている仕様の数字で、性能テストの点数ではない。">
<figcaption>読める長さはOpenAIと同じ、次元はOpenAIの4分の1</figcaption>
</figure>

<mark class="warn">voyage-multimodal-3.5自体の料金ページ（docs.voyageai.com・voyageai.com）には、この記事を書いた環境から到達できませんでした</mark>。経路遮断（`CONNECT tunnel failed`）によるもので、Voyage AI側のbot判定ではありません。到達できる環境が見つかったら、単価もここに追記する価値があります。

<mark>性能テストの点数（MTEBなど）は、この記事では3社を並べて比較していません</mark>。各社が自社で測っていて、ベンチマークの版・評価対象のタスクもそろっていないためです。公式の数字で言い切れるのは、読める長さ・次元・提供形態までで、どれが賢いかではありません。

## どういう人に効くか

**いま動かしてみるといい人**

- 社内文書や録音を、外部に送らずに検索したい人。EmbeddingGemma 2は自分の環境で動くので、データを外に出さずに済みます。
- 画像・動画・音声をまとめて検索する機能を、アプリに組み込みたい開発者。1つのモデルで4つのモダリティを扱えます。
- すでにEmbeddingGemma（v1）を使っている人。文章専用の構成は前世代より軽く、コードの検索精度も上がっています。

**急がなくていい人**

- プログラミングをする人に頼まず、自分で今日から使いたい人。EmbeddingGemma 2はモデルの重みで、チャット画面のように打てばすぐ動くものではありません。動かすには開発者か、対応済みのアプリ（Google AI Edge Gallery など）が必要です。
- 32,000トークンを超える長い文書を、1回で埋め込みたい人。EmbeddingGemma 2は8,192トークンまでです。
- 日本語での精度を最優先したい人。モデルカードは「100以上の言語に対応するが、言語間で精度が同じとは限らない」と明記しています（出典: 同上）。

**この記事で分からないこと**

実際に動かしたときの検索精度、日本語での使い心地、クラウド経由（Gemini Enterprise Agent Platform Model Garden）で使えるようになったときの料金。発表ページには「coming soon」とだけ書かれており、価格は書かれていません。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. EmbeddingGemma 2の発表（Google・2026年10月6日）: <https://blog.google/innovation-and-ai/technology/developers-tools/embeddinggemma-2/>
   （Google DeepMind側の<https://deepmind.google/blog/embeddinggemma-2-an-open-lightweight-multimodal-embedding-model/>を開くと、このページへ転送されます）
2. EmbeddingGemma 2のモデルカード（Google公式）: <https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2>
3. EmbeddingGemma（v1）のモデルカード（Google公式）: <https://ai.google.dev/gemma/docs/embeddinggemma/model_card>
4. Gemma利用規約（Google公式）: <https://ai.google.dev/gemma/terms>
5. EmbeddingGemma 2のHugging Faceページ: <https://huggingface.co/google/embeddinggemma-2>
6. OpenAIのEmbeddingsガイド: <https://developers.openai.com/api/docs/guides/embeddings>
7. OpenAIの料金ページ: <https://developers.openai.com/api/docs/pricing>
8. OpenAIのモデル一覧: <https://developers.openai.com/api/docs/models>
9. Anthropic公式ドキュメントのEmbeddingsページ（Voyage AIの紹介・仕様一覧）: <https://platform.claude.com/docs/en/docs/build-with-claude/embeddings>
10. Anthropicのモデル一覧（自社に埋め込みモデルが無いことの確認）: <https://platform.claude.com/docs/en/about-claude/models/overview>

Voyage AI自身の公式ページ（docs.voyageai.com・voyageai.com）には、この記事を書いた環境から到達できませんでした。そのため単価は「確認できず」のままにしてあります。

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
