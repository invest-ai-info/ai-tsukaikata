# 深掘り記事の待ち行列

要約を読んで「もっと詳しく知りたい」と思ったものの**URLを1行足す**だけ。
ルーティン（`ai-tsukaikata-deepdive`）が拾って、出典を実際に読んでから記事を書く。

ファイル名が `_` で始まるのでビルド対象外。サイトには出ない。

## 書き方

`- [ ] https://...` の形で足す。処理が終わったら routine が `- [x]` に変えて、
下に生成した下書きのファイル名を書く。**消さない**（同じものを二度書かないため）。

スマホからでも足せる: GitHub でこのファイルを開く → 鉛筆アイコン → 行を足す → Commit changes。

## 待ち行列

- [!] https://www.anthropic.com/news/claude-opus-5
  - 2026-08-04: 取得できず。実行環境の**ネットワーク許可リストに `www.anthropic.com` が入っていない**ため
    403 が返る（本文は `Host not in allowlist: www.anthropic.com. Add this host to your network egress
    settings to allow access.`）。プロキシ経由・プロキシ迂回（`--noproxy '*'`）の両方で同じ 403 なので、
    Anthropic 側の bot ブロックではなく**この環境の egress 設定**が原因。
    直し方＝環境のネットワーク設定に `www.anthropic.com` を追加してから、この行を `- [ ]` に戻す。
    ⚠️ 出典を読めないまま検索結果や二次情報で書かない（数字が壊れるため）。

## 処理済み

（まだ無し）
