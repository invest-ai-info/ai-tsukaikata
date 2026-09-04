---
title: 動画を最大40秒まで伸ばせる——解像度で値段は10倍違う
description: Googleが2026年8月27日に発表した「Gemini Omni 1.1 Flash」について、公式発表ページ・APIドキュメント・料金ページに書かれている数字だけを並べました。360pの下書きと4Kの本番出力では、同じ長さでも秒単価が10倍違います。OpenAIのSora 2は約3週間後にAPI提供が終了すると告知されています。
category: tools
scene: choose
published: 2026-09-04
checked: 2026-09-04
tags: [Gemini, 動画生成, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年8月27日に **Gemini Omni 1.1 Flash** を発表しました（出典: <https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- <mark>動画の「続き」を伸ばせる長さが、10秒刻みで最大40秒まで</mark>になりました。直前10秒ぶんの内容を踏まえて続きを作れます（従来は直前1秒しか見ていませんでした）（出典: 同上）。
- **開発者向けのAPI利用は、解像度が4段階になりました。**360p・720p・1080p・4Kで、1秒あたりの値段はそれぞれ違います（出典: 同上）。
- 前のモデル（Gemini Omni Flash）は2026年5月19日の発表で、まず Gemini アプリ・Google Flow・YouTube Shorts 向けでした。API 経由で開発者が有料で使えるようになったのは、今回の更新からです（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**公式ページとドキュメントに書かれていることを読んで整理したものです。「きれいに繋がった」「速かった」といった使用感は一切書いていません。

Gemini の動画関連の機能としては、動画を「読む」ほうの [Agentic Video](/tools/gemini-agentic-video/) を別記事で扱っています。今回の Omni 1.1 Flash は逆に、動画を「作る・編集する」ほうのモデルです。

## 値段は解像度で10倍違う

発表ページには価格表が載っています（本文のテキストではなく、表の画像として埋め込まれています。この記事を書いた担当が画像を直接開いて目視で確認しました）。1秒あたりの値段は次のとおりです。

| 解像度 | Gemini Omni 1.1 Flash（1秒あたり） |
|---|---|
| 360p（下書き） | $0.03 |
| 720p（標準） | $0.10 |
| 1080p | $0.15 |
| 4K | $0.30 |

出典: <https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/>（発表ページに埋め込まれた価格表の画像）

<figure class="figure">
<img src="/static/images/omni11-resolution-price.svg" alt="Gemini Omni 1.1 Flash の解像度別・動画1秒あたりの価格を示した横棒グラフ。360p（下書き）は0.03ドル、720p（標準）は0.10ドル、1080pは0.15ドル、4Kは0.30ドル。360pから4Kまでで価格は10倍になる。価格は発表ページに埋め込まれた表の画像から読み取ったもので、本文のテキストではない。40秒のフル尺を作ると360pなら1.20ドル、4Kなら12ドルになる（この記事の計算）。トークン単位の課金では、720pは秒あたり約0.10ドル相当と公式ドキュメントが説明している。">
<figcaption>360pの下書きと4Kの本番出力では、同じ長さでも10倍の差になります</figcaption>
</figure>

<mark class="warn">360pから4Kまでで、値段はちょうど10倍になります</mark>。40秒のフル尺を作ると仮定すると、360pなら $1.20、4Kなら $12 です（この記事の計算）。下書きを360pで何度も作り直し、決まった案だけ4Kに上げる、という使い方が値段の面では合理的です。

料金ページには、この価格をトークン単位の課金で説明している箇所もあります。<mark>入力は100万トークンあたり $1.50（テキスト・画像・動画・音声共通）、出力は動画が100万トークンあたり $17.50</mark>で、「720pの動画は1秒あたり5,792トークンとして計算し、これは実効的に1秒あたり約 $0.10 に相当する」と明記されています（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。上の表の720pの行と一致します。

なお、これはAPIで開発者が使う場合の値段です。**Google AI Plus・Pro・Ultra の契約者は、Google Flow と Gemini アプリの中で追加料金なしに使えます**（出典: 発表ページ、同上）。YouTube Shorts・YouTube Create App でも無料で使えると、前のモデルの発表時に案内されています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/>）。

## 前のモデルとの違い

### 解像度の選択肢が増えた

料金ページを見ると、前の Gemini Omni Flash（無印）は <mark>720pの1段階だけで、360p・1080p・4Kの行は「—」（提供なし）</mark>になっています（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。今回の 1.1 Flash で、下書き用の安い360pと、本番用の1080p・4Kが新しく加わった形です。

### 参照する秒数が10倍になった

発表ページには「Omni 1.1 は直前10秒ぶんの内容を踏まえられるようになった。従来のモデルは直前1秒しか参照していなかった」と明記されています（出典: 同上）。<mark>動画を伸ばすとき、直前の場面をどれだけ覚えていられるかが10倍</mark>になったということです。

<figure class="figure">
<img src="/static/images/omni11-scene-extension.svg" alt="シーン延長のとき、モデルが参照する直前の秒数を示した図。従来のモデルは1秒、Gemini Omni 1.1 Flashは10秒を参照する。延長は10秒刻みで、10秒・20秒・30秒・40秒と合計40秒まで積み増せる。延長は動画の最後にしか継ぎ足せず、途中への挿入や先頭への追加はできないと明記されている。アップロードした動画の延長はEU・スイス・英国では利用できないが、モデルが生成した動画の延長・複数ターンでの継続は全地域で利用できる。">
<figcaption>直前1秒しか見ていなかった延長が、10秒を見て最大40秒まで伸びます</figcaption>
</figure>

伸ばせる長さそのものにも上限があります。<mark class="warn">延長は10秒刻みで、合計40秒までしか積み増せません</mark>（出典: 同上）。それ以上の尺が必要な場合は、この機能だけでは足りないということです。

延長には他にも制約が書かれています。**延長は動画の最後にしか継ぎ足せず、途中への挿入や先頭への追加はできません**（出典: <https://ai.google.dev/gemini-api/docs/omni>）。自分の動画をアップロードして延長する場合、<mark class="warn">EU（欧州経済領域）・スイス・英国では利用できない</mark>と明記されています。ただし、モデルが生成した動画をそのまま複数ターンで延長する使い方は、地域を問わず利用できるとも書かれています（出典: 同上）。

### 新しく増えた操作

発表ページによると、今回の更新で次の操作が使えるようになりました（出典: 同上）。

- **始点・終点フレームの指定**: 開始フレームと終了フレームを指定すると、その間を滑らかにつなぐ動画を生成できます。
- **360pの下書きモード**: 720p標準に比べて「最大60%速く、3分の1の値段」で生成できます（発表ページの注記）。
- **1080p・4Kへのアップスケール**: 本番用の高解像度出力に対応しました。
- **動画リファレンス**: 最大3本まで、1本につき3秒ぶんの動画を参照として使えます。ただし**動画リファレンスに含まれる音声は無視される**と明記されています（出典: 同上）。

## 他社の最上位モデルとの比較

720pで音声付きの動画を1秒作る値段を、同じ条件で並べます。

| モデル | 720p・1秒あたり |
|---|---|
| Gemini Omni 1.1 Flash | $0.10 |
| Veo 3.1 Lite | $0.05 |
| Veo 3.1 Fast | $0.10 |
| Veo 3.1 Standard | $0.40 |
| Sora 2（OpenAI） | $0.10 |
| Sora 2 Pro（OpenAI） | $0.30 |

出典: Google の3モデルは <https://ai.google.dev/gemini-api/docs/pricing>、OpenAI の2モデルは <https://developers.openai.com/api/docs/pricing>

<figure class="figure">
<img src="/static/images/omni11-vendor-720p-price.svg" alt="720p・音声付き動画1秒あたりの価格を6モデルで比べた横棒グラフ。Gemini Omni 1.1 Flashは0.10ドル、Veo 3.1 Liteは0.05ドル、Veo 3.1 Fastは0.10ドル、Veo 3.1 Standardは0.40ドル、Sora 2は0.10ドル、Sora 2 Proは0.30ドル。Sora 2とSora 2 Proは、Videos APIごと2026年9月24日に提供終了と公式が告知しており、同ページに後継モデルの案内は無い。Anthropicは動画生成モデルを提供していない。">
<figcaption>720pなら、GeminiとSoraの標準モデルは同じ$0.10です</figcaption>
</figure>

<mark>720pだけで見ると、Gemini Omni 1.1 Flash と OpenAI の Sora 2 は同じ $0.10 です</mark>。GoogleはVeo 3.1という別ブランドで、さらに安いLite（$0.05）から高品質なStandard（$0.40）まで幅を用意しています。

ただし Sora 2 には、値段以前の大きな注意点があります。<mark class="warn">OpenAI は Sora 2・Sora 2 Pro を含む Videos API 全体を2026年9月24日に終了すると告知しています</mark>（2026年3月24日付の告知。出典: <https://developers.openai.com/api/docs/deprecations>）。この記事を確認した時点（2026年9月4日）で、20日後に迫っています。**確認したページの中に、後継モデルの案内はありませんでした。**Sora 2 は16秒・20秒の動画に対応していますが（出典: <https://developers.openai.com/api/docs/guides/video-generation>）、そのAPI自体がまもなく使えなくなります。

Anthropic はどうでしょうか。公式のモデル一覧ページには「現行モデルはすべてテキスト・画像入力、テキスト出力に対応」と書かれており、<mark>動画の生成や編集についての記載はありません</mark>（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。無理に並べず「提供していない」と書いておきます。

## どういう人に効くか

**いま動かしてみるといい人**

- Google AI Plus・Pro・Ultra を契約していて、Google Flow か Gemini アプリで動画を作りたい人。追加料金なしで、始点・終点フレーム指定や4Kアップスケールが使えます。
- YouTube Shorts・YouTube Create App で動画を作っている人。無料で使えると案内されています（前モデルの発表時点の情報）。
- API 経由で開発者として使う人で、下書きと本番出力を分けたい人。<mark>360pの下書きで何度も試し、決まった案だけ4Kに上げれば、値段を10分の1に抑えられます</mark>。

**急がなくていい人・注意が必要な人**

- 自分で撮影した動画をアップロードして延長・編集したい人のうち、EU・スイス・英国から使う人。**その用途は今のところ利用できません。**
- 40秒を超える尺が必要な人。延長機能の上限は合計40秒です。
- 動画の音声だけを差し替えたい人。**音声編集（Voice editing）は非対応**と明記されています（出典: <https://ai.google.dev/gemini-api/docs/omni>）。
- 日本語での品質を重視する人。ドキュメントは「英語は十分にサポートされているが、他の言語は評価されておらず、結果にばらつきがある」と明記しています（出典: 同上）。

**この記事で分からないこと**

実際に生成した動画の質、日本語プロンプトでの精度、生成にかかる待ち時間。発表ページには利用企業の声（Adobe・Figma・GMI Cloud・Runway）も載っていますが、どういう条件で作った動画の感想なのかは書かれていないため、この記事では比較に使っていません。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini Omni 1.1 Flash の発表（Google・2026年8月27日）: <https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-omni-1-1-flash/>
   （Google DeepMind 側の <https://deepmind.google/blog/gemini-omni-1-1-flash-lets-you-build-with-more-control/> を開くと、このページへ転送されます）
2. Gemini Omni（無印・前モデル）の発表（Google・2026年5月19日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/>
3. Gemini Omni Flash のモデルカード（Google DeepMind 公式）: <https://deepmind.google/models/model-cards/gemini-omni-flash/>
4. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
5. Gemini Omni Flash の開発者ドキュメント（Google 公式）: <https://ai.google.dev/gemini-api/docs/omni>
6. Sora の動画生成ガイド（OpenAI 公式）: <https://developers.openai.com/api/docs/guides/video-generation>
7. API の料金（OpenAI 公式）: <https://developers.openai.com/api/docs/pricing>
8. 提供終了の一覧（OpenAI 公式）: <https://developers.openai.com/api/docs/deprecations>
9. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>

料金と仕様は変わります。実際に支払う前に、必ず上記の公式ページで現在の値を確認してください。
