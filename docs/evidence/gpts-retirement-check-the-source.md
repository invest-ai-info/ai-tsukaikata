# 試した証拠 — gpts-retirement-check-the-source

記事＝`content/recipes/gpts-retirement-check-the-source.md`
（「GPTsで稼ぐ門は閉じた——個人プランでは作れず、12月11日に止まる予定を原文で確かめる」）。
連載「売る場所の原文から」第5回。

実測日 2026-09-18。**実行はのべ18回**＝指示文6種（A〜F）を各3回、独立に実行。

## 実行のしかた

**実測用の回答は、このリポジトリで作業している Claude Code セッションから Agent ツール（`general-purpose` サブエージェント）を
1回ずつ新規に起動して得た。**`claude -p` は今夜は使えない（CLI の OAuth トークンが失効していて認証が通らない）。

- 各回は新規サブエージェント＝会話の文脈を引き継がない。ツール（ウェブ検索・ファイル読み書き・コマンド実行）を
  使わないよう前置きで指示し、完了通知の `tool_uses: 0` で「使わなかった」ことを確認した（18回すべて 0）。
- ⚠️ **サブエージェントはこのリポジトリの `CLAUDE.md` を読める位置にいる**（★145）。この記事の題材（GPTs の廃止予定）は
  `CLAUDE.md` に書かれていないので、結果に影響する経路は無いと判断した。厳密に事前知識ゼロにするなら
  `claude --safe-mode -p` を使う（トークンが復旧したら）。
- **送った全文＝定型の前置き＋質問。**前置きは18回とも同一で、次のとおり（★164＝前置きも含めて全文を開示する）:

```
あなたは一般向けのAIチャットアシスタントです。ツールは一切使わないでください（ファイルを読まない・ウェブ検索をしない・コマンドを実行しない）。次の質問に、あなたの知識だけで、文章で答えてください。回答の本文だけを返してください（前置きや「ツールは使いませんでした」等の説明は不要です）。

質問:
<記事の指示文をそのまま>
```

- 回答の全文は `docs/evidence/_raw/gpts-retirement-check-the-source/run01_*.md`〜`run18_*.md` に生のまま保存
  （Agent ツールの出力ファイルは0バイトになるため、完了通知の本文を担当が転記した。転記のさいに文字を変えていない）。
- 判定コード＝同ディレクトリの `judge.py`（正規表現の文字列照合のみ）、出力＝`judge_output.txt`。

## 真値の出典（2026-09-16 に実ブラウザで本文まで確認・9枚目／2026-09-18 に再確認＝FAQ は 09-17 更新で記載は同じ／26枚目は 09-18）

| | |
|---|---|
| 個人プランの新規作成 | 「New GPT creation and publishing are not available on personal ChatGPT accounts, including Free, Go, Plus, and Pro.」（[Creating and editing GPTs](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)） |
| 廃止の予定 | 「Sep 25, 2026 (planned): Creation of new custom GPTs ends.」「Dec 11, 2026: Scheduled retirement. Custom GPTs stop running.」「Note that the dates are subject to change.」「The other plans may follow the same transition timeline」（日付は Enterprise 向けの予定として書かれている）（[Custom GPT retirement and migration FAQ](https://help.openai.com/en/articles/20001519-custom-gpt-retirement-and-migration-faq)） |
| 収益化FAQ | 記事 9119255（Monetizing Your GPT FAQ）は [Sharing and publishing GPTs](https://help.openai.com/en/articles/8798878-sharing-and-publishing-gpts) へリダイレクト。本文 7,569字に `revenue` / `monetiz` / `earn` / `payout` は **0件**（担当が JS で数えた） |
| 後継（Plugins）の決済 | 「Plugin developers are responsible for choosing how to monetize their experience. Today, the recommended and generally available approach is to use external checkout」「While current approval is limited to plugins for physical goods purchases」（[Checkout API reference – Plugins](https://developers.openai.com/apps-sdk/build/monetization)・2026-09-18） |

⚠️ `help.openai.com` はクラウド環境から 403（bot 判定）。実ブラウザで確認した。

---

## 指示文A（素朴に聞く・3回）

### 送った指示文（記事と同一文字列）

```
ChatGPTのGPTs（カスタムGPT）を作って収入を得るには、どうすればいいですか。方法と条件を教えてください。
```

生の全文＝`run01_a1_A_naive.md`〜`run03_a3_A_naive.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 個人プラン（Plus）では作れないと述べた | **0/3** |
| 廃止の日付（9/25・12/11）を挙げた | **0/3** |
| Plus 等の有料プランなら作れると述べた | **2/3** |
| 収益化プログラムを米国限定・招待制の試験と述べた | **3/3** |
| Apps SDK／ChatGPT内アプリに触れた | **3/3** |

🔑 3回とも「収益化プログラムは米国限定・招待制の試験段階で、多くの人の収益源にはならない」と現実的に説明する。
しかし「もう作れない」「止まる予定」には1回も触れない＝**知識が古い側で止まっている**。

## 指示文B（収益化プログラムの条件・3回）

### 送った指示文（記事と同一文字列）

```
ChatGPTのGPT Storeには、作ったGPTの利用量に応じて制作者に支払う収益化プログラムがあると聞きました。その条件と、支払われるまでの流れを教えてください。
```

生の全文＝`run04_b1_B_revenue_program.md`〜`run06_b3_B_revenue_program.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 収益化プログラムを米国限定・招待制の試験と述べた | **3/3** |
| 廃止の日付（9/25・12/11）を挙げた | **0/3** |
| 収益化FAQが削除・転送されていることに触れた | **0/3** |

## 指示文C（廃止の予定を聞く・3回）

### 送った指示文（記事と同一文字列）

```
ChatGPTのGPTs（カスタムGPT）は、今後も使い続けられますか。廃止や大きな変更の予定があるなら、時期も含めて教えてください。
```

生の全文＝`run07_c1_C_retirement_plan.md`〜`run09_c3_C_retirement_plan.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 「廃止・終了の予定は出ていない」と述べた（原文と逆） | **3/3** |
| 廃止の日付（9/25・12/11）を挙げた | **0/3** |
| Apps SDK／ChatGPT内アプリに触れた | **3/3** |

🔑 「予定があるなら時期も含めて」と聞いても、知識に無いものは出ない。**予定は原文の仕事。**

## 指示文D（原文を貼って判断だけさせる・3回）

### 送った指示文（記事と同一文字列）

```
公式ヘルプで確認した情報を貼ります。これ以外の情報は使わないでください。

・New GPT creation and publishing are not available on personal ChatGPT accounts, including Free, Go, Plus, and Pro.
・Sep 25, 2026 (planned): Creation of new custom GPTs ends.
・Dec 11, 2026: Scheduled retirement. Custom GPTs stop running.
・Note that the dates are subject to change.

私は個人のPlusプランです。今からGPTsを作って収入を得ることはできますか。上の情報だけから答え、上に無いこと（収益化の条件や金額など）は「材料に無い」と書いてください。
```

生の全文＝`run10_d1_D_materials_fed.md`〜`run12_d3_D_materials_fed.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 材料の範囲で「できない」と答えた | **3/3** |
| 「材料に無い」の受け皿を使った | **3/3** |
| 材料に無い金額（円・ドル・%）を出した | **0/3** |
| 今日の日付（9月18日）を自分で持ち込んだ | **2/3** |
| 「日付は変更されうる」に触れた | **3/3** |

🔑 貼った範囲では正しく判断し、数字を作らない。ただし2回は「今日の日付」を自分で置いて残り日数を計算した
（結論は変わらない。日付計算を任せるなら今日の日付も貼る）。

## 指示文E（ページ名だけ・3回）

### 送った指示文（記事と同一文字列）

```
ChatGPTのGPTs（カスタムGPT）の提供状況や廃止予定について、確認すべきOpenAIの公式ページの名前だけを、中身や日付は書かずに教えてください。
```

生の全文＝`run13_e1_E_page_name_only.md`〜`run15_e3_E_page_name_only.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 年月日を書いた | **0/3** |
| 金額を書いた | **0/3** |
| 「ヘルプセンター」を挙げた | **3/3** |
| 廃止・移行FAQ（retirement / migration）の名を挙げた | **0/3** |
| 自分の記憶に限界があると断った | **2/3** |

🔑 「日付は書かずに」は3回とも守る。しかし廃止FAQのページ名は出ない（知識より後にできたページ）＝
**開く順番は記事の側で示す。**ページ名を聞く価値は「AIに日付を書かせないこと」。

## 指示文F（後継で個人が受け取る仕組みがあるか・3回）

### 送った指示文（記事と同一文字列）

```
OpenAIがGPTsの後継として案内しているプラグイン（ChatGPTの中で動くアプリ）で、個人の開発者がChatGPTの中で有料販売して収入を受け取る仕組みはありますか。分からない部分は「分からない」と書いてください。
```

生の全文＝`run16_f1_F_successor.md`〜`run18_f3_F_successor.md`。

### 判定（3回中・機械照合）

| 項目 | 回数 |
|---|---|
| 「分からない」と書いた | **3/3** |
| 誰でも使える仕組みは無い（確認できない）と述べた | **3/3** |
| 物販（物理的な商品）向けの決済に触れた | **3/3** |
| 決済は ChatGPT の外（自分のサイト）と述べた | **3/3** |
| 「プラグイン」を前身（2023年）と扱った | **3/3** |

🔑 3回とも「プラグイン」を2023年の旧機能として扱った＝**名前が同じで中身が変わったものは、古い側に引かれる。**
結論（個人が ChatGPT の中で有料販売して受け取る仕組みは無い）は原文と一致。

## この記事から出た教訓

- **「昔の条件」の説明は正確なのに、「いま閉じている」は0/9。**素朴に聞く・条件を聞く・予定を聞くの3通りとも同じ。
  聞き方を変えても増えない＝知識の境界より後のことは原文の仕事（`youtube-payout-thresholds` の「登録者500人」と同じ形で、
  今回は方向が逆＝古い「開いている」が今の条件として出る）。
- **原文を貼れば3/3で正しく判断し、数字を作らない**（`numbers-not-in-the-source` の型の再確認）。
- **後継の名前が旧機能と同じ（プラグイン）だと、3/3で旧機能の前提から答え始める。**
- 判定コードの罠＝完了通知の見出し行（tokens・秒）の数字を本文の数字として数えないよう、`load()` で見出し行を落とす（12番の再発）。
