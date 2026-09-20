# 試した証拠 — udemy-97-or-37-who-brings-the-student

記事＝`content/recipes/udemy-97-or-37-who-brings-the-student.md`
（「Udemyの取り分は97%か37%か——3,000円×100本が、誰が客を連れてきたかで291,000円と111,000円に割れる」）。
連載「本気で稼ぐ式」第2回。

実測日 2026-09-18。**実行はのべ18回**＝指示文6種（A〜F）を各3回、独立に実行。

## 実行のしかた

`gpts-retirement-check-the-source` と同じ（同日・同じ方式）。Agent ツール（`general-purpose` サブエージェント）を
1回ずつ新規に起動し、ツールを使わないよう前置きで指示、完了通知の `tool_uses: 0` で確認（18回すべて 0）。
`claude -p` は CLI の OAuth トークンが失効していて使えない。⚠️ サブエージェントは `CLAUDE.md` を読める位置にいる（★145）。
この記事の題材（Udemy）は `CLAUDE.md` に無い。

送った全文＝定型の前置き＋質問。前置き（18回とも同一）:

```
あなたは一般向けのAIチャットアシスタントです。ツールは一切使わないでください（ファイルを読まない・ウェブ検索をしない・コマンドを実行しない）。次の質問に、あなたの知識だけで、文章で答えてください。回答の本文だけを返してください（前置きや「ツールは使いませんでした」等の説明は不要です）。

質問:
<記事の指示文をそのまま>
```

回答の全文＝`docs/evidence/_raw/udemy-97-or-37-who-brings-the-student/run01_*.md`〜`run18_*.md`（完了通知の本文を転記。文字は変えていない）。
判定コード＝同ディレクトリの `judge.py`（正規表現の文字列照合のみ）、出力＝`judge_output.txt`。

## 真値の出典（2026-09-18 に実ブラウザで本文まで確認・23枚目）

| | |
|---|---|
| 掲載は無料 | 「There is no fee to create and host a course on Udemy, and you can publish as many free and paid courses as you like.」（[Instructor revenue share](https://support.udemy.com/hc/en-us/articles/229605008-Instructor-revenue-share)） |
| 97% | 「Sales occurring through instructor promotions: instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.」（同） |
| 37% | 「Sales that do not occur through an instructor promotion: instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.」（同） |
| Net Amount | 「these are revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google for sales on iOS and Android.」（同） |
| Udemy Business | 「Each month, Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed across all Udemy Business courses.」（[How do I earn revenue from Udemy Business and subscription plans?](https://support.udemy.com/hc/en-us/articles/115013221767-How-do-I-earn-revenue-from-Udemy-Business-and-subscription-plans)） |
| 広告（Starter Plan） | 「25% of the amount attributable to eligible ad surfaces on qualifying courses will be allocated to instructors.」（同） |

⚠️ 2ページとも更新日の記載なし。⚠️ **過去の率（50%・25%・20%・17.5%）と変更時期は、どちらのページにも載っていない**＝AIが添えた経緯は検証できない。

真値の計算（3,000円×100本＝300,000円・税とアプリ手数料は考えない）: ×0.97＝**291,000円**／×0.37＝**111,000円**（差 180,000円）。

---

## 指示文A（取り分を素朴に聞く・3回）

### 送った指示文（記事と同一文字列）

```
Udemyで自分の講座を売ると、講師の取り分は売上の何%ですか。条件によって違うなら、その条件も教えてください。
```

生の全文＝`run01_a1_A_naive_share.md`〜`run03_a3_A_naive_share.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 97%（紹介リンク・クーポン経由） | **3/3** |
| 37%（Udemy経由） | **3/3** |
| Net Amount／アプリ手数料30%に触れた | **3/3** |
| Udemy Business のプールに触れた | **3/3** |
| UB＝15%と述べた | **3/3** |
| UB＝17.5%を（経緯として）述べた | **3/3** |
| 過去の率や変更時期を述べた（原文に無い） | **3/3** |

🔑 現在の率は3/3。**3回とも頼んでいない経緯（2018年・50%・25%→20%→17.5%→15%）を添えた。**原文に無いので正誤を判定できない。

## 指示文B（Udemy Business の支払われ方・3回）

### 送った指示文（記事と同一文字列）

```
Udemy Business（法人向けの定額プラン）で自分の講座が見られたとき、講師にはどのように支払われますか。
```

生の全文＝`run04_b1_B_business_pool.md`〜`run06_b3_B_business_pool.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 「プール（配分枠）」の仕組みを説明した | **3/3** |
| 「視聴された分数の割合」で分けると述べた | **3/3** |
| プール率＝15%と述べた | **3/3** |
| 17.5%を（経緯として）述べた | **3/3** |
| 過去の率や変更時期を述べた（原文に無い） | **3/3** |
| 「確認を／変わりうる」と断った | **3/3** |

## 指示文C（原文の英文を貼って計算だけさせる・3回）

### 送った指示文（記事と同一文字列）

```
Udemyの公式ヘルプ（英語）で確認した情報を貼ります。これ以外の数字は使わないでください。

・Sales occurring through instructor promotions: instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.
・Sales that do not occur through an instructor promotion: instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.
・these are revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google for sales on iOS and Android.
・Each month, Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed across all Udemy Business courses.

3,000円の講座が1か月に100本売れたとして、①全部が私の紹介リンク経由だった場合 ②全部がUdemyの検索経由（紹介リンクなし）だった場合、それぞれ講師の取り分を計算してください。iOS・Androidアプリ経由の販売はゼロで、税も考えないものとします。上に無い数字は使わず、必要なら「材料に無い」と書いてください。
```

生の全文＝`run07_c1_C_materials_fed.md`〜`run09_c3_C_materials_fed.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 紹介リンク経由 291,000円 | **3/3** |
| 検索経由 111,000円 | **3/3** |
| 差 180,000円 | **3/3** |
| 「材料に無い」を使った | **3/3** |
| 材料に無い率（%）を足した個数 | 0・0・0 |

## 指示文D（過去に変更されたか・3回）— 記事では4節目

### 送った指示文（記事と同一文字列）

```
Udemyの講師の取り分（レベニューシェア）は、過去に変更されたことがありますか。現在の率と、変更があったなら変更前の率と時期を教えてください。
```

生の全文＝`run13_e1_E_history.md`〜`run15_e3_E_history.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 現在＝97%／37%と述べた | **3/3** |
| UB現在＝15%と述べた | **2/3** |
| UB現在＝17.5%と述べた（原文と食い違う） | **1/3**（run14「2026年現在のサブスク分配率は17.5%」） |
| 50%（過去の率）を挙げた | **3/3** |
| 変更時期を年で書いた | **3/3**（run13「2013年頃」・run14「2018年」・run15「2020年頃」＝3回で3通り） |
| 「原文で確認を」と断った | **3/3** |

🔑 現在の率は当たるが、**経緯は3回で3通りの年**。原文に載っていないので、どれが正しいかを原文からは言えない。

## 指示文E（ページ名だけ・数字は書かずに・3回）— 記事では言い直し1つ目

### 送った指示文（記事と同一文字列）

```
Udemyの講師の取り分（レベニューシェア）について、確認すべき公式ヘルプページの名前だけを、数字は書かずに教えてください。
```

生の全文＝`run10_d1_D_page_names.md`〜`run12_d3_D_page_names.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 数字ゼロ（箇条書きの番号を除く） | **3/3** |
| 「Instructor Revenue Share」を挙げた | **3/3** |
| Udemy Business の配分ページに触れた | **2/3** |

## 指示文F（確認する順番・数字は書かずに・3回）— 記事では言い直し2つ目

### 送った指示文（記事と同一文字列）

```
私はUdemyで講座を出すか検討しています。取り分や支払いの条件は変わることがあるので、自分で公式ヘルプを確認したいです。

私が確認すべき箇所を、確認する順番に並べてください。

⚠️ あなたは率や金額の数字を書かないでください。数字は私が公式ヘルプで確認します。あなたが書くのは「どこで何を確認するか」だけにしてください。
```

生の全文＝`run16_f1_F_check_order_no_numbers.md`〜`run18_f3_F_check_order_no_numbers.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 率・金額の数字ゼロ（%・円・ドルの付いた数字） | **3/3** |
| 「誰が客を連れてきたか（紹介リンク／クーポン）」を確認項目に入れた | **3/3** |
| Udemy Business の配分を確認項目に入れた | **3/3** |
| 支払い（PayPal／Payoneer・時期）を確認項目に入れた | **3/3** |

⚠️ 「W-8BEN」「項目2〜9」のような数字は率・金額ではないので数えていない（最初は全部の数字を数えて 5・2・12 と出た＝計測器の誤り。12番の再発）。

## 推定（記事の金額ブロック）の計算

式＝3,000円×本数×0.97（自分の集客）または ×0.37（Udemyの集客）。本数は前提。税・アプリ手数料は考えない。

| 本数 | 売上 | ×0.97 | ×0.37 |
|---|---|---|---|
| 10 | 30,000 | **29,100** | **11,100** |
| 30 | 90,000 | **87,300** | **33,300** |
| 100 | 300,000 | **291,000** | **111,000** |

年（100本）＝3,492,000円／1,332,000円。Udemy Business のプール制は本数の式に入らないので推定に含めない。
支払い（最低額・時期）は今回開いた2ページに無いので書かない。

## この記事から出た教訓

- **現在の率は当たる（9/9）。経緯は9/9で添えられ、原文に無い**＝聞いていなくても付く。「いつ変わったか」を直接聞くと年が3通りになる。
- **貼れば1円単位で一致（3/3）**＝`note-membership-monthly-formula` と同じ。
- **プール制は本数の式に入らない**＝「1本いくら」で推定できない稼ぎ方があることを、式の側で明示する。
- 判定コードの罠＝「現在」の窓を80文字に取ると、経緯の中の「17.5%」まで「現在の率」として拾った。窓を30文字に縮め、「2026年〜」の直後だけを見るようにした（12番の再発）。
