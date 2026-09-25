# 深掘り記事の待ち行列

要約を読んで「もっと詳しく知りたい」と思ったものの**URLを1行足す**だけ。
ルーティン（`ai-tsukaikata-deepdive`）が拾って、出典を実際に読んでから記事を書く。

ファイル名が `_` で始まるのでビルド対象外。サイトには出ない。

## 書き方

`- [ ] https://...` の形で足す。処理が終わったら routine が `- [x]` に変えて、
下に生成した下書きのファイル名を書く。**消さない**（同じものを二度書かないため）。

スマホからでも足せる: GitHub でこのファイルを開く → 鉛筆アイコン → 行を足す → Commit changes。

🆕 **記事の構成は「結論が先、理由が後」**（2026-09-23 オーナー指示）＝題は「場面＋すること＋結果」、
最初の h2 は「結論」（読者の使い方ごとに やること → どうなるか を表で）、次に「なぜそうなるのか」。
決まりの本体は `_recipe_queue.md` の「✍️ 文章の書き方」。実例＝`content/tools/claude-opus-5-5.md`。

📦 `- →保管:` の行は、機械回転（毎日04:43 の rotate.yml）が済んだ項目の詳細を保管庫 `_*_archive.md` へ移した印。**行は重複防止の台帳なので消さない・読み直す必要もない。**

## 再試行の決まり（2026-09-14・オーナー承認）

未処理（`- [ ]`）が0件の朝だけ、`- [!]` を**1件**再試行する。選び方:

1. 停止理由に**経路遮断**（`CONNECT tunnel failed` / `EGRESS_BLOCKED` / 許可リスト）が書かれている行だけ。
   **先方の bot 判定**（`cf-mitigated: challenge` の403）だけの行は対象外
   🆕 **判定は行の印で決める**（2026-09-22）＝再試行しないと決めた行には、担当が
   `  - 🛑 再試行対象外（理由）` を**マーカー行のすぐ下**に書く。印の付いた行は翌朝の回転が
   調査記録を保管庫へ移し、この印だけを索引行として残す（本文の語句で判定しない＝実測で、
   bot判定の行にも「許可リスト」の語が出てくるし、読めたのに型が合わない行もあった）
2. **いちばん新しい行から**（下から上へ）。古い行ほど直っている見込みが低い
3. **同じ行は再試行3回まで。**3回目も変わらなければ、その行に `🔁 打ち止め（日付・回数）` と書いて、以後は対象にしない
4. 打ち止めの行を再び試すのは、**オーナーが「許可リストに足した」とその行に書き足した日だけ**（1回）

⚠️ 記録は短く。「変わらず」の再試行は**2行まで**（日付・回数・叩いた先と結果）。表を毎回貼り直さない
（Admin plugin の行は再試行6回で60行を超え、このファイルが予算600行を超えた）。

🔑 **なぜ変えたか**＝「上から1件」だと、直る見込みの無い古い行（openai.com 本体＝bot判定）が毎朝の枠を
取り続け、直る見込みのある新しい行（sakana.ai＝許可リスト）が一度も試されなかった（9/8〜9/13 で6回）。

## 待ち行列

- [x] https://deepmind.google/blog/introducing-gemini-3-6-flash-3-5-flash-lite-and-3-5-flash-cyber/
  - →保管: **2026-08-05: 下書きを作成**（content/_draft-gemini-3-6-flash.md・図4

- [!] https://openai.com/index/continuous-voice-interaction-with-gpt-live/
  - →保管: 🛑 再試行対象外（先方のbot判定・`cf-mitigated` の403。何度やっても同じ）

- [x] https://openrouter.ai/qwen/qwen3.8-max
  - →保管: **2026-08-20 2回目（再試行）: 公開した** → `content/tools/qwen3-8-max.m

- [x] https://www.anthropic.com/news/claude-opus-5
  - →保管: 2026-08-04 1回目: `Host not in allowlist: www.anthropic.com` の

- [!] https://openai.com/index/accelerating-defenders-with-gpt-daybreak-legacy
  - →保管: 🛑 再試行対象外（先方のbot判定・`cf-mitigated` の403。何度やっても同じ）

- [x] https://openai.com/index/daybreak-models-are-now-available-on-aws
  - →保管: ✅ **2026-08-21 2回目（再試行）: 公開した** → `content/tools/daybreak-on

- [x] https://deepmind.google/blog/introducing-gemini-3-7-flash/
  - →保管: 2026-08-13 自動追記（major・Google DeepMind「Introducing Gemini 3.7

- [x] https://tech.preferred.jp/ja/blog/introducing-matlantis-pfp-v9/
  - →保管: 2026-08-17 自動追記（major・Preferred Networks「PFP v9のご紹介: MLIP Ar

- [!] https://openai.com/index/chatgpt-for-teens
  - →保管: 🛑 再試行対象外（先方のbot判定・`cf-mitigated` の403。何度やっても同じ）

- [!] https://openai.com/index/introducing-ai-futures
  - →保管: 🛑 再試行対象外（先方のbot判定・`cf-mitigated` の403。何度やっても同じ）

- [!] https://openai.com/index/introducing-admin-plugin
  - →保管: 🛑 再試行対象外（先方のbot判定・`cf-mitigated` の403。何度やっても同じ）

- [!] https://openai.com/index/introducing-intelligence-age
  - →保管: 🛑 再試行対象外（先方のbot判定・`cf-mitigated` の403。何度やっても同じ）

### 🆕 2026-08-31 の補充（枠の詰まりを外すため・手動追記）

**なぜ足したか＝キューの未処理が0件で、保留6件が全部 `openai.com`（先方のbot判定・再試行の対象外）
だったから。**この状態だと毎朝のルーティンは手順1で「未処理なし」を見て38秒で帰る。実際
`content/tools/` の自動公開は **2026-08-21 の `daybreak-on-bedrock` が最後**（10日間ゼロ）。

🔑 **枠の取り合いが原因だった。**自動追記は1日3件までで、8/18・8/20×2・8/25・8/26 の
**5回連続が全部 `openai.com`**（発表語「Introducing …」にいちばんよく当たるため）。
読める会社のお知らせが来ても、枠が空いていない日があった。
→ `tracker/deepdive.py` に `UNREADABLE_HOSTS` を足し、**読めないと実測済みのホストには枠を取らせない**
ようにした（2026-08-31）。⚠️ 載せるのは**先方のbot判定**だけ。経路遮断は載せない（許可リストで直るので、
直った日に自動で戻ってほしい）。⚠️ サブドメインは含めない（`developers.openai.com` は200を実測済み）。

⚠️ **下の3件の到達性は、私の手元のPCで測った値。**クラウド側の結果は別（CLAUDE.md 2026-08-05 の実例）。
**この行に当たる担当は、自分の環境で測り直してから進めること。**

- [x] https://deepmind.google/blog/introducing-computer-use-in-gemini-3-5-flash/
  - →保管: ✅ **2026-08-31 1回目: 公開した** → `content/tools/gemini-computer-
- [x] https://www.anthropic.com/news/introducing-claude-tag
  - →保管: ✅ **2026-09-01 1回目: 公開した** → `content/tools/claude-tag-slack
- [x] https://www.anthropic.com/news/reflect-with-claude
  - →保管: ✅ **2026-09-02: 公開した** → `content/tools/reflect-with-claude.

📌 **同じ条件（読めるホスト・major のお知らせ・未処理）で残っている候補**——枠が空いたらここから足す。
`news.json` を `importance=major` かつ お知らせ系ソースで絞れば同じ一覧が出る:
`www.anthropic.com`＝Claude Sonnet 5(6/30)・Claude for Teachers(7/14)／
`deepmind.google`＝Gemma 4 12B(6/9)・Gemini Robotics ER 2(7/30)・Lyria 3.5(7/29)／
`tech.preferred.jp`＝PLaMo 3.0 Prime(6/22。⚠️ 301で `www.preferred.jp` へ飛ぶ・手元で最終200)。
⚠️ **古い告知でも構わない**（`tools/` は速報ではなく「このツールは何ができるか」の調べ物）。
ただし**記事に `checked` の日付を必ず入れる**こと。

- [x] https://deepmind.google/blog/introducing-agentic-video-in-gemini/
  - →保管: ✅ **2026-09-03: 公開した** → `content/tools/gemini-agentic-video

### 🆕 2026-09-05 の補充（オーナー指示「ChatGPT-6・アストラの深掘り」・手動追記）

**「ChatGPT-6」「アストラ」は同じもの＝OpenAI の GPT-6 Astra**（API 名 `gpt-6-astra`）。
2026-09-03 にプレビュー、9/5 に一般公開。⚠️ `news.json` には 9/1 の `path-to-astra` など
6件が入っているが、**自動追記の対象にならない**＝`deepdive.py` の `UNREADABLE_HOSTS` に
`openai.com` が入っているため（意図どおり。下の実測のとおり本当に読めない）。

🚨 **openai.com の記事ページは、手元からも読めない**（2026-09-05 実測）。
`openai.com/index/path-to-astra` は `Cf-Mitigated: challenge` 付きの **403**。
`help.openai.com` も 403。**先方の bot 判定なので許可リストでは直らない。UA偽装での迂回はしない。**

⭕️ **CLAUDE.md の振替ルートは、実測で両方とも生きている**:

| URL | 結果（2026-09-05 手元） |
|---|---|
| `openai.com/news/rss.xml` | **200**・約711KB（発表の公式要旨が入る。全文は入らない） |
| `developers.openai.com/api/docs/models` | **200**・約364KB |
| `developers.openai.com/api/docs/pricing` | **200**・約558KB |
| `developers.openai.com/api/docs/guides/latest-model` | **200**・約382KB（「Using GPT-6 Astra」） |
| `platform.openai.com/docs/models` | 301 → `developers.openai.com/api/docs/models` |

- [x] https://developers.openai.com/api/docs/guides/latest-model
  - →保管: ✅ **2026-09-05: 公開した**（オーナーのローカルセッションで作成） → `content/tools/g

### 🆕 2026-09-02 の補充（オーナー指示「ニュースの方からも深掘り」・手動追記）

**なぜ足したか＝オーナーが例に挙げた2件（Fable 5.1・Gemini の新モデル）のうち、Fable 5.1 は
トラッカーに入っておらず、Gemini の2件は `minor` 判定で自動追記の対象外だったから。**

🚨 **Fable 5.1 の発表ページは `news.json` に入っていない。**理由＝URLが `/news/` の下ではなく
`www.anthropic.com/claude-fable-and-mythos-5-1` で、RSC ペイロード上の型が `featuredGridLink`
（`date`/`url` を持つ）。`parse_anthropic_news` が拾うのは `publishedOn`+`slug` を持つ
`post` だけなので、**この形の「目玉発表」は構造的に落ちる**（2026-09-02 実測・1件だけ出現）。
トラッカー側の直しは別件（記事の作業では触らない）。

- [x] https://www.anthropic.com/claude-fable-and-mythos-5-1
  - →保管: ✅ **2026-09-02: 公開した**（オーナーのローカルセッションで作成） → `content/tools/c
- [x] https://deepmind.google/blog/gemini-omni-1-1-flash-lets-you-build-with-more-control/
  - →保管: ✅ **2026-09-04: 公開した** → `content/tools/gemini-omni-1-1-flas
- [x] https://deepmind.google/blog/intelligent-transcription-with-gemini-3-5-transcribe/
  - →保管: ✅ **2026-09-05: 公開した** → `content/tools/gemini-3-5-transcrib

- [x] https://deepmind.google/blog/introducing-gemini-3-8-flash-and-38-flash-cyber/
  - →保管: ✅ **2026-09-06: 公開した** → `content/tools/gemini-3-8-flash.md`

- [x] https://deepmind.google/blog/introducing-weathernext-3-our-most-advanced-and-accurate-global-weather-ai-model/
  - →保管: ✅ **2026-09-07: 公開した** → `content/tools/weathernext-3.md`

- [x] /fugu-max-release/
  - →保管: ✅ **2026-09-14 2回目（再試行）: 公開した** → `content/tools/sakana-fugu

- [x] https://deepmind.google/blog/introducing-gemini-3-8-live-and-3-8-live-extended-thinking/
  - →保管: ✅ **2026-09-15: 公開した** → `content/tools/gemini-3-8-live.md`

- [x] https://sakana.ai/chat-fugumax/
  - →保管: ✅ **2026-09-16: 公開した** → `content/tools/sakana-chat-memory.m

- [x] https://www.anthropic.com/news/life-sciences-verification-program
  - →保管: ✅ **2026-09-17: 公開した** → `content/tools/claude-life-sciences

- [!] https://sakana.ai/frontier-intelligence-group/
  - 2026-09-18 自動追記（major・Sakana AI「Introducing Sakana AI’s Frontier Intelligence Group (FIG)」）
  - **2026-09-18 1回目: 記事を書かずに停止した。**理由は「読めない」ではなく「このサイトの型に当てはまらない」。

    **① ページ自体は問題なく読めた（`sakana.ai` は200・36,837バイト、日英併記の全文を取得済み）**

    - 経路遮断でもbot判定でもない。本文（英語版・日本語版とも）を最後まで取得できている。

    **② 🆕 中身が「研究チームの発足・採用告知」で、モデルでも料金でも製品機能でもない**

    - FIG（Frontier Intelligence Group）は社内の研究者コミュニティの紹介。主旨＝「知能はまだ解決していない、
      Transformer一辺倒でないパラダイムを探す」という研究哲学と、5つの研究事例（Continuous Thought
      Machines・Augmented Lagrangian Predictive Coding・NVIDIAとのスパースTransformer共同研究・
      AI Picbreeder実験・Smart Cellular Bricks）の紹介。締めは「興味があれば Sakana AI に応募してほしい」
      という採用告知
    - 出典ページに出てくる数字（例＝フィードフォワード層のニューロンの95%以上が非活性・最大1,000層・
      物理ブロック約200個・ICML 2026採択・Nature Communications掲載）は、いずれも**単一の研究成果を
      説明する文脈の数字**で、料金でも性能ベンチマークでもなく、他社の公式ページと突き合わせて
      比較できる性質のものではない
    - 比較相手（他社の同種の「基礎研究チーム」発表）も無く、読者（自動化したい非エンジニアの会社員）が
      「どういう人に効くか」を判断できる要素が無い。プロダクトでもモデルでもないため、
      このサイトの記事の型（何が変わったか／前のモデルとの違い／他社との比較）に当てはまらない
    - 💡 **これは 2026-08-20 の「AI Futures」（OpenAIの新ブログ立ち上げ告知）とほぼ同じ構造**
      （①は解けている点が違うが、②＝数字はあっても比較できない・プロダクトではない、という
      停止理由は同一）。「AI Futures」はオーナーが独立検証のうえ 2026-08-21 に見送りで確定させた前例がある。
    - 💡 **次にこの行を見る人へ**＝担当の判断だけで `- [x]`（見送り確定）にはしない。
      オーナーに一言確認を仰いでから確定させるのが、AI Futuresのときの前例に合わせたやり方。
    - 2026-09-20: オーナー指示「二件とも進めて」は材料の補充（下の節）であって、この行の見送り確定ではない。
      技術的な遮断ではないので再試行の対象外のまま＝オーナー確認待ちを継続

### 🆕 2026-09-20 の補充（材料切れ・オーナー指示「二件とも進めて」・手動追記）

**なぜ足したか＝未処理が0件で、保留は `openai.com` の bot 判定6件＋FIG 1件（オーナー確認待ち）。
`news.json` には 9/18 以降「読めるホストの major お知らせ」が無く、自動追記は構造的に止まっていた**
（`tools/` の自動公開は 9/17 の `claude-life-sciences-verification` が最後）。

- `openai.com` 本体に枠を取らせない `UNREADABLE_HOSTS` は正しい。ただし CLAUDE.md の
  「OpenAI は出典を振り替える」（① `openai.com/news/rss.xml` ② `developers.openai.com`）が使える発表は、
  **手で足せば書ける**。下の2件は developers.openai.com 側に料金と仕様の表があることを手元で確かめた
- ⚠️ 到達性は**手元のPC（2026-09-20）で測った値**。クラウド側は担当が測り直すこと（CLAUDE.md 2026-08-05）

- [x] https://openai.com/index/introducing-chatgpt-images-2-5
  - →保管: ✅ **2026-09-20: 公開した** → `content/tools/chatgpt-images-2-5.m
- [x] https://openai.com/index/introducing-gpt-live-1-in-the-api
  - →保管: ✅ **2026-09-21: 公開した** → `content/tools/gpt-live-1-api.md`
- [x] https://sakana.ai/marlin-update/
  - →保管: ✅ **2026-09-22: 公開した** → `content/tools/sakana-marlin-interactive-reading.md`

- [x] https://www.anthropic.com/claude-opus-5-5
  - →保管: 2026-09-22 自動追記（major・Anthropic「Introducing Claude Opus 5.5」

- [x] https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory/
  - →保管: 2026-09-23 自動追記（minor・Google DeepMind「Advancing Private AI C

- [x] https://deepmind.google/blog/say-hello-to-gemini-38-text-to-speech/
  - →保管: ✅ **2026-09-24: 公開した** → `content/tools/gemini-3-8-tts.md`

- [x] https://deepmind.google/blog/introducing-gemini-38-live-with-live-avatar/
  - →保管: ✅ **2026-09-25: 公開した** → `content/tools/gemini-3-8-live-avatar.md`

## 処理済み

- https://deepmind.google/blog/introducing-gemini-38-live-with-live-avatar/ → **公開済み** content/tools/gemini-3-8-live-avatar.md（2026-09-25・公開）
  - 302転送で `blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-live-with-live-avatar/` へ到達（200）。
    発表本体に加え、Google Cloud公式ブログの一般提供（GA）記事・Agent Platform料金ページ・モデルカードを読んで数字を取った。
    図3枚（`gemini38avatar-output-price` / `gemini38avatar-output-budget` / `gemini38avatar-vendor-grid`）。
    `check_numbers.py` は照合対象7個のうち**7個すべて出典に存在**（出典9件すべて取得成功）。
    pytest 736 passed・build 230ファイル。`check_readability.py` は60字以上11%（目安15%以下、最長115字）。
  - 📌 記事の芯＝**Gemini 3.8 Live（音声のみ・9/15発表）に動画出力を追加した新機能で、
    使えるのはGemini Enterpriseだけ**（通常のGemini API・AI Studio・Gemini アプリでは使えない）。
    動画を足すと出力トークン上限が64,000→24,000に62.5%減る（モデルカードの2数字からこの記事が計算）。
    連続対話は「数分程度」とモデルカードの既知の制限に明記（具体的な分数は非公表）。
  - 🔍 **料金表の中で、動画（アバター）出力が最安だった**（$1.00／百万トークン。テキスト出力$4.50・
    音声出力$12.00より安い）。この行はGemini Enterprise向けの`cloud.google.com`料金ページにのみ存在し、
    開発者向け`ai.google.dev`の料金ページには無いことを実際に確認した（Enterprise限定の裏付け）。
  - ⚠️ 他社比較はOpenAI（`developers.openai.com`のモデル一覧・料金ページ）とAnthropic
    （`platform.claude.com`のモデル一覧）で確認できた。OpenAIのリアルタイム音声モデル（GPT-Live 1ほか）は
    音声・テキスト・画像のみで動画出力の記載なし。Anthropicはモデル一覧に「text and image input, text
    output」とだけあり、音声・動画への言及自体が無くリアルタイム音声AI製品自体が存在しないことを確認した。

- https://deepmind.google/blog/say-hello-to-gemini-38-text-to-speech/ → **公開済み** content/tools/gemini-3-8-tts.md（2026-09-24・公開）
  - 302転送で `blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-8-text-to-speech/` へ到達（200）。
    図3枚（`gemini38tts-price-old-vs-new` / `gemini38tts-price-doubles` / `gemini38tts-vendor-grid`）。
    `check_numbers.py` は照合対象12個のうち**11個が出典に存在**、残る1個（`55%`）は
    $20.00→$9.00から記事が計算した値で、そう明記してある（出典10件すべて取得成功）。
    pytest 736 passed・build 227ファイル。`check_readability.py` は60字以上9%（目安15%以下、最長70字）。
  - 📌 記事の芯＝**新2モデル（Flash TTS / Flash-Lite TTS）は前世代（3.1 Flash TTS Preview）より
    入力50%・出力55〜70%安いが、2027年1月1日にどちらも2倍に戻る導入価格**。前世代はモデル一覧ページで
    同時に「Legacy」表記になった。声の複製は同意録音を用意すれば申請なしで使えるが、
    AI Studio経由はイリノイ・テキサス・EEA・UK・スイス・インドでは利用できないと発表ページに明記。
  - ⚠️ 他社比較はOpenAI（`developers.openai.com`のモデル・料金・ガイド・custom voicesページ）と
    突き合わせられた。**OpenAIの唯一のTTSモデル（GPT-4o Mini TTS）は最大入力2,000トークン**、
    声の複製は「限定顧客のみ・要営業への問い合わせ」（自己申告制のGeminiと対照的）。
    Anthropicはモデル一覧に audio/speech の言及が無いことを確認。
  - 🔍 **Google自身の2つの公式ページで言語数の書き方が違う**（発表ページ本文「100以上の言語と方言」・
    モデル一覧ページ「Flash TTSは130言語、Flash-Liteは101言語」）。より詳しいモデル一覧側の数字を採用し、
    その旨を本文に明記した。

- https://deepmind.google/blog/advancing-private-ai-compute-with-secure-server-side-memory/ → **公開済み** content/tools/private-ai-compute-memory.md（2026-09-23・公開）
  - `deepmind.google` に到達（200）。関連ページとして初出発表（`blog.google`・2025-11-11）と
    Anthropicの記憶機能のブログ（`claude.com/blog/memory`）にも到達。図3枚
    （`pac-before-after` / `pac-architecture-flow` / `pac-vendor-grid`）。
    `check_numbers.py` は**照合対象0個**（本文に $・% が無い題材。日付や製品名は照合対象外）。
    pytest 736 passed・build 224ファイル。`check_readability.py` は60字以上2%（目安15%以下）。
  - 📌 記事の芯＝**Private AI Compute（2025年11月に発表・当初はステートレスでPixel 10の
    Magic CueとRecorderアプリだけに使用）に、永続的な記憶を追加すると発表**。記憶データは
    クラウド上でも暗号化し、鍵は利用者の端末だけが持つため「Googleも読めない」と説明している。
    ただし対象製品名・提供時期は発表に一切書かれていない（技術的な更新の告知に留まる）
  - ⚠️ 技術文書（PDF・`services.google.com`）は経路遮断で到達できず、独立監査の中身までは
    確認できなかった。次にこのドメインを叩く行が来たら再試行対象にすること
  - ⚠️ 他社比較はAnthropicのClaude記憶機能（2025-09-11提供開始・暗号化方式の記載なし）と
    突き合わせた。OpenAIのChatGPTメモリー機能は`openai.com`・`help.openai.com`とも
    今回もbot判定の403（`cf-mitigated: challenge`実測）で確認できず
- https://www.anthropic.com/claude-opus-5-5 → **公開済み（別セッション作成）** content/tools/claude-opus-5-5.md（2026-09-22・公開）
  - 🔑 **今回のルーティンが手順1で発見した記録漏れ**＝記事は同日中に別セッションが作成・公開済み
    （`768ea67`→構成を「結論が先」に組み替えた`fc68081`）だったが、待ち行列の行が`- [ ]`のまま
    残っていた。中身は確認済み（Opus 5→5.5の費用40%減・4設定がエラーになる件・他社比較）。
    重複執筆はせず、行を`- [x]`に直すだけにとどめた
- https://sakana.ai/marlin-update/ → **公開済み** content/tools/sakana-marlin-interactive-reading.md（2026-09-22・公開）
  - `sakana.ai/marlin-update/` と `sakana.ai/marlin/`（料金）に到達（いずれも200）。図3枚
    （`marlin-run-cost-by-plan` / `marlin-vendor-grid` / `marlin-update-timeline`）。出典6件すべて取得成功。
    `check_numbers.py` は**5個すべて出典に存在**。pytest 736 passed・build 220ファイル。
  - 📌 記事の芯＝**Sakana Marlinの1回あたり実質コストは、月極めプランで使い切れる会社ほど下がる**
    （従量課金¥9,800/回・Pro実質¥7,500/回・Team実質¥6,667/回。プラン別の実質額はページの数字から
    この記事が計算した値）。
  - ⚠️ 他社比較はOpenAI（`developers.openai.com`のDeep researchガイド・料金ページ）とGoogle
    （`gemini.google/overview/deep-research/`・`gemini.google/subscriptions/`）で到達できたが、
    **3社の提供形態そのものが違う**（Marlin=B2B SaaSのクレジット制、OpenAI=開発者向けAPIのトークン課金、
    Google=個人向けサブスクの一機能で無料枠あり）ため1本の表には並べず、比較不能とそのまま明記した。
    OpenAIの公式ガイドは`o3-deep-research`／`o4-mini-deep-research`と明記するが、料金ページには
    この2モデル名の価格行が無く、単価は「公表されていない」と書いた。
  - 📌 `sakana.ai` のminorがそのまま記事になった実例が増えた（`sources.yml`の`sakana-blog`に
    `deepdive_minor: true`を付ける根拠になりうるが、`tracker/`は今回のスコープ外なので触っていない）。
- https://openai.com/index/introducing-gpt-live-1-in-the-api → **公開済み** content/tools/gpt-live-1-api.md（2026-09-21・公開）
  - 発表ページは今回もbot判定の403で読めず、RSS要旨1文＋developers.openai.comのモデル・料金・
    ガイドページで執筆。図3枚（`gptlive1-architecture-grid` / `gptlive1-concurrent-tiers` /
    `gptlive1-vendor-voice-price`）。出典10件すべて取得成功。`check_numbers.py` は**10個すべて出典に存在**。
    pytest 657 passed・build 214ファイル。
  - 📌 記事の芯＝GPT-Live 1は「音声」と「頭脳」を分けた新アーキテクチャで、$0.05/分の音声セッション
    料金にはバックエンドのモデル代が含まれない。電話（SIP）に公式対応、同時セッションはTierで25〜500・
    Freeプラン対象外。他社比較ではGemini 3.8 Liveの分あたり音声単価より、GPT-Live 1のセッション料金
    だけで既に高いことを確認した。
- https://openai.com/index/introducing-chatgpt-images-2-5 → **公開済み** content/tools/chatgpt-images-2-5.md（2026-09-20・公開）
  - 発表ページは今回もbot判定の403で読めず、RSS要旨1文＋developers.openai.comのモデル・料金ページ・
    ガイドで執筆。図3枚（`chatgpt-images25-price-lineage` / `chatgpt-images25-old-vs-new` /
    `chatgpt-images25-vendor-price`）。出典11件すべて取得成功。`check_numbers.py` は**16個すべて出典に存在**。
    pytest 656 passed・build 211ファイル。
  - 📌 記事の芯＝**新モデル（Sunburst/Flare）は画質の選択肢が3→5段階に増え、出力単価も$32→$30に
    下がったが、まとめて半額になる「Batch」処理には対応していない**（両モデルのEndpoints表で
    `v1/batch: Not supported` と確認）。旧モデル（chatgpt-image-latest）のページには「以前ChatGPTで
    使われていたスナップショット」「API利用にはSunburstを推奨」と明記されており、後継関係を確認した。
  - ⚠️ 他社比較はGoogleのNano Banana系3モデル（Lite $30／2 $60／Pro $120）と突き合わせ、新モデルの
    単価はGoogleの下位モデル（Lite）と同額・Google自身の最上位（Pro）の1/4だった。Anthropicはモデル
    一覧・料金ページのどちらにも画像生成モデルの記載が無いことを確認し「提供していない」と明記した。

- https://www.anthropic.com/news/life-sciences-verification-program → **公開済み** content/tools/claude-life-sciences-verification.md（2026-09-17・公開）
  - `www.anthropic.com` に到達。図3枚（`lsvp-grant-types` / `lsvp-monitoring-shift` /
    `lsvp-vendor-grid`）。出典7件すべて取得成功。`check_numbers.py` は**8個すべて出典に存在**。
    pytest 646 passed・build 190ファイル。
  - 📌 記事の芯＝**Standard Use（チーム・年更新）とHigh-risk Use（単一プロジェクト・半年更新）の
    2段構え**で、生命科学関連のブロックを段階的に外す。安全策も「都度リアルタイムでブロック」から
    「30日分をまとめてオフラインで見る」方式に変わった。
  - ⚠️ 他社比較は**OpenAIのGPT-Rosalind**（developers.openai.comのモデル一覧・料金ページで確認）と
    突き合わせられた。**Claude Opus 5とgpt-rosalind-researchは入力$5・出力$25・キャッシュ$0.50で
    単価が完全一致**（両社の公式料金ページで確認）。OpenAI本体の発表ページ（`openai.com/index/...`）は
    今回もbot判定の403で読めず、RSSの要旨1文のみ引用。Googleは`deepmind.google/science/`・
    `cloud.google.com/security/ai/frontier-safety-framework`を確認したが同種の制度の記載なし。

- https://sakana.ai/chat-fugumax/ → **公開済み** content/tools/sakana-chat-memory.md（2026-09-16・公開）
  - `sakana.ai` に到達（200）。図3枚（`sakana-chat-timeline` / `sakana-chat-model-lineup` /
    `sakana-chat-memory-grid`）。出典6件すべて取得成功。`check_numbers.py` は**照合対象0個**
    （本文に $・% が無い題材）。pytest 646 passed・build 187ファイル。
  - 📌 記事の芯＝**Sakana Chatのメモリーは、更新以降の会話しか対象にしない**と発表ページに明記されている。
    Google Gemini（過去チャットの記憶が前提）・Anthropic Claude（初期設定時に過去チャットから生成可）と
    対比すると、3社のうちSakana Chatだけが過去に遡らない設計だった。搭載モデルは2026年9月11日にAPI
    公開されたばかりの Fugu Max に切り替わり（Chatへの搭載はその6日後）、旧モデル「Sakana Fugu」は
    2026年8月に加わってから短い期間で置き換わって消えた。
  - ⚠️ Sakana Chat自体の料金ページ（`chat.sakana.ai`）は経路遮断（`CONNECT tunnel failed`）で到達できず、
    料金は「発表ページに記載なし」のまま。`sakana.ai`（メインドメイン）とは別扱いなので、次にこの
    サブドメインを叩く行が来たら再試行対象にすること。
  - ⚠️ OpenAI（ChatGPT）のメモリー機能は、公式ニュースRSSで見出しと日付だけ確認できたが、本文
    （`openai.com`・`help.openai.com`・`chatgpt.com`）は今回もすべてbot判定の403だった。

- https://deepmind.google/blog/introducing-gemini-3-8-live-and-3-8-live-extended-thinking/ → **公開済み** content/tools/gemini-3-8-live.md（2026-09-15・公開）
  - `deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`gemini38live-benchmarks` /
    `gemini38live-price-same` / `gemini38live-vendor-grid`）。`check_numbers.py` は**16個すべて出典に存在**
    （出典10件すべて取得成功）。pytest 646 passed・build 184ファイル。
  - 📌 記事の芯＝**料金ページでは `gemini-3.1-flash-live-preview`（旧・プレビュー版）と
    `gemini-3.8-live` / `gemini-3.8-live-extended-thinking`（新・正式版）の3モデルIDが
    同じ価格の行にまとめられており、テキスト単価は入力$0.75・出力$4.50で完全に同額**。
    読める量（131,072トークン）・書ける量（65,536トークン）も前世代から変わっていない。
    いちばんの変化は「プレビューが正式版になったこと」と「97言語を会話の途中でも自動で
    切り替える」機能。モデルカードの学習データ締め切りは2026年1月（発表日は2026年9月15日）。
  - ⚠️ モデルカードのFrontier Safety評価は、前の音声モデル（3.1 Flash Live Preview）ではなく
    テキスト系の3.7 Flashを基準にしている（「3.7 Flashと比べて意味のある新しい能力・性能向上は
    無いと判断」と明記）。発表ページの「知性の大幅な向上」という宣伝文句と、この安全性評価の
    前提は一見矛盾するため、両方をそのまま書いた。
  - ⚠️ OpenAIのGPT-Live 1（$0.05/分・セッション課金）とGeminiの音声単価（トークン課金＋分換算併記）は
    課金の仕組み自体が違う（GPT-Live 1は「頭脳」のバックエンドモデルが別料金）ため、
    単純な安い高いの比較はできないと明記し、表を分けた。
  - Artificial Analysis（`artificialanalysis.ai`）は**経路遮断**（`CONNECT tunnel failed, response 403`・
    `cf-mitigated`ヘッダなし）で到達できず、Googleが発表ページで引用したベンチマーク値の
    独立検証はできなかった。次にこのドメインを叩く行が来たら再試行対象にすること。

- https://sakana.ai/fugu-max-release/ → **公開済み** content/tools/sakana-fugu-max.md（2026-09-14・公開）
  - 再試行で通った（1回目は2026-09-11に経路遮断で停止。今回 `sakana.ai` が WebFetch・curl とも200に
    なっているのを確認してから着手）。図4枚（`fugu-max-price-vs-flagships` / `fugu-max-bench-wins` /
    `fugu-ultra-v2-vs-v11` / `fugu-ultra-v2-vendor-grid`）。`check_numbers.py` は**14個すべて出典に存在**
    （出典4件とも取得成功）。pytest 646 passed・build 181ファイル。
  - 📌 記事の芯＝**Fugu Max・Fugu Ultra v2は単独モデルではなく、複数の既存モデルを自動で使い分ける
    「オーケストレーション」**。Fugu Maxの出力単価$6はSakana自身が比較したSonnet 5($10)・
    GPT 5.6 Terra($12)より安いが、この記事で独自にGemini 3.8 Flash($3.75)を突き合わせたところ
    そちらのほうが安かった。Fugu Ultra v2はClaude Opus 5・GPT-6 Astra等と並べた8項目中7項目で
    上位2位だが、ProgramBenchだけ3社に次ぐ4位だった。ベンチマーク比較の数値は発表ページのグラフ画像を
    直接開いて目視で読み取った（要約させずに生の表を見る、の手順どおり）。
  - ⚠️ 他社に同種の「複数モデルを横断オーケストレーション」する製品があるかは未調査のまま
    （時間の都合で見送り）。次にこの題材を掘り下げる人がいれば、そこから始めるとよい。

- https://deepmind.google/blog/introducing-gemini-3-8-flash-and-38-flash-cyber/ → **公開済み** content/tools/gemini-3-8-flash.md（2026-09-06・公開）
  - `deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`gemini38-price-three-gens` /
    `gemini38-safety-delta` / `gemini38-vendor-top-price`）。`check_numbers.py` は**24個中23個が出典に存在**
    （出典8件すべて取得成功）。pytest 625 passed・build 158ファイル。
  - 📌 記事の芯＝**Gemini 3.6・3.7・3.8の3世代とも導入価格がまったく同じ**（入力$0.75・出力$3.75）で、
    2027年1月1日に3世代いっせいに$1.50/$7.50へ上がる。単価だけ見ると3.8が特別安いのではなく、
    「導入期間中は前の世代と同額で出す」運用が3回続いているだけ。
  - ⚠️ 性能の比較表（3.7 Flashとの点数比較）はモデルカードに**画像として埋め込まれており**、
    配信元 `lh3.googleusercontent.com` が**経路遮断**（`CONNECT tunnel failed, response 403`）で
    読めなかった。本文に文章として書かれている数字（HLE-Verified 54.9%・Cyberのベンチマーク数値）と、
    文字で書かれている安全性評価表（3.7 Flashとの差・pp）だけで記事を組み立てた。
    `deepmind.com`（`deepmind.google` とは別ホスト）も経路遮断で読めなかった。
  - ⚠️ Cyber版はモデルカードが404・料金ページにも掲載が無いことを実際にURLを叩いて確認し、
    「Fairwind Program」経由の限定提供（一般には使えない）と記事に明記した。
- https://deepmind.google/blog/intelligent-transcription-with-gemini-3-5-transcribe/ → **公開済み** content/tools/gemini-3-5-transcribe.md（2026-09-05・公開）
  - `deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`transcribe-price-per-min` /
    `transcribe-wer-by-benchmark` / `transcribe-vendor-grid`）。`check_numbers.py` は**21個すべて出典に存在**
    （出典7件すべて取得成功）。pytest 625 passed・build 154ファイル。
  - 📌 記事の芯＝**話者分離は最大3人まで正式対応、それを超えると試験的**と発表ページに明記。
    誤り率（WER）は「全体平均」と「FLEURSベンチマーク（上位言語のみ）」で異なる数字が
    公式発表内に別々に載っており、単一の精度として合成せず両方を併記した。
  - ⚠️ 料金は発表ページになく、`ai.google.dev/gemini-api/docs/pricing` から別途取得した
    （両モデルとも「トークン単価」と「推定・分あたり」の両方が公式に併記されている）。
    配信版は事前録音版よりGeminiで約1.8倍、OpenAIの配信2モデル（GPT-Live-Transcribe・
    GPT-Realtime-Whisper）は事前録音の最安値の3倍以上（いずれもこの記事の計算と明記）。
    Anthropicは文字起こし専用モデルを公式ページに載せていない（音声への言及自体が無い）。
- https://deepmind.google/blog/gemini-omni-1-1-flash-lets-you-build-with-more-control/ → **公開済み** content/tools/gemini-omni-1-1-flash.md（2026-09-04・公開）
  - `deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`omni11-resolution-price` /
    `omni11-vendor-720p-price` / `omni11-scene-extension`）。`check_numbers.py` は**11個すべて出典に存在**
    （出典9件すべて取得成功）。pytest 618 passed・build 149ファイル。
  - ⚠️ 価格表（360p/720p/1080p/4K）は発表ページの本文テキストではなく埋め込み画像。
    画像を`curl`で取得しPNGに変換して目視で確認した（要約させずに生の表を見た）。
  - 📌 記事の芯＝**解像度で秒単価が10倍**（360p $0.03〜4K $0.30）。延長は10秒刻みで合計40秒が上限、
    アップロードした動画の延長はEU・スイス・英国では利用不可。比較したOpenAI Sora 2/Sora 2 Proは
    2026年9月24日にAPI提供終了と告知されており（確認時点で20日後）、Anthropicは動画生成モデルを
    提供していない。
- https://deepmind.google/blog/introducing-agentic-video-in-gemini/ → **公開済み** content/tools/gemini-agentic-video.md（2026-09-03・公開）
  - `deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`agentic-video-gains` /
    `agentic-video-timeline` / `agentic-video-modality`）。`check_numbers.py` は**10個すべて出典に存在**
    （出典7件すべて取得成功。うち1件は転送元URL）。pytest 618 passed・build 146ファイル。
  - 📌 記事の芯＝**静的処理（1FPS一律）に対しエージェント型は必要な部分だけ動的に探索し、
    長尺動画でトークン最大88%減・コスト最大66%減・精度最大7%向上**（Google発表の「最大」値、
    追加料金は無く標準トークン単価のまま）。**ただし短い動画（5分未満）は探索のぶん
    最初の応答が遅くなる**とドキュメントに明記されている。
  - ⚠️ 開発者ガイド（`ai.dev/learn/agentic-video-understanding-with-gemini`）は経路遮断
    （`Host not in allowlist: ai.dev`）。別ホストの `ai.google.dev` が到達できたので、
    数字はそちらと発表ページ・料金ページから取れた。次に `ai.dev` を叩く行が来たら
    ここに記録した経路遮断を再試行対象にすること。
  - 他社比較は Anthropic（`platform.claude.com`）・OpenAI（`developers.openai.com`）とも到達でき、
    どちらのモデル一覧にも「動画」の語が無いことを一次情報で確認できた。
- https://www.anthropic.com/news/reflect-with-claude → **公開済み** content/tools/reflect-with-claude.md（2026-09-02・公開）
  - `www.anthropic.com` に到達できた。図3枚（`reflect-4d-framework` / `reflect-privacy-scope` /
    `reflect-roadmap`）。出典は発表ページ1件のみ。`check_numbers.py` は照合対象0個（本文に $・% が無い題材）。
    pytest 618 passed・build 142ファイル。
  - 📌 記事の芯＝**対象はメモリ機能をオンにしたFree・Pro・Maxのみ**（発表ページにTeam・Enterpriseの
    記載は無い）。「使った時間の表示」「Coworkの振り返り」は本文に "soon" と明記され、まだ来ていない。
  - ⚠️ 他社比較は保留にした。OpenAI（`help.openai.com`）は403（bot判定の可能性が高いがヘッダ未確認）、
    Google（`knowledge.workspace.google.com`）は経路遮断（`CONNECT tunnel failed`）で到達できず。
    `support.claude.com` も経路遮断（Claude Tagの回と同じ）で、旧機能との違いは確認できなかった。

- https://www.anthropic.com/claude-fable-and-mythos-5-1 → **公開済み** content/tools/claude-fable-5-1.md（2026-09-02・公開）
  - 手元のセッションで作成（オーナー指示「ニュースの方からも1件深掘り」）。図3枚。
    `check_numbers.py` は照合できる数字47個すべてが出典6件のいずれかに存在。pytest 618 passed・build 139ファイル。
  - 📌 記事の芯＝**単価は据え置き（$10/$50）で、値下げはキャッシュ読み取り $1→$0.25 の1項目だけ。**
    「約25%」「最大約45%」は Anthropic が2026年8月の4週間の利用を集計した比率。
  - ⚠️ この発表は `news.json` に入っていない（`/news/` の外にある `featuredGridLink` 型のため）。
    トラッカーの `parse_anthropic_news` が拾えない構造＝別件で直す。

- https://www.anthropic.com/news/introducing-claude-tag → **公開済み** content/tools/claude-tag-slack.md（2026-09-01・公開）
  - `www.anthropic.com` に到達できた。図3枚（`claudetag-position-grid` / `claudetag-billing-boundary` /
    `claudetag-session-ladder`）。`check_numbers.py` は照合できる数字1個（65%）が出典に存在
    （出典4件とも取得成功）。pytest 618 passed・build 137ファイル。
  - 📌 記事の芯＝**Enterprise（請求書払い）は、自分で spend limit を設定するまで上限が無いと
    公式ドキュメントに明記されている**（Teamは逆に、残高を入金するまで一切反応しない）。
  - ⚠️ 他社比較は保留にした。OpenAI（`openai.com`・`help.openai.com`）はbot判定の403、
    Microsoft・Salesforceは経路遮断（`CONNECT tunnel failed`）で到達できず、
    Google（`cloud.google.com/gemini-enterprise`）は本体ページのみ200で詳細は確認できなかった。
    二次情報は使わず、記事内に「比較できなかった」とそのまま書いた。
  - ⚠️ 旧アプリ「Claude in Slack」の詳細（`support.claude.com`）も経路遮断で到達不可。
    次にこのドメインが来たら再試行対象にすること。
- https://deepmind.google/blog/introducing-computer-use-in-gemini-3-5-flash/ → **公開済み** content/tools/gemini-computer-use.md（2026-08-31・公開）
  - `blog.google`（転送先）に到達できた。図3枚（`gemini35cu-timeline` / `gemini35cu-osworld` / `gemini35cu-actions`）。
    `check_numbers.py` は **12個すべて出典に存在**（出典8件とも取得成功）。pytest 618 passed・build 135ファイル。
  - 📌 記事の芯＝**「専用モデル→主力モデルへの内蔵」という設計変更は Google も OpenAI も同じ**で、
    しかも Gemini 側は標準搭載からわずか50日で「推奨モデル」の座を次の世代（3.7 Flash）に譲っている。
  - ⚠️ Anthropic・OpenAI の数字は、この記事のために `platform.claude.com` と `developers.openai.com` を
    新たに読んだ（キューの元メモには無かった調査）。OSWorld のベンチマーク名が **OSWorld-Verified と
    OSWorld-2.0 で版違い**だったので、記事では混ぜずに書き分けた。
- https://openai.com/index/daybreak-models-are-now-available-on-aws → **公開済み** content/tools/daybreak-on-bedrock.md（2026-08-21・公開）
  - 再試行で通った3件目（1回目は 2026-08-11 に停止。理由②が `CONNECT tunnel failed`＝経路遮断だった）。
    図4枚（`daybreak-bedrock-vs-direct` / `daybreak-blue-same-price` / `daybreak-what-is-closed` /
    `daybreak-vendor-shapes`）。`check_numbers.py` は **13個すべて出典に存在**（出典8件とも取得成功）。
    pytest 555 passed・build 108ファイル。
  - ⚠️ **`openai.com` の本文は今日も読めていない（7回連続403）。**発表本文は **AWS 側の公式ブログ**から取った。
    数字は `docs.aws.amazon.com` のモデルカード3枚と `developers.openai.com` の料金ページ。
  - 📌 記事の芯＝**同じモデルでも AWS 経由のほうが高く、上げ幅が揃っていない**
    （Red は 1.1倍、Blue は入力 1.375倍・出力 1.65倍）。倍率は記事側の割り算だと明記した。
  - 🔍 **書きながら1件、自分の誤りを潰した**＝図の下書きで「速い層（Priority）・安い層（Flex）は
    汎用モデルなら使える」と書きかけたが、**汎用 Sol のモデルカードにも「Priority and Flex tiers are
    not supported」と書いてあった**。生の行を見て直した。
- https://tech.preferred.jp/ja/blog/introducing-matlantis-pfp-v9/ → **公開済み** content/tools/matlantis-pfp-v9.md（2026-08-20・公開）
  - 再試行で通った2件目（1回目は 2026-08-17 に `CONNECT tunnel failed`＝経路遮断）。図4枚
    （`pfp9-arena-rank` / `pfp9-five-tasks` / `pfp9-h2-rmse` / `pfp9-elements`）。
    `check_numbers.py` は照合できる数字3個のうち**2個が出典に存在**、残る1個（`61%`）は
    記事が 3.10 と 7.88 から計算した値で、**そう明記して載せてある**（出典4件とも取得成功）。
    pytest 555 passed・build 102ファイル。
  - ⚠️ 一次情報は **PFNの技術ブログ2本**と **arXiv の v8 プレプリント**だけ。
    **料金は書いていない**（`matlantis.com` に到達できず）。MLIP Arena の公開リーダーボードは
    Streamlit の動的ページで、HTMLにモデル名も点数も入っていない＝**中身を読めない**。
- https://openrouter.ai/qwen/qwen3.8-max → **公開済み** content/tools/qwen3-8-max.md（2026-08-20・公開）
  - 再試行で通った1件目。図4枚（`qwen38-two-weights` / `qwen38-vs-37` / `qwen38-not-first` / `qwen38-price-region`）。
    `check_numbers.py` は **6個すべて出典に存在**（出典9件とも取得成功）。pytest 529 passed・build 99ファイル。
    ⚠️ 一次情報は **HuggingFace のモデルカード**と **`help.aliyun.com`** の2つだけ。`qwen.ai` は今も読めない。
- https://deepmind.google/blog/introducing-gemini-3-7-flash/ → content/_draft-gemini-3-7-flash.md（2026-08-14）
  - 図4枚（`gemini37-price-window` / `gemini37-vs-36` / `gemini37-four-prices` / `gemini37-not-first`）。
    `check_numbers.py` は **48個すべて出典に存在**（出典9件とも取得成功）。
    **人間の検証待ち。**公開するなら `content/tools/gemini-3-7-flash.md` へ移す。
- https://deepmind.google/blog/introducing-gemini-3-6-flash-3-5-flash-lite-and-3-5-flash-cyber/ → content/_draft-gemini-3-6-flash.md（2026-08-05）
  - 図4枚（`gemini36-lineup` / `gemini36-cheap-price` / `gemini36-generation` / `gemini36-bench`）。
    **人間の検証待ち。**公開するなら `content/tools/gemini-3-6-flash.md` へ移す。
- https://www.anthropic.com/news/claude-opus-5 → **公開済み** content/tools/claude-opus-5.md（2026-08-04）
  - 同日、OpenAI の公式数字を足して全面的に書き直し（3回目）→ 人間が検証して公開。
  - ⚠️⚠️ **2026-08-05 訂正。**「`gpt-5.5-pro` の $60/$270 は外挿だった」と記録していたが**誤り**。
    生ページには `gpt-5.5-pro $30.00 - - $180.00 $60.00 - - $270.00` と実在する
    （見出しは Short context / Long context の8列）。ルーティンの下書きが正しかった。
    **誤ったのは検証した人間側**＝確認をAIに要約させ、「その行は無い」「272Kという但し書きだけ」
    という嘘の確認結果を信じて、正しい数字を消した。272K はページに1度も出てこない。
    → **数字の確認は、要約させずに生の行を見ること。**
