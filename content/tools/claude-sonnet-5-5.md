---
title: Sonnet 5.5は同じ値段で3割速い——4つの設定はエラーで止まる
description: 2026年9月28日に発表された Claude Sonnet 5.5 について、Anthropic の発表ページ・モデルのページ・料金ページに書かれている数字だけを並べました。単価は Sonnet 5 と完全に同額で、OpenAI の GPT-6 Sol とも一致しています。ただし「考える」を切る・道具を強制するなど4つの設定は、そのまま使うとエラーで止まります。
category: tools
scene: choose
published: 2026-09-29
checked: 2026-09-29
tags: [Claude, モデル比較, 料金, AI最新情報]
---

## 結論：使い方ごとに、こうなります

Anthropic は 2026年9月28日に **Claude Sonnet 5.5** を出しました（出典: <https://www.anthropic.com/claude-sonnet-5-5>）。Sonnet 5 から乗り換えたときの結果は、使い方で分かれます。

| どんな使い方か | やること | どうなるか |
|---|---|---|
| **Claude のアプリでチャットしている** | Sonnet 5.5 を選んで使う | 出力が30%以上速くなる。単価も使い勝手も変わらない |
| **API で Sonnet 5 を使っている（特別な設定なし）** | モデル名を `claude-sonnet-5-5` に替える | 単価は1トークンあたり同額。使うトークン数が減り、1つの仕事の費用は**最大30%減** |
| **API で「考える」を切る・道具を強制する・旧computer useを使っている** | **先に設定を直してから**替える | 直さずに替えると、**400エラーで止まる** |

<mark>一言でいうと、値段は変わらず出力は3割速くなった。ただし4つの設定は、そのままでは動かない。</mark>

先に断っておきます。**この記事は運営者が Sonnet 5.5 を試した記録ではありません。**公式ページに書かれていることを読んで、使い方ごとに整理したものです。

ここから下は、表の3行がなぜそうなるのかの説明です。

## なぜそうなるのか

### 費用が最大30%下がる理由

Anthropic は発表ページで、単価は変えていないと明記しています（出典: <https://www.anthropic.com/claude-sonnet-5-5>）。

| 100万トークンあたり | Claude Sonnet 5 | Claude Sonnet 5.5 |
|---|---|---|
| 入力 | $2 | $2 |
| 出力 | $10 | $10 |
| 読み直し（キャッシュ読み取り） | $0.20 | $0.20 |
| キャッシュ書き込み（5分保持） | $2.50 | $2.50 |
| キャッシュ書き込み（1時間保持） | $4 | $4 |

出典: <https://platform.claude.com/docs/en/models/sonnet-5-5/overview> と <https://platform.claude.com/docs/en/models/sonnet-5/overview>

<figure class="figure">
<img src="/static/images/sonnet55-what-changed.svg" alt="Sonnet 5からSonnet 5.5への変化を2列で比べた図。変わらないもの＝読める量100万トークン、書ける量12.8万トークン、単価は入力2ドル・出力10ドルでSonnet 5と同額、読める形式は文章と画像。変わったもの＝出力速度が30%以上速い、1つの仕事の費用が最大30%減る、知識の締め切りが2026年1月から6月、「考える」を切る指定がエラーになる、道具を強制する指定ができなくなった、旧computer useの道具が使えなくなった。">
<figcaption>器の大きさと単価は同じで、トークンの使い方と一部の設定が変わりました</figcaption>
</figure>

**単価そのものは1円も変わっていません。**それでも費用が下がるのは、Sonnet 5.5 が同じ仕事をより少ないトークンで終えるからだと公式は説明しています（出典: 同上）。<mark>公式のテストでは、1つの仕事あたりの費用が最大30%少なくなりました</mark>。

<mark class="warn">30%はAnthropic自身のテストの値です。自分の使い方で同じだけ下がるとは限りません。</mark>単価が変わっていないことだけは、どの使い方でも確かです。

### 出力が30%以上速くなる理由

<mark>Sonnet 5.5は、Sonnet 5より出力を30%以上速く生成します</mark>（出典: 同上）。Anthropicが出した中で、いちばん速いSonnetモデルです。速さの中身（どのテストで測ったか）は公式ページに書かれていないため、この記事では倍率だけを書きます。

### 4つの設定が止まる理由

Sonnet 5.5では内部の仕様が変わり、Sonnet 5で動いていた設定のうち4つがエラーになります（出典: <https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5>）。

| 設定 | Sonnet 5 | Sonnet 5.5 |
|---|---|---|
| 「考える」を切る指定 `disabled` | 切れる | **400エラー**（`between_tools` に置き換え） |
| 道具を強制する指定（`any` / `tool`） | できる | **400エラー**（`auto` と `none` だけ） |
| 旧パソコン操作の道具（`computer_20251124`） | 使える | **Claude API と Google Cloud では400エラー**（Amazon Bedrock では使える） |
| advisorツールの助言役に Opus 4.8 / Opus 4.7 / Sonnet 5 を指定 | できる | **400エラー** |

<mark class="warn">モデル名だけ書き換えて乗り換えると、上の設定を使っている自動化はその場で止まります</mark>。

もう1つ、エラーにはならないものの気づきにくい変化があります。「考える」の途中経過を記録した内部データ（thinking block）は、使ったモデルと会話に紐づきます（出典: 同上）。Sonnet 5.5 は Sonnet 5・Opus 4.8・Haiku 4.5 以前の記録は読めますが、Opus 5・Opus 5.5・Fable系・Mythos系の記録は読めません。合わないデータはAPIが自動で取り除くため、通常はリクエストが失敗することはありません。

ただし例外があります。2026年8月31日0時（UTC）以降に作られたアカウントでは、この確認が既定で有効です。会話の前提（システムプロンプトや道具）が変わった後に、古い記録をそのまま送ると400エラーになります（出典: 同上）。

公式が示している直し方は、次の順番です（出典: 同上）。

1. モデル名を `claude-sonnet-5` から `claude-sonnet-5-5` に変える
2. 「考える」を切る設定を `between_tools` に置き換える
3. 道具の強制指定は `auto` に戻し、どの場面でその道具を使うかを指示文に書く
4. パソコン操作は、Claude API・Google Cloud では新しい道具（`computer_toolset_20260801`）に移す

### 性能はどれだけ上がったか

発表ページの比較表から、Sonnet 5 と Sonnet 5.5 の列を抜き出しました。

| 何のテストか | 分野 | Sonnet 5 | Sonnet 5.5 |
|---|---|---|---|
| Terminal-Bench 4.0 | プログラム作成の自動化 | 10.3% | 70.6% |
| FrontierCode 1.1（Main・Max効果） | プログラム作成の自動化 | 42.4% | 46.2% |
| CursorBench 4.0 | プログラム作成の自動化 | 34.1% | 55.5% |
| GDPval-AA v2.1 | 事務の仕事 | 1449 | 1844 |
| AA-Briefcase v1.1 | 事務の仕事 | 1359 | 1811 |
| Humanity's Last Exam（道具あり） | 幅広い分野の推論 | 54.9% | 64.5% |
| OSWorld 2.1（部分点あり） | パソコン操作 | 57.0% | 80.1% |
| Chartography（道具なし） | グラフの読み取り | 15.6% | 61.6% |

出典: すべて <https://www.anthropic.com/claude-sonnet-5-5>

<figure class="figure">
<img src="/static/images/sonnet55-bench.svg" alt="Sonnet 5とSonnet 5.5の点数を比べた横棒グラフ。Terminal-Bench 4.0は10.3％から70.6％、FrontierCode 1.1（Max効果）は42.4％から46.2％、CursorBench 4.0は34.1％から55.5％、Humanity's Last Examの道具ありは54.9％から64.5％、OSWorld 2.1の部分点ありは57.0％から80.1％、Chartographyの道具なしは15.6％から61.6％。いずれもAnthropicが自社で測った値で、テストの中身も測り方も別々のため平均は取れない。">
<figcaption>％で書かれている6つの点数を、同じ目盛りで並べたもの</figcaption>
</figure>

<mark>いちばん差が大きいのはTerminal-Bench 4.0で、10.3%から70.6%に上がりました</mark>。公式はこの項目について「Sonnet 5の最高点を、1タスクあたり10分の1未満の費用で超えた」と説明しています（出典: 同上）。

いくつかのテストでは、Sonnet 5.5（Max効果）はOpus 5.5と同程度の点数になると公式も書いています。ただし公式は続けて、「ベンチマークの点数はモデルの能力の一面しか捉えていない。継続的な判断力が要る複雑で自由度の高い作業では、Opus 5.5のほうが明らかに上」とも説明しています（出典: 同上）。

GDPval-AAとAA-Briefcaseは、外部の計測会社（Artificial Analysis）が Sonnet 5.5 の公開前の版で測った値です。公式の注記によると、当時は構造化出力の応答が劣化するバグがありました（現在は修正済み）。影響があるとすれば、点数を低く見せる方向だとしています（出典: 同上）。

Sonnet 5 と他社の比較は [Claude Opus 5 の記事](/tools/claude-opus-5/) に、Opus 5.5 の中身は [Claude Opus 5.5 の記事](/tools/claude-opus-5-5/) に書いています。

## 他社の上位モデルと比べると

### 単価

各社の公式料金ページから直接取った数字だけを並べます。

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | 読み直し（キャッシュ読み取り） | キャッシュ書き込み |
|---|---|---|---|---|---|
| Claude Sonnet 5.5 | Anthropic | $2 | $10 | $0.20 | $2.50（5分）/ $4（1時間） |
| Claude Sonnet 5 | Anthropic | $2 | $10 | $0.20 | $2.50（5分）/ $4（1時間） |
| Claude Opus 5.5 | Anthropic | $4 | $20 | $0.20 | $5（5分） |
| GPT-6 Astra | OpenAI | $10.00 | $50.00 | $1.00 | $12.50 |
| GPT-6 Sol | OpenAI | $2.00 | $10.00 | $0.20 | $2.50 |
| Gemini 3.1 Pro Preview | Google | $2.00（20万トークン以下）/ $4.00（超過時） | $12.00（20万トークン以下）/ $18.00（超過時） | $0.20（20万トークン以下）/ $0.40（超過時） | 公表されていない |

出典: Claude は <https://platform.claude.com/docs/en/models/sonnet-5-5/overview>・<https://platform.claude.com/docs/en/models/sonnet-5/overview>・<https://platform.claude.com/docs/en/about-claude/pricing>、OpenAI は <https://developers.openai.com/api/docs/pricing>、Google は <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/sonnet55-vendor-price.svg" alt="6つのモデルの単価を比べた横棒グラフ。100万トークンあたりのドル。Claude Sonnet 5.5は入力2ドル・出力10ドル、Claude Sonnet 5も入力2ドル・出力10ドルで同額、Claude Opus 5.5は入力4ドル・出力20ドル、GPT-6 Astraは入力10ドル・出力50ドル、GPT-6 Solは入力2ドル・出力10ドルでSonnet 5.5と完全に一致、Gemini 3.1 Pro Previewは入力2ドル・出力12ドル。Geminiは20万トークン以下のときの値段。会社ごとにトークンの数え方が違うため、単価の安さは支払額の安さを意味しない。">
<figcaption>単価だけを並べたところ。この並びは「支払いの安さ」ではありません</figcaption>
</figure>

<mark>Claude Sonnet 5.5 と OpenAI の GPT-6 Sol は、単価が4項目とも一致しています</mark>（両社の公式料金ページで確認）。

- 入力: どちらも$2
- 出力: どちらも$10
- 読み直し（キャッシュ読み取り）: どちらも$0.20
- キャッシュ書き込み（5分保持）: どちらも$2.50

Anthropicにはこのほかに「1時間保持」のキャッシュ書き込み枠（$4）があります。OpenAIの料金表には、対応する行がありません。

**GPT-6 AstraはSonnet 5.5の5倍の単価です。**AstraはOpenAIの最上位モデルです。Sonnet 5.5と同じ「中位〜上位」の帯にいるのは、GPT-6 Solのほうです。

<mark class="warn">単価が同じでも、会社ごとにトークンの数え方が違うため、支払う金額が同じとは限りません。</mark>

### 仕様

| モデル | 一度に読める量 | 一度に書ける量 | 学習データの締め切り |
|---|---|---|---|
| Claude Sonnet 5.5 | 100万トークン | 12.8万トークン | 2026年6月 |
| Claude Sonnet 5 | 100万トークン | 12.8万トークン | 2026年1月 |
| GPT-6 Astra | 1,050,000トークン | 128,000トークン | 2026年4月30日 |
| GPT-6 Sol | 1,050,000トークン | 128,000トークン | 2026年4月20日 |
| Gemini 3.1 Pro Preview | 1,048,576トークン | 65,536トークン | 公表されていない |

出典: Claude は各モデルページ（前掲）、OpenAI は <https://developers.openai.com/api/docs/models/gpt-6-astra> と <https://developers.openai.com/api/docs/models/gpt-6-sol>、Google は <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview>

<mark>一度に書ける量は4モデルとも同じです</mark>。Sonnet 5.5・Sonnet 5・GPT-6 Astra・GPT-6 Solは、いずれも12.8万（128,000）トークンです。一度に読める量も、Claudeの2モデルは100万、OpenAIの2モデルは105万トークンとほぼ同じ規模です。<mark>学習データの締め切りは、Sonnet 5.5（2026年6月）がこの3社5モデルの中でいちばん新しくなりました</mark>。OpenAIの2モデルは4月、Sonnet 5は1月です。Geminiは締め切りが公式ページに書かれていません。

### 性能テスト（Anthropicの表に載っている範囲）

発表ページの比較表には GPT-6 Sol の列もあります。

| 何のテストか | Sonnet 5.5 | GPT-6 Sol |
|---|---|---|
| FrontierCode 1.1（Main） | 46.2% | 49.3% |
| GDPval-AA v2.1 | 1844 | 1487 |
| AA-Briefcase v1.1 | 1811 | 1483 |
| Chartography（道具なし） | 61.6% | 53.6% |

出典: すべて <https://www.anthropic.com/claude-sonnet-5-5>（Terminal-Bench・CursorBench・Humanity's Last Exam・OSWorldの列にGPT-6 Solの値は載っていません）

FrontierCodeだけはGPT-6 Solのほうが高い点です。それ以外の3項目はSonnet 5.5が上回っています。ただし前述のとおり、GDPval-AAとAA-Briefcaseは公開前の版で測られた値です。

<mark class="warn">ここに並ぶのは、測る側も条件もばらばらの数字です。公式の数字で言い切れるのは単価の並びまでで、「どれが賢いか」ではありません。</mark>

## この記事で分からないこと

- 実際に使ったときの体感
- 日本語での文章の品質
- 出力速度「30%以上」の具体的な測り方
- Claude Haiku 5.5 の中身

どれも公式ページに数字がなく、運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Claude Sonnet 5.5 の発表（Anthropic・2026年9月28日）: <https://www.anthropic.com/claude-sonnet-5-5>
2. Claude Sonnet 5.5 のモデルのページ（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/sonnet-5-5/overview>
3. What's new in Claude Sonnet 5.5（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/sonnet-5-5/whats-new-sonnet-5-5>
4. Claude Sonnet 5 のモデルのページ（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/sonnet-5/overview>
5. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
6. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
7. GPT-6 Astra のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-6-astra>
8. GPT-6 Sol のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-6-sol>
9. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
10. Gemini 3.1 Pro Preview のモデルページ（Google 公式）: <https://ai.google.dev/gemini-api/docs/models/gemini-3.1-pro-preview>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
