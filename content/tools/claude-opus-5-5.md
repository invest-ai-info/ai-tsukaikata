---
title: Opus 5を5.5に替えると費用は40%減——ただし4つの設定はエラーで止まる
description: 2026年9月22日に出た Claude Opus 5.5 に、Opus 5 から乗り換えるとどうなるかを使い方ごとにまとめました。チャットで使う人は文章が読みやすくなり、API の人は費用が公式の説明で40%減ります。ただし「考える」を切る設定など4つはエラーで止まるので、先に直す必要があります。数字は Anthropic・OpenAI・Google の公式ページのものだけです。
category: tools
scene: choose
published: 2026-09-23
checked: 2026-09-23
tags: [Claude, モデル比較, 料金, AI最新情報]
---

## 結論：使い方ごとに、こうなります

Anthropic は 2026年9月22日に **Claude Opus 5.5** を出しました（出典: <https://www.anthropic.com/news/claude-opus-5-5>）。Opus 5 から乗り換えたときの結果は、使い方で分かれます。

| どんな使い方か | やること | どうなるか |
|---|---|---|
| **Claude のアプリでチャットしている** | Opus 5.5 を選んで使う | 返事が読みやすくなる。Pro・Max・Team などは5時間ごとの利用上限が上がる |
| **API で Opus 5 を使っている（特別な設定なし）** | モデル名を `claude-opus-5-5` に替える | 費用は公式の説明で**約40%減**。ただし既定の「考える量」が1段下がる |
| **API で「考える」を切るなどの設定を使っている** | **先に設定を直してから**替える | 直さずに替えると、**400エラーで止まる** |

一言でいうと、<mark>値段は下がり、文章は読みやすくなった。ただし自動化の設定によっては、替えた瞬間に止まる</mark>。

先に断っておきます。**この記事は運営者が Opus 5.5 を試した記録ではありません。**公式ページに書かれていることを読んで、使い方ごとに整理したものです。

ここから下は、表の3行がなぜそうなるのかの説明です。

## なぜそうなるのか

### 費用が40%下がる理由

理由は2つあります。どちらも公式の説明です（出典: <https://www.anthropic.com/news/claude-opus-5-5>）。

1. **単価が下がった。**入力と出力で20%、「読み直し」で60%
2. **1つの仕事に使う量が減った。**公式は「トークンあたりも安く、1つの仕事あたりのトークンも少ない」と書いています

この2つを合わせて、<mark>既定の設定・ふつうの使い方で、Opus 5 より40%安い</mark>というのが公式の数字です。

単価の違いは次のとおりです。

| 100万トークンあたり | Claude Opus 5 | Claude Opus 5.5 |
|---|---|---|
| 入力 | $5 | **$4** |
| 出力 | $25 | **$20** |
| 読み直し（キャッシュ読み取り） | $0.50 | **$0.20** |
| キャッシュ書き込み（5分） | $6.25 | **$5** |
| まとめ処理（Batch）の入力 / 出力 | $2.50 / $12.50 | **$2 / $10** |
| 速いモードの入力 / 出力 | $10 / $50 | **$8 / $40** |

出典: <https://platform.claude.com/docs/en/about-claude/pricing>

<figure class="figure">
<img src="/static/images/opus55-what-changed.svg" alt="Opus 5 から Opus 5.5 への変化を2列で比べた図。変わらないもの＝読める量100万トークン、書ける量12.8万トークン、読める形式は文章と画像、データを残さない契約で使えること。変わったもの＝100万トークンあたりの入力が5ドルから4ドル、出力が25ドルから20ドルで20%減、読み直しの料金が0.50ドルから0.20ドルで60%減、知識の締め切りが2026年5月から6月、考える量の既定値が high から medium、考える機能を切れなくなった、道具の強制指定ができなくなった。">
<figcaption>器の大きさは同じで、値段と決まりが変わりました</figcaption>
</figure>

**一番大きく下がったのは「読み直し」です。**読み直しとは、一度読ませた資料を、次の質問でもう一度読むぶんの料金です。公式は、自動で長く作業させる使い方では<mark>この読み直しが費用の大半を占める</mark>と説明しています。

公式が挙げた具体例も2つあります。

| 何をさせたか | Opus 5 | Opus 5.5 |
|---|---|---|
| 架空の会社どうしの合併を分析し、Excel と説明資料を作る | 93分 | 63分・費用は50%少ない |
| 20万行のプログラムを点検して直す（先行利用者の例） | 20時間超 | 3時間未満 |

出典: <https://www.anthropic.com/news/claude-opus-5-5>

<mark class="warn">40%は Anthropic 自身のテストの値です。自分の使い方で同じだけ下がるとは限りません。</mark>単価が20%下がっていることだけは、どの使い方でも確かです。

### 返事が読みやすくなる理由

公式は、Opus 5 への不満で多かったのが「文章の分かりにくさ」だったと認めています。そこを直したと書いています（出典: <https://www.anthropic.com/news/claude-opus-5-5>）。

公式が挙げている変更は4つです。

- 大事なことを先に書く
- 専門用語や癖のある言い回しを使いにくくした
- 利用者が渡した「書き方の決まり」に従う
- 長い作業のあいだも、ひと目で分かるメッセージにする

発表ページには、同じ依頼への2つの返事が並べて載っています。たとえば「Slack のやり取りを上司向けに3点でまとめて」という依頼です。

- どちらの返事も「問題」「すぐやった対応」「これからの対応」の3つに分かれていました
- Opus 5 は、1つの文にカッコ書きで事実をいくつも詰め込んでいました
- Opus 5.5 は文を短く分け、誰がやったか・もう済んだかを項目ごとに書いていました

これは Anthropic が選んで載せた例です。<mark class="warn">毎回こうなるかは、公式ページからは分かりません</mark>。

有料プランの利用上限についても、発表ページに2つ書かれています（出典: 同上）。

- **5時間ごとの利用上限を引き上げる。**対象は Pro・Max・Team と、席ごとに契約する Enterprise
- **利用上限のリセットを1回もらえる。**取っておいて、好きなときに使える

引き上げ幅は書かれていません。だからこの記事にも書けません。

### 4つの設定が止まる理由

Opus 5.5 は、「考える」機能が**常にオン**になりました。道具を強制する指定も受け付けません。そのため、Opus 5 で動いていた設定のうち**4つがエラーになります**（出典: <https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5>）。

| 設定 | Opus 5 | Opus 5.5 |
|---|---|---|
| 「考える」を切る指定 | `high` 以下なら切れる | **400エラー**（常にオン） |
| 考える量をトークン数で決める指定 | —— | **400エラー**（`effort` で決める） |
| 道具を強制する指定（`any` / `tool`） | できる | **400エラー**（`auto` と `none` だけ） |
| 古いパソコン操作の道具（`computer_20251124`） | 使える | **Claude API と Google Cloud では400エラー** |

<mark class="warn">モデル名だけ書き換えて乗り換えると、上の設定を使っている自動化はその場で止まります</mark>。

公式が示している直し方は、次の順番です（出典: 同上）。

1. モデル名を `claude-opus-5` から `claude-opus-5-5` に変える
2. 「考える」を切る設定を消し、代わりに `effort`（どれだけ考えるか）を下げる
3. 道具の強制指定は `auto` に戻し、「どの場面でその道具を使うか」を指示文に書く
4. パソコン操作は、新しい道具（`computer_toolset_20260801`）に移す

エラーにはならないけれど、気づきにくい変化も3つあります（出典: 同上）。

- **既定の「考える量」が high から medium に下がった。**何も指定しないと、Opus 5 より浅く考えます
- **同じ設定なら、Opus 5 より多く考える。**特に `xhigh` と `max` で多いので、出力の上限に余裕を残すよう公式は勧めています
- **道具を使う合間のメモが画面に出なくなる。**途中経過を利用者に見せている仕組みは、黙ったままになります

### 性能はどれだけ上がったか

発表ページの表から、Opus 5 と Opus 5.5 の列を抜き出しました。

| 何のテストか | 分野 | Opus 5 | Opus 5.5 |
|---|---|---|---|
| Terminal-Bench 4.0 | プログラム作成の自動化 | 52.3% | 66.4% |
| FrontierCode v1.1 | プログラム作成の自動化 | 48.0% | 54.4% |
| CursorBench 4.0 | プログラム作成の自動化 | 46.6% | 57.8% |
| GDPval-AA v2.1 | 事務の仕事（44職種） | 1708 | 1846 |
| AutomationBench | 業務の自動化 | 26.9% | 40.0% |
| Humanity's Last Exam（道具あり） | 幅広い分野の推論 | 63.6% | 67.7% |
| Terminal-Bench-Science 0.1 | 科学研究の自動化 | 29.0% | 58.7% |
| OSWorld 2.0（部分点あり） | パソコン操作 | 74.0% | 81.8% |
| Chartography（道具あり） | グラフの読み取り | 83.4% | 89.0% |

出典: すべて <https://www.anthropic.com/news/claude-opus-5-5>

<figure class="figure">
<img src="/static/images/opus55-bench.svg" alt="Opus 5 と Opus 5.5 の点数を比べた横棒グラフ。Terminal-Bench 4.0 は52.3％から66.4％、FrontierCode v1.1 は48.0％から54.4％、CursorBench 4.0 は46.6％から57.8％、AutomationBench は26.9％から40.0％、Humanity’s Last Exam の道具ありは63.6％から67.7％、Terminal-Bench-Science 0.1 は29.0％から58.7％、OSWorld 2.0 の部分点ありは74.0％から81.8％、Chartography の道具ありは83.4％から89.0％。AutomationBench は Zapier が、それ以外は Anthropic が自社で測った値で、テストの中身も測り方も別々のため平均は取れない。">
<figcaption>％で書かれている8つの点数を、同じ目盛りで並べたもの</figcaption>
</figure>

9項目すべてで Opus 5 を上回っています。ただし、読むときの注意が4つあります。

- **測ったのは、ほぼ Anthropic 自身です。**AutomationBench だけは Zapier が測った値です
- **点数は最大の設定（max）のものです。**既定の設定（medium）で使うと、この点数にはなりません
- **安全装置が働いた課題は、別のモデルが解いています。**公式は「Opus 5.5 の点数を下げている可能性が高い」と注記しています
- **公式自身が「点差ほど差は無い」と書いています。**<mark>社内で使うと、Opus 5.5 と Fable 5.1 の差は点数より小さい</mark>という説明です

Opus 5 の中身は [Claude Opus 5 は何が変わったのか](/tools/claude-opus-5/) に書いています。上位モデルの話は [Claude Fable 5.1 の記事](/tools/claude-fable-5-1/) にあります。

## 他社の上位モデルと比べると

### 単価

各社の公式料金ページから直接取った数字だけを並べます。

| モデル | 提供元 | 入力（100万トークン） | 出力（100万トークン） | 読み直し（キャッシュ読み取り） |
|---|---|---|---|---|
| Claude Opus 5.5 | Anthropic | $4 | $20 | $0.20 |
| Claude Opus 5 | Anthropic | $5 | $25 | $0.50 |
| Claude Fable 5.1 | Anthropic | $10 | $50 | $0.25 |
| GPT-6 Astra | OpenAI | $10.00（短）/ $20.00（長） | $50.00（短）/ $75.00（長） | $1.00（短）/ $2.00（長） |
| GPT-6 Sol | OpenAI | $2.00（短）/ $4.00（長） | $10.00（短）/ $15.00（長） | $0.20（短）/ $0.40（長） |
| Gemini 3.1 Pro Preview | Google | $2.00（20万トークン以下）/ $4.00（超過時） | $12.00（20万トークン以下）/ $18.00（超過時） | $0.20（20万トークン以下）/ $0.40（超過時） |

出典: Claude は <https://platform.claude.com/docs/en/about-claude/pricing>、GPT は <https://developers.openai.com/api/docs/pricing>、Gemini は <https://ai.google.dev/gemini-api/docs/pricing>

<figure class="figure">
<img src="/static/images/opus55-vendor-price.svg" alt="6つのモデルの単価を比べた横棒グラフ。100万トークンあたりのドル。Claude Opus 5.5 は入力4ドル・出力20ドル、Claude Opus 5 は入力5ドル・出力25ドル、Claude Fable 5.1 は入力10ドル・出力50ドル、GPT-6 Astra は入力10ドル・出力50ドル、GPT-6 Sol は入力2ドル・出力10ドル、Gemini 3.1 Pro Preview は入力2ドル・出力12ドル。GPT と Gemini は短い入力のときの値段。会社ごとにトークンの数え方が違うため、単価の安さは支払額の安さを意味しない。">
<figcaption>単価だけを並べたところ。この並びは「支払いの安さ」ではありません</figcaption>
</figure>

読むときの注意が3つあります。

- **トークンの数え方が会社ごとに違います。**<mark>単価が安くても、支払いが安いとは限りません</mark>
- **OpenAI と Google は、入力が長くなると単価が上がります。**Google は「20万トークンを超えたら」と明記しています。OpenAI の料金ページは「短い」「長い」の境目を書いていません
- **Gemini 3.1 Pro は試用版（Preview）の表示です。**長く使う前提なら、値段が変わりうると考えてください

GPT-6 Astra の中身は [GPT-6 Astra の記事](/tools/gpt-6-astra/) に書いています。

### 性能テスト（Anthropic の表に載っている範囲）

発表ページの表には OpenAI のモデルの列もあります。ただし OpenAI のモデルの点数の多くは、「OpenAI が報告した値」と注記されています（出典: <https://www.anthropic.com/news/claude-opus-5-5>）。

| 何のテストか | Opus 5.5 | Fable 5.1 | GPT-6 Astra |
|---|---|---|---|
| Terminal-Bench 4.0 | 66.4% | 55.8% | 57.9% |
| FrontierCode v1.1 | 54.4% | 50.3% | 53.3% |
| GDPval-AA v2.1 | 1846 | 1735 | 1542 |
| AutomationBench | 40.0% | 31.4% | 41.4% |
| Terminal-Bench-Science 0.1 | 58.7% | 52.6% | 64.6% |

出典: すべて <https://www.anthropic.com/news/claude-opus-5-5>

<mark>公式の表でも、Opus 5.5 が全部で上とは限りません</mark>。AutomationBench と Terminal-Bench-Science 0.1 は、GPT-6 Astra のほうが高い値です。

ここに並ぶのは、測る側も条件もばらばらの数字です。<mark class="warn">公式の数字で言い切れるのは単価の並びまでで、「どれが賢いか」ではありません</mark>。

## この記事で分からないこと

- 実際に使ったときの体感
- 日本語での文章の品質
- 5時間ごとの利用上限がどれだけ増えるか
- Sonnet 5.5 と Haiku 5.5 の中身（公式は「数週間のうちに」出すと書いています）

どれも公式ページに数字がなく、運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Claude Opus 5.5 の発表（Anthropic・2026年9月22日）: <https://www.anthropic.com/news/claude-opus-5-5>
2. Claude Opus 5.5 のモデルのページ（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/opus-5-5/overview>
3. What's new in Claude Opus 5.5（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/opus-5-5/whats-new-opus-5-5>
4. Claude Opus 5 のモデルのページ（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/models/opus-5/overview>
5. 料金（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
6. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
7. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
