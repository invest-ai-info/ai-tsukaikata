---
title: Geminiが動画を「必要な所だけ」読む——短い動画では逆に遅い
description: 2026年9月1日にGoogleが発表した「エージェント型の動画理解」について、公式発表ページとGemini APIドキュメントに書かれている数字だけを並べました。長い動画ほどトークンが減る一方、短い動画では探しに行く分だけ最初の応答が遅くなると明記されています。
category: tools
scene: choose
published: 2026-09-03
checked: 2026-09-03
tags: [Gemini, 動画理解, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年9月1日、**Gemini 3.7 Flash・3.6 Flash・3.5 Flash-Lite に「エージェント型の動画理解」を追加した**と発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- これまでの動画の読み方（静的処理）は、**動画を1秒ごとに一律の速さでコマ送りにして読む**方式でした（出典: 同上）。
- 新しいエージェント型は、<mark>モデル自身が「どこを・どの速さで・映像か音声か文字起こしか」を考えながら、必要な部分だけを探しに行きます</mark>（出典: 同上）。
- 効果は、標準的な動画分析のベンチマークで**トークン消費が最大88%減、コストが最大66%減、精度が最大7%向上**したとGoogleは説明しています（出典: 同上）。

先に断っておきます。**この記事は運営者がこの機能を試した記録ではありません。**公式ページとGemini APIドキュメントに書かれていることを読んで整理したものです。「速かった」「見落としが減った」といった使用感は一切書いていません。

## 前のモデルとの違い（「静的」と「エージェント型」の違い）

### 読み方そのものが変わった

Gemini API のドキュメントには、動画の読み方が2つ用意されていると書かれています（出典: <https://ai.google.dev/gemini-api/docs/video-understanding>）。

| モード | 読み方 | 対応モデル |
|---|---|---|
| 静的（既定） | 1秒に1コマを一律に抜き出して、一気に読み込む | すべてのGeminiモデル |
| エージェント型 | モデルがタイムラインを自分で探索し、必要な映像・音声・文字起こしだけを読み込む | Gemini 3.8 Flash・3.7 Flash・3.6 Flash・3.5 Flash-Lite |

出典: 同上

<figure class="figure">
<img src="/static/images/agentic-video-gains.svg" alt="エージェント型の動画理解に切り替えたときの3つの変化を示した横棒グラフ。トークン消費は最大88%減、コストは最大66%減、精度（品質）は最大7%向上。いずれもGoogleが発表ページで挙げた標準的なベンチマークでの最大値で、個々のベンチマーク名や中間の数値は公表されていない。対象はGemini 3.7 Flash・3.6 Flash・3.5 Flash-Liteで、効果は長尺の動画ほど大きい。">
<figcaption>「最大」の値です。動画の内容によってはここまで変わりません</figcaption>
</figure>

<mark>この効果がとくに大きいのは、10分の作業解説から90分の講義、数時間の録画まで含む「長尺の動画」です</mark>（出典: 同上）。静的処理だと、長い動画をコマ数どおりに全部読み込むか、精度を落として間引くかの二択になっていたところに、選択肢が増えた形です。

### 短い動画では、むしろ遅くなる

<mark class="warn">エージェント型には裏があります。ドキュメントには「短い動画（5分未満）では、内部の考え込みとツールの往復のせいで、最初の応答までの時間（Time to First Token）がわずかに伸びることがある」とはっきり書かれています</mark>（出典: 同上）。ドキュメントの推奨は明確で、**長い動画や特定の場面を探す用途はエージェント型、待ち時間が大事な短い動画は静的**、と使い分けを勧めています（出典: 同上）。

トークンの数え方も具体的に書かれています。静的処理は「低い解像度なら動画1秒あたり約100トークン、高い解像度なら約300トークン」で計算できます（出典: 同上）。エージェント型は内容によって変わるため、この定額の計算式が使えません。

### 追加料金はゼロ、単価も変わらない

<mark>この機能を使うのに追加の料金はかかりません。通常のGemini APIのトークン単価がそのまま適用されます</mark>（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/>）。料金ページで実際の単価を確認すると、こうなっています。

| モデル | 入力（100万トークン） | 出力（100万トークン） |
|---|---|---|
| Gemini 3.8 Flash | $0.75（2026年12月31日まで。以降$1.50） | $3.75（以降$7.50） |
| Gemini 3.7 Flash | $0.75（同上） | $3.75（同上） |
| Gemini 3.6 Flash | $0.75（同上） | $3.75（同上） |
| Gemini 3.5 Flash-Lite | $0.30 | $2.50 |

出典: すべて <https://ai.google.dev/gemini-api/docs/pricing>

<mark>対応している上位3モデルは、いま出ている単価が全部同じです</mark>。つまりこの機能を使うために上の世代へ乗り換えても、トークン単価そのものは上がりません。3.5 Flash-Liteだけ単価が別枠で、入力・出力とも上位モデルより安い代わりに、動画の扱いは同じエージェント型に対応しています。

### 実は「2つ目」の機能だった

<figure class="figure">
<img src="/static/images/agentic-video-timeline.svg" alt="GeminiのAgentic機能が広がった年表。2026年1月27日、Gemini 3 Flashに画像向けのAgentic Visionを発表（コード実行で画像を拡大・注釈し、精度が最大10%上がると説明）。その217日後の9月1日、動画向けのAgentic Videoを発表。対象はGemini 3.7 Flash・3.6 Flash・3.5 Flash-Liteの3つ。9月3日（この記事の確認時点）では、公式ドキュメントの対応モデルが4つに増えており、発表には無かったGemini 3.8 Flashも対応と追記されている。217日という日数は暦日の単純な引き算。Agentic VisionとAgentic Videoは別の機能で、対象モデルも仕組みも別。3.8 Flashが対応に加わった正確な日付はドキュメントに記載がない。">
<figcaption>「エージェント型」は動画が初めてではありません</figcaption>
</figure>

発表ページ自身が「画像向けのAgentic Visionと同じ考え方だ」と書いています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/>）。実際に調べると、Agentic Vision（画像・Gemini 3 Flash向け）は2026年1月27日の発表で、コード実行を使って画像を拡大・注釈することで、精度が最大10%上がると説明されています（出典: <https://blog.google/innovation-and-ai/technology/developers-tools/agentic-vision-gemini-3-flash/>）。<mark>動画向けの発表は、そこから217日後でした</mark>（この記事の計算）。「一気に読む」から「必要な所だけ探す」への切り替えは、Googleの中で画像→動画という順番で広がっているのが分かります。

さらに、この記事を書いた時点（2026年9月3日）でGemini APIドキュメントを確認すると、<mark>対応モデルの一覧に発表時には無かったGemini 3.8 Flashも加わっていました</mark>（出典: <https://ai.google.dev/gemini-api/docs/video-understanding>）。3.8 Flash自体の発表は9月2日で、この記事とは別件です。追加された正確な日付はドキュメントに書かれていません。

## 他社の最上位モデルとの比較

**動画ファイルそのものを直接読み込ませる機能**が、AnthropicとOpenAIの公式ドキュメントにあるかを確かめました。

<figure class="figure">
<img src="/static/images/agentic-video-modality.svg" alt="動画ファイルを直接読み込めるかを3社で比べた表。Geminiは動画ファイルの直接入力ができる、動画の中を動的に探索する機能もある。Claude・GPTはどちらも公式ページに動画の記載がなく、動的に探索する機能もない。「記載なし」は機能が無いと明言されているわけではなく、公式ページに書かれていないという意味。Geminiの話はGemini 3.7 Flash・3.6 Flash・3.5 Flash-Lite（後日3.8 Flashも追加）についてで、Claude・GPTにも画像・音声を扱う機能はあるが、動画ファイルそのものを読み込む形式ではない。">
<figcaption>Claude・GPTのページに、動画という言葉自体が出てきません</figcaption>
</figure>

Anthropicのモデル一覧ページには「現行モデルはすべて、文章と画像の入力・文章の出力・多言語・vision・ツール使用に対応する」と書かれていて、<mark class="warn">動画という言葉は一度も出てきません</mark>（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。OpenAIのモデル一覧ページも同様で、「最新のOpenAIモデルはすべて、文章と画像の入力・文章出力・多言語・visionに対応する」とだけ書かれています（出典: <https://developers.openai.com/api/docs/models>）。

**「記載なし」は「対応していないと明言されている」という意味ではありません。**公式ページに書かれていないので、この記事では確認できなかったこととして扱っています。ただし、両社とも画像入力の説明はあるのに動画だけ触れていない以上、**動画ファイルを渡して内容を読み取らせる、という使い方は少なくとも前面には出ていない**とは言えそうです。

## どういう人に効くか

**いま動かしてみるといい人**

- 会議の録画・研修動画・監視カメラの映像など、**10分を超える長尺の動画をAIに読ませたい人**。トークンとコストの削減効果はここで最も出ます。
- 動画の中の「あの一瞬」を探したい人。ドキュメントは、コマ送りでは見逃しやすい一瞬の動き（カット点や状態変化）を拾いやすくなると説明しています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/>）。
- Anthropic・OpenAIの最上位モデルで動画そのものを直接扱いたかった人。<mark>少なくとも公式ページを見る限り、その使い方に対応しているのはいまのところGeminiです</mark>。

**急がなくていい人**

- **5分未満の短い動画を、待ち時間を気にしながら処理している人。**エージェント型は探索のぶん最初の応答が遅くなることがあると明記されています。静的処理のままのほうが向いています。
- コマ単位の正確さがどうしても必要な人。ドキュメントは「クリップ全体でフレーム単位の精度が要る場合は静的処理」と勧めています（出典: <https://ai.google.dev/gemini-api/docs/video-understanding>）。
- 単価の安さで選びたい人。<mark class="warn">この機能自体は無料ですが、Gemini 3.7 Flash・3.6 Flashの単価は2026年12月31日を境に2倍になります</mark>（出典: <https://ai.google.dev/gemini-api/docs/pricing>）。

**この記事で分からないこと**

日本語の動画での精度、実際に処理してみたときの体感速度、Gemini appやYouTubeの「Ask YouTube」機能への展開時期。発表ページには「まもなくGeminiアプリのFlash・Flash-Liteモデルに展開する」「今後数ヶ月でYouTubeのAsk YouTube機能にも使われる」と書かれていますが、時期はどちらも明言されていません。運営者も試していないので書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. エージェント型の動画理解の発表（Google・2026年9月1日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-agentic-video-in-gemini/>
   （Google DeepMind側の <https://deepmind.google/blog/introducing-agentic-video-in-gemini/> を開くと、このページへ転送されます）
2. 動画理解のガイド（Google Gemini API公式ドキュメント）: <https://ai.google.dev/gemini-api/docs/video-understanding>
3. Gemini APIの料金（Google公式）: <https://ai.google.dev/gemini-api/docs/pricing>
4. Agentic Visionの発表（Google・2026年1月27日）: <https://blog.google/innovation-and-ai/technology/developers-tools/agentic-vision-gemini-3-flash/>
5. モデル一覧と仕様（Anthropic公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>
6. モデル一覧（OpenAI公式ドキュメント）: <https://developers.openai.com/api/docs/models>

なお、Googleの開発者ガイド（`ai.dev/learn/agentic-video-understanding-with-gemini`）は、この記事を書いた環境からは到達できませんでした（許可リストに無いホストという理由で、先方のブロックではありません）。この記事で使った数字は、すべて上記6件の到達できたページから確認しています。

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
