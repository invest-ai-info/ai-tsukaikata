---
title: Googleの記憶は暗号化——使える製品も時期もまだ無い
description: 2026年9月23日にGoogle DeepMindが発表した「Private AI Compute」の記憶機能の更新について、公式発表ページと2025年11月の初出発表に書かれていることだけを整理しました。クラウドに預けた記憶も暗号化し、鍵は端末側だけが持つと説明されていますが、対象の製品名も提供時期も書かれていません。Anthropic・OpenAIの記憶機能とも比べています。
category: tools
scene: choose
published: 2026-09-23
checked: 2026-09-23
tags: [Google, Gemini, プライバシー, AI最新情報]
---

## 結論：三つに分けて読むとこうなる

Google DeepMindは2026年9月23日に発表しました。**Private AI Compute**というクラウド処理基盤に、「永続的な記憶」を追加するという内容です（出典: <https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory/>）。読者の立場ごとに、分かったことをまとめます。

| 読者の立場 | 発表の中身 | いま出来ること |
|---|---|---|
| Pixelや Gemini のアプリを使っている人 | 端末をまたいで記憶を持ち越す仕組みが、今後 Private AI Compute に加わる | 対象の製品名も提供時期も発表に無い。今日から使える機能ではない |
| プライバシーを重視する人 | クラウドに預けた記憶も暗号化し、鍵は自分の端末だけが持つとGoogleは説明している | 技術文書と独立監査の結果は公開されたが、この記事はそのPDF自体を確認できていない |
| Claude・ChatGPTの記憶機能と比べたい人 | 3社の「記憶」は、そもそも設計の説明の仕方が違う | OpenAIの該当ページは今回もbot判定で読めず、比較できなかった |

<mark>一言でいうと、Googleは「クラウドに預けても中身は見えない」設計を発表しました。対象製品も提供時期もまだありません</mark>。

先に断っておきます。**この記事は運営者がこの機能を試した記録ではありません。**公式発表ページと関連ページに書かれていることを読んで整理したものです。

ここから下は、表の3行がなぜそうなるのかの説明です。

## なぜそうなるのか

### 「消える記憶」から「残る記憶」への変化

Private AI Computeは、Googleが2025年11月11日に発表した処理基盤です。Gemini のクラウドモデルを使いながら、端末で処理するのと同じプライバシー保証を目指しています（出典: <https://blog.google/innovation-and-ai/products/google-private-ai-compute/>）。処理には自社製のチップ（TPU）を使うと説明されています。隔離環境には"Titanium Intelligence Enclaves（TIE）"という技術を使っています（出典: 同上）。

<mark>公開当初のPrivate AI Computeは、処理が終わると文脈が消える「ステートレス」設計でした</mark>。<mark>実際に使われていたのは、Pixel 10のMagic CueとRecorderアプリの2つだけでした</mark>。この基盤を使う目的は、それぞれ次のとおりです（出典: 同上）。

- **Magic Cue**：より時宜にかなった提案を返すため
- **Recorderアプリ**：文字起こしの要約を多言語に広げるため

今回の発表は、この「消える」性質を変えるというものです。発表ページは、記憶をクラウドの「安全な金庫」のように機能させると説明しています。例として挙げているのは、スマートグラスで見た手順の続きをパソコンで開く、という使い方です（出典: <https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory/>）。

<figure class="figure">
<img src="/static/images/pac-before-after.svg" alt="従来のPrivate AI Computeと今回の発表を2列で比べた図。従来（2025年11月〜）＝処理が終わると記憶は消える、対象はPixel 10のMagic CueとRecorderアプリの文字起こし要約、端末をまたぐ会話の継続は無い。今回の発表（2026年9月23日）＝永続的な記憶の層を追加すると発表、暗号化した「金庫」にクラウド保存、鍵は利用者の端末だけが持つ、対象製品・提供時期は発表に無い。">
<figcaption>器（Private AI Compute）は同じで、中身の性質が変わりました</figcaption>
</figure>

<mark class="warn">ただし、この変化はまだ発表の段階です</mark>。どの製品に、いつ搭載されるかは、発表ページのどこにも書かれていません。「今日から使える」という話ではありません。

### なぜ「Googleも読めない」と言えるのか

発表ページは、記憶データの扱いを次のように説明しています。「情報は専用の暗号化ストレージに封じ込められ、それを開く鍵は利用者本人の端末だけが持つ」（出典: 同上。原文: “the information needed to assist you is sealed within dedicated, encrypted storage, while the cryptographic keys required to unlock it are held exclusively on your personal devices”）。

仕組みは3段階で説明されています（出典: 同上）。

1. 端末とクラウドを、認証済みの暗号化された通信でつなぐ
2. クラウド側の「セキュアエンクレーブ」が、処理している間だけデータを一時的に復号する
3. 処理が終わったら新しい文脈も含めてすぐに再暗号化し、保存する

<figure class="figure">
<img src="/static/images/pac-architecture-flow.svg" alt="利用者の端末からセキュアエンクレーブを経て暗号化された保管庫に至る、Googleの説明を図にしたもの。利用者の端末は暗号の鍵をここだけに保管しGoogleのサーバーには渡さない。暗号化した通信でセキュアエンクレーブ（クラウド側・隔離された領域）に接続し、処理中だけ一時的に復号する。終わったらすぐ再暗号化して、暗号化された保管庫に保存する。鍵が無いと中身は読めない。下の枠には、独立監査の結果と技術文書の更新も公開したとGoogleが書いていること、ただしその技術文書（PDF）はこの記事を書いた環境からは経路遮断で開けず、監査の中身は発表ページの説明の範囲でしか確認できていないことが書かれている。">
<figcaption>鍵は端末側だけが持ち、クラウドは復号したまま保存しない設計です</figcaption>
</figure>

<mark>この設計だと、Google自身もデータを読めないとGoogleは説明しています</mark>。初出の発表（2025年11月）から使われている文言です。「あなたのデータは他の誰からも、Googleからさえもアクセスできません」（出典: <https://blog.google/innovation-and-ai/products/google-private-ai-compute/>。原文: “not accessible to anyone else, not even Google”）。

透明性の裏付けとして、Googleは次の3つを公開したと書いています（出典: <https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory/>）。

- 技術文書（whitepaper）の更新
- サーバーソフトウェアの改ざんを検知できる、公開の記録
- 独立したセキュリティ企業による監査の結果

<mark class="warn">ただし、この記事はその技術文書（PDF）自体を確認できていません</mark>。配信元のドメインは `services.google.com` です。この記事を書いた環境の許可リストに無く、経路遮断で開けませんでした。監査を行った企業名や、監査で具体的に何を調べたかは、この記事では検証できていません。

### 他社の「記憶」機能との違い

同じ「AIが記憶する」機能でも、各社の説明の中身は違います。この記事で確認できた範囲を並べます。

<figure class="figure">
<img src="/static/images/pac-vendor-grid.svg" alt="AIの「記憶」機能を、暗号化の説明・鍵の保管場所・現在使えるかで3社比べた表。暗号化の説明＝Googleはクラウド上でも暗号化すると説明、Anthropicは発表ページに暗号化方式の記載なし、OpenAIは確認できず。鍵の保管場所＝Googleは利用者の端末のみでGoogleは持たない、Anthropicは記載なし、OpenAIは確認できず。現在使えるか＝Googleは発表のみで提供時期は未定、Anthropicは Team/Enterprise・Pro/Maxで提供中、OpenAIは確認できず。OpenAIの該当ページはbot判定の403でこの記事からは確認できなかった。">
<figcaption>暗号化を明言しているのは、3社のうちGoogleだけでした</figcaption>
</figure>

**Anthropicの記憶機能は、すでに提供中です。**提供の経緯は次のとおりです（出典: <https://claude.com/blog/memory>）。

- **2025年9月11日**：Team・Enterprise向けに記憶機能を提供開始
- **2025年10月23日**：Pro・Maxプランにも拡大

<mark>プロジェクトごとに別々の記憶を持ち、利用者は「記憶の要約」を見て自分で編集できます</mark>。記憶に残したくない対話は、Incognitoチャットを選べます（出典: 同上）。

<mark>ただし、Anthropicの発表ページには、暗号化の方式についての説明がありません</mark>。「端末側だけが鍵を持つ」といった、Googleの発表にあるような設計の記述は見当たりませんでした（出典: 同上）。<mark class="warn">書かれていないことは、暗号化していないという意味ではありません。この記事が確認できなかっただけです</mark>。

**OpenAIのChatGPTにも記憶機能がありますが、この記事では確認できませんでした。**該当するページ（`openai.com`・`help.openai.com`）は、いずれも Cloudflare の bot 判定による403でした（`cf-mitigated: challenge` というヘッダーを確認済み）。この種類の遮断は、環境の許可リストを増やしても直りません。二次情報で埋めることはしないので、OpenAIの列は「確認できず」のままにしてあります。

Claudeの他の機能については、[Claude利用の振り返り機能「Reflect」の記事](/tools/reflect-with-claude/)にも書いています。

## この記事で分からないこと

- どの製品・アプリに、いつ搭載されるか（発表ページに記載なし）
- 記憶を保存できる期間や容量の上限
- 独立監査を行った企業名と、監査で具体的に何を調べたか（技術文書が未確認のため）
- 実際に使ったときの体感。運営者は試していないので書けません

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Advancing Private AI Compute with secure, server-side memory（Google DeepMind・2026年9月23日）: <https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory/>
2. Google Private AI Compute（Google・2025年11月11日・初出発表）: <https://blog.google/innovation-and-ai/products/google-private-ai-compute/>
3. Bringing memory to Claude（Anthropic・2025年9月11日）: <https://claude.com/blog/memory>

Private AI Computeの技術文書（PDF）は、この記事を書いた環境からは到達できませんでした。配信元は `services.google.com` で、経路遮断が理由です。OpenAIのChatGPTメモリー機能の公式ページも、bot判定の403で到達できませんでした。

料金・仕様・提供状況は変わります。実行する前に必ず上記の公式ページで現在の情報をご確認ください。
