# 試した証拠 — head-get-disagreement-still-sorts-correctly

キュー：`content/_recipe_queue.md`「自動化・ループ優先」節「同じリンクでHEADとGETが違うコードを
返す場合（例: HEAD=200・GET=404）、リンク切れ判定は誤らないか」（2026-11-16補充）。根拠は、公開済み
`mixed-status-not-misread.md:134`「リンクの本数がもっと多い場合や、1本のリンクで複数のコードが
混在する場合（HEADとGETで違うコードが返るなど）にも同じ結果になるかは、まだ確かめていません」。

実測日: 2026-11-20。実測の相手＝`claude --safe-mode --tools "" --print`（CLAUDE.md・skills・
plugins・履歴を全部無効化した新規プロセス。呼び出しごとに完全に独立したプロセス。会話は継続しない。
リポジトリの外の空のディレクトリで実行。材料＋指示文は標準入力で渡した）。

試したのは[前作](../../content/recipes/mixed-status-not-misread.md)の5つの指示文のうち、
見出しの件数が4回とも崩れなかった最後の版（指示文4＝「500番台を切れている側に含めたい」の節）
だけ。この指示文を1文字も変えずに、HEAD/GET不一致を仕込んだ新しい材料に当てた。

---

## 教材（架空データ）

[前作](../../content/recipes/mixed-status-not-misread.md)と同じ12本構成（真値のカテゴリは
本当に切れている・正常・403・転送・タイムアウト・5xxの6種）をベースに、3本だけHEADとGETに
別々のコードを仕込んだ。ドメイン・題材は前作と重複しないよう新しくした。

生成・真値の定義（`materials.py`、再現用に全文）：

```python
MATERIAL_E = {
    "name": "E（観葉植物の育て方ブログ）",
    "rows": [
        ("L01", "https://leaf-care-diary.jp/2019/watering-mistake",        "404", "404", "broken"),
        ("L02", "https://leaf-care-diary.jp/2020/repotting-signs",         "404", "404", "broken"),
        ("L03", "https://green-corner-notes.jp/guide/light-level-chart",   "200", "200", "ok"),
        ("L04", "https://green-corner-notes.jp/guide/humidity-basics",     "200", "200", "ok"),
        ("L05", "https://plant-tool-market.jp/items/mister-01",            "403", "403", "unverifiable"),
        ("L06", "https://plant-tool-market.jp/items/pot-tray-02",          "403", "200", "ok"),            # 不一致1
        ("L07", "https://green-corner-notes.jp/guide/old-fertilizer-chart","301", "301", "unverifiable"),
        ("L08", "https://leaf-care-diary.jp/archive/2018/pruning-faq",     "302", "404", "broken"),        # 不一致2
        ("L09", "https://plant-tool-market.jp/items/grow-light-03",        "タイムアウト", "タイムアウト", "unverifiable"),
        ("L10", "https://green-corner-notes.jp/guide/soil-mix-ratio",      "タイムアウト", "タイムアウト", "unverifiable"),
        ("L11", "https://leaf-care-diary.jp/2021/pest-signs-early",        "500", "500", "broken"),
        ("L12", "https://plant-tool-market.jp/items/drainage-rock-04",     "200", "503", "broken"),        # 不一致3
    ],
}
# MATERIAL_F は同じ構成でドメインだけキャンプ用品ブログに変更（記事本文に全文掲載）

def truths(material):
    broken = [r[0] for r in material["rows"] if r[4] == "broken"]
    unverifiable = [r[0] for r in material["rows"] if r[4] == "unverifiable"]
    ok = [r[0] for r in material["rows"] if r[4] == "ok"]
    return broken, unverifiable, ok
```

### 仕込みの検証（走らせる前にコードで確認）

```
assert len(mat["rows"]) == 12
assert len(broken) == 5 and len(unverifiable) == 4 and len(ok) == 3
mismatches = [r for r in mat["rows"] if r[2] != r[3]]
assert len(mismatches) == 3
```

実行結果（材料E・F共通）：

```
真値: broken= ['L01', 'L02', 'L08', 'L11', 'L12'] unverifiable= ['L05', 'L07', 'L09', 'L10'] ok(正常)= ['L03', 'L04', 'L06']
```

不一致3本の内訳：L06（HEAD=403・GET=200→真値は正常。HEADだけ見ると403で切れているように見える）、
L08（HEAD=302・GET=404→真値は切れている。HEADだけ見ると転送で生きているように見える）、
L12（HEAD=200・GET=503→真値は切れている。HEADだけ見ると正常に見える）。

### 材料E・F（記事と同一の12本）

```
=== 材料E（観葉植物の育て方ブログ） ===
L01  https://leaf-care-diary.jp/2019/watering-mistake  HEAD=404  GET=404
L02  https://leaf-care-diary.jp/2020/repotting-signs  HEAD=404  GET=404
L03  https://green-corner-notes.jp/guide/light-level-chart  HEAD=200  GET=200
L04  https://green-corner-notes.jp/guide/humidity-basics  HEAD=200  GET=200
L05  https://plant-tool-market.jp/items/mister-01  HEAD=403  GET=403
L06  https://plant-tool-market.jp/items/pot-tray-02  HEAD=403  GET=200
L07  https://green-corner-notes.jp/guide/old-fertilizer-chart  HEAD=301  GET=301
L08  https://leaf-care-diary.jp/archive/2018/pruning-faq  HEAD=302  GET=404
L09  https://plant-tool-market.jp/items/grow-light-03  HEAD=タイムアウト  GET=タイムアウト
L10  https://green-corner-notes.jp/guide/soil-mix-ratio  HEAD=タイムアウト  GET=タイムアウト
L11  https://leaf-care-diary.jp/2021/pest-signs-early  HEAD=500  GET=500
L12  https://plant-tool-market.jp/items/drainage-rock-04  HEAD=200  GET=503

=== 材料F（キャンプ・アウトドア装備ブログ） ===
L01  https://backyard-camp-log.jp/2019/tent-pole-snap  HEAD=404  GET=404
L02  https://backyard-camp-log.jp/2020/zipper-repair-fail  HEAD=404  GET=404
L03  https://gear-weight-notes.jp/guide/pack-weight-basics  HEAD=200  GET=200
L04  https://gear-weight-notes.jp/guide/layering-basics  HEAD=200  GET=200
L05  https://outdoor-supply-depot.jp/items/stove-01  HEAD=403  GET=403
L06  https://outdoor-supply-depot.jp/items/lantern-02  HEAD=403  GET=200
L07  https://gear-weight-notes.jp/guide/old-size-chart  HEAD=301  GET=301
L08  https://backyard-camp-log.jp/archive/2018/knot-guide  HEAD=302  GET=404
L09  https://outdoor-supply-depot.jp/items/cooler-box-03  HEAD=タイムアウト  GET=タイムアウト
L10  https://gear-weight-notes.jp/guide/rain-fly-check  HEAD=タイムアウト  GET=タイムアウト
L11  https://backyard-camp-log.jp/2021/bear-signs-notice  HEAD=500  GET=500
L12  https://outdoor-supply-depot.jp/items/water-filter-04  HEAD=200  GET=503
```

### 送った材料の構成（実際に標準入力で渡した形）

```
（上の材料E または F の12行）

次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETが404、または500番台の場合は、切れていると判断してください。それ以外でGETが200でない場合（301・302・403・タイムアウトなど）は、切れているとは断定せず、確認できないリンクとして分けてください。件数はまだ書かないでください。まず、切れているリンクと確認できないリンクのIDを箇条書きで全部挙げてください。箇条書きが終わったら、最後にそれぞれ「以上、何件」と書いてください。
```

---

## 指示文（記事：AIへの頼み方・材料E・F、言い直し方、応用の全箇所で同一文字列）

### 送った指示文（記事と同一文字列）

```
次は、ブログに貼っているリンクを自動点検した結果です。それぞれのリンクについて、HEADリクエストとGETリクエストの応答コードを記録しています。HEADの応答コードだけでは判断しないでください。HEADが404や403でも、GETが200ならそのリンクは切れていません。GETが404、または500番台の場合は、切れていると判断してください。それ以外でGETが200でない場合（301・302・403・タイムアウトなど）は、切れているとは断定せず、確認できないリンクとして分けてください。件数はまだ書かないでください。まず、切れているリンクと確認できないリンクのIDを箇条書きで全部挙げてください。箇条書きが終わったら、最後にそれぞれ「以上、何件」と書いてください。
```

### 返ってきたもの（生）— 材料E・1回目

```
**切れているリンク**（GETが404、または500番台）

- L01（GET=404）
- L02（GET=404）
- L08（GET=404）
- L11（GET=500）
- L12（GET=503）

以上、5件

**確認できないリンク**（GETが200以外で、404・500番台でもないもの）

- L05（GET=403）
- L07（GET=301）
- L09（GET=タイムアウト）
- L10（GET=タイムアウト）

以上、4件

（L03、L04、L06はGETが200なので切れていません。L06はHEADが403でも、GETが200なので正常です。）
```

### 返ってきたもの（生）— 材料E・2回目

```
**切れているリンク**（GETが404、または500番台）

- L01（GET=404）
- L02（GET=404）
- L08（GET=404）
- L11（GET=500）
- L12（GET=503）

以上、5件

**確認できないリンク**（GETが200以外で、404・500番台でもないもの）

- L05（GET=403）
- L07（GET=301）
- L09（GET=タイムアウト）
- L10（GET=タイムアウト）

以上、4件

※ L03・L04・L06はGETが200なので、切れていないリンクです。L06はHEADが403ですが、GETが200なので切れていません。
```

### 返ってきたもの（生）— 材料F・1回目

```
**切れているリンク**（GETが404または500番台）

- L01
- L02
- L08
- L11
- L12

以上、5件

**確認できないリンク**（GETが200以外で、404・500番台でもないもの）

- L05
- L07
- L09
- L10

以上、4件
```

### 返ってきたもの（生）— 材料F・2回目

```
**切れているリンク**（GETが404または500番台）

- L01（GET=404）
- L02（GET=404）
- L08（GET=404、HEADは302）
- L11（GET=500）
- L12（GET=503、HEADは200）

以上、5件

**確認できないリンク**（GETが200以外で、404・500番台でもないもの）

- L05（GET=403）
- L07（GET=301）
- L09（GET=タイムアウト）
- L10（GET=タイムアウト）

以上、4件

L03・L04・L06の3件はGETが200なので切れていません。L06はHEADが403ですが、GETが200のため問題ありません。
```

### 照合（機械）

判定スクリプト（`judge.py`。見出し直前までの本文から `L\d\d` を正規表現で抜き、
「以上、◯件」の数字と比較。走らせる前に、このスクリプト自体が材料E・Fそれぞれの
正しい真値リストを返すことを確認している＝台帳12番（計測器のほうが壊れる）対策）：

```python
def parse(text):
    idx_broken = text.find("切れているリンク")
    idx_unverif = text.find("確認できないリンク")
    broken_block, unverifiable_block = (
        (text[idx_broken:idx_unverif], text[idx_unverif:])
        if idx_broken < idx_unverif else
        (text[idx_broken:], text[idx_unverif:idx_broken])
    )
    def ids_in(block):
        end = block.find("以上")
        scan = block[:end] if end != -1 else block
        return re.findall(r"L\d\d", scan)
    def headline_count(block):
        end = block.find("以上")
        if end == -1:
            return None
        m = re.search(r"以上[、,]\s*(\d+)\s*件", block[end:end+30])
        return int(m.group(1)) if m else None
    return ids_in(broken_block), headline_count(broken_block), ids_in(unverifiable_block), headline_count(unverifiable_block)
```

実行結果（4回とも）：

| 回 | 切れている（ID／件数） | 確認できない（ID／件数） | 真値と一致 | 見出しと列挙が一致 |
|---|---|---|---|---|
| E-1 | L01,L02,L08,L11,L12／5件 | L05,L07,L09,L10／4件 | ✅ | ✅ |
| E-2 | 同上 | 同上 | ✅ | ✅ |
| F-1 | 同上 | 同上 | ✅ | ✅ |
| F-2 | 同上 | 同上 | ✅ | ✅ |

4回とも、不一致を仕込んだL06（正常側）・L08（切れている側）・L12（切れている側）を含めて
12本すべての分類が真値と一致し、見出しの「以上◯件」と箇条書きの本数もすべて一致した。

### 判定

**採用**。HEAD/GETの不一致を仕込んでも、前作で最も安定していた指示文のまま分類・件数とも崩れなかった。

---

## この記事から出た教訓（`content/_lessons.md` へ）

1. ★320が再発した（件数ズレの心配は、分類を増やさない限りは今回も起きなかった）。新しい教訓としては、
   不一致行への言及（「HEADは◯◯ですがGETが◯◯なので」という自発的な補足）は4回中3回しか付かず、
   材料F・1回目だけ分類は正しいのに補足が無かった。**分類結果とは独立に、説明文の有無は回によって
   変わる**——自動化の正しさの判定に、この補足テキストの有無を使ってはいけない。
