# deepdive_queue の保管庫

`tools/rotate_archives.py` が済んだ在庫を逐語で移す先（追記専用・担当は読まない）。
真の保管庫は git 履歴。設計＝docs/superpowers/specs/2026-08-20-token-diet-design.md

## 2026-08-20 回転

- [x] https://deepmind.google/blog/introducing-gemini-3-6-flash-3-5-flash-lite-and-3-5-flash-cyber/
  - **2026-08-05: 下書きを作成**（content/_draft-gemini-3-6-flash.md・図4枚）。
    ⚠️ **このURLは 302 で `blog.google` に転送される**（`blog.google/innovation-and-ai/models-and-research/
    gemini-models/gemini-3-6-flash-3-5-flash-lite-3-5-flash-cyber/`）。WebFetch は他ホストへの転送を追わないので、
    **返ってきた転送先URLで叩き直す**こと。本文は転送先にある。記事の出典は転送先URLで書いた。
  - **読めた一次情報**＝`blog.google`（発表本文）／`ai.google.dev/gemini-api/docs/pricing`（料金）／
    `deepmind.google/models/gemini/flash/` と `/flash-lite/`（コンテキスト長・最大出力・入力形式）／
    `platform.claude.com`（Haiku 4.5）／`developers.openai.com/api/docs/{pricing,models}`（GPT-5.6 Luna）。
    ⚠️ **`ai.google.dev/gemini-api/docs/models` には仕様表が無い**（説明文だけ）。コンテキスト長は
    `deepmind.google/models/gemini/...` 側にある。次回もここを見ること。
  - **見つからなかった数字**＝Gemini の学習データの締め切り（Google のどのページにも無い）／
    Gemini 3.5 Flash Cyber の料金・仕様（料金ページに行が無い。限定パイロットのため）／
    OpenAI の「短い入力／長い入力」の境目のトークン数（前回と同じ。**推測で埋めない**）／
    「毎秒350出力トークン」の測定条件。
  - 💡 **比較相手は GPT-5.6 Luna にした。**`developers.openai.com/api/docs/models` の Frontier models に
    mini / nano は載っていない（料金ページの表にはある）。**「コスト最適化型」として docs に説明があるのは Luna**
    なので、そちらを使った。安いモデル比較を次にやるときも同じ判断でよい。
  - **到達性は確認済み**＝`deepmind.google` と `ai.google.dev` は Opus 5 の記事を書いたときに
    クラウド側から実際に読めている。料金は `ai.google.dev/gemini-api/docs/pricing`。
  - 切り口＝**安いモデル同士の比較**。旗艦モデルより、このサイトの読者（非エンジニアの会社員）に近い。
    比較相手＝Claude Haiku 4.5（`platform.claude.com/docs/en/about-claude/pricing`）と
    OpenAI の小型モデル（**`developers.openai.com/api/docs/pricing` のみ**）。
  - ⚠️ **`openai.com` の HTMLページは 403（Cloudflare の bot 判定）。**RSS と `developers.openai.com` は
    200 なので、経路ではなく先方の判定。**UA偽装での迂回はしない。**`developers.openai.com` だけを使う。
  - ⚠️ **トークン課金と分課金を1本の表に混ぜない**（前回 `gpt-realtime-translate` $0.034/分 のような
    分課金があることを確認済み）。単位が違うものは表を分ける。
  - ⚠️ 3つのモデルが同時発表なので、**用途の違い**（Flash / Flash-Lite / Flash Cyber）を先に整理してから
    値段を並べること。値段だけ並べても選べない。
- [x] https://openrouter.ai/qwen/qwen3.8-max
  - **2026-08-20 2回目（再試行）: 公開した** → `content/tools/qwen3-8-max.md`。図4枚。
    🔑 **前回の停止理由「経路の遮断」が実際に直っていた。**`- [!]` の再試行が効いた最初の例。

    **① 到達性が変わった（2026-08-20 実測）**

    | ドメイン | 2026-08-05 | 2026-08-20 |
    |---|---|---|
    | `help.aliyun.com/zh/model-studio/model-pricing` | `CONNECT tunnel failed` | **200**・3.4MB |
    | `help.aliyun.com/zh/model-studio/text-generation-model` | 同上 | **200**・370KB |
    | `modelscope.cn` | 同上 | 302（未使用） |
    | `qwen.ai` / `www.qwen.ai` / `qwenlm.github.io` | 同上 | **まだ `CONNECT tunnel failed`** |
    | `www.alibabacloud.com` | 同上 | **まだ `CONNECT tunnel failed`** |
    | `www.qwencloud.com`（モデルカードが案内する新しい公式API窓口） | 未確認 | **`CONNECT tunnel failed`** |

    - ⚠️ **まだ許可リストに足す価値があるドメイン**＝`qwen.ai`（発表ブログ。`qwen.ai/blog?id=qwen3.8`）と
      **`qwencloud.com`（モデルカードが「公式のAPIサービス」として案内している新ドメイン。料金はここにある見込み）**。
      `qwenlm.github.io` と `www.alibabacloud.com`（`help.aliyun.com` の英語版）も未到達。
    - ⚠️ 環境の Network access を Custom にして足すとき、**「Also include default list of common package managers」の
      チェックを外さないこと**（外すと同じ環境の MarketWatch 側が全部壊れる）。

    **② 🆕 前回「当面できない」と書いた HuggingFace のモデルカードが、実際には出ていた**

    2026-08-05 の記録は「HuggingFace の `Qwen` org に Qwen3.8 は1件も無い」だったが、その後に公開された。
    **結果として、この記事のいちばん濃い一次情報になった**（Alibaba のドキュメントより情報量が多い）。

    - `Qwen/Qwen3.8-2.4T-A95B`（2026-08-08 作成）＝**最上位クラスの重み**。`license_name: qwen3.8-max`。
      **他社比較表つき**（Opus 4.8 / Fable 5 / GPT 5.6 Sol / Qwen3.7-Max / Qwen3.8-Max の5列・31項目）
    - `Qwen/Qwen3.8-27B`（2026-08-05 作成）＝**Apache-2.0**・画像/動画も読める
    - 📌 **教訓＝「重みが未公開だから当面できない」も、日付が変われば覆る。**停止理由に書いた前提は、
      再試行のたびに実際に測り直すこと（`help.aliyun.com` の経路と、この2つの両方が変わっていた）。

    **③ 数字を取るときに効いたこと（次も同じ型が使える）**

    - 🚨 **`help.aliyun.com` は素の `<tr>` を返さない。**本文は `window.__ICE_PAGE_PROPS__` の JSON の
      `docDetailData.storeData.data.content` に**HTMLエスケープされて入っている**。ここを取り出してから
      `<table>` を**セル単位**で解析する。⚠️ **平文化すると列がずれる**（`gemini-3-7-flash` と同じ罠）
    - `help.aliyun.com/zh/model-studio/models`（カード一覧）**には料金が無い**。料金は
      **`/zh/model-studio/model-pricing`**（`billing-for-model-studio` から 301）。仕様は
      **`/zh/model-studio/text-generation-model`**。この2本が単一ソース
    - 🚨 **単価が「元」建てで、他社は「ドル」。**換算レートは出典のどこにも無いので**換算しない**。
      表を2本に分けた（プロンプトの「単位が違うものを1本の表に混ぜない」がそのまま効いた）
    - 💡 **同じモデルなのに置いてある場所で単価が違う**＝北京・東京・フランクフルト・バージニアは
      12元/36元、**シンガポールだけ 14.988元/44.965元**。表の「服务部署范围」欄がシンガポールだけ「国际」で
      他は「全球」。**この2語の意味は料金ページに説明が無い**ので、記事にもそう書いた
    - 💡 **前の世代のほうが安く見える**＝`qwen3.7-max` は「原価12元 限时5折」。`qwen3.8-max` に割引表示は無い。
      ⚠️ **5折から6元/18元を計算して表に載せることはしなかった**（出典に「書いてある」のは原価と割引率だけ）

  - **見つからなかった数字**＝Qwen3.8-Max の**一度に書ける量**と**学習データの締め切り**
    （Alibaba のどのページにも無い）。発表日（`qwen.ai` が読めないため）。文脈キャッシュの割引率。
  - 📌 **記事側の計算**＝重みのファイル合計（213個の safetensors を合計して 4,892.4GB）と、
    「30項目中7項目で最高」「30項目すべてで前世代より上」の数え。`check_numbers.py` は $ と % しか
    見ないので照合対象外。**どちらも記事本文に「この記事で数えた／足した」と明記してある**。
  - 旧メモ（2026-08-04 追記時点）: 2026-08-04 にトラッカーが即時メールで拾った Alibaba の最上位モデル。
    ⚠️ OpenRouter は提供窓口であって一次情報ではない。**Alibaba/Qwen 自身の公式発表かモデルカードを探すこと**
    （HuggingFace の `Qwen` org は許可リストに入っている）。見つからなければ「公表されていない」と書く。
    比較相手は Claude Opus 5 / GPT-5.6 / Gemini 3.1 Pro。**単価・読める量・学習データの締め切り**が揃えば表になる。
    到達できないドメインがあったら、ここに**ドメイン名を列挙**しておくこと（まとめて許可リストに足すため）。
  - **2026-08-05 1回目: 下書きを作らずに停止した。**キューのURL自体（OpenRouter）は取得できたが、
    **Alibaba/Qwen 側の一次情報に到達できる経路が1つも無い**ため。二次情報で数字を埋めるくらいなら書かない。

    **① 許可リストに足すドメイン（全部 `CONNECT tunnel failed, response 403` ＝経路の遮断。先方のbotブロックではない）**

    | ドメイン | 何が載っているはずか |
    |---|---|
    | `qwen.ai` / `www.qwen.ai` | Qwen 公式サイト・ブログ（`qwen.ai/blog?id=...` の形）。**最優先** |
    | `qwenlm.github.io` | 公式ブログの旧ドメイン。技術記事はこちらに残っている |
    | `help.aliyun.com` | Model Studio（百煉）の日本語/中国語ドキュメント。**モデル一覧と料金はここ。2番目に重要** |
    | `www.alibabacloud.com` | 同じものの英語版（`/help/en/model-studio/models`） |
    | `dashscope.aliyuncs.com` | DashScope API のドキュメント/エンドポイント |
    | `modelscope.cn` / `www.modelscope.cn` | ModelScope。中国側のモデルカードはここに先に出る |
    | `www.aliyun.com` / `bailian.console.aliyun.com` | 料金ページ・コンソール |
    | `chat.qwen.ai` | 一般向けチャット。仕様の記載は薄いので優先度は低い |

    ⚠️ 環境の Network access を Custom にして足すとき、**「Also include default list of common package managers」の
    チェックを外さないこと**（外すと同じ環境の MarketWatch 側が全部壊れる）。手順は SESSION_HANDOFF.md の
    「クラウドルーティンは既定では各社の発表ページを読めない」節。

    **② 許可リストに足しても解決しないかもしれない点（先に知っておくと無駄足が減る）**

    - **HuggingFace の `Qwen` org に Qwen3.8 は1件も無い**（API で全件確認。最新は `Qwen3-ASR-0.6B-hf`＝2026-07-22、
      Qwen3.5/3.6 止まり）。重みが未公開なので、モデルカード経由の仕様確認は**当面できない**。
    - **GitHub の `QwenLM` にも Qwen3.8 のリポジトリが無い**（ピン留めは Qwen3.6 / Qwen3-VL / Qwen3-Coder / Qwen3-Omni）。
      GitHub は到達できるので、ここに出たらそれが一番早い一次情報になる。
    - → **次に足すべきは `help.aliyun.com` と `qwen.ai` の2つ。**クラウドの提供ドキュメントは重み未公開でも先に出る。

    **③ 参考（記事には使っていない）** OpenRouter のページには 入力 $2 / 出力 $6（100万トークンあたり）・
    コンテキスト 100万トークン・公開日 2026-08-03 と書かれていた。**これは OpenRouter が自社の窓口について
    書いている値であって、Alibaba 公式の値ではない**ので、一次情報が読めるまで記事には載せない。
    最大出力・学習データの締め切り・パラメータ数は OpenRouter にも記載が無い。
- [x] https://www.anthropic.com/news/claude-opus-5
  - 2026-08-04 1回目: `Host not in allowlist: www.anthropic.com` の403で取得できず停止（記録は正しい挙動）。
    環境のネットワークアクセスを「カスタム」にして各社ドメインを追加し、解消。経緯は SESSION_HANDOFF.md 参照。
  - 2026-08-04 2回目: 取得成功。下書きを作成。
    ⚠️ **OpenAI のドメインは許可リストに入っていない**（`openai.com` / `developers.openai.com` とも
    プロキシが `CONNECT tunnel failed, response 403` を返す＝先方のbotブロックではなく経路の遮断）。
    Google（`ai.google.dev` / `deepmind.google`）と Anthropic（`www.anthropic.com` /
    `platform.claude.com`）は到達する。他社比較を書くなら、次に許可リストへ足すのは OpenAI。
  - 2026-08-04 3回目: 許可リストに `*.openai.com` を追加したので再実行。**OpenAI の公式料金ページの数字を
    入れて書き直すこと。**前の版は git に残っているので、悪くなったら戻せる。
  - 2026-08-04 3回目の結果: **完了**。OpenAI の公式料金・公式モデル一覧を実際に読んで書き直した。
    ⚠️ **`openai.com/api/pricing/` は403のまま**（プロキシではなく先方が返す403）。読めるのは
    **`developers.openai.com/api/docs/pricing`** と **`/api/docs/models`**。
    `platform.openai.com/docs/pricing` は 301 で developers 側へ飛ぶので、そちらを直接叩くのが速い。
    ⚠️ OpenAI の料金表は「短い入力／長い入力」の2段だが、**境目のトークン数がページに書かれていない**。
    記事には「公表されていない」と明記した。埋めたくなっても推測で書かないこと。
- [x] https://deepmind.google/blog/introducing-gemini-3-7-flash/
  - 2026-08-13 自動追記（major・Google DeepMind「Introducing Gemini 3.7 Flash」）
  - **2026-08-14: 下書きを作成**（content/_draft-gemini-3-7-flash.md・図4枚）。
    ⚠️ **3.6 Flash と同じく 302 で `blog.google` に転送される**
    （`blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-3-7-flash/`）。
    **返ってきた転送先URLで叩き直すこと。**これで2回連続なので、`deepmind.google/blog/...` は毎回そう考えてよい。
  - 🚨 **WebFetch は本文を要約して返した**（「Return the full text verbatim」と頼んでも要約になった）。
    数字を写す用途では使えない。**`curl` で生HTMLを取って、自分で `<tr>`/`<td>` を解析すること。**
  - 🚨🚨 **タグを剥がして1行ずつにした版は、表の空セルを落として列がずれる。**実例＝モデルカードの
    `Input price` 行は、平文化すると `$0.75 / $2.00 / $1.25` の**3値**に見えるが、生の `<tr>` は
    **5列で `$0.75* | $0.75* | $2.00 | $2.00 | $1.25`**（3.7 Flash / 3.6 Flash / Claude Sonnet 5 /
    GPT-5.6 Terra / Muse Spark 1.2）。**平文で読むと「3.6 Flash の値段が消える」**＝過去の
    `gpt-5.5-pro` 事故とまったく同じ壊れ方。**表はセル単位で解析する。**
  - **読めた一次情報**＝`blog.google`（発表本文）／
    **`deepmind.google/models/model-cards/gemini-3-7-flash`（HTML・比較表20項目つき。今回いちばん濃い）**／
    `ai.google.dev/gemini-api/docs/pricing`（料金・Standard/Batch/Flex/Priority の4段）／
    `deepmind.google/models/gemini/flash/`（モデルカードと同じ比較表＋利用企業の声）／
    `platform.claude.com`（Sonnet 5）／`developers.openai.com/api/docs/{pricing,models}`（GPT-5.6 Terra）。
  - ⚠️ **`deepmind.google/models/model-cards/gemini-3-6-flash`（前の世代）は PDF**
    （`storage.googleapis.com/deepmind-media/Model-Cards/...pdf` へ転送）。**この環境では中身を取り出せない**
    （`pdftotext` 無し・`pypdf` は `_cffi_backend` が壊れていて import できない）。
    **3.7 のカードは HTML なので読める。**新旧を比べたいときはこの差に注意。
  - **見つからなかった数字**＝Muse Spark 1.2（Meta）の一次情報すべて。OpenAI の「短い入力／長い入力」の
    境目のトークン数（前回と同じ。**推測で埋めない**）／利用企業の声の「35%安い」の測定条件。
  - 🚨 **許可リストに足すドメイン（全部 `CONNECT tunnel failed, response 403` ＝経路の遮断。先方のbot判定ではない）**

    | ドメイン | 何が載っているはずか |
    |---|---|
    | `dev.meta.ai` | Meta の Model API ドキュメント。**Muse Spark 1.2 の料金と仕様はここ。最優先** |
    | `ai.meta.com` | Meta AI の公式サイト・モデル紹介 |
    | `www.llama.com` / `llama.com` | Llama/Muse 系のモデルカード |
    | `about.fb.com` | Meta のプレスリリース |

    ⚠️ 環境の Network access を Custom にして足すとき、**「Also include default list of common package managers」の
    チェックを外さないこと**（外すと同じ環境の MarketWatch 側が全部壊れる）。
  - 💡 **今回の記事の芯になった3つ（次に同じ型が使える）**
    1. **「半額」は 3.7 の特典ではない**＝料金ページを下まで読むと **3.6 Flash も $0.75/$3.75** に下がっている。
       どちらも「2026-12-31まで／2027-01-01から $1.50/$7.50」。**値下げの主語を確かめること。**
    2. **同じ会社の同じ日の2ページで数字が食い違う**＝3.6 Flash の DeepSWE v1.1 が
       **発表ページ 49.0% ／ モデルカード 48.6%**。どちらが正かは公表されていないので両方書いた。
    3. **他社の値は他社の公式で突き合わせる**＝Google の表の Claude Sonnet 5（$2/$10）と
       GPT-5.6 Terra（$2/$12）は**各社の公式ページと一致した**。Muse Spark 1.2 だけ確認できず。
       **この「突き合わせて一致した／できなかった」を書く型は、比較記事で毎回使える。**
  - 📌 **20項目中9項目で最高**という数え（残り11項目は他社か前の世代が上）は**記事側の計算**。
    `check_numbers.py` は $ と % しか見ないので、この種の数はそもそも照合対象外。

## 2026-08-22 回転

- [x] https://tech.preferred.jp/ja/blog/introducing-matlantis-pfp-v9/
  - 2026-08-17 自動追記（major・Preferred Networks「PFP v9のご紹介: MLIP Arenaでのベンチマーク評価とr2SCANによる実験値再現性の向上」）
  - ✅ **2026-08-20 2回目（再試行）: 公開した** → `content/tools/matlantis-pfp-v9.md`
    - **許可リストが直っていた。**1回目に `CONNECT tunnel failed` だった `tech.preferred.jp`・`aws.amazon.com`・
      `docs.aws.amazon.com`・`arxiv.org` は**すべて 200**（実測）。⚠️ ただし `matlantis.com` と
      `www.nature.com` と `papers.nips.cc` は**まだ通らない**（`http=000`）。
    - 🔑 **「経路遮断なら再試行する」という規則が、実際に1本の記事になった2例目。**
      1回目の記録に「どちらの遮断だったか」を書いてあったから拾い直せた。**この記録は続けること。**
    - ⚠️ **表1・表2は本文テキストではなく PNG 画像**（`wp-content/uploads/2026/08/image10.png` と
      `image4.png`）。HTMLをテキストに直しただけでは数字が1つも取れない。画像を落として直接読むこと。
      そのため `grep` では照合できない（`eSEN` の注記も画像の中にある）。
    - 切り口＝「材料の話」ではなく**「総合1位の読み方」**に寄せた（読者が非エンジニアのため）。
  - **2026-08-17 1回目: 下書きを作らずに停止した。**発表本文に到達できないため。

    **① `tech.preferred.jp` は経路の遮断（許可リスト）。先方の bot 判定ではない**

    | 叩いた先 | 結果 |
    |---|---|
    | `tech.preferred.jp/ja/blog/introducing-matlantis-pfp-v9/` | `CONNECT tunnel failed, response 403` |
    | `tech.preferred.jp/ja/blog/`（別パス） | 同上 |
    | `tech.preferred.jp/ja/blog/feed/`（トラッカーが見ているRSS） | 同上 |
    | `www.preferred.jp/ja/` | 同上 |
    | `matlantis.com/` / `matlantis.com/ja/` / `docs.matlantis.com/` / `www.matlantis.com/` | 同上 |
    | WebFetch（同URL） | `EGRESS_BLOCKED: Access to tech.preferred.jp is blocked by the network egress proxy` |
    | `huggingface.co/spaces/atomind/mlip-arena`（参考・MLIP Arena本体） | **200** |
    | `arxiv.org/abs/2504.03112`（参考・MLIP Arena の論文） | `CONNECT tunnel failed, response 403` |

    - ⚠️ **同じドメインのどのパスも 403 で、応答ヘッダ自体が返ってこない**（`cf-mitigated` のような
      先方由来のヘッダは無い＝プロキシが CONNECT の段階で切っている）。**許可リストに足せば直る種類。**
      切り分けの根拠＝`huggingface.co` は同じ経路で 200 が返っていること。**UA偽装での迂回はしない。**
    - トラッカー自身は GitHub Actions 側で走っているので RSS を取得できている。**読めないのはこの
      クラウドルーティンの環境だけ。**環境が違えば結果が変わる（SESSION_HANDOFF の「到達できるかどうかは
      必ずクラウド側で測ること」と同じ話の裏返し）。

    **② 許可リストに足すドメイン**

    | ドメイン | 何が載っているはずか |
    |---|---|
    | `tech.preferred.jp` | PFN 技術ブログ。**発表本文とベンチマークの数字はここ。最優先** |
    | `www.preferred.jp` / `preferred.jp` | PFN 公式サイト・プレスリリース |
    | `matlantis.com` / `www.matlantis.com` / `docs.matlantis.com` | Matlantis 製品ページ・料金・ドキュメント |
    | `arxiv.org` | MLIP Arena の論文（Chiang ら）。**比較の土俵の定義がここにある。他の記事でも使う** |

    ⚠️ 環境の Network access を Custom にして足すとき、**「Also include default list of common package managers」の
    チェックを外さないこと**（外すと同じ環境の MarketWatch 側が全部壊れる）。

    **③ RSS から分かったこと（トラッカーの `data/tracker/news.json` 経由。本文ではないので記事には使えない）**

    - 公開日 **2026-08-17 06:00 GMT**。`importance` は major、`vendor` は Preferred Networks
    - description は **抜粋のみで `[…]` で切れている**（「2021年7月のMatlantis™提供開始以来、その中核技術である
      機械学習原子間ポテンシャル(Machine Learning Interatomic Potential, MLIP)「Matlantis PFP […]」）。
      → **ベンチマークの点数・r2SCAN での再現性の数値・v8 との差は、ここから1つも取れない。**
    - **同じ日に続きの記事が出ている**＝「PFP v9のMLIP Arenaベンチマーク評価(詳細版)」
      `https://tech.preferred.jp/ja/blog/matlantis-pfp-v9-mlip-arena/`（minor・2026-08-17 05:59 GMT）。
      **数字が濃いのは間違いなくこちら。**①が解けたら2本セットで読むこと。

    **④ 書くとしたときの注意（①が解けた後の話）**

    - 題材が**材料シミュレーション（原子間ポテンシャル）**で、このサイトの読者（自動化したい非エンジニアの
      会社員）からは遠い。**LLM の料金比較の型はそのまま使えない。**書くなら「AIが実験を置き換える話」として
      1本にまとめるか、読者に近くないと判断して見送るか、**先に切り口を決めてから数字を集めること。**
    - 比較相手を置くなら MLIP Arena に載っている他のモデル（`huggingface.co/spaces/atomind/mlip-arena` は
      **この環境から 200 で読める**）。⚠️ ただし PFP v9 の行が Arena 側にあるかは未確認。

## 2026-08-23 回転

- [x] https://openai.com/index/daybreak-models-are-now-available-on-aws
  - ✅ **2026-08-21 2回目（再試行）: 公開した** → `content/tools/daybreak-on-bedrock.md`
    **再試行の理由＝前回の停止理由②が「経路遮断（CONNECT tunnel failed）」だったから**（手順1の条件どおり）。
    実際に**AWS 系ドメインが到達できるようになっていた**（`aws.amazon.com` 200・`docs.aws.amazon.com` 200）。
    🔑 **これが「一時的な失敗を永続的な状態にしない」設計が効いた2例目。**足された許可リストを
    誰も拾い直さなければ、この題材は永久に埋まったままだった。
  - ⚠️ **①（`openai.com` の bot 判定）は今日も直っていない。7回連続403**（`cf-mitigated: challenge`）。
    それでも書けたのは、**発表本文を AWS 側から取れたから**。この発表は AWS との共同発表で、
    **AWS 自身が同じ日に出したブログに本文がある**（著者3人のうち1人は OpenAI の担当者）:
    `https://aws.amazon.com/blogs/machine-learning/accelerate-cyber-defense-with-openai-and-aws-daybreak-red-daybreak-blue-now-available-to-eligible-customers-on-amazon-bedrock/`
    💡 **次に `openai.com/index/...` が来たときの新しい逃げ道**＝**発表の相手方を探すこと。**
    共同発表なら、もう一方の当事者の公式ブログは一次情報であって二次情報ではない。
  - 📌 **値段は `aws.amazon.com/bedrock/pricing/` ではなく、そこからリンクされている
    `docs.aws.amazon.com` のモデルカードに載っている。**料金ページ側の最上位モデルの値は
    `{priceOf!...}` の差し込みで、静的HTMLには入っていない（gpt-oss の一部だけ静的）。
    ⚠️ 料金ページのリンク `model-card-openai-daybreak-blue.html` は302で index に飛ぶ（先方のリンク切れ）。
    正しいのは **`model-card-openai-gpt-daybreak-blue-56-sol.html`**（Red 側のページの次ページリンクから拾える）。
  - 2026-08-11 自動追記（major・OpenAI「Daybreak models are now available on AWS」）
  - **2026-08-11 1回目: 下書きを作らずに停止した。**理由は2つあり、どちらも単独で停止の理由になる。
    ⚠️ 前回（`-legacy` の件）と違い、**このURLは現在のRSSに実在する**。消えたのではなく、読めないだけ。

    **① `openai.com` の HTMLページは今日も403（Cloudflare の bot 判定）。3回連続で戻っていない**

    | 叩いた先 | 結果 |
    |---|---|
    | `openai.com/index/daybreak-models-are-now-available-on-aws/`（スラッシュ有り） | **403**・9,842バイト |
    | 同（スラッシュ無し） | **403**・9,839バイト |
    | 同（WebFetch） | **HTTP 403**・本文なし |
    | `openai.com/news/rss.xml` | **200**・683,906バイト（1,124 item） |
    | `developers.openai.com/api/docs/models` | **200**・343,585バイト |
    | `developers.openai.com/api/docs/pricing` | **200**・542,673バイト |
    | `developers.openai.com/api/docs/guides/amazon-bedrock` | **200**・379,550バイト |

    - 応答ヘッダは前回と同じ **`cf-mitigated: challenge`** ＋ `server: cloudflare`。⚠️**先方のbot判定であって
      経路（許可リスト）の遮断ではない。許可リストに足しても直らない。**切り分けの根拠＝同じ `openai.com` の
      RSS が 200 で返っていること。**UA偽装での迂回はしない。**
    - 💡 **08-05（GPT-Live）→ 08-10（Daybreak legacy）→ 08-11（本件）で3回連続403。**「時間帯やegressのIP評価で
      戻る」ことは3回とも起きなかった。**次に `openai.com/index/...` が来ても、まずここを読んでから叩くこと。**

    **② AWS側（＝この発表のもう一方の当事者）のドメインが1つも到達できない。ここが本件固有の壁**

    この記事の主題は「AWSで使えるようになった」なので、**値段・対応リージョン・使える相手はAWS側にしか無い**。
    ところが Amazon 系は**全部 `CONNECT tunnel failed, response 403` ＝経路の遮断**（先方のbot判定ではない）。

    | ドメイン | 何が載っているはずか |
    |---|---|
    | `aws.amazon.com` | Bedrock の料金ページ（`/bedrock/pricing/`）と What's New。**最優先** |
    | `docs.aws.amazon.com` | Bedrock ユーザーガイド（対応モデル・対応リージョン）。**2番目に重要** |
    | `press.aboutamazon.com` / `www.aboutamazon.com` | Amazon 側のプレスリリース |

    ⚠️ 環境の Network access を Custom にして足すとき、**「Also include default list of common package managers」の
    チェックを外さないこと**（外すと同じ環境の MarketWatch 側が全部壊れる）。

    **③ RSS から分かったこと（本文ではないので記事には使えない）**

    - タイトルは待ち行列のURLどおり **"Daybreak models are now available on AWS"**。カテゴリは `Product`
    - 公開日 **2026-08-11 10:00 GMT**
    - description 全文＝`OpenAI and AWS are making Daybreak cybersecurity capabilities available through Amazon Bedrock to support enterprise security workflows.`
    - → **「どのモデルが」「どのリージョンで」「いくらで」「誰が使えるのか」は、この1文から1つも取れない。**

    **④ 到達できた一次情報（`developers.openai.com` 実測・生の行をそのまま写す）**

    ⚠️ **記事には使っていない。**書くときは必ずページを開き直して、その数字がそこに在ることを確かめること。

    - `/api/docs/guides/amazon-bedrock` に **Bedrock 版の機能対応表が実在**。ただし
      **本文に `Daybreak` は0回・`Cyber` は3回とも左のナビ項目**（Cybersecurity checks / Cyber safety）で、
      **本件の中身（Daybreak が Bedrock に載った話）は、このガイドにはまだ1行も無い**。
      ページ自身が「The information below represents feature availability as of **July 13, 2026**」と断っている。
    - 同ガイドから拾える生の記述（**AWS側の話だがOpenAIが書いているので一次情報**）:
      - コンテキスト長＝`272,000 tokens for GPT-5.4 and GPT-5.5` / `1,050,000 tokens for GPT-5.6 Sol, Terra, and Luna`
      - Bedrock では使えないもの＝音声入力・WebSocket・Pro mode・Programmatic Tool Calling・Multi-agent・
        hosted file search・Computer use・Shell tool・Image generation tool・Remote MCP servers。
        サービス階層は `On-demand inference only`
      - 料金＝`AWS bills Amazon Bedrock usage.` / `Bedrock-specific pricing can differ from direct OpenAI API pricing`
    - `/api/docs/pricing` にも **`OpenAI models in Amazon Bedrock are billed through AWS and may differ from direct
      OpenAI pricing.`** と明記。⚠️**つまり Bedrock の値段は OpenAI 側のどのページにも無い。**
      AWS が読めない限り、この記事の中心になる「AWSでいくらか」は**構造的に書けない**。
    - `/api/docs/models` の Specialized models にある Daybreak は前回と同じ3つ（`GPT-5.6 Cyber` /
      `Daybreak Red` / `Daybreak Blue`）で、**説明文1行だけ。コンテキスト長・締め切りの記載は無い**。
    - `/api/docs/pricing` の Cyber models の表（Short context / Long context の8列）も前回と同一。生の行:
      - `gpt-5.6-sol   $5.00 $0.50 $6.25 $30.00   $10.00 $1.00 $12.50 $45.00`
      - `gpt-5.6-cyber $12.50 $1.25 $15.625 $75.00   - - - -`
    - 💡 **参考: 「272K」の出どころが判明した。**過去の訂正メモにある `272K` は
      **`/api/docs/pricing` には今日も0回**（実測）だが、**`/api/docs/guides/amazon-bedrock` には実在する**
      （GPT-5.4 / 5.5 の Bedrock でのコンテキスト長）。**別ページの数字が混ざっていた**というのが実態。
      過去の訂正（「料金ページに272Kは無い」）はそのまま正しい。

    → **①だけなら「発表本文が読めない」で済むが、②があるので、許可リストを直しても今日は書けなかった。**
      **次にやるべきは AWS 系ドメインの追加。**それが済めば、AWS の Bedrock 料金ページ・対応リージョン表という
      一次情報が使えるようになり、`developers.openai.com` 側と突き合わせて比較記事が成立する。

## 2026-09-03 回転

- [x] https://www.anthropic.com/claude-fable-and-mythos-5-1
  - ✅ **2026-09-02: 公開した**（オーナーのローカルセッションで作成） → `content/tools/claude-fable-5-1.md`
    （図3枚 `fable51-price-grid` / `fable51-cost-index` / `fable51-bench`・出典6件すべて取得成功・
    `check_numbers.py` は照合できる数字 **47/47** が出典に存在・pytest 618 passed・build 139ファイル）
  - 📌 記事の芯＝**入力・出力の単価は Fable 5 と同じ $10/$50 で、下がったのはキャッシュ読み取り
    $1→$0.25 の1項目だけ。それで「約25%（最大約45%）安い」と公式が説明している**
  - ⚠️ 手元では `www.anthropic.com` 200・約450KB。クラウド側は 9/1 に `/news/introducing-claude-tag` へ
    到達できているので同じホストは通るはず（未測定）

## 2026-09-06 回転

- [x] https://developers.openai.com/api/docs/guides/latest-model
  - ✅ **2026-09-05: 公開した**（オーナーのローカルセッションで作成） → `content/tools/gpt-6-astra.md`
    （図3枚 `astra-habits-grid` / `astra-vs-sol-price` / `astra-output-price-tier`・出典4件すべて取得成功・
    `check_numbers.py` は照合できる数字 **17/17** が出典に存在・pytest 625 passed・build 140ファイル・
    ブラウザ厳密計測 0問題）
  - 📌 記事の芯＝**いちばん大きな変更は性能ではなく「聞き返して止まりやすくなった」こと。
    OpenAI 自身が公式ガイドでそう書き、直すための指示文を公開している**。記事はその指示文を
    日本語に直して並べたもの＝このサイトの型（プロンプト中心）にそのまま乗る
  - 📌 単価は GPT-5.6 Sol の **2.5倍**（入力 $10 / 出力 $50）。ただし公式は「出力トークンが減るので
    1件あたりの費用は下がる」と書いている。⚠️ **その数字は公開されていない**ので記事では比率を出していない
  - ⚠️ **発表ページ本体は読めていない**ので、安全性の話（Preparedness Framework で Critical に達した
    最初のモデル）は **RSS の公式要旨の範囲だけ**にとどめ、記事にもそう明記した

## 2026-09-22 回転

- [x] https://deepmind.google/blog/introducing-computer-use-in-gemini-3-5-flash/
  - →保管: ✅ **2026-08-31 1回目: 公開した** → `content/tools/gemini-computer-use.md`
    （`blog.google` へ302転送・到達できた。図3枚・出典8件すべて取得成功・check_numbers.py は12/12が出典に存在）
  - 2026-08-31 手動追記（補充1件目。`news.json` の major お知らせのうち、読めるホストで未処理のもの）
  - **このサイトの読者にいちばん近い題材**＝AIが画面を操作する＝コードを書かずに自動化する話そのもの
  - ⚠️ **302 で `blog.google` へ飛ぶ**（手元で最終200・約379KB を実測）。
    最終URL＝`blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-computer-use-gemini-3-5-flash/`。
    **`deepmind.google` だけでなく `blog.google` にも届く必要がある。**届かなければ、それは経路遮断
    （＝許可リストに足せば直る種類）なので、そう書いて止まること
  - 集めたい数字＝**対応している操作の種類・制限・料金・使えるモデル**。
    比較相手は Anthropic の computer use（`docs.claude.com` は許可リストに入っている）
- [x] https://www.anthropic.com/news/introducing-claude-tag
  - →保管: ✅ **2026-09-01 1回目: 公開した** → `content/tools/claude-tag-slack.md`
    （`www.anthropic.com` に到達・図3枚。`check_numbers.py` は照合できる数字1個〈65%〉が出典に存在。
    出典4件すべて取得成功。pytest 618 passed・build 137ファイル）
  - 📌 公開日は2026-06-23（発表ページの表示日付）。待ち行列に積まれたのは2026-08-31だが、
    「古い告知でも構わない」の方針どおり、checked日付を入れて処理した
  - ⚠️ **他社比較は保留にした。**OpenAI（`openai.com`・`help.openai.com`）はbot判定の403、
    Microsoft（`learn.microsoft.com`）・Salesforce（`help.salesforce.com`）は経路遮断
    （`CONNECT tunnel failed`）で到達できず。Google（`cloud.google.com/gemini-enterprise`）は
    本体ページのみ200で、料金・連携の詳細は確認できなかった。二次情報は使わず、
    記事内で「比較できなかった」とそのまま書いた
  - 🚨 旧アプリ「Claude in Slack」の詳細ページ（`support.claude.com`）は経路遮断で到達不可。
    次にこのドメインを叩く行が来たら、まずここに記録した経路遮断を再試行対象にすること
- [x] https://www.anthropic.com/news/reflect-with-claude
  - →保管: ✅ **2026-09-02: 公開した** → `content/tools/reflect-with-claude.md`
    （`www.anthropic.com` に到達。図3枚。出典は発表ページ1件のみ〈他は経路遮断・bot判定で
    到達できず〉。数字が薄い題材で `check_numbers.py` は照合対象0個〈$・%が本文に無い〉。
    pytest 618 passed・build 142ファイル）
  - ⚠️ `help.openai.com`（OpenAIの個人利用分析ページ想定）は403（bot判定の可能性が高いが
    ヘッダは未確認）。`knowledge.workspace.google.com`（GoogleのGemini利用レポート）は
    `CONNECT tunnel failed`＝**経路遮断**。次にこのドメインを叩く行が来たら再試行対象にすること
  - 📌 `support.claude.com` も引き続き経路遮断（Claude Tagの回と同じ）。Team・Enterpriseプランの
    対象可否は発表ページに記載がなく、確認できていない
- [x] https://deepmind.google/blog/introducing-agentic-video-in-gemini/
  - →保管: ✅ **2026-09-03: 公開した** → `content/tools/gemini-agentic-video.md`
    （`deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`agentic-video-gains` /
    `agentic-video-timeline` / `agentic-video-modality`）。出典7件すべて取得成功
    （うち1件は転送元URL）。`check_numbers.py` は照合できる数字10個すべてが出典に存在。
    pytest 618 passed・build 146ファイル）
  - 2026-09-01 自動追記（major・Google DeepMind「Introducing agentic video understanding with Gemini」）
  - 📌 記事の芯＝**静的処理（1FPS一律）に対しエージェント型は必要な部分だけ動的に探索し、
    長尺動画でトークン最大88%減・コスト最大66%減・精度最大7%向上（Google発表の「最大」値）。
    ただし短い動画（5分未満）は探索のぶん最初の応答が遅くなるとドキュメントに明記されている**。
    追加料金は無く標準トークン単価のまま
  - ⚠️ **開発者ガイド（`ai.dev/learn/agentic-video-understanding-with-gemini`）は経路遮断**
    （`Host not in allowlist: ai.dev`）。本文の数字はすべて `ai.google.dev`（別ホスト・到達可）と
    発表ページ・料金ページから取れたため、この記事は止めずに書けた。次に `ai.dev` を叩く行が
    来たら、まずここに記録した経路遮断を再試行対象にすること
  - 他社比較は Anthropic（`platform.claude.com`）・OpenAI（`developers.openai.com`）とも到達でき、
    どちらのモデル一覧にも「動画」の語が無いことを確認できた（二次情報は使っていない）
- [x] https://deepmind.google/blog/gemini-omni-1-1-flash-lets-you-build-with-more-control/
  - →保管: ✅ **2026-09-04: 公開した** → `content/tools/gemini-omni-1-1-flash.md`
    （`deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`omni11-resolution-price` /
    `omni11-vendor-720p-price` / `omni11-scene-extension`）。出典9件すべて取得成功。
    `check_numbers.py` は照合できる数字11個すべてが出典に存在。pytest 618 passed・build 149ファイル）
  - ⚠️ **価格表（360p/720p/1080p/4K）は発表ページのテキストではなく埋め込み画像**。
    担当が画像を直接開いて目視で確認した（`gemini-omni-1.1-flash-pricing-ta...webp` を取得しPNG変換して読んだ）。
    `check_numbers.py` は複数出典をまとめて照合するため、$0.03・$0.15 等は他ページの無関係な値と
    偶然一致して「照合できた」扱いになっている可能性がある——**この記事の数字は画像の目視確認が根拠**であり、
    自動照合はその裏付けにはなっていない。次にこの種の「価格が画像埋め込み」のページが来たら同じ手順
    （画像URLを`curl`で取得→ PNG変換 → Read で目視）を使うとよい
  - 📌 記事の芯＝**解像度で秒単価が10倍**（360p $0.03 〜 4K $0.30）。延長は10秒刻みで合計40秒が上限、
    EU・スイス・英国はアップロード動画の延長が利用不可。比較したOpenAI Sora 2/Sora 2 Proは
    2026年9月24日にAPI提供終了と告知されており（この記事の確認時点で20日後）、Anthropicは
    動画生成モデルを提供していない
  - 2026-09-02 手動追記（オーナー指示の例「Gemini の新しいモデル」。`news.json` では `minor`）
- [x] https://deepmind.google/blog/intelligent-transcription-with-gemini-3-5-transcribe/
  - →保管: ✅ **2026-09-05: 公開した** → `content/tools/gemini-3-5-transcribe.md`
    （`deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`transcribe-price-per-min` /
    `transcribe-wer-by-benchmark` / `transcribe-vendor-grid`）。出典7件すべて取得成功。
    `check_numbers.py` は照合できる数字21個すべてが出典に存在。pytest 625 passed・build 154ファイル）
  - 2026-09-02 手動追記（同上。`news.json` では `minor`）
  - ⚠️ **302 で `blog.google` へ飛ぶ**（手元で最終200・約401KB を実測）。最終URL＝
    `blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-3-5-transcribe/`
  - 集めたい数字＝**文字起こしの料金（分課金かトークン課金か。⚠️ 単位が違うなら表を分ける）・
    対応言語・話者分離の有無**。このサイトの読者に近い題材＝会議の文字起こしを自動化する話
  - 📌 記事の芯＝**話者分離は最大3人まで正式対応、それを超えると試験的だと発表ページに明記**。
    誤り率（WER）は「全体平均」と「FLEURSベンチマーク（上位言語のみ）」で異なる2つの数字が
    公式発表内に別々に載っており、単一の精度として合成できないため両方併記した。
    料金は発表ページになく `ai.google.dev/gemini-api/docs/pricing` から取得。
    配信版は事前録音版よりGeminiで約1.8倍、OpenAIの配信2モデルは事前録音の最安値の3倍以上
    （いずれもこの記事の計算）。Anthropicは文字起こし専用モデルを公式ページに載せていない
- [x] https://deepmind.google/blog/introducing-gemini-3-8-flash-and-38-flash-cyber/
  - →保管: ✅ **2026-09-06: 公開した** → `content/tools/gemini-3-8-flash.md`
    （`deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`gemini38-price-three-gens` /
    `gemini38-safety-delta` / `gemini38-vendor-top-price`）。出典8件すべて取得成功。
    `check_numbers.py` は照合できる数字24個中23個が出典に存在、残る1個（`7.5%`）は
    出典の生の行に `+7.5-9.7%` という結合表記であることを直接確認して残した
    （消していない）。pytest 625 passed・build 158ファイル）
  - 2026-09-02 自動追記（major・Google DeepMind「Introducing Gemini 3.8 Flash and 3.8 Flash Cyber」）
  - 📌 記事の芯＝**3.6・3.7・3.8の3世代とも導入価格が入力$0.75・出力$3.75で完全に同じ**
    （2027年1月1日に3世代いっせいに$1.50/$7.50へ）。性能の比較表はモデルカードに
    画像として埋め込まれており、配信元 `lh3.googleusercontent.com` に**経路遮断**
    （`CONNECT tunnel failed, response 403`）で到達できず、本文中の数字だけで記事を書いた。
    次にこのホストを叩く行が来たら、まずここに記録した経路遮断を再試行対象にすること
  - ⚠️ **`deepmind.com`（`deepmind.google` ではない）も経路遮断**（evals-methodology ページ）。
    こちらも次に来たら再試行対象
  - ⚠️ Cyber版のモデルカードは404で存在せず、料金ページにも掲載が無い（Fairwind Program
    経由の限定提供のみ・一般には使えない）ことを実際にURLを叩いて確認した
- [x] https://deepmind.google/blog/introducing-weathernext-3-our-most-advanced-and-accurate-global-weather-ai-model/
  - →保管: ✅ **2026-09-07: 公開した** → `content/tools/weathernext-3.md`
    （`deepmind.google` → `blog.google` へ302転送・到達できた。図3枚（`weathernext3-resolution-grid` /
    `weathernext3-precip-gain` / `weathernext3-vs-aurora`）。出典6件すべて取得成功。
    `check_numbers.py` は照合できる数字7個すべてが出典に存在。pytest 655 passed・build 163ファイル）
  - 📌 記事の芯＝**「全体でおよそ5倍鮮明」の中身は変数によって差がある**。気温・水分は25km→5km、
    その他の地表変数は25km→10kmに上がった一方、大気の変数（上空の風速など）は前の世代と
    同じ25kmのまま。降水精度の改善幅もIMERG比60%・MRMS比30%・雨量計比10%とバラバラ
  - ⚠️ 他社比較はAnthropic・OpenAIに気象AI製品が無いため、同時期（2026-07-09）に大型更新を
    発表したMicrosoftの「Aurora 1.5」を選んだ。更新頻度（両方1時間ごと）と予測手法
    （両方アンサンブル・確率的）は同じ方向だが、公開の形（Googleは製品統合・Microsoftは
    オープンソース）は正反対。自社発表の比較指標（CRPS改善率 vs ECMWF ENSに対する勝率）は
    測り方が違うため1本の数字では比較できないと明記した
  - ⚠️ Aurora 1.5の空間解像度は発表ブログに具体的な数値の記載が無かったため、2024年の
    旧Aurora（0.1度・約11km）の数値とWeatherNext 3を直接比べることはしなかった
  - 🚨 独立評価機関「Brightband」（`brightband.com`）と Google の実験公開プラットフォーム
    「Weather Lab」（`weatherlab.deepmind.google`）は**経路遮断**（`CONNECT tunnel failed`）で
    到達できず。次にこれらのドメインを叩く行が来たら再試行対象にすること
- [x] /fugu-max-release/
  - →保管: ✅ **2026-09-14 2回目（再試行）: 公開した** → `content/tools/sakana-fugu-max.md`
    （経路遮断が解消。`sakana.ai/fugu-max-release/` は WebFetch・curl とも200。図4枚、
    出典4件すべて取得成功、`check_numbers.py` は照合できる数字14個すべてが出典に存在）
  - 2026-09-11 自動追記（major・Sakana AI「Introducing Fugu Max and Fugu Ultra v2: Orchestrating the Pareto Frontier」）
  - 完全なURL＝`https://sakana.ai/fugu-max-release/`（`tracker/sources.yml` の `sakana-blog` は
    `https://sakana.ai/feed.xml`。`news.json` の `url` はサイトルート相対なので補って読むこと）
  - **2026-09-11 1回目: 下書きを作らずに停止した。**理由＝**経路遮断（`CONNECT tunnel failed, response 403`）**。
    2026-09-14 に再試行したところ解消していた（下記）。

    | 叩いた先 | 結果 |
    |---|---|
    | `sakana.ai/fugu-max-release/` | **`CONNECT tunnel failed, response 403`** |
    | `sakana.ai/feed.xml` | **`CONNECT tunnel failed, response 403`** |
    | `sakana.ai/`（ルート） | **`CONNECT tunnel failed, response 403`** |

    - `sakana.ai` ドメイン全体がこの環境のプロキシで止まっている（3パスとも同じエラー）。
      **応答ヘッダに `cf-mitigated` は無く、先方のbot判定を示す形跡も無い**——プロキシが
      CONNECT自体を拒否しており、先方に届く前に止まっている。**経路（許可リスト）の遮断**と判定した。
    - このサイトで Sakana AI の記事は初めて（`tools/` にまだ0本）。他社比較の候補は未調査
      （①が解けてから、Anthropic・OpenAI・Google に同種の製品〈オーケストレーション／複数モデル切替〉が
      あるかを確認すること）。
- [x] https://deepmind.google/blog/introducing-gemini-3-8-live-and-3-8-live-extended-thinking/
  - →保管: ✅ **2026-09-15: 公開した** → `content/tools/gemini-3-8-live.md`
    （`deepmind.google` → `blog.google` へ302転送・到達できた。図3枚
    （`gemini38live-benchmarks` / `gemini38live-price-same` / `gemini38live-vendor-grid`）。
    出典10件すべて取得成功。`check_numbers.py` は照合できる数字16個すべてが出典に存在。
    pytest 646 passed・build 184ファイル）
  - 2026-09-15 自動追記（major・Google DeepMind「Introducing Gemini 3.8 Live and 3.8 Live Extended Thinking」）
- [x] https://sakana.ai/chat-fugumax/
  - →保管: ✅ **2026-09-16: 公開した** → `content/tools/sakana-chat-memory.md`
    （`sakana.ai` に到達（200）。図3枚（`sakana-chat-timeline` / `sakana-chat-model-lineup` /
    `sakana-chat-memory-grid`）。出典6件すべて取得成功。`check_numbers.py` は照合対象0個
    （$・%が本文に無い題材）。pytest 646 passed・build 187ファイル）
  - 2026-09-16 自動追記（major・Sakana AI「Sakana Chatをアップデート：最新モデルに刷新、メモリー機能を追加」）
  - 📌 記事の芯＝**メモリーで記憶されるのは更新以降の会話だけで、過去の会話は対象外**と発表ページに
    明記されている。Google Gemini（過去チャットの記憶が前提）・Anthropic Claude（初期設定時に過去
    チャットから生成可）と対比すると、Sakana Chatだけが過去に遡らない設計だと分かった。
  - ⚠️ **Sakana Chat自体の料金ページ（`chat.sakana.ai`）は経路遮断**（`CONNECT tunnel failed, response 403`）。
    `sakana.ai`（メインドメイン）は到達できるが、`chat.` サブドメインは別扱い。次にこのドメインを
    叩く行が来たら再試行対象にすること。API向けの `sakana.ai/fugu/`（Fugu/Fugu Ultra/Fugu Maxの
    料金FAQ）は到達できたが、Sakana Chat自体の価格とは別物のため記事では使っていない。
  - ⚠️ OpenAI（ChatGPT）のメモリー機能は、公式ニュースRSS（`openai.com/news/rss.xml`）で見出しと
    日付（2024-02-13・2026-06-04）だけ確認。本文（`openai.com`・`help.openai.com`・`chatgpt.com`）は
    今回もすべてbot判定の403で、詳細は比較に使っていない。
- [x] https://www.anthropic.com/news/life-sciences-verification-program
  - →保管: ✅ **2026-09-17: 公開した** → `content/tools/claude-life-sciences-verification.md`
    （`www.anthropic.com` に到達。図3枚（`lsvp-grant-types` / `lsvp-monitoring-shift` /
    `lsvp-vendor-grid`）。出典7件すべて取得成功。`check_numbers.py` は照合できる数字8個すべてが
    出典に存在。pytest 646 passed・build 190ファイル）
  - 2026-09-17 自動追記（major・Anthropic「Introducing the Life Sciences Verification Program」）
- [x] https://openai.com/index/introducing-chatgpt-images-2-5
  - →保管: ✅ **2026-09-20: 公開した** → `content/tools/chatgpt-images-2-5.md`
    （発表ページは今回もbot判定の403で読めず、RSS要旨1文＋developers.openai.comのモデル・料金ページ・
    ガイドで執筆。図3枚（`chatgpt-images25-price-lineage` / `chatgpt-images25-old-vs-new` /
    `chatgpt-images25-vendor-price`）。出典11件すべて取得成功。`check_numbers.py` は照合できる数字16個
    すべてが出典に存在。pytest 656 passed・build 211ファイル）
  - 📌 記事の芯＝**新モデル（Sunburst/Flare）は画質の選択肢が3→5段階に増え、出力単価も$32→$30に
    下がったが、まとめて半額になる「Batch」処理には対応していない**（両モデルのEndpoints表で
    `v1/batch: Not supported` と確認）。旧モデル（chatgpt-image-latest）が「以前ChatGPTで使われていた
    スナップショット」と明記され、後継としてSunburstが公式に名指しされていることも確認した
  - 他社比較はGoogleのNano Banana系3モデル（Lite/2/Pro）と突き合わせ、新モデルの単価はGoogleの
    下位モデル（Lite）と同額・Google自身の最上位（Pro）の1/4だった。Anthropicはモデル一覧・料金ページ
    のどちらにも画像生成モデルの記載が無いことを確認し「提供していない」と明記
  - 2026-09-20 手動追記（`news.json` では 9/8 の major。`UNREADABLE_HOSTS` のため自動追記されなかった行）
  - 🚨 発表ページは bot 判定で読めない前提（確かめるのは1回でよい）。出典は振り替える＝
    ① `openai.com/news/rss.xml` の description（1文だけ。手元実測）
    ② `developers.openai.com/api/docs/models/gpt-image-2.5-sunburst.md`・同 `gpt-image-2.5-flare.md`・
    `developers.openai.com/api/docs/pricing.md`（「Image generation models」＝Prices per 1M tokens。手元で 200 を実測）
  - 集めたい数字＝画像生成の単価を Sunburst／Flare／gpt-image-2／gpt-image-1.5 で並べる
    （手元実測: Standard の表で Sunburst・Flare・gpt-image-2 は Image 入力 $8.00／キャッシュ $2.00／出力 $30.00 で同額、
    gpt-image-1.5 は出力 $32.00）。⚠️ 同じページに **Batch の半額表**があるので混ぜない（表の見出しで区別する）
  - 比較相手＝Google の画像生成の料金（`ai.google.dev/gemini-api/docs/pricing`）。Anthropic が画像生成を
    提供していなければ「提供していない」と書く（無理に並べない）
  - ⚠️ ChatGPT 内での見え方（どのプランで使えるか等）は読めない（`chatgpt.com`・`help.openai.com` は bot 判定）。
    **API 側の数字だけで書く。**書けないことは「発表ページが読めないため確認できなかった」と明記する
- [x] https://openai.com/index/introducing-gpt-live-1-in-the-api
  - →保管: ✅ **2026-09-21: 公開した** → `content/tools/gpt-live-1-api.md`
    （発表ページは今回もbot判定の403で読めず、RSS要旨1文＋developers.openai.comのモデル・料金・
    ガイドページで執筆。図3枚（`gptlive1-architecture-grid` / `gptlive1-concurrent-tiers` /
    `gptlive1-vendor-voice-price`）。出典10件すべて取得成功。`check_numbers.py` は照合できる数字10個
    すべてが出典に存在。pytest 657 passed・build 214ファイル）
  - 📌 記事の芯＝**GPT-Live 1は「音声」と「頭脳」を分けた新しいアーキテクチャで、$0.05/分の
    音声セッション料金にはバックエンドのモデル代が含まれない**（Realtime APIは1モデルで完結する
    別エンドポイント。相互に差し替え不可）。電話（SIP・G.711）に公式対応、同時セッションはTierで
    25〜500。Free プランは対象外
  - 他社比較はGemini 3.8 Liveの分あたり音声単価（入力$0.005・出力$0.018）と突き合わせ、GPT-Live 1の
    セッション料金だけで既にどちらより高いことを確認。Anthropicは音声対話モデルの記載なし
    （platform.claude.comを今回改めて確認・fontクラス名以外にvoiceの言及なし）
  - ⚠️ 「custom voices」はRSS要旨にあるが、GPT-Live 1自身のガイドに説明が無く、見つかったのは
    Realtime向け別ガイドの「承認された顧客のみ」の記載。GPT-Live 1に同じ制限が及ぶかは確認できず、
    記事にもそう明記した
  - 2026-09-20 手動追記（`news.json` では 9/10 の minor。8/5 の `[!]` 行（ChatGPT 側の GPT-Live）とは別＝API 提供の発表）
