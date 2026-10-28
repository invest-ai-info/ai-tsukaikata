# 試した証拠 — head-only-flags-live-pages-as-broken

記事に載せる指示文すべてについて、この形式で残す。

⚠️ このファイルは `content/` の中に置いていない（ビルド除外はファイル名の `_` 判定のため）。

実測日: 2026-10-28。実測の相手＝`claude --print --safe-mode --tools "" --system-prompt "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。ユーザーの依頼に文章だけで答えてください。"`（CLAUDE.md・skills・plugins・履歴を全部無効化した新規プロセス。呼び出しごとに完全に独立したプロセス、会話の継続なし）。

---

## 教材（架空データ）

架空のブログに貼ったリンク一覧、20本×2材料。各材料の構成は共通で、**本当に切れている(a)8本・HEADは404だがGETは200(b)4本・HEAD/GETとも403でボット判定の可能性(c)4本・正常(d)4本**。真値はコードで仕込んだ（`materials.py`）。

### 材料A（観葉植物ブログのリンク一覧）

```
L01  https://green-room-note.jp/entry/2021/leaf-care  HEAD=404  GET=404
L02  https://plant-almanac-notes.jp/guide/watering  HEAD=200  GET=200
L03  https://soil-mix-notes.jp/archive/2020/repotting  HEAD=404  GET=404
L04  https://houseplant-faq.jp/help/light-levels  HEAD=404  GET=200
L05  https://garden-supply-co.jp/products/pot-01  HEAD=403  GET=403
L06  https://green-room-note.jp/entry/2022/pest-control  HEAD=200  GET=200
L07  https://plant-almanac-notes.jp/guide/fertilizer  HEAD=404  GET=404
L08  https://houseplant-faq.jp/help/humidity  HEAD=404  GET=200
L09  https://soil-mix-notes.jp/archive/2019/drainage  HEAD=404  GET=404
L10  https://garden-supply-co.jp/products/mister-02  HEAD=403  GET=403
L11  https://green-room-note.jp/entry/2021/propagation  HEAD=200  GET=200
L12  https://plant-almanac-notes.jp/guide/pruning  HEAD=404  GET=404
L13  https://houseplant-faq.jp/help/temperature  HEAD=404  GET=200
L14  https://soil-mix-notes.jp/archive/2021/fungus  HEAD=404  GET=404
L15  https://garden-supply-co.jp/products/shelf-03  HEAD=403  GET=403
L16  https://green-room-note.jp/entry/2023/seasonal  HEAD=200  GET=200
L17  https://plant-almanac-notes.jp/guide/species-list  HEAD=404  GET=404
L18  https://houseplant-faq.jp/help/repotting-season  HEAD=404  GET=200
L19  https://soil-mix-notes.jp/archive/2022/root-rot  HEAD=404  GET=404
L20  https://garden-supply-co.jp/products/tray-04  HEAD=403  GET=403
```
真値＝a(本当に切れている): ['L01', 'L03', 'L07', 'L09', 'L12', 'L14', 'L17', 'L19'] / b(HEAD404・GET200): ['L04', 'L08', 'L13', 'L18'] / c(403・ボット判定の可能性): ['L05', 'L10', 'L15', 'L20'] / d(正常): ['L02', 'L06', 'L11', 'L16']

### 材料B（ランニング記録ブログのリンク一覧）

```
L01  https://run-log-diary.jp/2020/race-report-spring  HEAD=404  GET=404
L02  https://shoe-review-hub.jp/model/trail-9  HEAD=200  GET=200
L03  https://pace-chart-notes.jp/archive/2019/interval  HEAD=404  GET=404
L04  https://marathon-faq.jp/help/carb-loading  HEAD=404  GET=200
L05  https://sports-gear-outlet.jp/items/belt-02  HEAD=403  GET=403
L06  https://run-log-diary.jp/2022/half-marathon-fall  HEAD=200  GET=200
L07  https://pace-chart-notes.jp/archive/2018/tempo-run  HEAD=404  GET=404
L08  https://marathon-faq.jp/help/taper-week  HEAD=404  GET=200
L09  https://run-log-diary.jp/2019/injury-recovery  HEAD=404  GET=404
L10  https://sports-gear-outlet.jp/items/watch-05  HEAD=403  GET=403
L11  https://shoe-review-hub.jp/model/road-7  HEAD=200  GET=200
L12  https://pace-chart-notes.jp/archive/2020/fartlek  HEAD=404  GET=404
L13  https://marathon-faq.jp/help/hydration-plan  HEAD=404  GET=200
L14  https://run-log-diary.jp/2021/winter-training  HEAD=404  GET=404
L15  https://sports-gear-outlet.jp/items/socks-03  HEAD=403  GET=403
L16  https://shoe-review-hub.jp/model/track-2  HEAD=200  GET=200
L17  https://pace-chart-notes.jp/archive/2017/long-run  HEAD=404  GET=404
L18  https://marathon-faq.jp/help/race-week-diet  HEAD=404  GET=200
L19  https://run-log-diary.jp/2018/first-marathon  HEAD=404  GET=404
L20  https://sports-gear-outlet.jp/items/cap-04  HEAD=403  GET=403
```
真値＝a(本当に切れている): ['L01', 'L03', 'L07', 'L09', 'L12', 'L14', 'L17', 'L19'] / b(HEAD404・GET200): ['L04', 'L08', 'L13', 'L18'] / c(403・ボット判定の可能性): ['L05', 'L10', 'L15', 'L20'] / d(正常): ['L02', 'L06', 'L11', 'L16']

---

## 指示文1（記事：AIへの頼み方 1・HEADだけを渡す）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストの応答コードを記録しています。この中でリンク切れになっているものを教えてください。
```
このあとに空行を挟んで、点検結果の一覧（HEADの応答コードのみ）をそのまま貼って送った。

### 返ってきたもの（生）— 材料A・1回目

```
結果から判断すると、リンク切れ(404)は以下の12件です。

**404(リンク切れ)**
- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L04 https://houseplant-faq.jp/help/light-levels
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L08 https://houseplant-faq.jp/help/humidity
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L13 https://houseplant-faq.jp/help/temperature
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L18 https://houseplant-faq.jp/help/repotting-season
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

**判断を保留すべきもの(403)**
L05, L10, L15, L20(garden-supply-co.jp の4件)は403です。403は「アクセス拒否」で、ページ自体は存在していてもHEADリクエストやボット的なアクセスを弾いている可能性があります。リンク切れと断定せず、ブラウザで実際に開いて確認するのがおすすめです。

**正常(200)**
L02, L06, L11, L16

**補足**
- 404のドメイン別の傾向を見ると、houseplant-faq.jp(4件)と soil-mix-notes.jp(4件)は点検した全リンクが404です。サイト全体の移転・閉鎖やURL構造の変更の可能性があるので、トップページを確認すると、新URLへまとめて修正できるかもしれません。
- plant-almanac-notes.jp は3件が404で、1件(L02)だけ200です。
- 一部のサーバーはHEADに対して誤って404を返すことがあるため、念のため404のものもGETで再確認すると確実です。
```

### 返ってきたもの（生）— 材料A・2回目

```
結果から判断すると、リンク切れ(404)は次の12件です。

**404(リンク切れ)**
- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L04 https://houseplant-faq.jp/help/light-levels
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L08 https://houseplant-faq.jp/help/humidity
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L13 https://houseplant-faq.jp/help/temperature
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L18 https://houseplant-faq.jp/help/repotting-season
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

**切れとは断定できないもの(403)**
- L05、L10、L15、L20(すべて garden-supply-co.jp の商品ページ)

403は「アクセス拒否」の意味で、ページ自体は存在していてもボットや自動アクセスを弾いている可能性があります。4件すべてが同じドメインで、同じ403という点もその可能性を示唆しています。ブラウザで実際に開いて確認することをおすすめします。HEADを許可していないサーバーもあるので、GETでも試すとより確実です。

**正常(200)**
- L02、L06、L11、L16

**傾向**
404のページはドメインごとにまとまっています。houseplant-faq.jp(4件)、soil-mix-notes.jp(4件)は点検した全リンクが404で、plant-almanac-notes.jp も3件中2件が404です。個別の記事削除ではなく、サイト構造の変更やドメイン移転、サイト閉鎖の可能性があります。移転先があれば、一括置換で直せるかもしれません。また、Wayback Machineなどのアーカイブへ差し替える方法もあります。
```

### 返ってきたもの（生）— 材料B・1回目

```
結果から判断すると、リンク切れ(404)と確認できるのは次の12件です。

**404(リンク切れ)**
- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L04 https://marathon-faq.jp/help/carb-loading
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L08 https://marathon-faq.jp/help/taper-week
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L13 https://marathon-faq.jp/help/hydration-plan
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L18 https://marathon-faq.jp/help/race-week-diet
- L19 https://run-log-diary.jp/2018/first-marathon

**判断を保留すべきもの(403)**
- L05(belt-02)、L10(watch-05)、L15(socks-03)、L20(cap-04)はすべて sports-gear-outlet.jp のページです。403は「存在するがアクセスを拒否された」ことを示すので、リンク切れとは断定できません。HEADリクエストや自動アクセスをサイト側がブロックしている可能性があります。ブラウザで実際に開いて確認することをおすすめします。

**正常(200)**
- L02、L06、L11、L16

**補足**
- 404のリンクはドメインごとに偏っています。run-log-diary.jp(2018〜2021年の記事)、pace-chart-notes.jp(archive配下すべて)、marathon-faq.jp(help配下すべて)です。個別のページ削除というより、サイトのURL構成変更や移転、アーカイブ廃止が原因かもしれません。新しいURLに一括で置き換えられる可能性があります。
- 一部のサーバーはHEADを正しく処理せず404を返すことがあるため、念のため404のものもGETで再確認すると確実です。
```

### 返ってきたもの（生）— 材料B・2回目

```
結果からの判断をまとめます。

**リンク切れと判断できるもの(HEAD=404、12件)**

- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L04 https://marathon-faq.jp/help/carb-loading
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L08 https://marathon-faq.jp/help/taper-week
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L13 https://marathon-faq.jp/help/hydration-plan
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L18 https://marathon-faq.jp/help/race-week-diet
- L19 https://run-log-diary.jp/2018/first-marathon

**正常(HEAD=200、3件)**:L02、L06、L11、L16(※L16を含めると4件です)

**判断を保留すべきもの(HEAD=403、4件)**

- L05 https://sports-gear-outlet.jp/items/belt-02
- L10 https://sports-gear-outlet.jp/items/watch-05
- L15 https://sports-gear-outlet.jp/items/socks-03
- L20 https://sports-gear-outlet.jp/items/cap-04

403は「アクセス拒否」を意味し、ページが存在しないという意味ではありません。自動点検のHEADリクエストをボット対策などで弾いている可能性があります。ブラウザで実際に開いて確認するか、GETリクエストで再確認してください。ブラウザで正常に表示されるなら、リンク切れではありません。

**補足**

- 404の傾向として、pace-chart-notes.jp(3件とも過去アーカイブ)、marathon-faq.jp(help配下4件すべて)、run-log-diary.jpの2018〜2021年の記事が軒並み切れています。サイト単位で構成変更や閉鎖が起きている可能性があるので、移転先のURLがないか確認すると、まとめて修正できるかもしれません。
- 一部のサーバーはHEADに対して誤って404を返すことがあります。念のため、404のものも数件GETで確認すると確実です。

(内訳:404が12件、200が4件、403が4件の計20件です。冒頭で「3件」と書いたのは誤りで、正しくは4件です。)
```

### 照合（機械）

```
4回とも、b(HEAD404・GET200)の4件すべてが「リンク切れ」の列に含まれた（false positive=4/4）。
V0_A_r1: broken主張=L01,L03,L04,L07,L08,L09,L12,L13,L14,L17,L18,L19（12件）/ 真のa=L01,L03,L07,L09,L12,L14,L17,L19 / b混入=L04,L08,L13,L18（4件とも混入）
V0_A_r2: 同じ12件・同じ4件混入
V0_B_r1: broken主張=L01,L03,L04,L07,L08,L09,L12,L13,L14,L17,L18,L19（12件）/ b混入=L04,L08,L13,L18（4件とも混入）
V0_B_r2: 同じ12件・同じ4件混入
c(403)の4件は、4回とも「判断を保留すべきもの」に分けられ、brokenには入らなかった（0/4）。
```

### 判定

**採用**（記事「AIへの頼み方1」）。本当の危険（HEADだけでは生きているページを誤判定する）を再現する目的の指示文。

---

## 指示文2（記事：AIへの頼み方 2・HEADだけでは確定できないと言い添える）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストの応答コードを記録しています。HEADの応答コードだけでは、本当に切れているかは確定できません。404や403のリンクは、GETリクエストでの再確認が必要なものとして分けてください。GETで再確認済みのものは、まだありません。
```
このあとに空行を挟んで、点検結果の一覧（HEADの応答コードのみ）をそのまま貼って送った。

### 返ってきたもの（生）— 材料A・1回目

```
結果を分類しました。GETでの再確認済みのものはまだないため、404/403のリンクはすべて「再確認が必要」として扱っています。

## HEAD=200(正常応答・再確認の対象外)
5件
- L02 https://plant-almanac-notes.jp/guide/watering
- L06 https://green-room-note.jp/entry/2022/pest-control
- L11 https://green-room-note.jp/entry/2021/propagation
- L16 https://green-room-note.jp/entry/2023/seasonal

## GETでの再確認が必要なもの(計16件)

### HEAD=404(12件)
- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L04 https://houseplant-faq.jp/help/light-levels
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L08 https://houseplant-faq.jp/help/humidity
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L13 https://houseplant-faq.jp/help/temperature
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L18 https://houseplant-faq.jp/help/repotting-season
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

### HEAD=403(4件)
- L05 https://garden-supply-co.jp/products/pot-01
- L10 https://garden-supply-co.jp/products/mister-02
- L15 https://garden-supply-co.jp/products/shelf-03
- L20 https://garden-supply-co.jp/products/tray-04

## 訂正
上の「HEAD=200」の見出しの件数は4件が正しく、「5件」は誤りです。内訳は200が4件、404が12件、403が4件で、合計20件です。

## 補足
- 現時点では、404や403のリンクが実際に切れているとは断定できません。HEADを拒否したり、HEADだけ異なる応答を返したりするサーバーもあります。
- 403は、bot対策やHEADメソッドの制限によるものである可能性があります。garden-supply-co.jpの4件は全部403なので、サイト全体の制限を疑ってよいと思います。
- 404が特定のドメイン(houseplant-faq.jp、soil-mix-notes.jp、plant-almanac-notes.jp)に集中している点も注目に値します。サイトのURL構造が変わっただけかもしれません。
- GETで再確認したあと、まだ404のものは、リンク先の修正や削除を検討してください。

GETの再確認用にcurlコマンドなどが必要でしたら、お知らせください。
```

### 返ってきたもの（生）— 材料A・2回目

```
HEADの結果だけでの分類です。GETでの再確認は、どれもまだ行っていません。

## GETでの再確認が必要(HEAD=404または403):14件

**HEAD=404(10件)**
- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L04 https://houseplant-faq.jp/help/light-levels
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L08 https://houseplant-faq.jp/help/humidity
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L13 https://houseplant-faq.jp/help/temperature
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L18 https://houseplant-faq.jp/help/repotting-season
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

(404は上記12件です。合計は下記の通りです。)

**HEAD=403(4件)**
- L05 https://garden-supply-co.jp/products/pot-01
- L10 https://garden-supply-co.jp/products/mister-02
- L15 https://garden-supply-co.jp/products/shelf-03
- L20 https://garden-supply-co.jp/products/tray-04

訂正します。404が12件、403が4件で、再確認が必要なのは合計16件です。

## HEAD=200(4件)
- L02 https://plant-almanac-notes.jp/guide/watering
- L06 https://green-room-note.jp/entry/2022/pest-control
- L11 https://green-room-note.jp/entry/2021/propagation
- L16 https://green-room-note.jp/entry/2023/seasonal

この4件はHEADでは応答がありましたが、ページ内容までは確認していません。

## 補足
- 404はドメイン別に見ると、soil-mix-notes.jp、houseplant-faq.jp、plant-almanac-notes.jpで集中しています。サイト側の構造変更やHEAD非対応の可能性もあるため、GETで確かめてから切れていると判断するのが安全です。
- garden-supply-co.jpの403は4件すべてで出ています。HEADやボット的なアクセスを拒否している可能性があるので、GETで User-Agent を通常のブラウザ相当にして再試行すると切り分けやすくなります。
```

### 返ってきたもの（生）— 材料B・1回目

```
HEADの応答コードだけでは切れているか確定できないため、404と403のリンクをGETでの再確認が必要なものとして分けました。GETで再確認済みのものはまだありません。

## GETでの再確認が必要(404または403)：17件

**HEAD=404(12件)**
- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L04 https://marathon-faq.jp/help/carb-loading
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L08 https://marathon-faq.jp/help/taper-week
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L13 https://marathon-faq.jp/help/hydration-plan
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L18 https://marathon-faq.jp/help/race-week-diet
- L19 https://run-log-diary.jp/2018/first-marathon

**HEAD=403(4件)**
- L05 https://sports-gear-outlet.jp/items/belt-02
- L10 https://sports-gear-outlet.jp/items/watch-05
- L15 https://sports-gear-outlet.jp/items/socks-03
- L20 https://sports-gear-outlet.jp/items/cap-04

合計は12件+4件の16件で、17件ではありませんでした。訂正します。**再確認が必要なのは16件**です。

## 再確認の対象外(HEAD=200)：4件
- L02 https://shoe-review-hub.jp/model/trail-9
- L06 https://run-log-diary.jp/2022/half-marathon-fall
- L11 https://shoe-review-hub.jp/model/road-7
- L16 https://shoe-review-hub.jp/model/track-2

## 補足
- 403の4件はすべて sports-gear-outlet.jp です。HEADやボット的なアクセスを拒否している可能性があり、GETで開けるか確認する価値があります。
- 404の12件は、pace-chart-notes.jp(archive配下)や marathon-faq.jp(help配下)など、ドメインごとにまとまっています。サイト全体の構造変更やURL移転の可能性もあるため、GETでも404なら、新しいURLを探すか削除を検討してください。
- HEAD=200の4件は、今回の結果では問題ありません。
```

### 返ってきたもの（生）— 材料B・2回目

```
HEADの応答コードだけでは切れているか確定できないため、404と403のリンクをGETでの再確認が必要なものとして分けました。GETでの再確認はまだ行っていません。

## GETでの再確認が必要(404または403): 16件

**HEAD=404(11件)**
- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L04 https://marathon-faq.jp/help/carb-loading
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L08 https://marathon-faq.jp/help/taper-week
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L13 https://marathon-faq.jp/help/hydration-plan
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L18 https://marathon-faq.jp/help/race-week-diet
- L19 https://run-log-diary.jp/2018/first-marathon

(上記は実際には12件です。HEAD=404は計12件、HEAD=403は4件で、合計16件になります。)

**HEAD=403(4件)**
- L05 https://sports-gear-outlet.jp/items/belt-02
- L10 https://sports-gear-outlet.jp/items/watch-05
- L15 https://sports-gear-outlet.jp/items/socks-03
- L20 https://sports-gear-outlet.jp/items/cap-04

## HEAD=200(再確認の対象外): 4件
- L02 https://shoe-review-hub.jp/model/trail-9
- L06 https://run-log-diary.jp/2022/half-marathon-fall
- L11 https://shoe-review-hub.jp/model/road-7
- L16 https://shoe-review-hub.jp/model/track-2

## 補足
- 404の12件のうち、`pace-chart-notes.jp` の古いアーカイブ(2017〜2020年)と `marathon-faq.jp/help/` 配下は、ドメインごとにまとめて404です。個別のページ削除ではなく、サイト側のURL構造変更や移転の可能性があります。GETの再確認と合わせて、リダイレクト先の有無も見るとよいです。
- 403の4件はすべて `sports-gear-outlet.jp` です。HEADやボット判定を拒否している可能性があるため、GETの結果次第では実際には生きている場合があります。
- HEAD=200の4件は、現時点では問題なしとみなせます。
```

### 照合（機械）

```
4回とも、404・403のリンク16件（a8+b4+c4）全部を「切れている」と断定せず、GET再確認が必要な保留扱いに分けた（false positiveでbrokenに断定された件数=0/4）。
⚠️ 見出しの件数は4回とも食い違った（後述の★300系と同じ自己訂正つきの誤記。V0B_A_r1: HEAD=200見出し「5件」→本文訂正「4件」。V0B_A_r2: 「404は上記12件です」の直前に10件の見出し→訂正。V0B_B_r1: 「17件」→訂正「16件」。V0B_B_r2: 「HEAD=404(11件)」の見出し→本文で12件と訂正）。本文内で自己訂正され、最終的な分類（16件が保留）自体は4回とも正しい。
```

### 判定

**採用**（記事「AIへの頼み方2」）。GETの点検をまだ組み込んでいない場合の、安全な待ち方として採用。

---

## 指示文3（記事：AIへの頼み方 3・HEADとGETの両方を渡す）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。この中でリンク切れになっているものを教えてください。
```
このあとに空行を挟んで、点検結果の一覧（HEADとGETの両方の応答コード）をそのまま貼って送った。

### 返ってきたもの（生）— 材料A・1回目

```
結果から判断すると、リンク切れと言えるのは **HEAD・GETの両方が404** のものです。

**リンク切れ(8件)**
- L01 https://green-room-note.jp/entry/2021/leaf-care(404/404)
- L03 https://soil-mix-notes.jp/archive/2020/repotting(404/404)
- L07 https://plant-almanac-notes.jp/guide/fertilizer(404/404)
- L09 https://soil-mix-notes.jp/archive/2019/drainage(404/404)
- L12 https://plant-almanac-notes.jp/guide/pruning(404/404)
- L14 https://soil-mix-notes.jp/archive/2021/fungus(404/404)
- L17 https://plant-almanac-notes.jp/guide/species-list(404/404)
- L19 https://soil-mix-notes.jp/archive/2022/root-rot(404/404)

**リンク切れではないもの**
- **HEAD=404 / GET=200(L04, L08, L13, L18)**:サーバーがHEADリクエストに正しく対応していないだけで、ブラウザからは通常どおり開けます。リンク切れではありません。
- **HEAD・GETとも403(L05, L10, L15, L20)**:garden-supply-co.jp の商品ページ4件です。ページ自体は存在していても、自動アクセス(ボット)を拒否している可能性が高く、404のような「消えた」状態とは異なります。ただし確定ではないので、ブラウザで一度開いて確認することをおすすめします。
- **200/200(L02, L06, L11, L16)**:正常です。

**補足**
- 点検ツール側でHEADが404のときはGETで再確認する設定にしておくと、L04などの誤検知を減らせます。
- リンク切れ8件のうち、soil-mix-notes.jp が4件、plant-almanac-notes.jp が3件(L07, L12, L17)を占めています。サイト全体の構造変更やURL変更の可能性があるので、移転先がないか確認すると、まとめて直せるかもしれません。
```

### 返ってきたもの（生）— 材料A・2回目

```
## リンク切れと判断できるもの(HEAD・GETともに404)

| ID | URL |
|---|---|
| L01 | https://green-room-note.jp/entry/2021/leaf-care |
| L03 | https://soil-mix-notes.jp/archive/2020/repotting |
| L07 | https://plant-almanac-notes.jp/guide/fertilizer |
| L09 | https://soil-mix-notes.jp/archive/2019/drainage |
| L12 | https://plant-almanac-notes.jp/guide/pruning |
| L14 | https://soil-mix-notes.jp/archive/2021/fungus |
| L17 | https://plant-almanac-notes.jp/guide/species-list |
| L19 | https://soil-mix-notes.jp/archive/2022/root-rot |

計8件です。

## リンク切れではないもの

- **L04, L08, L13, L18(houseplant-faq.jp)**: HEADは404ですが、GETは200で、実際にはページが表示されます。サーバー側がHEADリクエストに対応していないだけと考えられ、点検ツールの誤検知です。
- **L02, L06, L11, L16**: どちらも200で正常です。

## 要確認

- **L05, L10, L15, L20(garden-supply-co.jp)**: HEAD・GETともに403です。ページが存在しないのではなく、アクセス拒否(ボット対策や地域制限など)の可能性が高いです。ブラウザで実際に開いて確認してください。開ければ問題なし、開けなければ商品ページの終了などが考えられます。

## 補足

点検ツールがHEADだけで判定している場合、L04・L08・L13・L18が誤ってリンク切れ扱いになります。HEADが404や405のときはGETで再確認する設定にすると、誤検知を減らせます。
```

### 返ってきたもの（生）— 材料B・1回目

```
リンク切れと判断できるのは、HEAD・GETの両方が404のものです。

**リンク切れ(8件)**
- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L19 https://run-log-diary.jp/2018/first-marathon

**リンク切れではないもの**
- L04、L08、L13、L18(marathon-faq.jp)は、HEADが404でもGETは200です。サーバーがHEADに対応していないだけで、ページは正常に表示できます。誤検知なので修正は不要です。
- L05、L10、L15、L20(sports-gear-outlet.jp)は、HEADもGETも403です。ページは存在しますが、アクセス制限(ボット対策など)で弾かれている可能性が高く、リンク切れとは断定できません。実際にブラウザで開いて確認することをおすすめします。
- L02、L06、L11、L16は、どちらも200で正常です。

**補足**
リンク切れはすべて run-log-diary.jp と pace-chart-notes.jp の過去記事(2017〜2021年)です。サイト構成の変更や記事の削除が原因かもしれません。移転先があるか、Web魚拓(Internet Archive)などで確認し、見つからなければリンクの削除や代替ページへの差し替えを検討してください。
```

### 返ってきたもの（生）— 材料B・2回目

```
結論から言うと、リンク切れと判断できるのは **HEAD・GETの両方が404** のものです。

**リンク切れ(8件)**
- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L19 https://run-log-diary.jp/2018/first-marathon

**リンク切れではないもの**
- **正常(200/200)**: L02, L06, L11, L16
- **HEADだけ404でGETは200(4件の誤検知)**: L04, L08, L13, L18(すべて marathon-faq.jp)。サーバーがHEADリクエストに対応していないだけで、実際にはページを開けるため、リンク切れではありません。
- **403/403(4件)**: L05, L10, L15, L20(すべて sports-gear-outlet.jp)。ページは存在しているものの、点検ツールのアクセスが拒否されている可能性が高く、リンク切れとは断定できません。ブラウザで実際に開いて確認することをおすすめします。ボット対策やアクセス制限によるものであれば、問題ないはずです。

**補足**
リンク切れの8件は、run-log-diary.jp と pace-chart-notes.jp に集中しています。サイト構成の変更や過去記事の削除が考えられるため、新しいURLが見つかれば差し替え、なければリンクを外すか、Web魚拓などのアーカイブ版へ置き換えるとよいでしょう。
```

### 照合（機械）

```
4回とも、brokenとして挙げたのは真のa(8件)とちょうど一致（false positive=0/4・false negative=0/4）。
b(4件)は4回とも「リンク切れではない」と明示的に除外。c(4件)は4回とも「要確認」に分類され、brokenに含まれなかった。
見出しの件数（「リンク切れ(8件)」等）は4回とも実際の列挙と一致（miscount=0/4）。
```

### 判定

**採用**（記事「AIへの頼み方3」）。この記事の核＝HEADとGETを両方渡すだけで、数字の基準を指示しなくても正しく仕分けられることを示す指示文。

---

## 指示文4（記事：言い直し方・基準を数字で書く）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETも404の場合だけ、切れていると判断してください。この基準で、リンク切れになっているものを教えてください。
```
このあとに空行を挟んで、点検結果の一覧（HEADとGETの両方の応答コード）をそのまま貼って送った。

### 返ってきたもの（生）— 材料A・1回目

```
GETも404のものだけがリンク切れです。該当は次の10件です。

- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

数えると8件でした。訂正します。リンク切れは上の8件です。

**切れていないと判断したもの**
- HEADが404でGETが200: L04、L08、L13、L18
- HEADもGETも200: L02、L06、L11、L16
- HEADもGETも403: L05、L10、L15、L20

L05、L10、L15、L20は、GETが404ではないため、ご指定の基準ではリンク切れに含めていません。ただし403はアクセス拒否を意味するので、リンク先が存在していても、ブラウザで開けない可能性があります。念のため、実際に表示できるか確認することをおすすめします。
```

### 返ってきたもの（生）— 材料A・2回目

```
GETも404のものだけがリンク切れです。該当は次の10件です。

- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

数えると8件でした。先ほど「10件」と書いたのは誤りで、正しくは上記の8件です。

**切れていないリンクの内訳**
- HEAD=404でもGET=200のもの(L04、L08、L13、L18)は、HEADに対応していないだけで、リンクは生きています。
- GET=403のもの(L05、L10、L15、L20)は、404ではないので、ご指定の基準では「切れている」とは判断しません。ただ、アクセス制限やボット対策でブロックされている可能性があります。ブラウザで実際に開けるか、一度確認すると安心です。
- 両方200のもの(L02、L06、L11、L16)は正常です。

**傾向**
リンク切れは `soil-mix-notes.jp` の4件(L03、L09、L14、L19)と `plant-almanac-notes.jp` の3件(L07、L12、L17)に集中しています。サイト構成やURLの変更が起きた可能性があるので、新しいURLへの差し替えやアーカイブの利用を検討してください。
```

### 返ってきたもの（生）— 材料B・1回目

```
ご指定の基準（GETも404の場合だけリンク切れ）で判定すると、リンク切れは次の7件です。

| ID | URL | HEAD | GET |
|---|---|---|---|
| L01 | https://run-log-diary.jp/2020/race-report-spring | 404 | 404 |
| L03 | https://pace-chart-notes.jp/archive/2019/interval | 404 | 404 |
| L07 | https://pace-chart-notes.jp/archive/2018/tempo-run | 404 | 404 |
| L09 | https://run-log-diary.jp/2019/injury-recovery | 404 | 404 |
| L12 | https://pace-chart-notes.jp/archive/2020/fartlek | 404 | 404 |
| L14 | https://run-log-diary.jp/2021/winter-training | 404 | 404 |
| L17 | https://pace-chart-notes.jp/archive/2017/long-run | 404 | 404 |
| L19 | https://run-log-diary.jp/2018/first-marathon | 404 | 404 |

（訂正：数えると8件です。L01、L03、L07、L09、L12、L14、L17、L19の8件がリンク切れです。）

**リンク切れではないもの**
- L04、L08、L13、L18（marathon-faq.jp）：HEADは404ですが、GETは200なので生きています。
- L02、L06、L11、L16：HEAD・GETとも200で正常です。
- L05、L10、L15、L20（sports-gear-outlet.jp）：HEAD・GETとも403です。基準では「GETも404の場合だけ」リンク切れなので、リンク切れには含めていません。ただし、アクセス制限やボット対策でブロックされている可能性があります。ブラウザで実際に開けるか、一度確認することをおすすめします。

**傾向**
リンク切れ8件は、run-log-diary.jp（4件）と pace-chart-notes.jp（4件）の過去記事に集中しています。サイト側で古い記事が削除されたか、URLの構成が変わったのかもしれません。
```

### 返ってきたもの（生）— 材料B・2回目

```
ご指定の基準(GETも404の場合のみ切れている)で判定すると、リンク切れは次の7件です。

- L01 https://run-log-diary.jp/2020/race-report-spring (HEAD=404 / GET=404)
- L03 https://pace-chart-notes.jp/archive/2019/interval (HEAD=404 / GET=404)
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run (HEAD=404 / GET=404)
- L09 https://run-log-diary.jp/2019/injury-recovery (HEAD=404 / GET=404)
- L12 https://pace-chart-notes.jp/archive/2020/fartlek (HEAD=404 / GET=404)
- L14 https://run-log-diary.jp/2021/winter-training (HEAD=404 / GET=404)
- L17 https://pace-chart-notes.jp/archive/2017/long-run (HEAD=404 / GET=404)
- L19 https://run-log-diary.jp/2018/first-marathon (HEAD=404 / GET=404)

訂正します。数え直すと8件でした(L01、L03、L07、L09、L12、L14、L17、L19)。

補足です。

- **切れていない扱い**: L04、L08、L13、L18 は HEAD=404 ですが GET=200 なので、リンクは生きています。
- **404ではないもの**: L05、L10、L15、L20 は HEAD・GET ともに 403 です。基準上は「GETも404の場合のみ切れている」ので、リンク切れには含めていません。ただし、アクセス拒否(ボット対策や会員限定など)の可能性があるため、ブラウザで一度確認すると安心です。
- **正常**: L02、L06、L11、L16 は HEAD・GET ともに 200 です。

なお、リンク切れはドメイン別では run-log-diary.jp が4件、pace-chart-notes.jp が4件です。
```

### 照合（機械）

```
4回とも、brokenとして最終的に列挙したIDは真のa(8件)と完全一致（分類ミスは0/4）。
⚠️ ただし4回とも、見出しに書いた最初の件数が実際の列挙件数(8)と食い違い、本文中で自己訂正した（miscount=4/4）。
V2_A_r1: 「該当は次の10件です」→列挙8件→「数えると8件でした。訂正します。」
V2_A_r2: 「該当は次の10件です」→列挙8件→「数えると8件でした。先ほど『10件』と書いたのは誤りで、正しくは上記の8件です。」
V2_B_r1: 「リンク切れは次の7件です」→列挙8件→「（訂正：数えると8件です。...)」
V2_B_r2: 「リンク切れは次の7件です」→列挙8件→「訂正します。数え直すと8件でした。」
```

### 判定

**採用**（記事「言い直し方」の最初の例・見出しの件数がずれる現象を示す）。分類の正しさとは別に、見出しの件数だけが毎回ずれた。

---

## 指示文5（記事：言い直し方・確認できないリンクを分ける）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETも404の場合は、切れていると判断してください。GETが200でも404でもない場合（403など）は、サーバーがロボットを拒否している可能性があり、人がブラウザで開けば中身を見られることがあります。この場合は切れているとは断定せず、確認できないリンクとして分けてください。この基準で、切れているリンクと確認できないリンクを、それぞれ教えてください。
```
このあとに空行を挟んで、点検結果の一覧（HEADとGETの両方の応答コード）をそのまま貼って送った。

### 返ってきたもの（生）— 材料A・1回目

```
ご指定の基準（GETが404なら切れている、GETが200なら生きている、それ以外は確認できない）で分けました。

## 切れているリンク（GETも404）：8件
- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

## 確認できないリンク（GETが403）：4件
サーバーがロボットを拒否している可能性があります。切れているとは断定せず、ブラウザで開いて確認してください。
- L05 https://garden-supply-co.jp/products/pot-01
- L10 https://garden-supply-co.jp/products/mister-02
- L15 https://garden-supply-co.jp/products/shelf-03
- L20 https://garden-supply-co.jp/products/tray-04

## 参考：切れていないリンク（8件）
- GET=200で正常：L02、L06、L11、L16
- HEADは404だがGETが200なので正常：L04、L08、L13、L18

確認できないリンクはすべて garden-supply-co.jp のものです。同じドメインで一律に403なので、ロボット対策の可能性が高そうです。
```

### 返ってきたもの（生）— 材料A・2回目

```
## 切れているリンク（GETも404）：9件

- L01 https://green-room-note.jp/entry/2021/leaf-care
- L03 https://soil-mix-notes.jp/archive/2020/repotting
- L07 https://plant-almanac-notes.jp/guide/fertilizer
- L09 https://soil-mix-notes.jp/archive/2019/drainage
- L12 https://plant-almanac-notes.jp/guide/pruning
- L14 https://soil-mix-notes.jp/archive/2021/fungus
- L17 https://plant-almanac-notes.jp/guide/species-list
- L19 https://soil-mix-notes.jp/archive/2022/root-rot

数え直すと8件です（上記の8件が正しい件数です）。

## 確認できないリンク（GETが403）：3件

サーバーがロボットを拒否している可能性があります。ブラウザで開いて確認してください。

- L05 https://garden-supply-co.jp/products/pot-01
- L10 https://garden-supply-co.jp/products/mister-02
- L15 https://garden-supply-co.jp/products/shelf-03
- L20 https://garden-supply-co.jp/products/tray-04

こちらも数え直すと4件です。

## 参考：切れていないリンク

- GETが200：L02、L04、L06、L08、L11、L13、L16、L18
- このうちL04、L08、L13、L18はHEADが404でしたが、GETが200なので切れていません。

## 集計

- 切れている：8件
- 確認できない：4件
- 問題なし：8件
- 合計：20件

見出しの件数（9件、3件）に誤りがありました。正しくは、切れているリンクが8件、確認できないリンクが4件です。
```

### 返ってきたもの（生）— 材料B・1回目

```
ご指定の基準で分類した結果は次のとおりです。

## 切れているリンク（GETが404）：8件

- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L19 https://run-log-diary.jp/2018/first-marathon

## 確認できないリンク（GETが403）：4件

サーバーがロボットを拒否している可能性があります。切れているとは断定できないため、ブラウザで開いて確認してください。

- L05 https://sports-gear-outlet.jp/items/belt-02
- L10 https://sports-gear-outlet.jp/items/watch-05
- L15 https://sports-gear-outlet.jp/items/socks-03
- L20 https://sports-gear-outlet.jp/items/cap-04

## 補足（問題なしと判断したリンク：8件）

- GETが200で、HEADは404だったもの（切れていません）：L04、L08、L13、L18（いずれも marathon-faq.jp）
- HEAD、GETともに200だったもの：L02、L06、L11、L16

## 傾向

- 切れているリンクは、run-log-diary.jp の旧記事（2018〜2021年）と pace-chart-notes.jp のアーカイブ（2017〜2020年）に集中しています。サイト側で古い記事が削除されたか、URLが変わった可能性があります。
- sports-gear-outlet.jp は4件すべて403なので、サイト全体でボット対策が働いているのかもしれません。
```

### 返ってきたもの（生）— 材料B・2回目

```
ご指定の基準で分類しました。

## 切れているリンク（GETも404）：9件
- L01 https://run-log-diary.jp/2020/race-report-spring
- L03 https://pace-chart-notes.jp/archive/2019/interval
- L07 https://pace-chart-notes.jp/archive/2018/tempo-run
- L09 https://run-log-diary.jp/2019/injury-recovery
- L12 https://pace-chart-notes.jp/archive/2020/fartlek
- L14 https://run-log-diary.jp/2021/winter-training
- L17 https://pace-chart-notes.jp/archive/2017/long-run
- L19 https://run-log-diary.jp/2018/first-marathon

（数え直すと8件です。上記の8件が正しい件数で、「9件」は誤記でした。）

## 確認できないリンク（GETが403）：4件
サーバーがロボットを拒否している可能性があるため、切れているとは断定せず、ブラウザで開いて確認してください。
- L05 https://sports-gear-outlet.jp/items/belt-02
- L10 https://sports-gear-outlet.jp/items/watch-05
- L15 https://sports-gear-outlet.jp/items/socks-03
- L20 https://sports-gear-outlet.jp/items/cap-04

## 参考：切れていないリンク
- HEADは404ですが、GETが200のため問題ありません（3件）：L04、L08、L13、L18 → 正しくは4件です。
- HEAD・GETともに200（4件）：L02、L06、L11、L16

内訳は、切れている8件、確認できない4件、切れていない8件で、合計20件です。
```

### 照合（機械）

```
4回とも、broken=真のa(8件)・unconfirmed=真のc(4件)と完全一致（分類ミスは0/4）。
見出しの件数の食い違いは4回中2回に減ったが、消えなかった（miscount=2/4）。
V3_A_r1: 「切れているリンク(GETも404)：8件」正しい。「確認できないリンク(GETが403)：4件」正しい。食い違い無し。
V3_A_r2: 「切れているリンク(GETも404)：9件」→列挙8件→訂正「数え直すと8件です」。「確認できないリンク(GETが403)：3件」→列挙4件→訂正「こちらも数え直すと4件です」。2箇所で食い違い。
V3_B_r1: 「切れているリンク(GETが404)：8件」正しい。「確認できないリンク(GETが403)：4件」正しい。食い違い無し。
V3_B_r2: 「切れているリンク(GETも404)：9件」→列挙8件→訂正。「HEADは404ですが、GETが200のため問題ありません(3件)」→列挙4件→「→正しくは4件です」。2箇所で食い違い。
```

### 判定

**採用**（記事「言い直し方」2番目の例）。受け皿を増やしても、見出しの件数の食い違いは半分には減るが消えないことを示す。

---

## 指示文6（記事：言い直し方・件数は名前を挙げたあとに書かせる）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETも404の場合は、切れていると判断してください。GETが200でも404でもない場合（403など）は、サーバーがロボットを拒否している可能性があり、人がブラウザで開けば中身を見られることがあります。この場合は切れているとは断定せず、確認できないリンクとして分けてください。

まず、切れているリンクのIDだけを箇条書きで全部挙げてください。件数はまだ書かないでください。箇条書きが終わったら、最後に「以上、何件」と書いてください。確認できないリンクも同じ形で、先にIDを全部挙げてから、最後に件数を書いてください。
```
このあとに空行を挟んで、点検結果の一覧（HEADとGETの両方の応答コード）をそのまま貼って送った。

### 返ってきたもの（生）— 材料A・1回目

```
**切れているリンク（HEAD・GETともに404）**

- L01
- L03
- L07
- L09
- L12
- L14
- L17
- L19

以上、8件

**確認できないリンク（GETが403で、ロボット拒否の可能性あり）**

- L05
- L10
- L15
- L20

以上、4件

なお、L04・L08・L13・L18はHEADが404でもGETが200なので、切れていません。L02・L06・L11・L16も正常です。
```

### 返ってきたもの（生）— 材料A・2回目

```
**切れているリンク**

- L01
- L03
- L07
- L09
- L12
- L14
- L17
- L19

以上、8件

**確認できないリンク**（GETが403で、サーバーがロボットを拒否している可能性があるもの）

- L05
- L10
- L15
- L20

以上、4件

なお、残りの8件（L02、L04、L06、L08、L11、L13、L16、L18）はGETが200のため、切れていません。L04、L08、L13、L18はHEADが404でしたが、GETが200なので問題ありません。
```

### 返ってきたもの（生）— 材料B・1回目

```
分類は、GETの応答コードで行いました。

**切れているリンク（GET=404）**
- L01
- L03
- L07
- L09
- L12
- L14
- L17
- L19

以上、8件

**確認できないリンク（GETが200でも404でもない。今回はすべて403）**
- L05
- L10
- L15
- L20

以上、4件

**参考：切れていないリンク**
HEADが404でもGETが200のL04、L08、L13、L18は、切れていません。HEADとGETがともに200のL02、L06、L11、L16も問題ありません。
```

### 返ってきたもの（生）— 材料B・2回目

```
分類は、GETの応答コードだけで行いました。

**切れているリンク（GETが404）**
- L01
- L03
- L07
- L09
- L12
- L14
- L17
- L19

以上、8件

**確認できないリンク（GETが403）**
- L05
- L10
- L15
- L20

以上、4件

なお、L04・L08・L13・L18はHEADが404でもGETが200なので、切れていません。L02・L06・L11・L16も正常です。
```

### 照合（機械）

```
4回とも、broken=真のa(8件)・unconfirmed=真のc(4件)と完全一致（分類ミスは0/4）。
4回とも、「以上、8件」「以上、4件」という見出しの件数が、実際に列挙した件数と完全一致（miscount=0/4）。
V4_A_r1: 「以上、8件」（列挙8件・一致）「以上、4件」（列挙4件・一致）
V4_A_r2: 「以上、8件」（一致）「以上、4件」（一致）
V4_B_r1: 「以上、8件」（一致）「以上、4件」（一致）
V4_B_r2: 「以上、8件」（一致）「以上、4件」（一致）
```

### 判定

**採用**（記事「言い直し方」最後の例・保存版）。件数を先に宣言させず、列挙のあとに回すだけで、見出しの食い違いが4回中0回に消えた。

---

## この記事から出た教訓（`content/_lessons.md` へ）


1. HEADリクエストだけでリンク切れを判定すると、HEADには404を返すがGETには200を返す生きているページを「切れている」に含めてしまう（2材料×各2回＝4回とも、4件全部が混入）。GETの応答コードも渡すだけで、数字の判定基準を指示しなくても誤判定は0回に消える。
2. ★297・★300系の「見出しの件数と実際の列挙件数が食い違う」現象が、リンク点検という別領域でも、しかもずっと高い頻度で再現した。判断基準を数字で明示した指示文（「GETも404の場合だけ」）では4回中4回、「確認できない」の受け皿を足すと4回中2回、どちらも見出しの件数が実際の列挙とずれ、本文中で自己訂正していた。基準を数字にすることが、むしろ見出しの集計を狂わせる方向に働いた。
3. 2の食い違いは、受け皿を増やしても消えなかったが、「名前を全部挙げたあとに件数を書く」と指示順序を変えるだけで4回中0回に消えた。件数を先に宣言させる言い方そのものが、ズレの引き金だった可能性が高い。
