# /start/ の原材料（2026-08-09 収集）

実装計画 `2026-08-09-getting-started-guide.md` の Task 1 の結果。
**すべて公式ページの生テキストから拾った。**要約（WebFetch）は使っていない
——要約は書いてあることを消すため（2026-08-05 の実害）。

検索は「URLを見つける」ためだけに使い、**事実は必ず生ページで確かめ直した。**

## 取得できたページ

| URL | 状態 | 拾った記述 |
|---|---|---|
| `https://docs.claude.com/en/docs/claude-code/setup` | 200（365,107字・dateModified 2026-07-28） | Claude Code のシステム要件と導入手順（下記） |

⚠️ **上の1本目は、すでに `https://code.claude.com/docs/en/setup` へのリダイレクトだった**
（2026-08-09 18:20 に実測。ページ自身が名乗る正式URLも移転先）。リダイレクトが効いているので
週次の死活検査では鳴らない。**記事のリンクは移転先に直した。**
🔑 これが「腐り方③＝URLが動く」の実例。**200が返ることと、そのURLが正式であることは別。**
| `https://help.openai.com/en/articles/9982051` | 200（24,855字・Updated 9 days ago） | 「System Requirements: Windows 10 (x64 and arm64) version 17763.0 or higher」／Windowsアプリは**有料プラン限定**（Plus, Team, Edu, Enterprise）・Microsoft Store から |
| `https://support.google.com/gemini/answer/13275745` | 200（768,691字） | 「To use gemini.google.com, you need access to a supported browser: Chrome, Safari, Firefox, Opera, or Edgium.」 |
| `https://learn.microsoft.com/en-us/windows/release-health/release-information` | 200（85,154字） | 「Version 1809 (OS build 17763)」＝1809 と 17763 が同じものだと確認 |
| `https://claude.com/download` | 200（147,770字） | Windows/macOS のダウンロード導線はあるが、**システム要件の記載なし**（ヘルプセンターへ誘導） |
| `https://nodejs.org/en/download` | 200（256,673字） | 取得はできたが**使わない**（ネイティブ導入に Node.js は要らないため） |

## 取得できなかったページ

| URL | 何が起きたか |
|---|---|
| `https://support.anthropic.com/en/articles/8996904` | HTTPError（記事IDが違うか、移転した可能性） |

⚠️ **`openai.com` の403を警戒していたが、実際に届かなかったのは Anthropic のサポートだけだった。**
help.openai.com は素で200を返した。次回も先入観で決めず、実際に叩くこと。

## 公式の記載が見つからなかったもの（推測で埋めない）

- **ChatGPT（ブラウザ版）の対応ブラウザ**
- **Claude（ブラウザ版）の対応ブラウザ**
- **3社ともブラウザ版の必要メモリ**（Gemini も対応ブラウザは出しているがメモリは出していない）

→ 記事では「公式の記載なし」と書く。**書いていないこと自体が答え**（普通のPCなら通る）と添える。

## Claude Code のシステム要件（生テキストからそのまま）

> Operating system : macOS 13.0+ / Windows 10 1809+ or Windows Server 2019+ / Ubuntu 20.04+ /
> Debian 10+ / Alpine Linux 3.19+
> Hardware : **4 GB+ RAM, x64 or ARM64 processor**
> Network : internet connection required
> Shell : Bash, Zsh, PowerShell, or CMD
> Location : Anthropic supported countries
> ripgrep : usually included with Claude Code

## Claude Code の入れ方（Windows・生テキストからそのまま）

- **Native Install（推奨）** — PowerShell: `irm https://claude.ai/install.ps1 | iex`
- CMD: `curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd`
- 他に Homebrew / WinGet
- **Desktop app** ＝「Prefer a graphical interface? The Desktop app lets you use Claude Code
  without the terminal.」＝**ターミナルなしで使える道がある**
- **Git for Windows が推奨**（無い場合、Claude Code は Bash tool の代わりに PowerShell を使う）
- ネイティブ導入は**バックグラウンドで自動更新**される
- **npm 版は v2.1.198 以降 Node.js 22 以上が必要**（＝ネイティブ導入なら Node.js は要らない）

**公式が書いている「間違えたときの見分け方」**（そのまま記事に使える）:

- `The token '&&' is not a valid statement separator` が出た → **PowerShell にいる**（CMD ではない）
- `'irm' is not recognized as an internal or external command` が出た → **CMD にいる**（PowerShell ではない）
- プロンプトが `PS C:\` なら PowerShell、`C:\` だけなら CMD

## 最低要件の表（図①と記事の表にそのまま使う）

| ツール | 対応OS／ブラウザ | メモリ | ターミナル | 支払い |
|---|---|---|---|---|
| ChatGPT（ブラウザ） | 公式の記載なし | 公式の記載なし | 不要 | 無料で開始 |
| Claude（ブラウザ） | 公式の記載なし | 公式の記載なし | 不要 | 無料で開始 |
| Gemini（ブラウザ） | Chrome / Safari / Firefox / Opera / Edgium | 公式の記載なし | 不要 | 無料で開始 |
| Claude Code | Windows 10 1809+ ／ macOS 13.0+ | **4GB以上** | 不要（デスクトップ版）／必要（コマンド版） | 有料プラン |

⚠️ 「ChatGPT の Windows **アプリ**」は Windows 10 17763.0+ かつ**有料プラン限定**。
ブラウザ版とは別物なので、表では分けずに本文で1行触れる。

## この記事を書いた機械（比較対象として1行載せる）

| | |
|---|---|
| OS | Windows 11 Home（10.0.26200） |
| メモリ | 15.6 GB |
| CPU | Intel Core Ultra 5 125H（14コア／18論理） |
| Node.js | **入っていない** |
| Claude Code | 2.1.104（ネイティブ導入） |

⚠️ ホスト名・ユーザー名・絶対パスは載せない（`validate.py` が `C:\Users\` を弾く）。

## 設計への影響（設計書の前提が3つ覆った）

| 設計書に書いていたこと | 実際 |
|---|---|
| 「要るのはスペックではなく**ターミナルと Node.js**」 | **Node.js は要らない**（ネイティブ導入）。**ターミナルも必須ではない**（デスクトップ版） |
| 「ブラウザ版AIの推奨メモリは公表されていない可能性が高い」 | ブラウザ版は確かに無い。**ただし Claude Code は 4GB+ と明記されている** |
| 「表がスカスカに見えるかもしれない」 | **一番重い Claude Code に公式の数字がある**ので、答えとしては十分に埋まる |

🔑 **記事の芯になる事実:**

1. **4つのうち一番重い Claude Code で「4GB以上」。**つまり **4GB あれば全部動く**。
   これが「必要最低限のスペック」への、出典のある答えになる
2. **足切り線は Windows 10 1809（＝ビルド17763）。**ChatGPT の Windows アプリの
   `17763.0 or higher` と、Claude Code の `Windows 10 1809+` が**同じ線**。
   1809 = 17763 は Microsoft の公式ページで確認済み
3. **Node.js もターミナルも必須ではない。**初心者の障壁として一番大きい2つが、実は要らない
