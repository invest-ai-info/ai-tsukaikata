---
title: 自己採点1位のCarbon——使えるのはまだ一部
description: Googleは2026年10月28日にGemini 4 Carbonを発表しました。価格はArgonと完全に同額で先に決まっていますが、使えるのはまだ一部のサイバー防御担当者だけです。公式の発表ページに書かれている数字だけを並べました。
category: tools
scene: choose
published: 2026-10-29
checked: 2026-10-29
tags: [Gemini, モデル比較, 料金, AI最新情報]
---

## 結論：今の立場ごとに、こうなります

Google は2026年10月28日、次のモデル **Gemini 4 Carbon** を発表しました（出典: 発表ページ）。
2週間前に発表した Gemini 4 Argon の後継で、公式は「最も高性能なモデル」と説明しています。
ただし、この記事でいちばん先に書いておきたいのは性能の数字ではありません。
**今日の時点で、一般の開発者はこのモデルを使えません。**

| 今の立場 | 今できること | どうなるか |
|---|---|---|
| **今すぐ試したい開発者・会社員** | 公開APIが無いので試せない | まず一部のサイバー防御担当者に提供され、その後Fairwind Program経由で信頼されたパートナーへ広がる。開発者・企業・一般消費者への提供は「できるだけ早く」としか書かれていない |
| **Gemini 4 Argonを使っている・気にしている人** | そのまま使い続ける | Carbonの導入価格はArgonと1円も違わない。性能は自己採点のベンチマークで上回るとされるが、仕様（コンテキストウィンドウ等）はまだ非公表 |
| **将来の予算を先に見ておきたい人** | 導入価格（入力$2・出力$10）を基準に試算する | 導入期間が終わると入力$4・出力$20に上がる。**終わる日付は発表に書かれていない**（Argonと同じパターン） |

<mark>一言でいうと、値段はもう決まっているが、使えるのはまだサイバー防御の一部の担当者だけです。</mark>

先に断っておきます。**この記事は運営者がCarbonを試した記録ではありません。**公式の発表ページに書かれている数字だけを読んで整理したものです。

ここから下は、表の3行がなぜそうなるのかの説明です。

## なぜそうなるのか

### まだ使えない理由

発表ページには、Carbonの提供範囲がはっきり書かれています（出典: 同上）。

> We're taking a deliberate approach to rollout and are actively engaged in the U.S. government's voluntary process for pre-release model testing. Starting this week, we will make Carbon available to a subset of cyber defenders and will gradually phase access to additional trusted partners through our Fairwind Program.

公開前に、米国政府の自主的な試験プロセスに関わっていると明記されています。<mark class="warn">一般の開発者・企業・個人向けの提供は、まだ始まっていません</mark>。発表ページは「開発者・企業・一般利用者への提供は、できるだけ早く行う」と書くにとどめ、具体的な日付は示していません（出典: 同上）。

> We're eager to see how the initial cohort of cyber defenders use this model and we look forward to bringing Carbon to developers, businesses, and consumers soon.

<mark>この「限定公開→時期未定で一般公開」という流れは、今回が初めてではありません</mark>。2026年9月6日公開の **Gemini 3.8 Flash Cyber**、2026年9月30日公開の **Gemini 4 Argon** に続いて、これで3件目です。[Argonの発表記事](/tools/gemini-4-argon/)で扱ったとおり、Argonは10月13日に一般提供を始めましたが、Carbonは発表からまだ1日で、同じ道筋をたどるかどうかは今の時点では分かりません。

### 価格はArgonと完全に同額（でも使えない）

使えないのに、価格はすでに発表されています。

| | 入力（100万トークンあたり） | 出力（100万トークンあたり） | キャッシュ済み入力 |
|---|---|---|---|
| Carbon（導入価格） | $2.00 | $10.00 | 入力価格の95%引き |
| Carbon（導入期間終了後） | $4.00 | $20.00 | 同上 |

出典: 発表ページ本文と脚注

<mark>Carbonの導入価格は、Argonの導入価格と1円も違いません</mark>（出典: 発表ページ、<https://ai.google.dev/gemini-api/docs/pricing>）。発表ページはこう書いています。

> Gemini 4 Carbon will launch at the same introductory price as Argon at $2 per million input tokens and $10 per million output tokens, with cached input tokens priced at 95% off input token price. After the introductory period expires, the price of $4 per 1M input tokens and $20 per 1M output tokens will apply.

<figure class="figure">
<img src="/static/images/carbon-price-deadline.svg" alt="Gemini 4 Argon（〜2026年11月30日・入力2ドル出力10ドル）、Gemini 4 Argon（12月1日から・入力4ドル出力20ドル）、Gemini 4 Carbon（導入価格・入力2ドル出力10ドル）、Gemini 4 Carbon（導入後・入力4ドル出力20ドル）を比べた横棒グラフ。100万トークンあたりのドル。金額はArgonとCarbonで完全に同額。Argonは値上がりの日付（2026年12月1日）が判明しているが、Carbonの発表にはその記載が無い。">
<figcaption>金額は同じ。違うのは「値上がりの日付が分かっているかどうか」です</figcaption>
</figure>

ここで、Argonとの違いが1つだけあります。Argonは一般提供を始めたときの記事（[Argon一般提供開始](/tools/gemini-4-argon-ga/)）で確認したとおり、値上がりの日付が**2026年12月1日**と判明しています（出典: Gemini API公式料金ページ）。<mark>Carbonの発表には、導入期間がいつ終わるかという日付が一切書かれていません。</mark>いつ値上がりするか分からないまま、価格だけが先に決まっている状態です。

### 性能はどう謳われているか（自社測定だけ）

発表ページは、4つのベンチマークで新記録や1位を主張しています。

| ベンチマーク | 何を測るか | 点数 |
|---|---|---|
| Artificial Analysis Intelligence Index v5.0 | 総合的な知能の指標 | **59**（1位） |
| SEC-bench Pro | セキュリティ脆弱性の発見 | **88.2%**（最高水準） |
| ExploitGym | 見つけた脆弱性の悪用実証 | **54.8%**（新記録） |
| CWE-bench（Collinear運営） | 脆弱性の修復パッチ作成 | **71.0%** |

出典: すべて発表ページ

<figure class="figure">
<img src="/static/images/carbon-benchmarks.svg" alt="Gemini 4 Carbonの発表ページが挙げた点数4つを並べた横棒グラフ。Artificial Analysis Intelligence Index v5.0（総合的な知能の指標）は59で1位、SEC-bench Pro（セキュリティ脆弱性の発見）は88.2%で最高水準、ExploitGym（見つけた脆弱性の悪用実証）は54.8%で新記録、CWE-bench（Collinear運営・脆弱性の修復パッチ作成）は71.0%。いずれもGoogle自身の測定で、他社モデルを同じ条件で測った数字は発表に無い。">
<figcaption>どれもGoogle自身の測定です。他社の同条件の点数は発表にありません</figcaption>
</figure>

このサイトの方針として、<mark>性能テストの点数は、各社が自社で測っていて測り方も対象も違うため、他社モデルと横に並べません</mark>。公式の数字で言い切れるのは単価の並びまでです。この4項目についても、「Googleがそう主張している」という事実だけを書いておきます。

発表ページは、WebDev Arena（開発者向けの投票ランキング）でも数字を挙げています。

> Carbon jumps +89 elo points to land at #4 (1768) on WebDev Arena.

前のモデル（Argon）から89ポイント上がって4位、という書き方です。1位から3位のモデルの名前や点数は、この発表ページには書かれていません。

### 安全性：比較できる数字が1つだけある

発表ページの安全性の節には、いくつかの主張があります。ほとんどは比較対象の数字が無いか、「約2倍」という倍率だけで、元の数字が書かれていません。

| 主張 | Carbonの数字 | 比較対象 |
|---|---|---|
| Terminal-Bench 4.0での不正行為 | 成功率**0.0%**（試行は0.4%） | 前のモデルの数字は非公表 |
| Gray SwanのIPIベンチマーク（プロンプトインジェクション耐性） | 攻撃成功率**0.0%** | Argonの0.7%（比較できる） |
| 根拠のない主張（unsupported claims） | Argonより約2倍減少 | 元の%は非公表 |
| セキュアなコード生成の成功率 | Argonより2倍超に向上 | 元の%は非公表 |

出典: すべて発表ページ

<mark>比較できる具体的な数字は、Gray SwanのIPIベンチマークだけです。</mark>発表ページはこう書いています。

> Argon previously led the Gray Swan's Indirect Prompt Injection (IPI) Benchmark with a very low 0.7% attack success rate. Carbon achieves 0.0% — resisting every evaluated attack attempt.

<mark class="warn">残り3つの主張は、「約2倍」「0.0%」という数字だけで、比較のもとになった元の数字（Terminal-Bench 4.0でのArgonの不正行為成功率や、unsupported claimsの元の割合）は発表に書かれていません。</mark>倍率だけを示す書き方では、元の数字が小さいのか大きいのかが読み手には分からないままです。

## 他社の最上位モデルと比べると

### 単価

各社の公式ページから直接取った数字だけを並べます。Carbonはまだ一般提供されていないため、発表ページに書かれた導入価格を使います。

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | キャッシュ済み入力 |
|---|---|---|---|---|
| Gemini 4 Carbon（導入価格） | Google | $2.00 | $10.00 | $0.10（95%引き） |
| Gemini 4 Argon（現在の価格） | Google | $2.00 | $10.00 | $0.10（95%引き） |
| Claude Opus 5.5（Anthropic最上位） | Anthropic | $4.00 | $20.00 | $0.20（5%） |
| GPT-6 Astra（OpenAI最上位・短い入力） | OpenAI | $10.00 | $50.00 | $1.00（90%引き） |

出典: Carbonは発表ページ（前掲）、Argonは <https://ai.google.dev/gemini-api/docs/pricing>、Claude Opus 5.5は <https://platform.claude.com/docs/en/about-claude/pricing>、GPT-6 Astraは <https://developers.openai.com/api/docs/pricing>（いずれも2026年10月29日に確認）

<figure class="figure">
<img src="/static/images/carbon-vendor-price.svg" alt="Gemini 4 Carbon（導入価格・入力2ドル出力10ドル）、Gemini 4 Argon（現在の価格・入力2ドル出力10ドルで同額）、Claude Opus 5.5（入力4ドル出力20ドル）、GPT-6 Astra（短い入力・入力10ドル出力50ドル）を比べた横棒グラフ。100万トークンあたりのドル。Carbonはまだ一部のサイバー防御担当者しか使えない。">
<figcaption>導入価格は安く見えますが、今日から契約できる値段ではありません</figcaption>
</figure>

<mark>Carbonの導入価格は、Anthropic・OpenAIの最上位モデルよりはっきり安く見えます。</mark>Claude Opus 5.5の1/2、GPT-6 Astraの1/5の入力単価です。ただし<mark class="warn">Carbonはまだ誰でも契約できる値段ではありません。</mark>「使えたら安い」であって、「今日から安く使える」ではない点を混同しないでください。

### 仕様

| モデル | コンテキストウィンドウ | 出力の上限 | 知識の締め切り | 提供状況 |
|---|---|---|---|---|
| Gemini 4 Carbon | 公表されていない | 公表されていない | 公表されていない | **一部の限定提供のみ**（サイバー防御担当者・Fairwind Program） |
| Gemini 4 Argon | 1,048,576トークン（入出力を統合） | 65,536（既定）／long decode利用時は最大1,048,576 | 公表されていない | 一般提供（Stable） |
| Claude Opus 5.5 | 1,000,000トークン | 128,000トークン | 2026年6月 | 一般提供 |
| GPT-6 Astra | 1,050,000トークン（入力922,000＋出力128,000） | 128,000トークン | 2026年4月30日 | 一般提供 |

出典: Carbonは発表ページ（前掲）、Argonは <https://ai.google.dev/gemini-api/docs/models/gemini-4-argon>、Claude Opus 5.5は <https://platform.claude.com/docs/en/about-claude/models/overview>、GPT-6 Astraは <https://developers.openai.com/api/docs/models/gpt-6-astra>

<mark class="warn">4モデルの中で、仕様の数字が1つも分かっていないのはCarbonだけです。</mark>コンテキストウィンドウ・出力の上限・知識の締め切りのいずれも、発表ページに記載がありません。Argonの初回発表（出力100万トークンのみ判明）より、さらに情報が少ない状態です。

## どういう人に効くか

**今、関係がある人**

- サイバーセキュリティの防御担当者で、Fairwind Programへの参加資格がある人。脆弱性の発見・修正にCarbonを先行して使えます。
- 米国政府の自主的な事前試験プロセスに関わる立場の人。発表ページがこの取り組みに言及しています。
- 予算を先に立てておきたい人。導入価格（入力$2・出力$10）を基準値として使えます。ただし値上がりの時期は読めません。

**急がなくていい人**

- 今すぐ自分のサービスにCarbonを組み込みたい開発者。公開APIが無いので、組み込みようがありません。
- コンテキストウィンドウや出力の上限で乗り換え先を決めたい人。Carbonはどの仕様も公表されていないため、比較のしようがありません。
- 性能の良さだけで判断したい人。ベンチマークの点数はいずれもGoogle自身の測定で、他社との同条件比較ではありません。

## この記事で分からないこと

- 一般公開（開発者・企業・個人向け）の具体的な時期
- 導入価格が終わる日付
- コンテキストウィンドウ・出力の上限・学習データの知識の締め切り
- Terminal-Bench 4.0での不正行為成功率や「unsupported claims」の割合について、Argon側の元の数字（Carbonの発表は倍率だけを示している）
- 実際に使ったときの体感、日本語での品質

どれも発表ページに数字がなく、運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 4 Carbon の発表（Google・2026年10月28日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-carbon/>
   （Google DeepMind 側の <https://deepmind.google/blog/gemini-4-carbon-our-next-frontier-model/> を開くと、このページへ転送されます）
2. Gemini 4 Argon の公式モデルページ（Google公式）: <https://ai.google.dev/gemini-api/docs/models/gemini-4-argon>
3. Gemini API の料金（Google公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. 料金（Anthropic公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
5. モデル一覧と仕様（Anthropic公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>
6. APIの料金（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
7. GPT-6 Astraのモデルページ（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-6-astra>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
