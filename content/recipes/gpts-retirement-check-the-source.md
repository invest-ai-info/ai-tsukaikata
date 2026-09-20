---
title: GPTsで稼ぐ門は閉じた——個人プランでは作れず、12月11日に止まる予定を原文で確かめる
category: recipes
scene: earn
description: 「ChatGPTのGPTsで収入を得るには」をウェブ検索を切ったAIに9回聞きました。「個人プランでは新しく作れない」「2026年12月11日に停止予定」には9回とも触れず、廃止予定を聞いた3回は「予定は出ていない」と原文と逆を答えました。原文を貼った3回は3回とも「今からは収入を得られない」と正しく答え、材料に無い金額を1つも作りませんでした。
published: 2026-09-18
checked: 2026-09-18
series: 売る場所の原文から
series_no: 5
series_total: 6
tags: [副業, ChatGPT, GPTs, 収益化, 規約, プロンプト]
time_required: 20分
cost: 無料
---

## これで何ができるか {: .what }

「GPTsで稼ぐ」「GPT Storeの収益化プログラム完全ガイド」という記事は、2026年9月の今も検索に出ます。ところが<mark>OpenAIの公式ヘルプには、個人プラン（Free・Go・Plus・Pro）では新しいGPTを作れないこと、2026年9月25日に新規作成が終わる予定であること、12月11日にカスタムGPTが停止する予定であることが書かれています。</mark>収益化のFAQは、開くと別の記事に転送され、本文に「revenue」も「payout」もありません。日付はEnterprise向けの予定として書かれ、「他のプランも同じ日程に従う見込み」と添えられています。

この記事は、その門が閉じたことをAIが知っているかを**9回**実測し、それでも読者が自分で原文から確かめられる手順に落としたものです。

<mark>先に結果を書きます。素朴に聞いた9回は、収益化プログラムを「米国限定・招待制の試験」と丁寧に説明しましたが、「もう作れない」「12月に止まる」には1回も触れず、廃止予定を聞いた3回は3回とも「予定は出ていない」と答えました。</mark>原文を貼った3回は、3回とも「今からは収入を得られない」と正しく答えました。

<figure class="figure">
<img src="/static/images/gpts-retirement-timeline.svg" alt="ChatGPTのカスタムGPT（GPTs）で収入を得る門が閉じていることを、OpenAIヘルプの記載どおりに日付順で並べた図。1行目＝いま（2026年9月18日確認時点）、個人プラン（Free・Go・Plus・Pro）では新規作成と公開が不可で赤。2行目＝2026年9月25日（planned）に新しいカスタムGPTの作成が終了する予定。3行目＝2026年12月11日（Scheduled）にカスタムGPTが停止する予定。4行目＝収益化FAQ（記事9119255）は開くと別記事へ転送され、本文に revenue・monetiz・earn・payout の語が0件で赤。日付はEnterprise向けの予定で他のプランも同じ日程に従う見込みとされ、原文自身が「subject to change」と書いているため予定であって確定ではないと注記。下の枠には、一般記事は今も検索に出るが個人が新しく作る入口は無いこと、後継のPluginsにも個人がChatGPTの中で有料販売して受け取る仕組みは未提供であること、この門の推定収入は0円で、確かめる先は原文3ページであることが書かれている。">
<figcaption>原文の予定表。日付は「planned」「Scheduled」付きで、原文自身が変わりうると書いています。</figcaption>
</figure>

## 前提 {: .need }

| | |
|---|---|
| かかる時間 | 20分 |
| 費用 | 無料（この記事は原文を読むだけ。ChatGPTの有料プランは必要ありません） |
| 必要なもの | AIとの会話と、公式ヘルプを開くブラウザ |
| プログラミング | **不要** |

⚠️ <mark>この記事は運営者がGPTsで収入を得た記録ではありません。</mark>公式ヘルプに書かれていることの確認と、AIに聞いたときの返り方の実測です。予定は変わります。この記事の日付は2026-09-18に原文を開いて確認したもの（予定表のFAQは2026-09-17に更新されたばかりでした）で、使う前にご自身でも開いて確かめてください。

📌 **実測に使ったAIについて。**このサイトを書いているのと同じClaude系のAIを、**1回ずつ新しいサブエージェントとして起動し、ウェブ検索・ファイル読み書き・コマンド実行を一切使わないよう指示した状態**で聞いています（各回が初対面で、会話の文脈は引き継ぎません。ツールを使わなかったことは記録上の `tool_uses: 0` で確認しています）。**別のAIサービスや、検索できる状態のAIでは結果が変わります。**判定は正規表現の文字列照合で、送った全文（前置きを含む）と項目名と結果は[試した証拠](https://github.com/invest-ai-info/ai-tsukaikata/blob/main/docs/evidence/gpts-retirement-check-the-source.md)にあります。

## AIへの頼み方 {: .ask }

### 1. まず、素朴に聞いてみる

いちばん普通の聞き方から試しました。

<div class="prompt">ChatGPTのGPTs（カスタムGPT）を作って収入を得るには、どうすればいいですか。方法と条件を教えてください。</div>

**3回**通しました。3回とも、GPT Storeの収益化プログラムを「米国限定・招待制の試験的な仕組み」と説明し、「多くの人にとって直接の収益源にはならない」と現実的な注意まで付けました。ここまでは丁寧です。

<mark class="warn">ところが3回とも「個人プランでは新しいGPTを作れない」には触れず、2回は「Plus以上の有料プランなら作れる」と、原文と逆のことを書きました。</mark>原文はこうです。

> New GPT creation and publishing are not available on personal ChatGPT accounts, including Free, Go, Plus, and Pro.（[Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)・2026-09-18確認）

📌 なぜこの言い方をしたか。「どうすればいいですか」という素朴な聞き方は、AIが持っている知識のうち**最新のものだけを選ばせる保証がありません。**「Plusなら作れる」は1年前なら正しく、その古い条件が今の条件として同じ調子で出てきます。読んだ側には見分けがつきません。

### 2. 収益化プログラムの条件を聞く

次に、収益化プログラムそのものにしぼって聞きました。

<div class="prompt">ChatGPTのGPT Storeには、作ったGPTの利用量に応じて制作者に支払う収益化プログラムがあると聞きました。その条件と、支払われるまでの流れを教えてください。</div>

**3回**とも「米国のビルダー限定」「招待制」「利用量（エンゲージメント）に応じて支払う試験段階」と説明し、日本からは対象外だと3回とも書きました。ここは実測の時点で確かめられる範囲では矛盾していません。

<mark>ただし、この収益化のFAQ自体が公式ヘルプから消えていることには、3回とも触れませんでした。</mark>担当が2026-09-18に「Monetizing Your GPT FAQ」（記事番号9119255）を開くと、[Sharing and publishing GPTs](https://help.openai.com/en/articles/8798878-sharing-and-publishing-gpts)へ転送され、その本文に「revenue」「monetiz」「earn」「payout」は0件でした。**条件を説明できることと、その条件がまだ有効であることは別です。**

### 3. 廃止の予定を、そのまま聞く

門が閉じることを知っているか、直接聞きました。

<div class="prompt">ChatGPTのGPTs（カスタムGPT）は、今後も使い続けられますか。廃止や大きな変更の予定があるなら、時期も含めて教えてください。</div>

<mark class="warn">3回とも「現時点で廃止や終了の予定は公表されていない」と答えました。</mark>原文はこうです。

> Sep 25, 2026 (planned): Creation of new custom GPTs ends.
> Dec 11, 2026: Scheduled retirement. Custom GPTs stop running.
> Note that the dates are subject to change.（[Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq)・2026-09-18確認）

3回とも、Apps SDK（ChatGPTの中で動くアプリ）が「GPTsより高度な仕組みとして並行して案内されている」ことには触れています。**後継の存在は知っているのに、前のものが止まる予定は知らない**という形でした。

<figure class="figure">
<img src="/static/images/gpts-ai-hit-and-miss.svg" alt="ChatGPTのGPTsについてAIに聞いた結果を並べた表。上4行は原文と一致した回数で、個人プランでは新しく作れないと述べた回数が0/9で赤、廃止・停止の日付（9月25日・12月11日）を挙げた回数が0/9で赤、原文を貼って聞いた回に「今からは収入を得られない」と答えた回数が3/3で緑、材料に無い金額を作らなかった回数が3/3で緑。下2行は原文と逆のことを言った回数で、「廃止・終了の予定は出ていない」と述べた回数が3/9、「Plus以上の有料プランなら作れる」と述べた回数が3/9、いずれも赤。下の枠には、素朴に聞いた9回は収益化プログラムを米国限定・招待制の試験と説明したが（7/9）、「もう作れない」「12月に止まる」には1回も触れず、廃止予定を聞いた3回は「予定は無い」と答えたこと、AIが知っている昔の条件を今の条件として読まず、予定は原文で確かめるという結論が書かれている。">
<figcaption>「昔の条件」は当たる。「いま閉じている」は9回とも出ませんでした。</figcaption>
</figure>

📌 なぜこの言い方をしたか。「予定があるなら時期も含めて」と聞けば、知っていれば出てきます。**3回とも出なかったのは、AIの知識がこの予定より前で止まっているから**で、聞き方を工夫しても増えません。ここから先は原文の仕事です。

### 4. 原文を自分で取ってきて、判断だけAIにさせる

原文の4行をこちらが貼り、「上の情報だけから答えて」と縛りました。

<div class="prompt">公式ヘルプで確認した情報を貼ります。これ以外の情報は使わないでください。

・New GPT creation and publishing are not available on personal ChatGPT accounts, including Free, Go, Plus, and Pro.
・Sep 25, 2026 (planned): Creation of new custom GPTs ends.
・Dec 11, 2026: Scheduled retirement. Custom GPTs stop running.
・Note that the dates are subject to change.

私は個人のPlusプランです。今からGPTsを作って収入を得ることはできますか。上の情報だけから答え、上に無いこと（収益化の条件や金額など）は「材料に無い」と書いてください。</div>

**3回**とも「今からGPTsを作って収入を得ることはできない」と答え、根拠を貼った4行に限って説明しました。<mark>3回とも、収益化の条件や金額については「材料に無い」と書き、渡していない数字を1つも作りませんでした。</mark>3回とも「日付は変更されうる」という原文の但し書きも自分から引きました。

これは[AIに数字を「それっぽく」埋めさせないための頼み方](/recipes/numbers-not-in-the-source/)と同じ結果です。**知識を聞くと古いものが混ざり、原文を貼れば貼った範囲で正しく判断する。**この差が、この記事で一番大きい差です。

ただし2回（3回中2回）は、貼っていない「今日の日付（2026年9月18日）」を自分で持ち込み、「9月25日まであと1週間」と計算しました。結論は変わりませんが、**日付の計算まで任せるなら、今日の日付も材料として貼るほうが確実です。**

## うまくいかないときの言い直し方 {: .fix }

### AIが「まだ使える」「Plusなら作れる」と言い張るとき {: .trouble }

AIの知識を訂正しようとするより、**確認する場所だけを聞いて自分で開く**ほうが早いです。

<div class="prompt">ChatGPTのGPTs（カスタムGPT）の提供状況や廃止予定について、確認すべきOpenAIの公式ページの名前だけを、中身や日付は書かずに教えてください。</div>

**3回**とも日付と金額を1つも書かず、「OpenAIヘルプセンター」を確認先として挙げました。ただし<mark>廃止・移行のFAQというページの名前は、3回とも出ませんでした</mark>（AIの知識より後にできたページなので、知らないのは当然です）。2回は「自分の知識には限界がある」と自分から断りました。

だから開く順番は、この記事のほうで示します（下の「開く順番」）。ページ名を聞く価値は、**AIに日付を書かせないこと**にあります。

### 「後継のアプリで売ればいい」と言われたとき {: .trouble }

GPTsの後継として案内されている仕組みで、個人が受け取れるかも聞きました。

<div class="prompt">OpenAIがGPTsの後継として案内しているプラグイン（ChatGPTの中で動くアプリ）で、個人の開発者がChatGPTの中で有料販売して収入を受け取る仕組みはありますか。分からない部分は「分からない」と書いてください。</div>

**3回**とも、「個人の開発者がChatGPTの中で有料販売して受け取る、誰でも使える仕組みは確認できない」と答え、分からない部分は「分からない」と書きました。3回とも、決済はChatGPTの外（開発者自身のサイト）で行い、承認されているのは物理的な商品の購入だけ、と説明しています。原文はこうです。

> While current approval is limited to plugins for physical goods purchases, we are actively working to support a wider range of commerce use cases.（[Checkout API reference – Plugins](https://developers.openai.com/apps-sdk/build/monetization)・2026-09-18確認）

⚠️ 3回とも「プラグイン」を2023年の旧機能として扱い、質問の意図（GPTsの後継として案内されているもの）とはずれた前提で答え始めました。**名前が同じで中身が変わったものは、AIの知識の中で古いほうに引っ張られます。**ここも原文で確かめました。

## 応用・次の一手 {: .next }

**この門の推定収入は、頑張り方にかかわらず0円です。**理由は3つあり、どれも原文にあります。

<div class="money-note">
金額の目安: 推定0円（個人プランでは新しいGPTを作れず、収益化FAQは削除され、カスタムGPT自体が2026-12-11に停止する予定。日付はEnterprise向けの予定で、他のプランも同じ日程に従う見込みと原文にある）
根拠: 「New GPT creation and publishing are not available on personal ChatGPT accounts, including Free, Go, Plus, and Pro.」（出典: <a href="https://help.openai.com/en/articles/8554397-creating-and-editing-gpts">Creating and editing GPTs</a>・2026-09-18確認）／「Dec 11, 2026: Scheduled retirement. Custom GPTs stop running.」（出典: <a href="https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq">Custom GPT retirement and migration FAQ</a>・2026-09-18確認）／収益化FAQ（記事9119255）は <a href="https://help.openai.com/en/articles/8798878-sharing-and-publishing-gpts">Sharing and publishing GPTs</a> へ転送され、本文に revenue・payout の記載なし（2026-09-18確認）
週に何時間かけても、作る入口が無いので掛け算が立ちません。日付は原文が「変更されうる」と書いているとおり動く可能性があります。この金額は目安であり、収益を保証するものではありません。
</div>

この記事で分かったことをそのまま指示にすると、こうなります。

- **収益化プログラムの「昔の条件」**はAIに聞いてもよい（9回中7回、米国限定・招待制と正確でした）
- **「いま作れるか」「いつ止まるか」**はAIに聞かない（9回中0回。廃止予定を聞いた3回は逆を答えました）
- 原文を貼って、**判断だけAIにさせる**（貼った3回は3回とも正しく、材料に無い数字を作りませんでした）
- **後継の仕組みで個人が受け取れるか**も、原文で見る（AIは「プラグイン」を旧機能と取り違えました）

**開く順番はこの3ページです。**

1. 予定表 → [Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq)（9月25日・12月11日の予定と「dates are subject to change」）
2. 誰が作れるか → [Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)（個人プランでは新規作成・公開が不可）
3. 後継の決済 → [Checkout API reference – Plugins](https://developers.openai.com/apps-sdk/build/monetization)（承認は物理的な商品のみ、決済は開発者のサイト側）

同じ「原文で確かめる」型は、[noteで売る前に、引かれる手数料を原文で確かめる](/recipes/note-fee-before-you-sell/)と[YouTubeの入金しきい値が分かる](/recipes/youtube-payout-thresholds/)にあります。同じシリーズの次は、[AI画像を売る場所は2026年に割れた](/recipes/ai-stock-images-adobe-vs-pixta/)です。3つの流れのどこに自分がいるかは、[副業のお金は3つの流れで届く](/tools/money-map-three-routes/)の地図で確かめられます。

⚠️ この記事は特定のサービスへの参加をすすめるものでも、やめるようすすめるものでもありません。<mark class="warn">「GPTsで稼ぐ」と題した記事を読むときは、その記事の日付と、原文の予定表の日付を並べてください。</mark>予定は原文が変わりうると書いているとおり、変わります。
