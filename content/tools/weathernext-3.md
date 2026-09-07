---
title: WeatherNext 3は毎時更新に——「5倍鮮明」は大気の変数には届かない
description: 2026年9月3日にGoogleが発表した気象予測AI「WeatherNext 3」について、公式発表ページとモデルページに書かれている数字だけを並べました。同時期に発表されたMicrosoftの気象AI「Aurora 1.5」の公式ブログとも突き合わせています。
category: tools
scene: choose
published: 2026-09-07
checked: 2026-09-07
tags: [Google, 気象AI, WeatherNext, AI最新情報]
---

## 何が変わったか

Google は 2026年9月3日、**気象予測AI「WeatherNext 3」**を発表しました（出典: <https://blog.google/innovation-and-ai/models-and-research/google-deepmind/introducing-weathernext-3/>）。公式ページに書かれている数字だけを並べます。3行にすると、こうなります。

- **世界で初めて、1日24回・1時間ごとに予報を作り直す気象AIになった**とGoogle自身が説明しています（出典: <https://deepmind.google/models/weathernext/>）。前の世代 WeatherNext 2 は6時間ごとの更新でした（出典: 同上の発表ページ）。
- 気温・水分は解像度25kmから**5km**へ、その他の地表変数は**10km**へ上がりました。ただし<mark>上空の風速などの「大気の変数」は25kmのまま変わっていません</mark>（出典: 同上）。
- 雨・雪の予報精度は、比較する相手によって**最大60%・30%・10%**とバラバラの改善幅が公式に書かれています（出典: 同上）。

先に断っておきます。**この記事は運営者がこのモデルを試した記録ではありません。**Googleの発表ページ・モデルページと、同時期に発表されたMicrosoftの気象AI「Aurora 1.5」の公式ブログに書かれていることを読んで整理したものです。「よく当たった」「速かった」といった使用感は一切書いていません。

## 前のモデルとの違い

### 「5倍鮮明」の中身は、変数によって違う

発表ページには「全体で、前の世代 WeatherNext 2 のおよそ5倍鮮明」と書かれています（出典: <https://blog.google/innovation-and-ai/models-and-research/google-deepmind/introducing-weathernext-3/>）。ここは読み違えやすいので、内訳をそのまま表にします。

<figure class="figure">
<img src="/static/images/weathernext3-resolution-grid.svg" alt="WeatherNext 2とWeatherNext 3の解像度・更新頻度を比べた表。気温・水分（地表）は25kmから5kmへ、その他の地表変数（風など）は25kmから10kmへ改善した。いっぽう大気の変数（上空の風速など）は25kmのままで変わっていない。更新頻度は6時間ごとから1時間ごとになった。Googleは「全体でおよそ5倍鮮明」と説明しているが、内訳を見ると変数によって改善の度合いが違う。">
<figcaption>「5倍鮮明」は全体をならした値。大気の変数だけは前の世代と同じです</figcaption>
</figure>

発表ページの原文はこうです。「temperature and moisture — at a 5-kilometer resolution, other surface variables at 10 kilometers, and atmospheric variables, like wind speed, at 25 kilometers」（出典: 同上）。<mark>気温・水分と地表の一部変数は上がりましたが、上空の風速などの大気変数は、前の世代と同じ25kmのままです</mark>。「全体で5倍」という見出しの数字だけを見ると、全変数が5倍になったように読めてしまいますが、公式ページ自身の説明を分解するとそうではありません。

### 学習のさせ方そのものを変えた

発表ページは、多くのAI気象モデル（前の世代のWeatherNext 2を含む）が「数値予報（NWP）モデルの出力」を学習データにしていて、これには6時間の遅れがあると説明しています（出典: 同上）。WeatherNext 3は代わりに、**リアルタイムの静止気象衛星の生データ**と、**観測所（地上）の観測データ**を直接学習に使っていると書かれています（出典: 同上）。これによって、衛星から届いた最新の観測をもとに毎時予報を作れるようになった、というのが公式の説明です。

降水の学習データには、NASAの衛星観測「IMERG」と、Google独自の衛星レーダーによる降水解析を使っていると書かれています（出典: 同上）。

### 降水の精度改善は、比較対象によって数字が違う

<figure class="figure">
<img src="/static/images/weathernext3-precip-gain.svg" alt="WeatherNext 3の降水予報の精度改善を、比較対象別に示した横棒グラフ。衛星観測（IMERG）との比較では最大60%改善、レーダー観測網（MRMS）との比較では最大30%改善、雨量計の観測との比較では最大10%改善。いずれも中期予報の早い予報時間でのCRPS（正解との近さを測る指標）の改善幅で、Google発表の「最大」の値。">
<figcaption>同じ「精度改善」でも、何と比べたかで数字が変わります</figcaption>
</figure>

発表ページの原文は「a Continuous Ranked Probability Score (CRPS) improvement of up to 60% against IMERG, 30% for MRMS, and 10% against rain gauge measurements for early lead times」です（出典: 同上）。CRPSは値が小さいほど正確という指標で、「改善」はCRPSが小さくなったという意味です。<mark class="warn">3つの数字は、同じ地域・同じ予報時間で同時に測った値とは限りません。</mark>比較対象が変われば改善幅も変わる、という前提で読む必要があります。

もう1つ、消費者向けの体感に近い数字も書かれています。**「1日以上先を計画するとき、降水予報の精度が最大50%向上する」**というものです（出典: 同上）。これは先ほどのCRPSの数字とは別の指標・別の条件下の話で、「過去に精度が低かった地域ほど改善幅が大きい」と付け加えられています（出典: 同上）。

### 新しく増えた用途: 再生可能エネルギー向けの予報

WeatherNext 3は、風力発電のタービンの高さに近い**上空100mの風速**、太陽光発電向けの雲の量・日射量も予報すると書かれています（出典: 同上）。これは前の世代の説明には無かった項目です。

### どこで使えるようになるか

発表ページによると、WeatherNext 3は2026年9月3日から、Google検索・Gemini アプリ・Google マップ・Google Maps Platform Weather API・Google Earth Engineに組み込まれ始めています（出典: 同上）。開発者・企業向けには、BigQueryとEarth Engineでのクエリ、Google Cloud Storageからの一括ダウンロードが用意されています（出典: 同上）。

料金については、WeatherNext専用の価格表は発表ページに見当たりません。Earth Engineの一般的な料金ページには、非営利団体・研究者は「非営利・研究目的のプロジェクトであれば追加料金なしで利用できる」と明記されています（出典: <https://cloud.google.com/earth-engine/pricing>）。商用利用の計算課金は利用量に応じた段階制で、たとえば同ページには「1時間あたり0.40ドル〜0.16ドル（利用量が多いほど単価が下がる）」という計算単位（EECU時間）の料金が載っていますが、これはEarth Engine全体の一般料金であり、WeatherNextのデータ取得だけに絞った専用の金額ではありません（出典: 同上）。

## 他社の最上位モデルとの比較

Anthropic・OpenAIの公式ページを確認しましたが、両社とも気象予測に特化したモデルや製品は公式に出していません。そこで比較相手として、**同時期に大型アップデートを発表した気象AIモデル**である、Microsoftの「Aurora 1.5」（2026年7月9日発表）を選びました（出典: <https://www.microsoft.com/en-us/research/blog/aurora-1-5-extending-open-foundation-models-for-weather-and-earth-system-applications/>）。

<figure class="figure">
<img src="/static/images/weathernext3-vs-aurora.svg" alt="Google の WeatherNext 3（2026年9月3日発表）と Microsoft の Aurora 1.5（2026年7月9日発表）を、公式発表に書かれている型で並べた表。発表日・更新頻度（両方とも1時間ごと。Auroraは1.5で新規追加）・予測の出し方（両方ともアンサンブル・確率的で、Auroraは1.5で新規追加）・公開の形（Googleは自社製品への統合とクラウドでの提供、Microsoftはオープンソース）・自社発表の比較指標（GoogleはIMERGとの比較でCRPS最大60%改善、MicrosoftはECMWF ENSを88.9%の項目で上回る）を比べている。比較指標は測り方が別で、1本の数字としては比べられない。">
<figcaption>2社とも同じ時期に「毎時」「確率的」へ舵を切りました</figcaption>
</figure>

**同じ方向に進んでいる点が2つあります。**

1つめは更新頻度です。Aurora 1.5の発表には「hourly temporal resolution」が新しく加わったと書かれています（出典: 同上）。WeatherNext 3の「1時間ごと」と同じ方向です。

2つめは、予報の出し方です。Aurora 1.5は「ensemble forecasting（確率的な予測手法。複数の予測を走らせて、起こりうる結果の幅を示す）」を新しく搭載したと書かれており（出典: 同上）、WeatherNext 3もモデルページで「an ensemble model」と説明されています（出典: <https://deepmind.google/models/weathernext/>）。<mark>両社とも、2026年に「確率的な予測」を主力製品に組み込んだ点が重なっています。</mark>

**一方で、公開の仕方は正反対です。**Aurora 1.5は「Released as open source on GitHub with model checkpoints on Hugging Face」と明記されていて、モデルの重み自体をダウンロードして使える形で公開されています（出典: 同上）。<mark>WeatherNext 3は、GoogleのSearch・Maps・Gemini・クラウドサービスに統合される形で提供され、モデル自体を配布する記述は発表ページにありません。</mark>

**自社発表の比較指標も、測り方がまったく違います。**Googleは「IMERGとの比較でCRPSが最大60%改善」と説明し、Microsoftは「Aurora 1.5の確率的な予報は、ECMWFの最先端のアンサンブル予報（ECMWF ENS）に対して、評価対象の88.9%の項目で上回った」と説明しています（出典: 同上）。<mark class="warn">CRPSの改善率と、比較対象を上回った項目の割合は、そもそも単位も基準も違う数字です。「どちらの精度が高いか」をこの2つの数字から言い切ることはできません。</mark>

なお、Aurora 1.5より前の「Aurora」（2024年6月3日公開・Natureに2025年掲載）は、0.1度（赤道付近でおよそ11km）の空間解像度、13億パラメータ、数値予報システムIFSに対しておよそ5,000倍の計算速度、GraphCastというAIモデルに対して94%の項目で同等以上、大気汚染予測ではCAMSという指標に対して74%の項目で上回ったと発表されています（出典: <https://www.microsoft.com/en-us/research/blog/introducing-aurora-the-first-large-scale-foundation-model-of-the-atmosphere/>）。<mark class="warn">ただし、この解像度の数字は2024年時点の（1.5より前の）Auroraのものです。Aurora 1.5の発表ブログには、空間解像度を具体的な数値で言い直した記述が見当たりませんでした。</mark>そのため、WeatherNext 3の「5km/10km/25km」とAurora 1.5の解像度を、そのまま並べて比べることはできません。

Aurora 1.5の発表ページには、2024〜2025年に発生した熱帯低気圧すべてに対する評価で、進路の予測誤差が元のAuroraに比べて「およそ3分の1」小さくなった（アンサンブルの中央値、5日先の予測で最も改善幅が大きい）とも書かれています（出典: 同上）。これはWeatherNext 3側に対応する数字が発表ページに見当たらないため、比較のしようがない項目としてそのまま書いておきます。

料金についても、Microsoft側に専用の価格表は見当たりません。商用利用は「Aurora 1.5 on Microsoft Foundry」への案内と、公式ブログに記載されたメールでの問い合わせ先が書かれているだけです（出典: 同上）。**両社とも、気象AI単体の料金をドルで明示したページは見つかりませんでした。**

## どういう人に効くか

**いま関係してくる人**

- Google検索・Google マップ・Gemini アプリで天気を確認している人。<mark>何もしなくても、9月3日から裏側のモデルが変わっています。</mark>
- 太陽光・風力など再生可能エネルギーに関わる仕事をしている人。上空100mの風速・日射量・雲量という、前の世代には無かった項目が予報に加わりました。
- 天気データをBigQueryやEarth Engineに取り込んで自社の分析に使いたい人。モデルのセットアップ無しで高解像度データにアクセスできると発表ページに書かれています。

**急がなくていい人・様子見でいい人**

- 上空の風速など「大気の変数」の精度を重視する人。<mark class="warn">この部分は前の世代から解像度が変わっていません（25kmのまま）。</mark>
- 気象モデルを自分のサーバーで動かしたい人。<mark>その用途にはWeatherNext 3ではなく、オープンソースで重みが公開されているAurora 1.5のほうが向いています。</mark>
- 「どちらが賢いか」を1つの数字で知りたい人。公式の比較指標同士がそもそも測り方が違うため、この記事では言い切れません。

**この記事で分からないこと**

日本語での予報の反映状況、実際の体感精度、日本国内での提供開始の詳細な時期。発表ページには「starting today」とだけ書かれていて、国・地域ごとの展開順序は明記されていません。運営者も実際に使い比べていないため、体感については書けません。

## 出典一覧

すべて各社の公式ページです。まとめ記事・ニュースサイト・個人ブログは1件も使っていません。

1. WeatherNext 3の発表（Google・2026年9月3日）: <https://blog.google/innovation-and-ai/models-and-research/google-deepmind/introducing-weathernext-3/>
   （Google DeepMind側の <https://deepmind.google/blog/introducing-weathernext-3-our-most-advanced-and-accurate-global-weather-ai-model/> を開くと、このページへ転送されます）
2. WeatherNext 3のモデルページ（Google DeepMind公式）: <https://deepmind.google/models/weathernext/>
3. Earth Engineの料金（Google Cloud公式）: <https://cloud.google.com/earth-engine/pricing>
4. Aurora 1.5の発表（Microsoft Research・2026年7月9日）: <https://www.microsoft.com/en-us/research/blog/aurora-1-5-extending-open-foundation-models-for-weather-and-earth-system-applications/>
5. Auroraの発表（Microsoft Research・2024年6月3日）: <https://www.microsoft.com/en-us/research/blog/introducing-aurora-the-first-large-scale-foundation-model-of-the-atmosphere/>

なお、独立の気象AI評価機関「Brightband」のサイトと、Googleの実験公開プラットフォーム「Weather Lab」は、この記事を書いた環境からは到達できませんでした（許可リストに無いホストという理由で、先方のブロックではありません）。発表ページが引用している「独立評価による『最も高精度』」という評価そのものは、この記事では検証していません。この記事で使った数字は、すべて上記5件の到達できたページから確認しています。

料金と仕様は変わります。実際に使う前に、必ず上記の公式ページで現在の値を確認してください。
