---
title: AIの最新情報を自動で集めて、重要なものだけメールで受け取る
description: 15の公式ソースを毎時チェックし、重大な発表だけ即メール、それ以外は毎朝1通にまとめる仕組みを、サーバー代0円で作ります。
category: recipes
published: 2026-08-01
tags: [GitHub Actions, 自動化, 無料, 情報収集, Python]
time_required: 1時間
cost: 無料
---

## これで何ができるか

AIの新モデルや新機能の発表を、**自分で見に行かなくても向こうから届くようにします**。

- OpenAI・Anthropic・Google・xAI・DeepSeek など15の公式ソースを1時間おきに自動チェック
- 「新モデル発表」級のものだけ**その場でメール**（1時間に最大1通）
- 細かい更新は溜めておいて**毎朝7時台に1通**にまとめて配信
- サーバーもVPSも不要。GitHub の無料枠だけで動く

届くメールは2種類です。

<figure class="figure">
<img src="/static/images/tracker-mail.svg" alt="2種類のメール。上は重要アップデートの即時通知で、件名は「🚨 AI重要アップデート 1件」、本文にDeepSeekの新モデル名・公開日時・HuggingFaceのURL・要約が並ぶ。下は毎朝のダイジェストで、件名は「📮 AI更新ダイジェスト 3件」、Claude Codeのリリースが2件並び、末尾に「qwen-blog: 3回連続で失敗 (HTTPError: 404)」という死活警告が付いている。">
<figcaption>実際に届くメール。2026年8月1日にソースを取得し、この記事で作る送信コードでそのまま組み立てた本物の出力です（配色だけこの記事に合わせています）。末尾の警告については「フィードが静かに死ぬ」で説明します。</figcaption>
</figure>

全体はこう動きます。

<figure class="figure">
<img src="/static/images/tracker-flow.svg" alt="処理の流れ。15の公式ソースを毎時17分に取得し、seen.jsonに無いものだけを新着として重要度判定にかける。重要なものはその場でメール送信、それ以外はキューに溜めて毎朝7時22分のダイジェストで1通にまとめて送る。">
<figcaption>毎時17分に取得し、既読でないものだけを重要度で振り分けます。判定に迷ったときは必ず「重要でない」側に倒します。溜めた分は翌朝1通にまとまるので、情報は失われず最大24時間遅れるだけです。</figcaption>
</figure>

この記事で作るものの完成品は [GitHub で公開しています](https://github.com/invest-ai-info/ai-tsukaikata)。動かしながら読むならそちらを clone するのが早いです。

## 前提

| | |
|---|---|
| かかる時間 | 1時間（うち待ち時間20分） |
| 費用 | 無料。GitHub Actions の無料枠内で収まります |
| 必要なもの | GitHubアカウント / Gmailアカウント / Python 3.12 |
| プログラミング | コードを書く必要はありません。設定ファイルを触るだけです |

GitHub Actions の無料枠は、公開（public）リポジトリなら**実行時間が無制限**です。この仕組みは1回30秒ほどなので、非公開リポジトリでも無料枠（月2000分）に余裕で収まります。

## 手順

### 1. リポジトリを用意する

GitHub で新しいリポジトリを作ります。公開・非公開どちらでも動きますが、**公開のほうが実行時間の制限を気にしなくて済みます**。

完成品を使う場合:

```bash
git clone https://github.com/invest-ai-info/ai-tsukaikata.git
cd ai-tsukaikata
pip install -r requirements.txt
```

### 2. 追いかけるソースを決める

`tracker/sources.yml` が唯一の設定ファイルです。**ここに数行足すだけでソースが増えます。**コードは触りません。

```yaml
sources:
  - id: openai-news
    vendor: OpenAI
    label: OpenAI News
    type: rss
    url: https://openai.com/news/rss.xml

  - id: claude-code
    vendor: Anthropic
    label: Claude Code
    type: github_releases
    url: https://github.com/anthropics/claude-code/releases.atom

  - id: hf-deepseek
    vendor: DeepSeek
    label: DeepSeek 新モデル
    type: huggingface
    org: deepseek-ai
```

`type` は4種類あります。

| type | 何を見るか | 指定するもの |
|---|---|---|
| `rss` | 普通のブログのRSS/Atom | `url` |
| `github_releases` | GitHubのリリース | `url`（`.../releases.atom`） |
| `huggingface` | HuggingFaceの新モデル | `org`（組織名） |
| `openrouter` | OpenRouterで提供開始されたモデル | `org`（ベンダー接頭辞） |

**追加する前に、そのURLが本当に生きているか確認してください。**AI企業の公式ブログはRSSを出していないことがかなりあります。ブラウザでURLを開いてXMLが出れば大丈夫です。

### 3. Gmailのアプリパスワードを取る

通知はGmailのSMTPで送ります。普段のログインパスワードではなく、**アプリパスワード**という専用のものを使います。

1. Googleアカウントで2段階認証を有効にする（これが済んでいないとアプリパスワードの項目が出てきません）
2. Googleアカウントの「セキュリティ」→「アプリ パスワード」へ
3. 生成された16桁を控える

この16桁は**画面を閉じると二度と表示されません**。控え忘れたら作り直しになります。

### 4. GitHubにSecretsを登録する

GitHub側で触るのは2箇所だけです。

<figure class="figure">
<img src="/static/images/github-settings.svg" alt="GitHubのSettingsで触る2箇所の図解。1つ目はSecrets and variablesのActionsで、GMAIL_USER・GMAIL_APP_PASSWORD・ALERT_RECIPIENTの3件を登録する。2つ目はActionsのGeneralにあるWorkflow permissionsで、初期値のRead repository contents permissionではなくRead and write permissionsを選び、Saveを押す。">
<figcaption>GitHubの画面配置を説明するための図解です（実際の画面とは配色・文言が異なります）。左が手順4、右が手順5。右を初期値のままにすると、メールは届くのに最後の保存だけ 403 で落ちます。</figcaption>
</figure>

リポジトリの `Settings → Secrets and variables → Actions` で、以下を `New repository secret` から登録します。

| 名前 | 中身 |
|---|---|
| `GMAIL_USER` | 送信元のGmailアドレス |
| `GMAIL_APP_PASSWORD` | 手順3で控えた16桁 |
| `ALERT_RECIPIENT` | 受信先アドレス（未設定なら送信元と同じところに届きます） |

ここに入れた値はログにも出ませんし、あとから中身を見ることもできません。**コードの中に直接書かないでください。**公開リポジトリなら世界中に見えますし、非公開でも履歴に残り続けます。

### 5. 権限を Read and write にする

`Settings → Actions → General → Workflow permissions` を **Read and write permissions** に変えます。

この仕組みは「どれを既読にしたか」をリポジトリのファイルに書き戻すので、書き込み権限が要ります。初期値の Read only のままだと後で 403 で落ちます。

### 6. 初期化する（ここが一番大事）

**いきなり通常運転を始めてはいけません。**まず初期化を走らせて、今ある記事を全部「既読」にします。

```bash
python -m tracker.run --mode bootstrap
```

```
初期化しました。311件を既読として記録（通知なし）
```

これで `data/tracker/seen.json` ができます。**この初期化ではメールは1通も飛びません。**

なぜこれが必要かは「つまずいた点」で書きます。ここを飛ばすと本当に痛い目に遭います。

初期化した状態をリポジトリに保存します。

```bash
git add data/tracker/seen.json
git commit -m "chore: トラッカーの初期状態を記録"
git push
```

### 7. ワークフローを2本置く

`.github/workflows/tracker.yml`（毎時チェック）:

```yaml
name: AI Update Tracker

on:
  # 毎時17分。毎時0分は負荷が集中して遅延・スキップが起きやすいため避ける
  schedule:
    - cron: "17 * * * *"
  workflow_dispatch:

permissions:
  contents: write

concurrency:
  group: tracker
  cancel-in-progress: false

jobs:
  check:
    runs-on: ubuntu-latest
    env:
      GMAIL_USER: ${{ secrets.GMAIL_USER }}
      GMAIL_APP_PASSWORD: ${{ secrets.GMAIL_APP_PASSWORD }}
      ALERT_RECIPIENT: ${{ secrets.ALERT_RECIPIENT }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: 依存をインストール
        run: pip install -r requirements.txt

      - name: 新着をチェック
        run: python -m tracker.run --mode check

      - name: 既読状態をコミット
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/tracker/seen.json
          git diff --staged --quiet || git commit -m "chore: トラッカーの既読状態を更新"
          git push
```

もう1本、毎朝のダイジェスト用（`.github/workflows/tracker-digest.yml`）は、`schedule` を `cron: "22 22 * * *"`（UTC 22:22 = JST 7:22）にして、実行するコマンドを `--mode digest` に変えるだけです。

### 8. 手動で動かして確認する

`Actions` タブ → `AI Update Tracker` → `Run workflow`。

初期化した直後なので新着は0〜数件のはずです。ログに `新着 0件（major 0 / minor 0）` と出れば成功です。

**この手動実行での確認を必ずやってください。**スケジュールが初めて動くのを待つと、失敗していた場合に1時間無駄になります。

## つまずいた点と直し方

ここからが本題です。全部、実際にやらかしたことです。

### 初回にいきなり通常運転させると1000通超のメールが飛ぶ

これが最大の罠です。

RSSフィードには**過去記事が全部入っています**。何も知らない状態で「新着チェック」を走らせると、フィードにある記事が全部「新着」になります。試したところ、**OpenAI のフィードだけで1105件**ありました。15ソース分だと数千通です。

<figure class="figure">
<img src="/static/images/tracker-bootstrap.svg" alt="初期化を飛ばした場合と実行した場合の比較。飛ばすとフィードの過去記事が全部新着と判定され、OpenAIのフィード1本だけで1105通の通知が飛ぶ。先に初期化を実行すると全件を既読として記録し、通知は0通。以後は本当の新着だけが届く。">
<figcaption>左が初期化を飛ばした場合、右が先に実行した場合。差は「既読の記録が1件でもあるかどうか」だけです。</figcaption>
</figure>

だから手順6の初期化が必要です。初期化は「今フィードにあるものを、通知せずに全部既読にする」だけの処理です。

これは人間の注意力に任せてはいけない種類の事故なので、**コードで止めています**。状態ファイルが無い状態で通常運転しようとすると、実行前に止まります。

```python
if args.mode == "check" and not args.state.exists():
    print(
        f"状態ファイルがありません: {args.state}\n"
        "先に --mode bootstrap を実行してください。これをせずに check を走らせると、"
        "全ソースの過去記事が新着扱いになり1000通以上のメールが飛びます。"
    )
    return 1
```

**「気をつける」ではなく「気をつけなくても壊れない」を作ってください。**深夜に眠い頭で作業する自分は、必ず手順を飛ばします。

### 権限が読み取り専用だと最後の push で 403

手順5を飛ばすと、チェック自体は成功してメールも届くのに、最後のコミットで落ちます。

```
remote: Permission to <user>/<repo>.git denied to github-actions[bot].
fatal: unable to access ...: The requested URL returned error: 403
```

タチが悪いのは、**メールは届いているのに既読が保存されていない**ことです。次の実行で同じものがもう一度届きます。1時間おきに同じメールが来たらこれを疑ってください。

### コミットのステップに `if: always()` を付けてはいけない

一見すると親切そうな設定ですが、これを付けると**送信に失敗しても既読として記録されます**。

「既読にしたのに届いていない更新」は、二度と拾われません。永久のデータ損失です。

送信が失敗したときは既読を保存せずに落ちるのが正しい挙動です。次の実行でもう一度送ろうとしてくれます。最悪でも重複メールで済み、情報は落ちません。

同じ理由で、**送信は保存より先**に呼んでいます。逆順にすると同じ事故が起きます。

### HuggingFace の組織名は大文字小文字が効く

エラーも警告も出ず、**静かに0件を返します**。

| 動くもの | 0件を返すもの |
|---|---|
| `moonshotai` | `MoonshotAI` |
| `zai-org` | `THUDM` |
| `deepseek-ai` | |
| `Qwen` | |

ブラウザで `https://huggingface.co/<組織名>` を開いて、モデル一覧が出るかを確認してから書いてください。

### 403 を返すサイトを迂回しようとしない

x.ai の公式ニュースページは、プログラムからのアクセスを 403 で弾いています。

User-Agent を偽装すれば通るかもしれませんが、**やめました**。相手が明示的に断っているものを、名乗りを偽って取りに行くのは筋が悪いですし、規約違反になり得ます。

代わりに OpenRouter 経由で追っています。こちらは「実際に提供が始まったモデル」だけが出てくるので、むしろノイズが減りました。**塞がれたら別の入口を探すほうが、結果的にいいものになります。**

### cron の毎時0分は避ける

`0 * * * *` と書きたくなりますが、**世界中のジョブが毎時0分に集中します**。GitHub のスケジュール実行は混雑すると遅れますし、ひどいときはスキップされます。

`17 * * * *` のような半端な分にしてください。それだけで体感が変わります。

なお、GitHub Actions のスケジュールは**数分〜十数分遅れるのが正常**です。「7時ちょうどに届く」ことに依存した設計にしないでください。この仕組みは「seen.json に無いものが新着」という判定なので、遅れても・スキップされても、次に走ったときに必ず拾います。**取りこぼしはなく、遅れるだけ**です。

### 通知が多すぎるときの調整

運用を始めると、HuggingFace 系がうるさく感じるはずです。実測では DeepSeek 87%・Kimi 89%・GLM 77% が「重要」判定でした。研究成果物のリポジトリや、同じ日に出る `-Base` / `-Instruct` の兄弟モデルが多いためです。

ただし**1時間に飛ぶメールは最大1通**（その時間の重要な更新をまとめて1通）なので、受信箱が溢れることはありません。それでもうるさければ、派生モデルの除外ルールを足すか、そのソースを OpenRouter 経由（実際に提供開始されたモデルだけ）に置き換えてください。

判定に迷ったときは**必ず「重要でない」側に倒す**設計にしています。重要でない扱いになっても翌朝のダイジェストには必ず載るので、情報は失われず最大24時間遅れるだけです。逆に「重要」を出しすぎると全部読まなくなり、そちらのほうが実害が大きいからです。

### Windowsで日本語が文字化けして落ちる

ローカルで動かすと、日本語のログ出力でいきなり落ちることがあります。

```
UnicodeEncodeError: 'cp932' codec can't encode character ...
```

Windowsのコンソールの文字コードが原因です。実行前にこれを付けてください。

```powershell
$env:PYTHONUTF8 = 1
python -m tracker.run --mode bootstrap
```

GitHub Actions 側（Linux）では起きません。

### フィードが静かに死ぬ

一番怖い壊れ方は、エラーで止まることではなく、**エラーを出さずに情報が来なくなること**です。フィードのURLは予告なく変わります。

対策として、3回連続で失敗したソースを毎朝のダイジェストの末尾に出しています。

```
--- 取得できていないソース ---
⚠️ qwen-blog: 3回連続で失敗 (HTTPError: 404)
```

このとき**「取得できた生の件数」で判定する**のがポイントです。重複を除いた新着件数で判定すると、更新が少ないソースが3時間で死亡扱いになって誤報が出ます（実際に一度やらかしました）。

## 応用・次の一手

**ソースを増やす**のはYAMLに数行足すだけです。コードは触りません。自分が普段チェックしているサイトのRSSを片っ端から入れてみてください。

**通知先を変える**なら、メール送信の部分を Slack や Discord の Webhook に差し替えるだけです。組み立てと送信は分けてあるので、送信側だけ書き換えれば済みます。

**溜まったデータを使う**のもおすすめです。半年も動かすと「どのベンダーがどれくらいの頻度で何を出しているか」という、どこにも売っていないデータが手元に貯まります。

この仕組みを作った日から、AI関連の情報収集に使う時間はほぼゼロになりました。**見に行かなくても、重要なものは向こうから来る**からです。

次は [GitHub Actions で「毎日決まった時刻に自動実行」を無料で作る](/recipes/github-actions-daily-cron/) を読むと、この仕組みのスケジュール部分だけを他の用途に転用できます。
