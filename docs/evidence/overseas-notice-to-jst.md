# 試した証拠 — overseas-notice-to-jst

記事に載せる指示文すべてについて、この形式で残す。

⚠️ このファイルは `content/` の中に置いていない（ビルド除外はファイル名の `_` 判定のため）。

実測日: 2026-09-03。実測の相手＝`claude --safe-mode --tools ""`（CLAUDE.md・skills・plugins・履歴を全部無効化した新規プロセス。呼び出しごとに完全に独立したセッション）。

---

## 教材（架空データ）

架空の海外拠点からの英文案内24通を、内容の異なる2つの材料（A・B）で用意した。仕込み＝①日付が変わる8通（前日へ3・翌日へ5、UTC固定オフセットのみでDSTには関与させていない）②米国の夏時間（2026年は3月8日〜11月1日）の期間中に送られた、標準／夏時間をどちらとも明記しない「PT」「ET」表記4通③同じ期間の前後で「PST」「EDT」と略号まで明記した4通（実際の季節と食い違わせて、表記を信じるかを見る）④すでに日本時間（JST）で書かれた、換算してはいけない2通⑤インドの30分刻み（IST・UTC+5:30）2通⑥送信日を基準にした相対表現（"next Thursday"）2通⑦易しい対照2通。真値は生成コード内でPythonのオフセット計算により確定し、走らせる前に件数・境界方向（前日3件・翌日5件）をassertした。

### 材料A（N-01〜N-24）

```
[N-01]
From: Auckland Ops
Subject: Weekly sync notes
Sent: Monday, April 13, 2026, 1:00 AM (UTC+13)

This note is time-stamped 1:00 AM on April 13.

Best regards,
Auckland Ops

---

[N-02]
From: Fiji Logistics
Subject: Shipment window
Sent: Tuesday, May 5, 2026, 2:30 AM (UTC+12)

This note is time-stamped 2:30 AM on May 5.

Best regards,
Fiji Logistics

---

[N-03]
From: Sydney Support
Subject: Ticket handover
Sent: Tuesday, June 9, 2026, 1:30 AM (UTC+11)

This note is time-stamped 1:30 AM on June 9.

Best regards,
Sydney Support

---

[N-04]
From: London HQ
Subject: Board memo
Sent: Tuesday, March 17, 2026, 8:00 PM (UTC+0)

This note is time-stamped 8:00 PM on March 17.

Best regards,
London HQ

---

[N-05]
From: Lagos Partner
Subject: Contract note
Sent: Thursday, April 2, 2026, 10:00 PM (UTC+1)

This note is time-stamped 10:00 PM on April 2.

Best regards,
Lagos Partner

---

[N-06]
From: Sao Paulo Finance
Subject: Invoice batch
Sent: Tuesday, July 14, 2026, 9:30 PM (UTC-3)

This note is time-stamped 9:30 PM on July 14.

Best regards,
Sao Paulo Finance

---

[N-07]
From: Toronto Vendor
Subject: Delivery slip
Sent: Monday, September 21, 2026, 7:00 PM (UTC-5)

This note is time-stamped 7:00 PM on September 21.

Best regards,
Toronto Vendor

---

[N-08]
From: Anchorage Field
Subject: Site report
Sent: Tuesday, August 11, 2026, 5:00 PM (UTC-8)

This note is time-stamped 5:00 PM on August 11.

Best regards,
Anchorage Field

---

[N-09]
From: Seattle Product
Subject: Sprint review
Sent: Tuesday, April 7, 2026, 9:00 AM PT

Please block your calendar for 9:00 AM PT on April 7.

Best regards,
Seattle Product

---

[N-10]
From: Portland Design
Subject: Asset handoff
Sent: Tuesday, June 16, 2026, 3:00 PM PT

Please block your calendar for 3:00 PM PT on June 16.

Best regards,
Portland Design

---

[N-11]
From: Boston Legal
Subject: Contract redline
Sent: Tuesday, May 12, 2026, 11:00 AM ET

Please block your calendar for 11:00 AM ET on May 12.

Best regards,
Boston Legal

---

[N-12]
From: Atlanta Sales
Subject: Renewal call
Sent: Wednesday, September 9, 2026, 2:00 PM ET

Please block your calendar for 2:00 PM ET on September 9.

Best regards,
Atlanta Sales

---

[N-13]
From: San Jose Eng
Subject: Release freeze
Sent: Tuesday, April 7, 2026, 9:00 AM PST

The session starts at 9:00 AM PST sharp on April 7.

Best regards,
San Jose Eng

---

[N-14]
From: Fresno Ops
Subject: Vendor demo
Sent: Thursday, July 2, 2026, 1:00 PM PST

The session starts at 1:00 PM PST sharp on July 2.

Best regards,
Fresno Ops

---

[N-15]
From: New York Ops
Subject: Audit call
Sent: Thursday, December 3, 2026, 10:00 AM EDT

The session starts at 10:00 AM EDT sharp on December 3.

Best regards,
New York Ops

---

[N-16]
From: Miami Support
Subject: Escalation review
Sent: Tuesday, January 20, 2026, 4:00 PM EDT

The session starts at 4:00 PM EDT sharp on January 20.

Best regards,
Miami Support

---

[N-17]
From: Tokyo HQ
Subject: Facility notice
Sent: Friday, May 1, 2026, 1:00 PM JST

This is already in Japan time: 1:00 PM on May 1.

Best regards,
Tokyo HQ

---

[N-18]
From: Osaka Branch
Subject: Payroll reminder
Sent: Tuesday, October 6, 2026, 9:30 AM JST

This is already in Japan time: 9:30 AM on October 6.

Best regards,
Osaka Branch

---

[N-19]
From: Bengaluru Dev
Subject: Handover notes
Sent: Wednesday, March 25, 2026, 11:00 PM IST (UTC+5:30)

Sync call scheduled 11:00 PM IST (UTC+5:30) on March 25.

Best regards,
Bengaluru Dev

---

[N-20]
From: Mumbai Finance
Subject: Reconciliation
Sent: Thursday, November 12, 2026, 8:45 PM IST (UTC+5:30)

Sync call scheduled 8:45 PM IST (UTC+5:30) on November 12.

Best regards,
Mumbai Finance

---

[N-21]
From: Chicago Client
Subject: Kickoff
Sent: Thursday, April 9, 2026

Let's meet next Thursday at 9:00 AM ET.

Best regards,
Chicago Client

---

[N-22]
From: Dublin Partner
Subject: Follow-up
Sent: Thursday, October 15, 2026

Let's meet next Thursday at 3:00 PM GMT.

Best regards,
Dublin Partner

---

[N-23]
From: Berlin Office
Subject: Lunch survey
Sent: Tuesday, June 2, 2026, 10:00 AM (UTC+2)

Quick reminder about today's item at 10:00 AM (UTC+2).

Best regards,
Berlin Office

---

[N-24]
From: Manila Support
Subject: Status check
Sent: Thursday, September 3, 2026, 11:00 AM (UTC+8)

Quick reminder about today's item at 11:00 AM (UTC+8).

Best regards,
Manila Support
```

### 材料B（N-01〜N-24・別内容）

```
[N-01]
From: Wellington Ops
Subject: Roadmap update
Sent: Tuesday, May 19, 2026, 12:30 AM (UTC+12)

This note is time-stamped 12:30 AM on May 19.

Best regards,
Wellington Ops

---

[N-02]
From: Noumea Logistics
Subject: Container ETA
Sent: Tuesday, July 7, 2026, 1:00 AM (UTC+11)

This note is time-stamped 1:00 AM on July 7.

Best regards,
Noumea Logistics

---

[N-03]
From: Suva Support
Subject: Incident handover
Sent: Monday, August 3, 2026, 2:00 AM (UTC+12)

This note is time-stamped 2:00 AM on August 3.

Best regards,
Suva Support

---

[N-04]
From: Dublin HQ
Subject: Policy memo
Sent: Tuesday, April 21, 2026, 9:00 PM (UTC+1)

This note is time-stamped 9:00 PM on April 21.

Best regards,
Dublin HQ

---

[N-05]
From: Accra Partner
Subject: Payment note
Sent: Tuesday, May 26, 2026, 11:00 PM (UTC+0)

This note is time-stamped 11:00 PM on May 26.

Best regards,
Accra Partner

---

[N-06]
From: Buenos Aires Finance
Subject: Invoice batch
Sent: Thursday, October 8, 2026, 8:00 PM (UTC-3)

This note is time-stamped 8:00 PM on October 8.

Best regards,
Buenos Aires Finance

---

[N-07]
From: Mexico City Vendor
Subject: Delivery slip
Sent: Wednesday, June 24, 2026, 6:30 PM (UTC-6)

This note is time-stamped 6:30 PM on June 24.

Best regards,
Mexico City Vendor

---

[N-08]
From: Honolulu Field
Subject: Site report
Sent: Tuesday, November 3, 2026, 4:00 PM (UTC-10)

This note is time-stamped 4:00 PM on November 3.

Best regards,
Honolulu Field

---

[N-09]
From: San Diego Product
Subject: Sprint review
Sent: Monday, May 11, 2026, 9:30 AM PT

Please block your calendar for 9:30 AM PT on May 11.

Best regards,
San Diego Product

---

[N-10]
From: Sacramento Design
Subject: Asset handoff
Sent: Tuesday, August 18, 2026, 4:00 PM PT

Please block your calendar for 4:00 PM PT on August 18.

Best regards,
Sacramento Design

---

[N-11]
From: Philadelphia Legal
Subject: Contract redline
Sent: Tuesday, April 14, 2026, 10:00 AM ET

Please block your calendar for 10:00 AM ET on April 14.

Best regards,
Philadelphia Legal

---

[N-12]
From: Raleigh Sales
Subject: Renewal call
Sent: Tuesday, October 20, 2026, 1:00 PM ET

Please block your calendar for 1:00 PM ET on October 20.

Best regards,
Raleigh Sales

---

[N-13]
From: Los Angeles Eng
Subject: Release freeze
Sent: Monday, May 11, 2026, 9:30 AM PST

The session starts at 9:30 AM PST sharp on May 11.

Best regards,
Los Angeles Eng

---

[N-14]
From: Fresno Sales
Subject: Vendor demo
Sent: Tuesday, September 15, 2026, 2:00 PM PST

The session starts at 2:00 PM PST sharp on September 15.

Best regards,
Fresno Sales

---

[N-15]
From: Washington Ops
Subject: Audit call
Sent: Thursday, January 8, 2026, 11:00 AM EDT

The session starts at 11:00 AM EDT sharp on January 8.

Best regards,
Washington Ops

---

[N-16]
From: Orlando Support
Subject: Escalation review
Sent: Thursday, December 17, 2026, 3:00 PM EDT

The session starts at 3:00 PM EDT sharp on December 17.

Best regards,
Orlando Support

---

[N-17]
From: Nagoya HQ
Subject: Facility notice
Sent: Monday, June 15, 2026, 2:00 PM JST

This is already in Japan time: 2:00 PM on June 15.

Best regards,
Nagoya HQ

---

[N-18]
From: Fukuoka Branch
Subject: Payroll reminder
Sent: Monday, November 2, 2026, 9:00 AM JST

This is already in Japan time: 9:00 AM on November 2.

Best regards,
Fukuoka Branch

---

[N-19]
From: Pune Dev
Subject: Handover notes
Sent: Wednesday, April 29, 2026, 10:30 PM IST (UTC+5:30)

Sync call scheduled 10:30 PM IST (UTC+5:30) on April 29.

Best regards,
Pune Dev

---

[N-20]
From: Chennai Finance
Subject: Reconciliation
Sent: Wednesday, December 9, 2026, 9:15 PM IST (UTC+5:30)

Sync call scheduled 9:15 PM IST (UTC+5:30) on December 9.

Best regards,
Chennai Finance

---

[N-21]
From: Detroit Client
Subject: Kickoff
Sent: Thursday, May 7, 2026

Let's meet next Thursday at 10:00 AM ET.

Best regards,
Detroit Client

---

[N-22]
From: Edinburgh Partner
Subject: Follow-up
Sent: Thursday, September 10, 2026

Let's meet next Thursday at 2:00 PM GMT.

Best regards,
Edinburgh Partner

---

[N-23]
From: Warsaw Office
Subject: Lunch survey
Sent: Monday, July 6, 2026, 9:00 AM (UTC+2)

Quick reminder about today's item at 9:00 AM (UTC+2).

Best regards,
Warsaw Office

---

[N-24]
From: Jakarta Support
Subject: Status check
Sent: Monday, October 12, 2026, 10:00 AM (UTC+7)

Quick reminder about today's item at 10:00 AM (UTC+7).

Best regards,
Jakarta Support
```

---

## 指示文1（記事1節・素のまま）

### 送った指示文（記事と同一文字列）

```
次の案内をすべて日本時間に直して、一覧にしてください。

1件につき1行、「ID: 日本時間の日付と時刻」の形式で先に一覧を書いてください。
```

（この指示文の後ろに「以下が案内です。」と材料Aまたは材料Bの全文を続けて送った。）

### 材料A・1回目

```
## 一覧(日本時間)

- N-01: 2026年4月12日(日) 21:00
- N-02: 2026年5月4日(月) 23:30
- N-03: 2026年6月8日(月) 23:30
- N-04: 2026年3月18日(水) 5:00
- N-05: 2026年4月3日(金) 6:00
- N-06: 2026年7月15日(水) 9:30
- N-07: 2026年9月22日(火) 9:00
- N-08: 2026年8月12日(水) 10:00
- N-09: 2026年4月8日(水) 1:00
- N-10: 2026年6月17日(水) 7:00
- N-11: 2026年5月13日(水) 0:00
- N-12: 2026年9月10日(木) 3:00
- N-13: 2026年4月8日(水) 2:00
- N-14: 2026年7月3日(金) 6:00
- N-15: 2026年12月3日(木) 23:00
- N-16: 2026年1月21日(水) 5:00
- N-17: 2026年5月1日(金) 13:00
- N-18: 2026年10月6日(火) 9:30
- N-19: 2026年3月26日(木) 2:30
- N-20: 2026年11月13日(金) 0:15
- N-21: 2026年4月16日(木) 22:00
- N-22: 2026年10月23日(金) 0:00
- N-23: 2026年6月2日(火) 17:00
- N-24: 2026年9月3日(木) 12:00

## 補足(判断に注意が必要だった点)

- **N-07/N-08/N-13〜N-16**: 本文中に明記されたオフセット(例:PST=UTC-8、EDT=UTC-4)をそのまま採用しました。実際の季節では別の略称(例:12月はEST、4月はPDT)になるはずですが、案内文に明記されている数値を優先しています。
- **N-21/N-22**: 送信日自体が木曜日のため、「来週の木曜日」は送信日の1週間後(N-21→4/16、N-22→10/23)としました。
- **N-17/N-18/N-23/N-24**: すでに日本時間、または当日扱いのため日付は変更していません。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料A・2回目

```
## 日本時間換算 一覧

- N-01: 2026年4月12日 21:00
- N-02: 2026年5月4日 23:30
- N-03: 2026年6月8日 23:30
- N-04: 2026年3月18日 5:00
- N-05: 2026年4月3日 6:00
- N-06: 2026年7月15日 9:30
- N-07: 2026年9月22日 9:00
- N-08: 2026年8月12日 10:00
- N-09: 2026年4月8日 1:00
- N-10: 2026年6月17日 7:00
- N-11: 2026年5月13日 0:00
- N-12: 2026年9月10日 3:00
- N-13: 2026年4月8日 2:00
- N-14: 2026年7月3日 6:00
- N-15: 2026年12月3日 23:00
- N-16: 2026年1月21日 5:00
- N-17: 2026年5月1日 13:00
- N-18: 2026年10月6日 9:30
- N-19: 2026年3月26日 2:30
- N-20: 2026年11月13日 0:15
- N-21: 2026年4月16日 22:00
- N-22: 2026年10月23日 0:00
- N-23: 2026年6月2日 17:00
- N-24: 2026年9月3日 12:00

---

### 補足（換算根拠）

- **N-01〜N-08, N-19, N-20, N-23, N-24**：本文中に明記されたUTCオフセットをそのまま使用し、JST（UTC+9）との差分で換算しました。
- **N-09〜N-16**：PT／ET／PST／EDT等の表記をそのまま採用しています（例：N-13/N-14は本文に明示的に「PST」とあるため、実際の季節に関わらずUTC-8として計算。N-15/N-16も同様に「EDT」表記をUTC-4として計算）。
- **N-17, N-18**：すでにJST表記のためそのまま。
- **N-21**：送信日（2026年4月9日・木曜）から見た「来週の木曜」＝2026年4月16日として計算。
- **N-22**：送信日（2026年10月15日・木曜）から見た「来週の木曜」＝2026年10月22日として計算（GMT＝UTC+0として換算）。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料B・1回目

```
## 一覧(日本時間)

- N-01: 2026年5月18日 21:30
- N-02: 2026年7月6日 23:00
- N-03: 2026年8月2日 23:00
- N-04: 2026年4月22日 5:00
- N-05: 2026年5月27日 8:00
- N-06: 2026年10月9日 8:00
- N-07: 2026年6月25日 9:30
- N-08: 2026年11月4日 11:00
- N-09: 2026年5月12日 1:30
- N-10: 2026年8月19日 8:00
- N-11: 2026年4月14日 23:00
- N-12: 2026年10月21日 2:00
- N-13: 2026年5月12日 2:30
- N-14: 2026年9月16日 7:00
- N-15: 2026年1月9日 0:00
- N-16: 2026年12月18日 4:00
- N-17: 2026年6月15日 14:00
- N-18: 2026年11月2日 9:00
- N-19: 2026年4月30日 2:00
- N-20: 2026年12月10日 0:45
- N-21: 2026年5月14日 23:00
- N-22: 2026年9月17日 23:00
- N-23: 2026年7月6日 16:00
- N-24: 2026年10月12日 12:00

---

### 換算にあたっての注意点

- **N-09/N-10(PT)**: 該当日は米国夏時間期間中のため、PDT(UTC-7)として換算しました。
- **N-11/N-12(ET)**: 該当日は米国夏時間期間中のため、EDT(UTC-4)として換算しました(N-12の10月20日は夏時間終了前です)。
- **N-13/N-14**: 本文に明記された「PST」の表記をそのまま採用し、UTC-8として換算しました(季節的には本来PDTの時期ですが、記載を優先)。
- **N-15/N-16**: 本文に明記された「EDT」の表記をそのまま採用し、UTC-4として換算しました(N-15の1月は本来ESTの時期ですが、記載を優先)。
- **N-21**: 送信日(2026年5月7日・木曜)から見た「来週木曜」= 2026年5月14日として計算しました。
- **N-22**: 送信日(2026年9月10日・木曜)から見た「来週木曜」= 2026年9月17日、本文明記の「GMT」(UTC+0)をそのまま採用しました(英国は同時期サマータイムでUTC+1が実態ですが、記載を優先)。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料B・2回目

```
# JST変換一覧

| ID | 日本時間 |
|---|---|
| N-01 | 2026年5月18日(月) 21:30 |
| N-02 | 2026年7月6日(月) 23:00 |
| N-03 | 2026年8月2日(日) 23:00 |
| N-04 | 2026年4月22日(水) 05:00 |
| N-05 | 2026年5月27日(水) 08:00 |
| N-06 | 2026年10月9日(金) 08:00 |
| N-07 | 2026年6月25日(木) 09:30 |
| N-08 | 2026年11月4日(水) 11:00 |
| N-09 | 2026年5月12日(火) 01:30 |
| N-10 | 2026年8月19日(水) 08:00 |
| N-11 | 2026年4月14日(火) 23:00 |
| N-12 | 2026年10月21日(水) 02:00 |
| N-13 | 2026年5月12日(火) 02:30 |
| N-14 | 2026年9月16日(水) 07:00 |
| N-15 | 2026年1月9日(金) 00:00 |
| N-16 | 2026年12月18日(金) 04:00 |
| N-17 | 2026年6月15日(月) 14:00 |
| N-18 | 2026年11月2日(月) 09:00 |
| N-19 | 2026年4月30日(木) 02:00 |
| N-20 | 2026年12月10日(木) 00:45 |
| N-21 | 2026年5月14日(木) 23:00 |
| N-22 | 2026年9月17日(木) 23:00 |
| N-23 | 2026年7月6日(月) 16:00 |
| N-24 | 2026年10月12日(月) 12:00 |

---

## 換算の根拠(注意が必要だった点)

- **UTC+12/+11/+10/+5:30 など明示オフセット**:そのまま計算(N-01, N-02, N-03, N-19, N-20, N-23, N-24)。
- **N-04(ダブリン)**:4月21日はアイルランドのサマータイム期間中で、明記されたUTC+1は実態と一致。
- **N-05(アクラ)/N-06(ブエノスアイレス)/N-07(メキシコシティ)/N-08(ホノルル)**:いずれもDSTを採用しない地域(またはメキシコは2022年よりDST廃止)のため、明記オフセットをそのまま使用。
- **N-09(サンディエゴ)/N-10(サクラメント)**:「PT」は日付に応じた実際の区分が必要 → 5月・8月は夏時間なのでPDT(UTC-7)。
- **N-11(フィラデルフィア)**:4月14日はEDT期間中(UTC-4)。
- **N-12(ローリー)**:10月20日はDST終了(11/1)前なのでまだEDT(UTC-4)。
- **N-13(ロサンゼルス)/N-14(フレズノ)**:本文に明示的に「PST」(=UTC-8)と表記されているため、実際は夏時間期間中でもラベル通りUTC-8として換算(意図的な冬時間表記と解釈)。
- **N-15(ワシントン)/N-16(オーランド)**:同様に本文が明示的に「EDT」(=UTC-4)と表記されているため、実際の季節(1月・12月は本来EST)に関わらずラベル通りUTC-4で換算。
- **N-17, N-18**:すでにJSTのためそのまま。
- **N-21(デトロイト)**:送信日(木、5/7)から「next Thursday」=翌週木曜5/14と解釈。ETは日付に応じて実際の区分が必要 → 5月はEDT(UTC-4)。
- **N-22(エディンバラ)**:送信日(木、9/10)から「next Thursday」=翌週木曜9/17と解釈。本文で明示的に「GMT」(=UTC+0)と表記されているため、実際の英国夏時間(BST/UTC+1)期間中でもラベル通りUTC+0で換算。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 判定

**採用**。材料2本×各2回＝のべ96件、24件×4回とも真値と完全一致。

---

## 指示文2（記事2節・時差と夏時間を申告させる）

### 送った指示文（記事と同一文字列）

```
次の案内をすべて日本時間に直して、一覧にしてください。

日付・時刻を、日本の読者がそのまま読める形にしてください。

書き換えたものは、原文の表記をカッコの中に残してください。

時差の換算をしたときは、換算前の時刻と、使った時差（協定世界時からの差）も書いてください。夏時間の有無も書いてください。

1件につき1行、「ID: 日本時間の日付と時刻」の形式で先に一覧を書いてください。行の後ろに、原文の表記・使った時差・夏時間の有無を続けて書いてください。
```

### 材料A・1回目

```
# 日本時間換算 一覧

- N-01: 2026年4月12日(日) 21:00
- N-02: 2026年5月4日(月) 23:30
- N-03: 2026年6月8日(月) 23:30
- N-04: 2026年3月18日(水) 5:00
- N-05: 2026年4月3日(金) 6:00
- N-06: 2026年7月15日(水) 9:30
- N-07: 2026年9月22日(火) 9:00
- N-08: 2026年8月12日(水) 10:00
- N-09: 2026年4月8日(水) 1:00
- N-10: 2026年6月17日(水) 7:00
- N-11: 2026年5月13日(水) 0:00
- N-12: 2026年9月10日(木) 3:00
- N-13: 2026年4月8日(水) 2:00
- N-14: 2026年7月3日(金) 6:00
- N-15: 2026年12月3日(木) 23:00
- N-16: 2026年1月21日(水) 5:00
- N-17: 2026年5月1日(金) 13:00
- N-18: 2026年10月6日(火) 9:30
- N-19: 2026年3月26日(木) 2:30
- N-20: 2026年11月13日(金) 0:15
- N-21: 2026年4月16日(木) 22:00
- N-22: 2026年10月23日(金) 0:00
- N-23: 2026年6月2日(火) 17:00
- N-24: 2026年9月3日(木) 12:00

---

## 詳細（原文表記・使用時差・夏時間の有無）

**N-01**（Auckland Ops）
原文：Monday, April 13, 2026, 1:00 AM (UTC+13)
時差：UTC+13 → JST（差 −4時間）
夏時間：あり（ニュージーランド夏時間 NZDT, UTC+13）

**N-02**（Fiji Logistics）
原文：Tuesday, May 5, 2026, 2:30 AM (UTC+12)
時差：UTC+12 → JST（差 −3時間）
夏時間：なし（フィジー標準時、通年UTC+12）

**N-03**（Sydney Support）
原文：Tuesday, June 9, 2026, 1:30 AM (UTC+11)
時差：UTC+11 → JST（差 −2時間）
夏時間：原文表記のUTC+11はオーストラリア夏時間（AEDT）相当。ただし6月は南半球の冬で、シドニーの実際の標準時はUTC+10のため、原文の表記に矛盾がある可能性があります。ここでは原文表記のUTC+11をそのまま採用しました。

**N-04**（London HQ）
原文：Tuesday, March 17, 2026, 8:00 PM (UTC+0)
時差：UTC+0 → JST（差 +9時間）
夏時間：なし（GMT。英国の夏時間BSTは2026年3月29日開始のため、3月17日はまだ標準時）

**N-05**（Lagos Partner）
原文：Thursday, April 2, 2026, 10:00 PM (UTC+1)
時差：UTC+1 → JST（差 +8時間）
夏時間：なし（西アフリカ時間WAT、通年UTC+1固定）

**N-06**（Sao Paulo Finance）
原文：Tuesday, July 14, 2026, 9:30 PM (UTC-3)
時差：UTC−3 → JST（差 +12時間）
夏時間：なし（ブラジルは2019年に夏時間制度を廃止、通年UTC−3）

**N-07**（Toronto Vendor）
原文：Monday, September 21, 2026, 7:00 PM (UTC-5)
時差：UTC−5 → JST（差 +14時間）
夏時間：原文表記のUTC−5はEST（標準時）相当ですが、9月のトロントは実際には夏時間EDT（UTC−4）期間中です。原文の表記に矛盾がある可能性がありますが、ここでは原文表記のUTC−5をそのまま採用しました。

**N-08**（Anchorage Field）
原文：Tuesday, August 11, 2026, 5:00 PM (UTC-8)
時差：UTC−8 → JST（差 +17時間）
夏時間：あり（アラスカ夏時間 AKDT, UTC−8）

**N-09**（Seattle Product）
原文：Tuesday, April 7, 2026, 9:00 AM PT
時差：PT＝太平洋夏時間PDT（UTC−7）と判断 → JST（差 +16時間）
夏時間：あり（2026年の米国夏時間は3月8日開始のため、4月はPDT）

**N-10**（Portland Design）
原文：Tuesday, June 16, 2026, 3:00 PM PT
時差：PT＝PDT（UTC−7）→ JST（差 +16時間）
夏時間：あり（PDT）

**N-11**（Boston Legal）
原文：Tuesday, May 12, 2026, 11:00 AM ET
時差：ET＝EDT（UTC−4）→ JST（差 +13時間）
夏時間：あり（EDT）

**N-12**（Atlanta Sales）
原文：Wednesday, September 9, 2026, 2:00 PM ET
時差：ET＝EDT（UTC−4）→ JST（差 +13時間）
夏時間：あり（EDT）

**N-13**（San Jose Eng）
原文：Tuesday, April 7, 2026, 9:00 AM PST
時差：原文表記のPST（UTC−8）をそのまま採用 → JST（差 +17時間）
夏時間：原文表記は「PST」（標準時）ですが、実際の4月の北米西海岸は夏時間PDT（UTC−7）期間です。原文表記のUTC−8をそのまま使用しました。

**N-14**（Fresno Ops）
原文：Thursday, July 2, 2026, 1:00 PM PST
時差：原文表記のPST（UTC−8）をそのまま採用 → JST（差 +17時間）
夏時間：原文表記は「PST」ですが、実際の7月は夏時間PDT（UTC−7）期間です。原文表記のUTC−8をそのまま使用しました。

**N-15**（New York Ops）
原文：Thursday, December 3, 2026, 10:00 AM EDT
時差：原文表記のEDT（UTC−4）をそのまま採用 → JST（差 +13時間）
夏時間：原文表記は「EDT」ですが、実際の12月は標準時EST（UTC−5）期間です。原文表記のUTC−4をそのまま使用しました。

**N-16**（Miami Support）
原文：Tuesday, January 20, 2026, 4:00 PM EDT
時差：原文表記のEDT（UTC−4）をそのまま採用 → JST（差 +13時間）
夏時間：原文表記は「EDT」ですが、実際の1月は標準時EST（UTC−5）期間です。原文表記のUTC−4をそのまま使用しました。

**N-17**（Tokyo HQ）
原文：Friday, May 1, 2026, 1:00 PM JST
時差：換算不要（既にJST、UTC+9）
夏時間：なし（日本にサマータイム制度なし）

**N-18**（Osaka Branch）
原文：Tuesday, October 6, 2026, 9:30 AM JST
時差：換算不要（既にJST、UTC+9）
夏時間：なし（日本にサマータイム制度なし）

**N-19**（Bengaluru Dev）
原文：Wednesday, March 25, 2026, 11:00 PM IST (UTC+5:30)
時差：UTC+5:30 → JST（差 +3時間30分）
夏時間：なし（インドにサマータイム制度なし、通年UTC+5:30）

**N-20**（Mumbai Finance）
原文：Thursday, November 12, 2026, 8:45 PM IST (UTC+5:30)
時差：UTC+5:30 → JST（差 +3時間30分）
夏時間：なし（インドにサマータイム制度なし）

**N-21**（Chicago Client）
原文：送信日 Thursday, April 9, 2026／本文「next Thursday at 9:00 AM ET」（2026年4月16日と解釈）
時差：ET＝EDT（UTC−4）→ JST（差 +13時間）
夏時間：あり（EDT）

**N-22**（Dublin Partner）
原文：送信日 Thursday, October 15, 2026／本文「next Thursday at 3:00 PM GMT」（2026年10月22日と解釈）
時差：原文表記のGMT（UTC+0）をそのまま採用 → JST（差 +9時間）
夏時間：原文表記は「GMT」（標準時）ですが、アイルランドの夏時間IST（2026年は10月25日終了）は10月22日時点でまだ有効です。原文表記のUTC+0をそのまま使用しました。

**N-23**（Berlin Office）
原文：Tuesday, June 2, 2026, 10:00 AM (UTC+2)
時差：UTC+2 → JST（差 +7時間）
夏時間：あり（中央ヨーロッパ夏時間 CEST, UTC+2）

**N-24**（Manila Support）
原文：Thursday, September 3, 2026, 11:00 AM (UTC+8)
時差：UTC+8 → JST（差 +1時間）
夏時間：なし（フィリピン標準時、通年UTC+8固定）
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料A・2回目

```
以下、すべて日本時間（JST, UTC+9、日本にはサマータイムなし）に統一した一覧です。1件につき1行で、「ID: 日本時間」の後ろに「原文の表記／使った時差／夏時間の有無」を続けています。

- **N-01**: 2026年4月12日(日) 21:00 ／原文: "Monday, April 13, 2026, 1:00 AM (UTC+13)" ／使った時差: UTC+13 ／夏時間: あり（NZDT＝ニュージーランド夏時間相当）
- **N-02**: 2026年5月4日(月) 23:30 ／原文: "Tuesday, May 5, 2026, 2:30 AM (UTC+12)" ／使った時差: UTC+12 ／夏時間: なし（フィジー標準時）
- **N-03**: 2026年6月8日(月) 23:30 ／原文: "Tuesday, June 9, 2026, 1:30 AM (UTC+11)" ／使った時差: UTC+11 ／夏時間: あり（AEDT表記。※実際の6月豪州は南半球の冬で標準時UTC+10が通常だが、原文表記のUTC+11をそのまま採用）
- **N-04**: 2026年3月18日(水) 5:00 ／原文: "Tuesday, March 17, 2026, 8:00 PM (UTC+0)" ／使った時差: UTC+0 ／夏時間: なし（GMT。英国夏時間開始前）
- **N-05**: 2026年4月3日(金) 6:00 ／原文: "Thursday, April 2, 2026, 10:00 PM (UTC+1)" ／使った時差: UTC+1 ／夏時間: なし（ナイジェリアはWAT、通年夏時間なし）
- **N-06**: 2026年7月15日(水) 9:30 ／原文: "Tuesday, July 14, 2026, 9:30 PM (UTC-3)" ／使った時差: UTC-3 ／夏時間: なし（ブラジルは2019年に夏時間廃止）
- **N-07**: 2026年9月22日(火) 9:00 ／原文: "Monday, September 21, 2026, 7:00 PM (UTC-5)" ／使った時差: UTC-5 ／夏時間: なし（UTC-5＝EST表記。※実際の9月トロントは夏時間中のEDT＝UTC-4が通常だが、原文表記をそのまま採用）
- **N-08**: 2026年8月12日(水) 10:00 ／原文: "Tuesday, August 11, 2026, 5:00 PM (UTC-8)" ／使った時差: UTC-8 ／夏時間: あり（ADT＝アラスカ夏時間）
- **N-09**: 2026年4月8日(水) 1:00 ／原文: "Tuesday, April 7, 2026, 9:00 AM PT" ／使った時差: UTC-7（PT表記のため、4月は夏時間期間としてPDTを採用）／夏時間: あり
- **N-10**: 2026年6月17日(水) 7:00 ／原文: "Tuesday, June 16, 2026, 3:00 PM PT" ／使った時差: UTC-7（PDT）／夏時間: あり
- **N-11**: 2026年5月13日(水) 0:00 ／原文: "Tuesday, May 12, 2026, 11:00 AM ET" ／使った時差: UTC-4（ET表記のため、5月は夏時間期間としてEDTを採用）／夏時間: あり
- **N-12**: 2026年9月10日(木) 3:00 ／原文: "Wednesday, September 9, 2026, 2:00 PM ET" ／使った時差: UTC-4（EDT）／夏時間: あり
- **N-13**: 2026年4月8日(水) 2:00 ／原文: "Tuesday, April 7, 2026, 9:00 AM PST" ／使った時差: UTC-8（PST表記どおり採用）／夏時間: なし（※実際の4月太平洋岸は夏時間中でPDT＝UTC-7が通常だが、原文のPST表記をそのまま採用）
- **N-14**: 2026年7月3日(金) 6:00 ／原文: "Thursday, July 2, 2026, 1:00 PM PST" ／使った時差: UTC-8（PST表記どおり採用）／夏時間: なし（※同上の注意点あり）
- **N-15**: 2026年12月3日(木) 23:00 ／原文: "Thursday, December 3, 2026, 10:00 AM EDT" ／使った時差: UTC-4（EDT表記どおり採用）／夏時間: あり（※実際の12月米東部は標準時EST＝UTC-5が通常だが、原文のEDT表記をそのまま採用）
- **N-16**: 2026年1月21日(水) 5:00 ／原文: "Tuesday, January 20, 2026, 4:00 PM EDT" ／使った時差: UTC-4（EDT表記どおり採用）／夏時間: あり（※同上の注意点あり）
- **N-17**: 2026年5月1日(金) 13:00 ／原文: "Friday, May 1, 2026, 1:00 PM JST" ／使った時差: UTC+9（変換不要、すでに日本時間）／夏時間: なし（日本は夏時間制度なし）
- **N-18**: 2026年10月6日(火) 9:30 ／原文: "Tuesday, October 6, 2026, 9:30 AM JST" ／使った時差: UTC+9（変換不要）／夏時間: なし
- **N-19**: 2026年3月26日(木) 2:30 ／原文: "Wednesday, March 25, 2026, 11:00 PM IST (UTC+5:30)" ／使った時差: UTC+5:30 ／夏時間: なし（インドは夏時間なし）
- **N-20**: 2026年11月13日(金) 0:15 ／原文: "Thursday, November 12, 2026, 8:45 PM IST (UTC+5:30)" ／使った時差: UTC+5:30 ／夏時間: なし
- **N-21**: 2026年4月16日(木) 22:00 ／原文: 送信日 "Thursday, April 9, 2026" ＋本文 "next Thursday at 9:00 AM ET"（送信日自体が木曜のため、「次の木曜日」＝2026年4月16日と解釈）／使った時差: UTC-4（ET表記のため、4月はEDTを採用）／夏時間: あり
- **N-22**: 2026年10月23日(金) 0:00 ／原文: 送信日 "Thursday, October 15, 2026" ＋本文 "next Thursday at 3:00 PM GMT"（同様に「次の木曜日」＝2026年10月22日と解釈）／使った時差: UTC+0（GMT表記どおり採用）／夏時間: なし（※実際は英国夏時間BSTが10月25日まで続くため10月22日はBST＝UTC+1が通常だが、原文のGMT表記をそのまま採用）
- **N-23**: 2026年6月2日(火) 17:00 ／原文: "Tuesday, June 2, 2026, 10:00 AM (UTC+2)" ／使った時差: UTC+2 ／夏時間: あり（CEST＝中欧夏時間）
- **N-24**: 2026年9月3日(木) 12:00 ／原文: "Thursday, September 3, 2026, 11:00 AM (UTC+8)" ／使った時差: UTC+8 ／夏時間: なし（フィリピンは夏時間なし）

**補足（前提の確認）**
- N-21・N-22は送信日自体が「次の木曜日」の起点となる曜日（木曜）だったため、「次の木曜日」＝送信日の7日後と解釈しました。別の解釈（送信日と同日を指す等）であれば結果が変わります。
- 一部の通知（N-03、N-07、N-13、N-14、N-15、N-16、N-22）は、実際の暦上の夏時間切替時期と表記されたタイムゾーン略号／UTCオフセットが一致していませんが、いずれも原文に明記された数値・略号をそのまま正としてJST換算しています。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料B・1回目

```
以下、すべての案内を日本時間（JST, UTC+9）に統一した一覧です。まず要約一覧、続けて各件の原文表記・換算に使った時差・夏時間の有無を記載します。

## 一覧（日本時間）

- N-01: 2026年5月18日(月) 21:30
- N-02: 2026年7月6日(月) 23:00
- N-03: 2026年8月2日(日) 23:00
- N-04: 2026年4月22日(水) 5:00
- N-05: 2026年5月27日(水) 8:00
- N-06: 2026年10月9日(金) 8:00
- N-07: 2026年6月25日(木) 9:30
- N-08: 2026年11月4日(水) 11:00
- N-09: 2026年5月12日(火) 1:30
- N-10: 2026年8月19日(水) 8:00
- N-11: 2026年4月14日(火) 23:00
- N-12: 2026年10月21日(水) 2:00
- N-13: 2026年5月12日(火) 2:30
- N-14: 2026年9月16日(水) 7:00
- N-15: 2026年1月9日(金) 0:00
- N-16: 2026年12月18日(金) 4:00
- N-17: 2026年6月15日(月) 14:00
- N-18: 2026年11月2日(月) 9:00
- N-19: 2026年4月30日(木) 2:00
- N-20: 2026年12月10日(木) 0:45
- N-21: 2026年5月14日(木) 23:00
- N-22: 2026年9月17日(木) 23:00
- N-23: 2026年7月6日(月) 16:00
- N-24: 2026年10月12日(月) 12:00

## 詳細（原文表記・時差・夏時間）

**N-01**（Wellington Ops）
原文: Tuesday, May 19, 2026, 12:30 AM (UTC+12)
換算: UTC+12 → JST(UTC+9)、差 −3時間
夏時間: なし（5月はニュージーランドの標準時期間）

**N-02**（Noumea Logistics）
原文: Tuesday, July 7, 2026, 1:00 AM (UTC+11)
換算: UTC+11 → JST、差 −2時間
夏時間: なし（ニューカレドニアは夏時間制度なし）

**N-03**（Suva Support）
原文: Monday, August 3, 2026, 2:00 AM (UTC+12)
換算: UTC+12 → JST、差 −3時間
夏時間: なし（8月はフィジーの夏時間期間外）

**N-04**（Dublin HQ）
原文: Tuesday, April 21, 2026, 9:00 PM (UTC+1)
換算: UTC+1 → JST、差 −8時間
夏時間: あり（4月21日はアイルランド夏時間期間中。原文のUTC+1にはこの夏時間が反映済み）

**N-05**（Accra Partner）
原文: Tuesday, May 26, 2026, 11:00 PM (UTC+0)
換算: UTC+0 → JST、差 −9時間
夏時間: なし（ガーナは夏時間制度なし）

**N-06**（Buenos Aires Finance）
原文: Thursday, October 8, 2026, 8:00 PM (UTC-3)
換算: UTC−3 → JST、差 −12時間
夏時間: なし（アルゼンチンは夏時間を廃止済み）

**N-07**（Mexico City Vendor）
原文: Wednesday, June 24, 2026, 6:30 PM (UTC-6)
換算: UTC−6 → JST、差 −15時間
夏時間: なし（メキシコシティは夏時間を廃止済み、年間UTC−6）

**N-08**（Honolulu Field）
原文: Tuesday, November 3, 2026, 4:00 PM (UTC-10)
換算: UTC−10 → JST、差 −19時間
夏時間: なし（ハワイは夏時間制度なし）

**N-09**（San Diego Product）
原文: Monday, May 11, 2026, 9:30 AM PT
換算: PT=PDT（夏時間、UTC−7）→ JST、差 −16時間
夏時間: あり（5月は米国夏時間期間中）

**N-10**（Sacramento Design）
原文: Tuesday, August 18, 2026, 4:00 PM PT
換算: PT=PDT（UTC−7）→ JST、差 −16時間
夏時間: あり（8月は米国夏時間期間中）

**N-11**（Philadelphia Legal）
原文: Tuesday, April 14, 2026, 10:00 AM ET
換算: ET=EDT（UTC−4）→ JST、差 −13時間
夏時間: あり（4月は米国夏時間期間中）

**N-12**（Raleigh Sales）
原文: Tuesday, October 20, 2026, 1:00 PM ET
換算: ET=EDT（UTC−4）→ JST、差 −13時間
夏時間: あり（10月20日はまだ米国夏時間期間中、終了は11月1日）

**N-13**（Los Angeles Eng）
原文: Monday, May 11, 2026, 9:30 AM PST
換算: 原文表記のPST（標準時、UTC−8）をそのまま採用 → JST、差 −17時間
夏時間: 原文表記上は「なし」。ただし5月は本来PDT（夏時間, UTC−7）にあたる時期であり、PSTという表記自体が実態と不整合の可能性がある点に注意

**N-14**（Fresno Sales）
原文: Tuesday, September 15, 2026, 2:00 PM PST
換算: 原文表記のPST（UTC−8）をそのまま採用 → JST、差 −17時間
夏時間: 原文表記上は「なし」。ただし9月は本来PDT（夏時間）にあたる時期であり、同様に表記との不整合の可能性あり

**N-15**（Washington Ops）
原文: Thursday, January 8, 2026, 11:00 AM EDT
換算: 原文表記のEDT（夏時間, UTC−4）をそのまま採用 → JST、差 −13時間
夏時間: 原文表記上は「あり」。ただし1月は本来EST（標準時, UTC−5）にあたる時期であり、EDTという表記自体が実態と不整合の可能性がある点に注意

**N-16**（Orlando Support）
原文: Thursday, December 17, 2026, 3:00 PM EDT
換算: 原文表記のEDT（UTC−4）をそのまま採用 → JST、差 −13時間
夏時間: 原文表記上は「あり」。ただし12月は本来EST（標準時）にあたる時期であり、同様に不整合の可能性あり

**N-17**（Nagoya HQ）
原文: Monday, June 15, 2026, 2:00 PM JST
換算: 換算不要（元々日本時間で表記済み）
夏時間: なし（日本は夏時間制度なし）

**N-18**（Fukuoka Branch）
原文: Monday, November 2, 2026, 9:00 AM JST
換算: 換算不要（元々日本時間で表記済み）
夏時間: なし（日本は夏時間制度なし）

**N-19**（Pune Dev）
原文: Wednesday, April 29, 2026, 10:30 PM IST (UTC+5:30)
換算: UTC+5:30 → JST、差 −3時間30分
夏時間: なし（インドは夏時間制度なし）

**N-20**（Chennai Finance）
原文: Wednesday, December 9, 2026, 9:15 PM IST (UTC+5:30)
換算: UTC+5:30 → JST、差 −3時間30分
夏時間: なし（インドは夏時間制度なし）

**N-21**（Detroit Client）
原文: 送信日 Thursday, May 7, 2026／本文中「next Thursday at 10:00 AM ET」→ 2026年5月14日(木) 10:00 AM ETと解釈
換算: ET=EDT（UTC−4）→ JST、差 −13時間
夏時間: あり（5月は米国夏時間期間中）

**N-22**（Edinburgh Partner）
原文: 送信日 Thursday, September 10, 2026／本文中「next Thursday at 2:00 PM GMT」→ 2026年9月17日(木) 2:00 PM GMTと解釈
換算: 原文表記のGMT（UTC+0）をそのまま採用 → JST、差 −9時間
夏時間: 原文表記上は「なし」。ただし9月17日は本来英国夏時間（BST, UTC+1）の期間中であり、GMTという表記自体が実態と不整合の可能性がある点に注意

**N-23**（Warsaw Office）
原文: Monday, July 6, 2026, 9:00 AM (UTC+2)
換算: UTC+2 → JST、差 −7時間
夏時間: あり（7月はポーランドの夏時間期間中。原文のUTC+2にはこの夏時間が反映済み）

**N-24**（Jakarta Support）
原文: Monday, October 12, 2026, 10:00 AM (UTC+7)
換算: UTC+7 → JST、差 −2時間
夏時間: なし（インドネシアは夏時間制度なし）

---

**補足**: N-13、N-14、N-15、N-16、N-22 は、原文の時刻帯表記（PST/EDT/GMTなど）と実際の日付における夏時間・標準時の運用が食い違っている可能性があります。上記では原文の表記をそのまま数値として採用して換算していますが、送信元の意図次第では実際の現地時刻が1時間前後する可能性がある点にご留意ください。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料B・2回目

```
以下、すべて日本時間（JST, UTC+9、夏時間なし）に変換した一覧です。1件1行で、原文の表記・使った時差（UTC差）・夏時間の有無を続けて記載しています。

**[N-01]** 2026年5月18日(月) 21:30 ／原文: Tuesday, May 19, 2026, 12:30 AM (UTC+12) ／使用時差: UTC+12 ／夏時間: なし（NZ標準時）

**[N-02]** 2026年7月6日(月) 23:00 ／原文: Tuesday, July 7, 2026, 1:00 AM (UTC+11) ／使用時差: UTC+11 ／夏時間: なし（ニューカレドニアはDSTなし）

**[N-03]** 2026年8月2日(日) 23:00 ／原文: Monday, August 3, 2026, 2:00 AM (UTC+12) ／使用時差: UTC+12 ／夏時間: なし（8月はフィジー標準時期間）

**[N-04]** 2026年4月22日(水) 05:00 ／原文: Tuesday, April 21, 2026, 9:00 PM (UTC+1) ／使用時差: UTC+1 ／夏時間: あり（アイルランド夏時間、4月下旬は適用中）

**[N-05]** 2026年5月27日(水) 08:00 ／原文: Tuesday, May 26, 2026, 11:00 PM (UTC+0) ／使用時差: UTC+0 ／夏時間: なし（ガーナはDSTなし）

**[N-06]** 2026年10月9日(金) 08:00 ／原文: Thursday, October 8, 2026, 8:00 PM (UTC-3) ／使用時差: UTC-3 ／夏時間: なし（アルゼンチンは2009年以降DS Tなし）

**[N-07]** 2026年6月25日(木) 09:30 ／原文: Wednesday, June 24, 2026, 6:30 PM (UTC-6) ／使用時差: UTC-6 ／夏時間: なし（メキシコシティは2022年にDST廃止）

**[N-08]** 2026年11月4日(水) 11:00 ／原文: Tuesday, November 3, 2026, 4:00 PM (UTC-10) ／使用時差: UTC-10 ／夏時間: なし（ハワイはDSTなし）

**[N-09]** 2026年5月12日(火) 01:30 ／原文: Monday, May 11, 2026, 9:30 AM PT ／使用時差: UTC-7（PDT） ／夏時間: あり（5月は太平洋夏時間期間のためPDTとして換算）

**[N-10]** 2026年8月19日(水) 08:00 ／原文: Tuesday, August 18, 2026, 4:00 PM PT ／使用時差: UTC-7（PDT） ／夏時間: あり（8月はPDT期間）

**[N-11]** 2026年4月14日(火) 23:00 ／原文: Tuesday, April 14, 2026, 10:00 AM ET ／使用時差: UTC-4（EDT） ／夏時間: あり（4月中旬は東部夏時間期間）

**[N-12]** 2026年10月21日(水) 02:00 ／原文: Tuesday, October 20, 2026, 1:00 PM ET ／使用時差: UTC-4（EDT） ／夏時間: あり（10月下旬はEDT期間）

**[N-13]** 2026年5月12日(火) 02:30 ／原文: Monday, May 11, 2026, 9:30 AM PST ／使用時差: UTC-8 ／夏時間: なし（※原文が「PST」と明記されているためそのまま採用。実際の暦では5月は夏時間期間でPDT=UTC-7となる点に注意）

**[N-14]** 2026年9月16日(水) 07:00 ／原文: Tuesday, September 15, 2026, 2:00 PM PST ／使用時差: UTC-8 ／夏時間: なし（※同上。実暦では9月はPDT期間）

**[N-15]** 2026年1月9日(金) 00:00 ／原文: Thursday, January 8, 2026, 11:00 AM EDT ／使用時差: UTC-4 ／夏時間: あり（※原文が「EDT」と明記されているためそのまま採用。実際の暦では1月は標準時期間でEST=UTC-5となる点に注意）

**[N-16]** 2026年12月18日(金) 04:00 ／原文: Thursday, December 17, 2026, 3:00 PM EDT ／使用時差: UTC-4 ／夏時間: あり（※同上。実暦では12月はEST期間）

**[N-17]** 2026年6月15日(月) 14:00 ／原文: Monday, June 15, 2026, 2:00 PM JST ／使用時差: 換算不要（既にJST） ／夏時間: なし（日本はDSTなし）

**[N-18]** 2026年11月2日(月) 09:00 ／原文: Monday, November 2, 2026, 9:00 AM JST ／使用時差: 換算不要（既にJST） ／夏時間: なし

**[N-19]** 2026年4月30日(木) 02:00 ／原文: Wednesday, April 29, 2026, 10:30 PM IST (UTC+5:30) ／使用時差: UTC+5:30 ／夏時間: なし（インドはDSTなし）

**[N-20]** 2026年12月10日(木) 00:45 ／原文: Wednesday, December 9, 2026, 9:15 PM IST (UTC+5:30) ／使用時差: UTC+5:30 ／夏時間: なし

**[N-21]** 2026年5月14日(木) 23:00 ／原文: 送信 Thursday, May 7, 2026「next Thursday at 10:00 AM ET」 ／換算前日時（推定）: 2026年5月14日 10:00 ET ／使用時差: UTC-4（EDT、5月は夏時間期間） ／夏時間: あり ／※「next Thursday」は送信日の翌週の木曜（5/14）と解釈

**[N-22]** 2026年9月17日(木) 23:00 ／原文: 送信 Thursday, September 10, 2026「next Thursday at 2:00 PM GMT」 ／換算前日時（推定）: 2026年9月17日 14:00 GMT ／使用時差: UTC+0 ／夏時間: なし（※原文が「GMT」と明記のためUTC+0を採用。実暦では9月は英国夏時間BST=UTC+1の期間） ／※「next Thursday」は送信日の翌週の木曜（9/17）と解釈

**[N-23]** 2026年7月6日(月) 16:00 ／原文: Monday, July 6, 2026, 9:00 AM (UTC+2) ／使用時差: UTC+2 ／夏時間: あり（ポーランド夏時間、7月は適用中）

**[N-24]** 2026年10月12日(月) 12:00 ／原文: Monday, October 12, 2026, 10:00 AM (UTC+7) ／使用時差: UTC+7 ／夏時間: なし（インドネシアはDSTなし）

---

**補足（前提の明示）**
- N-13・N-14は原文表記が「PST」（本来5月・9月は夏時間期間でPDTのはずですが）となっていたため、表記どおりUTC-8として換算しました。
- N-15・N-16は原文表記が「EDT」（本来1月・12月は標準時期間でESTのはずですが）となっていたため、表記どおりUTC-4として換算しました。
- N-21・N-22は「next Thursday」の起点日そのものが木曜日だったため、「翌週の木曜日」と解釈して日付を確定しました。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 判定

**採用**。のべ96件とも真値と完全一致し、申告された「使った時差」も真値と96件とも一致した（★4形の自己申告と実測の突き合わせ）。

---

## 指示文3（記事3節・決められないものは〔要確認〕）

### 送った指示文（記事と同一文字列）

```
次の案内をすべて日本時間に直して、一覧にしてください。

日付・時刻を、日本の読者がそのまま読める形にしてください。

書き換えたものは、原文の表記をカッコの中に残してください。

時差の換算をしたときは、換算前の時刻と、使った時差（協定世界時からの差）も書いてください。夏時間の有無も書いてください。

夏時間かどうかが決められないものは換算せず、〔要確認〕と書いてください。

1件につき1行、「ID: 日本時間の日付と時刻」の形式で先に一覧を書いてください。行の後ろに、原文の表記・使った時差・夏時間の有無を続けて書いてください。〔要確認〕にした場合はその旨を書いてください。
```

### 材料A・1回目

```
以下、全24件を日本時間（JST, UTC+9）に換算した一覧です。日本にはサマータイム制度がないため、JST側は常にUTC+9固定です。

---

- N-01: 2026年4月12日(日) 21:00 ｜原文: 2026年4月13日(月) 1:00 AM (UTC+13) ｜時差: UTC+13 ｜夏時間: あり（NZDT＝ニュージーランド夏時間、原文に明記）
- N-02: 2026年5月4日(月) 23:30 ｜原文: 2026年5月5日(火) 2:30 AM (UTC+12) ｜時差: UTC+12 ｜夏時間: なし（フィジー標準時、5月は非DST期間）
- N-03: 2026年6月8日(月) 23:30 ｜原文: 2026年6月9日(火) 1:30 AM (UTC+11) ｜時差: UTC+11（原文明記のまま採用）｜夏時間: あり扱い ※注：シドニーの夏時間は通常10〜4月で、6月は本来UTC+10のはず。原文の表記(UTC+11)を優先して換算
- N-04: 2026年3月18日(水) 5:00 ｜原文: 2026年3月17日(火) 8:00 PM (UTC+0) ｜時差: UTC+0 ｜夏時間: なし（英国のBST開始は3/29のため、3/17はGMT）
- N-05: 2026年4月3日(金) 6:00 ｜原文: 2026年4月2日(木) 10:00 PM (UTC+1) ｜時差: UTC+1 ｜夏時間: なし（ナイジェリアはDST制度なし、年間UTC+1）
- N-06: 2026年7月15日(水) 9:30 ｜原文: 2026年7月14日(火) 9:30 PM (UTC-3) ｜時差: UTC-3 ｜夏時間: なし（ブラジルは2019年にDST廃止済み）
- N-07: 2026年9月22日(火) 9:00 ｜原文: 2026年9月21日(月) 7:00 PM (UTC-5) ｜時差: UTC-5（原文明記のまま採用）｜夏時間: なし扱い ※注：トロントは通常3〜11月がEDT(UTC-4)期間で、9/21は本来UTC-4のはず。原文の表記(UTC-5)を優先して換算
- N-08: 2026年8月12日(水) 10:00 ｜原文: 2026年8月11日(火) 5:00 PM (UTC-8) ｜時差: UTC-8 ｜夏時間: あり（AKDT＝アラスカ夏時間、8月はDST期間で整合）
- N-09: 2026年4月8日(水) 1:00 ｜原文: 2026年4月7日(火) 9:00 AM PT ｜時差: UTC-7 ｜夏時間: あり（PDT。4月はDST期間中のため判定可能）
- N-10: 2026年6月17日(水) 7:00 ｜原文: 2026年6月16日(火) 3:00 PM PT ｜時差: UTC-7 ｜夏時間: あり（PDT。6月はDST期間中）
- N-11: 2026年5月13日(水) 0:00 ｜原文: 2026年5月12日(火) 11:00 AM ET ｜時差: UTC-4 ｜夏時間: あり（EDT。5月はDST期間中）
- N-12: 2026年9月10日(木) 3:00 ｜原文: 2026年9月9日(水) 2:00 PM ET ｜時差: UTC-4 ｜夏時間: あり（EDT。9月はDST期間中）
- N-13: 2026年4月8日(水) 2:00 ｜原文: 2026年4月7日(火) 9:00 AM PST ｜時差: UTC-8（原文明記のまま採用）｜夏時間: なし扱い ※注：実際の4月はPDT(UTC-7)期間のはず。原文の表記(PST)を優先して換算
- N-14: 2026年7月3日(金) 6:00 ｜原文: 2026年7月2日(木) 1:00 PM PST ｜時差: UTC-8（原文明記のまま採用）｜夏時間: なし扱い ※注：実際の7月はPDT(UTC-7)期間のはず。原文の表記(PST)を優先して換算
- N-15: 2026年12月3日(木) 23:00 ｜原文: 2026年12月3日(木) 10:00 AM EDT ｜時差: UTC-4（原文明記のまま採用）｜夏時間: あり扱い ※注：実際の12月はEST(UTC-5)期間のはず。原文の表記(EDT)を優先して換算
- N-16: 2026年1月21日(水) 5:00 ｜原文: 2026年1月20日(火) 4:00 PM EDT ｜時差: UTC-4（原文明記のまま採用）｜夏時間: あり扱い ※注：実際の1月はEST(UTC-5)期間のはず。原文の表記(EDT)を優先して換算
- N-17: 2026年5月1日(金) 13:00 ｜原文: 2026年5月1日(金) 1:00 PM JST ｜時差: なし（すでに日本時間）｜夏時間: 該当なし
- N-18: 2026年10月6日(火) 9:30 ｜原文: 2026年10月6日(火) 9:30 AM JST ｜時差: なし（すでに日本時間）｜夏時間: 該当なし
- N-19: 2026年3月26日(木) 2:30 ｜原文: 2026年3月25日(水) 11:00 PM IST (UTC+5:30) ｜時差: UTC+5:30 ｜夏時間: なし（インドはDST制度なし）
- N-20: 2026年11月13日(金) 0:15 ｜原文: 2026年11月12日(木) 8:45 PM IST (UTC+5:30) ｜時差: UTC+5:30 ｜夏時間: なし（インドはDST制度なし）
- N-21: 2026年4月16日(木) 22:00 ｜原文: 送信2026年4月9日(木)「next Thursday 9:00 AM ET」｜時差: UTC-4 ｜夏時間: あり（EDT。4月はDST期間中）※注：「next Thursday」は送信日の翌週木曜(4/16)と解釈
- N-22: 2026年10月23日(金) 0:00 ｜原文: 送信2026年10月15日(木)「next Thursday 3:00 PM GMT」｜時差: UTC+0（原文明記のまま採用）｜夏時間: なし扱い ※注：①「next Thursday」は送信日の翌週木曜(10/22)と解釈 ②アイルランドの夏時間(IST, UTC+1)終了は10/25のため10/22時点では本来UTC+1のはずだが、原文の表記(GMT)を優先して換算
- N-23: 2026年6月2日(火) 17:00 ｜原文: 2026年6月2日(火) 10:00 AM (UTC+2) ｜時差: UTC+2 ｜夏時間: あり（CEST＝中欧夏時間、6月はDST期間中で整合）
- N-24: 2026年9月3日(木) 12:00 ｜原文: 2026年9月3日(木) 11:00 AM (UTC+8) ｜時差: UTC+8 ｜夏時間: なし（フィリピンはDST制度なし）

補足:
- 〔要確認〕に該当した項目はありません（すべて原文にオフセットまたは日付から判定可能な情報があったため）。
- ただし N-03・N-07・N-13・N-14・N-15・N-16 は、原文の表記（UTC+11/UTC-5/PST/EDTなど）がその地域・時期の一般的な夏時間ルールと一致しない箇所があります。実態と異なる可能性がある旨を注記の上、原文の表記をそのまま優先して換算しました。
- N-21・N-22 は具体的な日付が書かれておらず「next Thursday」という表現のみのため、送信日の翌週の木曜日と解釈して換算しました（別解釈の可能性がある旨を注記済み）。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料A・2回目

```
以下、[N-01]〜[N-24]をすべて日本時間（JST, UTC+9, サマータイムなし）に変換した一覧です。各行は「ID: 日本時間」→「原文表記／使った時差／夏時間の有無」の順で記載しています。曜日は日本時間換算後のものを付記しました。

- **[N-01]** 2026年4月12日(日) 21:00
 原文: Monday, April 13, 2026, 1:00 AM (UTC+13) ／ 時差: UTC+13→UTC+9（4時間差し引き）／ 夏時間: あり（NZDT扱い。※実際のNZの暦では4/5にサマータイムが終了しUTC+12のはずだが、原文表記のUTC+13どおりに換算）

- **[N-02]** 2026年5月4日(月) 23:30
 原文: Tuesday, May 5, 2026, 2:30 AM (UTC+12) ／ 時差: UTC+12→UTC+9（3時間差し引き）／ 夏時間: なし（フィジー標準時。この時期のフィジーは実暦とも整合）

- **[N-03]** 2026年6月8日(月) 23:30
 原文: Tuesday, June 9, 2026, 1:30 AM (UTC+11) ／ 時差: UTC+11→UTC+9（2時間差し引き）／ 夏時間: あり（AEDT扱い。※実際のシドニーは6月は冬でUTC+10のはずだが、原文表記のUTC+11どおりに換算）

- **[N-04]** 2026年3月18日(水) 5:00
 原文: Tuesday, March 17, 2026, 8:00 PM (UTC+0) ／ 時差: UTC+0→UTC+9（9時間加算）／ 夏時間: なし（GMT。英国の夏時間開始は3/29のため実暦とも整合）

- **[N-05]** 2026年4月3日(金) 6:00
 原文: Thursday, April 2, 2026, 10:00 PM (UTC+1) ／ 時差: UTC+1→UTC+9（8時間加算）／ 夏時間: なし（ナイジェリアは西アフリカ時間でサマータイム制度なし）

- **[N-06]** 2026年7月15日(水) 9:30
 原文: Tuesday, July 14, 2026, 9:30 PM (UTC-3) ／ 時差: UTC-3→UTC+9（12時間加算）／ 夏時間: なし（ブラジルは2019年にサマータイム廃止済み）

- **[N-07]** 2026年9月22日(火) 9:00
 原文: Monday, September 21, 2026, 7:00 PM (UTC-5) ／ 時差: UTC-5→UTC+9（14時間加算）／ 夏時間: なし（EST扱い。※実際のトロントはこの時期サマータイム中でUTC-4のはずだが、原文表記のUTC-5どおりに換算）

- **[N-08]** 2026年8月12日(水) 10:00
 原文: Tuesday, August 11, 2026, 5:00 PM (UTC-8) ／ 時差: UTC-8→UTC+9（17時間加算）／ 夏時間: あり（AKDT。8月のアラスカは実暦とも整合）

- **[N-09]** 2026年4月8日(水) 1:00
 原文: Tuesday, April 7, 2026, 9:00 AM PT ／ 時差: PDT=UTC-7→UTC+9（16時間加算）／ 夏時間: あり（4/7は米国の夏時間期間中〔2026年は3/8〜11/1〕のためPDTと判断）

- **[N-10]** 2026年6月17日(水) 7:00
 原文: Tuesday, June 16, 2026, 3:00 PM PT ／ 時差: PDT=UTC-7→UTC+9（16時間加算）／ 夏時間: あり（6/16は夏時間期間中のためPDTと判断）

- **[N-11]** 2026年5月13日(水) 0:00
 原文: Tuesday, May 12, 2026, 11:00 AM ET ／ 時差: EDT=UTC-4→UTC+9（13時間加算）／ 夏時間: あり（5/12は夏時間期間中のためEDTと判断）

- **[N-12]** 2026年9月10日(木) 3:00
 原文: Wednesday, September 9, 2026, 2:00 PM ET ／ 時差: EDT=UTC-4→UTC+9（13時間加算）／ 夏時間: あり（9/9は夏時間期間中〔終了は11/1〕のためEDTと判断）

- **[N-13]** 2026年4月8日(水) 2:00
 原文: Tuesday, April 7, 2026, 9:00 AM PST ／ 時差: PST=UTC-8→UTC+9（17時間加算）／ 夏時間: なし（PSTと明記されているためUTC-8で換算。※実際のこの時期は米国太平洋夏時間PDT〔UTC-7〕の期間だが、原文表記どおりに処理）

- **[N-14]** 2026年7月3日(金) 6:00
 原文: Thursday, July 2, 2026, 1:00 PM PST ／ 時差: PST=UTC-8→UTC+9（17時間加算）／ 夏時間: なし（PSTと明記のためUTC-8で換算。※実際は夏時間期間中だが原文表記どおりに処理）

- **[N-15]** 2026年12月3日(木) 23:00
 原文: Thursday, December 3, 2026, 10:00 AM EDT ／ 時差: EDT=UTC-4→UTC+9（13時間加算）／ 夏時間: あり（EDTと明記のためUTC-4で換算。※実際の12月は米国東部標準時EST〔UTC-5〕の期間だが、原文表記どおりに処理）

- **[N-16]** 2026年1月21日(水) 5:00
 原文: Tuesday, January 20, 2026, 4:00 PM EDT ／ 時差: EDT=UTC-4→UTC+9（13時間加算）／ 夏時間: あり（EDTと明記のためUTC-4で換算。※実際の1月はEST期間だが、原文表記どおりに処理）

- **[N-17]** 2026年5月1日(金) 13:00（換算なし・原文のまま）
 原文: Friday, May 1, 2026, 1:00 PM JST ／ 時差: 換算不要（すでに日本時間）／ 夏時間: 該当なし

- **[N-18]** 2026年10月6日(火) 9:30（換算なし・原文のまま）
 原文: Tuesday, October 6, 2026, 9:30 AM JST ／ 時差: 換算不要（すでに日本時間）／ 夏時間: 該当なし

- **[N-19]** 2026年3月26日(木) 2:30
 原文: Wednesday, March 25, 2026, 11:00 PM IST (UTC+5:30) ／ 時差: UTC+5:30→UTC+9（3時間30分加算）／ 夏時間: なし（インドはサマータイム制度なし）

- **[N-20]** 2026年11月13日(金) 0:15
 原文: Thursday, November 12, 2026, 8:45 PM IST (UTC+5:30) ／ 時差: UTC+5:30→UTC+9（3時間30分加算）／ 夏時間: なし（インドはサマータイム制度なし）

- **[N-21]** 2026年4月16日(木) 22:00
 原文: 送信 Thursday, April 9, 2026／本文「next Thursday at 9:00 AM ET」→送信日が木曜のため「次の木曜」は2026年4月16日(木) 9:00 AM ETと特定 ／ 時差: EDT=UTC-4→UTC+9（13時間加算）／ 夏時間: あり（4/16は夏時間期間中のためEDTと判断）

- **[N-22]** 2026年10月23日(金) 0:00
 原文: 送信 Thursday, October 15, 2026／本文「next Thursday at 3:00 PM GMT」→送信日が木曜のため「次の木曜」は2026年10月22日(木) 3:00 PM GMTと特定 ／ 時差: UTC+0→UTC+9（9時間加算）／ 夏時間: なし（GMTと明記のためUTC+0で換算。※実際のダブリンはこの時期夏時間IST/BST〔UTC+1、終了は10/25〕の期間だが、原文表記どおりに処理）

- **[N-23]** 2026年6月2日(火) 17:00
 原文: Tuesday, June 2, 2026, 10:00 AM (UTC+2) ／ 時差: UTC+2→UTC+9（7時間加算）／ 夏時間: あり（ドイツのCEST。6月は実暦とも整合）

- **[N-24]** 2026年9月3日(木) 12:00
 原文: Thursday, September 3, 2026, 11:00 AM (UTC+8) ／ 時差: UTC+8→UTC+9（1時間加算）／ 夏時間: なし（フィリピンはサマータイム制度なし）

---

**補足**
- 〔要確認〕とした案内はありませんでした。すべての案内は「明示された数値オフセット」または「本文中の日付から判定できる夏時間状況」によって一意に換算できました。
- N-01・N-03・N-07・N-13・N-14・N-15・N-16・N-22 は、原文に明記された表記（数値オフセットまたは略称）と、その日時における実際の現地の暦上の夏時間運用とが一致しません（例：PSTと明記されているが実際はPDT期間、など）。これらはいずれも**原文の表記をそのまま採用して換算**しており、実暦への「補正」は行っていません。念のため各行に注記しています。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料B・1回目

```
以下、案内24件を日本時間（JST, UTC+9）に変換した一覧です。日本にサマータイム制度はないため、変換後はすべて「その日付・時刻がそのまま日本時間」になります。

---

## 一覧

**N-01**: 2026年5月18日(月) 21:30 JST
　原文: Tue, May 19, 2026, 12:30 AM (UTC+12) ｜ 使用した時差: UTC+12→JST(UTC+9)、差3時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要（ニュージーランドは5月は非サマータイム期間＝NZST）

**N-02**: 2026年7月6日(月) 23:00 JST
　原文: Tue, July 7, 2026, 1:00 AM (UTC+11) ｜ 使用した時差: UTC+11→JST(UTC+9)、差2時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要（ニューカレドニアはサマータイム制度なし）

**N-03**: 2026年8月2日(日) 23:00 JST
　原文: Mon, August 3, 2026, 2:00 AM (UTC+12) ｜ 使用した時差: UTC+12→JST(UTC+9)、差3時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要

**N-04**: 2026年4月22日(水) 5:00 JST
　原文: Tue, April 21, 2026, 9:00 PM (UTC+1) ｜ 使用した時差: UTC+1→JST(UTC+9)、差8時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要（4月のアイルランドは夏時間期間だが表記の+1をそのまま採用）

**N-05**: 2026年5月27日(水) 8:00 JST
　原文: Tue, May 26, 2026, 11:00 PM (UTC+0) ｜ 使用した時差: UTC+0→JST(UTC+9)、差9時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要（ガーナはサマータイム制度なし）

**N-06**: 2026年10月9日(金) 8:00 JST
　原文: Thu, October 8, 2026, 8:00 PM (UTC-3) ｜ 使用した時差: UTC-3→JST(UTC+9)、差12時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要（アルゼンチンは現在サマータイム制度なし）

**N-07**: 2026年6月25日(木) 9:30 JST
　原文: Wed, June 24, 2026, 6:30 PM (UTC-6) ｜ 使用した時差: UTC-6→JST(UTC+9)、差15時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要（メキシコシティはサマータイム制度なし）

**N-08**: 2026年11月4日(水) 11:00 JST
　原文: Tue, November 3, 2026, 4:00 PM (UTC-10) ｜ 使用した時差: UTC-10→JST(UTC+9)、差19時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要（ハワイはサマータイム制度なし）

**N-09**: 2026年5月12日(火) 1:30 JST
　原文: Mon, May 11, 2026, 9:30 AM PT ｜ 使用した時差: PDT(UTC-7)→JST(UTC+9)、差16時間 ｜ 夏時間: あり（2026年の米国DST期間［3/8～11/1］に該当するためPDTを採用）

**N-10**: 2026年8月19日(水) 8:00 JST
　原文: Tue, August 18, 2026, 4:00 PM PT ｜ 使用した時差: PDT(UTC-7)→JST(UTC+9)、差16時間 ｜ 夏時間: あり（同上、DST期間に該当）

**N-11**: 2026年4月14日(火) 23:00 JST
　原文: Tue, April 14, 2026, 10:00 AM ET ｜ 使用した時差: EDT(UTC-4)→JST(UTC+9)、差13時間 ｜ 夏時間: あり（DST期間に該当するためEDTを採用）

**N-12**: 2026年10月21日(水) 2:00 JST
　原文: Tue, October 20, 2026, 1:00 PM ET ｜ 使用した時差: EDT(UTC-4)→JST(UTC+9)、差13時間 ｜ 夏時間: あり（10/20はDST終了[11/1]前のため、まだEDT）

**N-13**: 2026年5月12日(火) 2:30 JST
　原文: Mon, May 11, 2026, 9:30 AM PST ｜ 使用した時差: PST(UTC-8)→JST(UTC+9)、差17時間 ｜ 夏時間: なし（表記が明示的にPST＝標準時のため。実際の5月の米国太平洋岸はPDT期間だが原文表記のまま採用）

**N-14**: 2026年9月16日(水) 7:00 JST
　原文: Tue, September 15, 2026, 2:00 PM PST ｜ 使用した時差: PST(UTC-8)→JST(UTC+9)、差17時間 ｜ 夏時間: なし（表記どおりPST。実際の9月はPDT期間だが原文表記のまま採用）

**N-15**: 2026年1月9日(金) 0:00 JST
　原文: Thu, January 8, 2026, 11:00 AM EDT ｜ 使用した時差: EDT(UTC-4)→JST(UTC+9)、差13時間 ｜ 夏時間: あり（表記どおりEDT。実際の1月はEST期間だが原文表記のまま採用）

**N-16**: 2026年12月18日(金) 4:00 JST
　原文: Thu, December 17, 2026, 3:00 PM EDT ｜ 使用した時差: EDT(UTC-4)→JST(UTC+9)、差13時間 ｜ 夏時間: あり（表記どおりEDT。実際の12月はEST期間だが原文表記のまま採用）

**N-17**: 2026年6月15日(月) 14:00 JST（変換なし・原文のまま）
　原文: Mon, June 15, 2026, 2:00 PM JST ｜ 使用した時差: なし（すでにJST） ｜ 夏時間: 該当なし（日本にサマータイム制度なし）

**N-18**: 2026年11月2日(月) 9:00 JST（変換なし・原文のまま）
　原文: Mon, November 2, 2026, 9:00 AM JST ｜ 使用した時差: なし（すでにJST） ｜ 夏時間: 該当なし（日本にサマータイム制度なし）

**N-19**: 2026年4月30日(木) 2:00 JST
　原文: Wed, April 29, 2026, 10:30 PM IST (UTC+5:30) ｜ 使用した時差: UTC+5:30→JST(UTC+9)、差3時間30分 ｜ 夏時間: インドはサマータイム制度なし

**N-20**: 2026年12月10日(木) 0:45 JST
　原文: Wed, December 9, 2026, 9:15 PM IST (UTC+5:30) ｜ 使用した時差: UTC+5:30→JST(UTC+9)、差3時間30分 ｜ 夏時間: インドはサマータイム制度なし

**N-21**: 2026年5月14日(木) 23:00 JST
　原文: 送信日 Thu, May 7, 2026／本文「next Thursday at 10:00 AM ET」 ｜ 解釈: 送信日(木)から見た「来週木曜日」＝5月14日と解釈 ｜ 使用した時差: EDT(UTC-4)→JST(UTC+9)、差13時間 ｜ 夏時間: あり（5月はDST期間のためEDTを採用）

**N-22**: 2026年9月17日(木) 23:00 JST
　原文: 送信日 Thu, September 10, 2026／本文「next Thursday at 2:00 PM GMT」 ｜ 解釈: 送信日(木)から見た「来週木曜日」＝9月17日と解釈 ｜ 使用した時差: GMT(UTC+0)→JST(UTC+9)、差9時間 ｜ 夏時間: なし（表記が明示的にGMT。実際の9月の英国はBST[UTC+1]期間だが原文表記のまま採用）

**N-23**: 2026年7月6日(月) 16:00 JST
　原文: Mon, July 6, 2026, 9:00 AM (UTC+2)（本文「today's item」＝送信日当日） ｜ 使用した時差: UTC+2→JST(UTC+9)、差7時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要

**N-24**: 2026年10月12日(月) 12:00 JST
　原文: Mon, October 12, 2026, 10:00 AM (UTC+7)（本文「today's item」＝送信日当日） ｜ 使用した時差: UTC+7→JST(UTC+9)、差2時間 ｜ 夏時間: 数値オフセット表記のため個別判定不要

---

### 補足（換算方針のまとめ）
- **数値のUTCオフセット表記（例：UTC+12、UTC+1など）**は、その数値自体に現地の夏時間調整が反映済みとみなし、そのまま採用しました。
- **PST/PDT・EST/EDT・GMTのように夏時間・標準時が明示された略語**は、実際のその日付における現地慣行と食い違う場合（例：5月なのにPST表記、1月なのにEDT表記、9月なのにGMT表記）でも、原文の表記をそのまま信頼して換算しました（送信者側の誤記の可能性はありますが、本文からは訂正の判断材料がないため）。
- **PT・ETのように夏時間/標準時の区別がない略語**は、2026年の米国DST実施期間（3月8日～11月1日）に基づき、日付から機械的にPDT/EDTまたはPST/ESTを判定しました。
- 〔要確認〕とすべき項目（夏時間の有無が原文からもルールからも決定できないもの）は今回はありませんでした。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料B・2回目

```
以下、全24件をJST（UTC+9、夏時間なし）に統一して一覧にしました。各行の形式は「ID: 日本時間の日付・時刻」＋「原文表記／使用した時差／夏時間の有無（または要確認の理由）」です。

- **[N-01]** 2026年5月18日(月) 21:30 JST（原文: 2026年5月19日(火) 0:30 (UTC+12)／使用した時差: UTC+12／夏時間: なし〔南半球の冬で標準時(NZST)〕）
- **[N-02]** 2026年7月6日(月) 23:00 JST（原文: 2026年7月7日(火) 1:00 (UTC+11)／使用した時差: UTC+11／夏時間: なし〔ニューカレドニアに夏時間制度なし〕）
- **[N-03]** 2026年8月2日(日) 23:00 JST（原文: 2026年8月3日(月) 2:00 (UTC+12)／使用した時差: UTC+12／夏時間: なし〔南半球の冬で標準時〕）
- **[N-04]** 2026年4月22日(水) 5:00 JST（原文: 2026年4月21日(火) 21:00 (UTC+1)／使用した時差: UTC+1／夏時間: あり〔アイルランド夏時間(IST)適用期間中〕）
- **[N-05]** 2026年5月27日(水) 8:00 JST（原文: 2026年5月26日(火) 23:00 (UTC+0)／使用した時差: UTC+0／夏時間: なし〔ガーナに夏時間制度なし〕）
- **[N-06]** 2026年10月9日(金) 8:00 JST（原文: 2026年10月8日(木) 20:00 (UTC-3)／使用した時差: UTC-3／夏時間: なし〔アルゼンチンは2009年以降廃止〕）
- **[N-07]** 2026年6月25日(木) 9:30 JST（原文: 2026年6月24日(水) 18:30 (UTC-6)／使用した時差: UTC-6／夏時間: なし〔メキシコシティは2022年改正以降、通年UTC-6〕）
- **[N-08]** 2026年11月4日(水) 11:00 JST（原文: 2026年11月3日(火) 16:00 (UTC-10)／使用した時差: UTC-10／夏時間: なし〔ハワイに夏時間制度なし〕）
- **[N-09]** 2026年5月12日(火) 1:30 JST（原文: 2026年5月11日(月) 9:30 (PT)／使用した時差: UTC-7(PDT)／夏時間: あり〔5月11日は米国夏時間期間中のためPT=PDTと判断〕）
- **[N-10]** 2026年8月19日(水) 8:00 JST（原文: 2026年8月18日(火) 16:00 (PT)／使用した時差: UTC-7(PDT)／夏時間: あり〔8月18日は米国夏時間期間中のためPT=PDTと判断〕）
- **[N-11]** 2026年4月14日(火) 23:00 JST（原文: 2026年4月14日(火) 10:00 (ET)／使用した時差: UTC-4(EDT)／夏時間: あり〔4月14日は米国夏時間期間中のためET=EDTと判断〕）
- **[N-12]** 2026年10月21日(水) 2:00 JST（原文: 2026年10月20日(火) 13:00 (ET)／使用した時差: UTC-4(EDT)／夏時間: あり〔10月20日は米国夏時間期間中(終了は11/1)のためET=EDTと判断〕）
- **[N-13]** 〔要確認〕（原文: 2026年5月11日(月) 9:30 (PST)／理由: 5月11日は米国夏時間期間中でPDT(UTC-7)のはずが表記はPST(UTC-8)で矛盾しており確定不可）
- **[N-14]** 〔要確認〕（原文: 2026年9月15日(火) 14:00 (PST)／理由: 9月15日は米国夏時間期間中でPDT(UTC-7)のはずが表記はPST(UTC-8)で矛盾しており確定不可）
- **[N-15]** 〔要確認〕（原文: 2026年1月8日(木) 11:00 (EDT)／理由: 1月8日は米国夏時間期間外でEST(UTC-5)のはずが表記はEDT(UTC-4)で矛盾しており確定不可）
- **[N-16]** 〔要確認〕（原文: 2026年12月17日(木) 15:00 (EDT)／理由: 12月17日は米国夏時間期間外でEST(UTC-5)のはずが表記はEDT(UTC-4)で矛盾しており確定不可）
- **[N-17]** 2026年6月15日(月) 14:00 JST（原文: 2026年6月15日(月) 14:00 (JST)／既に日本時間のため換算不要）
- **[N-18]** 2026年11月2日(月) 9:00 JST（原文: 2026年11月2日(月) 9:00 (JST)／既に日本時間のため換算不要）
- **[N-19]** 2026年4月30日(木) 2:00 JST（原文: 2026年4月29日(水) 22:30 (IST, UTC+5:30)／使用した時差: UTC+5:30／夏時間: なし〔インドに夏時間制度なし〕）
- **[N-20]** 2026年12月10日(木) 0:45 JST（原文: 2026年12月9日(水) 21:15 (IST, UTC+5:30)／使用した時差: UTC+5:30／夏時間: なし〔インドに夏時間制度なし〕）
- **[N-21]** 2026年5月14日(木) 23:00 JST（原文: 送信2026年5月7日(木)、本文「next Thursday 10:00 AM ET」→翌週木曜5月14日と解釈／使用した時差: UTC-4(EDT)／夏時間: あり〔5月14日は米国夏時間期間中〕）
- **[N-22]** 〔要確認〕（原文: 送信2026年9月10日(木)、本文「next Thursday 2:00 PM GMT」→翌週木曜9月17日と解釈／理由: 9月17日は英国夏時間(BST, UTC+1)期間中でGMT(UTC+0)にはならないはずで矛盾しており確定不可）
- **[N-23]** 2026年7月6日(月) 16:00 JST（原文: 2026年7月6日(月) 9:00 (UTC+2)／使用した時差: UTC+2／夏時間: あり〔ポーランド夏時間(CEST)期間中〕）
- **[N-24]** 2026年10月12日(月) 12:00 JST（原文: 2026年10月12日(月) 10:00 (UTC+7)／使用した時差: UTC+7／夏時間: なし〔インドネシアに夏時間制度なし〕）

**補足（要確認とした理由の要点）**
- N-13, N-14, N-15, N-16は、"PST"/"EDT"という具体的な標準時・夏時間の略称が明記されているにもかかわらず、実際の日付上の米国夏時間の適用期間（毎年3月第2日曜〜11月第1日曜）と食い違っています（例: 5月なのにPST〔標準時〕、1月なのにEDT〔夏時間〕）。表記のミスなのか、UTC-8/UTC-4を意図的に指しているのか判断できないため換算していません。
- N-22も同様に、日付から算出した「翌週木曜（9月17日）」は英国夏時間(BST)期間中にあたるため、本文中の「GMT」表記と矛盾しており確定できません。
```

**照合（機械）**

```
found=24/24 correct=19/24
unsure_flags=['N-13', 'N-14', 'N-15', 'N-16', 'N-22']
unsure_false_positive=['N-13', 'N-14', 'N-15', 'N-16', 'N-22']
selfreport_offset_mismatch=[('N-13', -7.0, -8.0), ('N-14', -7.0, -8.0), ('N-15', -5.0, -4.0), ('N-16', -5.0, -4.0), ('N-22', 1.0, 0.0)]
wrong_detail=N-13(真値2026-05-12 02:30); N-14(真値2026-09-16 07:00); N-15(真値2026-01-09 00:00); N-16(真値2026-12-18 04:00); N-22(真値2026-09-17 23:00)
```

### 判定

**採用（ただし不安定さを本文に明記）**。材料2本×各2回のうち3回は24件全部正解。B材料2回目のみ、標準時・夏時間まで略号で明記した4件（N-13,14,15,16）と、相対表現1件（N-22）を誤って〔要確認〕にした（真値はどれも算出可能）。同じ指示文・同じ材料の別の回では5件とも問題なく換算できている。

---

## 指示文4（記事4節・仕上げに二重変換を自己点検）

### 送った指示文（記事と同一文字列）

```
次の案内をすべて日本時間に直して、一覧にしてください。

日付・時刻を、日本の読者がそのまま読める形にしてください。

書き換えたものは、原文の表記をカッコの中に残してください。

時差の換算をしたときは、換算前の時刻と、使った時差（協定世界時からの差）も書いてください。夏時間の有無も書いてください。

1件につき1行、「ID: 日本時間の日付と時刻」の形式で先に一覧を書いてください。行の後ろに、原文の表記・使った時差・夏時間の有無を続けて書いてください。

最後に、原文にすでに日本時間（JST）と書かれていたものを、誤って換算していないか確かめて、該当する番号を1行で書いてください。
```

### 材料A・1回目

```
# 日本時間換算 一覧

| ID | 日本時間（換算後） |
|---|---|
| N-01 | 2026年4月12日(日) 21:00 |
| N-02 | 2026年5月4日(月) 23:30 |
| N-03 | 2026年6月8日(月) 23:30 |
| N-04 | 2026年3月18日(水) 5:00 |
| N-05 | 2026年4月3日(金) 6:00 |
| N-06 | 2026年7月15日(水) 9:30 |
| N-07 | 2026年9月22日(火) 9:00 |
| N-08 | 2026年8月12日(水) 10:00 |
| N-09 | 2026年4月8日(水) 1:00 |
| N-10 | 2026年6月17日(水) 7:00 |
| N-11 | 2026年5月13日(水) 0:00 |
| N-12 | 2026年9月10日(木) 3:00 |
| N-13 | 2026年4月8日(水) 2:00 |
| N-14 | 2026年7月3日(金) 6:00 |
| N-15 | 2026年12月3日(木) 23:00 |
| N-16 | 2026年1月21日(水) 5:00 |
| N-17 | 2026年5月1日(金) 13:00 |
| N-18 | 2026年10月6日(火) 9:30 |
| N-19 | 2026年3月26日(木) 2:30 |
| N-20 | 2026年11月13日(金) 0:15 |
| N-21 | 2026年4月16日(木) 22:00 |
| N-22 | 2026年10月23日(金) 0:00 |
| N-23 | 2026年6月2日(火) 17:00 |
| N-24 | 2026年9月3日(木) 12:00 |

---

## 詳細（原文表記／換算前時刻／使った時差／夏時間の有無）

- **N-01**: 原文「2026年4月13日(月) 1:00 AM (UTC+13)」／換算前: 1:00 AM／時差: UTC+13／夏時間: あり（NZDT扱い。※実際の暦ではNZの夏時間は4月上旬に終了するため矛盾する可能性あり、原文表記をそのまま採用）
- **N-02**: 原文「2026年5月5日(火) 2:30 AM (UTC+12)」／換算前: 2:30 AM／時差: UTC+12／夏時間: なし（フィジー標準時）
- **N-03**: 原文「2026年6月9日(火) 1:30 AM (UTC+11)」／換算前: 1:30 AM／時差: UTC+11／夏時間: あり（AEDT扱い。※実際は6月は豪州の冬でAEST(UTC+10)期間のため矛盾。原文表記をそのまま採用）
- **N-04**: 原文「2026年3月17日(火) 8:00 PM (UTC+0)」／換算前: 8:00 PM／時差: UTC+0／夏時間: なし（GMT）
- **N-05**: 原文「2026年4月2日(木) 10:00 PM (UTC+1)」／換算前: 10:00 PM／時差: UTC+1／夏時間: なし（ナイジェリアは通年UTC+1）
- **N-06**: 原文「2026年7月14日(火) 9:30 PM (UTC-3)」／換算前: 9:30 PM／時差: UTC-3／夏時間: なし（ブラジルは2019年以降夏時間廃止）
- **N-07**: 原文「2026年9月21日(月) 7:00 PM (UTC-5)」／換算前: 7:00 PM／時差: UTC-5／夏時間: なし（EST表記。※実際の9月はEDT(UTC-4)期間のため矛盾。原文表記をそのまま採用）
- **N-08**: 原文「2026年8月11日(火) 5:00 PM (UTC-8)」／換算前: 5:00 PM／時差: UTC-8／夏時間: あり（AKDT、実季節とも整合）
- **N-09**: 原文「2026年4月7日(火) 9:00 AM PT」／換算前: 9:00 AM／時差: UTC-7（PDT）／夏時間: あり
- **N-10**: 原文「2026年6月16日(火) 3:00 PM PT」／換算前: 3:00 PM／時差: UTC-7（PDT）／夏時間: あり
- **N-11**: 原文「2026年5月12日(火) 11:00 AM ET」／換算前: 11:00 AM／時差: UTC-4（EDT）／夏時間: あり
- **N-12**: 原文「2026年9月9日(水) 2:00 PM ET」／換算前: 2:00 PM／時差: UTC-4（EDT）／夏時間: あり
- **N-13**: 原文「2026年4月7日(火) 9:00 AM PST」／換算前: 9:00 AM／時差: UTC-8（PST表記）／夏時間: なし（※実際の4月はPDT期間のため矛盾。原文表記のPSTをそのまま採用）
- **N-14**: 原文「2026年7月2日(木) 1:00 PM PST」／換算前: 1:00 PM／時差: UTC-8（PST表記）／夏時間: なし（※実際の7月はPDT期間のため矛盾。原文表記をそのまま採用）
- **N-15**: 原文「2026年12月3日(木) 10:00 AM EDT」／換算前: 10:00 AM／時差: UTC-4（EDT表記）／夏時間: あり（※実際の12月はEST期間のため矛盾。原文表記をそのまま採用）
- **N-16**: 原文「2026年1月20日(火) 4:00 PM EDT」／換算前: 4:00 PM／時差: UTC-4（EDT表記）／夏時間: あり（※実際の1月はEST期間のため矛盾。原文表記をそのまま採用）
- **N-17**: 原文「2026年5月1日(金) 1:00 PM JST」／換算なし（すでに日本時間）
- **N-18**: 原文「2026年10月6日(火) 9:30 AM JST」／換算なし（すでに日本時間）
- **N-19**: 原文「2026年3月25日(水) 11:00 PM IST (UTC+5:30)」／換算前: 11:00 PM／時差: UTC+5:30／夏時間: なし（インドは夏時間なし）
- **N-20**: 原文「2026年11月12日(木) 8:45 PM IST (UTC+5:30)」／換算前: 8:45 PM／時差: UTC+5:30／夏時間: なし
- **N-21**: 原文「送信: 2026年4月9日(木)」「next Thursday 9:00 AM ET」→ 会議日を2026年4月16日(木)と特定／換算前: 9:00 AM／時差: UTC-4（EDT）／夏時間: あり
- **N-22**: 原文「送信: 2026年10月15日(木)」「next Thursday 3:00 PM GMT」→ 会議日を2026年10月22日(木)と特定／換算前: 3:00 PM／時差: UTC+0（GMT表記）／夏時間: なし（※10月22日時点のアイルランドは実際にはBST(UTC+1)期間の可能性があるが、原文の「GMT」表記をそのまま採用）
- **N-23**: 原文「2026年6月2日(火) 10:00 AM (UTC+2)」／換算前: 10:00 AM／時差: UTC+2／夏時間: あり（CEST、実季節とも整合）
- **N-24**: 原文「2026年9月3日(木) 11:00 AM (UTC+8)」／換算前: 11:00 AM／時差: UTC+8／夏時間: なし（フィリピンは夏時間なし）

---

## 確認結果（誤って再換算していないか）

すでに日本時間（JST）と明記されていた項目は **N-17、N-18** で、いずれも換算せず原文の時刻をそのまま採用しています。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 材料B・1回目

```
以下、すべて日本時間（JST, UTC+9）に統一した一覧です。

- N-01: 2026年5月18日(月) 21:30 JST／原文: 2026年5月19日(火) 0:30 (UTC+12)／使用時差: UTC+12／夏時間: なし（NZは5月は非サマータイム期間）
- N-02: 2026年7月6日(月) 23:00 JST／原文: 2026年7月7日(火) 1:00 (UTC+11)／使用時差: UTC+11／夏時間: なし（ニューカレドニアはサマータイム制度なし）
- N-03: 2026年8月2日(日) 23:00 JST／原文: 2026年8月3日(月) 2:00 (UTC+12)／使用時差: UTC+12／夏時間: なし（フィジーは8月は非サマータイム期間）
- N-04: 2026年4月22日(水) 5:00 JST／原文: 2026年4月21日(火) 21:00 (UTC+1)／使用時差: UTC+1／夏時間: あり（アイルランドは4月は夏時間=IST適用中）
- N-05: 2026年5月27日(水) 8:00 JST／原文: 2026年5月26日(火) 23:00 (UTC+0)／使用時差: UTC+0／夏時間: なし（ガーナはサマータイム制度なし）
- N-06: 2026年10月9日(金) 8:00 JST／原文: 2026年10月8日(木) 20:00 (UTC-3)／使用時差: UTC-3／夏時間: なし（アルゼンチンはサマータイム制度なし）
- N-07: 2026年6月25日(木) 9:30 JST／原文: 2026年6月24日(水) 18:30 (UTC-6)／使用時差: UTC-6／夏時間: なし（メキシコシティは2022年に夏時間廃止）
- N-08: 2026年11月4日(水) 11:00 JST／原文: 2026年11月3日(火) 16:00 (UTC-10)／使用時差: UTC-10／夏時間: なし（ハワイはサマータイム制度なし）
- N-09: 2026年5月12日(火) 1:30 JST／原文: 2026年5月11日(月) 9:30 AM PT／使用時差: UTC-7（PDT、5月は米国夏時間期間中）／夏時間: あり
- N-10: 2026年8月19日(水) 8:00 JST／原文: 2026年8月18日(火) 16:00 PT／使用時差: UTC-7（PDT）／夏時間: あり
- N-11: 2026年4月14日(火) 23:00 JST／原文: 2026年4月14日(火) 10:00 ET／使用時差: UTC-4（EDT、4月は米国夏時間期間中）／夏時間: あり
- N-12: 2026年10月21日(水) 2:00 JST／原文: 2026年10月20日(火) 13:00 ET／使用時差: UTC-4（EDT、10月20日時点はまだ夏時間期間中）／夏時間: あり
- N-13: 2026年5月12日(火) 2:30 JST／原文: 2026年5月11日(月) 9:30 AM PST／使用時差: UTC-8（原文の"PST"表記どおりに換算。※実際の5月の米太平洋岸は夏時間中でPDT＝UTC-7が実運用のため表記と実態が食い違っています）／夏時間: なし（表記上）
- N-14: 2026年9月16日(水) 7:00 JST／原文: 2026年9月15日(火) 14:00 PST／使用時差: UTC-8（原文表記どおり。※実際の9月も米太平洋岸は夏時間中でPDT＝UTC-7が実運用）／夏時間: なし（表記上）
- N-15: 2026年1月9日(金) 0:00 JST／原文: 2026年1月8日(木) 11:00 EDT／使用時差: UTC-4（原文表記どおり。※実際の1月の米東部は標準時でEST＝UTC-5が実運用）／夏時間: あり（表記上）
- N-16: 2026年12月18日(金) 4:00 JST／原文: 2026年12月17日(木) 15:00 EDT／使用時差: UTC-4（原文表記どおり。※実際の12月の米東部は標準時でEST＝UTC-5が実運用）／夏時間: あり（表記上）
- N-17: 2026年6月15日(月) 14:00 JST／原文: 2026年6月15日(月) 14:00 JST（換算なし、原文が既に日本時間）
- N-18: 2026年11月2日(月) 9:00 JST／原文: 2026年11月2日(月) 9:00 JST（換算なし、原文が既に日本時間）
- N-19: 2026年4月30日(木) 2:00 JST／原文: 2026年4月29日(水) 22:30 IST (UTC+5:30)／使用時差: UTC+5:30／夏時間: なし（インドはサマータイム制度なし）
- N-20: 2026年12月10日(木) 0:45 JST／原文: 2026年12月9日(水) 21:15 IST (UTC+5:30)／使用時差: UTC+5:30／夏時間: なし（インドはサマータイム制度なし）
- N-21: 2026年5月14日(木) 23:00 JST／原文: 送信日2026年5月7日(木)、本文「来週木曜 10:00 AM ET」→対象日は2026年5月14日(木)／使用時差: UTC-4（EDT、5月は米国夏時間期間中）／夏時間: あり
- N-22: 2026年9月17日(木) 23:00 JST／原文: 送信日2026年9月10日(木)、本文「来週木曜 2:00 PM GMT」→対象日は2026年9月17日(木)／使用時差: UTC+0（原文の"GMT"表記どおりに換算。※実際の9月の英国は夏時間中でBST＝UTC+1が実運用のため表記と実態が食い違っています）／夏時間: なし（表記上）
- N-23: 2026年7月6日(月) 16:00 JST／原文: 2026年7月6日(月) 9:00 (UTC+2)／使用時差: UTC+2／夏時間: あり（ポーランドは7月は夏時間=CEST適用中）
- N-24: 2026年10月12日(月) 12:00 JST／原文: 2026年10月12日(月) 10:00 (UTC+7)／使用時差: UTC+7／夏時間: なし（インドネシアはサマータイム制度なし）

【原文がすでにJSTだった項目の確認】
N-17とN-18は原文が最初から日本時間（JST）表記であり、これらについては時差換算を一切行わず、原文の日時をそのまま採用しています（誤って再換算していないことを確認済みです）。
```

**照合（機械）**

```
found=24/24 correct=24/24
```

### 判定

**採用**。材料2本×各1回＝のべ48件とも真値と完全一致し、自己点検の申告も2回とも正しくN-17・N-18を名指しした（二重変換はもとより0件）。

---

## 指示文5（言い直し方1つ目・先回りして直す）

### 送った指示文（記事と同一文字列）

```
次の案内をすべて日本時間に直して、一覧にしてください。

日付・時刻を、日本の読者がそのまま読める形にしてください。

書き換えたものは、原文の表記をカッコの中に残してください。

時差の換算をしたときは、換算前の時刻と、使った時差（協定世界時からの差）も書いてください。夏時間の有無も書いてください。

夏時間かどうかが決められないものは換算せず、〔要確認〕と書いてください。ただし、PST・EDTのように標準時か夏時間かまで略号で明記されている場合は、実際の暦と食い違って見えても、その略号のとおりに換算してください。〔要確認〕にするのは、PT・ETのように標準時か夏時間かが略号に書かれていない場合だけです。

1件につき1行、「ID: 日本時間の日付と時刻」の形式で先に一覧を書いてください。行の後ろに、原文の表記・使った時差・夏時間の有無を続けて書いてください。〔要確認〕にした場合はその旨を書いてください。
```

### 材料A・1回目

```
# 日本時間換算 一覧

| ID | 日本時間 |
|---|---|
| N-01 | 2026年4月12日(日) 21:00 |
| N-02 | 2026年5月4日(月) 23:30 |
| N-03 | 2026年6月8日(月) 23:30 |
| N-04 | 2026年3月18日(水) 05:00 |
| N-05 | 2026年4月3日(金) 06:00 |
| N-06 | 2026年7月15日(水) 09:30 |
| N-07 | 2026年9月22日(火) 09:00 |
| N-08 | 2026年8月12日(水) 10:00 |
| N-09 | 〔要確認〕 |
| N-10 | 〔要確認〕 |
| N-11 | 〔要確認〕 |
| N-12 | 〔要確認〕 |
| N-13 | 2026年4月8日(水) 02:00 |
| N-14 | 2026年7月3日(金) 06:00 |
| N-15 | 2026年12月3日(木) 23:00 |
| N-16 | 2026年1月21日(水) 05:00 |
| N-17 | 2026年5月1日(金) 13:00 |
| N-18 | 2026年10月6日(火) 09:30 |
| N-19 | 2026年3月26日(木) 02:30 |
| N-20 | 2026年11月13日(金) 00:15 |
| N-21 | 〔要確認〕 |
| N-22 | 2026年10月23日(金) 00:00 |
| N-23 | 2026年6月2日(火) 17:00 |
| N-24 | 2026年9月3日(木) 12:00 |

---

## 詳細

**N-01**
- 原文: Monday, April 13, 2026, 1:00 AM (UTC+13)
- 時差: UTC+13 → JST(UTC+9)＝4時間差（JSTが4時間遅い）
- 夏時間: UTC+13はニュージーランド夏時間（NZDT）に相当する値。原文に数値オフセットが明記されているためそのまま採用。

**N-02**
- 原文: Tuesday, May 5, 2026, 2:30 AM (UTC+12)
- 時差: UTC+12 → JST(UTC+9)＝3時間差（JSTが3時間遅い）
- 夏時間: フィジーは5月は標準時（UTC+12）期間で夏時間なし。

**N-03**
- 原文: Tuesday, June 9, 2026, 1:30 AM (UTC+11)
- 時差: UTC+11 → JST(UTC+9)＝2時間差（JSTが2時間遅い）
- 夏時間: シドニーの6月は本来標準時（AEST、UTC+10）の時期だが、原文にUTC+11の数値オフセットが明記されているためそのまま採用。

**N-04**
- 原文: Tuesday, March 17, 2026, 8:00 PM (UTC+0)
- 時差: UTC+0 → JST(UTC+9)＝9時間差（JSTが9時間進み）
- 夏時間: ロンドンの3月17日は夏時間（BST）開始前で標準時と整合。夏時間なし。

**N-05**
- 原文: Thursday, April 2, 2026, 10:00 PM (UTC+1)
- 時差: UTC+1 → JST(UTC+9)＝8時間差（JSTが8時間進み）
- 夏時間: ラゴス（西アフリカ時間）は通年UTC+1で夏時間制度なし。

**N-06**
- 原文: Tuesday, July 14, 2026, 9:30 PM (UTC-3)
- 時差: UTC-3 → JST(UTC+9)＝12時間差（JSTが12時間進み）
- 夏時間: ブラジルは2019年以降サマータイム廃止、UTC-3は通年標準時。夏時間なし。

**N-07**
- 原文: Monday, September 21, 2026, 7:00 PM (UTC-5)
- 時差: UTC-5 → JST(UTC+9)＝14時間差（JSTが14時間進み）
- 夏時間: トロントの9月は本来夏時間（EDT、UTC-4）の時期だが、原文にUTC-5の数値オフセットが明記されているためそのまま採用。

**N-08**
- 原文: Tuesday, August 11, 2026, 5:00 PM (UTC-8)
- 時差: UTC-8 → JST(UTC+9)＝17時間差（JSTが17時間進み）
- 夏時間: アンカレッジの8月は夏時間（AKDT、UTC-8）期間で整合。

**N-09**
- 原文: Tuesday, April 7, 2026, 9:00 AM PT
- 略号「PT」は標準時（PST）か夏時間（PDT）かが明記されていないため換算不可。〔要確認〕

**N-10**
- 原文: Tuesday, June 16, 2026, 3:00 PM PT
- 略号「PT」は標準時か夏時間かが明記されていないため換算不可。〔要確認〕

**N-11**
- 原文: Tuesday, May 12, 2026, 11:00 AM ET
- 略号「ET」は標準時か夏時間かが明記されていないため換算不可。〔要確認〕

**N-12**
- 原文: Wednesday, September 9, 2026, 2:00 PM ET
- 略号「ET」は標準時か夏時間かが明記されていないため換算不可。〔要確認〕

**N-13**
- 原文: Tuesday, April 7, 2026, 9:00 AM PST
- 時差: PST(UTC-8) → JST(UTC+9)＝17時間差（JSTが17時間進み）
- 夏時間: 略号「PST」は標準時であることが明記されているため、実際の4月が夏時間（PDT）期間であっても指示どおり標準時として換算。

**N-14**
- 原文: Thursday, July 2, 2026, 1:00 PM PST
- 時差: PST(UTC-8) → JST(UTC+9)＝17時間差（JSTが17時間進み）
- 夏時間: 略号「PST」は標準時明記のため、実際の7月が夏時間期間であっても指示どおり標準時として換算。

**N-15**
- 原文: Thursday, December 3, 2026, 10:00 AM EDT
- 時差: EDT(UTC-4) → JST(UTC+9)＝13時間差（JSTが13時間進み）
- 夏時間: 略号「EDT」は夏時間であることが明記されているため、実際の12月が標準時（EST）期間であっても指示どおり夏時間として換算。

**N-16**
- 原文: Tuesday, January 20, 2026, 4:00 PM EDT
- 時差: EDT(UTC-4) → JST(UTC+9)＝13時間差（JSTが13時間進み）
- 夏時間: 略号「EDT」は夏時間明記のため、実際の1月が標準時期間であっても指示どおり夏時間として換算。

**N-17**
- 原文: Friday, May 1, 2026, 1:00 PM JST（換算不要、原文どおり）
- 時差: なし（すでに日本時間）
- 夏時間: 該当なし。

**N-18**
- 原文: Tuesday, October 6, 2026, 9:30 AM JST（換算不要、原文どおり）
- 時差: なし（すでに日本時間）
- 夏時間: 該当なし。

**N-19**
- 原文: Wednesday, March 25, 2026, 11:00 PM IST (UTC+5:30)
- 時差: IST(UTC+5:30) → JST(UTC+9)＝3時間30分差（JSTが3時間30分進み）
- 夏時間: インドはサマータイム制度なし。

**N-20**
- 原文: Thursday, November 12, 2026, 8:45 PM IST (UTC+5:30)
- 時差: IST(UTC+5:30) → JST(UTC+9)＝3時間30分差（JSTが3時間30分進み）
- 夏時間: インドはサマータイム制度なし。

**N-21**
- 原文: Sent Thursday, April 9, 2026／本文「next Thursday at 9:00 AM ET」（＝2026年4月16日 9:00 AM ET）
- 略号「ET」は標準時か夏時間かが明記されていないため換算不可。〔要確認〕

**N-22**
- 原文: Sent Thursday, October 15, 2026／本文「next Thursday at 3:00 PM GMT」（＝2026年10月22日 3:00 PM GMT）
- 時差: GMT(UTC+0) → JST(UTC+9)＝9時間差（JSTが9時間進み）
- 夏時間: 略号「GMT」は標準時であることが明記されているため、実際の10月22日が英国の夏時間（BST）期間中であっても指示どおり標準時として換算。

**N-23**
- 原文: Tuesday, June 2, 2026, 10:00 AM (UTC+2)
- 時差: UTC+2 → JST(UTC+9)＝7時間差（JSTが7時間進み）
- 夏時間: ベルリンの6月は夏時間（CEST、UTC+2）期間で整合。

**N-24**
- 原文: Thursday, September 3, 2026, 11:00 AM (UTC+8)
- 時差: UTC+8 → JST(UTC+9)＝1時間差（JSTが1時間進み）
- 夏時間: フィリピンはサマータイム制度なし。
```

**照合（機械）**

```
found=24/24 correct=19/24
unsure_flags=['N-09', 'N-10', 'N-11', 'N-12', 'N-21']
unsure_false_positive=['N-21']
wrong_detail=N-09(真値2026-04-08 01:00); N-10(真値2026-06-17 07:00); N-11(真値2026-05-13 00:00); N-12(真値2026-09-10 03:00); N-21(真値2026-04-16 22:00)
```

### 材料B・1回目

```
以下、すべて日本時間（JST, UTC+9）に変換した一覧です。1件につき1行、「ID: 日本時間」→原文表記→使った時差→夏時間の有無、の順で記載しています。

- **N-01**: 2026年5月18日(月) 21:30 JST ｜原文: Tuesday, May 19, 2026, 12:30 AM (UTC+12) ｜時差: UTC+12（JSTへ −3時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-02**: 2026年7月6日(月) 23:00 JST ｜原文: Tuesday, July 7, 2026, 1:00 AM (UTC+11) ｜時差: UTC+11（JSTへ −2時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-03**: 2026年8月2日(日) 23:00 JST ｜原文: Monday, August 3, 2026, 2:00 AM (UTC+12) ｜時差: UTC+12（JSTへ −3時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-04**: 2026年4月22日(水) 5:00 JST ｜原文: Tuesday, April 21, 2026, 9:00 PM (UTC+1) ｜時差: UTC+1（JSTへ +8時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-05**: 2026年5月27日(水) 8:00 JST ｜原文: Tuesday, May 26, 2026, 11:00 PM (UTC+0) ｜時差: UTC+0（JSTへ +9時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-06**: 2026年10月9日(金) 8:00 JST ｜原文: Thursday, October 8, 2026, 8:00 PM (UTC-3) ｜時差: UTC−3（JSTへ +12時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-07**: 2026年6月25日(木) 9:30 JST ｜原文: Wednesday, June 24, 2026, 6:30 PM (UTC-6) ｜時差: UTC−6（JSTへ +15時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-08**: 2026年11月4日(水) 11:00 JST ｜原文: Tuesday, November 3, 2026, 4:00 PM (UTC-10) ｜時差: UTC−10（JSTへ +19時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-09**: 〔要確認〕（換算不可）｜原文: Monday, May 11, 2026, 9:30 AM PT ｜理由: PTは標準時(PST)か夏時間(PDT)かが略号に明記されていないため
- **N-10**: 〔要確認〕（換算不可）｜原文: Tuesday, August 18, 2026, 4:00 PM PT ｜理由: PTは標準時(PST)か夏時間(PDT)かが略号に明記されていないため
- **N-11**: 〔要確認〕（換算不可）｜原文: Tuesday, April 14, 2026, 10:00 AM ET ｜理由: ETは標準時(EST)か夏時間(EDT)かが略号に明記されていないため
- **N-12**: 〔要確認〕（換算不可）｜原文: Tuesday, October 20, 2026, 1:00 PM ET ｜理由: ETは標準時(EST)か夏時間(EDT)かが略号に明記されていないため
- **N-13**: 2026年5月12日(火) 2:30 JST ｜原文: Monday, May 11, 2026, 9:30 AM PST ｜時差: PST=UTC−8（JSTへ +17時間）｜夏時間: なし（PST＝標準時と明記のためそのまま採用、暦上は同時期PDTの地域だが表記に従う）
- **N-14**: 2026年9月16日(水) 7:00 JST ｜原文: Tuesday, September 15, 2026, 2:00 PM PST ｜時差: PST=UTC−8（JSTへ +17時間）｜夏時間: なし（PST＝標準時と明記のためそのまま採用）
- **N-15**: 2026年1月9日(金) 0:00 JST ｜原文: Thursday, January 8, 2026, 11:00 AM EDT ｜時差: EDT=UTC−4（JSTへ +13時間）｜夏時間: あり（EDT＝夏時間と明記のためそのまま採用、暦上は冬季だが表記に従う）
- **N-16**: 2026年12月18日(金) 4:00 JST ｜原文: Thursday, December 17, 2026, 3:00 PM EDT ｜時差: EDT=UTC−4（JSTへ +13時間）｜夏時間: あり（EDT＝夏時間と明記のためそのまま採用、暦上は冬季だが表記に従う）
- **N-17**: 2026年6月15日(月) 14:00 JST ｜原文: Monday, June 15, 2026, 2:00 PM JST ｜時差: 換算不要（原文がJST）｜夏時間: 該当なし
- **N-18**: 2026年11月2日(月) 9:00 JST ｜原文: Monday, November 2, 2026, 9:00 AM JST ｜時差: 換算不要（原文がJST）｜夏時間: 該当なし
- **N-19**: 2026年4月30日(木) 2:00 JST ｜原文: Wednesday, April 29, 2026, 10:30 PM IST (UTC+5:30) ｜時差: UTC+5:30（JSTへ +3時間30分）｜夏時間: 該当なし（インドはサマータイム未導入）
- **N-20**: 2026年12月10日(木) 0:45 JST ｜原文: Wednesday, December 9, 2026, 9:15 PM IST (UTC+5:30) ｜時差: UTC+5:30（JSTへ +3時間30分）｜夏時間: 該当なし（インドはサマータイム未導入）
- **N-21**: 〔要確認〕（換算不可、日付候補: 2026年5月14日(木)）｜原文: 送信日 Thursday, May 7, 2026／本文 "next Thursday at 10:00 AM ET" ｜理由: ETは標準時/夏時間の別が略号に明記されていないため
- **N-22**: 2026年9月17日(木) 23:00 JST ｜原文: 送信日 Thursday, September 10, 2026／本文 "next Thursday at 2:00 PM GMT"（＝2026年9月17日 2:00 PM GMT）｜時差: GMT=UTC+0（JSTへ +9時間）｜夏時間: なし（GMTは標準時、英国の夏時間はBSTと表記されるためGMTは常にUTC+0）
- **N-23**: 2026年7月6日(月) 16:00 JST ｜原文: Monday, July 6, 2026, 9:00 AM (UTC+2) ｜時差: UTC+2（JSTへ +7時間）｜夏時間: 該当なし（数値オフセット表記のため）
- **N-24**: 2026年10月12日(月) 12:00 JST ｜原文: Monday, October 12, 2026, 10:00 AM (UTC+7) ｜時差: UTC+7（JSTへ +2時間）｜夏時間: 該当なし（数値オフセット表記のため）

---

**補足**
- N-09・N-10・N-11・N-12・N-21は、略号「PT」「ET」だけでは標準時（PST/EST）か夏時間（PDT/EDT）かが判別できないため、指示に従い換算せず〔要確認〕としました。
- N-13〜N-16は「PST」「EDT」と標準時/夏時間まで明記されているため、実際の暦（例：1月はEST期間のはず）と食い違って見えても、指示どおり表記された略号のオフセットをそのまま採用しました。
- N-21は「next Thursday」の指す日付（2026年5月14日）は特定できましたが、時刻（ET）の夏時間有無が不明なため、時刻自体は〔要確認〕としています。
- N-22の「GMT」はPT/ETと異なり夏時間の別名（BST）が独立して存在するため、GMT＝UTC+0固定として換算しました。
```

**照合（機械）**

```
found=24/24 correct=19/24
unsure_flags=['N-09', 'N-10', 'N-11', 'N-12', 'N-21']
unsure_false_positive=['N-21']
wrong_detail=N-09(真値2026-05-12 01:30); N-10(真値2026-08-19 08:00); N-11(真値2026-04-14 23:00); N-12(真値2026-10-21 02:00); N-21(真値2026-05-14 23:00)
```

### 判定

**落とした**。材料2本×各1回＝のべ48件のうち10件で誤り。2回ともN-09, N-10, N-11, N-12（標準時/夏時間の略号が明記されていない「PT」「ET」＝指示文3では問題なく暦から換算できていた）と、相対表現のN-21を〔要確認〕にしてしまい、指示文3より誤動作が悪化・拡大した。理由は「言い直し方」節を参照。

---

## 指示文6（言い直し方2つ目・止まった行だけ貼り直す）

### 送った指示文（記事と同一文字列）

```
以下は、案内を日本時間に直そうとしたときに〔要確認〕のまま止まった5件です。

- N-13: 原文 Monday, May 11, 2026, 9:30 AM PST／止まった理由: 5月11日は米国夏時間期間中でPDT(UTC-7)のはずが、表記はPST(UTC-8)で矛盾しており確定不可
- N-14: 原文 Tuesday, September 15, 2026, 2:00 PM PST／止まった理由: 9月15日は米国夏時間期間中でPDT(UTC-7)のはずが、表記はPST(UTC-8)で矛盾しており確定不可
- N-15: 原文 Thursday, January 8, 2026, 11:00 AM EDT／止まった理由: 1月8日は米国夏時間期間外でEST(UTC-5)のはずが、表記はEDT(UTC-4)で矛盾しており確定不可
- N-16: 原文 Thursday, December 17, 2026, 3:00 PM EDT／止まった理由: 12月17日は米国夏時間期間外でEST(UTC-5)のはずが、表記はEDT(UTC-4)で矛盾しており確定不可
- N-22: 送信 Thursday, September 10, 2026、本文「next Thursday at 2:00 PM GMT」（翌週木曜9月17日と解釈）／止まった理由: 9月17日は英国夏時間(BST, UTC+1)期間中でGMT(UTC+0)にはならないはずで矛盾しており確定不可

PST・EDT・GMTのように、標準時か夏時間かまで略号で明記されている場合は、実際の暦と食い違って見えても、その略号のとおりに換算してください。矛盾は無視してよい理由ではなく、略号のほうを優先する理由です。

上の5件を、〔要確認〕のままにせず、1件につき1行「ID: 日本時間の日付と時刻」の形式で書き直してください。
```

### 1回目（新規の独立プロセス）

```
以下のとおりです(略号を優先し、暦との矛盾は無視して換算)。

- N-13: 2026年5月12日(火) 午前2:30
- N-14: 2026年9月16日(水) 午前7:00
- N-15: 2026年1月9日(金) 午前0:00
- N-16: 2026年12月18日(金) 午前4:00
- N-22: 2026年9月17日(木) 午後11:00
```

### 2回目（新規の独立プロセス）

```
以下、略号（PST/EDT/GMT)を額面通りに採用して換算した結果です。

- N-13: 2026年5月12日(火) 2:30
- N-14: 2026年9月16日(水) 7:00
- N-15: 2026年1月9日(金) 0:00
- N-16: 2026年12月18日(金) 4:00
- N-22: 2026年9月17日(木) 23:00
```

**照合（機械・真値との突き合わせ）**

```
真値: N-13=2026-05-12 02:30 / N-14=2026-09-16 07:00 / N-15=2026-01-09 00:00 / N-16=2026-12-18 04:00 / N-22=2026-09-17 23:00
1回目: N-13=2026年5月12日(火)午前2:30 ✓ / N-14=2026年9月16日(水)午前7:00 ✓ / N-15=2026年1月9日(金)午前0:00 ✓ / N-16=2026年12月18日(金)午前4:00 ✓ / N-22=2026年9月17日(木)午後11:00 ✓ → 5/5
2回目: N-13=2026年5月12日(火)2:30 ✓ / N-14=2026年9月16日(水)7:00 ✓ / N-15=2026年1月9日(金)0:00 ✓ / N-16=2026年12月18日(金)4:00 ✓ / N-22=2026年9月17日(木)23:00 ✓ → 5/5
```

### 判定

**採用**。独立した会話2回とも5件全部が真値どおりに換算し直された。

---

## この記事から出た教訓（`content/_lessons.md` へ）

1. 「決められないものは換算せず確認に回して」という受け皿の一文は、間違いを防ぐのではなく受け皿そのものが不安定になることがある（同じ指示文・同じ材料の別の回で、既に答えが決まっている項目まで受け皿に入れてしまった＝4回に1回）。
2. その受け皿の誤動作を「発火条件を先に明文化する」形で直そうとすると、条件に厳密に当てはめるぶん、以前は正しく判断できていた別のケースまで受け皿に入り、誤動作の頻度と範囲がどちらも悪化した。
3. 効いたのは先回りではなく、止まった行だけを見せて後から個別に聞き直すこと（2回とも全部直った）。指示文を複雑にする前に、まず個別に聞き直す価値がある。
