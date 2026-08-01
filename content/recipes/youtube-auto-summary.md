---
title: YouTubeの動画を毎晩自動で要約させて、見る前に中身を知る
description: 追いかけているチャンネルの新着を毎日まとめて要約させます。30分の動画を10秒で判断できるようになります。
category: recipes
published: 2026-08-01
tags: [YouTube, 自動化, 要約, GitHub Actions, Gemini]
time_required: 1時間30分
cost: 無料〜（AIの利用料のみ）
---

## これで何ができるか

**追いかけているYouTubeチャンネルの新着動画を、見る前に中身を知れるようにします。**

- 登録チャンネルの新着を毎日自動でチェック
- 字幕を取ってきてAIに要約させる
- 「3行サマリー」「重要トピック」の形で1ページにまとめる

30分の動画が5本溜まっていても、**10秒で「今日はどれを見るべきか」が判断できます**。全部見れば2時間半、要約を読めば1分です。

情報収集系のチャンネルを何本も追いかけている人ほど効きます。実際に運用していて、動画を見る本数は減ったのに「見逃した」感覚はなくなりました。

## 前提

| | |
|---|---|
| かかる時間 | 1時間30分 |
| 費用 | 無料枠で収まります（Gemini・YouTube Data API とも無料枠あり） |
| 必要なもの | GitHubアカウント / Googleアカウント / Python |
| 前提知識 | [GitHub Actionsで定時実行を作る](/recipes/github-actions-daily-cron/) を先に読むと楽です |

**先に言っておくと、これは前の2つのレシピより手間がかかります。**外部APIを2つ使うのと、YouTube側の事情で素直に取れないケースがあるためです。ただ、そのハマりどころは全部この記事に書きました。

## 手順

### 1. APIキーを2つ取る

**Gemini APIキー**（要約用）

[Google AI Studio](https://aistudio.google.com/) にログインして「Get API key」から発行します。無料枠があります。

**YouTube Data APIキー**（動画一覧の取得用）

[Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作り、「YouTube Data API v3」を有効化してから、APIキーを発行します。無料枠は1日10,000ユニットで、この用途なら十分すぎます。

どちらもGitHubのSecretsに登録します（`GEMINI_API_KEY` と `YOUTUBE_API_KEY`）。**コードに直接書かないでください。**

### 2. 追いかけるチャンネルを決める

チャンネルIDの一覧をコードに書きます。ハンドル名（`@xxxxx`）ではなく**チャンネルID**（`UC` で始まる24文字）が必要です。

```python
CHANNELS = [
    ("@example_channel_1", "UCxxxxxxxxxxxxxxxxxxxxxx", "チャンネルA"),
    ("@example_channel_2", "UCyyyyyyyyyyyyyyyyyyyyyy", "チャンネルB"),
]

MAX_VIDEOS = 5        # 1日に新しく要約する本数
MAX_AGE_HOURS = 72    # 何時間前までの動画を対象にするか
KEEP_DAYS = 3         # 要約を何日分ページに残すか
```

チャンネルIDの調べ方は、そのチャンネルのページを開いてソースを表示し、`channelId` で検索するのが確実です。

### 3. 動画リストを取ってくる

YouTube Data API を3回叩きます。

```python
YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"

def fetch_channel_videos_api(channel_id, api_key, max_results=10):
    # ① チャンネルの「アップロード済み再生リスト」IDを取る
    ch = _get("channels", {"part": "contentDetails", "id": channel_id}, api_key)
    uploads_id = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    # ② その再生リストから動画IDを取る
    pl = _get("playlistItems", {
        "part": "contentDetails",
        "playlistId": uploads_id,
        "maxResults": str(max_results),
    }, api_key)
    video_ids = [it["contentDetails"]["videoId"] for it in pl["items"]]

    # ③ 動画の詳細（タイトル・説明・再生時間）を取る
    return _get("videos", {
        "part": "snippet,contentDetails",
        "id": ",".join(video_ids),
    }, api_key)
```

APIキーを使わずRSS（`https://www.youtube.com/feeds/videos.xml?channel_id=...`）でも一覧は取れますが、**GitHub ActionsのIPからだと不安定です**。理由は後述します。

### 4. 字幕を取る

`youtube-transcript-api` を使います。

```python
from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    api = YouTubeTranscriptApi()
    # 日本語 → 英語 → 中国語 の順で試す
    for langs in (["ja", "ja-JP"], ["en", "en-US"], ["zh", "zh-CN"]):
        try:
            t = api.fetch(video_id, languages=langs)
            return " ".join([s.text for s in t])
        except Exception:
            continue
    # どれも無ければ、利用可能な言語から1つ拾う
    try:
        for t_info in api.list(video_id):
            try:
                return " ".join([s.text for s in t_info.fetch()])
            except Exception:
                continue
    except Exception:
        pass
    return None
```

**言語を1つだけ指定して諦めるのはもったいないです。**日本語字幕が無くても自動生成の英語字幕があることは多く、AIは英語字幕からでも日本語で要約してくれます。

### 5. 要約させる

プロンプトで**出力の形を固定する**のがポイントです。

```
以下の動画の字幕を読んで、要約してください。

【出力フォーマット】（このフォーマットを厳守）
3行サマリー:
- (1行目: 動画の核心メッセージ)
- (2行目: 注目すべき具体的なデータ・数字)
- (3行目: 自分にとっての示唆)

重要トピック:
- (箇条書きで3〜5個。具体的に)

【注意】
- 動画で明示されていない情報は推測しない
- 過度な断定は避ける
- 日本語で出力
- Markdown装飾（**、##、__ など）は一切使わずプレーンテキストで出力すること
```

字幕は長いので、渡す量に上限を付けます（12,000文字程度）。長い動画を丸ごと渡すとコストも待ち時間も増えるわりに、要約の質はあまり変わりません。

### 6. 定時実行にする

```yaml
name: Update YouTube Summary

on:
  schedule:
    - cron: '13 1 * * *'    # 10:13 JST 本命
    - cron: '13 2 * * *'    # 11:13 JST バックアップ
  workflow_dispatch:

jobs:
  generate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    env:
      GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install youtube-transcript-api google-generativeai
      - run: python generate_youtube_summary.py
      - name: 変更があればコミット
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add youtube-summary.html youtube-summary-data.json
          if git diff --cached --quiet; then
            echo "変更なし"
          else
            git commit -m "chore: YouTube要約を更新"
            git pull --rebase origin main || true
            git push
          fi
```

## つまずいた点と直し方

### 字幕が取れないことがある。だから代替経路を用意する

これが最大の壁です。原因はいくつも重なります。

- そもそも字幕が付いていない動画がある
- 投稿者が字幕を無効にしている
- **クラウドのIPからのアクセスが制限されることがある**（自宅のPCでは取れるのにGitHub Actionsでは取れない、という現象が起きます）

「字幕が取れなければ諦める」だと、日によって中身が空になります。**段階的に落とす**設計にしてください。

1. 字幕が取れたら、字幕を要約する（最良）
2. 取れなければ、**タイトルと説明文だけで**紹介文を書かせる（次善）
3. それも失敗したらその動画はスキップする

2番目に落ちたときが重要です。**AIは中身を見ていないのに、見てきたような要約を書きます。**プロンプトで明示的に縛ってください。

```
【動画情報】（タイトルと説明文のみ・動画内容は未視聴）
...
【注意】
- 動画本編は未視聴である前提で、「〜と思われる」「〜の可能性」
  「〜について解説していると見られる」など慎重な表現を使う
- タイトルや説明にない情報の捏造はしない
```

これを書かないと、**読者は「AIが動画を見て要約した」と誤解します**。自分だけが読むなら害は小さいですが、公開するなら必須です。

### Shortsを「60秒以下」で判定すると外れる

短尺動画を除外したくなりますが、**YouTube Shorts は最長180秒まで伸びました**。60秒で判定すると素通りします。

実際に使っている判定はこうです。

1. 再生時間が90秒以下 → ほぼ確実にShorts
2. 180秒以下 かつ タイトルにハッシュタグが3個以上 → Shortsの可能性が高い
3. タイトルや説明文に `#shorts` 等のマーカーがある → Shorts

再生時間はYouTube Data API の `contentDetails.duration` から `PT5M30S` のような形式で返ってくるので、秒に直して使います。

```python
def _parse_iso_duration(s):
    """ISO 8601 duration (PT5M30S) → 秒"""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", s or "")
    if not m:
        return 0
    return int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + int(m.group(3) or 0)
```

**RSSでは再生時間が取れません。**これがAPIを使うもう一つの理由です。

### AIのモデル名は消える

半年前に動いていたモデル名が、ある日突然エラーになります。1本のモデル名を決め打ちにすると、その日から全部失敗します。

候補を並べて、順に試す形にしてください。

```python
MODEL_CANDIDATES = ("gemini-2.0-flash", "gemini-2.5-flash", "gemini-flash-latest")

for model in MODEL_CANDIDATES:
    try:
        return call_model(model, prompt)
    except Exception as e:
        last_err = e
        continue
print(f"全モデルで失敗: {last_err}")
```

`-latest` が付いた名前を最後に置いておくと、生き残る確率が上がります。

### 「Markdownを使うな」と言っても使ってくる

生成結果をHTMLに埋め込む場合、`**強調**` や `## 見出し` がそのまま文字として表示されて崩れます。

プロンプトで禁止しても、**完全には守られません**。受け取った側でも装飾記号を落とす処理を入れてください。プロンプトは「お願い」であって「保証」ではありません。

同じ理由で、**決めたフォーマットで返ってこなかったときの受け皿**も要ります。パースに全部失敗したら、冒頭から箇条書きの行を拾って埋める、くらいの雑な救済でも「ページが真っ白」よりずっとマシです。

### 同じ動画を毎日要約してしまう

要約結果をJSONファイルに保存して、**既に要約済みの動画IDはスキップ**します。これをしないと毎日同じ動画にAPIコストを払い続けます。

```python
DATA_FILE = "youtube-summary-data.json"
KEEP_DAYS = 3     # 3日より古い要約は捨てる
```

古いものを捨てないとファイルが延々と膨らみます。「何日分をページに載せるか」と「何日分を保存するか」は揃えてください。

### 複数のワークフローが同じリポジトリにpushして衝突する

他の自動化と同じリポジトリを使っていると、pushが競合して落ちます。

```bash
git pull --rebase origin main || true
git push
```

`|| true` を付けているのは、pullが失敗しても続行させるためです。ここで止まると、せっかく生成した要約が捨てられます。

### Windowsのコンソールで絵文字を出すと落ちる

ログに絵文字を使うと、ローカル実行時にこうなります。

```
UnicodeEncodeError: 'cp932' codec can't encode character ...
```

スクリプトの冒頭にこれを入れておくと解決します。

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
```

### 無料枠は意外と余裕がある

心配になりますが、実測では余裕でした。

- YouTube Data API: 1チャンネルあたり3ユニット。10チャンネルでも1日30ユニット（無料枠は10,000）
- Gemini: 1日5本の要約なら無料枠の範囲

コストが問題になるとしたら、字幕を丸ごと渡している部分です。上限を切っておけば予測可能な範囲に収まります。

## 応用・次の一手

**要約の出力先はHTMLである必要はありません。**メールで送る、Slackに流す、Markdownでメモアプリに落とす、どれでも同じ仕組みで作れます。要約を作る部分と出す部分を分けておけば、あとから差し替えられます。

**チャンネル以外にも使えます。**RSSがあるものなら何でも同じ形です。ニュースサイト、Podcast、企業のプレスリリース。「新着を取る → 中身を取る → 要約させる → 保存する」の4段は共通です。

そして、**この手の自動化は必ず静かに壊れます。**APIの仕様変更、字幕が取れなくなる、モデル名が消える。エラーは出ないのに中身が空のまま更新され続ける、というのが一番怖い壊れ方です。対策は [サービスが静かに壊れたのを自動で見つける](/recipes/auto-health-check/) に書きました。
