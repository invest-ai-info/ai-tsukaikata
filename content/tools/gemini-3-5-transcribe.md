---
title: 85言語を自動で聞き分ける——会議は4人からが試験扱い
description: 2026年8月26日にGoogleが発表した文字起こしモデル「Gemini 3.5 Transcribe」について、発表ページと料金ページに書かれている数字だけを並べました。話者の聞き分けは3人までが正式対応で、それを超えると試験的な扱いになると明記されています。OpenAIの文字起こしモデルとの単価も並べています。
category: tools
scene: choose
published: 2026-09-05
checked: 2026-09-05
tags: [Gemini, 文字起こし, 料金, AI最新情報]
---

## 何が変わったか

Google は 2026年8月26日、新しい文字起こし専用モデル **Gemini 3.5 Transcribe**（事前録音向け）と **Gemini 3.5 Transcribe Live**（配信・リアルタイム向け）を発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5-transcribe/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- **85言語以上を自動で判定し、方言や訛りにも対応する**とGoogleは説明しています（出典: 同上）。
- 話し合いの録音では、<mark>最大3人までの話者に、タイムスタンプ付きで正確に発言を割り当てられます</mark>。3人を超える話者への対応は試験的だと明記されています（出典: 同上）。
- 前の文字起こしモデル「Chirp 3」と比べて、**最終的な文字起こしが出るまでの時間が70%短くなった**とGoogleは説明しています（出典: 同上）。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**公式ページと料金ページに書かれていることを読んで整理したものです。「速かった」「聞き取りやすかった」といった使用感は一切書いていません。

## 前のモデルとの違い（Chirp 3 との比較）

### 読み方が2つに分かれている

発表ページによると、用途に応じて2つのモデルが用意されています（出典: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5-transcribe/>）。

| モデルID | 用途 |
|---|---|
| `gemini-3.5-transcribe` | 録音済みの音声ファイルを文字にする |
| `gemini-3.5-transcribe-live` | 配信中の音声をリアルタイムで文字にする |

出典: 同上

さらに、自己修正（言い直しの処理）・フィラー語（「えー」「あの」など）の自動除去・整形・カスタム語彙の認識・関数呼び出しによる作業の委譲ができるとGoogleは説明しています（出典: 同上）。

### 誤り率（WER）は、測り方によって2つの数字がある

発表ページには、精度を示す数字が2種類、別々の文脈で載っています。**この2つを混ぜて「これが精度です」と1つにまとめることはできません。**

<figure class="figure">
<img src="/static/images/transcribe-wer-by-benchmark.svg" alt="Gemini 3.5 Transcribeの誤り率（WER）を、測り方が違う2組で比べた横棒グラフ。公式発表の全体平均はストリーミング4.0%、非ストリーミング2.6%。FLEURSベンチマーク（上位言語のみ）はストリーミング5.50%、非ストリーミング5.04%。低いほど正確。2組は測り方が違うため単純に比較できず、Google自身も合算していない。前の転写モデルChirp 3の同じ数値は発表ページに書かれておらず比較できない。「最終的な文字起こしまでの時間はChirp 3比70%改善」という発表もあるが、この図の数字とは別の指標。">
<figcaption>「精度」を1つの数字で語れない理由</figcaption>
</figure>

発表ページ本文には「平均のWord Error Rate（誤り率）は、ストリーミングで4.0%、非ストリーミングで2.6%」と書かれています（出典: 同上）。いっぽう、<mark class="warn">別の箇所では「FLEURSベンチマーク（主要言語・地域のみ）ではストリーミングで5.50%、非ストリーミングで5.04%」という、それより高い誤り率も載っています</mark>（出典: 同上）。どちらも同じモデルの公式発表値ですが、測定条件（対象言語や集計方法）が違うため、**この記事ではどちらか一方だけを「精度」として採用することはしません。**

**前のモデル「Chirp 3」の同じ条件でのWER数値は、この発表ページには書かれていません。**そのため、誤り率そのものがどれだけ改善したかは確認できません。確認できるのは「最終的な文字起こしが出るまでの時間が70%短くなった」という、精度とは別の指標だけです（出典: 同上）。

### 提供場所

発表ページによると、開発者向けには Gemini API（Google AI Studio 経由）と Gemini Enterprise Agent Platform で公開プレビュー版として利用できます（出典: 同上）。一般ユーザー向けには、macOS の Gemini アプリ（英語）と、Android の一部の国・言語向け機能ですでに使われており、Chrome への展開は近日予定と書かれています（出典: 同上）。<mark class="warn">Gemini Enterprise for Customer Experience への提供は「近日予定」で、まだ始まっていません</mark>（出典: 同上）。

## 料金

発表ページ自体には料金の記載がありません。**料金は Gemini API の料金ページで別途確認しました。**

| | 入力（音声） | 出力（文字） |
|---|---|---|
| Gemini 3.5 Transcribe | $2.00／100万トークン、または推定 $0.003／分 | $12.00／100万トークン、または推定 $0.002／分 |
| Gemini 3.5 Transcribe Live | $3.50／100万トークン、または推定 $0.005／分 | $21.00／100万トークン、または推定 $0.004／分 |

出典: すべて <https://ai.google.dev/gemini-api/docs/pricing>（無料枠あり。上記は有料枠の値。分あたりの値は「音声入力は秒25トークン、テキスト出力は分175トークン」という前提での推定と注記されている）

料金ページはさらに、この前提をもとにした「実質の分あたり単価」も示しています。**Gemini 3.5 Transcribe は約 $0.005／分、Gemini 3.5 Transcribe Live は約 $0.009／分**です（出典: 同上）。<mark>配信向けにすると、事前録音向けよりも単価が約1.8倍になります</mark>（この記事の計算）。

## 他社の最上位モデルとの比較

**同じ「音声を文字にする」機能**を、OpenAI と Anthropic の公式ページで確認しました。

<figure class="figure">
<img src="/static/images/transcribe-vendor-grid.svg" alt="文字起こし機能を3社で比べた表。文字起こし専用モデル＝Geminiはあり（2機種）、GPTはあり（4機種＋Whisper）、Claudeは記載なし。対応言語数＝Geminiは85言語以上、GPTは記載なし、Claudeは—。話者分離＝Geminiは最大3人（3人超は試験的）、GPTはdiarize版のみ対応で上限は記載なし、Claudeは—。「記載なし」「—」は機能が無いと明言されているのではなく、公式ページに書かれていない意味。">
<figcaption>「音声を文字にする」専用モデルを持たないのはAnthropicだけ</figcaption>
</figure>

OpenAI の公式ドキュメントには、文字起こし専用のモデルが複数載っています（出典: <https://developers.openai.com/api/docs/models>）。話者分離ができると明記されているのは **GPT-4o Transcribe Diarize** で、説明文は「Transcription + diarization」です（出典: 同上）。ただし<mark class="warn">話者分離の上限人数は、モデルページを確認した範囲では書かれていません</mark>（出典: <https://developers.openai.com/api/docs/models/gpt-4o-transcribe-diarize>）。対応言語数も、確認した範囲では明記されていませんでした。

Anthropic のモデル一覧ページには「現行モデルはすべて、文章と画像の入力・文章の出力・多言語・vision・ツール使用に対応する」と書かれていて、<mark class="warn">音声（audio）や文字起こし（transcription）という言葉は一度も出てきません</mark>（出典: <https://platform.claude.com/docs/en/about-claude/models/overview>）。**「記載なし」は「対応していないと明言されている」という意味ではありません。**公式ページに書かれていないので、この記事では確認できなかったこととして扱っています。

### 単価も並べる

<figure class="figure">
<img src="/static/images/transcribe-price-per-min.svg" alt="文字起こしモデル8種の推定分単価を比べた横棒グラフ。ドルの分あたり。事前録音向けは、Gemini 3.5 Transcribeが0.005ドル、GPT-Transcribeが0.0045ドル、GPT-4o Transcribeが0.006ドル、GPT-4o Transcribe Diarize（話者分離つき）が0.006ドル、GPT-4o mini Transcribeが0.003ドル。配信向けは、Gemini 3.5 Transcribe Liveが0.009ドル、GPT-Live-Transcribeが0.017ドル、GPT-Realtime-Whisperが0.017ドル。配信に切り替えると単価は上がるが、上がり幅はGeminiが約1.8倍、OpenAIの2モデルは事前録音の最安値からおよそ3倍と、OpenAI側で上がり幅が大きい。いずれも各社の公式料金ページに載っている「推定・分あたり」の値をそのまま使ったもので、実際の課金はトークン数で決まる。Anthropicは文字起こし専用のモデルを公式ページに載せていない。">
<figcaption>事前録音は僅差、配信はGoogleのほうが安い</figcaption>
</figure>

OpenAI の料金ページにも、Google と同じように「Estimated（推定）」と明記した分あたりの単価が載っています（出典: <https://developers.openai.com/api/docs/pricing>）。生の行はこうなっています。

| モデル | 入力（音声） | 出力（文字） | 推定（分あたり） |
|---|---|---|---|
| GPT-Transcribe（事前録音向け） | 記載なし | 記載なし | $0.0045 |
| GPT-4o Transcribe | $2.50／100万トークン | $10.00／100万トークン | $0.006 |
| GPT-4o Transcribe Diarize | $2.50／100万トークン | $10.00／100万トークン | $0.006 |
| GPT-4o mini Transcribe | $1.25／100万トークン | $5.00／100万トークン | $0.003 |
| GPT-Live-Transcribe（配信） | 記載なし | 記載なし | $0.017 |
| GPT-Realtime-Whisper（配信） | 記載なし | 記載なし | $0.017 |

出典: すべて <https://developers.openai.com/api/docs/pricing>

**事前録音どうしを比べると、いちばん安いのは OpenAI の GPT-Transcribe（$0.0045／分）で、Gemini 3.5 Transcribe（$0.005／分）とほぼ同じ水準です。**いっぽう<mark>配信に切り替えると差が開きます。Gemini は事前録音の約1.8倍（$0.009／分）で済むのに対し、OpenAI の配信2モデルはどちらも $0.017／分で、事前録音の最安値の3倍以上になります</mark>（この記事の計算）。

## どういう人に効くか

**いま動かしてみるといい人**

- 2〜3人の打ち合わせや面談の録音を文字にしたい人。<mark>話者分離は3人までが公式の対応範囲です</mark>。
- 配信・ライブ配信のリアルタイム字幕を試したい人。$0.009／分という推定単価は、同じ配信用途のOpenAIモデル（$0.017／分）より安く出ています。
- 85言語のどれかで話される音声を扱う人。個別の言語名の一覧は無いものの、自動判定に対応すると明記されています。

**急がなくていい人**

- **4人以上が同時に話す会議の録音を文字にしたい人。**3人を超える話者への対応は試験的だと公式に明記されています。安定した結果を求めるなら、今は3人以下の場面に絞ったほうが無難です。
- 「精度」を一言で知りたい人。公式発表には測定条件の違う2種類のWER数値があり、どちらか一方だけを正解として選べません。
- 日本語での話者分離の精度を今すぐ知りたい人。対応言語は85言語以上とだけ書かれており、言語別の精度は公表されていません。

**この記事で分からないこと**

日本語での実際の聞き取り精度、専門用語やなまりへの実際の強さ、Chrome や Gemini Enterprise for Customer Experience への提供時期（発表ページには「近日予定」とだけ書かれています）。運営者も試していないので、体感としては書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. Gemini 3.5 Transcribe の発表（Google・2026年8月26日）: <https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5-transcribe/>
   （Google DeepMind 側の <https://deepmind.google/blog/intelligent-transcription-with-gemini-3-5-transcribe/> を開くと、このページへ転送されます）
2. Gemini API の料金（Google 公式）: <https://ai.google.dev/gemini-api/docs/pricing>
3. モデル一覧（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models>
4. GPT-4o Transcribe Diarize のモデルページ（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/models/gpt-4o-transcribe-diarize>
5. API の料金（OpenAI 公式ドキュメント）: <https://developers.openai.com/api/docs/pricing>
6. モデル一覧と仕様（Anthropic 公式ドキュメント）: <https://platform.claude.com/docs/en/about-claude/models/overview>

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
