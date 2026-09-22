---
title: Udemyの取り分は97%か37%か——3,000円×100本が、誰が客を連れてきたかで291,000円と111,000円に割れる
category: recipes
scene: earn
description: 「Udemyで講座を売ると講師の取り分は何%か」をウェブ検索を切ったAIに18回実測しました。「自分の紹介リンク経由は97%、Udemy経由は37%」は3回とも当たり、原文の英文を貼った3回は3,000円×100本で291,000円と111,000円を1円単位で返しました。ところが過去の率や変更時期（50%・25%・17.5%など）は9回すべてに添えられ、その経緯は原文のどこにも載っていません。
published: 2026-09-18
checked: 2026-09-18
series: 本気で稼ぐ式
series_no: 2
series_total: 7
tags: [副業, Udemy, 講座, 取り分, 見積もり, プロンプト]
time_required: 20分
cost: 無料
---

## これで何ができるか {: .what }

Udemyは講座を「作って置く」型です。置いたあと、**誰が客を連れてきたか**で取り分が割れます。<mark>公式ヘルプでは、講師のクーポンや紹介リンク経由の販売は講師97%、それ以外（Udemyの検索や広告経由）は講師37%。同じ3,000円の講座が月に100本売れても、前者なら291,000円、後者なら111,000円です。</mark>法人向けのUdemy Businessは1本いくらではなく、定額収入の15%を講師全体のプールにして視聴された分数で按分します。

この記事は、この割れ方をAIが知っているかを**18回**実測し、本数を前提として置いたときの推定を、読者が式から出せる形にしたものです。

<mark>先に結果を書きます。97%と37%は3回とも当たり、原文の英文を貼った3回は1円単位で一致しました。外れたのは「いつ変わったか」で、過去の率や変更時期（50%・25%・17.5%・2020〜2027年）が9回すべてに添えられ、その経緯は原文のどこにも載っていません。</mark>

<figure class="figure">
<img src="/static/images/udemy-97-or-37-split.svg" alt="Udemyの講座1本が、誰が客を連れてきたかで講師の取り分が97%と37%に割れることを、3,000円の講座が月に100本売れた場合（前提）で並べた図。講師のクーポン・紹介リンク経由なら講師97%で300,000円×0.97＝291,000円／月（緑）、Udemyの検索・広告経由（紹介リンクなし）なら講師37%で111,000円／月。率が掛かるのはNet Amount（税やアプリ手数料を引いた後の額）で、iOS・Androidアプリ経由の販売は先に30%が引かれる。3段目はUdemy Business（法人向け定額）で見られた場合で、1本いくらではなく月の定額収入の15%を講師全体のプールにして視聴された分数の割合で按分する。下の枠には、差は月180,000円で2.6倍、講座の中身は同じで変わったのは誰が客を連れてきたかだけであること、作って置く型は置いた後の集客をどちらがするかで同じ本数でも取り分が割れること、本数は前提で何本売れるかの出典は無いことが書かれている。">
<figcaption>講座は同じ。変わるのは「誰が客を連れてきたか」だけ。100本は前提です。</figcaption>
</figure>

## 前提 {: .need }

| | |
|---|---|
| かかる時間 | 20分 |
| 費用 | 無料（原文に「There is no fee to create and host a course on Udemy」とあります。この記事は式を出すだけで、講座の公開は必要ありません） |
| 必要なもの | AIとの会話と、公式ヘルプ（英語）を開くブラウザ |
| プログラミング | **不要** |

⚠️ <mark>この記事は運営者がUdemyで収入を得た記録ではありません。</mark>公式ヘルプ（英語）に書かれている率の確認と、AIに聞いたときの返り方の実測です。率は変わります。この記事の率は2026-09-18に原文を開いて確認したもので、原文は英語のまま引き、訳は担当が付けています。**本数（10・30・100本）はすべてこちらが置いた前提で、売れる根拠はありません。**

📌 **実測に使ったAIについて。**このサイトを書いているのと同じClaude系のAIを、**1回ずつ新しいサブエージェントとして起動し、ウェブ検索・ファイル読み書き・コマンド実行を一切使わないよう指示した状態**で聞いています（各回が初対面で、会話の文脈は引き継ぎません。ツールを使わなかったことは記録上の `tool_uses: 0` で確認しています）。**別のAIサービスや、検索できる状態のAIでは結果が変わります。**判定は正規表現の文字列照合で、送った全文（前置きを含む）と項目名と結果は[試した証拠](https://github.com/invest-ai-info/ai-tsukaikata/blob/main/docs/evidence/udemy-97-or-37-who-brings-the-student.md)にあります。

## AIへの頼み方 {: .ask }

### 1. まず、素朴に聞いてみる

いちばん普通の聞き方から試しました。

<div class="prompt">Udemyで自分の講座を売ると、講師の取り分は売上の何%ですか。条件によって違うなら、その条件も教えてください。</div>

**3回**通しました。3回とも「講師のクーポン・紹介リンク経由は97%」「それ以外は37%」と原文どおりで、率が掛かるのが税やアプリ手数料を引いた後の額（Net Amount）であることにも3回とも触れました。Udemy Businessが「プールを視聴時間で按分する」仕組みだという説明も3回とも出ました。原文はこうです。

> Sales occurring through instructor promotions: instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.／Sales that do not occur through an instructor promotion: instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.（[Instructor revenue share](https://support.udemy.com/hc/en-us/articles/229605008-Instructor-revenue-share)・2026-09-18確認。訳＝講師の宣伝経由の販売は97%、それ以外は37%）

<mark class="warn">ただし3回とも、頼んでいない過去の率と変更時期（「2018年の改定前は検索経由50%・広告経由25%」「Udemy Businessは25%→20%→17.5%→15%と段階的に引き下げ」など）を添えました。この経緯は、担当が確認した原文のどこにも載っていません。</mark>正しいかどうかを、原文からは確かめられません。

📌 なぜこの言い方をしたか。「条件によって違うなら、その条件も」と足すと、AIは現在の条件だけでなく**知っている経緯まで並べます。**現在の率は原文で確かめられますが、経緯は確かめる手段がありません。同じ段落の中で、確かめられる数字と確かめられない数字が同じ調子で並びます。

### 2. Udemy Business の支払われ方を聞く

1本いくらではない仕組みを、知っているか聞きました。

<div class="prompt">Udemy Business（法人向けの定額プラン）で自分の講座が見られたとき、講師にはどのように支払われますか。</div>

**3回**とも「法人向け定額の収入の一定割合を講師プールにし、視聴された分数の割合で分ける」と説明し、率は3回とも15%を挙げました。原文はこうです。

> Each month, Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed across all Udemy Business courses.（[How do I earn revenue from Udemy Business and subscription plans?](https://support.udemy.com/hc/en-us/articles/115013221767-How-do-I-earn-revenue-from-Udemy-Business-and-subscription-plans)・2026-09-18確認。訳＝毎月、Udemy Businessの定額収入の15%を講師プールとし、各講師の取り分は全講座の視聴分数に占める割合と等しい）

<mark>仕組みは3回とも当たりました。ここでも3回とも、25%から段階的に下がったという経緯を添えていて、それは原文にありません。</mark>プール制は「自分の講座が何分見られたか ÷ 全講座の合計分数」で決まるので、**本数の式では推定できません。**この記事の推定はプール制を含めていません。

### 3. 原文を自分で取ってきて、計算だけAIにさせる

原文の英文4行をこちらが貼り、3,000円×100本を2つの経路で計算させました。

<div class="prompt">Udemyの公式ヘルプ（英語）で確認した情報を貼ります。これ以外の数字は使わないでください。

・Sales occurring through instructor promotions: instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.
・Sales that do not occur through an instructor promotion: instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.
・these are revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google for sales on iOS and Android.
・Each month, Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed across all Udemy Business courses.

3,000円の講座が1か月に100本売れたとして、①全部が私の紹介リンク経由だった場合 ②全部がUdemyの検索経由（紹介リンクなし）だった場合、それぞれ講師の取り分を計算してください。iOS・Androidアプリ経由の販売はゼロで、税も考えないものとします。上に無い数字は使わず、必要なら「材料に無い」と書いてください。</div>

**3回**とも「紹介リンク経由なら291,000円、Udemy経由なら111,000円、差180,000円」と1円単位で一致しました。<mark>3回とも「材料に無い」を使い、貼っていない率を1つも足しませんでした。</mark>3回とも、実際は2つの経路が混ざるので「紹介リンク経由の割合が取り分を決める」と自分から補っています。

<figure class="figure">
<img src="/static/images/udemy-ai-hit-and-miss.svg" alt="UdemyについてAIに聞いた結果を並べた表。上6行は原文と一致した回数で、紹介リンク経由97%・Udemy経由37%と述べたのが3/3、Net Amount（アプリ手数料30%を引いた後）に触れたのが3/3、Udemy Businessはプールを視聴分数で按分と述べたのが3/3、材料を貼った回に291,000円と111,000円（差180,000円）を出したのが3/3、ページ名だけの回に数字ゼロでInstructor Revenue Shareを挙げたのが3/3、数字は書かないでの確認順の回に率・金額の数字がゼロだったのが3/3で、いずれも緑。下2行は原文に無いこと・違うことを言った回数で、過去の率・変更時期を述べたのが9/9、Udemy Businessの率を現在17.5%と述べたのが1/3で、いずれも赤。下の枠には、現在の率は素朴に聞いても当たり材料を貼れば1円単位で一致したこと、過去の率や変更時期は9回とも添えられ原文には載っていないこと、率は原文を貼って計算だけさせ、いつ変わったかは聞かないという結論が書かれている。">
<figcaption>現在の率は当たる。「いつ変わったか」は原文に無い話が付きます。</figcaption>
</figure>

これは[AIに数字を「それっぽく」埋めさせないための頼み方](/recipes/numbers-not-in-the-source/)と同じ結果です。**率は原文を貼り、本数を変えた計算だけAIにさせる。**次の節の推定は、そうやって置いた前提です。

### 4. 「過去に変わったことがあるか」を、あえて聞く

経緯がどれだけ揺れるかを見るために、直接聞きました。

<div class="prompt">Udemyの講師の取り分（レベニューシェア）は、過去に変更されたことがありますか。現在の率と、変更があったなら変更前の率と時期を教えてください。</div>

**3回**とも現在の率を97%・37%と答えました。<mark class="warn">ところが変更の時期は3回で「2018年」「2020年頃」「2021年」と揺れ、Udemy Businessの率は1回が「2026年現在は17.5%」と、原文の15%と食い違いました。</mark>残り2回は「予定どおりなら現在は15%」です。3回とも「公式ヘルプで確認を」と断っていますが、**同じ質問に3回とも違う年が返る**ことが、経緯を聞かないほうがいい理由です。

## うまくいかないときの言い直し方 {: .fix }

### 率の数字をAIに言わせたくないとき {: .trouble }

率は変わるので、AIに数字を書かせず、確認する場所だけを聞くほうが安全です。

<div class="prompt">Udemyの講師の取り分（レベニューシェア）について、確認すべき公式ヘルプページの名前だけを、数字は書かずに教えてください。</div>

**3回**とも数字を1つも書かず、「Instructor Revenue Share」というページ名を挙げました（2回はUdemy Businessの配分ページにも触れました）。ページ名を聞く価値は、**AIに率と経緯を書かせないこと**にあります。

### 何をどの順に確かめればいいか分からないとき {: .trouble }

始める前に確認する箇所を、順番つきで出させました。

<div class="prompt">私はUdemyで講座を出すか検討しています。取り分や支払いの条件は変わることがあるので、自分で公式ヘルプを確認したいです。

私が確認すべき箇所を、確認する順番に並べてください。

⚠️ あなたは率や金額の数字を書かないでください。数字は私が公式ヘルプで確認します。あなたが書くのは「どこで何を確認するか」だけにしてください。</div>

**3回**とも率も金額も書かず、「誰が客を連れてきたかの判定（クーポン・紹介リンクの条件）」「Udemy Businessの配分」「支払い方法と時期・税務書類」を確認項目に入れました。<mark>「率や金額の数字を書かないで」と足すと、3回とも数字ゼロで、確認の順番だけが返りました。</mark>ただし確認項目に「W-8BEN（税務書類）」のような固有名は出ます。それは数字ではないので、原文で見る対象として扱いました。

## 応用・次の一手 {: .next }

**推定は「3,000円 × 本数 × 97%（自分の集客）または 37%（Udemyの集客）」で、本数と経路の割合が本人の頑張り次第の前提です。**

<div class="money-note">
金額の目安（推定・3,000円の講座・税とアプリ手数料は考えない）:

| 月の本数 | 全部が自分の紹介リンク経由 | 全部がUdemy経由 |
|---|---|---|
| 10本 | 29,100円 | 11,100円 |
| 30本 | 87,300円 | 33,300円 |
| 100本 | 291,000円（準本業帯） | 111,000円（副業帯） |

年に直すと 100本で 3,492,000円〜1,332,000円
根拠: 「instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link」「instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used」「revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google」（出典: <a href="https://support.udemy.com/hc/en-us/articles/229605008-Instructor-revenue-share">Instructor revenue share</a>・2026-09-18確認）× 本数（10・30・100本はこちらが置いた前提。何本売れるかの出典は無い）
Udemy Business（定額）で見られた分は、本数の式に入れていません。「15% of monthly subscription revenue」のプールを視聴分数で按分する仕組みだからです（出典: <a href="https://support.udemy.com/hc/en-us/articles/115013221767-How-do-I-earn-revenue-from-Udemy-Business-and-subscription-plans">How do I earn revenue from Udemy Business and subscription plans?</a>・2026-09-18確認）。支払いはPayPal／Payoneer（米国外）で、最低額と時期は今回開いた出典に無いので書いていません。副業で月20万円以上を得ている人は、副業者1万1,358人の調査で10.8%でした（20万〜25万円未満3.9%＋25万円以上6.9%）。出典は<a href="https://www.jil.go.jp/institute/research/2024/documents/0245_01.pdf">JILPT 調査シリーズNo.245「副業者の就労に関する調査」本文PDF</a>の図表2-4-21です（2022年10月実施のインターネット調査・2026-09-18確認）。この金額は目安であり、収益を保証するものではありません。
</div>

<figure class="figure">
<img src="/static/images/udemy-estimate-ladder.svg" alt="Udemyで3,000円の講座が月に何本売れたかを前提として置き、講師の取り分を2つの経路で並べた横棒グラフ。10本なら紹介リンク経由（97%）で29,100円・Udemy経由（37%）で11,100円、30本なら87,300円と33,300円、100本なら291,000円と111,000円。率は原文で本数はこちらが置いた前提、税やアプリ手数料は考えないと注記。下の枠には、同じ100本でも自分で集客すれば準本業帯（291,000円）でUdemy任せなら副業帯（111,000円）であること、実際は2つの経路が混ざり自分の紹介リンク経由の割合がそのまま取り分の割合を決めること、支払いはPayPalまたはPayoneer（米国外）で最低額と時期は今回の出典に無いので書いていないことが書かれている。">
<figcaption>同じ本数でも、自分で集客するかどうかで帯が動きます。本数は前提です。</figcaption>
</figure>

この記事で分かったことをそのまま指示にすると、こうなります。

- **現在の率と仕組み**（97%／37%・Net Amount・プール制）はAIに聞いてもよい（9回とも原文どおりでした）
- **経緯（いつ・何%から変わったか）**は聞かない（9回すべてに原文に無い経緯が付き、年は3回で3通りでした）
- 原文の英文を貼って、**本数を変えた計算だけAIにさせる**（3回とも1円単位で一致しました）
- **何本売れるか**はAIに聞かず、自分の前提として置く（出典が無いので、AIに聞いても出典は増えません）

**開く順番はこの2ページです。**

1. 単品販売の率 → [Instructor revenue share](https://support.udemy.com/hc/en-us/articles/229605008-Instructor-revenue-share)（97%／37%・Net Amount・「作成と掲載は無料」）
2. 定額プランの配分 → [How do I earn revenue from Udemy Business and subscription plans?](https://support.udemy.com/hc/en-us/articles/115013221767-How-do-I-earn-revenue-from-Udemy-Business-and-subscription-plans)（Udemy Businessのプール15%・視聴分数で按分・広告の25%・支払いスケジュール）

「時間を売る」型の講座（ストアカ）は、[手順書を人に渡す前にAIに止まる場所を探させる](/recipes/teaching-ai-runbook-stops-where/)で扱っています。同じ「本気で稼ぐ式」の1つ前は[noteメンバーシップの手取りを式で出す](/recipes/note-membership-monthly-formula/)です。3つの流れのどこに自分がいるかは、[副業のお金は3つの流れで届く](/tools/money-map-three-routes/)の地図で確かめられます。

⚠️ この記事は特定のサービスへの参加をすすめるものではありません。<mark class="warn">本数は前提であって見込みではなく、「売れる講座の作り方」はこの記事にありません。</mark>式を使うときは、ご自身の本数と、紹介リンク経由の割合に置き換えてください。
