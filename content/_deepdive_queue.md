# 深掘り記事の待ち行列

要約を読んで「もっと詳しく知りたい」と思ったものの**URLを1行足す**だけ。
ルーティン（`ai-tsukaikata-deepdive`）が拾って、出典を実際に読んでから記事を書く。

ファイル名が `_` で始まるのでビルド対象外。サイトには出ない。

## 書き方

`- [ ] https://...` の形で足す。処理が終わったら routine が `- [x]` に変えて、
下に生成した下書きのファイル名を書く。**消さない**（同じものを二度書かないため）。

スマホからでも足せる: GitHub でこのファイルを開く → 鉛筆アイコン → 行を足す → Commit changes。

📦 `- →保管:` の行は、機械回転（毎日04:43 の rotate.yml）が済んだ項目の詳細を保管庫 `_*_archive.md` へ移した印。**行は重複防止の台帳なので消さない・読み直す必要もない。**

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

## 処理済み

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
