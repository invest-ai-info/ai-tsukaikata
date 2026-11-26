# 稼ぎ方の変化の見張り（稼ぎ方研究担当が毎日使う）

**編集者向けの内部メモ。サイトには出ない**（ファイル名が `_` で始まるのでビルド対象外）。

## 何のためか（2026-11-26 オーナー判断）

本数を決めず、**稼ぎ方に関わる公式の変化が出た日に書く**。
その変化（手数料・料率・入金の条件・規約・収益化の条件）を、出た日のうちに見つけて書き手へ渡すのがこのファイルの役目。
書く本数・書く型の決まりは `content/_recipe_queue.md` の冒頭🔢節（ここには書かない）。

## 毎日の手順（15:30・稼ぎ方研究担当）

1. 下の「見張る記事」の表から、**最後に照合した日が古い順に3本**選ぶ（「未」が最優先）
2. 1本ずつ `python tools/check_numbers.py content/<種類>/<slug>.md` を回す。
   出典に無いと言われた数字は、出典ページを開いて**記事の数字と、公式の今の数字を1つずつ比べる**
3. 公式の数字・条文が記事と違っていたら＝**変化**。キューの「### 副業」節の最初の項目の前に、次の形で足す
   ```
   - [ ] 【変化】<サービス>の<何>が<前>→<後>に（<公式ページの名前>・<確かめた日>）
     - 出典: <URL>
     - 需要: 公式の変更（既存記事 `<slug>` の読者に影響）
     - 既存記事: `<slug>`（数字が古くなった。改稿は「🔧 改稿」節へ1行）
   ```
4. 表の「最後に照合した日」と「結果」を書き換える
   （`変化なし`／`変化あり→キューへ`／`開けず＝経路遮断` か `開けず＝bot判定`）
5. 時間が残れば「見張るお知らせページ」も開き、料率・規約・収益化の条件の変更の告知があれば3と同じ形で足す
6. 作業ログ（`content/_earn_research.md` の `### YYYY-MM-DD`）に、その日の結果を1行書く（心拍の番人が見る）

- ⚠️ **変化が無い日は、キューに何も足さない。**数を埋めるための補充はしない
- ⚠️ **UA偽装で迂回しない。**開けなかったら、どちらの遮断かを表に書いて次へ
- ⚠️ 数字の比べ方は機械（`check_numbers.py`）が先、目が後。機械が「出典に無い」と言わなかった数字も、
  料率・手数料・しきい値の数字は目でも確かめる（ページの別の場所に同じ数字があると、機械は「ある」と言う）

## 見張る記事

`scene: money` の記事で、出典が公式ページのもの。**書き手は公開したら1行足す。**

| slug | 種類 | 最後に照合した日 | 結果 |
|---|---|---|---|
| `ai-stock-images-adobe-vs-pixta` | recipes | 未 | — |
| `ai-writing-rate-below-the-rule-of-thumb` | recipes | 未 | — |
| `gpts-retirement-check-the-source` | recipes | 未 | — |
| `instagram-two-gates-500-and-10000` | recipes | 未 | — |
| `kindle-ai-disclosure-check` | recipes | 未 | — |
| `kindle-royalty-formula` | recipes | 未 | — |
| `note-fee-before-you-sell` | recipes | 未 | — |
| `note-membership-monthly-formula` | recipes | 未 | — |
| `udemy-97-or-37-who-brings-the-student` | recipes | 未 | — |
| `x-pay-before-you-earn` | recipes | 未 | — |
| `youtube-payout-thresholds` | recipes | 未 | — |
| `coconala-ai-automation-634-listings` | tools | 未 | — |
| `mercor-ai-evaluation-job-anatomy` | tools | 未 | — |
| `mercor-hourly-week20-formula` | tools | 未 | — |
| `money-map-three-routes` | tools | 未 | — |

## 見張るお知らせページ

各社の「お知らせ」「変更履歴」「規約の改定」のページ。見つけたら足す（最初は空）。

| サービス | ページ | 最後に開いた日 | 結果 |
|---|---|---|---|
