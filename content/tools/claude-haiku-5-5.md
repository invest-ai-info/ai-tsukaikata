---
title: Haiku 5.5はLunaと単価一致——複雑な自動コーディングはSonnet任せ
description: 2026年10月7日に出た Claude Haiku 5.5 について、Anthropic・OpenAI・Google の公式ページに書かれている数字だけをまとめました。10万トークン以下の単価はHaiku 4.5よりどれも90%下がり、OpenAIの同じ価格帯のモデル（GPT-6 Luna）と単価が完全一致します。性能も上がっていますが、複雑な自動コーディングの差はまだ大きいままです。
category: tools
scene: choose
published: 2026-10-08
checked: 2026-10-08
tags: [Claude, モデル比較, 料金, AI最新情報]
---

## 結論：使い方ごとに、こうなります

Anthropic は 2026年10月7日に **Claude Haiku 5.5** を出しました（出典: <https://www.anthropic.com/claude-haiku-5-5>）。公式は「もっとも安く、もっとも速く、もっとも賢い Haiku」と説明しています。使い方で結果が分かれます。

| どんな使い方か | やること | どうなるか |
|---|---|---|
| **要約・分類・DB検索など、早くて単純な作業をAPIでさせている** | Haiku 5.5に替える（`claude-haiku-5-5`） | 公式の説明で平均**約75%**安くなる |
| **すでにHaiku 4.5を使っている（特別な設定なし）** | モデル名を替えるだけ | 10万トークン以下の単価はどれも**90%減**。性能もHaiku 4.5を全項目で上回る |
| **「考える」を手動指定・温度指定・古いパソコン操作の道具を使っている** | **先に設定を直してから**替える | 直さずに替えると**エラーで止まる**（該当する設定が4つある） |
| **Sonnet/Opusで複雑な自動コーディングをさせている** | Haikuには替えない | Terminal-Bench 4.0でHaiku 5.5は39.2%、Sonnet 5.5は70.6%。複雑な仕事はまだ上位モデルが要る |

一言でいうと、<mark>値段は最大90%下がり、Haiku 4.5より確実に賢くなった。ただし複雑な自動コーディングの差は、まだ大きい</mark>。

先に断っておきます。**この記事は運営者が Haiku 5.5 を試した記録ではありません。**公式ページに書かれていることを読んで、使い方ごとに整理したものです。

ここから下は、表の4行がなぜそうなるのかの説明です。

## なぜそうなるのか

### 単価が最大90%下がる理由

公式のモデルのページには、prompt の長さで分かれた2つの階層が書かれています（出典: <https://platform.claude.com/docs/en/models/haiku-5-5/overview>）。

| 100万トークンあたり | Haiku 4.5 | Haiku 5.5（10万トークン以下） | Haiku 5.5（10万トークン超） |
|---|---|---|---|
| 入力 | $1.00 | **$0.10**（90%減） | $0.50（50%減） |
| 出力 | $5.00 | **$0.50**（90%減） | $2.50（50%減） |
| 読み直し（キャッシュ読み取り） | $0.10 | **$0.01**（90%減） | $0.05（50%減） |
| キャッシュ書き込み（5分） | $1.25 | **$0.125**（90%減） | $0.625（50%減） |

出典: <https://platform.claude.com/docs/en/models/haiku-5-5/overview> と <https://platform.claude.com/docs/en/models/haiku-4-5/overview>

<figure class="figure">
<img src="/static/images/haiku55-price-vs-prev.svg" alt="Claude Haiku 4.5 から Haiku 5.5 への単価の変化を示す横棒グラフ（prompt 10万トークン以下）。100万トークンあたりのドル。薄い灰＝Haiku 4.5、濃い青＝Haiku 5.5。入力は1.00ドルから0.10ドルへ90%減、出力は5.00ドルから0.50ドルへ90%減、読み直し（キャッシュ読み取り）は0.10ドルから0.01ドルへ90%減、キャッシュ書き込み（5分）は1.25ドルから0.125ドルへ90%減。10万トークンを超える分の下げ幅は50%で、これより小さい。">
<figcaption>どの項目も10万トークン以下は正確に90%減です</figcaption>
</figure>

公式自身は「平均で約75%安い」と書いています（出典: <https://www.anthropic.com/claude-haiku-5-5>）。90%より低いのには理由があります。<mark class="warn">Haiku 5.5はHaiku 4.5より新しいトークンの数え方を使っていて、同じ文章がおよそ30%多いトークン数になります</mark>（出典: <https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5>）。単価そのものは90%下がっても、1つの仕事に使うトークン数が増えるぶん、実際の下げ幅は75%に落ち着く、という計算です。

もう1つ注記があります。公式は「Haiku 4.5への依頼の90%は、もともと10万トークン以下に収まっていた」と説明しています（出典: <https://www.anthropic.com/claude-haiku-5-5>）。だから<mark>多くの利用者にとって、実際に効くのは90%減のほう</mark>です。

### 性能そのものもHaiku 4.5より上がっている

公式発表のベンチマーク表から、3モデルとも値がある項目だけを抜き出しました（最大の設定 max の点数）。

| 何のテストか | 分野 | Haiku 4.5 | GPT-6 Luna | Haiku 5.5 |
|---|---|---|---|---|
| OSWorld 2.1（オフライン subset） | パソコン操作 | 15.7% | 48.9% | 72.4% |
| Terminal-Bench 4.0 | 自動作業 | 0.0% | 16.4% | 39.2% |
| Chartography（道具なし） | 図表の読み取り | 6.4% | 29.1% | 46.4% |
| GDPval-AA v2.1 | 事務の仕事（44職種・点） | 735 | 1437 | 1620 |
| AA-Briefcase v1.1 | 知識労働（点） | 614 | 1336 | 1578 |
| FrontierCode 1.1（Main） | 自動コーディング | 公表なし | 42.4% | 46.4% |

出典: すべて <https://www.anthropic.com/claude-haiku-5-5>

<figure class="figure">
<img src="/static/images/haiku55-bench.svg" alt="Haiku 4.5・GPT-6 Luna・Haiku 5.5 の点数を比べた横棒グラフ。OSWorld 2.1（オフラインsubset）はHaiku 4.5が15.7％、GPT-6 Lunaが48.9％、Haiku 5.5が72.4％。Terminal-Bench 4.0はHaiku 4.5が0.0％、GPT-6 Lunaが16.4％、Haiku 5.5が39.2％。Chartography（道具なし）はHaiku 4.5が6.4％、GPT-6 Lunaが29.1％、Haiku 5.5が46.4％。いずれもHaiku 5.5が最大の設定（max）で3モデル中もっとも高い。">
<figcaption>値がある項目はすべて、Haiku 5.5が3モデル中もっとも高い</figcaption>
</figure>

<mark>値がある6項目すべてで、Haiku 5.5はHaiku 4.5とGPT-6 Lunaの両方を上回っています</mark>。ただし注意が2つあります。Humanity's Last Exam は GPT-6 Luna の値が「—」（未測定扱い）だったため表から外しました。また<mark class="warn">点数は公式発表の最大設定（max）のもので、既定設定（medium）で使うとこの点数にはなりません</mark>（出典: 同上）。

### 初めて「考える量」を選べるようになった

公式は「Haiku 5.5は、調整できる考える量（effort）を持つ初めてのHaikuクラスのモデル」と説明しています（出典: <https://www.anthropic.com/claude-haiku-5-5>）。発表ページのグラフから、OSWorldとGDPval-AAでの効果（点数と費用）を抜き出しました。

| 設定 | OSWorld 2.1（点数・費用） | GDPval-AA v2.1（点数・費用） |
|---|---|---|
| Low | 42.0% / $0.07 | 1125 / $0.01 |
| Med | 53.3% / $0.13 | 1277 / $0.03 |
| High | 61.3% / $0.18 | 1420 / $0.09 |
| Xhigh | 67.6% / $0.28 | 1513 / $0.27 |
| Max | 72.4% / $0.61 | 1620 / $0.87 |
| Haiku 4.5（Max） | 15.7% / $1.45 | 735 / $0.24 |

出典: すべて <https://www.anthropic.com/claude-haiku-5-5>（1タスクあたりの費用。発表ページのグラフに埋め込まれた数値から書き写した）

<mark>Haiku 5.5の一番安い設定（Low・1タスク$0.07）は、Haiku 4.5の最大設定（Max・1タスク$1.45）より安いうえに正確です</mark>（OSWorldで42.0%対15.7%）。GDPval-AAでも同じ形で、Lowの1125点・$0.01がHaiku 4.5のMax・735点・$0.24を上回ります。既定の設定は medium です（出典: <https://platform.claude.com/docs/en/models/haiku-5-5/overview>）。

### 乗り換えると止まる設定が4つある

公式の「What's new」ページには、Haiku 4.5からの変更点がまとめられています。そのうち**4つは「Breaking」（エラーで止まる）**と明記されています（出典: <https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5>）。

| 設定 | Haiku 4.5 | Haiku 5.5 |
|---|---|---|
| 「考える」を手動で指定（`budget_tokens`） | できる | **エラー**（`effort` に置き換える） |
| `temperature` / `top_p` / `top_k` の既定値以外の指定 | できる | **エラー**（指定を外す） |
| アシスタントの発言で文章を続ける指定（prefill） | できる | **エラー**（ユーザーの発言で終える） |
| パソコン操作の古い道具（`computer_20250124`） | 使える | Claude APIとGoogle Cloudでは**エラー**（`computer_toolset_20260801` に替える） |

<mark class="warn">モデル名だけ書き換えて乗り換えると、上の4つの設定を使っている自動化はその場で止まります</mark>。

エラーにはならないけれど、気づきにくい変化も3つあります（出典: 同上）。

- 安全装置が依頼を拒否するとき、`stop_reason` が `"refusal"` になる。クライアント側で受け止める処理が要る
- 「考える」内容のテキストは既定では表示されない。見るには `thinking.display` を `"summarized"` にする
- 「考える」内容を別のアカウントで再生すると無効になる。生成した側のアカウントで再生する

### 複雑な自動コーディングはまだ上位モデルが要る

公式は「Sonnet 5.5とOpus 5.5は、Terminal-Bench 4.0のような複雑な自動コーディングの作業では、依然として良い選択です。対照的に、Haiku 5.5はコンパクション・要約・サブエージェント作業のような、より狭い範囲の作業に向いています」と明記しています（出典: 同上）。

| | Haiku 5.5 | Sonnet 5.5 |
|---|---|---|
| Terminal-Bench 4.0 | 39.2% | 70.6% |

出典: <https://www.anthropic.com/claude-haiku-5-5>

<mark>公式自身が、複雑な自動コーディングにはHaikuを使わないよう線を引いています</mark>。この表の差（31.4ポイント）がその根拠です。

### 読める量・書ける量・知識の締め切りも変わった

| | Haiku 4.5 | Haiku 5.5 |
|---|---|---|
| 一度に読める量 | 20万トークン | **100万トークン**（5倍） |
| 一度に書ける量 | 6.4万トークン | **12.8万トークン**（2倍。Message Batches APIのベータでは30万トークンまで） |
| 学習データの締め切り | 2025年7月 | 2026年6月 |
| 安定して正しいと言える知識の締め切り | 2025年2月 | 2026年6月 |

出典: <https://platform.claude.com/docs/en/models/haiku-5-5/overview>、<https://platform.claude.com/docs/en/models/haiku-4-5/overview>、
Batchのベータは <https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta>

### 同時に発表された2つのおまけ

Haiku 5.5 と同時に、Anthropic は2つの変更を発表しました（出典: <https://www.anthropic.com/claude-haiku-5-5>）。

1. **Claude Sonnet 5.5のキャッシュ読み取りが半額に。**$0.20→**$0.10**（100万トークンあたり）。公式は「自動で長く作業させる使い方の費用を、約20%下げる」と説明しています
2. **Claude MaxとTeamに、月ごとのAPIクレジットが追加される。**Max 5xは$100、Max 20xは$200、Teamは席をまとめて最大$500。公式は「今週中」に展開すると書いていますが、具体的な日付は書かれていません

## 他社の最上位モデルと比べると

### 単価

各社の公式料金ページから直接取った数字だけを並べます。安い系のモデルと、各社の最上位モデルは値の大きさが大きく違うため、表を分けます。

| 安い系モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） |
|---|---|---|---|
| Claude Haiku 5.5（10万トークン以下） | Anthropic | $0.10 | $0.50 |
| GPT-6 Luna | OpenAI | $0.10 | $0.50 |
| Gemini 3.5 Flash-Lite | Google | $0.30 | $2.50 |

出典: Claude は <https://platform.claude.com/docs/en/models/haiku-5-5/overview>、GPT は <https://developers.openai.com/api/docs/pricing>、Gemini は <https://ai.google.dev/gemini-api/docs/pricing>

🔍 Claude Haiku 5.5 と GPT-6 Luna は、入力・出力の単価が一致するだけではありません。<mark>読み直し（$0.01）とキャッシュ書き込み（$0.125）まで含めて、4つの単価すべてが完全に一致しています</mark>（出典: 同上）。

| 各社の最上位モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） |
|---|---|---|---|
| Claude Opus 5.5 | Anthropic | $4.00 | $20.00 |
| GPT-6 Astra | OpenAI | $10.00（短い入力） | $50.00（短い入力） |
| Gemini 3.1 Pro Preview | Google | $2.00（20万トークン以下） | $12.00（20万トークン以下） |

出典: Claude は <https://platform.claude.com/docs/en/about-claude/pricing>、GPT は <https://developers.openai.com/api/docs/pricing>、Gemini は <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/haiku55-vendor-price.svg" alt="安い系モデルと各社の最上位モデルの単価を比べた横棒グラフ。100万トークンあたりのドル。上下で目盛りの縮尺が違う。安い系モデル＝Claude Haiku 5.5は入力0.10ドル・出力0.50ドル、GPT-6 Lunaは入力0.10ドル・出力0.50ドルで両方の4つの単価が完全一致、Gemini 3.5 Flash-Liteは入力0.30ドル・出力2.50ドル。各社の最上位モデル＝Claude Opus 5.5は入力4.00ドル・出力20.00ドル、GPT-6 Astraは入力10.00ドル・出力50.00ドル、Gemini 3.1 Pro Previewは入力2.00ドル・出力12.00ドル（いずれも短い入力のときの値段）。">
<figcaption>Haikuの出力単価は、自社の最上位モデル（Opus 5.5）の1/40、GPT-6 Astraの1/100です</figcaption>
</figure>

<mark class="warn">出力の単価だけで比べると、Haiku 5.5はAnthropic自身の最上位モデル（Opus 5.5）の1/40、OpenAIの最上位モデル（GPT-6 Astra）の1/100です</mark>（$0.50に対し$20.00・$50.00。この倍率は各社の公式料金ページの数字からこの記事が計算した）。<mark>単価が安い＝支払いが安い、ではありません</mark>。会社ごとにトークンの数え方が違ううえ、GPT と Gemini は入力が長くなると単価が上がります（OpenAIは「短い」「長い」の境目を料金ページに書いていません。Googleは「20万トークンを超えたら」と明記しています）。Gemini 3.1 Pro は試用版（Preview）の表示で、長く使う前提なら値段が変わりうると考えてください。

### 性能

GPT-6 Lunaとの性能比較は、上の「性能そのものもHaiku 4.5より上がっている」の表がそのまま使えます。<mark>値がある6項目すべてで、Haiku 5.5がGPT-6 Lunaを上回っています</mark>。GPT-6 AstraやGemini 3.1 Proとの性能比較は、Haiku 5.5の発表ページに値が載っていないため「公表されていない」とします。

## どういう人に効くか

**いま動かすといい人**

- 要約・分類・ルーティング・DB検索・サブエージェント作業をAPIでさせている人。公式がそのまま挙げている想定用途です
- すでにHaiku 4.5を使っている人。単価が下がり性能も上がっているので、乗り換えを控える理由が見当たりません（下の「設定を先に直す人」は例外）
- Claude MaxやTeamを契約していて、自分でAPIを使ったツールを作ってみたい人。月ごとのクレジットが新しく付きます

**先に設定を直す人**

- 次のどれかに当たる人は、**先に設定を直してから**乗り換えてください
  - 「考える」を`budget_tokens`で手動指定している
  - `temperature`等を既定値以外にしている
  - アシスタントの発言で文章を続けている（prefill）
  - 古いパソコン操作の道具（`computer_20250124`）を使っている

**急がなくていい人**

- Sonnet やOpus で複雑な自動コーディングをさせている人。Terminal-Bench 4.0でHaiku 5.5はSonnet 5.5の約半分の点数です
- 他社の最上位モデル（GPT-6 Astra・Gemini 3.1 Pro）と性能で比べたい人。Haiku 5.5の発表ページに、その比較の数字が載っていません

## この記事で分からないこと

- 実際に使ったときの体感
- 日本語での文章の品質
- 新しい月次APIクレジットの提供開始が具体的にいつか（公式は「今週中」としか書いていません）
- GPT-6 AstraやGemini 3.1 Proとの性能の直接比較（Haiku 5.5の発表ページに値がありません）

どれも公式ページに数字がなく、運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Claude Haiku 5.5 の発表（Anthropic・2026年10月7日）: <https://www.anthropic.com/claude-haiku-5-5>
2. Claude Haiku 5.5 のモデルのページ（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/haiku-5-5/overview>
3. What's new in Claude Haiku 5.5（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/haiku-5-5/whats-new-haiku-5-5>
4. Claude Haiku 4.5 のモデルのページ（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/haiku-4-5/overview>
5. Message Batches API（出力拡張のベータ）（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/build-with-claude/batch-processing#extended-output-beta>
6. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
7. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
8. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
