---
title: Geminiが画面操作を標準搭載——2ヶ月足らずで旧世代に
description: 2026年6月24日にGoogleが発表した「Gemini 3.5 Flashへの画面操作（Computer Use）標準搭載」について、公式ドキュメントとモデルカードに書かれている数字だけを並べました。Anthropic・OpenAIの画面操作ツールとも、操作の数と料金の建て付けを突き合わせています。
category: tools
scene: choose
published: 2026-08-31
checked: 2026-08-31
tags: [Gemini, 画面操作, Computer Use, AI最新情報]
---

## 何が変わったか

Google は 2026年6月24日、**画面操作（Computer Use）を Gemini 3.5 Flash の標準機能にした**と発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-computer-use-gemini-3-5-flash/>）。公式ページに書かれていることだけを並べます。3行にすると、こうなります。

- 画面操作は、これまで **`gemini-2.5-computer-use-preview-10-2025`** という専用の別モデルでした。それが 3.5 Flash に**内蔵ツールとして統合**されました（出典: 同上）。
- ブラウザ・モバイル・デスクトップの**3つの環境**に対応します（出典: 同上）。Gemini API と Gemini Enterprise Agent Platform から、発表当日にすぐ使えます。
- 料金は専用モデルとしての別建てをやめ、**普通の 3.5 Flash と同じトークン単価**になりました（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。

先に断っておきます。**この記事は運営者がこの機能を試した記録ではありません。**公式ページとドキュメントに書かれていることを読んで整理したものです。「動きが速かった」「精度が良かった」といった使用感は一切書いていません。

<figure class="figure">
<img src="/static/images/gemini35cu-timeline.svg" alt="Gemini の画面操作機能の年表。2026年5月19日にGemini 3.5 Flashを発表（この時点では画面操作は搭載されていない）。その36日後の6月24日、画面操作をGemini API・Gemini Enterprise Agent Platform経由で標準搭載。さらに50日後の8月13日にGemini 3.7 Flashを発表し、公式ドキュメントの推奨モデルが3.7 Flashに交代した。8月26日（この記事の確認時点）でもドキュメントは3.5 Flashを「Previous stable model」と説明している。日数はいずれも暦日の単純な引き算。">
<figcaption>画面操作が標準搭載されてから、推奨モデルが交代するまで50日</figcaption>
</figure>

<mark>Gemini 3.5 Flash 自体の発表は 2026年5月19日で、画面操作はその時点では載っていませんでした</mark>（出典: <https://deepmind.google/models/model-cards/gemini-3-5-flash>）。発表から36日後に、あとから機能として追加された形です。

さらに、この記事を書いている時点（2026年8月26日更新のドキュメントを確認）で、ai.google.dev の Computer use ページは <mark class="warn">3.5 Flash を「Previous stable model」（前の安定版）と表記しています</mark>（出典: <https://ai.google.dev/gemini-api/docs/computer-use>）。「推奨モデル」の座は、2026年8月13日に発表された Gemini 3.7 Flash に移っています（出典: 同上）。標準搭載の発表からわずか50日です。

## 前のモデルとの違い

### 専用モデルから内蔵ツールへ

前の画面操作モデル `gemini-2.5-computer-use-preview-10-2025` は、「ブラウザ制御エージェントの構築に最適化した、当社の Computer Use モデル」という専用モデルでした（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。ドキュメントでは「Legacy preview model optimized for browser-based computer use」（レガシーのプレビューモデル、ブラウザ向け）と説明されています（出典: <https://ai.google.dev/gemini-api/docs/computer-use>）。<mark>対応環境はブラウザだけでした</mark>。

いま画面操作に対応しているのは、Gemini 3.7 Flash・Gemini 3.5 Flash-Lite・Gemini 3.5 Flash・Gemini 3 Flash Preview の4モデルです（出典: 同上）。**ドキュメントが「推奨」と明記しているのは Gemini 3.7 Flash で、Gemini 3.5 Flash は「Previous stable model」（1つ前の安定版）という表記です**（出典: 同上）。この記事の主役である「3.5 Flash への標準搭載」自体、いまでは一段落ちた位置づけになっています。

### 対応環境が1つから3つに

Gemini 3.x 系の画面操作は、**ブラウザ・モバイル・デスクトップ**の3つの環境に対応します（出典: <https://ai.google.dev/gemini-api/docs/computer-use>）。環境ごとに使える操作（アクション）の数を、ドキュメントの表から数えました。

<figure class="figure">
<img src="/static/images/gemini35cu-actions.svg" alt="3社の画面操作ツールで、1回に呼べる操作の種類の数を比べた横棒グラフ。Geminiのブラウザ環境が20個、Geminiのデスクトップ環境が17個、Anthropicのデスクトップ専用ツールが17個、Geminiのモバイル環境が10個、OpenAIのgpt-5.6のcomputerツールが9個。OpenAIのclickはボタン（左・右・中央）を引数で渡す形なので、右クリックや中央クリックは別の操作として数えていない。Anthropicは画面操作とは別にブラウザ専用のbrowser use toolを持つが、この図には含めていない。">
<figcaption>同じ「画面操作」でも、1回に呼べる操作の数は会社ごとに違う</figcaption>
</figure>

**ブラウザ環境が一番多機能で20個の操作**（クリック系6種・キー操作5種・スクロール・前後移動など）に対応しています。**モバイル環境は10個**しかなく、`open_app`（アプリを名前で開く）や `list_apps`（インストール済みアプリの一覧を取る）といったモバイル特有の操作に入れ替わっています（出典: 同上）。デスクトップ環境は17個で、ブラウザ用の `navigate`（URLを直接開く）・`go_back`・`go_forward` の3つが無い代わりに、それ以外はブラウザ環境と同じです（出典: 同上）。

## 他社の最上位モデルとの比較

### 操作の数え方が会社ごとに違う

Anthropic の computer use tool（`computer_toolset_20260801`）は、<mark>「17個のメンバーツールを持つ」とドキュメントに明記</mark>されています（出典: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>）。ちょうど Gemini のデスクトップ環境と同じ数です。ただし Anthropic は画面操作（デスクトップ）とは別に、**ブラウザ内の作業専用の「browser use tool」を別立てで用意**しています（出典: 同上）。1つのツールで3環境をまかなう Gemini とは、道具の分け方が違います。

OpenAI は少し毛色が違います。ガイドの「Possible Computer use actions」の一覧には、<mark>click・double_click・scroll・type・wait・keypress・drag・move・screenshot の9個しか並んでいません</mark>（出典: <https://developers.openai.com/api/docs/guides/tools-computer-use>）。右クリックや中央クリックといった専用の操作は無く、`click` にボタンを指定する形で表現します。**操作の種類が少ないからといって、できることが少ないとは言い切れません**——1つの操作に引数を持たせて表現の幅を広げる設計だからです。

<mark class="warn">なお同じガイドの本文は「gpt-5.4 が画面操作向けの新しい訓練を受けている」と書いている一方、コード例はすべて gpt-5.6 を使っています</mark>（出典: 同上）。どちらが現行の推奨モデルなのか、本文とコード例で表記がずれています。

### 専用モデルの終了は、OpenAIも同じ道をたどった

OpenAI も同じ設計変更を経験しています。ガイドの移行セクションには、**「非推奨の computer-use-preview ツールから移行するには」**という見出しがあり、専用モデル `computer-use-preview` は非推奨と明記されています（出典: <https://developers.openai.com/api/docs/guides/tools-computer-use>）。移行後は、flagship モデルである gpt-5.6-sol・gpt-5.6-terra・gpt-5.6-luna のいずれでも `computer` ツールとして画面操作が使えます（出典: <https://developers.openai.com/api/docs/models>）。**「専用モデル→主力モデルへの内蔵」という流れは、GoogleもOpenAIも同じです。**

### 料金の建て付け

Gemini の画面操作は、いまは**別立ての料金がありません**。ドキュメントには「Computer use: Charged as regular tokens per model pricing (e.g., standard Gemini 3.5 Flash pricing)」（画面操作は、使うモデルの通常のトークン料金で課金される）とはっきり書かれています（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。

| | 入力（100万トークン） | 出力（100万トークン） |
|---|---|---|
| 旧: Gemini 2.5 Computer Use Preview（専用モデル） | $1.25（20万トークンまで）／$2.50（超過分） | $10.00（20万トークンまで）／$15.00（超過分） |
| 新: Gemini 3.5 Flash（内蔵ツール・通常料金） | $1.50 | $9.00 |

出典: いずれも <https://ai.google.dev/gemini-api/docs/pricing>

**出力側は $10.00〜$15.00 から $9.00 に下がり、長い入力（20万トークン超）向けの割増料金も無くなりました**。<mark>入力側だけは $1.25 から $1.50 にわずかに上がっています</mark>が、専用モデル時代にあった「長い入力は2倍」という段差が消えたぶん、長いやり取りをするタスクでは差が出ます。

Anthropic は少し違う課金の考え方です。**画面操作ツールそのものの追加料金は無く、通常のツール利用料金**に従いますが、`computer_toolset_20260801` を宣言するだけで、リクエストに**約4,500トークン分のオーバーヘッド**が乗ります。モデルによって差があり、Claude Fable 5・Mythos 5・Opus 5・Opus 4.8 では約4,520トークン、**Claude Sonnet 5 では約4,590トークン**とドキュメントに書かれています（出典: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>）。`zoom`（画面の一部を拡大して読む機能）を無効にすると、そこから約410トークン減ります（出典: 同上）。<mark>スクリーンショット自体は画像入力として別途課金されます</mark>（出典: 同上）。

### 画面操作の実力テストでの立ち位置

Google が Gemini 3.5 Flash のモデルカードに載せている比較表から、画面操作の実力を測る **OSWorld-Verified** の行を抜き出しました。

<figure class="figure">
<img src="/static/images/gemini35cu-osworld.svg" alt="OSWorld-Verified（画面操作の実力を測るベンチマーク）の点数を6モデルで比べた横棒グラフ。GPT-5.5が78.7%、Gemini 3.5 Flashが78.4%、Claude Opus 4.7が78.0%、Gemini 3.1 Proが76.2%、Claude Sonnet 4.6が72.5%、Gemini 3 Flashが65.1%。Gemini 3.5 Flashは自社の旧世代（Gemini 3 Flash・3.1 Pro）より高く、他社の当時の最上位（GPT-5.5・Claude Opus 4.7）とほぼ並ぶ。表を作ったのはGoogleであり、他社が同じ条件で測った値ではない。比較に使われた他社モデルは2026年5月時点の世代。">
<figcaption>画面操作の実力テストで、3.5 Flashは自社の旧世代より他社に近い</figcaption>
</figure>

出典: すべて <https://deepmind.google/models/model-cards/gemini-3-5-flash>（「Results as of May, 2026」の表・UI Control / OSWorld-Verified の行）

<mark>Gemini 3.5 Flash は 78.4% で、自社の旧世代（Gemini 3 Flash の65.1%、Gemini 3.1 Pro の76.2%）より高い点数です</mark>。他社の当時の最上位モデルとも近く、GPT-5.5 の78.7%とはほぼ並び、Claude Opus 4.7 の78.0%もわずかに下回るだけです。

<mark class="warn">ただし、この表を作ったのは Google です</mark>。他社が同じ条件・同じ環境で測った値ではありません。さらに**比較に使われている Claude Sonnet 4.6・Claude Opus 4.7・GPT-5.5 は、いずれも2026年5月時点の世代**です。この記事を書いている8月時点の最新世代（Claude Sonnet 5・Opus 5、GPT-5.6）ではないので、いまの他社モデルと比べたらこの順位のままとは限りません。

また、モデルカードのテスト名は **OSWorld-Verified** です。<mark class="warn">Gemini 3.7 Flash のモデルページに載っている「OSWorld-2.0」は別バージョンの表記なので、この記事では両者の数字を並べていません</mark>。名前が似ているだけで、同じテストとして比べると誤った結論になります。

## どういう人に効くか

**いま動かしてみるといい人**

- ブラウザだけでなく、モバイルやデスクトップの操作も自動化したい人。3つの環境に1つのツールで対応します。
- 前の `gemini-2.5-computer-use-preview-10-2025` を使っていた人。**通常のトークン料金になり、長い入力の割増も消えました。**
- OpenAI の `computer-use-preview` を使っていた人。同じ「専用モデルから主力モデルへの統合」が Gemini でも起きています。

**急がなくていい人**

- 「最新のGeminiを」という理由だけで選びたい人。ドキュメント上の推奨モデルはすでに Gemini 3.7 Flash です。
- Anthropic のように、ブラウザ操作とデスクトップ操作を別のツールとして厳密に切り分けたい人。Gemini は1つのツールにまとまっています。
- 他社の最新モデルと比べて選びたい人。**Googleが載せている比較表は2026年5月時点の他社モデルとの比較で、いまの最新世代ではありません。**

**この記事で分からないこと**

実際に画面操作をさせたときの成功率・失敗のしかた・日本語UIでの挙動。運営者は試していないので書けません。OSWorld-Verified の点数は「テスト環境でのタスク成功率」であり、実際の業務アプリでの成功率とは別物です。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. 画面操作の標準搭載の発表（Google・2026年6月24日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-computer-use-gemini-3-5-flash/>
   （Google DeepMind 側の <https://deepmind.google/blog/introducing-computer-use-in-gemini-3-5-flash/> を開くと、このページへ転送されます）
2. Computer use のドキュメント（Google 公式・最終更新 2026-08-26）: <https://ai.google.dev/gemini-api/docs/computer-use>
3. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. Gemini 3.5 Flash モデルカード（Google DeepMind 公式）: <https://deepmind.google/models/model-cards/gemini-3-5-flash>
5. computer use tool のドキュメント（Anthropic 公式）: <https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool>
6. Computer use のガイド（OpenAI 公式）: <https://developers.openai.com/api/docs/guides/tools-computer-use>
7. モデル一覧（OpenAI 公式）: <https://developers.openai.com/api/docs/models>

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
