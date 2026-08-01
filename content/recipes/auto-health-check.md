---
title: サイトやサービスが静かに壊れたのを、自動で見つけて知らせる
description: 「落ちていないか」ではなく「更新が止まっていないか」を見張ります。自動化で一番怖い、エラーを出さない故障を捕まえる仕組みです。
category: recipes
published: 2026-08-01
tags: [監視, 自動化, GitHub Actions, 無料]
time_required: 45分
cost: 無料
---

## これで何ができるか

**自動化が「エラーを出さずに壊れた」ことを、自分より先に機械に見つけさせます。**

自動化を作ると、必ずこの日が来ます。

- 気づいたら3日前のデータがずっと表示されていた
- メールが来なくなっていたが、いつからか分からない
- ページは開くのに、中身が途中で切れていた

**どれもエラーメッセージは出ません。**ジョブは緑のチェックマークで「成功」しています。だから気づけません。

この記事で作るのは、それを見つけて**GitHubのIssueを自動で立てる**仕組みです。無料で、45分でできます。

## 前提

| | |
|---|---|
| かかる時間 | 45分 |
| 費用 | 無料 |
| 必要なもの | GitHubアカウント / 監視したいサイトやサービス |
| 前提知識 | [GitHub Actionsで定時実行を作る](/recipes/github-actions-daily-cron/) を先に読んでください |

## 手順

### 1. 「正常とは何か」を先に決める

ここが一番大事で、一番飛ばされる工程です。

「動いている」を**外から測れる形**に言い換えてください。実際に使っている3つはこれです。

| 見るもの | 何を捕まえるか |
|---|---|
| HTTPステータスが200か | ページが落ちた |
| 中身のサイズが一定以上か | 生成が途中で切れた |
| **ページに書かれた更新日が今日か** | **更新が止まった** |

3つ目が本命です。1つ目と2つ目は「派手な壊れ方」で、たいてい自分で気づきます。**静かに壊れるのは3つ目だけです。**

### 2. チェックするスクリプトを書く

```python
"""サイトが正常に更新されているかをチェックする。

異常があれば health_report.md を書き出して非ゼロ終了する
（ワークフロー側でIssueが立つ）。
"""
import datetime
import re
import sys
import zoneinfo

import requests

BASE = "https://example.com"
PAGES = ["index.html", "calendar.html", "charts.html"]
MIN_BYTES = 5000   # 途中切れ検出の閾値
TIMEOUT = 20


def jst_today():
    return datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Tokyo")).date()


def check_page(path):
    url = f"{BASE}/{path}"
    errors = []

    try:
        r = requests.get(url, timeout=TIMEOUT)
    except Exception as e:
        return [f"❌ `{path}` 取得失敗: {e}"]

    if r.status_code != 200:
        return [f"❌ `{path}` HTTP {r.status_code}"]

    body = r.text
    size = len(body.encode("utf-8"))
    if size < MIN_BYTES:
        errors.append(f"⚠️ `{path}` サイズ異常: {size} bytes（途中切れの可能性）")

    if path == "index.html":
        m = re.search(r"最終更新[:：]\s*(?:<[^>]+>\s*)*(\d{4})年(\d{1,2})月(\d{1,2})日", body)
        if not m:
            errors.append("⚠️ 「最終更新」の日付が見つからない")
        else:
            page_date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            today = jst_today()
            if page_date < today:
                delta = (today - page_date).days
                errors.append(
                    f"🚨 日付が古い: ページ `{page_date}` / 今日 `{today}`（{delta}日遅れ）"
                )

    return errors
```

異常があればレポートを書き出して、**非ゼロで終了**します。これがワークフロー側で「失敗」として扱われます。

```python
def main():
    all_errors = []
    for path in PAGES:
        errors = check_page(path)
        all_errors.extend(errors)
        print(f"{'✅' if not errors else '❌'} {path}")

    if all_errors:
        with open("health_report.md", "w", encoding="utf-8") as f:
            f.write(f"# 🚨 異常検知 ({jst_today()} JST)\n\n")
            f.write("\n".join(f"- {e}" for e in all_errors))
        sys.exit(1)          # ← これでワークフローが「失敗」になる

    print("すべて正常")
```

### 3. 異常時にIssueを立てる

メール通知でもいいのですが、**GitHubのIssueにすると「未対応のものが一覧で残る」**ので取りこぼしません。

```yaml
name: Health Check

on:
  schedule:
    - cron: '13 3 * * *'    # 12:13 JST
    - cron: '13 11 * * *'   # 20:13 JST
  workflow_dispatch:

jobs:
  check:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      issues: write         # Issueを立てるのに必要
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install requests

      - name: チェック実行
        run: python check_site_health.py

      - name: 異常ならIssueを立てる（または既存にコメント）
        if: failure() && hashFiles('health_report.md') != ''
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const body = fs.readFileSync('health_report.md', 'utf8');
            const today = new Date().toLocaleDateString('ja-JP', {
              timeZone: 'Asia/Tokyo', year: 'numeric', month: '2-digit', day: '2-digit'
            }).replace(/\//g, '-');

            // 既に開いているIssueがあるか確認（重複防止）
            const existing = await github.rest.issues.listForRepo({
              owner: context.repo.owner,
              repo: context.repo.repo,
              state: 'open',
              labels: 'health-check',
              per_page: 1
            });

            if (existing.data.length === 0) {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `🚨 サイト異常検知: ${today}`,
                body: body,
                labels: ['bug', 'health-check']
              });
            } else {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: existing.data[0].number,
                body: `## 🔁 ${today} 再検知\n\n${body}`
              });
            }
```

**`permissions` に `issues: write` を忘れないでください。**無いとIssue作成が403で落ちます。

## つまずいた点と直し方

### 監視の時刻は「監視される側の最後の砦」より後に置く

これを間違えると、毎日偽の警報が鳴ります。

監視対象が朝7:27に動き、遅延対策で8:57まで再試行するなら、**監視は9時ではなく12時**に置きます。90分以上のバッファを取ってください。

GitHub Actions のスケジュールは遅れるので、監視される側が遅れているだけなのに「異常」と判定されます。**狼少年になった監視は無視されるようになり、無いのと同じになります。**

### 「1回失敗したら通知」にしない

一時的なネットワークエラーや、相手側の瞬間的な不調で毎回鳴ります。

別の仕組み（AIの更新情報を集めるトラッカー）ではこうしています。

```python
FAILURE_THRESHOLD = 3

def record_result(state, source_id, error, count):
    """取得結果を記録する。成功かつ1件以上なら失敗カウントをリセットする。"""
    if error is None and count > 0:
        state["failures"].pop(source_id, None)
        return
    entry = state["failures"].get(source_id, {"count": 0, "last_error": ""})
    entry["count"] += 1
    entry["last_error"] = error or "0件"
    state["failures"][source_id] = entry


def dead_sources(state):
    """3回以上連続で失敗しているものだけを返す。"""
    return [
        (source_id, entry["count"], entry["last_error"])
        for source_id, entry in sorted(state["failures"].items())
        if entry["count"] >= FAILURE_THRESHOLD
    ]
```

**成功したらカウントをリセットする**のが要点です。「累計3回」ではなく「連続3回」で見ます。

### 「取れた件数」の数え方を間違えると誤報が出る

これは実際にやらかしました。

新着記事を取ってくる仕組みで、死活判定に**「重複を除いた新着の件数」**を使っていました。すると、更新頻度の低いサイトが**3時間で「死亡」扱い**になります。新着が無いのは正常なのに、です。

正しくは**「サーバーから返ってきた生の件数」**で判定します。0件が返ってきたなら本当に異常、10件返ってきて全部既読ならそれは正常です。

「何を数えているのか」を一度立ち止まって確認してください。ここは静かに間違えます。

### 監視する側が壊れたら気づけない

監視ワークフローが止まっても、当然ながら誰も教えてくれません。

対策は2つあります。

1. **監視の監視を作る。**「各ワークフローの最終成功時刻」を集めて、しばらく動いていないものを報告する仕組みを別に置く
2. **正常でも定期的に生存報告を出す。**「異常なし」の通知が来なくなったこと自体を異常のサインにする

1つ目のほうが静かで済みます。ただし**その仕組み自体は絶対に単純にしてください。**複雑な監視は必ず監視対象より先に壊れます。

### 検知の条件がHTMLの構造に依存すると、デザイン変更で壊れる

日付を正規表現で拾う方式は、ページの構造を変えた瞬間に「日付が見つからない」と鳴り始めます。実際、トップページの整理をしたときに壊れました。

そのときの直し方は、**日付の前に任意のタグを許すよう緩めた**だけです。

```python
# 「最終更新: <span>2026年8月1日</span>」も
# 「最終更新: <details><summary>2026年8月1日」も拾えるようにする
re.search(r"最終更新[:：]\s*(?:<[^>]+>\s*)*(\d{4})年(\d{1,2})月(\d{1,2})日", body)
```

**検知の条件は、見た目ではなく意味に結び付けてください。**「特定のHTML構造の中にある日付」ではなく「ページのどこかに書いてある最終更新日」を見る、という形にします。

理想を言えば、監視用に機械が読む専用の出力（`health.json` のようなもの）を用意して、そちらを見るのが一番壊れにくいです。

### 監視は絶対に書き込まない

監視スクリプトに「ついでに直す」処理を足したくなりますが、やめてください。

読み取り専用に徹すれば、**監視が原因で壊れることが構造的にありえなくなります**。実際、監視ワークフローの権限は `contents: read` にしてあります。書き込む権限を持たせていません。

自動修復が必要なら、それは監視とは別の仕組みとして作ってください。

## 応用・次の一手

**まず1項目から始めてください。**「トップページの更新日が今日か」だけで、静かな故障の8割は捕まります。完璧な監視を設計しようとして作らずに終わるより、雑でも今日動かすほうが100倍マシです。

慣れてきたら、監視対象を「自動化そのもの」に広げます。ワークフローの最終成功時刻、生成されたファイルの更新時刻、届いたメールの件数。**「動いているはず」を「動いていることを確認済み」に変えていく**作業です。

自動化を増やすほど、この仕組みの価値は上がります。10本の自動化を人間が毎朝目視で確認するのは無理ですが、10本を1本の監視で見るのは簡単だからです。
