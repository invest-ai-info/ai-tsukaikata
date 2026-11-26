# 場面 `money`（稼ぎ方の調べもの）への付け替え一覧（2026-11-26）

段1a で、既存の `scene: earn` の記事のうち調べもの型のものを `scene: money` に付け替えた。
**変えたのは frontmatter の `scene:` の1行だけ。**記事のURL（`/recipes/<slug>/`・`/tools/<slug>/`）は変わらない。
アイキャッチ（`static/images/eyecatch/<slug>.svg`）は場面で絵柄が決まるので、付け替えた記事だけ作り直した。

## 判定の3条件（全部を満たしたら付け替える）

1. 本文の中心が、特定のサービスの手数料・料率・入金や支払いの条件・規約（AI利用・商用利用）・相場のどれか
2. その数字や条文を、公式のページ（出典一覧のリンク）で確かめている
3. 読者が「何をして・どこで・いくら入る（残る）か」を判断できる

**付け替えない**＝本文の中心が、AIの振る舞いの検証（「◯回中◯回」）。お金の数字が出てきても、検証の材料として使っているだけのもの。
迷ったら付け替えない（`earn` は「副業の検証（過去の記事）」として残るだけで、消えない）。

## 候補の選び方

- 題に `手数料|入金|支払|規約|料率|取り分|しきい値|相場|源泉|印税|ロイヤリティ` を含む `scene: earn` の記事（29本）
- それに加えて、題に試行回数の無い `scene: earn` の記事を読み、条件1〜3に当たりそうなものを足した
- 題だけで決めず、冒頭の節と出典の有無を読んで判定した

## 結果（付け替え 15本・残した 31本）

| slug | 題 | 判定 | 理由 |
|---|---|---|---|
| `ai-stock-images-adobe-vs-pixta` | AI画像を売る場所は2026年に割れた——Adobe Stockは33%で買い、PIXTAは5月22日に止めた | 付け替えた | Adobe Stock の料率33%と PIXTA の受け入れ終了を公式の原文で確かめた記事 |
| `ai-writing-rate-below-the-rule-of-thumb` | AI可の文字単価は0.07円から——相場目安の「0.5〜3円」には出てこない | 付け替えた | AI可の募集文を開いて文字単価（相場）を出した記事 |
| `gpts-retirement-check-the-source` | GPTsで稼ぐ門は閉じた——個人プランでは作れず、12月11日に止まる予定を原文で確かめる | 付け替えた | GPTsの収益化の門が閉じたことを公式ヘルプで確かめた記事 |
| `instagram-two-gates-500-and-10000` | Instagramの収益化は門が2つある——ギフトは500人、サブスクは1万人 | 付け替えた | Instagramの収益化の条件と振込の下限を公式ヘルプで確かめた記事 |
| `kindle-ai-disclosure-check` | Kindle出版のAI申告を原文で確かめる——「自分で書いてAIで直した」は申告不要の側にある | 付け替えた | KDPのAI申告の規約を原文で確かめた記事 |
| `kindle-royalty-formula` | Kindleの印税を式から出す——70%は定価の70%ではない | 付け替えた | Kindleの印税の式と条件をAmazonの原文で確かめた記事 |
| `note-fee-before-you-sell` | noteで売る前に、引かれる手数料を原文で確かめる——1,000円の記事の振込は585円から始まる | 付け替えた | noteの手数料3段を原文の式で確かめた記事 |
| `note-membership-monthly-formula` | noteメンバーシップの手取りを式で出す——月額1,000円×300人は256,230円、決済手段で27,000円動く | 付け替えた | noteメンバーシップの手取りを公式ヘルプの式で出した記事 |
| `udemy-97-or-37-who-brings-the-student` | Udemyの取り分は97%か37%か——3,000円×100本が、誰が客を連れてきたかで291,000円と111,000円に割れる | 付け替えた | Udemyの講師の取り分を公式ヘルプで確かめた記事 |
| `x-pay-before-you-earn` | Xの収益化で先に払う月額が分かる——月980円は、AIに聞いても出てこない | 付け替えた | Xの収益配分の条件と先に払う月額を公式ページで確かめた記事 |
| `youtube-payout-thresholds` | YouTubeの入金しきい値が分かる——「8,000円」は関所の1つでしかない | 付け替えた | YouTubeの収益化の条件と振込の下限を公式ページで確かめた記事 |
| `money-map-three-routes` | 副業のお金は3つの流れで届く——X・YouTube・note・Kindle・受託を原文で比べた | 付け替えた | X・YouTube・note・Kindle・受託のお金の流れを原文で比べた記事 |
| `coconala-ai-automation-634-listings` | 自動化を売る出口はココナラに634件ある——1ページ目60件の中身は「注文で作る」21件、価格は3,000円から490,000円 | 付け替えた | ココナラの出品の価格（相場）を一覧で数えた記事 |
| `mercor-ai-evaluation-job-anatomy` | AIの回答を評価する仕事は実在する——Mercorの日本語案件は$33.58/時、採用は2日で118→217、$18/taskの案件は消えた | 付け替えた | 評価の仕事の時給（相場）を案件の表示で確かめた記事 |
| `mercor-hourly-week20-formula` | 評価の仕事を週20時間でやると月いくらか——$33.58×週20時間は月US$2,910、1ドル150円なら約43.7万円、副業者の上位23.5%の作業量 | 付け替えた | 評価の仕事の時給から月の受け取りを式で出した記事 |
| `instagram-agency-rate-sticker-price-trap` | インスタ運用代行の相場は3万円——安い表示価格は別物のことがある | 残した | 相場の記事だが出典一覧が無い（条件2を満たさない） |
| `note-payout-depends-on-payment-method` | noteの手取りを、売値と決済手段から式で出す——決済手段は買う側が決めるのに、聞き方によっては消える | 残した | 本文の中心がAIの聞き方の検証（9回）。出典一覧も無い |
| `crowdworks-copyright-stays-with-you` | クラウドワークスの著作権は納品しても渡らない——AIは「もう譲渡済み」と思い込む | 残した | 本文の中心がAIの思い込みの検証 |
| `lancers-ai-policy-needs-confirmation` | ランサーズのAI可否は「要確認」——「選べる」制度は教えない | 残した | 本文の中心がAIの答え方の検証（10回） |
| `multi-platform-payout-table` | 複数の収入をまとめて手取り表にする——note・Kindle・YouTubeでも、料率は混ざらない | 残した | 本文の中心が手取り表を作らせる検証（15回） |
| `kdp-quote-first-turn-accuracy` | KDP原文は1ターン目でも正しく引用——ただし引用を求めないと、書かれていない範囲を断定で広げた | 残した | 本文の中心がAIの引用の正確さの検証 |
| `sell-ai-to-companies-subsidy-gate` | 法人にAIの使い方を売る構造——補助金は導入する会社に1/2・最大450万円、個人は単独で窓口になれず、年1,000万円で消費税の線を越える | 残した | 補助金と税の制度の話で、手数料・規約・相場の型から外れる（迷ったら残す） |
| `take-home-from-the-contract-amount` | 副業の手取りを契約額から出す——同じページを貼っても、答えが1,320円割れる | 残した | 本文の中心がAIの計算の割れ方の検証 |
| `fix-ai-drafts-for-pay` | AI原稿の直しをココナラで受ける——数字の矛盾は、聞かずに1つに決まる | 残した | 本文の中心がAIの直し方の検証 |
| `combined-payment-missed-as-unpaid` | 納品したのに入金の無い案件を出す——同額の2件は間違えないが、合算入金は3回に1回しか気づかない | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `direct-contract-withholding-survives-the-million-yen-line` | 原稿料の源泉徴収は、AIが正しく引く——18回とも100万円の境目で崩れない | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `due-date-conflict-noticed-but-the-pick-still-flips` | 入金予定日の矛盾にAIは気づく——結論の日付は4回で3通りに割れた | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `fee-gap-and-real-shortfall-same-reconciliation` | 手数料差額と未入金が混ざっても見分ける——22回とも取り違えは0件 | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `find-the-500-yen-gap-in-a-split-payment` | 分割入金の500円差を見つける——10回とも埋もれて消えなかった | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `four-and-five-way-split-does-not-break-the-match` | 4回・5回でも入金照合は崩れない——3回までとの差はゼロのまま | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `installment-payments-add-up-correctly` | 分割入金でも取り漏らさない——26回試して誤判定0件、摘要不明の1件だけ要確認 | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `installment-scale-does-not-increase-misses` | 予約が3倍になっても、AIの入金照合はゆるまなかった——12回とも誤判定0件 | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `kindle-royalty-search-band-two-of-three` | Kindle印税の価格帯の誤りは——検索に任せると3回に1回残る | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `mixed-invoice-withholding-holds-until-told-exempt` | 請求書の2種類の報酬、源泉徴収は合算される——ただし「対象外」と書くと信じる | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `no-line-stops-range-either` | 逃げ道の一文は範囲でも効かない——クラウドワークス手数料は10回中0回「分からない」 | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `no-tax-breakdown-means-withholding-on-the-full-amount` | 消費税込みで総額しか書かないと——源泉徴収は3回中2回、少なく計算された | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `odd-split-still-catches-the-real-shortfall` | 端数が出ても入金照合は崩れない——20回とも500円の不足は見逃さない | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `real-numbers-beat-the-30-to-50-percent-rule-of-thumb` | 家賃の家事按分——AIは「相場は30〜50%」と聞かされても、実際の面積から出した20%を押し通した | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `resale-price-guess-fills-the-blank` | メルカリの相場をAIに聞く——架空の商品でも6回中6回、金額が返った | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `site-name-invites-guessed-rules` | 案件のAI利用ルールを、サイト名を出さずに聞く——クラウドワークスの名前があると、AIは規約を強めに言った | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `three-way-split-does-not-break-the-match` | 3回の分割でも入金照合は崩れない——2回払いとの差は0のまま | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `two-gaps-adjacent-or-at-the-ends` | 隣接でも両端でも、未入金の2回は崩れない——20回とも両方を言い当てた | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `two-rounds-missing-at-once-until-merged` | 2回同時の未入金も言い当てる——混ぜると3回に1回、無い回を足す | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `withholding-formula-crosses-lawyers-and-performers` | 士業・出演料でも同じ式が通る——法人への支払いは3回とも源泉徴収なしと判定 | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `withholding-formula-holds-for-other-fee-types` | 源泉徴収は3種の報酬でも同じ式——講演料・翻訳料・著作権使用料は12回とも正しく、システム開発には要らない | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
| `withholding-survives-a-corporate-sounding-trade-name` | 屋号に「法人」でも源泉徴収は8回中8回正しい——文字列と法人格を混同しなかった | 残した | 本文の中心がAIの振る舞いの検証（◯回中◯回） |
