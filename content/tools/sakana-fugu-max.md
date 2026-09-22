---
title: Sakana Fugu Maxは「モデル」を持たない——複数の既存モデルを使い分けて安さを稼ぐ
description: 2026年9月11日に Sakana AI が発表した Fugu Max・Fugu Ultra v2 について、公式発表ページに書かれている数字だけを整理しました。単独のAIモデルではなく、複数のモデルを自動で使い分ける「オーケストレーション」という仕組みで、価格とベンチマークをそれぞれ他社の公式ページと突き合わせています。
category: tools
scene: choose
published: 2026-09-14
checked: 2026-09-14
tags: [Sakana AI, オーケストレーション, 料金, AI最新情報]
---

## 何が変わったか

日本の Sakana AI（サカナAI）は2026年9月11日、**Fugu Max**と**Fugu Ultra v2**を発表しました（出典: <https://sakana.ai/fugu-max-release/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- <mark>Fugu Max・Fugu Ultra v2 は、それ自体が1つのAIモデルではありません</mark>。複数のオープンモデルや専門モデルを自動で選んで組み合わせる「オーケストレーション」という仕組みで、公式は「同じオーケストレーションの基盤を、2つの目的に最適化したもの」と説明しています（出典: 同上）。
- **Fugu Max**は安さ重視です。100万トークンあたり入力$2・出力$6で、Sakana自身の比較グラフでは10項目のベンチマーク中6項目で最高値でした（出典: 同上）。
- **Fugu Ultra v2**は性能重視です。Sakana自身の比較グラフでは、Claude Opus 5・GPT-6 Astra などと並べた8項目中5項目で最高または同点最高でした（出典: 同上）。

先に断っておきます。**この記事は運営者がFugu Max・Fugu Ultra v2を試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「速かった」「賢くなった」といった使用感は一切書いていません。

## 前のモデルとの違い

### ここまでの歩み

Sakana AI は発表ページに、Fugu の展開をこう振り返っています（出典: 同上）。

| 時期 | 出来事 |
|---|---|
| 2026年4月 | Beta公開。マルチエージェントの組み合わせが、1つの基盤モデルとして機能することを示した |
| 2026年6月 | 一般提供開始＋Fugu Ultra v1。オーケストレーション層が難しいベンチマークで閉じたフロンティアモデルに並べることを示した |
| 2026年7月 | Fugu-Cyber＋Claude Code対応。セキュリティやコーディング環境向けの専門化を示した |
| 2026年8月 | Sakana Chatの提供・**NVIDIA Nemotron**ファミリーとの連携開始 |
| 2026年9月（今回） | Fugu Max・Fugu Ultra v2 |

<mark>Fugu Max は「Sakana Fugu がオーケストレーションできるモデルの数を増やした」ものです。</mark>NVIDIA との連携で Nemotron ファミリーを含む、オープンウェイトと専門モデルの組み合わせをこれまでで最も多く統合したと公式は説明しています（出典: 同上）。

### Fugu Ultra v1.1 → v2 のベンチマーク

公式ページには、前のバージョン Fugu Ultra v1.1 と v2 を並べた比較グラフがあります。グラフに書き添えられた数字をそのまま表にしました。

| ベンチマーク | Fugu Ultra v1.1 | Fugu Ultra v2 |
|---|---|---|
| HLE (text) | 53.5 | 56.3 |
| GDP.pdf（難しいPDFの読み取り） | 30.0 | 34.3 |
| Chartography（図表の読み取りとデータ解釈） | 47.0 | 48.3 |
| SWEFish（Sakana独自のコーディング課題） | 68.5 | 71.8 |
| DeepSWE（長い工程のソフト開発） | 72.3 | 74.3 |
| ProgramBench | 79.8 | 81.0 |
| GPQA-D（大学院レベルの専門知識テスト） | 95.6 | 95.5 |
| Toolathon | 75.0 | 80.6 |

出典: すべて <https://sakana.ai/fugu-max-release/>

<figure class="figure">
<img src="/static/images/fugu-ultra-v2-vs-v11.svg" alt="前のバージョン Fugu Ultra v1.1 と Fugu Ultra v2 の点数を比べた横棒グラフ。HLE(text)は53.5から56.3、GDP.pdfは30.0から34.3、Chartographyは47.0から48.3、SWEFishは68.5から71.8、DeepSWEは72.3から74.3、ProgramBenchは79.8から81.0、Toolathonは75.0から80.6へ上がった。GPQA-Dだけ95.6から95.5へわずかに下がった。Sakana AI が発表ページのグラフに書き添えた数字をそのまま並べたもの。">
<figcaption>8項目中7項目で上がったが、1項目だけ下がっている</figcaption>
</figure>

<mark>8項目のうち7項目は前のバージョンより点数が上がっていますが、GPQA-Dだけ 95.6 から 95.5 へわずかに下がっています</mark>（出典: 同上）。差はわずかですが、「全部よくなった」わけではないことは、公式のグラフにそう書いてあります。

もう1つ、公式ページの注記で分かることがあります。<mark class="warn">Fugu Ultra v2 のベンチマークには、Claude Fable 5・Fable 5.1・GPT-6-Astra がモデルの組み合わせ先に含まれていない</mark>と明記されています（出典: 同上）。つまりこれらのモデルを内部で呼び出して答えを作っているわけではなく、それでいて次の節で見る通り、いくつかのベンチマークではこれらのモデルと並ぶか上回る点数を出しています。

## 他社の最上位モデルとの比較

### 価格：Sonnet 5より安いが、Gemini 3.8 Flashより高い

Fugu Max の価格は「100万トークンあたり入力$2・出力$6」で、公式は「この出力単価は Sonnet 5・GPT 5.6 Terra・Kimi K3 より40〜60%安い」と説明しています（出典: <https://sakana.ai/fugu-max-release/>）。この記事では、Sakana が比較に挙げた2社の単価を、各社自身の公式料金ページで確かめました。

| モデル | 入力（100万トークン） | 出力（100万トークン） | 確認先 |
|---|---|---|---|
| Fugu Max | $2 | $6 | Sakana AI 発表ページ |
| Gemini 3.8 Flash | $0.75（年内） | $3.75（年内） | Google 公式料金ページ |
| Claude Sonnet 5 | $2 | $10 | Anthropic 公式ドキュメント |
| GPT 5.6 Terra（入力短） | $2 | $12 | OpenAI 公式ドキュメント |

出典: Fugu Max は <https://sakana.ai/fugu-max-release/>、Gemini は <https://ai.google.dev/gemini-api/docs/pricing>、Claude は <https://platform.claude.com/docs/en/about-claude/pricing>、GPT は <https://developers.openai.com/api/docs/pricing>（すべて2026-09-14 確認）

<figure class="figure">
<img src="/static/images/fugu-max-price-vs-flagships.svg" alt="Fugu Max・Gemini 3.8 Flash・Claude Sonnet 5・GPT 5.6 Terra の単価を比べた横棒グラフ。100万トークンあたりのドル。Fugu Max は入力2ドル・出力6ドル、Gemini 3.8 Flash は入力0.75ドル・出力3.75ドル、Claude Sonnet 5 は入力2ドル・出力10ドル、GPT 5.6 Terra（入力が短いとき）は入力2ドル・出力12ドル。GPT 5.6 Terra は入力が長いと入力4ドル・出力18ドルに上がる。Gemini 3.8 Flashの価格は2026年12月31日までの導入価格で、2027年1月1日から1.50ドルと7.50ドルになる。">
<figcaption>Sonnet 5より安いが、いちばん安いのはGemini 3.8 Flash</figcaption>
</figure>

<mark>Sakana が比較に挙げた Claude Sonnet 5・GPT 5.6 Terra については、公式ページの数字と一致しました</mark>。Fugu Max の出力単価$6は、Sonnet 5の$10より40%、GPT 5.6 Terraの$12より50%安く、Sakanaの「40〜60%安い」という説明の範囲に収まります（この記事の計算）。

<mark class="warn">ただし、この記事で新たに突き合わせた Gemini 3.8 Flash（出力$3.75・2026年12月31日までの導入価格）は、Fugu Max より安いです</mark>。Fugu Maxの出力単価はGemini 3.8 Flashより60%高くなります（この記事の計算）。Sakanaの比較にGemini 3.8 Flashは入っていないので、「40〜60%安い」という説明そのものは誤りではありませんが、比較相手を広げると一番安いわけではありません。

### ベンチマーク：Fugu Maxは10項目中6項目で最高

Sakana自身の発表ページには、Fugu Max と GLM-5.3・Gemini 3.8 Flash・Qwen3.8-max・Sonnet 5・GPT 5.6 Terra・DeepSeek V4 Pro・Kimi K3 を並べた比較グラフが10項目分あります。この記事で1項目ずつ数えました。

<figure class="figure">
<img src="/static/images/fugu-max-bench-wins.svg" alt="Sakana AI が発表ページに載せた比較グラフで、Fugu Max が最高値だった項目の数を示した図。10項目のうち6項目で最高、残り4項目は他のモデルのほうが上だった。上だった例として、HLE(text)はFugu Maxの44.7に対しKimi K3が46.9、DeepSWEは70.8に対しGemini 3.8 Flashが73.7、CharXiv Reasoning（道具なし）は88.1に対しQwen3.8-maxが88.4、Chartographyは37.0に対しGemini 3.8 Flashが40.9。表を作ったのはSakana AIであり、相手の会社が同じ条件で測った値ではない。">
<figcaption>最高値だったのは10項目中6項目。残り4項目は他社モデルのほうが上</figcaption>
</figure>

<mark>10項目のうち、Fugu Max が最高値だったのは Terminal Bench 2.1・GPQA-D・AA-LCR・GDP.pdf・AutomationBench・SWEFish の6項目です</mark>（出典: 同上）。残り4項目（HLE・DeepSWE・CharXiv Reasoning・Chartography）は、Kimi K3 や Gemini 3.8 Flash、Qwen3.8-max のほうが上でした。

<mark class="warn">ただし、この表を作ったのは Sakana AI です</mark>。他社が同じ条件で同じテストを測った値ではありません。

### Fugu Ultra v2：他社の最上位モデルと並べて上位2位に入れなかったのは1項目

Fugu Ultra v2 のグラフには、Claude Opus 5・Claude Fable 5.1・GPT-6 Astra・GPT 5.6 Sol・Kimi K3 が並んでいます。前バージョンの Fugu Ultra v1.1 を除いて順位を数えると、次のようになります。

<figure class="figure">
<img src="/static/images/fugu-ultra-v2-vendor-grid.svg" alt="Fugu Ultra v2 を、Claude Opus 5・Claude Fable 5.1・GPT-6 Astra・GPT 5.6 Sol・Kimi K3 と並べた8つのベンチマークで、上位2位に入った項目の数を示した図。8項目のうち7項目で上位2位に入り、残り1項目のProgramBenchだけ4位だった。ProgramBenchの順位は、1位GPT-6 Astra 85.4、2位Claude Fable 5.1 82.7、3位Claude Opus 5 82.3、4位Fugu Ultra v2 81.0。前バージョンのFugu Ultra v1.1は順位から除いて数えている。表を作ったのはSakana AIであり、相手の会社が同じ条件で測った値ではない。">
<figcaption>8項目中7項目で上位2位。ProgramBenchだけ4位だった</figcaption>
</figure>

<mark>8項目のうち7項目で上位2位に入っています。</mark>ただしProgramBenchだけは4位（81.0）でした。上にいるのは次の3モデルです（出典: 同上）。

- GPT-6 Astra（85.4）
- Claude Fable 5.1（82.7）
- Claude Opus 5（82.3）
「Fugu Ultra v2は複雑な多段タスクで新しい基準を作った」という発表文の中でも、この1項目だけは他社の3モデルすべてに及んでいません。

比較に使った各社の最上位モデルの単価も、公式ページで確認できる範囲で並べておきます。

| モデル | 入力（100万トークン） | 出力（100万トークン） |
|---|---|---|
| Claude Opus 5 | $5 | $25 |
| Claude Fable 5.1 | $10 | $50 |
| GPT-6 Astra | $10（入力短） | $50（入力短） |
| GPT 5.6 Sol | $4（入力短） | $20（入力短） |

出典: Claude は <https://platform.claude.com/docs/en/about-claude/pricing>、GPT は <https://developers.openai.com/api/docs/pricing>（いずれも2026-09-14 確認）。Fugu Ultra v2自体の単価は発表ページに記載がなく、確認できませんでした（記載があるのはFugu Maxの単価のみ）。

## どういう人に効くか

**いま動かしてみるといい人**

- すでに OpenAI互換のAPIで何かを動かしていて、トークン単価を抑えたい人。公式は「1行のパラメータ変更だけでアップグレードでき、移行作業は不要」と説明しています（出典: <https://sakana.ai/fugu-max-release/>）。
- 特定の1社に依存せず、複数のモデルを裏で切り替えて使いたい人。公式は「交換可能なモデルの組み合わせによって、サプライチェーンの回復力が設計として組み込まれている」と説明しています（出典: 同上）。

**急がなくていい人**

- どのモデルが実際に答えを作ったかを、自分で指定・確認したい人。オーケストレーションの仕組み上、リクエストごとにどのモデルが選ばれたかは公式ページに記載がありません。
- 単価だけで乗り換え先を決めたい人。<mark>比較を広げると、この記事で見た範囲では Gemini 3.8 Flash のほうが安いです</mark>。
- 日本語での品質や、応答が返ってくるまでの待ち時間を先に知りたい人。発表ページにはどちらも記載がなく、運営者も試していないので書けません。

## 出典一覧

すべて公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Fugu Max・Fugu Ultra v2 の発表（Sakana AI・2026年9月11日）: <https://sakana.ai/fugu-max-release/>
2. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
3. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
4. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
