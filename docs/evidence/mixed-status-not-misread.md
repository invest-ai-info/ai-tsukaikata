# 試した証拠 — mixed-status-not-misread

記事に載せる指示文すべてについて、この形式で残す。

⚠️ このファイルは `content/` の中に置いていない（ビルド除外はファイル名の `_` 判定のため）。

実測日: 2026-11-03。実測の相手＝`claude --safe-mode --tools ""`（CLAUDE.md・skills・plugins・
履歴を全部無効化した新規プロセス。呼び出しごとに完全に独立したプロセス）。

[リンク切れ点検の判断をAIに任せる](../../content/recipes/head-only-flags-live-pages-as-broken.md)
の続き。あちらは404・403・200の組み合わせだけを試した。この記事は、あちらが最後に残した
宿題（301・302・タイムアウト・500番台を混ぜたらどうなるか）に答える。

---

## 教材（架空データ）

架空のブログに貼ったリンク一覧、12本×2材料。各材料の構成は共通で、
**本当に切れている(a)2本・正常(d)2本・403でボット判定の可能性(c)2本・
恒久転送301(e1)2本・一時転送302(e2)2本・タイムアウト(f)2本・サーバーエラー500/503(g)2本**。

### 材料C（資格試験の勉強ブログのリンク一覧）

```
L01  https://exam-prep-notes.jp/2020/past-paper-review  HEAD=404  GET=404
L02  https://study-method-hub.jp/guide/spaced-repetition  HEAD=200  GET=200
L03  https://license-archive-notes.jp/2019/mock-test  HEAD=404  GET=404
L04  https://exam-prep-notes.jp/2021/schedule-template  HEAD=200  GET=200
L05  https://cert-gear-store.jp/items/timer-01  HEAD=403  GET=403
L06  https://cert-gear-store.jp/items/binder-02  HEAD=403  GET=403
L07  https://study-method-hub.jp/guide/old-syllabus  HEAD=301  GET=301
L08  https://license-archive-notes.jp/archive/2018/intro  HEAD=302  GET=302
L09  https://exam-prep-notes.jp/2022/mentor-interview  HEAD=タイムアウト  GET=タイムアウト
L10  https://cert-gear-store.jp/items/desk-lamp-03  HEAD=タイムアウト  GET=タイムアウト
L11  https://study-method-hub.jp/guide/burnout-signs  HEAD=500  GET=500
L12  https://license-archive-notes.jp/2020/renewal-steps  HEAD=503  GET=503
```

真値＝a(本当に切れている): L01, L03 / d(正常): L02, L04 / c(403): L05, L06 /
e(転送301/302): L07, L08 / f(タイムアウト): L09, L10 / g(5xx): L11, L12

### 材料D（手作りお菓子レシピブログのリンク一覧）

```
L01  https://home-baking-journal.jp/2019/sugar-ratio-fail  HEAD=404  GET=404
L02  https://pastry-basics-notes.jp/guide/oven-temp-check  HEAD=200  GET=200
L03  https://flour-type-archive.jp/2018/cake-flour-swap  HEAD=404  GET=404
L04  https://home-baking-journal.jp/2021/holiday-cookie-plan  HEAD=200  GET=200
L05  https://baking-tool-outlet.jp/items/scale-01  HEAD=403  GET=403
L06  https://baking-tool-outlet.jp/items/mixer-02  HEAD=403  GET=403
L07  https://pastry-basics-notes.jp/guide/old-measurement-chart  HEAD=301  GET=301
L08  https://flour-type-archive.jp/archive/2017/starter-guide  HEAD=302  GET=302
L09  https://home-baking-journal.jp/2022/guest-contributor-notes  HEAD=タイムアウト  GET=タイムアウト
L10  https://baking-tool-outlet.jp/items/thermometer-03  HEAD=タイムアウト  GET=タイムアウト
L11  https://pastry-basics-notes.jp/guide/humidity-adjustment  HEAD=500  GET=500
L12  https://flour-type-archive.jp/2020/sourdough-faq  HEAD=503  GET=503
```

真値＝a(本当に切れている): L01, L03 / d(正常): L02, L04 / c(403): L05, L06 /
e(転送301/302): L07, L08 / f(タイムアウト): L09, L10 / g(5xx): L11, L12

---

## 指示文1（記事：AIへの頼み方 1・基準を渡さず素朴に聞く）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。この中でリンク切れになっているものを教えてください。
```

### 返ってきたもの（生）— 材料C・1回目

```
結果から判断すると、リンク切れと確定できるものと、要確認のものに分かれます。

**リンク切れ(確定)**
- L01 `exam-prep-notes.jp/2020/past-paper-review` — 404
- L03 `license-archive-notes.jp/2019/mock-test` — 404

HEAD・GETの両方で404なので、ページ自体が存在しません。差し替えか削除が必要です。

**要確認(リンク切れの可能性あり)**
- L07 `study-method-hub.jp/guide/old-syllabus` — 301(恒久移転)
- L08 `license-archive-notes.jp/archive/2018/intro` — 302(一時転送)

リダイレクト自体は切れではありませんが、転送先が404だったり、トップページに飛ばされるだけの場合は実質的なリンク切れです。転送先を確認してください。L07は新URLに更新するのが望ましいです。

- L09 `exam-prep-notes.jp/2022/mentor-interview` — タイムアウト
- L10 `cert-gear-store.jp/items/desk-lamp-03` — タイムアウト

一時的な障害の可能性があります。日を改めて再チェックし、続くようなら切れとして扱ってください。

- L11 `study-method-hub.jp/guide/burnout-signs` — 500
- L12 `license-archive-notes.jp/2020/renewal-steps` — 503

サーバー側のエラーで、一時的な不具合のことが多いです。再試行して解消しなければ対応を検討してください。

- L05 `cert-gear-store.jp/items/timer-01` — 403
- L06 `cert-gear-store.jp/items/binder-02` — 403

アクセス拒否で、ページが存在しないとは限りません。自動アクセス(ボット)をブロックしている可能性があるので、ブラウザで実際に開いて確認してください。同一サイトのL10もタイムアウトなので、cert-gear-store.jp全体がボットを弾いているか、サイト自体に問題がある可能性もあります。

**正常**
- L02、L04 — 200

**まとめ**:確実に切れているのはL01とL03の2件です。他の8件(L05〜L12)は再確認が必要で、特にL07・L08は転送先のチェックが重要です。
```

### 返ってきたもの（生）— 材料C・2回目

```
結果から判断すると、リンク切れと言えるものは次のとおりです。

## 確実にリンク切れ(修正・削除が必要)
| ID | URL | 状態 |
|---|---|---|
| L01 | exam-prep-notes.jp/2020/past-paper-review | 404 |
| L03 | license-archive-notes.jp/2019/mock-test | 404 |

HEAD・GETの両方で404なので、ページが存在しません。

## ほぼリンク切れ(要確認・対応推奨)
| ID | URL | 状態 | 理由 |
|---|---|---|---|
| L07 | study-method-hub.jp/guide/old-syllabus | 301 | 移転済み。転送先URLに更新が必要 |
| L08 | license-archive-notes.jp/archive/2018/intro | 302 | 一時転送。転送先が有効か確認し、可能なら更新 |

リダイレクト自体は閲覧できる可能性が高いですが、転送先が404やトップページになっていないかの確認が必要です。

## 判断保留(一時的な障害の可能性あり)
| ID | URL | 状態 | 理由 |
|---|---|---|---|
| L09 | exam-prep-notes.jp/2022/mentor-interview | タイムアウト | サーバー負荷や一時的な障害の可能性 |
| L10 | cert-gear-store.jp/items/desk-lamp-03 | タイムアウト | 同上 |
| L11 | study-method-hub.jp/guide/burnout-signs | 500 | サーバーエラー |
| L12 | license-archive-notes.jp/2020/renewal-steps | 503 | 一時的な利用不可 |

日を改めて再チェックし、継続して失敗するなら切れと判断してください。

## 問題なしの可能性が高い
| ID | URL | 状態 | 理由 |
|---|---|---|---|
| L05 | cert-gear-store.jp/items/timer-01 | 403 | ボット対策によるアクセス拒否の可能性。ブラウザで実際に開いて確認 |
| L06 | cert-gear-store.jp/items/binder-02 | 403 | 同上 |

## 正常
- L02、L04(200)

## まとめ
- **確定:** L01、L03
- **要対応(リダイレクト):** L07、L08
- **再確認:** L09〜L12
- **ブラウザで目視確認:** L05、L06
```

### 返ってきたもの（生）— 材料D・1回目

```
結果から判断すると、**明確にリンク切れ**なのは次の2件です。

| ID | URL | 状態 |
|----|-----|------|
| L01 | https://home-baking-journal.jp/2019/sugar-ratio-fail | 404 |
| L03 | https://flour-type-archive.jp/2018/cake-flour-swap | 404 |

**要確認(リンク切れと断定できないもの)**

- **L05, L06(403)**: baking-tool-outlet.jp はアクセスを拒否しています。ページ自体は存在していて、自動アクセスをブロックしている可能性があります。ブラウザで実際に開いて確認してください。
- **L09, L10(タイムアウト)**: 一時的な障害の可能性があります。時間を置いて再チェックし、それでも繋がらなければ切れていると判断してよいでしょう。
- **L11(500), L12(503)**: サーバー側のエラーです。特に503は一時的なメンテナンスや過負荷であることが多いので、再チェックをおすすめします。

**問題なし(ただし修正推奨)**

- **L07(301), L08(302)**: リダイレクトされており、転送先が正常ならリンクは機能しています。ただしL07は恒久的な移転なので、リンク先を新URLに更新しておくと安心です。L08は一時的な転送なので、転送先を確認しておくとよいでしょう。

**問題なし**: L02, L04(200)

まとめると、確実に直すべきなのはL01とL03で、L05・L06・L09〜L12は再確認してから判断するのがよいと思います。
```

### 返ってきたもの（生）— 材料D・2回目

```
結果から判断すると、リンク切れと言えるのは次のものです。

**確実にリンク切れ(404)**
- L01 `home-baking-journal.jp/2019/sugar-ratio-fail`
- L03 `flour-type-archive.jp/2018/cake-flour-swap`

**リンク切れの可能性が高く、要再確認**
- L11 `pastry-basics-notes.jp/guide/humidity-adjustment`(500):サーバー側エラー。一時的な不具合かもしれませんが、恒久的ならページ自体が壊れています。
- L12 `flour-type-archive.jp/2020/sourdough-faq`(503):一時的なメンテナンスや過負荷の可能性が高いので、日を改めて再確認してください。
- L09 `home-baking-journal.jp/2022/guest-contributor-notes`(タイムアウト)
- L10 `baking-tool-outlet.jp/items/thermometer-03`(タイムアウト)

タイムアウトや5xxは一時的な障害でも起こるため、複数回・時間をずらして再チェックし、続くようなら切れていると判断するのが安全です。

**リンク切れではない(ただし確認が望ましい)**
- L05、L06(403):`baking-tool-outlet.jp` はアクセス拒否で、自動チェックのBot対策に弾かれている可能性があります。ブラウザで開いて表示されるなら問題ありません。
- L07(301)、L08(302):リダイレクトで、転送先が正常ならリンクは生きています。ただし L07 は「old」と付いているので、新URLへ書き換えておくと良いです。

**正常**
- L02、L04(200)

まとめると、確定は2件(L01、L03)、再確認が必要なのは4件(L09〜L12)、手動確認が望ましいのは403の2件(L05、L06)です。
```

### 照合（機械）

| 回 | 「確実に切れている」に入った件 | 真値a | 誤分類（a以外が確実側に混入） | バケツの数 |
|---|---|---|---|---|
| C-1 | L01, L03 | L01, L03 ✅ | 0件 | 2種（リンク切れ確定／要確認） |
| C-2 | L01, L03 | L01, L03 ✅ | 0件 | 5種 |
| D-1 | L01, L03 | L01, L03 ✅ | 0件 | 4種 |
| D-2 | L01, L03 | L01, L03 ✅ | 0件 | 4種 |

4回とも誤分類は0件。バケツの数は2・5・4・4と回によって異なり、同じL07(301)がC-2では「ほぼリンク切れ」、D-2では「リンク切れではない」という別の性質のバケツに入った。

### 判定

**採用**（誤分類は無いが、出力の形が不安定であることを示す材料として）。

---

## 指示文2（記事：AIへの頼み方 2・保存版の基準をそのまま使う）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETも404の場合は、切れていると判断してください。GETが200でも404でもない場合（403など）は、サーバーがロボットを拒否している可能性があり、人がブラウザで開けば中身を見られることがあります。この場合は切れているとは断定せず、確認できないリンクとして分けてください。この基準で、切れているリンクと確認できないリンクを、それぞれ教えてください。
```

### 返ってきたもの（生）— 材料C・1回目

```
## 切れているリンク（GETが404）: 2件

| ID | URL |
|---|---|
| L01 | https://exam-prep-notes.jp/2020/past-paper-review |
| L03 | https://license-archive-notes.jp/2019/mock-test |

## 確認できないリンク（GETが200でも404でもない）: 8件

切れているとは断定できず、ブラウザでの目視確認が必要です。

| ID | URL | GET | 補足 |
|---|---|---|---|
| L05 | https://cert-gear-store.jp/items/timer-01 | 403 | ロボット拒否の可能性 |
| L06 | https://cert-gear-store.jp/items/binder-02 | 403 | ロボット拒否の可能性 |
| L07 | https://study-method-hub.jp/guide/old-syllabus | 301 | 転送。転送先を確認 |
| L08 | https://license-archive-notes.jp/archive/2018/intro | 302 | 転送。転送先を確認 |
| L09 | https://exam-prep-notes.jp/2022/mentor-interview | タイムアウト | 一時的な可能性 |
| L10 | https://cert-gear-store.jp/items/desk-lamp-03 | タイムアウト | 一時的な可能性 |
| L11 | https://study-method-hub.jp/guide/burnout-signs | 500 | サーバーエラー |
| L12 | https://license-archive-notes.jp/2020/renewal-steps | 503 | 一時的な停止の可能性 |

## 問題なし（GETが200）: 2件
L02, L04

ご指定の基準を厳密に適用したため、リダイレクト（301/302）、タイムアウト、5xxもすべて「確認できない」に入れています。このうち301/302は転送先が生きていれば問題ないことが多く、タイムアウトや5xxは時間をおいて再チェックすると判定できる場合があります。同じサイトでまとまって失敗している点（cert-gear-store.jp の3件など）も、サイト側の一時的な問題かボット拒否の目安になります。
```

### 返ってきたもの（生）— 材料C・2回目

```
## 切れているリンク（GETが404）: 2件

| ID | URL |
|---|---|
| L01 | https://exam-prep-notes.jp/2020/past-paper-review |
| L03 | https://license-archive-notes.jp/2019/mock-test |

## 確認できないリンク（GETが200でも404でもない）: 8件

| ID | URL | GET | 内訳 |
|---|---|---|---|
| L05 | https://cert-gear-store.jp/items/timer-01 | 403 | ロボット拒否の可能性 |
| L06 | https://cert-gear-store.jp/items/binder-02 | 403 | ロボット拒否の可能性 |
| L07 | https://study-method-hub.jp/guide/old-syllabus | 301 | 恒久的な転送 |
| L08 | https://license-archive-notes.jp/archive/2018/intro | 302 | 一時的な転送 |
| L09 | https://exam-prep-notes.jp/2022/mentor-interview | タイムアウト | 応答なし |
| L10 | https://cert-gear-store.jp/items/desk-lamp-03 | タイムアウト | 応答なし |
| L11 | https://study-method-hub.jp/guide/burnout-signs | 500 | サーバーエラー |
| L12 | https://license-archive-notes.jp/2020/renewal-steps | 503 | 一時的に利用不可 |

## 問題なし（GETが200）: 2件
L02、L04

## 補足
ご指定の基準どおり、200と404以外はすべて「確認できない」に入れています。ただ、中身は性質が異なるので、確認の優先度は次のように考えるとよいと思います。

- **L07、L08（転送）**: 転送先まで追えば判定できる可能性が高いです。転送先が200なら問題なし、404なら切れています。L07は恒久転送なので、リンクを新URLに差し替えるのがおすすめです。
- **L05、L06（403）**: ブラウザで開いて確認してください。
- **L09〜L12（タイムアウト、5xx）**: 一時的な障害の可能性があるので、時間を置いて再点検するのが確実です。
```

### 返ってきたもの（生）— 材料D・1回目

```
## 切れているリンク（GETが404）: 2件

| ID | URL |
|---|---|
| L01 | https://home-baking-journal.jp/2019/sugar-ratio-fail |
| L03 | https://flour-type-archive.jp/2018/cake-flour-swap |

## 確認できないリンク（GETが200でも404でもない）: 8件

| ID | URL | 応答 |
|---|---|---|
| L05 | https://baking-tool-outlet.jp/items/scale-01 | 403 |
| L06 | https://baking-tool-outlet.jp/items/mixer-02 | 403 |
| L07 | https://pastry-basics-notes.jp/guide/old-measurement-chart | 301 |
| L08 | https://flour-type-archive.jp/archive/2017/starter-guide | 302 |
| L09 | https://home-baking-journal.jp/2022/guest-contributor-notes | タイムアウト |
| L10 | https://baking-tool-outlet.jp/items/thermometer-03 | タイムアウト |
| L11 | https://pastry-basics-notes.jp/guide/humidity-adjustment | 500 |
| L12 | https://flour-type-archive.jp/2020/sourdough-faq | 503 |

## 問題なし（GETが200）: 2件
L02、L04
```

### 返ってきたもの（生）— 材料D・2回目

```
## 切れているリンク（GETが404）: 2件

| ID | URL | HEAD / GET |
|---|---|---|
| L01 | https://home-baking-journal.jp/2019/sugar-ratio-fail | 404 / 404 |
| L03 | https://flour-type-archive.jp/2018/cake-flour-swap | 404 / 404 |

## 確認できないリンク（GETが200でも404でもない）: 8件

切れているとは断定できません。内訳は次のとおりです。

**403（ロボット拒否の可能性）**
- L05 https://baking-tool-outlet.jp/items/scale-01 (403 / 403)
- L06 https://baking-tool-outlet.jp/items/mixer-02 (403 / 403)

**リダイレクト（301/302）**
- L07 https://pastry-basics-notes.jp/guide/old-measurement-chart (301 / 301)
- L08 https://flour-type-archive.jp/archive/2017/starter-guide (302 / 302)

**タイムアウト**
- L09 https://home-baking-journal.jp/2022/guest-contributor-notes
- L10 https://baking-tool-outlet.jp/items/thermometer-03

**サーバーエラー（500/503）**
- L11 https://pastry-basics-notes.jp/guide/humidity-adjustment (500 / 500)
- L12 https://flour-type-archive.jp/2020/sourdough-faq (503 / 503)

## 正常なリンク（200）: 2件
L02、L04
```

### 照合（機械）

4回とも「切れている」2件・「確認できない」8件・「正常」2件の、同じ形に分かれた。
301・302・タイムアウト・500・503は4回とも「確認できない」に入り、「切れている」に混ざった回は0回。

### 判定

**採用**。基準を変えずに流用するだけで、出力の形も安定した。

---

## 指示文3（記事：AIへの頼み方 3・確認できないを4種に分ける）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETも404の場合は、切れていると判断してください。GETが200でも404でもない場合は、切れているとは断定せず、確認できないリンクとして分けてください。確認できないリンクは、さらに次の4種類に分けてください。①転送（301・302）②タイムアウト（応答なし）③サーバーエラー（500番台）④その他（403など）。この基準で、切れているリンクと、確認できないリンクの4種類を、それぞれ教えてください。
```

### 返ってきたもの（生）— 材料C・1回目

```
## 判定結果

### 切れているリンク(GETが404)
- **L01** https://exam-prep-notes.jp/2020/past-paper-review
- **L03** https://license-archive-notes.jp/2019/mock-test

### 切れていないリンク(GETが200)
- L02、L04

### 確認できないリンク(GETが200でも404でもない)

**① 転送(301・302)**
- **L07** https://study-method-hub.jp/guide/old-syllabus(301)
- **L08** https://license-archive-notes.jp/archive/2018/intro(302)

**② タイムアウト(応答なし)**
- **L09** https://exam-prep-notes.jp/2022/mentor-interview
- **L10** https://cert-gear-store.jp/items/desk-lamp-03

**③ サーバーエラー(500番台)**
- **L11** https://study-method-hub.jp/guide/burnout-signs(500)
- **L12** https://license-archive-notes.jp/2020/renewal-steps(503)

**④ その他(403など)**
- **L05** https://cert-gear-store.jp/items/timer-01(403)
- **L06** https://cert-gear-store.jp/items/binder-02(403)

### 集計
切れている 2件 / 切れていない 2件 / 確認できない 8件(転送2・タイムアウト2・サーバーエラー2・その他2)

L05・L06は、HEADもGETも403なので「切れていない」とは言えず、確認できないリンクとして分類しています。
```

### 返ってきたもの（生）— 材料C・2回目

```
## 切れているリンク（GETも404）：3件

- L01 https://exam-prep-notes.jp/2020/past-paper-review
- L03 https://license-archive-notes.jp/2019/mock-test

（訂正：該当は上記の **2件** です。）

## 切れていないリンク（GET=200）：2件
- L02、L04

## 確認できないリンク：8件

**① 転送（301・302）：2件**
- L07 https://study-method-hub.jp/guide/old-syllabus（301）
- L08 https://license-archive-notes.jp/archive/2018/intro（302）

**② タイムアウト（応答なし）：2件**
- L09 https://exam-prep-notes.jp/2022/mentor-interview
- L10 https://cert-gear-store.jp/items/desk-lamp-03

**③ サーバーエラー（500番台）：2件**
- L11 https://study-method-hub.jp/guide/burnout-signs（500）
- L12 https://license-archive-notes.jp/2020/renewal-steps（503）

**④ その他（403など）：2件**
- L05 https://cert-gear-store.jp/items/timer-01（403）
- L06 https://cert-gear-store.jp/items/binder-02（403）

最初の見出しで件数を「3件」と書いてしまいましたが、正しくは2件です（L01、L03）。
```

### 返ってきたもの（生）— 材料D・1回目

```
## 切れているリンク（GETも404）

- L01 https://home-baking-journal.jp/2019/sugar-ratio-fail
- L03 https://flour-type-archive.jp/2018/cake-flour-swap

## 確認できないリンク

**① 転送（301・302）**
- L07 https://pastry-basics-notes.jp/guide/old-measurement-chart（301）
- L08 https://flour-type-archive.jp/archive/2017/starter-guide（302）

**② タイムアウト（応答なし）**
- L09 https://home-baking-journal.jp/2022/guest-contributor-notes
- L10 https://baking-tool-outlet.jp/items/thermometer-03

**③ サーバーエラー（500番台）**
- L11 https://pastry-basics-notes.jp/guide/humidity-adjustment（500）
- L12 https://flour-type-archive.jp/2020/sourdough-faq（503）

**④ その他（403など）**
- L05 https://baking-tool-outlet.jp/items/scale-01（403）
- L06 https://baking-tool-outlet.jp/items/mixer-02（403）

## 切れていない（GETが200）
- L02、L04

HEADとGETの結果はどのリンクでも一致していたため、判定に差は出ていません。
```

### 返ってきたもの（生）— 材料D・2回目

```
## 切れているリンク(GETが404): 2件
- L01 https://home-baking-journal.jp/2019/sugar-ratio-fail
- L03 https://flour-type-archive.jp/2018/cake-flour-swap

## 確認できないリンク(GETが200でも404でもない): 6件

**① 転送(301・302): 2件**
- L07 https://pastry-basics-notes.jp/guide/old-measurement-chart (301)
- L08 https://flour-type-archive.jp/archive/2017/starter-guide (302)

**② タイムアウト(応答なし): 2件**
- L09 https://home-baking-journal.jp/2022/guest-contributor-notes
- L10 https://baking-tool-outlet.jp/items/thermometer-03

**③ サーバーエラー(500番台): 2件**
- L11 https://pastry-basics-notes.jp/guide/humidity-adjustment (500)
- L12 https://flour-type-archive.jp/2020/sourdough-faq (503)

**④ その他: 2件**
- L05 https://baking-tool-outlet.jp/items/scale-01 (403)
- L06 https://baking-tool-outlet.jp/items/mixer-02 (403)

## 参考: 切れていないリンク(GETが200): 2件
- L02、L04

合計は 2 + 6 + 2 = 12件で、全リンクを分類できています。
```

### 照合（機械）

| 回 | 各カテゴリのID | 真値との一致 | 見出しの件数 | 実際の件数 | 一致 |
|---|---|---|---|---|---|
| C-1 | 全10IDが真値と一致 | ✅ | 2/2/8（転送2・TO2・5xx2・他2） | 同じ | ✅ |
| C-2 | 全10IDが真値と一致 | ✅ | 「切れている3件」 | 2件 | ❌ |
| D-1 | 全10IDが真値と一致 | ✅ | 件数の明記なし | ― | ― |
| D-2 | 全10IDが真値と一致 | ✅ | 「確認できない6件」 | 8件（内訳2+2+2+2） | ❌ |

分類（IDの集合）は4回とも真値と完全一致。件数を明記した3回（C-1, C-2, D-2）のうち2回（C-2, D-2）で、
見出しの数字が実際の件数と食い違った。D-2はさらに「合計は2+6+2=12件」という閉じの一文自体も、
2+6+2の計算結果（10）と書かれた「12件」が食い違っている（12という数字は全リンク数と一致するが、
示された式からは出ない）。

### 判定

**採用**（分類は正しいが、件数のズレが再発することを示す材料として）。

---

## 指示文4（記事：AIへの頼み方 4・500番台だけ切れている側に）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETが404、または500番台の場合は、切れていると判断してください。それ以外でGETが200でない場合（301・302・403・タイムアウトなど）は、切れているとは断定せず、確認できないリンクとして分けてください。件数はまだ書かないでください。まず、切れているリンクと確認できないリンクのIDを箇条書きで全部挙げてください。箇条書きが終わったら、最後にそれぞれ「以上、何件」と書いてください。
```

### 返ってきたもの（生）— 材料C・1回目

```
**切れているリンク**
- L01
- L03
- L11
- L12

**確認できないリンク**
- L05
- L06
- L07
- L08
- L09
- L10

以上、切れているリンクは4件、確認できないリンクは6件です。
```

### 返ってきたもの（生）— 材料C・2回目

```
**切れているリンク（GETが404または5xx）**
- L01
- L03
- L11
- L12

**確認できないリンク（GETが200以外で、404・5xx以外）**
- L05
- L06
- L07
- L08
- L09
- L10

以上、切れているリンクは4件、確認できないリンクは6件です。
```

### 返ってきたもの（生）— 材料D・1回目

```
**切れているリンク**（GETが404または500番台）
- L01
- L03
- L11
- L12

以上、4件

**確認できないリンク**（GETが200以外で、404・500番台ではないもの）
- L05
- L06
- L07
- L08
- L09
- L10

以上、6件

L02とL04はGETが200なので、切れていません。
```

### 返ってきたもの（生）— 材料D・2回目

```
**切れているリンク**（GETが404または500番台）
- L01
- L03
- L11
- L12

以上、4件

**確認できないリンク**（GETが200以外で、404・500番台ではないもの）
- L05
- L06
- L07
- L08
- L09
- L10

以上、6件

（補足：L02とL04はGETが200のため、切れていません。）
```

### 照合（機械）

| 回 | 切れている（ID／件数） | 確認できない（ID／件数） | 見出しの件数 | 一致 |
|---|---|---|---|---|
| C-1 | L01,L03,L11,L12／4件 | L05-L10／6件 | 4件・6件 | ✅ |
| C-2 | 同上 | 同上 | 4件・6件 | ✅ |
| D-1 | 同上 | 同上 | 4件・6件 | ✅ |
| D-2 | 同上 | 同上 | 4件・6件 | ✅ |

4回とも、「切れている」＝404(L01,L03)＋5xx(L11,L12)の4件、「確認できない」＝403・301・302・
タイムアウト(L05-L10)の6件に正確に分かれ、見出しの件数もすべて一致した。

### 判定

**採用**。

---

## 指示文5（記事：言い直し方「件数は、名前を全部挙げたあとに書かせる」）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETも404の場合は、切れていると判断してください。GETが200でも404でもない場合は、切れているとは断定せず、確認できないリンクとして分けてください。確認できないリンクは、さらに次の4種類に分けてください。①転送（301・302）②タイムアウト（応答なし）③サーバーエラー（500番台）④その他（403など）。件数はまだ書かないでください。まず、切れているリンクと、確認できないリンクの4種類それぞれについて、IDを箇条書きで全部挙げてください。箇条書きが終わったら、最後にそれぞれ「以上、何件」と書いてください。
```

これは指示文3に「件数はまだ書かないでください」「IDを箇条書きで全部挙げてから、最後に件数」を
足したもの。

### 返ってきたもの（生）— 材料C・1回目

```
## 切れているリンク(GETが404)
- L01
- L03

## 確認できないリンク

**① 転送(301・302)**
- L07
- L08

**② タイムアウト(応答なし)**
- L09
- L10

**③ サーバーエラー(500番台)**
- L11
- L12

**④ その他(403など)**
- L05
- L06

なお、L02とL04はGETが200なので、切れていません。

## 件数
- 切れているリンク: 以上、2件
- ① 転送: 以上、2件
- ② タイムアウト: 以上、2件
- ③ サーバーエラー: 以上、2件
- ④ その他: 以上、2件
```

### 返ってきたもの（生）— 材料C・2回目

```
## 切れているリンク（GETが404）
- L01
- L03

以上、2件

## 確認できないリンク

### ① 転送（301・302）
- L07
- L08

以上、2件

### ② タイムアウト（応答なし）
- L09
- L10

以上、2件

### ③ サーバーエラー（500番台）
- L11
- L12

以上、2件

### ④ その他（403など）
- L05
- L06

以上、2件

なお、L02とL04はGETが200なので、切れていません。
```

### 返ってきたもの（生）— 材料D・1回目

```
**切れているリンク**（GETが404）
- L01
- L03

以上、2件

**確認できないリンク**

① 転送（301・302）
- L07
- L08

以上、2件

② タイムアウト（応答なし）
- L09
- L10

以上、2件

③ サーバーエラー（500番台）
- L11
- L12

以上、2件

④ その他（403など）
- L05
- L06

以上、2件

**正常なリンク**（参考：GETが200）
- L02
- L04

以上、2件
```

### 返ってきたもの（生）— 材料D・2回目

```
**切れているリンク（GETも404）**
- L01
- L03

以上、2件

**確認できないリンク**

① 転送（301・302）
- L07
- L08

以上、2件

② タイムアウト（応答なし）
- L09
- L10

以上、2件

③ サーバーエラー（500番台）
- L11
- L12

以上、2件

④ その他（403など）
- L05
- L06

以上、2件

なお、L02とL04はHEAD・GETとも200で、問題ありません。
```

### 照合（機械）

4回とも、各カテゴリの見出しの件数（切れている2件、転送2件、タイムアウト2件、
サーバーエラー2件、その他2件）が、実際に箇条書きされたIDの数とすべて一致。
指示文3で2/3回起きた食い違いは、4回とも再現しなかった。

### 判定

**採用**。

---

## 指示文6（記事：言い直し方「この直し方を、1回効かせたら終わりにしない」）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETが404、または500番台の場合は、切れていると判断してください。それ以外でGETが200でない場合（301・302・403・タイムアウトなど）は、切れているとは断定せず、確認できないリンクとして分けてください。確認できないリンクは、どれを先に手で確認すべきか、優先順位を付けてください。理由も一緒に書いてください。
```

指示文4の基準（500番台を切れている側に）に、優先順位付けという作業を追加した。
⚠️ **「件数はまだ書かないでください」「名前を先に」の一文は、この指示文には入れていない。**

### 返ってきたもの（生）— 材料C・1回目

```
# リンク点検の判定結果

## 🔴 切れているリンク（4件）
GETが404、または500番台のもの。

| ID | URL | GET | 備考 |
|---|---|---|---|
| L01 | exam-prep-notes.jp/2020/past-paper-review | 404 | |
| L03 | license-archive-notes.jp/2019/mock-test | 404 | |
| L11 | study-method-hub.jp/guide/burnout-signs | 500 | サーバーエラー |
| L12 | license-archive-notes.jp/2020/renewal-steps | 503 | 一時的な障害の可能性あり |

## 🟢 切れていないリンク（2件）
L02、L04（HEAD・GETとも200）

## 🟡 確認できないリンク（6件）
L05、L06、L07、L08、L09、L10

## 確認できないリンクの確認優先順位

**1位：L07**（study-method-hub.jp/guide/old-syllabus / 301）
恒久的な移転を示しており、旧URLのままでは将来消える可能性が高いです。転送先を確認して新URLに差し替えれば、確実に解決できます。リンク先の記事自体は生きている見込みが高く、対応の効果が大きいです。

**2位：L08**（license-archive-notes.jp/archive/2018/intro / 302）
一時的な転送です。転送先が正しい記事なら問題ありませんが、トップページなどに飛ばされている場合は実質的に切れています。L07と同様、ブラウザで開けばすぐ判断できます。

**3位：L09**（exam-prep-notes.jp/2022/mentor-interview / タイムアウト）
HEADとGETの両方がタイムアウトで、サイトの混雑か記事の消失かが分かりません。同じドメインのL04は200なのでサイト自体は稼働しており、この記事個別の問題の可能性があります。インタビュー記事は内容が読者にとって価値が高いため、早めに確認したいです。

**4位：L10**（cert-gear-store.jp/items/desk-lamp-03 / タイムアウト）
商品ページが販売終了で削除された可能性があります。ただし、同じドメインのL05・L06が403を返しているため、サイト全体が自動アクセスを制限している可能性もあり、切れていると決めつけられません。

**5位・6位：L05、L06**（cert-gear-store.jp / 403）
HEADもGETも403ですが、これは自動点検ツールへのアクセス拒否（ボット対策）であることが多く、ブラウザでは普通に開ける場合が多いです。2件とも同じドメイン・同じパターンなので、どちらか1件をブラウザで開けば両方の状況がおおむね分かります。優先度は低めです。

## 補足
- L12（503）は一時的な過負荷やメンテナンスの可能性がありますが、ご指定のルールどおり「切れている」に分類しました。時間をおいて再点検することをおすすめします。
- L10の確認時にL05・L06も同じブラウザで開けば、cert-gear-store.jp全体の状況を一度に把握できます。
```

### 返ってきたもの（生）— 材料C・2回目

```
# リンク点検結果

## 1. 切れているリンク（GETが404、または5xx）：5件

| ID | URL | GET | 備考 |
|---|---|---|---|
| L01 | exam-prep-notes.jp/2020/past-paper-review | 404 | |
| L03 | license-archive-notes.jp/2019/mock-test | 404 | |
| L11 | study-method-hub.jp/guide/burnout-signs | 500 | |
| L12 | license-archive-notes.jp/2020/renewal-steps | 503 | |

訂正：上の表は4件です（5件ではありません）。L01、L03、L11、L12の4件が「切れている」と判断したリンクです。

※L11・L12は5xxなので、ご指定のルールどおり「切れている」に分類しました。ただし一時的なサーバー障害の可能性もあるため、修正・削除の前に再度アクセスして確認すると安全です。

## 2. 切れていないリンク：2件

| ID | URL | GET |
|---|---|---|
| L02 | study-method-hub.jp/guide/spaced-repetition | 200 |
| L04 | exam-prep-notes.jp/2021/schedule-template | 200 |

## 3. 確認できないリンク（手動確認が必要）：6件

GETが200でも404/5xxでもないものです。

### 優先順位

| 順位 | ID | URL | GET | 理由 |
|---|---|---|---|---|
| 1 | L09 | exam-prep-notes.jp/2022/mentor-interview | タイムアウト | 同じドメインのL02・L04は正常に200を返しているため、サイト全体の障害ではなく、このページ固有の問題（削除・重い処理など）の可能性が高い。ページ単位で壊れている疑いが最も強い。 |
| 2 | L07 | study-method-hub.jp/guide/old-syllabus | 301 | 恒久的な移転。転送先が有効なら、リンクを新URLに書き換えるだけで済む。転送先が404になっている場合もあるため確認が必要。URLに「old」とあり、内容が古い可能性もある。 |
| 3 | L08 | license-archive-notes.jp/archive/2018/intro | 302 | 一時的な転送。ただし同ドメインのL03が404、L12が503と不安定で、転送先がエラーになっている可能性がある。 |
| 4 | L10 | cert-gear-store.jp/items/desk-lamp-03 | タイムアウト | 商品ページは販売終了で消えることがある。ただしL05・L06と同じドメインで、サイト側がボット対策や遮断をしている可能性もあり、原因の切り分けが難しい。 |
| 5 | L05 | cert-gear-store.jp/items/timer-01 | 403 | HEADもGETも403。自動アクセスを拒否している可能性が高く、ブラウザでは普通に見られることが多い。ただし商品ページなので、在庫切れ・販売終了の確認を兼ねて見ておくとよい。 |
| 6 | L06 | cert-gear-store.jp/items/binder-02 | 403 | L05と同じ理由。同じドメインなので、L05を確認して正常に開ければ、こちらも同様の可能性が高い。 |

### 確認のコツ
- **L05・L06・L10**は同じドメインなので、まず1件をブラウザで開き、サイト全体の問題か個別の問題かを見分けると効率的です。
- **L07・L08**は、ブラウザで開いて最終的に表示されるURLと内容を確認し、問題なければリンク先を新URLに更新してください。
- **L09**は時間を置いて再度確認し、それでも開かなければ切れているとみなして構いません。

## まとめ

- 切れている：4件（L01、L03、L11、L12）
- 切れていない：2件（L02、L04）
- 確認できない：6件（L05〜L10）
```

### 返ってきたもの（生）— 材料D・1回目

```
## 点検結果の分類

### 切れているリンク（GETが404または5xx）
| ID | URL | GET |
|---|---|---|
| L01 | home-baking-journal.jp/2019/sugar-ratio-fail | 404 |
| L03 | flour-type-archive.jp/2018/cake-flour-swap | 404 |
| L11 | pastry-basics-notes.jp/guide/humidity-adjustment | 500 |
| L12 | flour-type-archive.jp/2020/sourdough-faq | 503 |

### 切れていないリンク（GETが200）
L02、L04

### 確認できないリンク（GETが200以外・404/5xx以外）
L05、L06（403）、L07（301）、L08（302）、L09、L10（タイムアウト）

## 手で確認する優先順位

1. **L07（301）**: 恒久的な移転を示しています。移転先で内容が残っている可能性が高く、リンク先を新URLに更新するだけで直せます。「old-measurement-chart」という名前からも、新しい資料に置き換わっている可能性があります。
2. **L08（302）**: 一時的な転送ですが、転送先がトップページや別の記事になっていることも多く、内容が合っているか確認が必要です。2017年の古い記事なので、実質的に失われている可能性もあります。
3. **L09（タイムアウト）**: 自分のブログ（home-baking-journal.jp）内のページなので、自分で原因を調べられます。サーバー側の問題なら、自分の管理範囲で直せます。
4. **L05・L06（403）**: 同じ店のページで、HEADもGETも403です。ボット対策による拒否の可能性が高く、ブラウザでは普通に開けることが多いです。2件まとめて1回で確認できます。
5. **L10（タイムアウト）**: L05・L06と同じ baking-tool-outlet.jp ですが、商品ページ単体の問題か、サイト全体が不安定かを見分ける必要があります。L05・L06をブラウザで開いたときにサイト全体の状態もわかるので、それと一緒に確認すると効率的です。

### 補足
- L11（500）・L12（503）は、ご指定の基準では「切れている」扱いにしました。ただし5xxは一時的なサーバー障害のこともあるため、修正や削除の前に時間をおいて再確認すると安全です。
- 301・302は、自動点検がリダイレクト先を追っていない可能性があります。リダイレクトを追ってGETし直せば、手作業をかなり減らせます。
```

### 照合（機械）

| 回 | 分類の正しさ | 見出しの件数 | 実際の件数 | 一致 |
|---|---|---|---|---|
| C-1 | 正しい（4/2/6で真値一致） | 4件・2件・6件 | 同じ | ✅ |
| C-2 | 正しい（4/2/6で真値一致） | 「切れている5件」 | 4件 | ❌（本文中で自己訂正） |
| D-1 | 正しい（4/2/6で真値一致） | 件数の明記なし | ― | ― |

分類（どのIDがどの扱いか）は3回とも真値と一致。件数を明記した2回（C-1, C-2）のうち1回（C-2）で、
見出しの数字が実際の件数と食い違った。指示文4・5で効いていた「件数はまだ書かないでください」
「名前を先に」が、この指示文には入っていない。

### 判定

**採用**（基準そのものは正しくても、別の作業を加えて件数の指示を省くと、同じ崩れが再発することを示す材料として）。

---

## この記事から出た教訓（`content/_lessons.md` へ）

1. リンク切れ点検の基準（HEADだけで判断しない・GETが200か404かで判断する）に、301・302・
   タイムアウト・500番台を混ぜても、404と取り違える誤分類は20回中0回だった。基準を渡さなくても、
   常識的な言い回しで404とそれ以外は区別されたが、バケツの数と名前は回によって2〜5種に変動した。
2. ★302（見出しの件数が実際の列挙件数と食い違う）が、確認できないリンクを4種に分けて件数も
   書かせる場面で再発した（件数を明記した3回のうち2回）。「名前を先に、件数はあとに」で直るが、
   直したあとに優先順位付けという別の作業を加え、その指示を省くと、また1回再発した。
   直し方は「基準を1回直したら終わり」ではなく、**新しい作業を追加するたびに、件数の指示を
   もう一度確認すること**。
