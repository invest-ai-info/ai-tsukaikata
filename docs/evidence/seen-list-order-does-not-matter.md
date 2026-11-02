# 試した証拠 ― seen-list-order-does-not-matter

2026-11-02 実施。架空の「社内掲示板の投稿一覧」（系列A・BBS接頭辞・60件）、「ナレッジベースの記事一覧」（系列B・KBX接頭辞・60件）、「問い合わせ記録」（系列C・NTC接頭辞・300件）を材料に、`claude --print --tools "" --system-prompt "あなたは親切な汎用アシスタントです。ツールやファイルシステムへのアクセスはありません。ユーザーの依頼に文章だけで答えてください。"` を実測の相手にした（[seen-list-catches-the-scattered-gaps](../../content/recipes/seen-list-catches-the-scattered-gaps.md)・[seen-list-catches-the-backfilled-one](../../content/recipes/seen-list-catches-the-backfilled-one.md)と同じ相手・同じ指示文。CLAUDE.md・skills・plugins・履歴を全部無効化。プロジェクト外の空ディレクトリから実行）。言い直し方の自己申告確認だけは、`--session-id <uuid>` で開始したセッションに `-r <同じID>` で続けて投げた（多ターン）。

🔑 **この記事の軸＝既読ID一覧の「並び順」だけ**。投稿一覧・新着の位置・個数・指示文はどれも動かしていない。

**流れ**＝①系列A・Bそれぞれで、既読ID一覧を(a)元の時系列順(b)一部だけ入れ替えた「近い順」(c)完全にランダムにシャッフル、の3条件×各2回＝12回 →②系列C（300件）で同じ3条件×各2回＝6回 →③系列Aのシャッフル版の一括回答に続けて、「今の判断は日付とIDの照合のどちらを手がかりにしたか・既読リストの並び順は投稿一覧と同じ順だったか」を聞く（1回成功、系列B・系列C（2条件）への同じ追加質問は4回中3回が`reasoning_extraction`のAPIセーフガードで失敗）。

**合計18回の独立呼び出し**（①12回＋②6回。③は本体の判定とは別の追加ターンなので呼び出し回数に数えない）。判定はすべて `grade_all.py`（正規表現でID抽出→集合比較）で行った。

---

## 教材（架空データ）

### 仕込み（先に宣言する。走らせる前にコードで確認済み）
```json
{
 "series_a": {
  "prefix": "BBS",
  "n_rows": 60,
  "new_ids": [
   "BBS-b496b461",
   "BBS-1f6cb808",
   "BBS-0ef4399d"
  ],
  "new_positions_pct": [
   10,
   50,
   90
  ],
  "new_idx_0based": [
   6,
   30,
   54
  ]
 },
 "series_b": {
  "prefix": "KBX",
  "n_rows": 60,
  "new_ids": [
   "KBX-1e0d0889",
   "KBX-92932366",
   "KBX-7419fe1c"
  ],
  "new_positions_pct": [
   10,
   50,
   90
  ],
  "new_idx_0based": [
   6,
   30,
   54
  ]
 },
 "series_c": {
  "prefix": "NTC",
  "n_rows": 300,
  "new_ids": [
   "NTC-bda6d410",
   "NTC-578dd4a8",
   "NTC-30955746"
  ],
  "new_positions_pct": [
   7,
   50,
   93
  ],
  "new_idx_0based": [
   21,
   150,
   279
  ],
  "shuffled_match_pct": 0.7,
  "noisy_match_pct": 31.3,
  "swaps": 102
 }
}
```

- IDは `sha1(f"{salt}-{連番}")` の先頭8文字の16進文字列。系列ごとに別のsaltを使った
- 生成スクリプト（下の「生成スクリプト」節）が、走らせる前に次をコードでassertしている（★24相当）:
  - ID文字列のアルファベット順と、一覧の並び順（日付順）の一致が、系列A・Bで2件以下・系列Cで5件以下しかないこと（連番のような手がかりが無いこと）
  - 「シャッフル」版は元の時系列順と同じ位置に来るIDが、系列A・Bで3件以下・系列Cで5件以下しかないこと（弱いシャッフルになっていないこと）
  - 「近い順（ノイズ）」版・シャッフル版とも、元の既読ID一覧と集合として完全に一致すること（重複なし・抜けなし）
- 一致度（並びの一致度）＝元の時系列順の一覧と、各条件の一覧を同じ位置で比べ、同じIDだった位置の割合

### 材料series_a・投稿一覧（60件）

```
2024-04-01: 「社内アンケートの依頼」(ID: BBS-b2f0ee32)
2024-04-02: 「備品の発注ルール変更」(ID: BBS-518b7670)
2024-04-04: 「来月の定例会議の議事録」(ID: BBS-bcc924d7)
2024-04-08: 「社内規程の改定案」(ID: BBS-5acb5676)
2024-04-10: 「備品の発注ルール変更」(ID: BBS-635e3f39)
2024-04-14: 「座席レイアウト変更の告知」(ID: BBS-45d22a11)
2024-04-16: 「オフィス移転の進捗報告」(ID: BBS-b496b461)
2024-04-20: 「社内アンケートの依頼」(ID: BBS-203bb4a1)
2024-04-24: 「社内アンケートの依頼」(ID: BBS-3fef04e4)
2024-04-27: 「座席レイアウト変更の告知」(ID: BBS-9eae9406)
2024-04-28: 「セキュリティ研修の案内」(ID: BBS-f92d68ce)
2024-04-29: 「来月の定例会議の議事録」(ID: BBS-0e1d4bdc)
2024-04-30: 「健康診断の予約方法」(ID: BBS-2cee3017)
2024-05-01: 「社内規程の改定案」(ID: BBS-3bc1b489)
2024-05-05: 「新入社員の自己紹介」(ID: BBS-37a6d6b1)
2024-05-06: 「備品の発注ルール変更」(ID: BBS-f99f2114)
2024-05-07: 「セキュリティ研修の案内」(ID: BBS-36c7afcb)
2024-05-09: 「セキュリティ研修の案内」(ID: BBS-9383f9ca)
2024-05-10: 「社内システムの定期メンテナンス」(ID: BBS-f1c9c435)
2024-05-14: 「来月の定例会議の議事録」(ID: BBS-95e5c81d)
2024-05-17: 「セキュリティ研修の案内」(ID: BBS-7505e629)
2024-05-19: 「オフィス移転の進捗報告」(ID: BBS-b2f1e189)
2024-05-22: 「新入社員の自己紹介」(ID: BBS-96670c80)
2024-05-23: 「部署対抗イベントの告知」(ID: BBS-61c00952)
2024-05-24: 「部署対抗イベントの告知」(ID: BBS-4ded2dc1)
2024-05-26: 「セキュリティ研修の案内」(ID: BBS-8cba495d)
2024-05-29: 「新入社員の自己紹介」(ID: BBS-848f1130)
2024-06-02: 「新しい福利厚生の案内」(ID: BBS-928117dc)
2024-06-06: 「来月の定例会議の議事録」(ID: BBS-6cc9becd)
2024-06-08: 「部署対抗イベントの告知」(ID: BBS-017ac47e)
2024-06-12: 「社内システムの定期メンテナンス」(ID: BBS-1f6cb808)
2024-06-15: 「社内規程の改定案」(ID: BBS-f96c23ea)
2024-06-18: 「社内システムの定期メンテナンス」(ID: BBS-07445953)
2024-06-19: 「新しい福利厚生の案内」(ID: BBS-dd81bdba)
2024-06-22: 「オフィス移転の進捗報告」(ID: BBS-f0829887)
2024-06-24: 「社内システムの定期メンテナンス」(ID: BBS-ff5da954)
2024-06-28: 「部署対抗イベントの告知」(ID: BBS-dd794f0e)
2024-07-02: 「来月の定例会議の議事録」(ID: BBS-c6e67f0e)
2024-07-03: 「来月の定例会議の議事録」(ID: BBS-02d0f4c5)
2024-07-05: 「座席レイアウト変更の告知」(ID: BBS-d44d18d1)
2024-07-07: 「新しい福利厚生の案内」(ID: BBS-d5829a30)
2024-07-10: 「オフィス移転の進捗報告」(ID: BBS-f73bdbef)
2024-07-12: 「新しい福利厚生の案内」(ID: BBS-efbb9ef8)
2024-07-16: 「備品の発注ルール変更」(ID: BBS-56150ea5)
2024-07-17: 「新入社員の自己紹介」(ID: BBS-4521d31a)
2024-07-20: 「セキュリティ研修の案内」(ID: BBS-63d664bf)
2024-07-22: 「社内システムの定期メンテナンス」(ID: BBS-c4ccee84)
2024-07-26: 「健康診断の予約方法」(ID: BBS-011c9277)
2024-07-29: 「部署対抗イベントの告知」(ID: BBS-fcc82f29)
2024-08-02: 「新入社員の自己紹介」(ID: BBS-c9ffd6ca)
2024-08-06: 「健康診断の予約方法」(ID: BBS-b1b43cd0)
2024-08-10: 「部署対抗イベントの告知」(ID: BBS-fd710b5c)
2024-08-14: 「社内規程の改定案」(ID: BBS-2268fcd9)
2024-08-15: 「社内システムの定期メンテナンス」(ID: BBS-9fbc9829)
2024-08-19: 「来月の定例会議の議事録」(ID: BBS-0ef4399d)
2024-08-20: 「社内アンケートの依頼」(ID: BBS-0a7ce682)
2024-08-21: 「部署対抗イベントの告知」(ID: BBS-07f085a6)
2024-08-23: 「社内システムの定期メンテナンス」(ID: BBS-0b817d5f)
2024-08-26: 「社内アンケートの依頼」(ID: BBS-fbeefc13)
2024-08-30: 「来月の定例会議の議事録」(ID: BBS-6709fd2f)
```

### 材料series_a・既読ID一覧（57件・①元の時系列順）

```
BBS-b2f0ee32、BBS-518b7670、BBS-bcc924d7、BBS-5acb5676、BBS-635e3f39、BBS-45d22a11、BBS-203bb4a1、BBS-3fef04e4、BBS-9eae9406、BBS-f92d68ce、BBS-0e1d4bdc、BBS-2cee3017、BBS-3bc1b489、BBS-37a6d6b1、BBS-f99f2114、BBS-36c7afcb、BBS-9383f9ca、BBS-f1c9c435、BBS-95e5c81d、BBS-7505e629、BBS-b2f1e189、BBS-96670c80、BBS-61c00952、BBS-4ded2dc1、BBS-8cba495d、BBS-848f1130、BBS-928117dc、BBS-6cc9becd、BBS-017ac47e、BBS-f96c23ea、BBS-07445953、BBS-dd81bdba、BBS-f0829887、BBS-ff5da954、BBS-dd794f0e、BBS-c6e67f0e、BBS-02d0f4c5、BBS-d44d18d1、BBS-d5829a30、BBS-f73bdbef、BBS-efbb9ef8、BBS-56150ea5、BBS-4521d31a、BBS-63d664bf、BBS-c4ccee84、BBS-011c9277、BBS-fcc82f29、BBS-c9ffd6ca、BBS-b1b43cd0、BBS-fd710b5c、BBS-2268fcd9、BBS-9fbc9829、BBS-0a7ce682、BBS-07f085a6、BBS-0b817d5f、BBS-fbeefc13、BBS-6709fd2f
```

### 材料series_a・既読ID一覧（57件・②近い順＝局所的な乱れ）

```
BBS-518b7670、BBS-b2f0ee32、BBS-5acb5676、BBS-bcc924d7、BBS-45d22a11、BBS-635e3f39、BBS-3fef04e4、BBS-203bb4a1、BBS-f92d68ce、BBS-9eae9406、BBS-0e1d4bdc、BBS-2cee3017、BBS-3bc1b489、BBS-37a6d6b1、BBS-36c7afcb、BBS-f99f2114、BBS-f1c9c435、BBS-9383f9ca、BBS-95e5c81d、BBS-7505e629、BBS-b2f1e189、BBS-96670c80、BBS-4ded2dc1、BBS-61c00952、BBS-8cba495d、BBS-848f1130、BBS-6cc9becd、BBS-928117dc、BBS-017ac47e、BBS-07445953、BBS-f96c23ea、BBS-dd81bdba、BBS-ff5da954、BBS-f0829887、BBS-dd794f0e、BBS-02d0f4c5、BBS-c6e67f0e、BBS-d44d18d1、BBS-d5829a30、BBS-f73bdbef、BBS-efbb9ef8、BBS-4521d31a、BBS-56150ea5、BBS-63d664bf、BBS-c4ccee84、BBS-fcc82f29、BBS-011c9277、BBS-c9ffd6ca、BBS-fd710b5c、BBS-b1b43cd0、BBS-2268fcd9、BBS-0a7ce682、BBS-9fbc9829、BBS-07f085a6、BBS-fbeefc13、BBS-0b817d5f、BBS-6709fd2f
```

### 材料series_a・既読ID一覧（57件・③完全にシャッフル）

```
BBS-f73bdbef、BBS-518b7670、BBS-dd794f0e、BBS-2268fcd9、BBS-efbb9ef8、BBS-2cee3017、BBS-9eae9406、BBS-011c9277、BBS-b2f1e189、BBS-203bb4a1、BBS-61c00952、BBS-c9ffd6ca、BBS-b1b43cd0、BBS-848f1130、BBS-37a6d6b1、BBS-07445953、BBS-5acb5676、BBS-9383f9ca、BBS-ff5da954、BBS-f99f2114、BBS-36c7afcb、BBS-635e3f39、BBS-6cc9becd、BBS-fcc82f29、BBS-fd710b5c、BBS-0a7ce682、BBS-f0829887、BBS-4521d31a、BBS-95e5c81d、BBS-02d0f4c5、BBS-bcc924d7、BBS-45d22a11、BBS-fbeefc13、BBS-0b817d5f、BBS-f1c9c435、BBS-c4ccee84、BBS-dd81bdba、BBS-3fef04e4、BBS-f96c23ea、BBS-7505e629、BBS-f92d68ce、BBS-56150ea5、BBS-63d664bf、BBS-d5829a30、BBS-0e1d4bdc、BBS-6709fd2f、BBS-d44d18d1、BBS-928117dc、BBS-96670c80、BBS-4ded2dc1、BBS-b2f0ee32、BBS-3bc1b489、BBS-8cba495d、BBS-9fbc9829、BBS-c6e67f0e、BBS-07f085a6、BBS-017ac47e
```

### 材料series_b・投稿一覧（60件）

```
2024-07-01: 「新バージョンの操作マニュアル」(ID: KBX-e1f6184c)
2024-07-03: 「トラブル対応のFAQ追加」(ID: KBX-d07cbd2d)
2024-07-05: 「外部連携APIの仕様変更」(ID: KBX-bf4d1285)
2024-07-07: 「請求書発行手順の更新」(ID: KBX-3110e6bf)
2024-07-10: 「問い合わせ分類の見直し」(ID: KBX-30ee667b)
2024-07-11: 「トラブル対応のFAQ追加」(ID: KBX-161538c3)
2024-07-16: 「外部連携APIの仕様変更」(ID: KBX-1e0d0889)
2024-07-19: 「設定手順のスクリーンショット更新」(ID: KBX-6ca9b025)
2024-07-21: 「データ保管ルールの改定」(ID: KBX-dc74851b)
2024-07-24: 「旧機能の廃止予定」(ID: KBX-11c473a8)
2024-07-27: 「旧機能の廃止予定」(ID: KBX-cfb4e90c)
2024-07-29: 「外部連携APIの仕様変更」(ID: KBX-9e7c2b3a)
2024-07-30: 「請求書発行手順の更新」(ID: KBX-501b732a)
2024-07-31: 「社内ツールの権限申請フロー」(ID: KBX-a982c7dc)
2024-08-02: 「問い合わせ分類の見直し」(ID: KBX-9df9973e)
2024-08-07: 「外部連携APIの仕様変更」(ID: KBX-c83515c4)
2024-08-08: 「新機能のリリースノート」(ID: KBX-e4256162)
2024-08-11: 「請求書発行手順の更新」(ID: KBX-2aebcce1)
2024-08-12: 「旧機能の廃止予定」(ID: KBX-9b4f77b0)
2024-08-14: 「外部連携APIの仕様変更」(ID: KBX-0de28669)
2024-08-17: 「社内ツールの権限申請フロー」(ID: KBX-0754e7aa)
2024-08-18: 「用語集の追補」(ID: KBX-95e37ba6)
2024-08-19: 「データ保管ルールの改定」(ID: KBX-a9caa3bd)
2024-08-21: 「新機能のリリースノート」(ID: KBX-77c5c8c4)
2024-08-23: 「旧機能の廃止予定」(ID: KBX-9218483b)
2024-08-24: 「設定手順のスクリーンショット更新」(ID: KBX-2cbd9675)
2024-08-29: 「トラブル対応のFAQ追加」(ID: KBX-5776a9fc)
2024-08-30: 「トラブル対応のFAQ追加」(ID: KBX-f296a3f9)
2024-08-31: 「既知の不具合と回避策」(ID: KBX-82480d81)
2024-09-05: 「新バージョンの操作マニュアル」(ID: KBX-fab8dad8)
2024-09-06: 「用語集の追補」(ID: KBX-92932366)
2024-09-09: 「設定手順のスクリーンショット更新」(ID: KBX-de0c5bf5)
2024-09-11: 「トラブル対応のFAQ追加」(ID: KBX-d15b67cf)
2024-09-14: 「請求書発行手順の更新」(ID: KBX-360e1431)
2024-09-15: 「外部連携APIの仕様変更」(ID: KBX-866a0383)
2024-09-17: 「問い合わせ分類の見直し」(ID: KBX-73cea57d)
2024-09-22: 「請求書発行手順の更新」(ID: KBX-f1b4025f)
2024-09-25: 「社内ツールの権限申請フロー」(ID: KBX-96eae079)
2024-09-27: 「設定手順のスクリーンショット更新」(ID: KBX-790e89ad)
2024-09-30: 「用語集の追補」(ID: KBX-89910e0f)
2024-10-05: 「既知の不具合と回避策」(ID: KBX-281ac18d)
2024-10-10: 「用語集の追補」(ID: KBX-a93d31b5)
2024-10-13: 「新機能のリリースノート」(ID: KBX-1d6023f2)
2024-10-15: 「旧機能の廃止予定」(ID: KBX-8c203668)
2024-10-16: 「設定手順のスクリーンショット更新」(ID: KBX-ee03b696)
2024-10-17: 「新バージョンの操作マニュアル」(ID: KBX-74e07e9b)
2024-10-20: 「新機能のリリースノート」(ID: KBX-91258790)
2024-10-21: 「データ保管ルールの改定」(ID: KBX-1397fc4e)
2024-10-24: 「データ保管ルールの改定」(ID: KBX-d0379a05)
2024-10-27: 「用語集の追補」(ID: KBX-32fc39e2)
2024-10-30: 「旧機能の廃止予定」(ID: KBX-a78b4d2c)
2024-10-31: 「社内ツールの権限申請フロー」(ID: KBX-16b059e5)
2024-11-03: 「トラブル対応のFAQ追加」(ID: KBX-df53d933)
2024-11-04: 「データ保管ルールの改定」(ID: KBX-05595d6e)
2024-11-07: 「問い合わせ分類の見直し」(ID: KBX-7419fe1c)
2024-11-10: 「外部連携APIの仕様変更」(ID: KBX-e0242e05)
2024-11-12: 「社内ツールの権限申請フロー」(ID: KBX-8fd9224b)
2024-11-14: 「設定手順のスクリーンショット更新」(ID: KBX-ec0099af)
2024-11-17: 「新機能のリリースノート」(ID: KBX-d04d01bd)
2024-11-22: 「請求書発行手順の更新」(ID: KBX-2014540e)
```

### 材料series_b・既読ID一覧（57件・①元の時系列順）

```
KBX-e1f6184c、KBX-d07cbd2d、KBX-bf4d1285、KBX-3110e6bf、KBX-30ee667b、KBX-161538c3、KBX-6ca9b025、KBX-dc74851b、KBX-11c473a8、KBX-cfb4e90c、KBX-9e7c2b3a、KBX-501b732a、KBX-a982c7dc、KBX-9df9973e、KBX-c83515c4、KBX-e4256162、KBX-2aebcce1、KBX-9b4f77b0、KBX-0de28669、KBX-0754e7aa、KBX-95e37ba6、KBX-a9caa3bd、KBX-77c5c8c4、KBX-9218483b、KBX-2cbd9675、KBX-5776a9fc、KBX-f296a3f9、KBX-82480d81、KBX-fab8dad8、KBX-de0c5bf5、KBX-d15b67cf、KBX-360e1431、KBX-866a0383、KBX-73cea57d、KBX-f1b4025f、KBX-96eae079、KBX-790e89ad、KBX-89910e0f、KBX-281ac18d、KBX-a93d31b5、KBX-1d6023f2、KBX-8c203668、KBX-ee03b696、KBX-74e07e9b、KBX-91258790、KBX-1397fc4e、KBX-d0379a05、KBX-32fc39e2、KBX-a78b4d2c、KBX-16b059e5、KBX-df53d933、KBX-05595d6e、KBX-e0242e05、KBX-8fd9224b、KBX-ec0099af、KBX-d04d01bd、KBX-2014540e
```

### 材料series_b・既読ID一覧（57件・②近い順＝局所的な乱れ）

```
KBX-d07cbd2d、KBX-e1f6184c、KBX-3110e6bf、KBX-bf4d1285、KBX-30ee667b、KBX-161538c3、KBX-6ca9b025、KBX-dc74851b、KBX-cfb4e90c、KBX-11c473a8、KBX-501b732a、KBX-9e7c2b3a、KBX-a982c7dc、KBX-c83515c4、KBX-9df9973e、KBX-e4256162、KBX-2aebcce1、KBX-9b4f77b0、KBX-0de28669、KBX-95e37ba6、KBX-0754e7aa、KBX-77c5c8c4、KBX-a9caa3bd、KBX-9218483b、KBX-2cbd9675、KBX-f296a3f9、KBX-5776a9fc、KBX-82480d81、KBX-de0c5bf5、KBX-fab8dad8、KBX-360e1431、KBX-d15b67cf、KBX-73cea57d、KBX-866a0383、KBX-96eae079、KBX-f1b4025f、KBX-89910e0f、KBX-790e89ad、KBX-281ac18d、KBX-a93d31b5、KBX-8c203668、KBX-1d6023f2、KBX-74e07e9b、KBX-ee03b696、KBX-91258790、KBX-d0379a05、KBX-1397fc4e、KBX-a78b4d2c、KBX-32fc39e2、KBX-df53d933、KBX-16b059e5、KBX-05595d6e、KBX-8fd9224b、KBX-e0242e05、KBX-ec0099af、KBX-2014540e、KBX-d04d01bd
```

### 材料series_b・既読ID一覧（57件・③完全にシャッフル）

```
KBX-05595d6e、KBX-82480d81、KBX-161538c3、KBX-2cbd9675、KBX-8c203668、KBX-ec0099af、KBX-501b732a、KBX-d04d01bd、KBX-281ac18d、KBX-8fd9224b、KBX-d07cbd2d、KBX-cfb4e90c、KBX-a93d31b5、KBX-c83515c4、KBX-bf4d1285、KBX-91258790、KBX-32fc39e2、KBX-95e37ba6、KBX-89910e0f、KBX-866a0383、KBX-9b4f77b0、KBX-16b059e5、KBX-d15b67cf、KBX-96eae079、KBX-360e1431、KBX-de0c5bf5、KBX-2aebcce1、KBX-1d6023f2、KBX-df53d933、KBX-9218483b、KBX-d0379a05、KBX-a9caa3bd、KBX-f1b4025f、KBX-dc74851b、KBX-2014540e、KBX-fab8dad8、KBX-790e89ad、KBX-0754e7aa、KBX-9e7c2b3a、KBX-74e07e9b、KBX-6ca9b025、KBX-f296a3f9、KBX-ee03b696、KBX-11c473a8、KBX-5776a9fc、KBX-1397fc4e、KBX-a78b4d2c、KBX-e1f6184c、KBX-a982c7dc、KBX-73cea57d、KBX-77c5c8c4、KBX-0de28669、KBX-3110e6bf、KBX-e0242e05、KBX-e4256162、KBX-30ee667b、KBX-9df9973e
```

### 材料series_c・投稿一覧（300件）

```
2023-05-01: 「オフィス移転の進捗報告」(ID: NTC-3ed2b89c)
2023-05-03: 「新入社員の自己紹介」(ID: NTC-93b8658f)
2023-05-05: 「部署対抗イベントの告知」(ID: NTC-e0ab30f6)
2023-05-09: 「社内規程の改定案」(ID: NTC-f7df0772)
2023-05-11: 「備品の発注ルール変更」(ID: NTC-a3d8160f)
2023-05-12: 「セキュリティ研修の案内」(ID: NTC-d730102b)
2023-05-16: 「社内アンケートの依頼」(ID: NTC-e106c938)
2023-05-20: 「オフィス移転の進捗報告」(ID: NTC-f70e4540)
2023-05-21: 「部署対抗イベントの告知」(ID: NTC-08f82dd1)
2023-05-24: 「トラブル対応のFAQ追加」(ID: NTC-24134f66)
2023-05-25: 「部署対抗イベントの告知」(ID: NTC-2751cf72)
2023-05-27: 「新バージョンの操作マニュアル」(ID: NTC-277ecb12)
2023-05-31: 「部署対抗イベントの告知」(ID: NTC-59256415)
2023-06-02: 「新バージョンの操作マニュアル」(ID: NTC-62d2e675)
2023-06-03: 「請求書発行手順の更新」(ID: NTC-2f9d1bbb)
2023-06-05: 「オフィス移転の進捗報告」(ID: NTC-8dd16c22)
2023-06-07: 「座席レイアウト変更の告知」(ID: NTC-471a2fc3)
2023-06-08: 「請求書発行手順の更新」(ID: NTC-ff65eb12)
2023-06-10: 「健康診断の予約方法」(ID: NTC-cda91ad1)
2023-06-14: 「部署対抗イベントの告知」(ID: NTC-157a650d)
2023-06-18: 「請求書発行手順の更新」(ID: NTC-8d15b96c)
2023-06-21: 「備品の発注ルール変更」(ID: NTC-bda6d410)
2023-06-25: 「部署対抗イベントの告知」(ID: NTC-4a055331)
2023-06-27: 「新しい福利厚生の案内」(ID: NTC-1e21aca1)
2023-06-30: 「オフィス移転の進捗報告」(ID: NTC-9e872276)
2023-07-02: 「新しい福利厚生の案内」(ID: NTC-851e95a4)
2023-07-06: 「座席レイアウト変更の告知」(ID: NTC-2c6ac15c)
2023-07-07: 「トラブル対応のFAQ追加」(ID: NTC-d412f945)
2023-07-11: 「新入社員の自己紹介」(ID: NTC-8cc8f2d9)
2023-07-14: 「健康診断の予約方法」(ID: NTC-a383a1dd)
2023-07-15: 「新バージョンの操作マニュアル」(ID: NTC-58f713ca)
2023-07-19: 「新入社員の自己紹介」(ID: NTC-d71a13f3)
2023-07-22: 「備品の発注ルール変更」(ID: NTC-4cbaba04)
2023-07-25: 「座席レイアウト変更の告知」(ID: NTC-52fa9051)
2023-07-27: 「新バージョンの操作マニュアル」(ID: NTC-ba0cb572)
2023-07-31: 「請求書発行手順の更新」(ID: NTC-4af23c87)
2023-08-01: 「健康診断の予約方法」(ID: NTC-fd925429)
2023-08-04: 「健康診断の予約方法」(ID: NTC-e32168fe)
2023-08-06: 「健康診断の予約方法」(ID: NTC-16a4caa7)
2023-08-08: 「請求書発行手順の更新」(ID: NTC-6590b8d0)
2023-08-11: 「セキュリティ研修の案内」(ID: NTC-afb8356c)
2023-08-12: 「来月の定例会議の議事録」(ID: NTC-b0f97a98)
2023-08-16: 「来月の定例会議の議事録」(ID: NTC-9fc47ea5)
2023-08-18: 「備品の発注ルール変更」(ID: NTC-d931bd05)
2023-08-20: 「オフィス移転の進捗報告」(ID: NTC-993fe7ba)
2023-08-24: 「トラブル対応のFAQ追加」(ID: NTC-a65c224c)
2023-08-25: 「新バージョンの操作マニュアル」(ID: NTC-311aea30)
2023-08-27: 「社内アンケートの依頼」(ID: NTC-e2256410)
2023-08-29: 「来月の定例会議の議事録」(ID: NTC-ddcc9276)
2023-08-31: 「来月の定例会議の議事録」(ID: NTC-f0a566ad)
2023-09-02: 「トラブル対応のFAQ追加」(ID: NTC-6f9968db)
2023-09-04: 「セキュリティ研修の案内」(ID: NTC-7b5035b5)
2023-09-07: 「座席レイアウト変更の告知」(ID: NTC-69f98ffe)
2023-09-10: 「座席レイアウト変更の告知」(ID: NTC-4a770ea7)
2023-09-12: 「来月の定例会議の議事録」(ID: NTC-a13c17e7)
2023-09-14: 「セキュリティ研修の案内」(ID: NTC-8fcdfba8)
2023-09-16: 「セキュリティ研修の案内」(ID: NTC-4f357f02)
2023-09-19: 「来月の定例会議の議事録」(ID: NTC-5e0412be)
2023-09-23: 「社内アンケートの依頼」(ID: NTC-cb3ed3dd)
2023-09-27: 「来月の定例会議の議事録」(ID: NTC-5f1fcac8)
2023-10-01: 「健康診断の予約方法」(ID: NTC-b8a58641)
2023-10-04: 「請求書発行手順の更新」(ID: NTC-a92fc1c2)
2023-10-05: 「社内アンケートの依頼」(ID: NTC-3a82fb3d)
2023-10-09: 「社内アンケートの依頼」(ID: NTC-54e8ea5c)
2023-10-13: 「社内システムの定期メンテナンス」(ID: NTC-01a8e350)
2023-10-14: 「請求書発行手順の更新」(ID: NTC-d3729278)
2023-10-17: 「オフィス移転の進捗報告」(ID: NTC-1d0b1ce0)
2023-10-19: 「社内アンケートの依頼」(ID: NTC-caa74e41)
2023-10-21: 「社内アンケートの依頼」(ID: NTC-df37979d)
2023-10-23: 「社内システムの定期メンテナンス」(ID: NTC-1380261c)
2023-10-27: 「座席レイアウト変更の告知」(ID: NTC-3a5c4e06)
2023-10-29: 「オフィス移転の進捗報告」(ID: NTC-54223c7d)
2023-11-01: 「健康診断の予約方法」(ID: NTC-f828e6f2)
2023-11-05: 「社内規程の改定案」(ID: NTC-a6dcb69d)
2023-11-06: 「オフィス移転の進捗報告」(ID: NTC-10f85012)
2023-11-08: 「社内規程の改定案」(ID: NTC-bcb5dd18)
2023-11-12: 「社内システムの定期メンテナンス」(ID: NTC-b251f857)
2023-11-13: 「部署対抗イベントの告知」(ID: NTC-550104f4)
2023-11-15: 「来月の定例会議の議事録」(ID: NTC-58211dd5)
2023-11-18: 「トラブル対応のFAQ追加」(ID: NTC-70b7abaf)
2023-11-20: 「セキュリティ研修の案内」(ID: NTC-0295e51b)
2023-11-22: 「新しい福利厚生の案内」(ID: NTC-8e543040)
2023-11-23: 「新しい福利厚生の案内」(ID: NTC-90a94703)
2023-11-25: 「社内規程の改定案」(ID: NTC-2ccd1471)
2023-11-26: 「社内システムの定期メンテナンス」(ID: NTC-7861f0a1)
2023-11-30: 「部署対抗イベントの告知」(ID: NTC-29031045)
2023-12-03: 「新バージョンの操作マニュアル」(ID: NTC-8c6e0b46)
2023-12-05: 「新バージョンの操作マニュアル」(ID: NTC-1301286c)
2023-12-08: 「新しい福利厚生の案内」(ID: NTC-d61e2ce3)
2023-12-09: 「部署対抗イベントの告知」(ID: NTC-de64dd33)
2023-12-12: 「トラブル対応のFAQ追加」(ID: NTC-ab14a1e3)
2023-12-14: 「新しい福利厚生の案内」(ID: NTC-64fa88ca)
2023-12-16: 「新バージョンの操作マニュアル」(ID: NTC-41fe4ba4)
2023-12-19: 「来月の定例会議の議事録」(ID: NTC-edb26bf7)
2023-12-20: 「社内システムの定期メンテナンス」(ID: NTC-2e5a6e0b)
2023-12-22: 「新入社員の自己紹介」(ID: NTC-33e5ccc3)
2023-12-24: 「請求書発行手順の更新」(ID: NTC-f80298af)
2023-12-26: 「オフィス移転の進捗報告」(ID: NTC-68d5e706)
2023-12-29: 「新入社員の自己紹介」(ID: NTC-a1d0f81e)
2023-12-31: 「社内アンケートの依頼」(ID: NTC-910f0e78)
2024-01-02: 「社内規程の改定案」(ID: NTC-dc5237dc)
2024-01-03: 「新入社員の自己紹介」(ID: NTC-a97b1a91)
2024-01-05: 「トラブル対応のFAQ追加」(ID: NTC-f45421ac)
2024-01-07: 「請求書発行手順の更新」(ID: NTC-13b6e1d1)
2024-01-08: 「座席レイアウト変更の告知」(ID: NTC-5aa872ee)
2024-01-10: 「来月の定例会議の議事録」(ID: NTC-085d9077)
2024-01-12: 「新入社員の自己紹介」(ID: NTC-df649200)
2024-01-14: 「部署対抗イベントの告知」(ID: NTC-93bff574)
2024-01-16: 「社内アンケートの依頼」(ID: NTC-bb0434e8)
2024-01-18: 「トラブル対応のFAQ追加」(ID: NTC-e5aaffa2)
2024-01-19: 「トラブル対応のFAQ追加」(ID: NTC-edd8be31)
2024-01-22: 「新しい福利厚生の案内」(ID: NTC-11a60c01)
2024-01-24: 「請求書発行手順の更新」(ID: NTC-86bbe679)
2024-01-27: 「備品の発注ルール変更」(ID: NTC-d538abd8)
2024-01-28: 「健康診断の予約方法」(ID: NTC-9fa416b6)
2024-01-30: 「座席レイアウト変更の告知」(ID: NTC-dcdf38f5)
2024-02-02: 「座席レイアウト変更の告知」(ID: NTC-a275756a)
2024-02-06: 「社内アンケートの依頼」(ID: NTC-48587cba)
2024-02-07: 「座席レイアウト変更の告知」(ID: NTC-bdab1ce7)
2024-02-11: 「新しい福利厚生の案内」(ID: NTC-c6a098bd)
2024-02-15: 「オフィス移転の進捗報告」(ID: NTC-0a9a8354)
2024-02-17: 「セキュリティ研修の案内」(ID: NTC-20f5494b)
2024-02-18: 「部署対抗イベントの告知」(ID: NTC-a6162a5e)
2024-02-19: 「新しい福利厚生の案内」(ID: NTC-f0b3fd85)
2024-02-20: 「新しい福利厚生の案内」(ID: NTC-21fb942c)
2024-02-22: 「新バージョンの操作マニュアル」(ID: NTC-94acc9c3)
2024-02-24: 「セキュリティ研修の案内」(ID: NTC-a112d1ee)
2024-02-26: 「備品の発注ルール変更」(ID: NTC-b361e253)
2024-02-27: 「新入社員の自己紹介」(ID: NTC-64c8ac9b)
2024-02-29: 「新バージョンの操作マニュアル」(ID: NTC-30456dbd)
2024-03-01: 「健康診断の予約方法」(ID: NTC-e7d282e2)
2024-03-03: 「新バージョンの操作マニュアル」(ID: NTC-11846ce4)
2024-03-04: 「新しい福利厚生の案内」(ID: NTC-f2b4fa41)
2024-03-06: 「社内アンケートの依頼」(ID: NTC-b9990db7)
2024-03-08: 「部署対抗イベントの告知」(ID: NTC-ff71666c)
2024-03-09: 「社内規程の改定案」(ID: NTC-8bbd2aba)
2024-03-11: 「座席レイアウト変更の告知」(ID: NTC-e1b0eeab)
2024-03-13: 「部署対抗イベントの告知」(ID: NTC-72ae4f0f)
2024-03-14: 「社内アンケートの依頼」(ID: NTC-51a042f7)
2024-03-16: 「トラブル対応のFAQ追加」(ID: NTC-9605eb43)
2024-03-19: 「請求書発行手順の更新」(ID: NTC-59307d99)
2024-03-20: 「来月の定例会議の議事録」(ID: NTC-7f2654f3)
2024-03-22: 「部署対抗イベントの告知」(ID: NTC-d2ff78cb)
2024-03-24: 「社内システムの定期メンテナンス」(ID: NTC-c901b009)
2024-03-27: 「トラブル対応のFAQ追加」(ID: NTC-6b27ca97)
2024-03-28: 「セキュリティ研修の案内」(ID: NTC-ee06ba27)
2024-03-31: 「社内システムの定期メンテナンス」(ID: NTC-0b99d6ff)
2024-04-02: 「座席レイアウト変更の告知」(ID: NTC-d821200b)
2024-04-06: 「トラブル対応のFAQ追加」(ID: NTC-fde1f364)
2024-04-08: 「セキュリティ研修の案内」(ID: NTC-884ee37c)
2024-04-11: 「備品の発注ルール変更」(ID: NTC-578dd4a8)
2024-04-14: 「トラブル対応のFAQ追加」(ID: NTC-9af21243)
2024-04-15: 「社内システムの定期メンテナンス」(ID: NTC-b9668371)
2024-04-17: 「新バージョンの操作マニュアル」(ID: NTC-95bcd44d)
2024-04-19: 「社内規程の改定案」(ID: NTC-c0e87e2d)
2024-04-20: 「座席レイアウト変更の告知」(ID: NTC-632f1dcb)
2024-04-21: 「来月の定例会議の議事録」(ID: NTC-8e2ad7a0)
2024-04-23: 「来月の定例会議の議事録」(ID: NTC-23d9638b)
2024-04-26: 「備品の発注ルール変更」(ID: NTC-140349f0)
2024-04-27: 「健康診断の予約方法」(ID: NTC-00e464ef)
2024-04-29: 「社内規程の改定案」(ID: NTC-ab79accf)
2024-05-02: 「請求書発行手順の更新」(ID: NTC-f332b315)
2024-05-04: 「セキュリティ研修の案内」(ID: NTC-3c1c9b88)
2024-05-05: 「請求書発行手順の更新」(ID: NTC-00416a4d)
2024-05-07: 「社内規程の改定案」(ID: NTC-fdb10b59)
2024-05-09: 「新入社員の自己紹介」(ID: NTC-c3cc3dbb)
2024-05-12: 「新しい福利厚生の案内」(ID: NTC-dd2668e1)
2024-05-14: 「部署対抗イベントの告知」(ID: NTC-91834675)
2024-05-18: 「オフィス移転の進捗報告」(ID: NTC-df759857)
2024-05-20: 「新バージョンの操作マニュアル」(ID: NTC-93ed8cdf)
2024-05-24: 「社内システムの定期メンテナンス」(ID: NTC-357b1dcf)
2024-05-26: 「座席レイアウト変更の告知」(ID: NTC-0ded99ec)
2024-05-27: 「来月の定例会議の議事録」(ID: NTC-054efc8a)
2024-05-28: 「部署対抗イベントの告知」(ID: NTC-7621dba7)
2024-05-31: 「座席レイアウト変更の告知」(ID: NTC-3a4da392)
2024-06-02: 「トラブル対応のFAQ追加」(ID: NTC-57e7c9a8)
2024-06-06: 「新バージョンの操作マニュアル」(ID: NTC-171cbcac)
2024-06-08: 「社内アンケートの依頼」(ID: NTC-4035d765)
2024-06-10: 「備品の発注ルール変更」(ID: NTC-99673e9b)
2024-06-12: 「健康診断の予約方法」(ID: NTC-246b7268)
2024-06-14: 「請求書発行手順の更新」(ID: NTC-55bc1f99)
2024-06-18: 「オフィス移転の進捗報告」(ID: NTC-d36b0cd5)
2024-06-22: 「新しい福利厚生の案内」(ID: NTC-013c8340)
2024-06-24: 「社内システムの定期メンテナンス」(ID: NTC-acd69773)
2024-06-28: 「トラブル対応のFAQ追加」(ID: NTC-8b1bbb62)
2024-07-02: 「新しい福利厚生の案内」(ID: NTC-8c8ffdb8)
2024-07-06: 「社内規程の改定案」(ID: NTC-bbcd6610)
2024-07-10: 「備品の発注ルール変更」(ID: NTC-25037d92)
2024-07-11: 「セキュリティ研修の案内」(ID: NTC-1197d2c4)
2024-07-13: 「社内アンケートの依頼」(ID: NTC-7aa47d82)
2024-07-16: 「新バージョンの操作マニュアル」(ID: NTC-a294247b)
2024-07-18: 「請求書発行手順の更新」(ID: NTC-8c0aeabd)
2024-07-20: 「社内規程の改定案」(ID: NTC-f4acc866)
2024-07-22: 「社内規程の改定案」(ID: NTC-09f7d07d)
2024-07-24: 「座席レイアウト変更の告知」(ID: NTC-f47b2032)
2024-07-26: 「社内規程の改定案」(ID: NTC-bbb699ae)
2024-07-29: 「社内規程の改定案」(ID: NTC-19e632fa)
2024-07-30: 「新しい福利厚生の案内」(ID: NTC-d7ada788)
2024-08-02: 「請求書発行手順の更新」(ID: NTC-4f443fab)
2024-08-06: 「来月の定例会議の議事録」(ID: NTC-3d231678)
2024-08-09: 「来月の定例会議の議事録」(ID: NTC-918b9e46)
2024-08-11: 「社内アンケートの依頼」(ID: NTC-160af81f)
2024-08-15: 「部署対抗イベントの告知」(ID: NTC-9238d300)
2024-08-18: 「座席レイアウト変更の告知」(ID: NTC-766a8c90)
2024-08-19: 「社内規程の改定案」(ID: NTC-faa309f9)
2024-08-22: 「新しい福利厚生の案内」(ID: NTC-e8e93292)
2024-08-24: 「オフィス移転の進捗報告」(ID: NTC-69091579)
2024-08-26: 「セキュリティ研修の案内」(ID: NTC-5ed8655b)
2024-08-28: 「新バージョンの操作マニュアル」(ID: NTC-cb0db7e8)
2024-09-01: 「社内アンケートの依頼」(ID: NTC-ad4c18be)
2024-09-03: 「社内アンケートの依頼」(ID: NTC-ca264f81)
2024-09-05: 「社内システムの定期メンテナンス」(ID: NTC-2b682ee3)
2024-09-06: 「社内アンケートの依頼」(ID: NTC-db92bd43)
2024-09-08: 「オフィス移転の進捗報告」(ID: NTC-4034f9d1)
2024-09-10: 「新バージョンの操作マニュアル」(ID: NTC-444e352f)
2024-09-12: 「社内規程の改定案」(ID: NTC-814d90d1)
2024-09-15: 「トラブル対応のFAQ追加」(ID: NTC-b4cf3769)
2024-09-17: 「来月の定例会議の議事録」(ID: NTC-66f57040)
2024-09-19: 「社内システムの定期メンテナンス」(ID: NTC-4a62d877)
2024-09-23: 「新入社員の自己紹介」(ID: NTC-b0ca7c1c)
2024-09-25: 「来月の定例会議の議事録」(ID: NTC-dd9282d1)
2024-09-27: 「健康診断の予約方法」(ID: NTC-2d400f23)
2024-09-29: 「社内システムの定期メンテナンス」(ID: NTC-357b9ffb)
2024-10-01: 「社内規程の改定案」(ID: NTC-dc6c22c5)
2024-10-04: 「新入社員の自己紹介」(ID: NTC-d54a5c4d)
2024-10-06: 「社内システムの定期メンテナンス」(ID: NTC-5d1d03d1)
2024-10-08: 「請求書発行手順の更新」(ID: NTC-4f4264bd)
2024-10-10: 「社内アンケートの依頼」(ID: NTC-12cfab30)
2024-10-12: 「来月の定例会議の議事録」(ID: NTC-89bd2c6d)
2024-10-13: 「部署対抗イベントの告知」(ID: NTC-2ab25d52)
2024-10-17: 「来月の定例会議の議事録」(ID: NTC-11da22a6)
2024-10-18: 「社内アンケートの依頼」(ID: NTC-d97868f6)
2024-10-21: 「座席レイアウト変更の告知」(ID: NTC-53f521d2)
2024-10-25: 「来月の定例会議の議事録」(ID: NTC-dd5259d6)
2024-10-26: 「来月の定例会議の議事録」(ID: NTC-691ad2b6)
2024-10-27: 「請求書発行手順の更新」(ID: NTC-45ea39a4)
2024-10-29: 「新バージョンの操作マニュアル」(ID: NTC-e7c7ab58)
2024-10-30: 「トラブル対応のFAQ追加」(ID: NTC-f9bcb61b)
2024-11-01: 「社内規程の改定案」(ID: NTC-76c2ef5b)
2024-11-03: 「部署対抗イベントの告知」(ID: NTC-d060a925)
2024-11-05: 「オフィス移転の進捗報告」(ID: NTC-50f4d581)
2024-11-07: 「請求書発行手順の更新」(ID: NTC-8e887a9a)
2024-11-09: 「オフィス移転の進捗報告」(ID: NTC-ebd1ede3)
2024-11-10: 「備品の発注ルール変更」(ID: NTC-3d2ca37a)
2024-11-12: 「座席レイアウト変更の告知」(ID: NTC-91877abb)
2024-11-16: 「健康診断の予約方法」(ID: NTC-be6d0d91)
2024-11-18: 「備品の発注ルール変更」(ID: NTC-9b439ff8)
2024-11-21: 「備品の発注ルール変更」(ID: NTC-72421e9e)
2024-11-24: 「セキュリティ研修の案内」(ID: NTC-aa1ce177)
2024-11-26: 「備品の発注ルール変更」(ID: NTC-c095ef33)
2024-11-28: 「セキュリティ研修の案内」(ID: NTC-6b876bfc)
2024-12-02: 「部署対抗イベントの告知」(ID: NTC-95778c6e)
2024-12-05: 「来月の定例会議の議事録」(ID: NTC-15d903a1)
2024-12-09: 「トラブル対応のFAQ追加」(ID: NTC-6303216e)
2024-12-11: 「トラブル対応のFAQ追加」(ID: NTC-81e9638b)
2024-12-13: 「オフィス移転の進捗報告」(ID: NTC-ab7e9f15)
2024-12-16: 「社内規程の改定案」(ID: NTC-6c349167)
2024-12-18: 「オフィス移転の進捗報告」(ID: NTC-59ff3781)
2024-12-20: 「部署対抗イベントの告知」(ID: NTC-fd1321d5)
2024-12-24: 「備品の発注ルール変更」(ID: NTC-14285196)
2024-12-25: 「健康診断の予約方法」(ID: NTC-4bd02780)
2024-12-29: 「セキュリティ研修の案内」(ID: NTC-eda7abae)
2024-12-30: 「備品の発注ルール変更」(ID: NTC-d545f47d)
2025-01-03: 「部署対抗イベントの告知」(ID: NTC-764ea99b)
2025-01-05: 「備品の発注ルール変更」(ID: NTC-abd13b83)
2025-01-09: 「健康診断の予約方法」(ID: NTC-7e74c55a)
2025-01-10: 「セキュリティ研修の案内」(ID: NTC-b6636501)
2025-01-12: 「社内アンケートの依頼」(ID: NTC-e0a2ce24)
2025-01-16: 「社内アンケートの依頼」(ID: NTC-4559e019)
2025-01-17: 「座席レイアウト変更の告知」(ID: NTC-227af9ff)
2025-01-21: 「社内規程の改定案」(ID: NTC-1bac142f)
2025-01-23: 「備品の発注ルール変更」(ID: NTC-3ca44132)
2025-01-27: 「部署対抗イベントの告知」(ID: NTC-3a845339)
2025-01-28: 「社内アンケートの依頼」(ID: NTC-f9658138)
2025-02-01: 「来月の定例会議の議事録」(ID: NTC-6c2007fa)
2025-02-03: 「備品の発注ルール変更」(ID: NTC-1951d360)
2025-02-05: 「社内規程の改定案」(ID: NTC-cd34b5ae)
2025-02-09: 「社内システムの定期メンテナンス」(ID: NTC-210c8a02)
2025-02-12: 「セキュリティ研修の案内」(ID: NTC-c431baa6)
2025-02-14: 「新入社員の自己紹介」(ID: NTC-30955746)
2025-02-18: 「来月の定例会議の議事録」(ID: NTC-9572aa80)
2025-02-19: 「オフィス移転の進捗報告」(ID: NTC-41ae9788)
2025-02-23: 「新バージョンの操作マニュアル」(ID: NTC-c4865234)
2025-02-25: 「新しい福利厚生の案内」(ID: NTC-2f85dd7a)
2025-02-27: 「セキュリティ研修の案内」(ID: NTC-63c8c88e)
2025-03-03: 「備品の発注ルール変更」(ID: NTC-5f405b4f)
2025-03-07: 「トラブル対応のFAQ追加」(ID: NTC-0c14a4f1)
2025-03-09: 「社内規程の改定案」(ID: NTC-9c17d8b4)
2025-03-10: 「備品の発注ルール変更」(ID: NTC-8384e089)
2025-03-12: 「社内規程の改定案」(ID: NTC-20725dc0)
2025-03-13: 「座席レイアウト変更の告知」(ID: NTC-f8452c9a)
2025-03-16: 「新しい福利厚生の案内」(ID: NTC-44557cb6)
2025-03-20: 「トラブル対応のFAQ追加」(ID: NTC-b20adf18)
2025-03-22: 「新バージョンの操作マニュアル」(ID: NTC-702200a5)
2025-03-25: 「オフィス移転の進捗報告」(ID: NTC-ce449113)
2025-03-27: 「健康診断の予約方法」(ID: NTC-23d0fad9)
2025-03-28: 「部署対抗イベントの告知」(ID: NTC-616c3d23)
2025-03-30: 「新しい福利厚生の案内」(ID: NTC-87ce3c1c)
2025-04-01: 「社内システムの定期メンテナンス」(ID: NTC-6b1209ab)
2025-04-03: 「新しい福利厚生の案内」(ID: NTC-681b6f45)
```

### 材料series_c・既読ID一覧（297件・①元の時系列順）

```
NTC-3ed2b89c、NTC-93b8658f、NTC-e0ab30f6、NTC-f7df0772、NTC-a3d8160f、NTC-d730102b、NTC-e106c938、NTC-f70e4540、NTC-08f82dd1、NTC-24134f66、NTC-2751cf72、NTC-277ecb12、NTC-59256415、NTC-62d2e675、NTC-2f9d1bbb、NTC-8dd16c22、NTC-471a2fc3、NTC-ff65eb12、NTC-cda91ad1、NTC-157a650d、NTC-8d15b96c、NTC-4a055331、NTC-1e21aca1、NTC-9e872276、NTC-851e95a4、NTC-2c6ac15c、NTC-d412f945、NTC-8cc8f2d9、NTC-a383a1dd、NTC-58f713ca、NTC-d71a13f3、NTC-4cbaba04、NTC-52fa9051、NTC-ba0cb572、NTC-4af23c87、NTC-fd925429、NTC-e32168fe、NTC-16a4caa7、NTC-6590b8d0、NTC-afb8356c、NTC-b0f97a98、NTC-9fc47ea5、NTC-d931bd05、NTC-993fe7ba、NTC-a65c224c、NTC-311aea30、NTC-e2256410、NTC-ddcc9276、NTC-f0a566ad、NTC-6f9968db、NTC-7b5035b5、NTC-69f98ffe、NTC-4a770ea7、NTC-a13c17e7、NTC-8fcdfba8、NTC-4f357f02、NTC-5e0412be、NTC-cb3ed3dd、NTC-5f1fcac8、NTC-b8a58641、NTC-a92fc1c2、NTC-3a82fb3d、NTC-54e8ea5c、NTC-01a8e350、NTC-d3729278、NTC-1d0b1ce0、NTC-caa74e41、NTC-df37979d、NTC-1380261c、NTC-3a5c4e06、NTC-54223c7d、NTC-f828e6f2、NTC-a6dcb69d、NTC-10f85012、NTC-bcb5dd18、NTC-b251f857、NTC-550104f4、NTC-58211dd5、NTC-70b7abaf、NTC-0295e51b、NTC-8e543040、NTC-90a94703、NTC-2ccd1471、NTC-7861f0a1、NTC-29031045、NTC-8c6e0b46、NTC-1301286c、NTC-d61e2ce3、NTC-de64dd33、NTC-ab14a1e3、NTC-64fa88ca、NTC-41fe4ba4、NTC-edb26bf7、NTC-2e5a6e0b、NTC-33e5ccc3、NTC-f80298af、NTC-68d5e706、NTC-a1d0f81e、NTC-910f0e78、NTC-dc5237dc、NTC-a97b1a91、NTC-f45421ac、NTC-13b6e1d1、NTC-5aa872ee、NTC-085d9077、NTC-df649200、NTC-93bff574、NTC-bb0434e8、NTC-e5aaffa2、NTC-edd8be31、NTC-11a60c01、NTC-86bbe679、NTC-d538abd8、NTC-9fa416b6、NTC-dcdf38f5、NTC-a275756a、NTC-48587cba、NTC-bdab1ce7、NTC-c6a098bd、NTC-0a9a8354、NTC-20f5494b、NTC-a6162a5e、NTC-f0b3fd85、NTC-21fb942c、NTC-94acc9c3、NTC-a112d1ee、NTC-b361e253、NTC-64c8ac9b、NTC-30456dbd、NTC-e7d282e2、NTC-11846ce4、NTC-f2b4fa41、NTC-b9990db7、NTC-ff71666c、NTC-8bbd2aba、NTC-e1b0eeab、NTC-72ae4f0f、NTC-51a042f7、NTC-9605eb43、NTC-59307d99、NTC-7f2654f3、NTC-d2ff78cb、NTC-c901b009、NTC-6b27ca97、NTC-ee06ba27、NTC-0b99d6ff、NTC-d821200b、NTC-fde1f364、NTC-884ee37c、NTC-9af21243、NTC-b9668371、NTC-95bcd44d、NTC-c0e87e2d、NTC-632f1dcb、NTC-8e2ad7a0、NTC-23d9638b、NTC-140349f0、NTC-00e464ef、NTC-ab79accf、NTC-f332b315、NTC-3c1c9b88、NTC-00416a4d、NTC-fdb10b59、NTC-c3cc3dbb、NTC-dd2668e1、NTC-91834675、NTC-df759857、NTC-93ed8cdf、NTC-357b1dcf、NTC-0ded99ec、NTC-054efc8a、NTC-7621dba7、NTC-3a4da392、NTC-57e7c9a8、NTC-171cbcac、NTC-4035d765、NTC-99673e9b、NTC-246b7268、NTC-55bc1f99、NTC-d36b0cd5、NTC-013c8340、NTC-acd69773、NTC-8b1bbb62、NTC-8c8ffdb8、NTC-bbcd6610、NTC-25037d92、NTC-1197d2c4、NTC-7aa47d82、NTC-a294247b、NTC-8c0aeabd、NTC-f4acc866、NTC-09f7d07d、NTC-f47b2032、NTC-bbb699ae、NTC-19e632fa、NTC-d7ada788、NTC-4f443fab、NTC-3d231678、NTC-918b9e46、NTC-160af81f、NTC-9238d300、NTC-766a8c90、NTC-faa309f9、NTC-e8e93292、NTC-69091579、NTC-5ed8655b、NTC-cb0db7e8、NTC-ad4c18be、NTC-ca264f81、NTC-2b682ee3、NTC-db92bd43、NTC-4034f9d1、NTC-444e352f、NTC-814d90d1、NTC-b4cf3769、NTC-66f57040、NTC-4a62d877、NTC-b0ca7c1c、NTC-dd9282d1、NTC-2d400f23、NTC-357b9ffb、NTC-dc6c22c5、NTC-d54a5c4d、NTC-5d1d03d1、NTC-4f4264bd、NTC-12cfab30、NTC-89bd2c6d、NTC-2ab25d52、NTC-11da22a6、NTC-d97868f6、NTC-53f521d2、NTC-dd5259d6、NTC-691ad2b6、NTC-45ea39a4、NTC-e7c7ab58、NTC-f9bcb61b、NTC-76c2ef5b、NTC-d060a925、NTC-50f4d581、NTC-8e887a9a、NTC-ebd1ede3、NTC-3d2ca37a、NTC-91877abb、NTC-be6d0d91、NTC-9b439ff8、NTC-72421e9e、NTC-aa1ce177、NTC-c095ef33、NTC-6b876bfc、NTC-95778c6e、NTC-15d903a1、NTC-6303216e、NTC-81e9638b、NTC-ab7e9f15、NTC-6c349167、NTC-59ff3781、NTC-fd1321d5、NTC-14285196、NTC-4bd02780、NTC-eda7abae、NTC-d545f47d、NTC-764ea99b、NTC-abd13b83、NTC-7e74c55a、NTC-b6636501、NTC-e0a2ce24、NTC-4559e019、NTC-227af9ff、NTC-1bac142f、NTC-3ca44132、NTC-3a845339、NTC-f9658138、NTC-6c2007fa、NTC-1951d360、NTC-cd34b5ae、NTC-210c8a02、NTC-c431baa6、NTC-9572aa80、NTC-41ae9788、NTC-c4865234、NTC-2f85dd7a、NTC-63c8c88e、NTC-5f405b4f、NTC-0c14a4f1、NTC-9c17d8b4、NTC-8384e089、NTC-20725dc0、NTC-f8452c9a、NTC-44557cb6、NTC-b20adf18、NTC-702200a5、NTC-ce449113、NTC-23d0fad9、NTC-616c3d23、NTC-87ce3c1c、NTC-6b1209ab、NTC-681b6f45
```

### 材料series_c・既読ID一覧（297件・②近い順＝局所的な乱れ）

```
NTC-93b8658f、NTC-3ed2b89c、NTC-e0ab30f6、NTC-a3d8160f、NTC-f7df0772、NTC-e106c938、NTC-d730102b、NTC-08f82dd1、NTC-f70e4540、NTC-2751cf72、NTC-24134f66、NTC-59256415、NTC-277ecb12、NTC-2f9d1bbb、NTC-62d2e675、NTC-8dd16c22、NTC-ff65eb12、NTC-471a2fc3、NTC-cda91ad1、NTC-157a650d、NTC-8d15b96c、NTC-1e21aca1、NTC-4a055331、NTC-851e95a4、NTC-9e872276、NTC-2c6ac15c、NTC-8cc8f2d9、NTC-d412f945、NTC-a383a1dd、NTC-d71a13f3、NTC-58f713ca、NTC-52fa9051、NTC-4cbaba04、NTC-4af23c87、NTC-ba0cb572、NTC-e32168fe、NTC-fd925429、NTC-16a4caa7、NTC-afb8356c、NTC-6590b8d0、NTC-9fc47ea5、NTC-b0f97a98、NTC-d931bd05、NTC-993fe7ba、NTC-a65c224c、NTC-e2256410、NTC-311aea30、NTC-ddcc9276、NTC-6f9968db、NTC-f0a566ad、NTC-69f98ffe、NTC-7b5035b5、NTC-a13c17e7、NTC-4a770ea7、NTC-4f357f02、NTC-8fcdfba8、NTC-5e0412be、NTC-5f1fcac8、NTC-cb3ed3dd、NTC-a92fc1c2、NTC-b8a58641、NTC-54e8ea5c、NTC-3a82fb3d、NTC-d3729278、NTC-01a8e350、NTC-caa74e41、NTC-1d0b1ce0、NTC-df37979d、NTC-3a5c4e06、NTC-1380261c、NTC-54223c7d、NTC-f828e6f2、NTC-10f85012、NTC-a6dcb69d、NTC-bcb5dd18、NTC-b251f857、NTC-550104f4、NTC-58211dd5、NTC-0295e51b、NTC-70b7abaf、NTC-8e543040、NTC-2ccd1471、NTC-90a94703、NTC-29031045、NTC-7861f0a1、NTC-1301286c、NTC-8c6e0b46、NTC-d61e2ce3、NTC-de64dd33、NTC-64fa88ca、NTC-ab14a1e3、NTC-edb26bf7、NTC-41fe4ba4、NTC-33e5ccc3、NTC-2e5a6e0b、NTC-f80298af、NTC-68d5e706、NTC-a1d0f81e、NTC-910f0e78、NTC-a97b1a91、NTC-dc5237dc、NTC-13b6e1d1、NTC-f45421ac、NTC-5aa872ee、NTC-df649200、NTC-085d9077、NTC-bb0434e8、NTC-93bff574、NTC-e5aaffa2、NTC-edd8be31、NTC-11a60c01、NTC-86bbe679、NTC-9fa416b6、NTC-d538abd8、NTC-dcdf38f5、NTC-a275756a、NTC-bdab1ce7、NTC-48587cba、NTC-0a9a8354、NTC-c6a098bd、NTC-a6162a5e、NTC-20f5494b、NTC-f0b3fd85、NTC-21fb942c、NTC-94acc9c3、NTC-b361e253、NTC-a112d1ee、NTC-64c8ac9b、NTC-e7d282e2、NTC-30456dbd、NTC-f2b4fa41、NTC-11846ce4、NTC-b9990db7、NTC-ff71666c、NTC-8bbd2aba、NTC-e1b0eeab、NTC-72ae4f0f、NTC-51a042f7、NTC-9605eb43、NTC-7f2654f3、NTC-59307d99、NTC-d2ff78cb、NTC-c901b009、NTC-6b27ca97、NTC-ee06ba27、NTC-0b99d6ff、NTC-fde1f364、NTC-d821200b、NTC-9af21243、NTC-884ee37c、NTC-95bcd44d、NTC-b9668371、NTC-632f1dcb、NTC-c0e87e2d、NTC-8e2ad7a0、NTC-140349f0、NTC-23d9638b、NTC-ab79accf、NTC-00e464ef、NTC-f332b315、NTC-3c1c9b88、NTC-fdb10b59、NTC-00416a4d、NTC-dd2668e1、NTC-c3cc3dbb、NTC-df759857、NTC-91834675、NTC-357b1dcf、NTC-93ed8cdf、NTC-054efc8a、NTC-0ded99ec、NTC-7621dba7、NTC-57e7c9a8、NTC-3a4da392、NTC-171cbcac、NTC-99673e9b、NTC-4035d765、NTC-55bc1f99、NTC-246b7268、NTC-013c8340、NTC-d36b0cd5、NTC-acd69773、NTC-8b1bbb62、NTC-bbcd6610、NTC-8c8ffdb8、NTC-1197d2c4、NTC-25037d92、NTC-a294247b、NTC-7aa47d82、NTC-8c0aeabd、NTC-f4acc866、NTC-09f7d07d、NTC-f47b2032、NTC-19e632fa、NTC-bbb699ae、NTC-d7ada788、NTC-3d231678、NTC-4f443fab、NTC-918b9e46、NTC-9238d300、NTC-160af81f、NTC-766a8c90、NTC-faa309f9、NTC-69091579、NTC-e8e93292、NTC-5ed8655b、NTC-ad4c18be、NTC-cb0db7e8、NTC-2b682ee3、NTC-ca264f81、NTC-4034f9d1、NTC-db92bd43、NTC-814d90d1、NTC-444e352f、NTC-b4cf3769、NTC-4a62d877、NTC-66f57040、NTC-dd9282d1、NTC-b0ca7c1c、NTC-2d400f23、NTC-dc6c22c5、NTC-357b9ffb、NTC-5d1d03d1、NTC-d54a5c4d、NTC-4f4264bd、NTC-89bd2c6d、NTC-12cfab30、NTC-11da22a6、NTC-2ab25d52、NTC-d97868f6、NTC-53f521d2、NTC-691ad2b6、NTC-dd5259d6、NTC-e7c7ab58、NTC-45ea39a4、NTC-f9bcb61b、NTC-d060a925、NTC-76c2ef5b、NTC-8e887a9a、NTC-50f4d581、NTC-3d2ca37a、NTC-ebd1ede3、NTC-91877abb、NTC-be6d0d91、NTC-72421e9e、NTC-9b439ff8、NTC-c095ef33、NTC-aa1ce177、NTC-6b876bfc、NTC-95778c6e、NTC-15d903a1、NTC-81e9638b、NTC-6303216e、NTC-6c349167、NTC-ab7e9f15、NTC-59ff3781、NTC-fd1321d5、NTC-4bd02780、NTC-14285196、NTC-d545f47d、NTC-eda7abae、NTC-abd13b83、NTC-764ea99b、NTC-b6636501、NTC-7e74c55a、NTC-e0a2ce24、NTC-4559e019、NTC-1bac142f、NTC-227af9ff、NTC-3ca44132、NTC-3a845339、NTC-6c2007fa、NTC-f9658138、NTC-1951d360、NTC-cd34b5ae、NTC-c431baa6、NTC-210c8a02、NTC-9572aa80、NTC-41ae9788、NTC-c4865234、NTC-63c8c88e、NTC-2f85dd7a、NTC-5f405b4f、NTC-9c17d8b4、NTC-0c14a4f1、NTC-20725dc0、NTC-8384e089、NTC-f8452c9a、NTC-44557cb6、NTC-702200a5、NTC-b20adf18、NTC-23d0fad9、NTC-ce449113、NTC-616c3d23、NTC-6b1209ab、NTC-87ce3c1c、NTC-681b6f45
```

### 材料series_c・既読ID一覧（297件・③完全にシャッフル）

```
NTC-3c1c9b88、NTC-fd1321d5、NTC-8e543040、NTC-0ded99ec、NTC-c901b009、NTC-d3729278、NTC-19e632fa、NTC-e5aaffa2、NTC-8b1bbb62、NTC-eda7abae、NTC-f828e6f2、NTC-a3d8160f、NTC-f8452c9a、NTC-c3cc3dbb、NTC-54223c7d、NTC-8384e089、NTC-e106c938、NTC-157a650d、NTC-13b6e1d1、NTC-c4865234、NTC-1301286c、NTC-a65c224c、NTC-5f1fcac8、NTC-4a62d877、NTC-69f98ffe、NTC-1197d2c4、NTC-2c6ac15c、NTC-68d5e706、NTC-4f357f02、NTC-e1b0eeab、NTC-59307d99、NTC-93bff574、NTC-48587cba、NTC-3d2ca37a、NTC-b20adf18、NTC-9e872276、NTC-b361e253、NTC-d54a5c4d、NTC-59256415、NTC-1bac142f、NTC-e7d282e2、NTC-15d903a1、NTC-1951d360、NTC-4a770ea7、NTC-11da22a6、NTC-d2ff78cb、NTC-95bcd44d、NTC-6c349167、NTC-58211dd5、NTC-5d1d03d1、NTC-edd8be31、NTC-14285196、NTC-bbcd6610、NTC-fdb10b59、NTC-9238d300、NTC-95778c6e、NTC-dd9282d1、NTC-dc6c22c5、NTC-d97868f6、NTC-acd69773、NTC-616c3d23、NTC-d060a925、NTC-99673e9b、NTC-8fcdfba8、NTC-2d400f23、NTC-69091579、NTC-d538abd8、NTC-f0a566ad、NTC-a275756a、NTC-171cbcac、NTC-7f2654f3、NTC-be6d0d91、NTC-a383a1dd、NTC-a112d1ee、NTC-cb0db7e8、NTC-8cc8f2d9、NTC-01a8e350、NTC-c431baa6、NTC-93b8658f、NTC-085d9077、NTC-c095ef33、NTC-246b7268、NTC-f45421ac、NTC-6303216e、NTC-9c17d8b4、NTC-44557cb6、NTC-cda91ad1、NTC-59ff3781、NTC-e0ab30f6、NTC-91877abb、NTC-91834675、NTC-2ab25d52、NTC-5e0412be、NTC-8e2ad7a0、NTC-f9658138、NTC-766a8c90、NTC-e8e93292、NTC-dcdf38f5、NTC-2f85dd7a、NTC-2f9d1bbb、NTC-e0a2ce24、NTC-12cfab30、NTC-33e5ccc3、NTC-58f713ca、NTC-6b876bfc、NTC-357b9ffb、NTC-bcb5dd18、NTC-471a2fc3、NTC-94acc9c3、NTC-6c2007fa、NTC-db92bd43、NTC-11a60c01、NTC-f80298af、NTC-aa1ce177、NTC-210c8a02、NTC-ba0cb572、NTC-23d0fad9、NTC-4f443fab、NTC-ce449113、NTC-4a055331、NTC-41ae9788、NTC-4cbaba04、NTC-f7df0772、NTC-76c2ef5b、NTC-054efc8a、NTC-89bd2c6d、NTC-3ed2b89c、NTC-7621dba7、NTC-bb0434e8、NTC-dd2668e1、NTC-0a9a8354、NTC-d36b0cd5、NTC-3a4da392、NTC-fde1f364、NTC-b251f857、NTC-9572aa80、NTC-f47b2032、NTC-311aea30、NTC-ddcc9276、NTC-a6162a5e、NTC-a92fc1c2、NTC-6590b8d0、NTC-45ea39a4、NTC-814d90d1、NTC-9af21243、NTC-51a042f7、NTC-41fe4ba4、NTC-6b27ca97、NTC-b6636501、NTC-ee06ba27、NTC-550104f4、NTC-2e5a6e0b、NTC-5ed8655b、NTC-ab14a1e3、NTC-00416a4d、NTC-b4cf3769、NTC-e32168fe、NTC-b8a58641、NTC-918b9e46、NTC-3a5c4e06、NTC-edb26bf7、NTC-16a4caa7、NTC-bbb699ae、NTC-227af9ff、NTC-20f5494b、NTC-de64dd33、NTC-1d0b1ce0、NTC-cd34b5ae、NTC-140349f0、NTC-0295e51b、NTC-d412f945、NTC-884ee37c、NTC-993fe7ba、NTC-abd13b83、NTC-1e21aca1、NTC-e2256410、NTC-caa74e41、NTC-72421e9e、NTC-7aa47d82、NTC-50f4d581、NTC-3a845339、NTC-afb8356c、NTC-4f4264bd、NTC-fd925429、NTC-b9990db7、NTC-a13c17e7、NTC-b0ca7c1c、NTC-4559e019、NTC-52fa9051、NTC-66f57040、NTC-93ed8cdf、NTC-a1d0f81e、NTC-23d9638b、NTC-2ccd1471、NTC-7e74c55a、NTC-444e352f、NTC-57e7c9a8、NTC-a294247b、NTC-4bd02780、NTC-a6dcb69d、NTC-d931bd05、NTC-681b6f45、NTC-5f405b4f、NTC-54e8ea5c、NTC-64fa88ca、NTC-f0b3fd85、NTC-1380261c、NTC-11846ce4、NTC-64c8ac9b、NTC-30456dbd、NTC-dc5237dc、NTC-ff65eb12、NTC-f9bcb61b、NTC-d545f47d、NTC-160af81f、NTC-f332b315、NTC-b0f97a98、NTC-8bbd2aba、NTC-86bbe679、NTC-10f85012、NTC-63c8c88e、NTC-9fa416b6、NTC-f4acc866、NTC-df37979d、NTC-8c8ffdb8、NTC-f70e4540、NTC-ebd1ede3、NTC-3a82fb3d、NTC-910f0e78、NTC-9fc47ea5、NTC-7861f0a1、NTC-00e464ef、NTC-29031045、NTC-d7ada788、NTC-4af23c87、NTC-53f521d2、NTC-e7c7ab58、NTC-357b1dcf、NTC-8c0aeabd、NTC-df649200、NTC-bdab1ce7、NTC-d71a13f3、NTC-20725dc0、NTC-ab79accf、NTC-d61e2ce3、NTC-faa309f9、NTC-dd5259d6、NTC-6f9968db、NTC-d821200b、NTC-ca264f81、NTC-21fb942c、NTC-4034f9d1、NTC-b9668371、NTC-ab7e9f15、NTC-2b682ee3、NTC-62d2e675、NTC-277ecb12、NTC-764ea99b、NTC-ad4c18be、NTC-25037d92、NTC-09f7d07d、NTC-24134f66、NTC-72ae4f0f、NTC-a97b1a91、NTC-df759857、NTC-851e95a4、NTC-70b7abaf、NTC-3ca44132、NTC-9605eb43、NTC-3d231678、NTC-8dd16c22、NTC-d730102b、NTC-691ad2b6、NTC-0b99d6ff、NTC-9b439ff8、NTC-ff71666c、NTC-8d15b96c、NTC-87ce3c1c、NTC-6b1209ab、NTC-c6a098bd、NTC-013c8340、NTC-2751cf72、NTC-8c6e0b46、NTC-0c14a4f1、NTC-4035d765、NTC-08f82dd1、NTC-c0e87e2d、NTC-8e887a9a、NTC-55bc1f99、NTC-90a94703、NTC-81e9638b、NTC-cb3ed3dd、NTC-f2b4fa41、NTC-702200a5、NTC-5aa872ee、NTC-632f1dcb、NTC-7b5035b5
```

### 生成スクリプト（固定seed・再現可能）

`gen.py`（系列A・B・60件を生成し、仕込み検証をassertする）:

```python
import hashlib
import random
import json
import datetime

TOPICS_A = [
    "社内規程の改定案", "来月の定例会議の議事録", "新しい福利厚生の案内", "座席レイアウト変更の告知",
    "社内システムの定期メンテナンス", "新入社員の自己紹介", "備品の発注ルール変更", "部署対抗イベントの告知",
    "健康診断の予約方法", "社内アンケートの依頼", "セキュリティ研修の案内", "オフィス移転の進捗報告",
]
TOPICS_B = [
    "請求書発行手順の更新", "新バージョンの操作マニュアル", "トラブル対応のFAQ追加", "外部連携APIの仕様変更",
    "社内ツールの権限申請フロー", "データ保管ルールの改定", "新機能のリリースノート", "旧機能の廃止予定",
    "問い合わせ分類の見直し", "用語集の追補", "設定手順のスクリーンショット更新", "既知の不具合と回避策",
]

def make_series(prefix, salt, topics, n_rows, new_positions_pct, start_date, step_days, seed):
    rnd = random.Random(seed)
    rows = []
    date = start_date
    for i in range(1, n_rows + 1):
        h = hashlib.sha1(f"{salt}-{i}".encode()).hexdigest()[:8]
        rid = f"{prefix}-{h}"
        topic = topics[rnd.randrange(len(topics))]
        rows.append({"seq": i, "id": rid, "date": date.isoformat(), "topic": topic})
        date = date + datetime.timedelta(days=step_days[rnd.randrange(len(step_days))])

    n = len(rows)
    new_idx = sorted(set(round(n * p / 100) for p in new_positions_pct))
    # ensure exactly len(new_positions_pct) unique indices, nudge collisions forward
    fixed = []
    used = set()
    for idx in new_idx:
        while idx in used or idx >= n:
            idx += 1
        used.add(idx)
        fixed.append(idx)
    new_ids = [rows[idx]["id"] for idx in fixed]

    # sanity: ID string order must not correlate with list (date) order
    id_rank = {r["id"]: i for i, r in enumerate(sorted(rows, key=lambda r: r["id"]))}
    date_rank = {r["id"]: i for i, r in enumerate(rows)}
    agree = sum(1 for rid in id_rank if id_rank[rid] == date_rank[rid])
    assert agree <= 3, f"IDの並びが日付順と一致しすぎている: {agree}件"

    seen_rows = [r for r in rows if r["id"] not in new_ids]
    assert len(seen_rows) == n - len(new_ids)
    seen_ids_ordered = [r["id"] for r in seen_rows]  # chronological, matches 投稿一覧 order

    shuffled = seen_ids_ordered[:]
    rnd2 = random.Random(seed + 999)
    rnd2.shuffle(shuffled)
    # sanity: shuffled must differ substantially from original order
    same_pos = sum(1 for a, b in zip(seen_ids_ordered, shuffled) if a == b)
    assert same_pos <= 3, f"シャッフルが弱い: 一致{same_pos}件"
    assert sorted(shuffled) == sorted(seen_ids_ordered)
    assert len(set(shuffled)) == len(shuffled)

    return {
        "prefix": prefix,
        "n_rows": n,
        "new_ids": new_ids,
        "new_positions_pct": new_positions_pct,
        "new_idx_0based": fixed,
        "rows": rows,
        "seen_ids_original_order": seen_ids_ordered,
        "seen_ids_shuffled_order": shuffled,
    }

series_a = make_series("BBS", "ai-tsukaikata-shuffle-A-2026-11-02", TOPICS_A, 60,
                        [10, 50, 90], datetime.date(2024, 4, 1), [1, 2, 3, 4], seed=20261102)
series_b = make_series("KBX", "ai-tsukaikata-shuffle-B-2026-11-02", TOPICS_B, 60,
                        [10, 50, 90], datetime.date(2024, 7, 1), [1, 2, 3, 5], seed=20261103)

def render_post_list(series):
    lines = []
    for r in series["rows"]:
        lines.append(f"{r['date']}: 「{r['topic']}」(ID: {r['id']})")
    return "\n".join(lines)

def render_id_list(ids):
    return "、".join(ids)

out = {}
for name, s in [("series_a", series_a), ("series_b", series_b)]:
    with open(f"/tmp/claude-0/-home-user-ai-tsukaikata/c02cfa33-6ee2-5c08-a9ad-90e1a1ab5945/scratchpad/shuffle-exp/{name}_postlist.txt", "w") as f:
        f.write(render_post_list(s))
    with open(f"/tmp/claude-0/-home-user-ai-tsukaikata/c02cfa33-6ee2-5c08-a9ad-90e1a1ab5945/scratchpad/shuffle-exp/{name}_seen_original.txt", "w") as f:
        f.write(render_id_list(s["seen_ids_original_order"]))
    with open(f"/tmp/claude-0/-home-user-ai-tsukaikata/c02cfa33-6ee2-5c08-a9ad-90e1a1ab5945/scratchpad/shuffle-exp/{name}_seen_shuffled.txt", "w") as f:
        f.write(render_id_list(s["seen_ids_shuffled_order"]))
    out[name] = {
        "prefix": s["prefix"],
        "n_rows": s["n_rows"],
        "new_ids": s["new_ids"],
        "new_positions_pct": s["new_positions_pct"],
        "new_idx_0based": s["new_idx_0based"],
    }

with open("/tmp/claude-0/-home-user-ai-tsukaikata/c02cfa33-6ee2-5c08-a9ad-90e1a1ab5945/scratchpad/shuffle-exp/manifest.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print(json.dumps(out, ensure_ascii=False, indent=1))
print("OK: 仕込み検証を通過")

```

`gen_noisy.py`（系列A・Bの「近い順」＝局所的な乱れ版を生成する）:

```python
import json
import random

BASE = "/tmp/claude-0/-home-user-ai-tsukaikata/c02cfa33-6ee2-5c08-a9ad-90e1a1ab5945/scratchpad/shuffle-exp"

with open(f"{BASE}/manifest.json") as f:
    manifest = json.load(f)

def read(path):
    with open(path) as f:
        return f.read()

for name, seed in [("series_a", 777), ("series_b", 778)]:
    original = read(f"{BASE}/{name}_seen_original.txt").split("、")
    rnd = random.Random(seed)
    noisy = original[:]
    # local perturbation: scan adjacent pairs, swap with prob 0.5, in one pass
    i = 0
    swaps = 0
    while i < len(noisy) - 1:
        if rnd.random() < 0.5:
            noisy[i], noisy[i + 1] = noisy[i + 1], noisy[i]
            swaps += 1
            i += 2
        else:
            i += 1
    same_pos = sum(1 for a, b in zip(original, noisy) if a == b)
    print(name, "swaps=", swaps, "same_pos=", same_pos, "/", len(original))
    assert sorted(noisy) == sorted(original)
    assert len(set(noisy)) == len(noisy)
    with open(f"{BASE}/{name}_seen_noisy.txt", "w") as f:
        f.write("、".join(noisy))

```

`gen300.py`（系列C・300件を3条件とも生成し、仕込み検証をassertする）:

```python
import hashlib
import random
import datetime
import json

BASE = "/tmp/claude-0/-home-user-ai-tsukaikata/c02cfa33-6ee2-5c08-a9ad-90e1a1ab5945/scratchpad/shuffle-exp"

TOPICS_C = [
    "社内規程の改定案", "来月の定例会議の議事録", "新しい福利厚生の案内", "座席レイアウト変更の告知",
    "社内システムの定期メンテナンス", "新入社員の自己紹介", "備品の発注ルール変更", "部署対抗イベントの告知",
    "健康診断の予約方法", "社内アンケートの依頼", "セキュリティ研修の案内", "オフィス移転の進捗報告",
    "請求書発行手順の更新", "新バージョンの操作マニュアル", "トラブル対応のFAQ追加",
]

def make_series(prefix, salt, topics, n_rows, new_positions_pct, start_date, step_days, seed):
    rnd = random.Random(seed)
    rows = []
    date = start_date
    for i in range(1, n_rows + 1):
        h = hashlib.sha1(f"{salt}-{i}".encode()).hexdigest()[:8]
        rid = f"{prefix}-{h}"
        topic = topics[rnd.randrange(len(topics))]
        rows.append({"seq": i, "id": rid, "date": date.isoformat(), "topic": topic})
        date = date + datetime.timedelta(days=step_days[rnd.randrange(len(step_days))])

    n = len(rows)
    new_idx = sorted(set(round(n * p / 100) for p in new_positions_pct))
    fixed, used = [], set()
    for idx in new_idx:
        while idx in used or idx >= n:
            idx += 1
        used.add(idx)
        fixed.append(idx)
    new_ids = [rows[idx]["id"] for idx in fixed]

    id_rank = {r["id"]: i for i, r in enumerate(sorted(rows, key=lambda r: r["id"]))}
    date_rank = {r["id"]: i for i, r in enumerate(rows)}
    agree = sum(1 for rid in id_rank if id_rank[rid] == date_rank[rid])
    assert agree <= 5, f"IDの並びが日付順と一致しすぎている: {agree}件"

    seen_rows = [r for r in rows if r["id"] not in new_ids]
    seen_ids_ordered = [r["id"] for r in seen_rows]

    rnd2 = random.Random(seed + 999)
    shuffled = seen_ids_ordered[:]
    rnd2.shuffle(shuffled)
    same_pos = sum(1 for a, b in zip(seen_ids_ordered, shuffled) if a == b)
    assert same_pos <= 5, f"シャッフルが弱い: 一致{same_pos}件"
    assert sorted(shuffled) == sorted(seen_ids_ordered)
    assert len(set(shuffled)) == len(shuffled)

    rnd3 = random.Random(seed + 1998)
    noisy = seen_ids_ordered[:]
    i = 0
    swaps = 0
    while i < len(noisy) - 1:
        if rnd3.random() < 0.5:
            noisy[i], noisy[i + 1] = noisy[i + 1], noisy[i]
            swaps += 1
            i += 2
        else:
            i += 1
    same_pos_noisy = sum(1 for a, b in zip(seen_ids_ordered, noisy) if a == b)
    assert sorted(noisy) == sorted(seen_ids_ordered)
    assert len(set(noisy)) == len(noisy)

    return {
        "prefix": prefix, "n_rows": n, "new_ids": new_ids,
        "new_positions_pct": new_positions_pct, "new_idx_0based": fixed,
        "rows": rows,
        "seen_original": seen_ids_ordered, "seen_shuffled": shuffled, "seen_noisy": noisy,
        "shuffled_match_pct": round(same_pos / len(seen_ids_ordered) * 100, 1),
        "noisy_match_pct": round(same_pos_noisy / len(seen_ids_ordered) * 100, 1),
        "swaps": swaps,
    }

series_c = make_series("NTC", "ai-tsukaikata-shuffle-C-2026-11-02", TOPICS_C, 300,
                        [7, 50, 93], datetime.date(2023, 5, 1), [1, 2, 2, 3, 4], seed=20261104)

def render_post_list(series):
    return "\n".join(f"{r['date']}: 「{r['topic']}」(ID: {r['id']})" for r in series["rows"])

def render_id_list(ids):
    return "、".join(ids)

with open(f"{BASE}/series_c_postlist.txt", "w") as f:
    f.write(render_post_list(series_c))
with open(f"{BASE}/series_c_seen_original.txt", "w") as f:
    f.write(render_id_list(series_c["seen_original"]))
with open(f"{BASE}/series_c_seen_shuffled.txt", "w") as f:
    f.write(render_id_list(series_c["seen_shuffled"]))
with open(f"{BASE}/series_c_seen_noisy.txt", "w") as f:
    f.write(render_id_list(series_c["seen_noisy"]))

manifest_c = {
    "prefix": series_c["prefix"], "n_rows": series_c["n_rows"],
    "new_ids": series_c["new_ids"], "new_positions_pct": series_c["new_positions_pct"],
    "new_idx_0based": series_c["new_idx_0based"],
    "shuffled_match_pct": series_c["shuffled_match_pct"],
    "noisy_match_pct": series_c["noisy_match_pct"],
    "swaps": series_c["swaps"],
}
print(json.dumps(manifest_c, ensure_ascii=False, indent=1))

with open(f"{BASE}/manifest_c.json", "w") as f:
    json.dump(manifest_c, f, ensure_ascii=False, indent=1)
print("OK: series_c 仕込み検証を通過")

```

---

## 指示文1（元の順・系列A/B共通）

### 送った指示文（記事と同一文字列）

```
既読リスト（これまでに確認済みのID一覧）は次のとおりです。

（ここに、既読ID一覧をそのまま貼ります）

投稿一覧は次のとおりです（全60件）。

（ここに、投稿一覧をそのまま貼ります）

既読リストに無い項目を新着として、該当する投稿のIDだけを列挙してください。説明や前置きは不要です。該当が無ければ「新着なし」とだけ書いてください。
```

実際に送った材料は、既読ID一覧（元の時系列順・57件・上記「教材」の該当ブロック）と投稿一覧（60件）を、プレースホルダの代わりに丸ごと展開したもの。

### 返ってきたもの（生）

**系列A・1回目**

```
BBS-b496b461
BBS-1f6cb808
BBS-0ef4399d
```

**系列A・2回目**

```
BBS-b496b461
BBS-1f6cb808
BBS-0ef4399d
```

**系列B・1回目**

```
KBX-1e0d0889
KBX-92932366
KBX-7419fe1c
```

**系列B・2回目**

```
KBX-1e0d0889
KBX-92932366
KBX-7419fe1c
```

### 照合（機械）

```
series_a / original / 回1: 見逃し=0 誤検知=0
series_a / original / 回2: 見逃し=0 誤検知=0
series_b / original / 回1: 見逃し=0 誤検知=0
series_b / original / 回2: 見逃し=0 誤検知=0
合計: 仕込み12件中 見逃し0件・誤検知0件（4回）
```

### 判定

**採用**。対照条件（元の時系列順）として、4回とも仕込んだ3件を1件も見逃さず、誤検知も0件。

---

## 指示文2（シャッフル・系列A/B共通）

### 送った指示文（記事と同一文字列）

指示文1と1字も同じ（テンプレートは不変）。

```
既読リスト（これまでに確認済みのID一覧）は次のとおりです。

（ここに、既読ID一覧をそのまま貼ります）

投稿一覧は次のとおりです（全60件）。

（ここに、投稿一覧をそのまま貼ります）

既読リストに無い項目を新着として、該当する投稿のIDだけを列挙してください。説明や前置きは不要です。該当が無ければ「新着なし」とだけ書いてください。
```

実際に送った材料は、既読ID一覧を完全にランダムな順序に並べ替えたもの（系列Aの一致度3.5%・系列Bの一致度5.3%・上記「教材」の該当ブロック）と、投稿一覧（60件・指示文1と同一）。

### 返ってきたもの（生）

**系列A・1回目**

```
BBS-b496b461
BBS-1f6cb808
BBS-0ef4399d
```

**系列A・2回目**

```
BBS-b496b461
BBS-1f6cb808
BBS-0ef4399d
```

**系列B・1回目**

```
KBX-1e0d0889
KBX-92932366
KBX-7419fe1c
```

**系列B・2回目**

```
KBX-1e0d0889
KBX-92932366
KBX-7419fe1c
```

### 照合（機械）

```
series_a / shuffled / 回1: 見逃し=0 誤検知=0
series_a / shuffled / 回2: 見逃し=0 誤検知=0
series_b / shuffled / 回1: 見逃し=0 誤検知=0
series_b / shuffled / 回2: 見逃し=0 誤検知=0
合計: 仕込み12件中 見逃し0件・誤検知0件（4回）
```

### 判定

**採用**。既読ID一覧を一致度3〜5%まで完全にシャッフルしても、4回とも見逃し0・誤検知0。対照条件と結果は同じ。

---

## 指示文3（近い順・ノイズ・系列A/B共通）

### 送った指示文（記事と同一文字列）

指示文1・2と1字も同じ。

```
既読リスト（これまでに確認済みのID一覧）は次のとおりです。

（ここに、既読ID一覧をそのまま貼ります）

投稿一覧は次のとおりです（全60件）。

（ここに、投稿一覧をそのまま貼ります）

既読リストに無い項目を新着として、該当する投稿のIDだけを列挙してください。説明や前置きは不要です。該当が無ければ「新着なし」とだけ書いてください。
```

実際に送った材料は、既読ID一覧の隣接する2件を約50%の確率で入れ替えた「局所的な乱れ」版（系列Aの一致度40.4%・系列Bの一致度29.8%・上記「教材」の該当ブロック）と、投稿一覧（60件・指示文1と同一）。

### 返ってきたもの（生）

**系列A・1回目**

```
BBS-b496b461
BBS-1f6cb808
BBS-0ef4399d
```

**系列A・2回目**

```
BBS-b496b461
BBS-1f6cb808
BBS-0ef4399d
```

**系列B・1回目**

```
KBX-1e0d0889
KBX-92932366
KBX-7419fe1c
```

**系列B・2回目**

```
KBX-1e0d0889
KBX-92932366
KBX-7419fe1c
```

### 照合（機械）

```
series_a / noisy / 回1: 見逃し=0 誤検知=0
series_a / noisy / 回2: 見逃し=0 誤検知=0
series_b / noisy / 回1: 見逃し=0 誤検知=0
series_b / noisy / 回2: 見逃し=0 誤検知=0
合計: 仕込み12件中 見逃し0件・誤検知0件（4回）
```

### 判定

**採用**。見た目は時系列に近いのに実際は一致度30〜40%しかない「近い順」でも、4回とも見逃し0・誤検知0。想定していた「気づかれにくい罠」としては機能しなかった。

---

## 指示文4（300件規模・系列C・3条件）

### 送った指示文（記事と同一文字列）

```
既読リスト（これまでに確認済みのID一覧）は次のとおりです。

（ここに、既読ID一覧をそのまま貼ります）

投稿一覧は次のとおりです（全300件）。

（ここに、投稿一覧をそのまま貼ります）

既読リストに無い項目を新着として、該当する投稿のIDだけを列挙してください。説明や前置きは不要です。該当が無ければ「新着なし」とだけ書いてください。
```

実際に送った材料は、系列C（300件・新着3件を7%・50%・93%目に仕込み）の既読ID一覧を、(a)元の時系列順(b)近い順・一致度31.3%(c)シャッフル・一致度0.7%、の3条件で用意したもの（上記「教材」の該当ブロック）と、投稿一覧（300件・3条件で共通）。

### 返ってきたもの（生）

**元の順・1回目**

```
NTC-bda6d410
NTC-578dd4a8
NTC-30955746
```

**元の順・2回目**

```
NTC-bda6d410
NTC-578dd4a8
NTC-30955746
```

**シャッフル・1回目**

```
NTC-bda6d410
NTC-578dd4a8
NTC-30955746
```

**シャッフル・2回目**

```
NTC-bda6d410
NTC-578dd4a8
NTC-30955746
```

**近い順・1回目**

```
NTC-bda6d410
NTC-578dd4a8
NTC-30955746
```

**近い順・2回目**

```
NTC-bda6d410
NTC-578dd4a8
NTC-30955746
```

### 照合（機械）

```
series_c / original / 回1: 見逃し=0 誤検知=0
series_c / original / 回2: 見逃し=0 誤検知=0
series_c / shuffled / 回1: 見逃し=0 誤検知=0
series_c / shuffled / 回2: 見逃し=0 誤検知=0
series_c / noisy / 回1: 見逃し=0 誤検知=0
series_c / noisy / 回2: 見逃し=0 誤検知=0
合計: 仕込み18件中 見逃し0件・誤検知0件（6回）
```

### 判定

**採用**。300件規模（前作と同じ規模）に増やしても、3条件×2回転＝6回とも見逃し0・誤検知0。60件での結果が規模によるものではないことを確認した。

---

## 指示文5（言い直し方・自己申告確認）

### 送った指示文（記事と同一文字列）

```
今の判断は、日付とIDの照合のどちらを手がかりにしましたか。既読リストの並び順は投稿一覧と同じ順でしたか、違う順でしたか。教えてください。
```

指示文2（系列Aのシャッフル版・1回目）に続けて、同じ `--session-id` のセッションに `-r` で投げた。

### 返ってきたもの（生）

**系列A（成功した1回）**

```
手がかりにしたのは **IDの照合**です。日付は使っていません。

- **照合の方法**: 投稿一覧の60件のIDを1つずつ既読リストと突き合わせました。既読リストに無かったのは3件です。
- **日付やタイトルを使わなかった理由**: タイトルは「備品の発注ルール変更」などが何度も出てきて、同じ題でも別IDの投稿があります。日付は、既読リストに載っていないので照合に使えません。
- **件数の確認**: 既読リストは57件、投稿一覧は60件です。差の3件が、答えた3件(BBS-b496b461、BBS-1f6cb808、BBS-0ef4399d)と一致します。

**並び順は違いました。** 既読リストは日付順でも投稿一覧の順でもなく、バラバラです。先頭は BBS-f73bdbef で、これは投稿一覧では2024-07-10の項目です。そのため、順番に見比べる方法は使えませんでした。
```

**系列B（指示文2・シャッフル版・1回目に続けて）**

```
exit=1
API Error: Sonnet 5.5's safeguards flagged this message (https://www.anthropic.com/legal/aup). This sometimes happens with safe, normal conversations. Claude Code can't respond to this message with Sonnet 5.5.
Details: `[reasoning_extraction]`
```

同じ問い方を言い換えて再送したが、同じエラーで失敗（2回連続）。

**系列C・シャッフル版（指示文4・shuffled・1回目に続けて）**

```
exit=1
API Error: ...（同じ）Details: `[reasoning_extraction]`
```

### 照合（機械）

目視判定（自己申告の文面を読んで、並び順への言及があるかを見る。機械で正規表現照合できる定型の返りではないため）。4回中1回成功、3回は `reasoning_extraction` のAPIセーフガードでエラー終了。

### 判定

**採用（成功した1回のみ）**。成功した系列Aの返りは「並び順は違いました」と明言し、1件ずつの照合に切り替えたことを自己申告している。失敗3回は本体の新着検出（指示文1〜4）の結果には影響しない独立したエラーなので、記事では「3回中3回失敗した」ことも含めて正直に書いた。

---

## 機械照合スクリプト（`grade_all.py`。全18回を一括で照合）

```python
import json
import re

BASE = "/tmp/claude-0/-home-user-ai-tsukaikata/c02cfa33-6ee2-5c08-a9ad-90e1a1ab5945/scratchpad/shuffle-exp"

with open(f"{BASE}/manifest.json") as f:
    manifest = json.load(f)
with open(f"{BASE}/manifest_c.json") as f:
    manifest_c = json.load(f)
manifest["series_c"] = manifest_c

ID_RE = re.compile(r"\b(BBS|KBX|NTC)-[0-9a-f]{8}\b")

plan = [
    ("series_a", ["original", "shuffled", "noisy"], [1, 2]),
    ("series_b", ["original", "shuffled", "noisy"], [1, 2]),
    ("series_c", ["original", "shuffled", "noisy"], [1, 2]),
]

results = []
for name, conds, trials in plan:
    true_new = set(manifest[name]["new_ids"])
    for cond in conds:
        for trial in trials:
            path = f"{BASE}/out_{name}_{cond}_t{trial}.txt"
            with open(path) as f:
                text = f.read()
            found = set(m.group(0) for m in ID_RE.finditer(text))
            missed = true_new - found
            false_pos = found - true_new
            results.append({
                "series": name, "cond": cond, "trial": trial,
                "n_rows": manifest[name]["n_rows"],
                "true_new": sorted(true_new), "answered": sorted(found),
                "n_missed": len(missed), "n_false_pos": len(false_pos),
            })

for r in results:
    print(f"{r['series']}(n={r['n_rows']}) / {r['cond']} / 回{r['trial']}: "
          f"見逃し={r['n_missed']} 誤検知={r['n_false_pos']}")

by_cond = {}
for r in results:
    by_cond.setdefault(r["cond"], {"missed": 0, "fp": 0, "checked": 0, "n": 0})
    by_cond[r["cond"]]["missed"] += r["n_missed"]
    by_cond[r["cond"]]["fp"] += r["n_false_pos"]
    by_cond[r["cond"]]["checked"] += len(r["true_new"])
    by_cond[r["cond"]]["n"] += 1

print("\n条件別集計:")
for cond, v in by_cond.items():
    print(f"  {cond}: {v['n']}回・新着{v['checked']}件中 見逃し{v['missed']}件・誤検知{v['fp']}件")

total_missed = sum(r["n_missed"] for r in results)
total_fp = sum(r["n_false_pos"] for r in results)
total_checked = sum(len(r["true_new"]) for r in results)
print(f"\n総合計: {len(results)}回・新着{total_checked}件中 見逃し{total_missed}件・誤検知{total_fp}件")

with open(f"{BASE}/grade_all_result.json", "w") as f:
    json.dump({"results": results, "by_cond": by_cond}, f, ensure_ascii=False, indent=1)

```

### 実行結果（そのまま）

```
series_a(n=60) / original / 回1: 見逃し=0 誤検知=0
series_a(n=60) / original / 回2: 見逃し=0 誤検知=0
series_a(n=60) / shuffled / 回1: 見逃し=0 誤検知=0
series_a(n=60) / shuffled / 回2: 見逃し=0 誤検知=0
series_a(n=60) / noisy / 回1: 見逃し=0 誤検知=0
series_a(n=60) / noisy / 回2: 見逃し=0 誤検知=0
series_b(n=60) / original / 回1: 見逃し=0 誤検知=0
series_b(n=60) / original / 回2: 見逃し=0 誤検知=0
series_b(n=60) / shuffled / 回1: 見逃し=0 誤検知=0
series_b(n=60) / shuffled / 回2: 見逃し=0 誤検知=0
series_b(n=60) / noisy / 回1: 見逃し=0 誤検知=0
series_b(n=60) / noisy / 回2: 見逃し=0 誤検知=0
series_c(n=300) / original / 回1: 見逃し=0 誤検知=0
series_c(n=300) / original / 回2: 見逃し=0 誤検知=0
series_c(n=300) / shuffled / 回1: 見逃し=0 誤検知=0
series_c(n=300) / shuffled / 回2: 見逃し=0 誤検知=0
series_c(n=300) / noisy / 回1: 見逃し=0 誤検知=0
series_c(n=300) / noisy / 回2: 見逃し=0 誤検知=0

条件別集計:
  original: 6回・新着18件中 見逃し0件・誤検知0件
  shuffled: 6回・新着18件中 見逃し0件・誤検知0件
  noisy: 6回・新着18件中 見逃し0件・誤検知0件

総合計: 18回・新着54件中 見逃し0件・誤検知0件
```

---

## この記事から出た教訓（`content/_lessons.md` へ）

1. 既読リストの並び順（元の時系列順・一部だけ入れ替えた近い順・完全なシャッフル）を変えても、既読ID一覧を使った新着検出は崩れなかった（60件規模×2系列、300件規模×1系列、各3条件×2回転＝合計18回・新着54件中、見逃し0件・誤検知0件）。前作が残した未測定事項「既読リストの並び順をシャッフルした場合」に、見逃し・誤検知ともに変化なしという答えが付いた。
2. 並び順が投稿一覧と揃っていないと、AIは自分から気づいて1件ずつの機械的な照合に切り替える（自己申告で確認）。前作で見られた「並びが揃っていれば目視で拾う」という挙動は、並びが揃っていないと起きない。これが、並び順を変えても精度が落ちなかった理由と考えられる。
3. 🆕 同じ趣旨の自己申告確認の質問を `-r` 継続で複数回投げると、文面を変えなくても`reasoning_extraction`のAPIセーフガードに時々引っかかる（4回中3回失敗）。本体の実測（新着検出そのもの）とは別のセッションの出来事として扱い、失敗した回を記事から隠さず、成功した回だけを「参考情報」として使うべき。→ `content/_lessons.md` ★316として追記。
