---
title: Claude利用の振り返り機能——メモリオン限定
description: Anthropicが2026年7月9日にベータ公開した「Reflect」機能について、発表ページに書かれていることだけを整理しました。過去1〜12ヶ月のAI利用を振り返れますが、対象はメモリ機能をオンにしたFree・Pro・Maxユーザーに限られ、時間の表示やCoworkの振り返りはまだ来ていません。
category: tools
scene: choose
published: 2026-09-02
checked: 2026-09-02
tags: [Claude, Anthropic, 振り返り, プライバシー, AI最新情報]
---

## 何が変わったか

Anthropicは2026年7月9日、**Reflect**というベータ機能を発表しました（出典: <https://www.anthropic.com/news/reflect-with-claude>）。自分がClaudeをどう使っているかを、レポートの形で振り返れる機能です。公式ページに書かれていることだけを並べます。

- 過去**1・3・6・12ヶ月**の利用を選んで振り返れます。よく出てきた話題・使い方のパターン・取り組んだタスクの種類がまとまったレポートが出てきます（出典: 同上）。
- 対象は<mark>メモリ機能をオンにしている、Free・Pro・Maxのユーザー</mark>です（出典: 同上。原文: “Free, Pro, and Max users who have memory turned on”）。
- レポートは「AI Fluency Framework」という4つの観点（委任・説明・識別・勤勉）でAIとの関わり方を整理すると説明されています（出典: 同上）。

先に断っておきます。**この記事は運営者が実際にReflectを使った記録ではありません。**発表ページに書かれていることを読んで整理したものです。「便利だった」「見やすかった」といった使用感は一切書いていません。

使い始め方も書かれています。Claudeの設定（Settings）から「reflect on your usage」を選ぶと、レポートが生成されます。ウェブ版とデスクトップアプリの両方で使えます（出典: 同上）。

## 何を4つの軸でみるか

発表ページは、レポートが軸にする4つの観点を「AI Fluency Framework」として挙げています。英語の名称と、その説明文をそのまま日本語にしました。

<figure class="figure">
<img src="/static/images/reflect-4d-framework.svg" alt="Reflectのレポートが軸にする4つの観点を示した図。①委任（Delegation）＝目標を決め、AIにどう関わるか・そもそも関わるかを判断すること。②説明（Description）＝AIから役に立つ働きを引き出せるよう、目標を的確に言葉にすること。③識別（Discernment）＝AIの出力がどれだけ役に立つかを、正確に見極めること。④勤勉（Diligence）＝AIを使って行ったことに、自分で責任を持つこと。下の枠には、4つとも使い方の質の観点であり、性能や料金の比較軸ではないことが書かれている。">
<figcaption>4つとも「使い方の質」の観点です</figcaption>
</figure>

<mark>この4つは、モデルの性能や料金を測る物差しではありません</mark>。「AIにどう関わっているか」という、使う側の姿勢を振り返るための軸です。レポートには、それぞれの観点でどう関わってきたかの実例や、改善のための具体的な提案（たとえば、都度説明し直すのではなくプロジェクトを始める、といった提案）が含まれると説明されています（出典: 同上）。

## プライバシーはどう設計されているか

自分のチャット履歴を材料にする機能なので、何が使われて何が使われないかは重要な点です。発表ページには、この境目がはっきり書かれています。

<figure class="figure">
<img src="/static/images/reflect-privacy-scope.svg" alt="レポートに使われる会話と、使われない会話を対比した図。使われるのは通常のチャット履歴（過去1〜12ヶ月）と、使い方のパターン・取り組んだタスクの種類の分類。使われないのはシークレットチャットと、健康連携ツールに繋がった会話（完全に除外）。下の枠には、設計にMIT Media LabのAHAプログラムとボストン小児病院のDigital Wellness Labが協力したと説明されていること、対象はメモリ機能をオンにしたFree・Pro・Maxのユーザーであることが書かれている。">
<figcaption>健康に関わる会話は、完全に除外されています</figcaption>
</figure>

<mark class="warn">シークレットチャットはレポートの材料に含まれません</mark>（出典: 同上。原文: “Your reflection doesn't draw from incognito chats”）。また、Slackやドライブなどの接続ツールを使っていても、<mark class="warn">その先にあるファイル本体は取得しないと説明されています</mark>（出典: 同上）。

いちばん踏み込んだ配慮は健康関連です。<mark class="warn">健康連携ツールに繋がった会話は、完全に除外されると明記されています</mark>（出典: 同上。原文: “any conversation connected to a health integration tool is left out”）。設計にあたっては、MIT Media LabのAHA（Advancing Humans with AI）プログラムと、ボストン小児病院のDigital Wellness Labが協力したと書かれています（出典: 同上）。

## 他社との比較

この記事の型では、他社の同等機能と数字を突き合わせます。今回は**その比較ができませんでした**。理由を正直に書きます。

- OpenAIの個人向け利用状況の分析機能に関連すると思われるヘルプページ（`help.openai.com`）は、この記事を書いた環境からは403でした。URLが正しく現存するかどうかも含めて確認できていません。
- Googleの管理者向けGemini利用レポートに関連すると思われるヘルプページ（`knowledge.workspace.google.com`）は、`CONNECT tunnel failed` で止まりました。この環境の許可リストによる経路の遮断です。

つまり、**自分自身の利用を振り返るという同じ土俵の機能**を、他社の公式ページの記述で突き合わせることが、この環境からはできませんでした。二次情報（まとめ記事や個人ブログ）の記述を写すことはしないので、この記事では比較を保留にしています。

## いま使える範囲、まだ来ていない範囲

ベータ版なので、発表時点で「できること」と「まだできないこと」が分かれています。発表ページの本文が明記している2点をそのまま図にしました。

<figure class="figure">
<img src="/static/images/reflect-roadmap.svg" alt="いま使える機能と、まだ来ていない機能を対比した図。いま使える（ベータ）のは、設定のreflect on your usageからレポートを作成できること、過去1・3・6・12ヶ月の振り返り、quiet hoursの設定と休憩の通知（nudge）。まだ来ていない（soon）のは、使った時間（time spent）の表示と、Coworkの会話の振り返りの2点で、本文にそう明記されている。下の警告枠には、発表ページにTeam・Enterpriseプランについての記載がないことが書かれている。">
<figcaption>「使った時間」と「Coworkの振り返り」は、まだ来ていません</figcaption>
</figure>

<mark>「使った時間（time spent）」の表示は、まだ実装されていません</mark>（出典: 同上。原文: “Soon, we'll add a view of how much time you've spent using Claude.”）。いま見られるのは話題やタスクの分類であって、時間そのものではありません。

<mark>Coworkでの会話も、いまはレポートの対象外です</mark>（出典: 同上。原文: “Reflecting on your Cowork conversations will be available soon.”）。Coworkを主に使っている人は、振り返りの材料にCowork分の履歴が含まれない点に注意が必要です。

quiet hours（静かな時間帯の設定）や、一定時間使ったら休憩を促す通知（nudge）の設定もできると説明されています（出典: 同上。原文: “you can also set quiet hours or schedule a nudge to take a break from using Claude after a certain amount of time.”）。使い方を眺めるだけでなく、使う量そのものを調整する機能も併設されている形です。

<mark class="warn">発表ページに、Team・Enterpriseプランについての記載はありません</mark>。書かれているのはFree・Pro・Maxの3プランだけです（出典: 同上）。会社支給のアカウントがTeamまたはEnterpriseプランの場合、この記事の元になった発表ページからは、Reflectが使えるかどうか分かりません。同じ理由で、モバイルアプリで使えるかどうかについても、発表ページに記載はありません。

## どういう人に効くか

**いま動かしてみるといい人**

- Free・Pro・Maxのいずれかを契約していて、メモリ機能をすでにオンにしている人。追加の申し込みなしに、設定からすぐ試せます。
- 「AIに頼みすぎていないか」「同じ説明を毎回繰り返していないか」を、感覚ではなく振り返りたい人。

**急がなくていい人**

- 会社支給のTeam・Enterpriseプランを使っている人。発表ページに記載がなく、この記事では対象かどうか確認できません。
- メモリ機能をオフにしている人。まずメモリをオンにしないと対象になりません。
- Coworkでの作業が中心の人。Coworkの会話は、いまのレポートには反映されません。

**この記事で分からないこと**

実際に生成されるレポートの見た目、日本語での表示、レポート生成にかかる時間。運営者もまだ試していないため、体験としては書けません。

## 出典一覧

すべて公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Reflectの発表（Anthropic・2026年7月9日）: <https://www.anthropic.com/news/reflect-with-claude>

OpenAI（`help.openai.com`）、Google（`knowledge.workspace.google.com`）の関連ページには、この記事を書いた環境から到達できませんでした。

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の内容を確認してください。
