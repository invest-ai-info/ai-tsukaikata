---
title: AWS経由でOpenAIを使う——同じモデルでも直接より高い
description: 2026年8月11日に AWS が発表した OpenAI の Daybreak Red / Daybreak Blue について、Amazon Bedrock のモデルカードと OpenAI の料金ページに書かれている数字だけを突き合わせました。同じモデルなのに AWS 経由のほうが高く、しかも上げ幅がモデルごとに違います。
category: tools
scene: choose
published: 2026-08-21
checked: 2026-08-21
tags: [OpenAI, Amazon Bedrock, AWS, モデル比較, 料金, AI最新情報]
---

## 何が変わったか

AWS は2026年8月11日、OpenAI の **Daybreak Red** と **Daybreak Blue** を Amazon Bedrock で使えるようにしたと発表しました（出典: <https://aws.amazon.com/blogs/machine-learning/accelerate-cyber-defense-with-openai-and-aws-daybreak-red-daybreak-blue-now-available-to-eligible-customers-on-amazon-bedrock/>）。3行にすると、こうなります。

- 中身は新しいモデルではありません。**Daybreak Red は GPT-5.6 Cyber、Daybreak Blue は GPT-5.6 Sol に防御向けの安全装置を付けたもの**だと AWS は説明しています（出典: 同上）。
- <mark>使えるのは米国東部オハイオだけで、審査を通った相手にしか開かれていません</mark>。OpenAI の「Trusted Access for Cyber」に登録して承認される必要があります（出典: 同上）。
- <mark>同じモデルでも、AWS 経由のほうが高くなっています</mark>。Amazon Bedrock の値段と OpenAI が直接出している値段を並べると、Red は1.1倍、Blue は入力が1.375倍・出力が1.65倍でした（倍率はこの記事の割り算。もとの数字は下の表）。

先に断っておきます。**この記事は運営者がこれを使った記録ではありません。**各社の公式ページに書かれていることを読んで整理したものです。使用感は一切書いていません。

<mark class="warn">それどころか、OpenAI 側の発表ページはこの記事を書いた環境から開けませんでした</mark>。`openai.com/index/daybreak-models-are-now-available-on-aws` は、何度叩いても Cloudflare の判定で 403 が返ってきます。そこで**この記事は、同じ発表を AWS 自身が同じ日に出したブログ**（著者3人のうち1人は OpenAI の担当者です）**と、両社の公式ドキュメントだけ**で書いています。まとめ記事やニュースサイトは1件も使っていません。

## 何をするためのモデルなのか

読者の大半には直接は関係のない話なので、先に位置づけだけ書きます。

AWS のブログによれば、この2つは**脆弱性を見つけてから直すまでの工程**を速くするためのものです。Blue のほうが入口で、脆弱性の発見・検知の仕組みづくり・事故対応に使う。Red はもっと踏み込んだ用途で、脆弱性の研究・再現・緩和策の開発に使う、と説明されています（出典: 同上）。

セキュリティの作業は、頼み方だけを見ると攻撃と区別がつきません。だから普通のモデルは断ります。この2つは**「誰が使っているか・どこで動いているか・どんな管理下にあるか」で線を引く**という設計だ、とブログには書かれています（出典: 同上）。

効果として挙げられている例は1つです。GPT-5.6 Cyber を Daybreak Red 経由で使った研究者が、Chrome の JavaScript エンジン V8 に未知の脆弱性を2件見つけ、最初の1件が CVE-2026-15903 として修正された。2026年の V8 CTF でゼロデイとして成功した4件のうちの1つだ、というものです（出典: 同上）。<mark class="warn">ただしこの記述には「According to OpenAI（OpenAI によれば）」と前置きが付いています</mark>。AWS が自分で確かめた数字としては書かれていません。

## 前のモデルとの違い

「前のモデル」にあたるのは、同じ GPT-5.6 の汎用版です。ここが本題なので、値段を並べます。

### AWS 経由と直接契約で、値段が違う

100万トークンあたりのドル、標準（Standard）の値です。AWS 側は同一リージョンで処理する場合の値です。

| | OpenAI と直接 | AWS 経由（Bedrock） |
|---|---|---|
| Daybreak Red・入力 | $12.50 | $13.75 |
| Daybreak Red・出力 | $75.00 | $82.50 |
| Daybreak Blue・入力（短い） | $4.00 | $5.50 |
| Daybreak Blue・出力（短い） | $20.00 | $33.00 |
| Daybreak Blue・入力（長い） | $8.00 | $11.00 |
| Daybreak Blue・出力（長い） | $30.00 | $49.50 |

出典: 直接の値は <https://developers.openai.com/api/docs/pricing>（Cyber models の表）、AWS 経由の値は <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-cyber.html> と <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-daybreak-blue-56-sol.html>

<figure class="figure">
<img src="/static/images/daybreak-bedrock-vs-direct.svg" alt="OpenAI と直接契約したときと Amazon Bedrock 経由のときで、同じモデルの単価を比べた横棒グラフ。100万トークンあたりのドル。Daybreak Red の入力は直接12.50ドルに対し AWS 経由が13.75ドル、出力は直接75.00ドルに対し AWS 経由が82.50ドル。Daybreak Blue の入力は直接4.00ドルに対し AWS 経由が5.50ドル、出力は直接20.00ドルに対し AWS 経由が33.00ドル。Red は1.1倍だが、Blue は入力が1.375倍・出力が1.65倍で、上げ幅が揃っていない。倍率は記事側の割り算で、上げ幅が揃わない理由はどちらのページにも書かれていない。">
<figcaption>同じモデルでも、通す場所で値段が変わります</figcaption>
</figure>

割り算するとこうなります。**Red は入力も出力もちょうど1.1倍**です（13.75 ÷ 12.50、82.50 ÷ 75.00）。<mark class="warn">Blue は入力が1.375倍・出力が1.65倍で、同じ日に同じ経路で出た2つなのに上げ幅が揃っていません</mark>（5.50 ÷ 4.00、33.00 ÷ 20.00）。この倍率は記事側で割り算した値です。

高くなること自体は隠されていません。<mark>OpenAI の料金ページには「Amazon Bedrock 上の OpenAI モデルは AWS を通して請求され、直接の料金と違うことがあります」と書かれています</mark>（出典: <https://developers.openai.com/api/docs/pricing>）。同じ説明は、OpenAI が出している Bedrock 向けの案内にもあります（出典: <https://developers.openai.com/api/docs/guides/amazon-bedrock>）。

**上げ幅が揃わない理由は、どちらのページにも書かれていません。**手がかりになりそうな但し書きが1つだけあります。OpenAI の料金ページには「GPT-5.6 Sol の割引価格は、少なくとも2026年11月21日までは続きます」と書かれています（出典: <https://developers.openai.com/api/docs/pricing>）。**Blue の中身は GPT-5.6 Sol なので、直接側だけが割引中なら差は開きます。**ただし AWS 側がその割引を反映しているのかどうかは、どこにも書かれていないので、ここは推測にしかなりません。書かれていないことは書きません。

### 安全装置に追加料金はかかっていない

もう1つ、同じモデルカードから分かることがあります。

| | 入力（短い） | 出力（短い） |
|---|---|---|
| 汎用の GPT-5.6 Sol・Global 経路 | $5.00 | $30.00 |
| 汎用の GPT-5.6 Sol・同一リージョン | $5.50 | $33.00 |
| Daybreak Blue・同一リージョン | $5.50 | $33.00 |

出典: <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-sol.html> と <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-daybreak-blue-56-sol.html>

<figure class="figure">
<img src="/static/images/daybreak-blue-same-price.svg" alt="Amazon Bedrock 上での単価を比べた横棒グラフ。100万トークンあたりのドル。汎用の GPT-5.6 Sol は Global 経路なら入力5.00ドル・出力30.00ドル、同じリージョン内で処理する経路なら入力5.50ドル・出力33.00ドル。安全装置つきの Daybreak Blue も入力5.50ドル・出力33.00ドルで、汎用と同額。ただし Daybreak Blue は Geo 経路も Global 経路も Not supported と書かれており、一番安い Global 経路を選べない。長い文脈（100万トークン）の行は Blue にだけあり、入力11.00ドル・出力49.50ドル。">
<figcaption>同じ値段に見えますが、選べる経路が1つ減っています</figcaption>
</figure>

<mark>安全装置が付いても、値段は汎用モデルと同じです</mark>。同一リージョンで処理する場合、どちらも $5.50 / $33.00 です。

ただし、そこで終わりではありません。<mark>汎用の Sol が選べる一番安い Global 経路を、Daybreak Blue は選べません</mark>。汎用の Sol のモデルカードには Global 経路の行があって $5.00 / $30.00 ですが、Daybreak の2つは Geo も Global も「Not supported」と書かれています（出典: 上記の3枚のモデルカード）。**同じ中身でも、安く済ませる選び方だけが最初から消えています。**

### 値段より先に、選べる幅が狭い

<figure class="figure">
<img src="/static/images/daybreak-what-is-closed.svg" alt="Amazon Bedrock のモデルカード3枚に書かれている条件を並べた表。汎用の GPT-5.6 Sol は事前の審査が要らず、米国・欧州・アジアの多数のリージョンの表があり、東京もその表にあり、Geo 経路と Global 経路が使えて、一度に100万トークン読める。Daybreak Blue と Daybreak Red はどちらも事前の審査が要り、リージョンの表は米国東部オハイオの1行だけで東京は無く、Geo 経路も Global 経路も使えず、微調整もできない。一度に読める量は Blue が100万トークン、Red は27.2万トークン。速い層（Priority）と安い層（Flex）は、汎用の Sol を含む3つとも使えないと書かれている。審査は OpenAI の Trusted Access for Cyber への登録で、承認後に AWS 側で申請する必要がある。">
<figcaption>単価を見比べる前に、ここで選択肢が決まります</figcaption>
</figure>

表の読み方を3つだけ補います。

**リージョン。**Daybreak の2つは、**モデルカードのリージョン表にオハイオの1行しかありません**。汎用の Sol のほうには東京・大阪を含む多数の行が並んでいます（出典: 上記の3枚のモデルカード）。**日本国内で処理させたい仕事には、そもそも使えません。**

**読める量。**Blue は一度に100万トークン読めますが、**Red には長い入力の値段が載っていません**。Red のモデルカードにある値段の表は「短い文脈（27.2万トークン）」の1つだけで、読める量も27.2万トークンと書かれています（出典: <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-cyber.html>）。OpenAI の料金ページでも、`gpt-5.6-cyber` の長い入力の列は4つともハイフンです（出典: <https://developers.openai.com/api/docs/pricing>）。**2つのページが同じことを言っている**ので、これは書き漏れではなさそうです。

**データの扱い。**AWS のブログには、推論に使ったデータはモデルの学習には使わないこと、OpenAI とのデータ共有に同意する必要はないこと、不正利用の検知で印が付いた通信だけを AWS が最大30日保持し、それも申請すれば保持しないようにできること、が書かれています（出典: 上記の AWS ブログ）。

## 他社の最上位モデルとの比較

「防御する側に強いAIを渡す」という話自体は他社もやっています。ただし**出し方が違うので、値段を1本の表に並べても比較になりません。**

<figure class="figure">
<img src="/static/images/daybreak-vendor-shapes.svg" alt="同じサイバー防御向けの取り組みを、3社がどういう形で出しているかを並べた図。OpenAI は AWS 経由で、審査を通った相手だけに専用モデルを別料金で開いており、Amazon Bedrock の同一リージョンでの標準価格は100万トークンあたり Daybreak Red が入力13.75ドル・出力82.50ドル、Daybreak Blue が入力5.50ドル・出力33.00ドル。2026年8月11日発表で、米国東部オハイオのみ、Trusted Access for Cyber への登録が必要。Anthropic は専用モデルではなく Claude Code に組み込んだ機能 Claude Code Security として出しており、2026年2月20日発表の限定リサーチプレビューで、Enterprise と Team 向け、別料金の記載はない。Google は Gemini API のモデル一覧に専用モデルを載せておらず、同じ形の発表はこの記事を書いた時点では見つかっていない。">
<figcaption>値段を比べる前に、そもそも売り方が違います</figcaption>
</figure>

<mark>Anthropic は専用モデルではなく、Claude Code に組み込んだ機能として出しています</mark>。2026年2月20日に発表された「Claude Code Security」で、コードを読んで脆弱性を探し、修正案を出す。人が承認するまで何も適用されない、と説明されています（出典: <https://www.anthropic.com/news/claude-code-security>）。提供は限定リサーチプレビューで、Enterprise と Team の顧客向け、オープンソースの維持者は無料で優先的に使える、とも書かれています（出典: 同上）。**モデル単位の別料金は書かれていません。**

Google は、Gemini API のモデル一覧にサイバーセキュリティ専用のモデルを載せていません（出典: <https://ai.google.dev/gemini-api/docs/models>）。

<mark class="warn">ここは「他社にはない」という意味ではありません</mark>。この記事が確かめたのは、上に挙げたページに何が書かれているかだけです。別のページや別の売り方で提供されている可能性は残ります。**確かめていないことを「無い」とは書きません。**

数字で比べられるところを1つだけ挙げると、Anthropic は Claude Opus 4.6 を使って公開されているソフトの中から500件を超える脆弱性を見つけたと書いています（出典: <https://www.anthropic.com/news/claude-code-security>）。OpenAI 側の数字は先ほどの V8 の2件です。**どちらも自社の発表であって、同じ条件で測ったものではありません。**並べても優劣は出ません。

## どういう人に効くか

**関係がある人**

- 会社がすでに AWS を使っていて、AI の請求・権限・監査ログを AWS 側にまとめたい人。この発表はそこが本題です。
- セキュリティの担当で、社外にコードを出せない事情がある人。ただし審査が要り、使えるのは米国東部だけです。

**この記事で本当に持ち帰ってほしいこと**

大半の会社員には Daybreak そのものは関係ありません。ただし**この話には、審査制ではない普通のモデルにもそのまま当てはまる部分があります。**

- <mark>クラウド経由の値段が、直接契約と同じだと思い込まないこと</mark>。今回は同じモデルで1.1倍と1.65倍という差が付いていました。
- **同じ会社の中でも、経路によって値段が変わります。**汎用の Sol は Global 経路なら $5.00、同一リージョンなら $5.50 でした（出典: <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-sol.html>）。
- **単価より先に、使えるリージョンと機能の制限を見ること。**東京で処理できないなら、単価がいくらでも選べません。

**この記事で分からないこと**

性能の比較ができません。<mark>Daybreak Red と Blue のベンチマークの点数は、AWS のブログにも Bedrock のモデルカードにも1つも載っていません</mark>。汎用の GPT-5.6 との差がどれくらいなのかは、この記事の出典からは分かりませんでした。返答の速さ、日本語での品質、実際の使い勝手も分かりません。運営者は使っていないので書けません。

同じ GPT-5.6 の汎用モデルについては [GPT-5.6 Sol と Luna](/tools/gpt-5-6-sol-luna/) に書いています。

## 出典一覧

すべて AWS・OpenAI・Anthropic・Google の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Daybreak Red と Daybreak Blue の提供開始（AWS 公式ブログ・2026年8月11日）: <https://aws.amazon.com/blogs/machine-learning/accelerate-cyber-defense-with-openai-and-aws-daybreak-red-daybreak-blue-now-available-to-eligible-customers-on-amazon-bedrock/>
2. Daybreak Red: GPT-5.6 Cyber のモデルカード（AWS 公式ドキュメント）: <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-cyber.html>
3. Daybreak Blue: GPT-5.6 Sol のモデルカード（AWS 公式ドキュメント）: <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-daybreak-blue-56-sol.html>
4. GPT-5.6 Sol（汎用）のモデルカード（AWS 公式ドキュメント）: <https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-openai-gpt-56-sol.html>
5. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
6. Amazon Bedrock での利用（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/guides/amazon-bedrock>
7. Claude Code Security の発表（Anthropic 公式・2026年2月20日）: <https://www.anthropic.com/news/claude-code-security>
8. Gemini API のモデル一覧（Google 公式）: <https://ai.google.dev/gemini-api/docs/models>

OpenAI 自身の発表ページ（`openai.com/index/daybreak-models-are-now-available-on-aws`）には、この記事を書いた環境から到達できませんでした。そのため、発表の中身は AWS 側のブログと両社の公式ドキュメントから取っています。読めなかったものを、二次情報で埋めることはしていません。

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
