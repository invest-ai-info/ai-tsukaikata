---
title: Claude Fable 5.1 は同じ作業が約25%安くなる——単価は据え置きで、下がったのは1項目だけ
description: 2026年9月1日に発表された Claude Fable 5.1 について、Anthropic の発表ページ・料金ページ・モデル一覧に書かれている数字だけを並べました。安くなる理由は「キャッシュ読み取り」1項目の値下げで、入力・出力の単価は Fable 5 と同じです。他社の最上位モデルの単価は、各社の公式料金ページで突き合わせています。
category: tools
scene: choose
published: 2026-09-02
checked: 2026-09-02
tags: [Claude, モデル比較, 料金, AI最新情報]
---

## 何が変わったか

Anthropic は 2026年9月1日に **Claude Fable 5.1** と **Claude Mythos 5.1** を発表しました（出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- 単価は Fable 5 と同じで、入力100万トークンあたり **$10**、出力 **$50** です。<mark>値下げされたのは「キャッシュ読み取り」の1項目だけで、$1 から $0.25 になりました</mark>（出典: <https://docs.claude.com/en/docs/about-claude/pricing>）。
- それでも公式は、<mark>ふつうの使い方で費用が約25%、長く自動で作業させる使い方では最大で約45%下がる</mark>と説明しています（出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>）。
- 公式が挙げた性能テストは7種類すべてで Fable 5 を上回っています。例＝Terminal-Bench 4.0 が 42.0% から 55.8%、AutomationBench が 17.1% から 31.4%（出典: 同上）。

先に断っておきます。**この記事は運営者が Fable 5.1 を試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「速かった」「賢くなった」といった使用感は一切書いていません。

Fable 5.1 と Mythos 5.1 は同じモデルで、違いは安全装置の強さだけです。Mythos 5.1 は審査を通った組織にしか提供されません（出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>）。この記事は、誰でも使える Fable 5.1 のほうを中心に書きます。1つ下のモデルの話は [Claude Opus 5 は何が変わったのか](/tools/claude-opus-5/) に書いています。

## 「25%安い」の中身

ここが一番、読み違えやすいところです。入力も出力も、単価は下がっていません。下がったのは「キャッシュ読み取り」という1項目です。

**キャッシュ読み取りとは何か。**AIに長い資料を読ませて質問すると、2つ目の質問のときも、AIは資料を最初から読み直します。この「一度読んだものをもう一度読む」ぶんを安くする仕組みがキャッシュで、その読み直しの料金が「キャッシュ読み取り」です。会話が長くなるほど、費用の大半がこの読み直しになります。

| 項目（100万トークンあたり） | Claude Fable 5 | Claude Fable 5.1 |
|---|---|---|
| 入力 | $10 | $10 |
| 出力 | $50 | $50 |
| キャッシュ書き込み（5分） | $12.50 | $12.50 |
| キャッシュ書き込み（1時間） | $20 | $20 |
| **キャッシュ読み取り** | $1 | **$0.25** |
| まとめ処理（Batch）の入力 / 出力 | $5 / $25 | $5 / $25 |

出典: すべて <https://docs.claude.com/en/docs/about-claude/pricing>

<figure class="figure">
<img src="/static/images/fable51-price-grid.svg" alt="Fable 5 から Fable 5.1 への単価の変化を2列で比べた図。100万トークンあたり。変わらないもの＝入力10ドル、出力50ドル、キャッシュ書き込みは5分が12.50ドル・1時間が20ドル、まとめ処理は入力5ドル・出力25ドル、読める量100万トークン、書ける量12.8万トークン。変わったもの＝キャッシュ読み取りが1ドルから0.25ドルへ75%減、学習データの締め切りが2026年6月、セキュリティ系の安全装置の誤検知が約60%減、初歩的な生物・医療の質問での誤検知が85%減。">
<figcaption>据え置きのものと、変わったもの</figcaption>
</figure>

公式の説明では、費用の下がり幅は使い方で変わります。<mark>ふつうの使い方で約25%、資料や道具を大量に読ませて長く自動で作業させる使い方で最大約45%です</mark>（出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>）。この比率は、Anthropic が 2026年8月の4週間の実際の利用を集計して出したもので、Claude Enterprise・Claude Code・API の利用がまとめて入っています（出典: 同上）。

<mark class="warn">短い質問を1回ずつ投げる使い方では、読み直しがほとんど発生しないので、値下げの効果もほとんどありません</mark>。単価が同じである以上、そこは Fable 5 と変わりません。

<figure class="figure">
<img src="/static/images/fable51-cost-index.svg" alt="同じ仕事をさせたときの費用を Fable 5 を100として比べた横棒グラフ。ふつうの使い方は Fable 5.1 で75（約25%減）、長く自動で作業させる使い方は55（最大で約45%減）。いずれも Anthropic が2026年8月の4週間の実際の利用から集計した比率で、読み直しが費用の大半を占める使い方ほど下がり幅が大きい。短い質問を1回ずつする使い方では読み直しがほとんど無いので、このようには下がらない。">
<figcaption>下がり幅は「読み直しがどれだけ多いか」で決まります</figcaption>
</figure>

## 前のモデル（Fable 5）との違い

### 公式が挙げている性能テストの結果

発表ページには、Fable 5・Opus 5・OpenAI の GPT-5.6 Sol と並べた表が載っています。まず Fable 5 との比較です。

| 何のテストか | 分野 | Fable 5 | Fable 5.1 |
|---|---|---|---|
| Terminal-Bench-Science 0.1 | 科学研究の自動化 | 24.7% | 52.6% |
| Terminal-Bench 4.0 | プログラム作成の自動化 | 42.0% | 55.8% |
| GDPval-AA v2 | 事務の仕事 | 1723 | 1853 |
| OSWorld 2.0（部分点あり） | パソコン操作 | 72.9% | 77.9% |
| OSWorld 2.0（完全一致のみ） | パソコン操作 | 36.1% | 41.7% |
| Humanity's Last Exam（道具なし） | 幅広い分野の推論 | 57.8% | 60.9% |
| Humanity's Last Exam（道具あり） | 幅広い分野の推論 | 63.8% | 65.0% |
| AutomationBench | 業務の自動化 | 17.1% | 31.4% |
| CursorBench 3.2.0 | プログラム作成の自動化 | 70.5% | 73.4% |

出典: すべて <https://www.anthropic.com/claude-fable-and-mythos-5-1>

<figure class="figure">
<img src="/static/images/fable51-bench.svg" alt="Fable 5 と Fable 5.1 の点数を比べた横棒グラフ。Terminal-Bench-Science 0.1 は24.7％から52.6％、Terminal-Bench 4.0 は42.0％から55.8％、OSWorld 2.0 の部分点ありは72.9％から77.9％、完全一致のみは36.1％から41.7％、Humanity's Last Exam の道具なしは57.8％から60.9％、AutomationBench は17.1％から31.4％、CursorBench 3.2.0 は70.5％から73.4％。いずれも Anthropic が自社で測った値で、テストの中身も測り方も別々のため平均は取れない。安全装置が働いた課題は0点として数えられている。">
<figcaption>％で書かれている7つの点数を、同じ目盛りで並べたもの</figcaption>
</figure>

読むときの注意が3つあります。

**1つめ。測ったのは Anthropic 自身です。**公式は、Fable 5.1 は本番の安全装置を有効にしたまま測ったと書いています。安全装置が働いた課題は OSWorld 2.0 で0点として数えられ、<mark>公式自身が「これは Fable 5.1 と Fable 5 の点数を下げている可能性が高い」と注記しています</mark>（出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>）。

**2つめ。同じモデルなのに点が違う行があります。**Terminal-Bench 4.0 では Fable 5.1 が 55.8%、Mythos 5.1 が 60.9% です。公式は、2つは同じモデルで、差はセキュリティ系の安全装置が介入した課題のぶんだと説明しています（出典: 同上）。

**3つめ。テストごとに誤差があります。**Terminal-Bench-Science 0.1 は、公式が標準誤差をモデルあたり ±3.5〜4.5 ポイントと書いています（出典: 同上）。差が数ポイントの行は、誤差の中に入ります。

### 「どれだけ考えるか」の設定で費用が変わる

Fable 5.1 には「どれだけ考えてから答えるか」の設定（effort）があり、`low` から `max` まで段階があります。公式は、<mark>Low か Medium に設定した Fable 5.1 は、Fable 5 と同じかそれ以上の結果を、ずっと低い費用で出す</mark>と説明しています（出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>）。既定値は Claude Code では High、Claude Cowork と Claude.ai では Medium です（出典: 同上）。

### 基本仕様（いま公式の一覧に載っているもの）

| | Claude Fable 5.1 | Claude Opus 5 |
|---|---|---|
| 一度に読める量 | 100万トークン | 100万トークン |
| 一度に書ける量 | 12.8万トークン | 12.8万トークン |
| 「考える」機能 | 常にオン | オン（切ることもできる） |
| 「どれだけ考えるか」の既定値 | high | high |
| 学習データの締め切り | **2026年6月** | 2026年5月 |
| モデルの呼び名（API） | `claude-fable-5-1` | `claude-opus-5` |

出典: <https://docs.claude.com/en/docs/about-claude/models/overview>

Fable 5 の行は、いまの公式一覧ページには載っていません。だから Fable 5 の学習データの締め切りは、この記事では比べていません。

### 安全装置が「効きすぎない」方向に変わった

会社で使う人に関係する変更が3つあります。すべて発表ページの説明です（出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>）。

- **セキュリティ系の誤検知が減る。**公式は、Claude Code での安全装置の介入が、Fable 5 のときより1セッションあたり平均で約60%減ると説明しています。ソフトの弱点を「見つける」用途は許可されるようになりました。攻撃に使う道具を作る用途は、引き続き Opus 系のモデルに回されます。
- **生物・医療系の誤検知が減る。**初歩的な生物や医療の質問で安全装置が働く回数が、Fable 5 の発売時より85%減ったと書かれています。
- **データを Anthropic 側に残さない仕組み（EFS）。**顧客側のクラウドにデータを置く方式で、今年の秋から段階的に提供すると書かれています。それまでの間、対象の企業顧客はデータ保持ゼロの条件で Fable 5.1 を使えるとしています。

もう1つ、文章を書く仕事の人に関係する変更があります。<mark>2026年8月2日より後に出たモデルの文章には、EU の規則に基づく「透かし」が入ります</mark>（出典: 同上）。公式は、透かしは目に見えず、文章の中身に影響せず、利用者の情報も含まないと説明しています。判定用の仕組みは、規制当局や報道機関などに限定して提供している段階です。

## 他社の最上位モデルとの比較

### 単価

各社の公式料金ページから直接取った数字だけを並べます。

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | 読み直し（キャッシュ読み取り） |
|---|---|---|---|---|
| Claude Fable 5.1 | Anthropic | $10 | $50 | $0.25 |
| Claude Opus 5 | Anthropic | $5 | $25 | $0.50 |
| GPT-5.6 Sol | OpenAI | $4.00（短）/ $8.00（長） | $20.00（短）/ $30.00（長） | $0.40（短）/ $0.80（長） |
| Gemini 3.1 Pro Preview | Google | $2.00（20万トークン以下）/ $4.00（超過時） | $12.00（20万トークン以下）/ $18.00（超過時） | $0.20（20万トークン以下）/ $0.40（超過時） |

出典: Claude は <https://docs.claude.com/en/docs/about-claude/pricing>、GPT は <https://developers.openai.com/api/docs/pricing>、Gemini は <https://ai.google.dev/gemini-api/docs/pricing>

読むときの注意が3つあります。

- <mark>Fable 5.1 の入力・出力の単価は、この表の中で一番高いままです</mark>。安くなったのは読み直しだけです。
- <mark class="warn">GPT-5.6 Sol の単価は「少なくとも2026年11月21日までの販促価格」と料金ページに書かれています</mark>（出典: <https://developers.openai.com/api/docs/pricing>）。それ以降の値段は書かれていません。
- OpenAI と Google は、入力が長くなると単価が上がります。Google は「20万トークンを超えたら」と明記していますが、OpenAI の料金ページは「短い」「長い」の境目が何トークンかを書いていません（出典: 同上）。

| | Claude Fable 5.1 | Claude Opus 5 | GPT-5.6 Sol |
|---|---|---|---|
| 一度に読める量 | 100万トークン | 100万トークン | 105万トークン |
| 一度に書ける量 | 12.8万トークン | 12.8万トークン | 12.8万トークン |
| 学習データの締め切り | 2026年6月 | 2026年5月 | 2026年2月16日 |

出典: Claude は <https://docs.claude.com/en/docs/about-claude/models/overview>、GPT は <https://developers.openai.com/api/docs/models>。Gemini 3.1 Pro Preview は、上で使った料金ページにこの3項目が載っていないので、この表には入れていません。

### 性能テスト（Anthropic の表に載っている範囲）

発表ページの表には GPT-5.6 Sol の列もあります。ただし測ったのは Anthropic です。

| 何のテストか | Fable 5.1 | Opus 5 | GPT-5.6 Sol |
|---|---|---|---|
| Terminal-Bench-Science 0.1 | 52.6% | 29.0% | 22.4% |
| Terminal-Bench 4.0 | 55.8% | 52.3% | 37.3% |
| GDPval-AA v2 | 1853 | 1824 | 1711 |
| AutomationBench | 31.4% | 26.9% | 19.6% |
| CursorBench 3.2.0 | 73.4% | 70.0% | 67.2% |

出典: <https://www.anthropic.com/claude-fable-and-mythos-5-1>

<mark class="warn">この表は Anthropic が自社で測って自社のページに載せた数字で、OpenAI が同じ条件で測った数字ではありません</mark>。OSWorld 2.0 と Humanity's Last Exam の行は、公式の表でも GPT-5.6 Sol の欄が空欄です。Google のモデルは表に入っていません。<mark>公式の数字で言い切れるのは「単価の並び」までで、「どれが賢いか」ではありません</mark>。

## どういう人に効くか

**乗り換えを検討していい人**

- Fable 5 を、長い資料を読ませたり、長く自動で作業させたりする用途で使っている人。<mark>単価が同じなので、費用の再計算をせずに切り替えられます</mark>。読み直しが多い使い方ほど、下がり幅が大きくなります。
- Opus 5 で足りずに困っている人。公式のモデル一覧は「まず Opus 5 から始め、手間の設定を上げても足りないときに Fable 5.1」と勧めています（出典: <https://docs.claude.com/en/docs/about-claude/models/overview>）。
- 2026年6月までの出来事を扱わせたい人。学習データの締め切りが Opus 5 より1か月新しくなっています（出典: 同上）。

**急がなくていい人**

- 短い質問を1回ずつする使い方の人。読み直しがほとんど無いので、値下げが効きません。
- 単価そのものを下げたい人。入力 $10・出力 $50 は Opus 5 の2倍のままです（出典: <https://docs.claude.com/en/docs/about-claude/pricing>）。
- 会社のルールで「データを保持させない」条件が要る人。EFS の提供は今年の秋以降と書かれているので、いまは対象の企業顧客だけです。

**この記事で分からないこと**

実際に使ったときの体感、日本語での品質、返答までの待ち時間。これらは公式ページに数字がなく、運営者も試していないので書けません。「約25%」「最大約45%」も Anthropic の利用者全体の集計で、自分の使い方でいくら下がるかは、請求を見るまで分かりません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Claude Fable 5.1 と Claude Mythos 5.1 の発表（Anthropic・2026年9月1日）: <https://www.anthropic.com/claude-fable-and-mythos-5-1>
2. 料金（Anthropic 公式ドキュメント）: <https://docs.claude.com/en/docs/about-claude/pricing>
3. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://docs.claude.com/en/docs/about-claude/models/overview>
4. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
5. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>
6. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
