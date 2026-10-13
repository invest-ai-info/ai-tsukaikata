---
title: Argon一般提供開始——出力100万は条件つき
description: Googleは2026年10月13日にGemini 4 Argonの一般提供を始めました。9月30日の発表で「公表されていない」としていた一般公開の時期と価格の終了日が判明し、公式モデルページで出力トークン上限に付く条件も確認できました。数字はすべて各社の公式ページから引用しています。
category: tools
scene: choose
published: 2026-10-13
checked: 2026-10-13
tags: [Gemini, モデル比較, 料金, AI最新情報]
---

## 結論：今の立場ごとに、こうなります

Google は2026年10月13日、**Gemini 4 Argon** の一般提供を始めました（出典: 発表ページ）。
9月30日の前回発表（[Argon、出力100万トークン——使えるのは一部の人だけ](/tools/gemini-4-argon/)）
では「一般公開はできるだけ早く行う」としか書かれておらず、具体的な日付は不明でした。

| 今の立場 | 今できること | どうなるか |
|---|---|---|
| **今すぐ試したい開発者・会社員** | API・AI Studio・Geminiアプリから使える（Fairwind Program限定から一般提供へ） | 既定の出力上限は65,536トークンで、前のモデルと同じ。「出力100万トークン」はlong decodeという別機能を使った場合だけの数字 |
| **価格を基準に判断したい人** | 導入価格（入力$2・出力$10）で使い始められる | 2026年11月30日を過ぎると入力$4・出力$20に上がる。この値段はClaude Opus 5.5の料金と完全に一致する |
| **前回記事を読んでいた人** | Fairwind Program限定提供だった | 一般提供は始まったが、Fairwind Program自体も「数百社への拡大」が同時に進んでいる |

<mark>一言でいうと、誰でも使えるようになったが、宣伝文句の「出力100万トークン」は既定では出ません。</mark>

先に断っておきます。**この記事は運営者がArgonを実際に使った記録ではありません。**公式の発表ページ・モデルページ・料金ページに書かれている数字だけを読んで整理したものです。

ここから下は、表の3行がなぜそうなるのかの説明です。

## なぜそうなるのか

### 「出力100万トークン」は、long decodeという別機能の数字

GA発表ページは、新しいトークン設計をこう説明しています（出典: 発表ページ）。

> This is enabled by an industry-leading 1M unified input-output token limit via the Gemini API.
>（Gemini API経由で、業界最高水準の「統合された入出力100万トークン上限」によって実現しています）

<mark class="warn">ここが前回記事と最も違う点です。前のモデルの公式ページは「入力の上限」「出力の上限」を
別々に載せていましたが、Argonのページは「統合された入出力トークン上限（Context window）」という
1つの数字に変わりました。</mark>公式モデルページで正確な値を確認すると、次のようになっています
（出典: Gemini API公式モデルページ）。

| 項目 | Gemini 4 Argon | 前のモデル（3.1 Pro Preview） |
|---|---|---|
| ページの表示項目 | Context window（統合） | Input token limit／Output token limit（別々） |
| 数字 | 1,048,576トークン | 入力1,048,576／出力65,536 |
| 既定の出力上限（同期呼び出し） | 65,536トークン | 65,536トークン |
| long decode利用時の出力上限 | 最大1,048,576トークン | （この機能自体が無い） |

<figure class="figure">
<img src="/static/images/argon-ga-output-budget.svg" alt="Gemini 3.1 Pro Previewの出力上限65,536トークン、Gemini 4 Argonの既定（同期呼び出し）の出力上限65,536トークン、Gemini 4 Argonのlong decode利用時の出力上限1,048,576トークンを比べた横棒グラフ。long decode利用時は既定の16倍（この記事の計算）。既定のままでは前のモデルと変わらない。">
<figcaption>既定の出力上限は変わっていない。16倍になるのはlong decodeを使った場合だけ</figcaption>
</figure>

<mark>何もしなければ、1回の応答で生成できるトークン数は前のモデルと同じ65,536のままです。</mark>
long decodeを明示的に使ったときだけ、上限が広がります。<mark class="warn">ただしその分、
入力に使える枠は減ります。</mark>1,048,576は入力と出力の合計上限であって、両方を同時に
最大まで使うことはできません。

1,048,576 ÷ 65,536 を計算すると、ちょうど**16倍**です（この記事の計算）。前回記事では
発表ページの丸めた表記「100万」をそのまま使い、前のモデルの65,536との比率を約15.3倍と
書きました。公式モデルページの正確な値（1,048,576）で計算し直すと16倍になります。

### 価格が上がる日は、2026年11月30日

前回記事で「終了する時期は発表に書かれていない」と書いた導入価格の期限が、今回判明しました。
GA発表ページの脚注は、次のように明記しています（出典: 発表ページ脚注）。

> After the introductory period expires on November 30, 2026, the price of $4 per 1M input tokens
> and $20 per 1M output tokens will apply.

Gemini API公式料金ページでも、同じ日付を確認しました（出典: ai.google.dev/gemini-api/docs/pricing）。

| | 入力（100万トークン） | 出力（100万トークン） | キャッシュ済み入力 |
|---|---|---|---|
| 〜2026年11月30日 | $2.00 | $10.00 | $0.10（95%引き） |
| 2026年12月1日から | $4.00 | $20.00 | $0.20（95%引き） |

<figure class="figure">
<img src="/static/images/argon-ga-price-deadline.svg" alt="Gemini 4 Argonの導入価格（入力2ドル・出力10ドル）と、2026年12月1日からの価格（入力4ドル・出力20ドル）を比べた横棒グラフ。100万トークンあたりのドル。値上がりの日付（2026年11月30日まで）は、発表ページの脚注と公式料金ページの両方で確認できた。">
<figcaption>値上がりの日付が、発表ページと料金ページの両方で確認できた</figcaption>
</figure>

<mark>この日付は、GA発表ページの脚注と公式料金ページという、2つの独立したページに
同じ数字で書かれています。</mark>確認できた数字として扱います。

### Fairwind Programは終わらず、拡大している

一般提供が始まっても、サイバー防御者向けの限定枠は消えていません。発表ページは
次のように書いています（出典: 発表ページ）。

> Starting today, we're beginning expansion to hundreds of additional Fairwind Program partners.

<mark class="warn">信頼されたサイバー防御の担当者には「サイバー用の安全装置を外した」版が
別に用意されています。</mark>一般提供される版とは中身が違う可能性がある、という前回記事の
注記は今も有効です。

GA発表ページは、新しい性能の主張もいくつか挙げています。いずれもGoogle自身の測定か、
提携先の非公開評価です。

| 項目 | 内容 |
|---|---|
| Vals Index（総合指標） | 1位 |
| ERQA（ロボティクスの視覚推論） | 87% |
| RareBench（希少疾患の診断支援） | 57% |
| LabBench（検査室での推論） | 52.2% |

出典: 発表ページ。このサイトの方針どおり、各社が自社で測った点数は他社と横に並べません。

## 他社の最上位モデルと比べると

### 単価は、値上がり後にClaude Opus 5.5と完全一致

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | キャッシュ済み入力 |
|---|---|---|---|---|
| Gemini 4 Argon（〜2026年11月30日） | Google | $2.00 | $10.00 | $0.10 |
| Gemini 4 Argon（2026年12月1日から） | Google | $4.00 | $20.00 | $0.20 |
| Claude Opus 5.5（Anthropic最上位） | Anthropic | $4.00 | $20.00 | $0.20 |
| GPT-6 Astra（OpenAI最上位） | OpenAI | $10.00 | $50.00 | $1.00 |

出典: Argonは発表ページ・公式料金ページ、Claude Opus 5.5は
<https://platform.claude.com/docs/en/about-claude/pricing>、GPT-6 Astraは
<https://developers.openai.com/api/docs/pricing>（いずれも2026年10月13日に確認）

<figure class="figure">
<img src="/static/images/argon-ga-vendor-match.svg" alt="Gemini 4 Argon（〜2026年11月30日・入力2ドル出力10ドル）、Gemini 4 Argon（2026年12月1日から・入力4ドル出力20ドル）、Claude Opus 5.5（入力4ドル出力20ドル）、GPT-6 Astra（入力10ドル出力50ドル）を比べた横棒グラフ。100万トークンあたりのドル。値上がり後のArgonはClaude Opus 5.5と単価が完全に一致する。">
<figcaption>値上がり後のArgonは、Claude Opus 5.5と同じ値段になる</figcaption>
</figure>

<mark>Gemini 4 Argonの値上がり後の価格（入力$4・出力$20）は、Claude Opus 5.5（入力$4・出力$20）と
1円も違いません。</mark>キャッシュ済み入力の値引き率も、両社とも入力価格の95%引きで、同じ数字
（$0.20）になります。<mark class="warn">導入価格の間だけは、ArgonのほうがOpus 5.5より半額です。</mark>

### 仕様は、ページの表示そのものが変わった

| モデル | コンテキストウィンドウ | 出力の上限 | 知識の締め切り | 提供状況 |
|---|---|---|---|---|
| Gemini 4 Argon | 1,048,576（入出力を統合） | 65,536（既定）／long decode利用時は最大1,048,576 | 公表されていない | **一般提供（Stable）** |
| Claude Opus 5.5 | 1,000,000 | 128,000 | 2026年6月 | 一般提供 |
| GPT-6 Astra | 1,050,000（入力922,000＋出力128,000） | 128,000 | 2026年4月30日 | 一般提供 |

出典: Argonは<https://ai.google.dev/gemini-api/docs/models/gemini-4-argon>、Claude Opus 5.5は
<https://platform.claude.com/docs/en/about-claude/models/overview>、GPT-6 Astraは
<https://developers.openai.com/api/docs/models/gpt-6-astra>

<mark class="warn">3社の「コンテキストウィンドウ」は、同じ基準で測った数字ではありません。</mark>
GPT-6 Astraは入力と出力の内訳まで公式ページに書かれていますが、Claude Opus 5.5は合計しか
書かれておらず、Argonは前のモデルの時点では別々だった2つの数字を今回「統合」に変えました。
知識の締め切りは、Argonだけ今も公表されていません。

## どういう人に効くか

**今、関係がある人**

- 今日から試したい開発者・会社員。API・AI Studio・Geminiアプリから使えます。
- 導入価格のうちに使い始めたい人。11月30日までは入力$2・出力$10です。
- サイバーセキュリティの防御担当者で、Fairwind Programへの参加資格がある人。

**急がなくていい人**

- 出力100万トークンを前提に設計したい人。既定では出ません。long decodeを使うかどうか、
  入力と出力の配分も含めて、先に公式ページで仕様を確認してください。
- 値上がり後の値段だけを見て「Argonは安い」と判断したい人。12月からはClaude Opus 5.5と同額です。
- 入力トークンの上限だけで比較したい人。Argonは入力単独の上限を公表していません。

## この記事で分からないこと

- 知識の締め切り（学習データの範囲）
- long decodeを使ったときの実際の料金（通常の出力と同じ単価なのか、発表に明記がない）
- 実際に使ったときの体感、日本語での品質

どれも公式ページに数字がなく、運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 4 Argon 一般提供の発表（Google・2026年10月13日）:
   <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/>
2. Gemini 4 Argon の公式モデルページ（Google公式）:
   <https://ai.google.dev/gemini-api/docs/models/gemini-4-argon>
3. Gemini API の料金（Google公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. 料金（Anthropic公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
5. モデル一覧と仕様（Anthropic公式ドキュメント）:
   <https://platform.claude.com/docs/en/about-claude/models/overview>
6. APIの料金（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
7. GPT-6 Astraのモデルページ（OpenAI公式ドキュメント）:
   <https://developers.openai.com/api/docs/models/gpt-6-astra>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
