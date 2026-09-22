# 深掘り記事の待ち行列

要約を読んで「もっと詳しく知りたい」と思ったものの**URLを1行足す**だけ。
ルーティン（`ai-tsukaikata-deepdive`）が拾って、出典を実際に読んでから記事を書く。

ファイル名が `_` で始まるのでビルド対象外。サイトには出ない。

## 書き方

`- [ ] https://...` の形で足す。処理が終わったら routine が `- [x]` に変えて、
下に生成した下書きのファイル名を書く。**消さない**（同じものを二度書かないため）。

スマホからでも足せる: GitHub でこのファイルを開く → 鉛筆アイコン → 行を足す → Commit changes。

📦 `- →保管:` の行は、機械回転（毎日04:43 の rotate.yml）が済んだ項目の詳細を保管庫 `_*_archive.md` へ移した印。**行は重複防止の台帳なので消さない・読み直す必要もない。**

## 再試行の決まり（2026-09-14・オーナー承認）

未処理（`- [ ]`）が0件の朝だけ、`- [!]` を**1件**再試行する。選び方:

1. 停止理由に**経路遮断**（`CONNECT tunnel failed` / `EGRESS_BLOCKED` / 許可リスト）が書かれている行だけ。
   **先方の bot 判定**（`cf-mitigated: challenge` の403）だけの行は対象外
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
  - **末尾のスラッシュを必ず付けること。**無いと 308 リダイレクトになる（付ければ 200・約505KB を実測）。
  - 比較相手＝Google の Gemini Live（`ai.google.dev` / `deepmind.google` は到達可）と、
    OpenAI の他の音声モデル（`developers.openai.com/api/docs/models` と `/api/docs/pricing` は到達可）。
    **Anthropic に同等の機能が無ければ「提供していない」と書けばよい。**無理に並べない。
  - 集めたい数字＝**応答までの待ち時間・料金・対応言語・使えるモデル**。
    ⚠️ 待ち時間は測り方で大きく変わる。条件が書かれていなければ「条件は公表されていない」と明記する。
  - ⚠️ `openai.com/api/pricing/` は先方が403を返す。料金は `developers.openai.com/api/docs/pricing` を見ること。
  - **2026-08-05 1回目: 下書きを作らずに停止した。**発表ページの本文が読めないため。

    **① 何が起きたか＝`openai.com` の HTMLページが全部 Cloudflare の challenge で 403 になった**

    | 叩いた先 | 結果 |
    |---|---|
    | `openai.com/index/continuous-voice-interaction-with-gpt-live/` | **403**（9,848バイトの challenge ページ） |
    | `openai.com/index/continuous-voice-interaction-with-gpt-live`（スラッシュ無し） | **403**（308にすらならない） |
    | `openai.com/` / `openai.com/news/` / `openai.com/index/gpt-5-6/` | **403**（＝この記事だけの問題ではない） |
    | `openai.com/news/rss.xml` | **200**・約674KB |
    | `developers.openai.com/api/docs/pricing` / `/api/docs/models` | **200** |

    - 応答ヘッダに **`cf-mitigated: challenge`** と `server: cloudflare`。⚠️**これは先方のbot判定であって、
      経路（プロキシの許可リスト）の遮断ではない。**許可リストに足しても直らない。切り分けの根拠＝同じ
      `openai.com` の RSS が 200 で返っていること。前回の `CONNECT tunnel failed, response 403` とは別物。
    - 末尾スラッシュ有り／無しで各3回・20秒間隔、WebFetch でも同じ 403。**UA偽装での迂回はしない**
      （x.ai と同じ方針。SESSION_HANDOFF「x.ai は403でbotブロック」節）。
    - **2026-08-04 には同じURLが 200・505KB で取れていた。**先方の設定が変わった可能性が高い。
      **時間帯やegressのIP評価で戻ることがあるので、次回そのまま再実行する価値はある。**

    **② RSS から分かったこと（本文ではないので記事には使えない）**

    `openai.com/news/rss.xml` に該当の item はある。ただし **`<description>` の1文だけで本文は入っていない**（item全体で645バイト）。

    - 実際のタイトルは **"How we built a realtime system for responsive voice AI in six months"**
      （待ち行列のURLから想像していた見出しとは違う）。カテゴリは `Engineering`
    - 公開日 **2026-08-03 07:00 GMT**
    - description 全文＝`GPT-Live enables continuous voice interaction with AI, using a turnless speech model and low-latency architecture for faster, more natural conversations.`
    - → **「待ち時間」の数値と測定条件、対応言語は、この1文からは1つも取れない。**ここが記事の主題なので書けない。

    **③ 到達できた一次情報（`developers.openai.com` 実測・次回はここから埋められる）**

    ⚠️ **記事にはまだ使っていない。**書くときは必ずページを開き直して、その数字がそこに在ることを確かめること。

    - `/api/docs/models` に **`gpt-live-transcribe` が実在**（＝GPT-Live は製品名として docs 側にも出ている）。
      ほかに `gpt-realtime-2.1` / `-2.1-mini` / `gpt-realtime-2` / `gpt-realtime-translate` / `gpt-realtime-1.5`。
      `gpt-realtime-mini` は Deprecated 表示。**コンテキスト長・学習データの締め切りは、どのモデルも記載が無い**
    - `/api/docs/pricing`（100万トークンあたり）＝ `gpt-realtime-2.1`: テキスト入力 $4.00 / 音声入力 $32.00 /
      テキスト出力 $24.00。`gpt-realtime-2.1-mini`: $0.60 / $10.00 / $2.40。
      **分あたりの課金のものもある**＝ `gpt-realtime-translate` $0.034/分、`gpt-live-transcribe` $0.017/分、
      `gpt-transcribe` $0.0045/分。**トークン課金と分課金が混在するので、1本の表に並べると壊れる**
    - `/api/docs/guides/realtime` は 200 で読める。接続方式は WebRTC / WebSocket / SIP の3つ。
      ⚠️ **待ち時間の数値も対応言語の一覧も、このガイドには書かれていない**（"low latency" という言葉だけ）
    - → **比較相手の Gemini Live 側（`ai.google.dev` / `deepmind.google`）はまだ叩いていない。**
      発表本文が読めない以上、そちらだけ集めても記事の軸が立たないため。

- [x] https://openrouter.ai/qwen/qwen3.8-max
  - →保管: **2026-08-20 2回目（再試行）: 公開した** → `content/tools/qwen3-8-max.m

- [x] https://www.anthropic.com/news/claude-opus-5
  - →保管: 2026-08-04 1回目: `Host not in allowlist: www.anthropic.com` の

- [!] https://openai.com/index/accelerating-defenders-with-gpt-daybreak-legacy
  - 2026-08-10 自動追記（major・OpenAI「Introducing GPT-Daybreak to accelerate defenders」）
  - **2026-08-10 1回目: 下書きを作らずに停止した。**理由は2つあり、どちらも単独で停止の理由になる。

    **① `openai.com` の HTMLページは今日も全部 403（Cloudflare の bot 判定）**

    | 叩いた先 | 結果 |
    |---|---|
    | `openai.com/index/accelerating-defenders-with-gpt-daybreak-legacy/`（スラッシュ有り） | **403**・9,863バイト |
    | 同（スラッシュ無し） | **403**・9,860バイト |
    | `openai.com/index/expanding-daybreak-as-the-cyber-defense-window-narrows` | **403**・9,881バイト |
    | `openai.com/news/` | **403**・9,652バイト |
    | `openai.com/news/rss.xml` | **200**・683,292バイト（1,123 item） |
    | `developers.openai.com/api/docs/models` | **200**・343,339バイト |
    | `developers.openai.com/api/docs/pricing` | **200**・542,564バイト |

    - 応答ヘッダは前回と同じ **`cf-mitigated: challenge`** ＋ `server: cloudflare`。⚠️**先方のbot判定であって
      経路（許可リスト）の遮断ではない。許可リストに足しても直らない。**切り分けの根拠＝同じ `openai.com` の
      RSS が 200 で返り、`developers.openai.com` も 200 で返っていること。**UA偽装での迂回はしない。**
    - WebFetch でも同じく HTTP 403。**2026-08-05 の GPT-Live の件から5日たっても戻っていない**
      （＝「時間帯やegressのIP評価で戻る」ことは、少なくとも2回連続で起きなかった）。
    - 💡 **次に `openai.com/index/...` のURLがキューに入ったときは、まずここを見ること。**先方の判定が続く限り、
      OpenAI の発表本文はこの環境から読めない。読めるのは RSS の `<description>` 1文と `developers.openai.com` だけ。

    **② そもそも、このURLは今のRSSに存在しない（ページが消えたか改名された可能性が高い）**

    - 現在の `openai.com/news/rss.xml`（1,123 item）に `accelerating-defenders-with-gpt-daybreak-legacy` は**1件も無い**。
      スラッグの末尾が `-legacy` なので、**改名前の旧URLが一時的にフィードに出ていた**と考えるのが自然。
    - トラッカーの記録（`data/tracker/news.json`）＝ `first_seen` 2026-08-10T17:11Z ／ `published` 2026-08-05T10:00Z ／
      title「Introducing GPT-Daybreak to accelerate defenders」／ importance major。
    - **今のフィードにある Daybreak 関連（次に狙うならこちら）**
      - 「Expanding Daybreak as the Cyber Defense Window Narrows」Mon, 10 Aug 2026 10:00 GMT
        → `openai.com/index/expanding-daybreak-as-the-cyber-defense-window-narrows`
        description＝`Meet GPT-5.6-Cyber, OpenAI's cybersecurity-specific model available through Daybreak Red for authorized vulnerability research, exploit validation, and security testing.`
      - 「Putting frontier cyber models in more trusted hands」Mon, 10 Aug 2026 10:00 GMT
        （⚠️ トラッカーは `published` 2026-08-05 で記録していた。**フィード側の pubDate が動いている**）
      - 「Responding to the next frontier of critical cyber capabilities」Fri, 07 Aug 2026 15:20 GMT
      - 「Daybreak: Tools for securing every organization in the world」「Patch the Planet」いずれも 2026-06-22
    - ⚠️ ただし後継URLも `openai.com` なので**①のbot判定で本文は読めない**。①が解けるまで、この題材は書けない。

    **③ 到達できた一次情報（`developers.openai.com` 実測・生の行をそのまま写す）**

    ⚠️ **記事には使っていない。**書くときは必ずページを開き直して、その数字がそこに在ることを確かめること。

    - `/api/docs/models` の Specialized models に **OpenAI Daybreak（"Frontier cyber models for defenders"）**の節が実在。
      中身は3つで、**説明文1行だけ。コンテキスト長・最大出力・学習データの締め切りはどれも記載が無い**。
      - `GPT-5.6 Cyber` = "Our most advanced cybersecurity model for authorized vulnerability research and security testing."
      - `Daybreak Red` = "An alias for advanced cybersecurity models for authorized vulnerability research and security testing."
      - `Daybreak Blue` = "An alias for frontier general-purpose models with safeguards for defensive cybersecurity work."
    - `/api/docs/pricing` に **「Cyber models / Our latest Daybreak models. Prices per 1M tokens.」の表**が実在。
      見出しは Short context / Long context の8列（Input / Cached input / Cache writes / Output ×2）。生の行:
      - `gpt-5.6-sol   $5.00 $0.50 $6.25 $30.00   $10.00 $1.00 $12.50 $45.00`
      - `gpt-5.6-cyber $12.50 $1.25 $15.625 $75.00   - - - -` ← **長い入力の4列は全部ハイフン**
    - → 料金と位置づけだけなら書ける。**が、発表本文（何ができるようになったか・誰に提供されるか・制限）が
      読めないので、記事の軸が立たない。**二次情報で埋めるくらいなら書かない（GPT-Live と同じ判断）。

- [x] https://openai.com/index/daybreak-models-are-now-available-on-aws
  - →保管: ✅ **2026-08-21 2回目（再試行）: 公開した** → `content/tools/daybreak-on

- [x] https://deepmind.google/blog/introducing-gemini-3-7-flash/
  - →保管: 2026-08-13 自動追記（major・Google DeepMind「Introducing Gemini 3.7

- [x] https://tech.preferred.jp/ja/blog/introducing-matlantis-pfp-v9/
  - →保管: 2026-08-17 自動追記（major・Preferred Networks「PFP v9のご紹介: MLIP Ar

- [!] https://openai.com/index/chatgpt-for-teens
  - 2026-08-18 自動追記（major・OpenAI「Introducing ChatGPT for Teens: Built for learning, backed by protections」）
  - **2026-08-18 1回目: 下書きを作らずに停止した。**発表本文に到達できないため。
    ⚠️ このURLは現在のRSSに実在する（消えたのではなく、読めないだけ）。

    **① `openai.com` の HTMLページは今日も403（Cloudflare の bot 判定）。4回連続で戻っていない**

    | 叩いた先 | 結果 |
    |---|---|
    | `openai.com/index/chatgpt-for-teens/`（スラッシュ有り） | **403**・9,731バイト |
    | 同（スラッシュ無し） | **403**・9,728バイト |
    | 同（WebFetch） | **HTTP 403**・本文なし |
    | 同（`?x=1` 付き＝キャッシュ回避） | **403**・9,758バイト |
    | `openai.com/ja-JP/index/chatgpt-for-teens/`（日本語版） | **403**・9,770バイト |
    | `openai.com/policies/usage-policies/` | **403**・9,731バイト |
    | **`help.openai.com/en/`**（ヘルプセンター・今回はじめて試した） | **403**・9,672バイト |
    | `help.openai.com/en/articles/8313398-chatgpt-for-teens` | **403**・9,796バイト |
    | `openai.com/news/rss.xml` | **200**・691,220バイト（1,137 item） |
    | `developers.openai.com/api/docs/models` | **200**・345,216バイト |
    | `developers.openai.com/api/docs/pricing` | **200**・544,675バイト |

    - 応答ヘッダは毎回と同じ **`cf-mitigated: challenge`** ＋ `server: cloudflare`。⚠️**先方のbot判定であって
      経路（許可リスト）の遮断ではない。許可リストに足しても直らない。**切り分けの根拠＝同じ `openai.com` の
      RSS が 200 で返っていること。**UA偽装での迂回はしない。**
    - 💡 **08-05（GPT-Live）→ 08-10（Daybreak legacy）→ 08-11（AWS）→ 08-18（本件）で4回連続403。**
      13日たっても戻っていない。**`openai.com/index/...` が来たら、まずここを読むこと。**
    - ⚠️ **`help.openai.com` も同じ判定だった**（今回の新しい知見）。ヘルプ記事から機能の詳細を埋める逃げ道も
      塞がっている。⚠️ `chatgpt.com` は別種で **`CONNECT tunnel failed, response 403` ＝経路の遮断**
      （許可リストに足せば直る種類）だが、製品ページに仕様の記載は薄いので優先度は低い。

    **② 🆕 到達できる OpenAI 一次情報が1つ増えた＝`model-spec.openai.com`（200・今回はじめて確認）**

    - `model-spec.openai.com/` → `2026-08-18.html` へ転送（**本件の発表と同じ日付**）。2,662,295バイト・素のHTMLで読める。
      ⚠️ 転送は `<meta http-equiv="refresh">` なので `curl -L` では追えない。**`2026-08-18.html` を直接叩くこと。**
    - 中身に **「Under-18 Principles」「Prioritize safety for teens」の節が実在**（`teen` 15回・`minor` 21回・
      `parent` 35回）。**未成年に対してモデルがどう振る舞うと定めているか**は、ここから一次情報として引ける。
    - ⚠️ **ただしこれは「モデルの振る舞いの規定」であって、製品「ChatGPT for Teens」の発表本文ではない。**
      対象年齢・提供国・料金・保護者向け機能の中身・提供開始日は Model Spec には書かれていない。
      **記事の軸（何が新しくなったのか）はこれだけでは立たない**ので、今回は書かなかった。

    **③ RSS から分かったこと（本文ではないので記事には使えない）**

    - タイトル＝**"Introducing ChatGPT for Teens: Built for learning, backed by protections"**。カテゴリは `Product`
    - 公開日 **2026-08-18 11:00 GMT**
    - description 全文＝`ChatGPT for Teens helps teens learn, think critically, and use AI with confidence, with stronger built-in protections, healthy-use features, and additional controls for parents.`
    - → **対象年齢・提供国・料金・保護者が何をできるのかは、この1文から1つも取れない。**
    - 💡 **同じ題材の過去記事がRSSに8本ある**（①が解けたら、経緯をたどる記事にできる材料）:
      - `why-teens-deserve-access-safe-ai`（2026-07-16 16:00 GMT・Safety）
      - `teen-safety-policies-gpt-oss-safeguard`（2026-03-24 11:00 GMT・Safety）
      - **`japan-teen-safety-blueprint`（2026-03-17 10:00 GMT・Safety）＝日本向け。日本の読者には効く**
      - `ai-literacy-resources-for-teens-and-parents` / `updating-model-spec-with-teen-protections`（ともに 2025-12-18 11:00 GMT）
      - `introducing-the-teen-safety-blueprint`（2025-11-06・Company）／`teen-safety-freedom-and-privacy`（2025-09-16・Safety）
      - ⚠️ **全部 `openai.com/index/...` なので①で読めない。**description の1文ずつしか取れない。

    **④ 書くとしたときの注意（①が解けた後の話）**

    - 題材が**料金でも性能でもない**（安全機能・保護者向けの管理）。**このサイトの料金比較の型はそのまま使えない。**
      比較軸になるのは「対象年齢／保護者ができること／提供国／追加料金の有無」。
    - 比較相手の到達性（今回確認）＝ **`www.anthropic.com` は 200**・**`ai.google.dev` は 200**。
      Google の Family Link / Gemini の年齢制限、Anthropic の利用規約の年齢要件は読める見込み。
      ⚠️ **同等の機能が無ければ「提供していない」と書けばよい。無理に並べない。**
    - 読者（自動化したい非エンジニアの会社員）から遠い題材なので、**切り口を先に決めること。**
      「子どもに使わせるとき、会社で使うのと何が違うか」なら近づく。

- [!] https://openai.com/index/introducing-ai-futures
  - 🔒 **2026-08-21 見送りで確定（オーナー判断）。再試行しない。**担当の停止判断が正しいと人が検証して確認した。`- [x]` にしないのは担当の指示どおり（記事は存在しないため）。⚠️ **この節は消さない**＝403の切り分け表は「次に `openai.com/index/...` が来たとき最初に読む資料」として生きている。
  - **人が独立に確かめたこと（2026-08-21）**:
    - 403は**6回連続**になった（WebFetchでも同じ）。`cf-mitigated: challenge` ＝先方のbot判定で、同じ `openai.com` の RSS が200で返るのが切り分けの根拠。許可リストでは直らない
    - RSS に全文は無い（description 1文のみ）。**一次情報は読めないままである**ことを再確認した
    - 🚨 **決め手は3つ目＝出典の質**。中身（Dean Ball／Strategic Futures／統治と自由が主題）は検索では取れるが、**どれも「私が読んでいない記事の、他人による要約」**。二次情報だけで「OpenAIはこう言っている」と書くのは、このサイトが一番やってはいけない形。
      担当の理由②（数字が無い）より、**こちらのほうが強い停止理由**だった
  - 📌 **題材として死んではいない**＝RSSのカテゴリ `AI Futures` は全1,143件中この1件だけ。今後の研究・論文はここに積まれるので、中身のある投稿が出たら別項目として拾えばよい
  - 2026-08-20 自動追記（major・OpenAI「Introducing AI Futures」）
  - **2026-08-20 1回目: 記事を書かずに停止した。**理由は2つあり、どちらも単独で停止の理由になる。

    **① `openai.com` の HTMLページは今日も403（Cloudflare の bot 判定）。5回連続で戻っていない**

    | 叩いた先 | 結果 |
    |---|---|
    | `openai.com/index/introducing-ai-futures/`（スラッシュ有り） | **403**・9,746バイト |
    | 同（スラッシュ無し） | **403**・9,743バイト |
    | 同（`?x=1` 付き＝キャッシュ回避） | **403**・9,794バイト |
    | `openai.com/ja-JP/index/introducing-ai-futures/`（日本語版） | **403**・9,785バイト |
    | `openai.com/news/` | **403**・9,652バイト |
    | `openai.com/news/rss.xml` | **200**・694,646バイト（1,143 item） |
    | `developers.openai.com/api/docs/models` | **200**・345,602バイト |
    | `model-spec.openai.com/2026-08-18.html` | **200**・2,662,295バイト |

    - 応答ヘッダは毎回と同じ **`cf-mitigated: challenge`** ＋ `server: cloudflare`。⚠️**先方のbot判定であって
      経路（許可リスト）の遮断ではない。許可リストに足しても直らない。**切り分けの根拠＝同じ `openai.com` の
      RSS が 200 で返り、`developers.openai.com` も `model-spec.openai.com` も 200 で返っていること。
      **UA偽装での迂回はしない。**
    - 💡 **08-05（GPT-Live）→ 08-10（Daybreak legacy）→ 08-11（AWS）→ 08-18（ChatGPT for Teens）→ 08-20（本件）で
      5回連続403。**15日たっても戻っていない。**`openai.com/index/...` が来たら、まずここを読むこと。**

    **② そもそも題材に数字が1つも無い。①が解けても、このサイトの型では書けない可能性が高い**

    - RSS の item は実在する。カテゴリは **`AI Futures`**（この1件だけ。RSS 全1,143 item 中、同カテゴリは他に無し）。
      公開日 **2026-08-20 07:00 GMT**
    - description 全文＝`Introducing AI Futures, a new OpenAI blog exploring how transformative AI could reshape
      power, governance, the economy, and individual freedom.`
    - → **これは「新しいブログを始めます」という告知**であって、モデルでも料金でも機能でもない。
      `developers.openai.com` に載る種類の数字（料金・コンテキスト長・ベンチマーク）は**構造的に存在しない**。
      ①が解けても、書けるのは「OpenAI が統治・経済・自由についてのブログを始めた」の1行だけ。
      **深掘り記事の型（何が変わったか／前のモデルとの違い／他社との比較）に当てはまらない。**
    - 💡 **次にこの行を見る人へ**＝①が解けたら、まず本文を読んで「比較できる数字があるか」を確かめること。
      無ければ `- [x]` にせず、**題材として見送ったと明記して閉じる**のが正しい。

- [!] https://openai.com/index/introducing-admin-plugin
  - 2026-08-25 自動追記（major・OpenAI「Introducing the Admin plugin for ChatGPT Work and Codex」）
  - **2026-08-25 1回目: 下書きを作らずに停止した。**理由は2つあり、どちらも単独で停止の理由になる。

    **① `openai.com` の発表ページは今日も403（Cloudflare の bot 判定）。6回連続で戻っていない**

    | 叩いた先 | 結果 |
    |---|---|
    | `openai.com/index/introducing-admin-plugin`（スラッシュ無し） | **403** |
    | 同（スラッシュ有り） | **403** |
    | `openai.com/news/rss.xml` | **200**（該当item実在） |

    - **今回はじめて `help.openai.com` の当該記事も同じ判定だった**＝`help.openai.com/en/articles/20001275-chatgpt-work-and-codex`
      （ChatGPT Work and Codex の解説記事・Web検索で見つけた）も **403**。2026-08-18 の「ChatGPT for Teens」のときの
      `help.openai.com` 403と一致し、たまたまではないことが濃くなった。**先方のbot判定であって経路（許可リスト）の
      遮断ではない。**切り分けの根拠＝同じ `openai.com` の RSS が200で返っていること。**UA偽装での迂回はしない。**
    - 💡 08-05→08-10→08-11→08-18→08-20→08-25 で6回連続403。**`openai.com/index/...` が来たら、まずここを読むこと。**

    **② 🆕 新しい発見＝`developers.openai.com/codex/enterprise/admin-setup` は `learn.chatgpt.com` へ308転送されるが、
    `learn.chatgpt.com` はこの環境の許可リストに無い（`EGRESS_BLOCKED`）**

    - これは①とは**別種の遮断**（`cf-mitigated` の応答ヘッダ付き403ではなく、明確な `EGRESS_BLOCKED` エラー）。
      **経路（許可リスト）の遮断＝ドメインを足せば直る可能性がある種類。**次に `learn.chatgpt.com` を叩く行が
      来たら、まずここに記録した「経路遮断」を見て再試行の対象にすること。
    - Web検索では `help.openai.com/en/articles/11509118-admin-controls-security-and-compliance-for-plugins-and-apps`
      や `developers.openai.com/codex/plugins` 等の関連ページも見つかったが、**要約だけを信じて数字を書くことはしない**
      （SESSION_HANDOFF「要約は書いてあることを消すこともある」の教訓）。生ページを開けなければ書かない。
    - RSS の description は `Use the Admin plugin for ChatGPT Work and Codex to analyze workspace usage, manage
      members and permissions, adjust limits, and act on admin requests.` の1文のみ。**対象プラン・提供時期・
      具体的にできることの範囲は、この1文からは1つも取れない。**
    - ⚠️ そもそも題材が**ワークスペース管理機能の告知**で、モデルでも料金でもない。数字（料金・性能）による
      比較という記事の型に、①②が解けても当てはまらない可能性が高い（2026-08-20「AI Futures」と同じ構造）。
      次にこの行を見る人へ＝①②が解けたら、まず本文を読んで「比較できる数字があるか」を確かめること。

  - **2026-08-30 2回目（再試行）: まだ読めない。**未処理（`- [ ]`）が0件だったため、停止理由が「経路遮断」だった
    本行を上から見て再試行した。結果は**両方とも変わらず**:
    - `openai.com/index/introducing-admin-plugin`（スラッシュ有り／無し） → **403**（変わらず、`cf-mitigated`
      の bot 判定。8/25 から数えて7回連続）
    - `learn.chatgpt.com/` → **`CONNECT tunnel failed, response 403`**（変わらず、経路＝許可リストの遮断。
      `developers.openai.com/codex/enterprise/admin-setup` の308転送先は今日も届かない）
    - `help.openai.com/en/articles/20001275-chatgpt-work-and-codex` → **403**（変わらず、bot 判定）
    - → **①②とも解けていない。**引き続き `- [!]` のまま据え置く。次に見る人へ＝`learn.chatgpt.com` が
      許可リストに追加されたら、まずここを再試行すること。①（openai.com本体・help.openai.com）はbot判定なので
      許可リストを足しても直らない点は変わらない。

  - **2026-09-08 3回目（再試行）: まだ読めない。**未処理（`- [ ]`）が0件だったため、停止理由が「経路遮断」だった
    本行を上から見て再試行した。結果は**両方とも変わらず**:
    - `openai.com/index/introducing-admin-plugin` → **403**（変わらず、`cf-mitigated: challenge` の bot 判定）
    - `learn.chatgpt.com/` → **`CONNECT tunnel failed, response 403`**（変わらず、経路＝許可リストの遮断）
    - `developers.openai.com/codex/enterprise/admin-setup` → **200 → 308転送**（転送先は今日も
      `learn.chatgpt.com/docs/enterprise/admin-setup`。転送元は到達できるが、転送先が許可リストに無いので
      本文には届かない）
    - `help.openai.com/en/articles/20001275-chatgpt-work-and-codex` → **403**（変わらず、bot 判定）
    - → **①②とも解けていない。**引き続き `- [!]` のまま据え置く。次に見る人へ＝`learn.chatgpt.com` が
      許可リストに追加されたら、まずここを再試行すること。①（openai.com本体・help.openai.com）はbot判定なので
      許可リストを足しても直らない点は変わらない。

  - **2026-09-09 4回目（再試行）: まだ読めない。**未処理（`- [ ]`）が0件だったため、停止理由が「経路遮断」だった
    本行を上から見て再試行した。結果は**引き続き変わらず**:
    - `openai.com/index/introducing-admin-plugin` → **403**（変わらず、`cf-mitigated: challenge` の bot 判定）
    - `learn.chatgpt.com/` → **`CONNECT tunnel failed, response 403`**（変わらず、経路＝許可リストの遮断。
      エージェントプロキシのログでも `connect_rejected (organization policy)` と明記されている）
    - `developers.openai.com/codex/enterprise/admin-setup` → **200 → 308転送**（転送先は今日も
      `learn.chatgpt.com/docs/enterprise/admin-setup`。転送元・`developers.openai.com/api/docs/models` は
      到達できるが、転送先が許可リストに無いので本文には届かない）
    - `help.openai.com/en/articles/20001275-chatgpt-work-and-codex` → **403**（変わらず、bot 判定）
    - → **①②とも解けていない（8/25初回から15日・4回連続で同じ結果）。**引き続き `- [!]` のまま据え置く。
      次に見る人へ＝`learn.chatgpt.com` が許可リストに追加されたら、まずここを再試行すること。
      ①（openai.com本体・help.openai.com）はbot判定なので許可リストを足しても直らない点は変わらない。

  - **2026-09-10 5回目（再試行）: まだ読めない。**未処理（`- [ ]`）が0件だったため、停止理由が「経路遮断」だった
    本行を上から見て再試行した。結果は**引き続き変わらず**:
    - `openai.com/index/introducing-admin-plugin` → **403**（変わらず、`cf-mitigated: challenge` の bot 判定）
    - `learn.chatgpt.com/`・`learn.chatgpt.com/docs/enterprise/admin-setup` → **`CONNECT tunnel failed, response 403`**
      （変わらず、経路＝許可リストの遮断。エージェントプロキシのログでも `connect_rejected (organization policy)` と明記）
    - `developers.openai.com/codex/enterprise/admin-setup` → **308転送**（転送先は今日も
      `learn.chatgpt.com/docs/enterprise/admin-setup`。転送元は到達できるが、転送先が許可リストに無いので
      本文には届かない）
    - `help.openai.com/en/articles/20001275-chatgpt-work-and-codex` → **403**（変わらず、bot 判定）
    - → **①②とも解けていない（8/25初回から16日・5回連続で同じ結果）。**引き続き `- [!]` のまま据え置く。
      次に見る人へ＝`learn.chatgpt.com` が許可リストに追加されたら、まずここを再試行すること。
      ①（openai.com本体・help.openai.com）はbot判定なので許可リストを足しても直らない点は変わらない。
      💡 **5回連続で経路遮断だけが変わらず残っている。**このドメインの許可リスト追加は自動では起きないので、
      オーナー側での対応（環境のNetwork accessに `learn.chatgpt.com` を追加）を待つ状態になっている。

  - **2026-09-12 6回目（再試行）: まだ読めない。**未処理（`- [ ]`）が0件だったため、停止理由が「経路遮断」だった
    本行を上から見て再試行した。結果は**引き続き変わらず**:
    - `openai.com/index/introducing-admin-plugin` → **403**（変わらず、`cf-mitigated: challenge` の bot 判定）
    - `learn.chatgpt.com/`・`learn.chatgpt.com/docs/enterprise/admin-setup` → **`CONNECT tunnel failed, response 403`**
      （変わらず、経路＝許可リストの遮断）
    - `developers.openai.com/codex/enterprise/admin-setup` → **308転送**（転送先は今日も
      `learn.chatgpt.com/docs/enterprise/admin-setup`。転送元は到達できるが、転送先が許可リストに無いので
      本文には届かない）
    - `help.openai.com/en/articles/20001275-chatgpt-work-and-codex` → **403**（変わらず、bot 判定）
    - → **①②とも解けていない（8/25初回から18日・6回連続で同じ結果）。**引き続き `- [!]` のまま据え置く。
      次に見る人へ＝`learn.chatgpt.com` が許可リストに追加されたら、まずここを再試行すること。
      ①（openai.com本体・help.openai.com）はbot判定なので許可リストを足しても直らない点は変わらない。

  - **2026-09-13 7回目（再試行）: まだ読めない。**未処理（`- [ ]`）が0件だったため、停止理由が「経路遮断」だった
    本行を上から見て再試行した。結果は**引き続き変わらず**:
    - `openai.com/index/introducing-admin-plugin` → **403**（変わらず、bot 判定）
    - `learn.chatgpt.com/docs/enterprise/admin-setup` → **`EGRESS_BLOCKED`**（変わらず、経路＝許可リストの遮断。
      プロキシが CONNECT 自体を拒否）
    - `developers.openai.com/codex/enterprise/admin-setup` → **308転送**（転送先は今日も
      `learn.chatgpt.com/docs/enterprise/admin-setup`。転送元は到達できるが、転送先が許可リストに無いので
      本文には届かない）
    - `help.openai.com/en/articles/20001275-chatgpt-work-and-codex` → **403**（変わらず、bot 判定）
    - → **①②とも解けていない（8/25初回から19日・7回連続で同じ結果）。**引き続き `- [!]` のまま据え置く。
      次に見る人へ＝`learn.chatgpt.com` が許可リストに追加されたら、まずここを再試行すること。
      ①（openai.com本体・help.openai.com）はbot判定なので許可リストを足しても直らない点は変わらない。
  - 🔁 **2026-09-14 打ち止め（1回目＋再試行6回＝7回で変化なし・オーナー承認）。**以後、毎朝の再試行の対象にしない。
    ① `openai.com` 本体は bot 判定＝直らない。② `learn.chatgpt.com` は経路遮断＝オーナーが許可リストに足したと
    この行に書き足した日にだけ、もう1回試す（上の「再試行の決まり」4）

- [!] https://openai.com/index/introducing-intelligence-age
  - 2026-08-26 自動追記（major・OpenAI「Introducing Intelligence Age」）
  - **2026-08-27 1回目: 記事を書かずに停止した。**理由は2つあり、どちらも単独で停止の理由になる。

    **① `openai.com` の発表ページは今日も403（Cloudflare の bot 判定）。7回連続で戻っていない**

    | 叩いた先 | 結果 |
    |---|---|
    | `openai.com/index/introducing-intelligence-age/`（スラッシュ有り） | **403**・9,785バイト |
    | 同（スラッシュ無し） | **403** |
    | `openai.com/index/introducing-ai-futures`（旧名と思われるURL） | **403** |
    | `openai.com/news/rss.xml` | **200**・該当item実在 |

    - 応答ヘッダは毎回と同じ **`cf-mitigated: challenge`** ＋ `server: cloudflare`。**先方のbot判定であって
      経路（許可リスト）の遮断ではない。許可リストに足しても直らない。**切り分けの根拠＝同じ `openai.com` の
      RSS が200で返っていること。**UA偽装での迂回はしない。**
    - 💡 08-05→08-10→08-11→08-18→08-20→08-25→08-27 で7回連続403。**`openai.com/index/...` が来たら、
      まずここを読むこと。**

    **② 🆕 これは2026-08-20に見送り済みの「AI Futures」の告知と、ほぼ同一の内容（改名後の可能性が高い）**

    - RSS の description 全文＝`Introducing Intelligence Age, a new OpenAI blog exploring how transformative
      AI could reshape power, governance, the economy, and individual freedom.`
    - これは **08-20 の「Introducing AI Futures」の description と一字一句同じ文面**（ブログ名の部分だけ
      「AI Futures」→「Intelligence Age」に変わっている）。公開日も同じ **2026-08-20 07:00 GMT**。
      カテゴリも `AI Futures` → `Intelligence Age` に変わっている。
    - → **同じ新ブログ立ち上げの告知が、名前を変えて再度キューに入ってきたと考えるのが自然。**
      「AI Futures」の行はオーナーが 2026-08-21 に**独立検証のうえ見送りで確定・再試行しない**と決めている
      （理由＝①bot判定で本文が読めない ②数字が1つも無い告知 ③二次情報だけで書くのはこのサイトが
      一番やってはいけない形）。この3点はどれも今回のURLにそのまま当てはまる。
    - 💡 **次にこの行を見る人へ**＝オーナーに「AI Futures と同一の告知が改名して再度来た」と一言確認を
      仰いでから、`- [x]`（見送り確定）にするか判断するのがよい。担当の判断だけで確定にはしない
      （AI Futures のときも人間の確認を経て確定させた前例に合わせる）。

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
- [ ] https://sakana.ai/marlin-update/
  - 2026-09-20 手動追記（`news.json` では 9/15 の minor。`sakana.ai` は 9/14・9/16 にクラウドから到達できている）
  - 集めたい数字＝発表ページ（最大8時間・数十ページ・今年6月公開）と、料金ページ `sakana.ai/marlin/`
    （手元実測 200: 1実行100クレジット・追加クレジット ¥98／¥90／¥85・毎月2,000／6,000クレジット付与・
    プランは4つ・無料トライアルあり）。⚠️ `chat.sakana.ai` は経路遮断の前例あり＝叩かない
  - 記事の芯＝「AIに調べさせて報告書にする」型の道具が、**読む側の手間**（裏取り・スライド化）まで
    面倒を見るようになった話。読者に近い使い方＝会議前の調査を任せる
  - 比較相手＝OpenAI の deep research（`developers.openai.com` の該当ガイド）・Google の Deep Research。
    読めなければ「比較できなかった」と書く（無理に並べない）
  - 📌 この minor が記事になれば、`sources.yml` の `sakana-blog` に `deepdive_minor: true` を付ける根拠になる
    （CLAUDE.md「付けるのは minor が実際に記事になった会社だけ」）

## 処理済み

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
