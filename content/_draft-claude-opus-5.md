---
title: Claude Opus 5 は何が変わったのか（公式発表の数字だけで比べる）
description: 2026年7月24日に公開された Claude Opus 5 について、Anthropic の公式発表・公式ドキュメント・公式料金ページに書かれている数字だけを並べました。まとめ記事の数字は使っていません。
category: tools
published: 2026-08-04
tags: [Claude, モデル比較, 料金, AI最新情報]
---

## 何が変わったか

Anthropic は 2026年7月24日に **Claude Opus 5** を公開しました（出典: <https://www.anthropic.com/news/claude-opus-5>）。公式発表とドキュメントを読んで、書かれている数字だけを並べます。3行にすると、こうなります。

- 料金は1つ前の Opus 4.8 と同じで、入力100万トークンあたり **$5**、出力100万トークンあたり **$25** です（出典: <https://platform.claude.com/docs/en/about-claude/pricing>）。
- 公式は性能テスト「Frontier-Bench v0.1」で <mark>Opus 4.8 の2倍を超え、しかも1タスクあたりの費用は下がる</mark>と説明しています（出典: <https://www.anthropic.com/news/claude-opus-5>）。
- 知識が新しくなりました。学習データの締め切りが Opus 4.8 の 2026年1月から、Opus 5 は **2026年5月** になっています（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。

先に断っておきます。**この記事は運営者が Opus 5 を試した記録ではありません。**公式ページに書かれていることを読んで整理したものです。「速かった」「賢くなった」といった使用感は一切書いていません。

そしてもう1つ、読む前に知っておくと損をしない点があります。<mark>公式が出しているのは「何倍」「何ポイント高い」という比率だけで、点数そのものは載っていません</mark>。だから「Opus 5 は Frontier-Bench で何点なのか」は、この記事にも書けません。

## 前のモデル（Opus 4.8）との違い

### 料金と基本仕様

| | Claude Opus 4.8 | Claude Opus 5 |
|---|---|---|
| 入力（100万トークン） | $5 | $5 |
| 出力（100万トークン） | $25 | $25 |
| まとめ処理（Batch API）の入力 / 出力 | $2.50 / $12.50 | $2.50 / $12.50 |
| 一度に読める量 | 100万トークン | 100万トークン |
| 一度に書ける量 | 12.8万トークン | 12.8万トークン |
| 学習データの締め切り | 2026年1月 | **2026年5月** |
| モデルの呼び名（API） | `claude-opus-4-8` | `claude-opus-5` |

出典: 仕様は <https://platform.claude.com/docs/en/about-claude/models/overview>、料金は <https://platform.claude.com/docs/en/about-claude/pricing>

**値段も、読める量も、書ける量も同じです。**変わったのは中身と、知識の新しさです。<mark>知識の締め切りが4か月ぶん進んでいます</mark>。

「トークン」は文章を機械が数えるときの単位です。公式ドキュメントは 100万トークンを「英語でおよそ55.5万語」と説明しています（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。

### 公式が挙げている性能テストの結果

| 何のテストか | 公式の説明 |
|---|---|
| Frontier-Bench v0.1 | Opus 4.8 の性能を2倍以上に。1タスクあたりの費用はより安い |
| CursorBench 3.2（max 設定時） | 上位モデル Fable 5 の最高点との差が0.5%以内。1タスクあたりの費用は半分 |
| ARC-AGI 3 | 2位のモデルの3倍の点数 |
| Zapier AutomationBench | 同じ1タスクあたり費用で、2位のモデルのおよそ1.5倍の正答率 |
| OSWorld 2.0 | Fable 5 を上回り、費用は3分の1強 |
| 有機化学 | Opus 4.8 より10.2ポイント高い |
| タンパク質関連の課題 | 1つ前のモデルより7.7ポイント高い |

出典: すべて <https://www.anthropic.com/news/claude-opus-5>

<mark>ここに並んでいるのは「1タスクあたりの費用」の比較で、1トークンあたりの単価の話ではありません</mark>。単価は据え置きなので、費用が下がったのは「同じ仕事を、より少ないやり取りで終わらせている」という意味になります。

公式は測り方も書いています。Frontier-Bench v0.1 の数字は社内での実行で、mini-SWE-agent という枠組みと GKE という実行基盤を使い、1つの課題につき5回試した平均値だとしています。また、安全性の判定で断られた場合は Opus 4.8 が代わりに答えた、とも書かれています（出典: <https://www.anthropic.com/news/claude-opus-5>）。<mark class="warn">この測り方は Anthropic 社内のもので、他社が同じ名前のテストを同じ条件で測っているとは限りません</mark>。

### 使い方が変わるところ

ここは、実際に使う人が引っかかる可能性のある変更です。すべて公式の移行ガイドに書かれています（出典: <https://platform.claude.com/docs/en/about-claude/models/migration-guide>）。

| 項目 | Opus 4.8 | Opus 5 |
|---|---|---|
| 何も指定しないときの「考える」動き | 考えずに答える | 考えてから答える |
| 「考える」を切る指定 | できる | `high` 以下の設定でのみ可能 |
| 前回の内容を使い回せる最小の長さ | 1,024トークン | 512トークン |
| 返事の長さ | — | 公式は「4.8 より長くなる」と説明 |

出典: <https://platform.claude.com/docs/en/about-claude/models/migration-guide>

<mark>Opus 5 は、何も指定しないと「考えてから答える」動きになります</mark>。考える部分も出力として数えられるので、出力の上限を低く設定したまま乗り換えると、答えが途中で切れることがあります。

<mark class="warn">手間の設定（effort）を `xhigh` か `max` にした状態で「考える機能を切る」と指定すると、エラーになって動きません</mark>（出典: 同上）。

なお「速いモード（fast mode）」というものがあります。<mark>公式は最大2.5倍の速さで、料金は入力$10・出力$50（通常の2倍）と説明しています</mark>（出典: <https://platform.claude.com/docs/en/build-with-claude/fast-mode>）。ただし研究プレビューという扱いで、利用には申し込みが要ります。Amazon・Google・Microsoft の各クラウド経由では使えない、とも書かれています。

## 他社の最上位モデルとの比較

ここが一番、数字が壊れやすいところです。**各社の公式料金ページから直接取った数字だけ**を並べます。

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | 一度に読める量 |
|---|---|---|---|---|
| Claude Opus 5 | Anthropic | $5 | $25 | 100万トークン |
| Claude Fable 5 | Anthropic | $10 | $50 | 100万トークン |
| Claude Sonnet 5 | Anthropic | $2（8月31日まで） / 以降 $3 | $10（8月31日まで） / 以降 $15 | 100万トークン |
| Gemini 3.1 Pro Preview | Google | $2.00（20万トークン以下）/ $4.00（超過時） | $12.00（20万トークン以下）/ $18.00（超過時） | 100万トークン |
| Gemini 3.6 Flash | Google | $1.50 | $7.50 | （このページには記載なし） |

出典: Claude 各モデルは <https://platform.claude.com/docs/en/about-claude/pricing> と <https://platform.claude.com/docs/en/about-claude/models/overview>、Gemini の料金は <https://ai.google.dev/gemini-api/docs/pricing>、Gemini 3.1 Pro の読める量・書ける量は <https://deepmind.google/models/gemini/pro/>

**この表は、そのまま「どれが安いか」の表として読めません。**理由を3つ書きます。

**1つめ。トークンの数え方が会社ごとに違います。**Anthropic の料金ページには、Claude 4.7 以降のモデルは新しい数え方を使っていて、**同じ文章でおよそ30%多いトークンになる**と書かれています（出典: <https://platform.claude.com/docs/en/about-claude/pricing>）。同じ社内でも世代でずれるということは、他社との間ではもっとずれます。<mark class="warn">単価だけを並べても、実際の支払額の大小は判定できません</mark>。

**2つめ。料金の形が違います。**<mark>Gemini 3.1 Pro は入力が20万トークンを超えると単価が上がりますが、Claude は100万トークンまで同じ単価です</mark>（出典: Anthropic 側は <https://platform.claude.com/docs/en/about-claude/pricing>、Google 側は <https://ai.google.dev/gemini-api/docs/pricing>）。長い資料を読ませる使い方だと、単価表の並びと請求額の並びが逆になり得ます。

**3つめ。性能テストの点数は、そもそも同じ土俵に載っていません。**Anthropic が公表しているのは「他社の次点モデルの3倍」といった比率で、相手のモデル名も、測ったときの設定も書かれていません。Google 側の公式ページに同じテストの数字があるわけでもありません。**単純比較はできない**、というのがこの記事の結論です。

### OpenAI の数字を載せていない理由

<mark>OpenAI の公式料金ページは、この記事を書いた環境から読めませんでした</mark>（`openai.com` と `developers.openai.com` がいずれも403で応答）。

このサイトは「数字は一次情報からしか取らない」という決まりで書いています。まとめ記事やニュースサイトの数字を使えば表は埋まりますが、そこが一番壊れているところです。<mark class="warn">二次情報の数字を写すと、条件の違いごと写します</mark>。だから空欄のまま残しました。読めた時点で追記します。

## どういう人に効くか

**乗り換えを検討していい人**

- 毎日 Opus 4.8 を業務で使っている人。<mark>料金が据え置きのまま世代が上がるので、費用の再計算をせずに切り替えられます</mark>。
- 2026年の1月から5月までの出来事をAIに扱わせたい人。知識の締め切りが4か月ぶん新しくなっています。
- 長い作業を任せている人。公式は、長く走る作業向けの手間設定（`xhigh`）に対応していると説明しています（出典: <https://platform.claude.com/docs/en/build-with-claude/effort>）。

**急がなくていい人**

- チャットで短い質問をするだけの人。公式は「返事が4.8より長くなる」と説明しているので、短く答えてほしい使い方だと、むしろ指示を書き直す手間が増えます。
- 決まった型の出力を大量に処理している人。移行ガイドは、乗り換えたら手間の設定を測り直すよう勧めています。設定を引き継ぐだけでは済みません。
- Amazon・Google・Microsoft のクラウド経由で「速いモード」を使いたい人。公式は、そこでは提供していないと書いています。

**この記事で分からないこと**

実際に使ったときの体感、日本語での品質、返答が返ってくるまでの待ち時間。これらは公式ページに数字がなく、運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・ブログは1件も使っていません。

1. Claude Opus 5 の発表（Anthropic・2026年7月24日）: <https://www.anthropic.com/news/claude-opus-5>
2. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>
3. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
4. Opus 4.8 から Opus 5 への移行ガイド（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/migration-guide>
5. 手間の設定（effort）の説明（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/build-with-claude/effort>
6. 速いモード（fast mode）の説明（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/build-with-claude/fast-mode>
7. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
8. Gemini Pro のモデルページ（Google DeepMind 公式）: <https://deepmind.google/models/gemini/pro/>

読めなかったページ: OpenAI の公式料金ページ（<https://openai.com/api/pricing/> および <https://developers.openai.com/api/docs/pricing>）。いずれも403で本文を取得できませんでした。

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
