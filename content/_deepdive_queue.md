# 深掘り記事の待ち行列

要約を読んで「もっと詳しく知りたい」と思ったものの**URLを1行足す**だけ。
ルーティン（`ai-tsukaikata-deepdive`）が拾って、出典を実際に読んでから記事を書く。

ファイル名が `_` で始まるのでビルド対象外。サイトには出ない。

## 書き方

`- [ ] https://...` の形で足す。処理が終わったら routine が `- [x]` に変えて、
下に生成した下書きのファイル名を書く。**消さない**（同じものを二度書かないため）。

スマホからでも足せる: GitHub でこのファイルを開く → 鉛筆アイコン → 行を足す → Commit changes。

## 待ち行列

- [ ] https://www.anthropic.com/news/claude-opus-5
  - 2026-08-04 1回目: `Host not in allowlist: www.anthropic.com` の403で取得できず停止（記録は正しい挙動）。
    環境のネットワークアクセスを「カスタム」にして各社ドメインを追加し、解消。経緯は SESSION_HANDOFF.md 参照。
  - 2026-08-04 2回目: 取得成功。下書きを作成。
    ⚠️ **OpenAI のドメインは許可リストに入っていない**（`openai.com` / `developers.openai.com` とも
    プロキシが `CONNECT tunnel failed, response 403` を返す＝先方のbotブロックではなく経路の遮断）。
    Google（`ai.google.dev` / `deepmind.google`）と Anthropic（`www.anthropic.com` /
    `platform.claude.com`）は到達する。他社比較を書くなら、次に許可リストへ足すのは OpenAI。
  - 2026-08-04 3回目: 許可リストに `*.openai.com` を追加したので再実行。**OpenAI の公式料金ページの数字を
    入れて書き直すこと。**前の版は git に残っているので、悪くなったら戻せる。

## 処理済み

- https://www.anthropic.com/news/claude-opus-5 → content/_draft-claude-opus-5.md（2026-08-04）
