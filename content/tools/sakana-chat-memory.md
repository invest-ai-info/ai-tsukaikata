---
title: Sakana Chatに記憶機能——過去の会話は思い出さない
description: Sakana AIが2026年9月17日に発表した「Sakana Chat」の更新について、公式発表ページに書かれている数字だけを整理しました。搭載モデルが最新の「Fugu Max」に切り替わり、会話の好みを引き継ぐメモリー機能が加わりましたが、対象は更新後の会話だけで、過去の会話は含まれません。GoogleのGemini・AnthropicのClaudeの同種機能とも突き合わせています。
category: tools
scene: choose
published: 2026-09-16
checked: 2026-09-16
tags: [Sakana AI, チャットAI, メモリー, AI最新情報]
---

## 何が変わったか

Sakana AIは2026年9月17日、チャット製品「**Sakana Chat**」の更新を発表しました（出典: <https://sakana.ai/chat-fugumax/>）。公式ページに書かれていることだけを並べます。3行にすると、こうなります。

- 搭載モデルが、2026年9月11日にAPI公開されたばかりの**Fugu Max**に切り替わりました。追加設定は不要で、モデル選択でFugu Maxを選べばすぐ使えると説明されています（出典: 同上）。
- **メモリー機能**が加わりました。役割や文体の好みなど、一度伝えた内容を次回以降の会話に引き継げます。NamazuとFugu Maxの両方で使えます（出典: 同上）。
- <mark class="warn">記憶されるのは、この更新以降の会話だけです。過去の会話は対象になりません</mark>（出典: 同上。原文: 「なお、記憶されるのは本アップデート以降の会話で、過去の会話は対象になりません」）。

先に断っておきます。**この記事は運営者がSakana Chatを実際に使った記録ではありません。**発表ページに書かれていることを読んで整理したものです。「便利だった」「速かった」といった使用感は一切書いていません。

Fugu Max自体の性能・料金の詳しい比較は、すでに [Sakana Fugu Maxの記事](/tools/sakana-fugu-max/) に書いています。この記事は「Sakana Chatという製品で何が変わったか」だけを扱います。

## 前のモデルとの違い

Sakana Chatは、この9か月で搭載モデルを2回入れ替えています。発表ページの経緯部分に書かれている日付をそのまま並べました。

<figure class="figure">
<img src="/static/images/sakana-chat-timeline.svg" alt="Sakana Chatに搭載されるモデルが増えた年表。2026年3月、Sakana Namazuのα版とともにSakana Chatを公開。2026年8月、Sakana Fuguを追加し、モデルを選べるようになり、コード実行・画像/文書添付にも対応。2026年9月17日（Fugu MaxのAPI公開の6日後）、搭載モデルをFugu Maxに切替え、会話の好みを次回に引き継げるメモリー機能を追加した。8月のアップデートの正確な日付は発表ページに記載がない。Namazuは9月の更新後も引き続き使え、メモリー機能はNamazu・Fugu Maxの両方が対象。">
<figcaption>Fugu MaxがChatに届くまで、API公開からわずか6日でした</figcaption>
</figure>

<mark>Sakana Chat自体は2026年3月、Sakana Namazuのα版とともに公開されました</mark>（出典: 同上）。8月のアップデートで「Sakana Fugu」が加わってモデルを選べるようになり、コードの実行や画像・文書の添付にも対応しました（出典: 同上）。⚠️ 8月の正確な日付は発表ページに記載がなく、「8月のアップデートでは」とだけ書かれています。

そして今回、Chatに載っていた「Sakana Fugu」が、上位モデルの「Fugu Max」に切り替わりました。<mark>Fugu MaxはAPIとして2026年9月11日に発表されたばかりで、Chatへの搭載はその6日後です</mark>（出典: Fugu MaxのAPI発表 <https://sakana.ai/fugu-max-release/>。6日という日数は暦日の引き算で、この記事で計算しました）。

<figure class="figure">
<img src="/static/images/sakana-chat-model-lineup.svg" alt="Sakana Chatで選べたモデルの移り変わりを示した表。2026年3月時点はSakana Namazuのみ。2026年8月にSakana Fuguが加わり、Namazu・Fuguの2つから選べるようになった。2026年9月17日、FuguがFugu Maxに切り替わり、Namazu・Fugu Maxの2つになった。Namazuは3月からずっと選択肢にある。Sakana Fuguは8月から9月17日までの短い期間だけ選択肢にあり、Fugu Maxに置き換わって消えた。">
<figcaption>「Sakana Fugu」は短い期間で表舞台から消えました</figcaption>
</figure>

<mark class="warn">古い「Sakana Fugu」と新しい「Fugu Max」の性能を、Sakana Chatの発表ページ自体は数字で比べていません</mark>。Fugu Max単体の性能・料金は、Sakana AIのAPI発表ページと [この記事](/tools/sakana-fugu-max/) にありますが、それは「Chatで前より速くなった／賢くなった」という比較ではなく、Fugu Maxを他社の最上位モデルと比べたものです。Sakana Chatの更新自体が主張しているのは、モデルの中身の向上ではなく「メモリー機能が加わったこと」です。

## 他社のメモリー機能との比較

この記事の型では、他社の最上位モデルの単価やベンチマークを突き合わせます。ただし今回の変更点である「メモリー機能」は、価格や点数で比べる性質のものではありません。代わりに、**同じ「会話をまたいで覚える」機能を、GoogleとAnthropicの公式ページで突き合わせました**。

<figure class="figure">
<img src="/static/images/sakana-chat-memory-grid.svg" alt="Sakana Chat・Gemini（Google）・Claude（Anthropic）のメモリー機能を3項目で比べた表。過去の会話を含むか＝Sakana Chatは含まない（アップデート以降の会話のみ）、Geminiは含む（過去チャットの記憶が前提）、Claudeは含められる（初期設定時に過去チャットから生成可）。使えるアカウント＝Sakana Chatは制限の記載なし、Geminiは個人アカウントのみ・18歳以上で職場/学校アカウントは不可、ClaudeはTeam/Enterpriseで始まりPro/Maxプランにも拡大。オフ・管理＝Sakana Chatは設定画面でオフ可能で個別削除の記載はなし、Geminiはオン/オフ切替可能で該当チャットを削除すると記憶も解除される、Claudeはオフ可能で管理者が組織単位で無効化できる。OpenAI（ChatGPT）にも記憶機能はあるが、この記事を書いた環境からは公式ページを確認できなかった。「記載なし」は機能が無いと明言されているのではなく、公式ページに書かれていない、という意味。">
<figcaption>「過去の会話を思い出すか」だけ見ても、3社は同じではありません</figcaption>
</figure>

<mark>いちばんの違いは「過去の会話を含むかどうか」です</mark>。GoogleのGeminiは、過去のチャットの記憶をそもそも前提にした機能です（出典: <https://support.google.com/gemini/answer/16598469>。原文: “Gemini can learn from your chats to understand more about you and your world.”）。AnthropicのClaudeは、メモリーを有効にする最初の設定で「過去のチャットからメモリーを生成させる」ことができます（出典: <https://claude.com/blog/memory>。原文: “let Claude generate memory with your past chats at initial set-up”）。

<mark class="warn">対してSakana Chatは、過去の会話をさかのぼって取り込む手段が発表ページに書かれていません</mark>。「本アップデート以降の会話が対象」という一文だけがあり、Claudeのような初期取り込みの仕組みには触れていません。

アカウントの制限にも差があります。<mark>Geminiのメモリーは、個人のGoogleアカウントで18歳以上、かつ職場・学校・保護者管理アカウントでは使えないと明記されています</mark>（出典: <https://support.google.com/gemini/answer/16598469>。原文: “This feature isn't available when you sign in to a work, school, or supervised Google Account.”）。Claudeは逆に、法人向けのTeam・Enterpriseプランで2025年9月に始まり、2025年10月23日にPro・Maxプランへ拡大したと書かれています（出典: <https://claude.com/blog/memory>）。Sakana Chatの発表ページには、アカウントやプランによる制限の記載がありません。

管理のしやすさも書かれている範囲で違います。Claudeは「Enterprise管理者が組織単位でいつでも無効化できる」と明記しています（出典: 同上。原文: “Enterprise admins can choose whether to disable memory for their organization at any time.”）。Geminiは個人が設定からオン・オフを切り替え、該当のチャットを削除すると記憶にも反映されると説明されています（出典: <https://support.google.com/gemini/answer/16598469>）。Sakana Chatは「設定画面から確認でき、機能をオフにすることもできる」とだけ書かれており、記憶した内容を1件ずつ削除できるかどうかは発表ページに記載がありません。

<mark class="warn">OpenAI（ChatGPT）にも記憶機能があります</mark>が、この記事を書いた環境からは確認できませんでした。OpenAIの公式ニュースRSS（<https://openai.com/news/rss.xml>）には、2024年2月13日の「Memory and new controls for ChatGPT」と、2026年6月4日の「Dreaming: Better memory for a more helpful ChatGPT」という2件の見出しが確認できます。ただし発表ページ本体（`openai.com`）はこの環境からアクセスできず、対象範囲やオフの手順は確認できていません。まとめ記事の記述を写すことはしないので、この記事ではタイトルと日付だけを載せています。

## どういう人に効くか

**いま動かしてみるといい人**

- すでにSakana Chatを使っている人。追加の申し込みなしに、モデル選択でFugu Maxを選べばすぐ試せます。
- 会話のたびに自分の役割や文体の好みを説明し直している人。メモリーをオンにすれば、その手間が減ると説明されています。

**急がなくていい人**

- これまでの会話を財産として蓄積してきて、それを一括で覚えさせたい人。Claudeのように過去チャットからまとめて記憶を作る仕組みは、Sakana Chatの発表には書かれていません。
- 法人でアカウントを管理していて、組織単位でオン・オフを制御したい人。Claudeにある管理者向けの無効化機能のような記載は、Sakana Chatにはありません。
- 会話の内容を後から個別に削除したい人。「オフにできる」とは書かれていますが、1件ずつ消せるかどうかは発表ページに記載がありません。

**この記事で分からないこと**

Sakana Chat自体の料金です。発表ページに記載がなく、料金ページ（`chat.sakana.ai`）はこの記事を書いた環境からは経路遮断で確認できませんでした。対応言語・モバイルアプリの有無・実際の記憶の精度も、発表ページには書かれておらず、運営者も試していないため書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Sakana Chatの更新発表（Sakana AI・2026年9月17日）: <https://sakana.ai/chat-fugumax/>
2. Fugu MaxのAPI発表（Sakana AI・2026年9月11日）: <https://sakana.ai/fugu-max-release/>
3. Geminiのメモリー機能（Google公式ヘルプ）: <https://support.google.com/gemini/answer/16598469>
4. Claudeのメモリー機能の発表（Anthropic公式・2025年9月11日、2025年10月23日更新）: <https://claude.com/blog/memory>
   （<https://www.anthropic.com/news/memory> を開くと、このページへ転送されます）
5. OpenAIの公式ニュースRSS（見出しと日付のみ確認）: <https://openai.com/news/rss.xml>

OpenAIの発表ページ本体（`openai.com`）と、Sakana Chat自体の料金ページ（`chat.sakana.ai`）には、この記事を書いた環境から到達できませんでした。

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の内容を確認してください。
