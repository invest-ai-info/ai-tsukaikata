---
title: SlackにAIをタグ付け——上限を決めないと請求は青天井
description: Anthropicが2026年6月23日に発表した「Claude Tag」について、公式サイトと公式ドキュメントに書かれている数字だけを並べました。SlackでAIをチームメイトとして扱える一方、料金の上限は自分で決めないと管理者が想定していない形で膨らみます。
category: tools
scene: choose
published: 2026-09-01
checked: 2026-09-01
tags: [Claude, Slack, Anthropic, チームでのAI活用, AI最新情報]
---

## 何が変わったか

Anthropicは2026年6月23日に **Claude Tag** を発表しました（出典: <https://www.anthropic.com/news/introducing-claude-tag>）。公式ページに書かれていることだけを並べます。

- Slackのチャンネルに **@Claude** をメンバーとして参加させ、誰でもタグ付けして仕事を任せられます。管理者がチャンネルごとにアクセス権とツールを設定します（出典: 同上）。
- <mark>Anthropicの自社プロダクトチームでは、コードの65%が社内版Claude Tagによって作られています</mark>（出典: 同上）。この記事を書いた時点で、公式が明かしている唯一の効果の数字です。
- 提供は**Claude EnterpriseとTeamプランのベータ版のみ**。個人向けのFree・Pro・Maxプランでは使えません（出典: <https://claude.com/docs/claude-tag/overview>）。動くモデルは **Opus 4.8** です（出典: <https://www.anthropic.com/news/introducing-claude-tag>）。

先に断っておきます。**この記事は運営者がClaude Tagを実際に使った記録ではありません。**公式サイトと公式ドキュメントに書かれていることを読んで整理したものです。「便利だった」「速かった」といった使用感は一切書いていません。

Claude Tagは、Slack上にいる既存の「Claude in Slack」アプリを置き換えるものだと説明されています。管理者は30日以内に移行をオプトインできます（出典: 同上）。

## 前のツールとの違い

### 何を置き換えるのか

公式ページは「Claude Tagは、既存のClaude in Slackアプリを置き換える」とだけ説明しています（出典: <https://www.anthropic.com/news/introducing-claude-tag>）。旧アプリ「Claude in Slack」の詳しい仕様が書かれている support.claude.com のページは、<mark>この記事を書いた環境からは到達できませんでした</mark>（経路の遮断で、内容の良し悪しとは無関係です）。そのため、旧アプリと比べて具体的に何が増えたのかは、この記事では確認できていません。

### 似た製品との使い分け

同じAnthropicには、Claude Tagのほかにも「Cowork」「Claude Code」というプロダクトがあります。公式ドキュメントは、この3つの違いを表にまとめています。

| | Claude Tag | Cowork | Claude Code |
|---|---|---|---|
| どこで | Slackのチャンネル | claude.aiのチャット | 端末やIDE |
| 誰の権限で動くか | 管理者が設定した共通の権限 | 自分のOAuth連携 | 自分のローカル環境 |
| 誰に見えるか | チャンネルの全員 | 自分だけ | 自分だけ |
| 向いている用途 | チームで見て動かす作業 | 個人の調査・下書き | 自分の手元でのコーディング |

出典: すべて <https://claude.com/docs/claude-tag/concepts/how-it-works>

<figure class="figure">
<img src="/static/images/claudetag-position-grid.svg" alt="Claude Tag・Cowork・Claude Codeを4項目で比べた表。どこで＝Claude TagはSlackのチャンネル、Coworkはclaude.aiのチャット、Claude Codeは端末やIDE。誰の権限で＝Claude Tagは管理者が設定した共通の権限、Coworkは自分のOAuth連携、Claude Codeは自分のローカル環境。誰に見えるか＝Claude Tagはチャンネルの全員、Coworkと Claude Codeは自分だけ。向いている用途＝Claude Tagはチームで見て動かす作業、Coworkは個人の調査・下書き、Claude Codeは自分の手元でのコーディング。下の枠には、公式が用途で使い分けることを勧めていること（チームで共有→Claude Tag、個人の下書き→Cowork、自分のコード→Claude Code）、3つとも同じ会社の製品で他社と並べた公式の比較表は見つかっていないことが書かれている。">
<figcaption>3つとも同じ会社の製品です。他社にそのまま並べられる公式な比較表ではありません</figcaption>
</figure>

<mark>「チームで共有して進める作業はClaude Tag、自分だけの調査や下書きはCowork、自分の手元でコードを書くならClaude Code」というのが公式の使い分けです</mark>（出典: 同上）。Slackのチャンネルに常駐して、誰が見ても進み具合が分かる——ここがClaude Tagだけの特徴です。

## 他社との比較

この記事の型では、他社の最上位モデルや同等の製品と料金・仕様を突き合わせます。ただし今回は**その比較ができませんでした**。理由を正直に書きます。

- OpenAIがSlack向けに提供しているとされる連携機能について、`openai.com` と `help.openai.com` のページはこの記事を書いた環境からはいずれも403でした（URLが正しく現存するかどうかも含めて確認できていません）。応答ヘッダーに `cf-mitigated: challenge` が付いており、これは<mark>先方のbot判定であって、経路の遮断ではありません</mark>。同じ `openai.com` のRSSフィード（`openai.com/news/rss.xml`）は200で返るのが切り分けの根拠です。
- Microsoftの「Microsoft 365 Copilot」やSalesforceの「Agentforce」に関連すると思われる公式ページ（`learn.microsoft.com`・`help.salesforce.com` など）は、`CONNECT tunnel failed` で止まりました。この環境の許可リストによる経路の遮断で、bot判定とは別種の理由です。
- Googleの「Gemini Enterprise」（`cloud.google.com/gemini-enterprise`）は本体ページには到達できましたが、料金ページは中身が見つからず、Slackとの連携について具体的な数字は確認できませんでした。

つまり、**チャンネルに常駐してチーム全員から仕事を任せられるAI**という同じ土俵の製品を、他社の公式ページの数字で突き合わせることが、この環境からはできませんでした。二次情報（まとめ記事や個人ブログ）の数字を写すことはしないので、この記事では比較を保留にしています。

## 料金の扱い——上限を決めないと請求は青天井

Claude Tagは、Slackに追加しても座席ごとの追加料金は発生しません。その代わり、チャンネルでの作業は「使用残高（usage balance）」から使われる仕組みです（出典: <https://claude.com/docs/claude-tag/admins/set-spend-limit>）。ここが一番、会社員に関わる部分です。

| 作業の種類 | 請求先 | 上限 |
|---|---|---|
| チャンネルでの作業 | 組織の使用残高 | 管理者が決めた spend limit（プラス、チャンネルごとの上限） |
| チャンネルを読むだけ・返信するか判断するだけ | どこにも請求されない | — |
| DM（個人チャット） | 送った本人のシート | そのシートのふだんの利用上限（組織の spend limit は無関係） |

出典: すべて <https://claude.com/docs/claude-tag/admins/set-spend-limit>

<figure class="figure">
<img src="/static/images/claudetag-billing-boundary.svg" alt="チャンネルでの作業とDMで、請求先と上限がどう分かれるかを示した図。チャンネルでの作業は、組織の使用残高（usage balance）に請求され、上限は管理者が決めるspend limit。Teamプランは残高を入金するまで反応しない。DM（個人チャット）は、送った本人のシートに請求され、上限はそのシートのふだんの利用上限で、組織のspend limitとは無関係。下の警告枠には、Teamは残高を入金するまでチャンネルで一切返信しないこと、Enterprise（請求書払い）は自分で上限を決めない限り上限が無いことが書かれている。注釈として、spend limitは定価で数えるため値引き契約があっても上限には反映されず請求時にだけ反映されること、DMは組織のspend limitを消費せず送った本人のふだんの利用上限だけが働くことが添えられている。">
<figcaption>チャンネルとDMは、財布も上限も別です</figcaption>
</figure>

<mark class="warn">Teamプランは、使用残高を入金するまでチャンネルで一切返信しません</mark>（出典: 同上）。逆に<mark class="warn">Enterprise（請求書払い）は、自分で上限を決めない限り上限が無いと、公式ドキュメントに明記されています</mark>（原文: “Usage bills to your invoice with no upper bound until you set a spend limit.”）。つまり、導入したその日に上限（spend limit）を設定しない限り、Enterpriseプランの請求は制度上は青天井です。

もう1つ見落としやすい点があります。<mark class="warn">spend limit は「定価」で数える設計です</mark>。原文には「組織が値引き契約を結んでいても、その値引きは上限には反映されず、請求時にだけ反映される」と書かれています（出典: 同上）。値引き契約があるからと油断して上限を高めに設定すると、実際の請求額の見積もりを誤ります。

なお、上限に達すると、Claudeはスレッド上で「作業を完了できなかった」と伝え、それ以上は動きません（出典: 同上）。上限を超えて勝手に使われ続けることはありません。

## セッションはどれくらい続くのか

Slack上の会話なので「いつまで覚えているか」も、会社での使い方に直結します。公式ドキュメントには、3つの既定の目安が書かれています。

<figure class="figure">
<img src="/static/images/claudetag-session-ladder.svg" alt="会話が止まってから何が起きるかを示した3段の図。①サンドボックス（1スレッドの作業部屋）を片づけるのは最後のやり取りから数分後。②チャンネル全体の会話を仕切り直すのは、無音のまま約1時間、または最初の会話から約1日。③チャンネルの読み込みを止めるのは、誰にも返信しないまま約100件たまったとき。下の枠には、3つとも既定値で公式ドキュメントが「変わることがあるので目安として扱ってほしい」と明記していること、②はチャンネルの設定が変わったときも仕切り直されることが書かれている。">
<figcaption>数字はすべて既定値で、公式は「変わることがある」と明記しています</figcaption>
</figure>

- **1つのスレッドの作業環境（サンドボックス）**は、最後のやり取りから**数分**で片づけられます。次に返信すると、また新しく作られます（出典: <https://claude.com/docs/claude-tag/concepts/how-it-works>）。
- **チャンネル全体の会話**は、無音のまま**約1時間**、またはできてから**約1日**たつと仕切り直されます。チャンネルの設定が変わったときも同じです（出典: 同上）。
- **チャンネルの読み込み**は、誰にも返信しないまま**約100件**メッセージがたまると止まります。`@Claude` と話しかければ、また読み始めます（出典: 同上）。

<mark>これら3つの数字はすべて既定値で、公式ドキュメントは「変わることがあるので、目安として扱ってほしい」と明記しています</mark>（出典: 同上）。数字そのものより、「サンドボックスは数分」「チャンネルの記憶は日単位」「読み込みには上限がある」という段差があること自体が、使うときに知っておく価値のある情報です。

なお、<mark class="warn">Slack側でスレッドやメッセージを削除しても、Anthropic側の記録（トランスクリプト）からは消えません</mark>。メッセージを編集した場合も、編集前と編集後の両方がAnthropicの記録に残ると説明されています（出典: 同上）。

## どういう人に効くか

**いま動かしてみるといい人**

- すでにSlackを日常的に使っていて、チームでの定型作業（バグの一次調査・議事録の整理・ダッシュボードの定期チェックなど）を1人のAIに集約したい人。
- Claude EnterpriseまたはTeamプランを契約している組織で、Slackワークスペースの管理者権限を持つ人。

**急がなくていい人**

- Free・Pro・Maxの個人プランを使っている人。Claude Tagはそもそも対象外です（出典: <https://claude.com/docs/claude-tag/overview>）。
- Slackを使っていない組織。Claude Tagは今のところSlack専用で、対応拡大の計画は「目標」としか書かれていません（出典: <https://www.anthropic.com/news/introducing-claude-tag>）。
- 導入初日に上限（spend limit）を設定できる担当者が決まっていない組織。Enterpriseプランは、上限を決めるまで請求に歯止めがかからない設計です。

**この記事で分からないこと**

実際に使ったときの応答の速さ、日本語での使い勝手、旧アプリ「Claude in Slack」との具体的な機能差。旧アプリの詳細ページ（support.claude.com）にはこの記事を書いた環境から到達できず、運営者も試していないため、体験としては書けません。

## 出典一覧

すべて公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Claude Tagの発表（Anthropic・2026年6月23日）: <https://www.anthropic.com/news/introducing-claude-tag>
2. Claude Tagの概要（claude.com 公式ドキュメント）: <https://claude.com/docs/claude-tag/overview>
3. Claude Tagの仕組み（claude.com 公式ドキュメント）: <https://claude.com/docs/claude-tag/concepts/how-it-works>
4. 上限（spend limit）の設定（claude.com 公式ドキュメント）: <https://claude.com/docs/claude-tag/admins/set-spend-limit>

OpenAI（`openai.com`・`help.openai.com`）、Microsoft（`learn.microsoft.com`）、Salesforce（`help.salesforce.com`）の関連ページには、この記事を書いた環境から到達できませんでした。Googleの `cloud.google.com/gemini-enterprise` は本体ページのみ到達でき、料金や連携機能の詳細は確認できていません。

料金と仕様は変わります。実際に導入する前に、必ず上記の公式ページで現在の値を確認してください。
