---
title: Claudeで生命科学の壁を外す——個人プランはまだ使えない
description: Anthropicが2026年9月17日に発表した「Life Sciences Verification Program」について、公式発表ページと料金ページに書かれている数字だけを整理しました。検証を受けた団体は、通常ブロックされる創薬などの作業ができますが、対象はチーム・団体のβ版のみで個人のPro・Maxプランはまだ使えません。OpenAIの専用モデルとの料金比較も載せています。
category: tools
scene: choose
published: 2026-09-17
checked: 2026-09-17
tags: [Claude, Anthropic, 生命科学, AI安全性, AI最新情報]
---

## 何が変わったか

Anthropicは2026年9月17日、**Life Sciences Verification Program（LSVP）**を発表しました（出典: <https://www.anthropic.com/news/life-sciences-verification-program>）。生命科学の専門家が、Mythos・Opus・Sonnetの各モデルを、生物学関連の作業向けに安全策を調整した状態で使えるようにする制度です。公式ページに書かれていることだけを並べます。

- 審査を通った団体は、**通常は一般提供モデルでブロックされている作業**（創薬・研究biology・臨床開発・製造など）を行えるようになります（出典: 同上）。
- グラントは**Standard Use**と**High-risk Use**の2種類があり、審査の厳しさと更新周期が違います（詳しくは次の節）。
- 現在は**チームや団体向けのβ版**で、個人向けのPro・Maxプランへの拡大は「今後」と書かれているだけで、時期は明記されていません（出典: 同上）。

先に断っておきます。**この記事は運営者がこの制度を実際に使った記録ではありません。**申請には研究資格などの審査があり、運営者は対象になりません。発表ページに書かれていることを読んで整理したものです。「使いやすかった」といった感想は一切書いていません。

## 検証を受けると、何ができるようになるか

審査では、研究者としての資格・セキュリティ体制・研究倫理上の監督体制が確認されると説明されています（出典: 同上）。審査を通った団体は、次の2種類のグラントを申請できます。

<figure class="figure">
<img src="/static/images/lsvp-grant-types.svg" alt="Standard UseとHigh-risk Useの違いを示した表。対象範囲＝Standard Useはチーム全体で毎日の幅広い業務向け、High-risk Useは研究プロジェクト単位で1件ずつの申請。更新周期＝Standard Useは年に1回、High-risk Useは半年に1回。対象モデル＝Standard UseはMythos 5.1・Opus 5・Sonnet 5（将来のモデルにも適用）、High-risk UseはOpus 5・Sonnet 5で、Mythosは米政府の追加審査を受けた団体のみ。セーフガード＝Standard Useは科学タスク向けに分類器を緩和、High-risk Useは生命科学関連のブロックをすべて解除。サイバー攻撃対策などの安全策は、どちらのグラントでも維持されると明記されている。">
<figcaption>Standard Useは年1回更新、High-risk Useは半年ごとに更新です</figcaption>
</figure>

<mark>Standard Useはチーム全体に広げられ、更新は年に1回です</mark>。基礎研究・研究開発・サプライチェーンと製造・臨床開発・品質保証・規制対応・投資判断まで、幅広い業務が対象だと説明されています（出典: 同上）。

<mark class="warn">High-risk Useは、Standard Useではブロックされる作業のための追加グラントで、生命科学関連の安全策をすべて解除します</mark>（出典: 同上。原文: “It removes all safeguards that block life sciences requests.”）。ただしチーム全体ではなく**単一の研究プロジェクトにしか適用されず**、更新は半年に1回です。発表ページの例では「特定のウイルスベクターが人の免疫経路にどう認識されるかを調べる」といった、二重用途になりうる個別プロジェクトへの適用が想定されています（出典: 同上）。

<mark>MythosでHigh-risk Useを使えるのは、追加の米政府審査を受けた一部の団体だけです</mark>（出典: 同上）。Opus 5とSonnet 5のHigh-risk Useは今日から使えますが、Mythosは当面この狭い対象に限られると書かれています。

サイバー攻撃対策の分類器など、生命科学に関係しない安全策はどちらのグラントでも維持されると明記されています（出典: 同上。原文: “All other safeguards, such as cyber classifiers, will remain in place under LSVP grants.”）。ブロックが外れるのはあくまで生命科学関連の判定だけです。

## 安全策の切り替え方——都度ブロックから、あとでまとめて見る方式へ

LSVPでは、違反の見つけ方そのものが変わると説明されています。想定する脅威は3つ挙げられています。アクセス権の乗っ取り（マルウェアやアカウント乗っ取り）、内部関係者による悪用、そしてエージェントの暴走（複数エージェントが連携・長時間タスクで意図しない危険な行動を取る）です（出典: 同上）。

<figure class="figure">
<img src="/static/images/lsvp-monitoring-shift.svg" alt="安全策の仕組みの変化を示した表。違反の検知＝従来は申請のたびにリアルタイムでブロック、LSVPでは行動パターンをオフラインでまとめて分析。データの保持＝従来は個々の申請で完結し保持の記載なし、LSVPでは30日間保持し学習利用・内部チームの閲覧は禁止。見つかったら＝従来はその場でブロックして終了、LSVPでは組織の管理者に通知し合意した期限内に対応。保持したデータはモデルの学習に使われず、Anthropicの生命科学研究チームもアクセスできないと明記されている。">
<figcaption>都度ブロックから、あとでまとめて見る方式に変わりました</figcaption>
</figure>

<mark>従来の「申請のたびに即座にブロックする」方式から、行動パターンをまとめて見る「オフライン監視」に変わりました</mark>（出典: 同上。原文: “we are shifting safeguards from real-time blocking … to offline monitoring”）。単発の申請では正常に見えても、複数の申請・セッションにまたがると悪用のパターンが見えてくる、という理屈です。

<mark class="warn">この監視のために、LSVP経由の通信は30日間保持されると明記されています</mark>（出典: 同上。原文: “we are requiring data retention for 30 days to be able to do this monitoring effectively.”）。<mark>保持したデータはモデルの学習には使われず、Anthropicの生命科学研究チームのメンバーもアクセスできないと書かれています</mark>（出典: 同上）。

違反の疑いが見つかった場合は、団体の管理者に通知し、あらかじめ合意した期限内に対応してもらう仕組みだと説明されています（出典: 同上）。ブロックして終わりではなく、団体側の管理責任と組み合わせる設計です。

## 他社の類似プログラムとの比較

生命科学向けにAIモデルへのアクセスを調整する制度は、Anthropicだけのものではありません。OpenAIの公式ページを確認したところ、似た制度が見つかりました。

<figure class="figure">
<img src="/static/images/lsvp-vendor-grid.svg" alt="生命科学向けのアクセス制度を3社で比べた表。アプローチ＝Anthropicは一般提供モデルに検証者向けの緩和策を適用、OpenAIは生命科学専用のGPT-Rosalindを新設、Googleは確認できず。対象＝Anthropicは研究資格などを審査した団体・チーム、OpenAIはTrusted Access Programの承認組織、Googleは記載なし。価格の目安（100万トークンあたり）＝Anthropicは既存モデルの通常価格で入力2〜10ドル・出力10〜50ドル、OpenAIはgpt-rosalind-researchが入力5ドル・出力25ドルで2026年10月5日に課金開始、Googleは記載なし。">
<figcaption>Claude Opus 5とGPT-Rosalindの専用モデルは、単価が同額でした</figcaption>
</figure>

<mark>OpenAIは同じ生命科学向けに、専用モデル「GPT-Rosalind」を新設しています</mark>（出典: <https://developers.openai.com/api/docs/models>。同ページの「Life sciences」の項目に「GPT-Rosalind Life sciences reasoning for approved organizations」と記載）。Anthropicが一般提供の3モデルに検証済み利用者向けの調整を加える設計なのに対し、OpenAIは生命科学専用のモデルを別枠で用意する設計です。

OpenAIの公式ニュースRSS（<https://openai.com/news/rss.xml>）には、2026年5月29日付で「Rosalind Biodefense」という取り組みの要旨が載っています。「vetted developers and U.S. government partners（審査済みの開発者と米政府のパートナー）」に、生物防衛・公衆衛生・パンデミック対策向けにGPT-Rosalindへの信頼されたアクセスを広げる、と書かれています。⚠️ 出典は同RSSです。発表ページ本体〈openai.com〉はこの記事を書いた環境からは開けず、確認できたのはRSSの要旨1文だけでした。

料金ページでは、gpt-rosalind-researchの単価も確認できました。<mark>Claude Opus 5とOpenAIのgpt-rosalind-researchは、100万トークンあたり入力$5・出力$25で同額です</mark>（出典: <https://platform.claude.com/docs/en/about-claude/pricing>、<https://developers.openai.com/api/docs/pricing>）。文脈キャッシュの再利用価格も、Opus 5の「Cache hits and refreshes」が$0.50、gpt-rosalind-researchの「Cached input」が$0.50で一致しています。ただしキャッシュの仕組み（書き込み・読み取りの区分）は会社ごとに違うため、金額が同じでも課金の細かい条件までは一致しません。

| モデル | 入力（100万トークン） | 出力（100万トークン） | キャッシュ再利用 |
|---|---|---|---|
| Claude Sonnet 5 | $2 | $10 | $0.20 |
| Claude Opus 5 | $5 | $25 | $0.50 |
| Claude Mythos 5.1（限定提供） | $10 | $50 | $0.25 |
| gpt-rosalind-research（OpenAI） | $5.00 | $25.00 | $0.50 |

出典: Claude各モデルは<https://platform.claude.com/docs/en/about-claude/pricing>、OpenAIは<https://developers.openai.com/api/docs/pricing>

<mark class="warn">gpt-rosalind-researchの課金は2026年10月5日に始まると料金ページに明記されており、この記事の確認時点（2026年9月17日）ではまだ始まっていません</mark>（出典: <https://developers.openai.com/api/docs/pricing>。原文: “Billing for gpt-rosalind-research begins on October 5, 2026.”）。またこのモデルは「Access is limited to approved internal research through the trusted-access program（trusted-access programで承認された内部研究に限る）」と明記されており、OpenAI側もAnthropicのLSVPと同じく、審査を通った組織だけに提供する形です（出典: 同上）。

Googleについては、DeepMindの研究一覧ページ（<https://deepmind.google/science/>）と、Google Cloudのフロンティア安全フレームワークのページ（<https://cloud.google.com/security/ai/frontier-safety-framework>）を確認しましたが、生命科学向けの検証済みアクセス制度についての記載は見当たりませんでした。**同種の制度が無いと断定はできず、「この記事を書いた環境で確認できた公式ページには見当たらなかった」というところまでです。**

## 使える範囲、まだ来ていない範囲

β版としての制約も、発表ページに具体的に書かれています。

- 利用できるのは、API利用時の第一者コンソール、Claude for EnterpriseとTeamプランです。**個人向けのプランと、他社のプラットフォーム経由では、まだ利用できません**（出典: 同上）。
- <mark class="warn">個人向けのPro・Maxプランは、現時点ではまだ対象外です</mark>（出典: 同上。原文: “We do not yet support individual plans but are working to expand access for these users.”）。
- <mark>BAA（医療データの取り扱いに関する契約）を結んだ組織は、このβ版では利用できないと明記されています</mark>（出典: 同上。原文: “As a beta, LSVP is not available for BAA-enabled orgs.”）。PHI（保護対象保健情報）を扱う顧客は、非BAA・非HIPAAの別組織を使うようにと案内されています（出典: 同上）。
- API・Claude Scienceでは複数のグラントを切り替えて使えます。一方、Claude.aiとClaude Codeでは、当初はあらかじめ選ばれた既定のグラントしか適用されないと書かれています（Claude CodeでAPI認証を使う場合を除く。出典: 同上）。

早期アクセスの連携先として、次の3社が名前を挙げられています（出典: 同上）。

- Xaira Therapeutics
- Edison Scientific
- Manifold Bio

この3社を含む「数十の団体」がすでに導入済みだと説明されています。申請は初週で数百件に達する見込みで、今後さらに規模を広げるとしています（出典: 同上）。

## どういう人に効くか

**この制度が直接関係する人**

- 製薬会社・バイオ系のスタートアップ・研究機関で、これまで安全策のブロックに阻まれてClaudeを使えなかった作業がある人。まずはStandard Useの対象範囲（基礎研究〜規制対応〜投資判断まで）に自分の業務が含まれるか、発表ページで確認する価値があります。
- 組織のセキュリティ・コンプライアンス担当者。監視方式の変更（リアルタイムブロック→オフライン監視、30日保持）は、社内でAI利用のリスク管理を説明する材料になります。

**急がなくていい人**

- 個人でPro・Maxプランを契約している人。まだ対象外で、拡大の時期も発表ページには書かれていません。
- 一般的な事務作業や情報収集にAIを使っている、このサイトの主な読者。今回の制度は生命科学分野の専門的な作業向けで、日常業務には関係しません。安全策の設計として「一律のブロックから、審査＋事後監視に切り替える」という考え方自体は、AIの使い方の変化として知っておく価値があります。

**この記事で分からないこと**

審査にかかる期間、実際に承認された団体がどんな作業を行っているかの具体例、日本の団体が申請できるかどうか。発表ページにはいずれも記載がなく、運営者もこの制度を使っていないため書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Life Sciences Verification Programの発表（Anthropic・2026年9月17日）: <https://www.anthropic.com/news/life-sciences-verification-program>
2. Claudeモデルの料金（Anthropic公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/pricing>
3. モデル一覧（OpenAI公式ドキュメント。GPT-Rosalindの記載を確認）: <https://developers.openai.com/api/docs/models>
4. APIの料金（OpenAI公式ドキュメント。gpt-rosalind-researchの単価を確認）: <https://developers.openai.com/api/docs/pricing>
5. OpenAI公式ニュースのRSS（Rosalind Biodefenseの要旨を確認）: <https://openai.com/news/rss.xml>
6. DeepMindの研究一覧（Google公式。生命科学向けの検証制度は確認できず）: <https://deepmind.google/science/>
7. フロンティア安全フレームワーク（Google Cloud公式。同上）: <https://cloud.google.com/security/ai/frontier-safety-framework>

制度の詳細・対象範囲は変わります。実際に申請する前に、必ず上記の公式ページで現在の内容を確認してください。
