# ライターSOP導入 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 手動ライター作業の省トークン手順（2会話分割＋並列実測＋raw/judge.py）を `content/_writer_sop.md` に成文化し、SESSION_HANDOFF から参照させる。

**Architecture:** 設計書 `docs/superpowers/specs/2026-08-27-writer-token-diet-design.md` の§2〜§6をチェックリスト化した静的ファイルを1つ足すだけ。コード変更なし。raw/judge.py の規約は記事執筆時に記事ごとに適用される（今回はディレクトリも作らない＝空ディレクトリはgitに乗らない）。

**Tech Stack:** Markdown のみ。検証は既存の `pytest` / `src.build`。

---

### Task 1: `content/_writer_sop.md` を作成

**Files:**
- Create: `content/_writer_sop.md`

- [ ] **Step 1: ファイルを以下の内容で作成**

````markdown
# ライター作業SOP — 1本を2会話で書く（トークン食・品質不触）

**対象**: 手動ライター作業（キューの記事を1本ずつ高品質に仕上げる作業）。
自動ルーティンには適用しない（第2段＝設計書§7）。
**理由と数字は設計書が正**: `docs/superpowers/specs/2026-08-27-writer-token-diet-design.md`

## 🚫 禁止（会話①②共通）

- **全読み禁止**: `_recipe_queue.md`（2,000行超）は Grep で題名→該当節だけ部分読み
- **手集計禁止**: 実測の数字は judge.py の出力から取る。手で数えた数字を記事に書かない
- **真値を渡さない**: サブエージェントには依頼＋材料だけ（仕込みの答え・期待値を渡さない＝★91）
- **中略した抜粋で判定しない**: 判定は必ず raw の全文へ（中略が判定行を落とした実例あり・8/27）

## 🔒 触らないもの（品質の本体）

実測の回数と独立性／証拠の逐語全文／独立レビュー（指摘が尽きるまで）／
判定コードの生テキスト再実行での裏取り／機械検査。**削るのは読み直しだけ。**

## 会話①＝企画＋実測

- [ ] キューの該当項目だけ部分読み（Grep→offset/limit）
- [ ] 企画: 構成と実測計画（何を・何回・どの条件で）
- [ ] **judge.py を先に書く**: `docs/evidence/_raw/<slug>/judge.py`（判定基準＝正規表現・数え方をコード化）
- [ ] 実測: 並列サブエージェント（1メッセージにN呼び出し・1呼び出し=1独立実行）
  - 各エージェントは生の全文を `docs/evidence/_raw/<slug>/runNN.md` に**自分で書く**
  - 冒頭ヘッダ: 版・材料・実行方法・日時
  - 親には条件＋判定用の数行だけ返させる（全文を返させない）
- [ ] judge.py を raw 全体に流して集計表を作る
- [ ] 証拠ファイル `docs/evidence/<slug>.md` を組み立て（指示文は同一文字列で全文・畳まない）
- [ ] キュー該当項目に注記: 実測済み・要点・rawパス（数行）
- [ ] `_writer_log.md` に実測行（回ごと1行）
- [ ] commit → `git pull --rebase` → push → **会話終了**（オーナーが新会話で②へ）

## 会話②＝執筆〜公開

- [ ] 読むもの: このSOP＋キュー該当項目（①の注記込み）＋証拠ファイル。**rawは読まない**（疑義が出た run だけ開く）
- [ ] 執筆（記事の型は CLAUDE.md どおり: 5ブロック・マーカー上限・数値比較は図2枚以上・座標は計算）
- [ ] 機械検査: `python -m pytest -q` ／ `python -m src.build` ／ `python tools/check_numbers.py <記事>`
- [ ] 独立レビュー: 材料（記事＋証拠＋judge.py集計）だけ渡す・指摘リストのみ返させる・指摘が尽きるまで
- [ ] 修正で数字を触るときは judge.py を raw に再実行してから（手で書き換えない）
- [ ] 公開: キュー「→保管」注記・`_writer_log.md`・commit → `git pull --rebase` → push
- [ ] 成り行き条項: 文脈🟠300k超えが見えたらレビュー境界で引き継ぎ注記を書いて切ってよい

## 📏 効果測定（3本目だけ必須）

- [ ] 公開後、`python ~/.claude/token-report.py` で2本目（8/27）と比較（目標▲50%・実測1回あたりも併記）
- [ ] 結果を設計書§6の下に追記。効いていたらルーティン移植（§7）をオーナーに提案
````

- [ ] **Step 2: 検査が通ることを確認**

Run: `python -m pytest -q` → Expected: 555 passed（既存と同数・減っていないこと）
Run: `python -m src.build` → Expected: 正常終了（`_` 始まりなのでビルド対象外＝ファイル数が増えないこと）

- [ ] **Step 3: Commit**

```bash
git add content/_writer_sop.md
git commit -m "手順: ライターSOPを追加（2会話分割・並列実測・raw/judge.py）"
```

### Task 2: SESSION_HANDOFF に参照1行を追記

**Files:**
- Modify: `SESSION_HANDOFF.md`（「次＝キューの3本目」の行の直後）

- [ ] **Step 1: 該当行の直後に1行追記**

対象（現状の行・部分一致で特定する）:

```
- **次＝キューの3本目「時給の推移を週ごとに並べる」→4本目「30案の次にもう30案出させる」の順で継続**
  （まだ着手していない。次のセッションはここから）
```

この直後に追記:

```
- 🆕 **3本目からの書く手順＝`content/_writer_sop.md` に従う**（2026-08-27 設計承認・
  2会話分割＋並列実測。手順の複製をここに書かない＝SOPが単一ソース）
```

- [ ] **Step 2: Commit・push**

```bash
git add SESSION_HANDOFF.md
git commit -m "引き継ぎ: ライターSOPへの参照を追加"
git pull --rebase
git push
```

Expected: push成功（リモートは自動ルーティンが動くので rebase を挟む）
