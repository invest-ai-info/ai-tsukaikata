---
title: 出力100万トークンのArgon——使えるのは一部の人だけ
description: 2026年9月30日に発表された Gemini 4 Argon について、Google の発表ページ・公式モデルページ・料金ページに書かれている数字だけを並べました。出力の上限は前のモデルの約15.3倍に広がりましたが、一般には公開されておらず、使えるのは一部のセキュリティ関係者とGoogle社内だけです。
category: tools
scene: choose
published: 2026-10-01
checked: 2026-10-01
tags: [Gemini, モデル比較, 料金, AI最新情報]
---

## 結論：今の立場ごとに、こうなります

Google は 2026年9月30日に、次の主力モデル **Gemini 4 Argon** を発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/>）。ただし、この記事でいちばん先に書いておきたいのは性能の数字ではありません。**今日の時点で、一般の開発者はこのモデルを使えません。**

| 今の立場 | 今できること | どうなるか |
|---|---|---|
| **今すぐ試したい開発者・会社員** | 公開APIが無いので試せない | Fairwind Program経由の信頼されたセキュリティ関係者と、Google社内だけが使える。一般公開は「できるだけ早く」としか書かれていない |
| **Gemini 3.1 Pro Preview を使っている人** | そのまま使い続ける | Argonは出力の上限が前のモデルの**約15.3倍**に広がるが、使えるようになる時期は未定 |
| **将来の予算を先に見ておきたい人** | 導入価格（入力$2・出力$10）を基準に試算する | 導入期間が終わると入力$4・出力$20に上がる。**ただし終わる日付は発表に書かれていない** |

<mark>一言でいうと、出力の器は大きく広がったが、今日の時点では誰も自由には使えません。</mark>

先に断っておきます。**この記事は運営者がArgonを試した記録ではありません。**公式の発表ページ・モデルページ・料金ページに書かれている数字だけを読んで整理したものです。

ここから下は、表の3行がなぜそうなるのかの説明です。

## なぜそうなるのか

### まだ使えない理由

発表ページには、Argonの提供範囲がはっきり書かれています（出典: 同上）。

> Argon is currently rolling out to trusted cyber defenders through the Fairwind Program.
>（Argonは現在、Fairwind Programを通じて信頼されたサイバー防御の担当者に展開されています）

<mark class="warn">一般の開発者・企業・個人向けの提供は、まだ始まっていません</mark>。発表ページは「開発者・企業・一般利用者への提供は、できるだけ早く行う」と書くにとどめ、具体的な日付は示していません（出典: 同上）。社内では「数千人のGoogle社員」がすでに使っていると書かれていますが、これはGoogle自身の業務での利用であって、外部から使える状態ではありません。

<mark>この「限定公開→時期未定で一般公開」という流れは、今回が初めてではありません</mark>。2026年9月6日公開の **Gemini 3.8 Flash Cyber**（サイバーセキュリティ専用モデル）も同じです。Fairwind Program経由の限定提供のまま、一般の料金ページには載っていません（この記事を書いた時点で確認）。3.8 Flash Cyber の発表そのものは[Gemini 3.8 Flashは値段そのまま](/tools/gemini-3-8-flash/)で扱っています。Argonはこの枠組みを、主力モデル本体にまで広げた形です。

セキュリティ分野での実例として、発表ページは **Wiz** の「Scan for Good」（重要インフラを無償で守る取り組み）でArgonがすでに使われていると説明しています。ある実演では、世界中の病院で使われている医療ソフトウェアから重大な脆弱性を発見。以前の最先端モデルが見逃していたものだったと書かれています（出典: 同上）。信頼された防御担当者とGoogle社内チームには「サイバー用の安全装置を外した」状態で提供するとも書かれており、一般提供時とは中身が違う可能性があります。

### 出力の上限が15.3倍に広がった理由

発表ページが明記する、唯一の確定した仕様変更がこれです。

<mark>Argonは出力トークンの上限を「業界最高水準の100万トークン」に広げたと公式が説明しています。前のモデルは6.4万トークンでした</mark>（出典: 同上）。前のモデルの正確な値は、Gemini API公式モデルページで **65,536トークン**と確認できます（出典: <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview>）。

<figure class="figure">
<img src="/static/images/argon-output-limit.svg" alt="Gemini 4 Argonの出力トークン上限を、前のモデルGemini 3.1 Pro Previewと比べた横棒グラフ。Gemini 3.1 Pro Previewは65,536トークン、Gemini 4 Argonは1,000,000トークンで、約15.3倍に広がった（この記事の計算）。出力トークン上限が増えても、入力側の上限が同じとは限らない（Argonの入力上限は発表に記載がなく未公表）。">
<figcaption>出力の器が、前のモデルの約15.3倍に広がりました</figcaption>
</figure>

1,000,000 ÷ 65,536 を計算すると、約15.3倍です（この記事の計算。発表ページに倍率の記載はありません）。公式は「モデルが深く考え、多くのトークンを生成できる余裕ができた」と説明しています。その結果、難しい問題を一気に解ける水準の推論が可能になったとしています（出典: 同上）。

<mark class="warn">ここで注意が要ります。公式が明言しているのは出力側の上限だけで、入力側（一度に読み込める量）については発表に記載がありません。</mark>前のモデル（3.1 Pro Preview）の入力上限は1,048,576トークンです。Argonがこれと同じなのか、それとも変わったのかは、この記事を書いた時点で公表されていません。推測では書かず「公表されていない」とだけ書いておきます。

### 価格はもう決まっている（でも使えない）

使えないのに、価格はすでに発表されています。

| | 入力（100万トークンあたり） | 出力（100万トークンあたり） | 備考 |
|---|---|---|---|
| Argon（導入価格） | $2.00 | $10.00 | キャッシュ済み入力は入力価格の**95%引き**（$0.10） |
| Argon（導入期間終了後） | $4.00 | $20.00 | **終了する時期は発表に書かれていない** |

出典: 発表ページ本文と脚注1（<https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/>）

<mark class="warn">他の新モデル（Gemini 3.7 Flashや3.8 Flashなど）は「2026年12月31日まで」と導入価格の期限を明記していました。Argonの発表にはその日付がありません。</mark>いつ値上がりするか分からないまま、価格だけが先に決まっている状態です。

前のモデル（Gemini 3.1 Pro Preview）は、プロンプトの長さで価格が2段階に分かれています。

| | 入力 | 出力 | キャッシュ済み入力 |
|---|---|---|---|
| 3.1 Pro（20万トークン以下） | $2.00 | $12.00 | $0.20（入力価格の90%引き） |
| 3.1 Pro（20万トークン超過時） | $4.00 | $18.00 | $0.40 |

出典: Gemini API 公式料金ページ（<https://ai.google.dev/gemini-api/docs/pricing>）

<figure class="figure">
<img src="/static/images/argon-price-tiers.svg" alt="Gemini 4 Argonの導入価格と導入後、前のモデルGemini 3.1 Proの2段階の単価を比べた横棒グラフ。100万トークンあたりのドル。Argon（導入価格）は入力2ドル・出力10ドル、Argon（導入後）は入力4ドル・出力20ドル、3.1 Pro（20万トークン以下）は入力2ドル・出力12ドル、3.1 Pro（20万トークン超過時）は入力4ドル・出力18ドル。Argonの導入価格が終わる時期は発表に書かれていない。キャッシュ済み入力はArgonが入力価格の95%引き、3.1 Proは90%引き。">
<figcaption>Argonの導入価格は、3.1 Proの「短いプロンプト」の値段とほぼ同じです</figcaption>
</figure>

<mark>Argonの導入価格（入力$2・出力$10）は、3.1 Proの短いプロンプト向け価格（入力$2・出力$12）とほぼ同額で、出力はむしろ$2安くなっています</mark>。ただし導入期間が終わると入力$4・出力$20になり、3.1 Proの長いプロンプト向け価格（入力$4・出力$18）より出力が$2高くなります。**ふたつの軸（期間と文脈の長さ）は別物なので、単純に「安くなった」「高くなった」とは言い切れません。**

キャッシュの割引率も変わりました。Argonはキャッシュ済み入力が入力価格の**95%引き**と発表ページに明記されています。3.1 Proの料金ページには「引き」という言葉はありません。$2.00→$0.20という実額だけが書かれているため、**90%引きはこの記事の計算**（$0.20÷$2.00）です。同じ会話を何度も読み返す使い方では、Argonのほうが割引が深くなります。

### 性能はどう謳われているか（自社測定だけ）

発表ページは、4つのベンチマークで新記録や1位を主張しています。

| ベンチマーク | 何を測るか | 点数 |
|---|---|---|
| DeepSWE v1.1 | 長時間のソフト開発作業 | **77.9%**（新記録） |
| LVBench | 長い動画の理解 | **91.7%**（新記録） |
| CWE-bench v1 | セキュリティ脆弱性の修復 | **68%**（同率1位） |
| AutomationBench（Zapier運営） | 業務自動化の実行力 | **51.3%**（1位） |

出典: すべて発表ページ（<https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/>）

<figure class="figure">
<img src="/static/images/argon-benchmarks.svg" alt="Gemini 4 Argonの発表ページが挙げた点数4つを並べた横棒グラフ。DeepSWE v1.1（長時間のソフト開発作業）は77.9%で新記録、LVBench（長い動画の理解）は91.7%で新記録、CWE-bench v1（セキュリティ脆弱性の修復）は68%で同率1位、AutomationBench（Zapier運営・業務自動化の実行力）は51.3%で1位。いずれもGoogle自身の測定で、他社モデルを同じ条件で測った数字は発表に無い。">
<figcaption>どれもGoogle自身の測定です。他社の同条件の点数は発表にありません</figcaption>
</figure>

このサイトの方針として、<mark>性能テストの点数は、各社が自社で測っていて測り方も対象も違うため、他社モデルと横に並べません</mark>。公式の数字で言い切れるのは単価の並びまでです。この4項目についても、「Googleがそう主張している」という事実だけを書いておきます。

CWE-bench v1については、発表ページに興味深い一文があります。「3.8 Flash Cyberが築いたCWE-bench v0での最先端の性能の上に、Argonは積み上げた」という趣旨の記述です（出典: 同上）。ただし**3.8 Flash CyberがCWE-bench v0で具体的に何点だったかは、この発表ページに書かれていません。**比較できる数字が無いので、この記事ではそのまま「書かれていない」としておきます。

発表ページは、Google社内での活用例もいくつか挙げています。これらも第三者の検証ではなく、Google自身の説明です。

- **量子コンピューティング**: Argonが量子アルゴリズムの最適化で、公開済みの基準値を数分で**40%上回った**という例
- **メモリ最適化**: Argonのエージェントがデータセンター全体のメモリを分析して最適化を適用。展開後に**300TiB超**を解放し、最終的には500TiB〜1PiBの節約を見込む
- **コード移植**: C/C++からRustへの大規模移植の例。動画デコーダー「libgav1」の既存Rust版を、32,000行のSIMDコードごと書き換え、**2.7倍速い**（出力は同一）コードを生成した

## 他社の最上位モデルと比べると

### 単価

各社の公式ページから直接取った数字だけを並べます。Argonはまだ一般提供されていないため、発表ページに書かれた導入価格を使います。

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | キャッシュ済み入力 |
|---|---|---|---|---|
| Gemini 4 Argon（導入価格） | Google | $2.00 | $10.00 | $0.10（95%引き） |
| Gemini 3.1 Pro Preview（前のモデル） | Google | $2.00（20万トークン以下） | $12.00（20万トークン以下） | $0.20（90%引き） |
| Claude Opus 5.5（Anthropic最上位） | Anthropic | $4.00 | $20.00 | $0.20（5%） |
| GPT-6 Astra（OpenAI最上位） | OpenAI | $10.00 | $50.00 | $1.00（90%引き） |

出典: Argonは発表ページ（前掲）、Gemini 3.1 Proは <https://ai.google.dev/gemini-api/docs/pricing>、Claude Opus 5.5は <https://platform.claude.com/docs/en/about-claude/pricing>、GPT-6 Astraは <https://developers.openai.com/api/docs/pricing>（いずれも2026年10月1日に確認）

<figure class="figure">
<img src="/static/images/argon-vendor-price.svg" alt="Gemini 4 Argon（導入価格）と各社の現時点の最上位モデルの単価を比べた横棒グラフ。100万トークンあたりのドル。Gemini 4 Argon（導入価格）は入力2ドル・出力10ドル、前のモデルGemini 3.1 Pro Previewは入力2ドル・出力12ドル、Claude Opus 5.5（Anthropic最上位）は入力4ドル・出力20ドル、GPT-6 Astra（OpenAI最上位）は入力10ドル・出力50ドル。Argonはまだ一般提供されておらず導入価格の値。会社ごとにトークンの数え方が違うため、単価の安さは支払額の安さを意味しない。">
<figcaption>Argonの導入価格は、他社の最上位モデルよりかなり安く見えます</figcaption>
</figure>

<mark>Argonの導入価格は、Anthropic・OpenAIの最上位モデルよりはっきり安く見えます。</mark>Claude Opus 5.5の1/2、GPT-6 Astraの1/5の入力単価です。ただし<mark class="warn">Argonはまだ誰でも契約できる値段ではありません。</mark>「使えたら安い」であって、「今日から安く使える」ではない点を混同しないでください。

### 仕様

| モデル | 入力の上限 | 出力の上限 | 知識の締め切り | 提供状況 |
|---|---|---|---|---|
| Gemini 4 Argon | 公表されていない | 1,000,000トークン | 公表されていない | **一部の限定提供のみ**（Fairwind Program・Google社内） |
| Gemini 3.1 Pro Preview | 1,048,576トークン | 65,536トークン | 公表されていない | Preview（Gemini API・アプリ等で利用可） |
| Claude Opus 5.5 | 1,000,000トークン | 128,000トークン | 2026年6月 | 一般提供 |
| GPT-6 Astra | 1,050,000トークン | 128,000トークン | 2026年4月30日 | 一般提供 |

出典: Argonは発表ページ（前掲）、Gemini 3.1 Proは <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview>、Claude Opus 5.5は <https://platform.claude.com/docs/en/about-claude/models/overview>、GPT-6 Astraは <https://developers.openai.com/api/docs/models/gpt-6-astra>

<mark class="warn">4モデルの中で、提供状況が「限定のみ」なのはArgonだけです。</mark>入力の上限と知識の締め切りも、Argonだけ発表に記載がありません。出力の上限（100万トークン）だけが、唯一はっきり分かっている仕様です。

## どういう人に効くか

**今、関係がある人**

- サイバーセキュリティの防御担当者で、Fairwind Programへの参加資格がある人。脆弱性の発見・修正にArgonを先行して使えます。
- Google Cloud・Gemini Enterpriseの契約で、社内の業務効率化の動向を追っている人。「Google社員数千人が実際に使っている」という社内実績が、今後の機能追加の手がかりになります。
- 予算を先に立てておきたい人。導入価格（入力$2・出力$10）を基準値として使えます。ただし値上がりの時期は読めません。

**急がなくていい人**

- 今すぐ自分のサービスにArgonを組み込みたい開発者。公開APIが無いので、組み込みようがありません。
- 入力コンテキストの長さで乗り換え先を決めたい人。Argonの入力上限は公表されていないため、比較のしようがありません。
- 性能の良さだけで判断したい人。4つの点数はいずれもGoogle自身の測定で、他社との同条件比較ではありません。

## この記事で分からないこと

- 一般公開（開発者・企業・個人向け）の具体的な時期
- 導入価格が終わる日付
- 入力トークンの上限（一度に読み込める量）
- 学習データの知識の締め切り
- 実際に使ったときの体感、日本語での品質

どれも発表ページ・公式モデルページに数字がなく、運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 4 Argon の発表（Google・2026年9月30日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/>
   （Google DeepMind 側の <https://deepmind.google/blog/gemini-4-argon-our-next-era-of-frontier-intelligence/> を開くと、このページへ転送されます）
2. Gemini 3.1 Pro Preview のモデルページ（Google 公式）: <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview>
3. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. Gemini 3.1 Pro の紹介ページ（Google DeepMind 公式）: <https://deepmind.google/models/gemini/pro/>
5. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
6. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>
7. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
8. GPT-6 Astra のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-6-astra>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
