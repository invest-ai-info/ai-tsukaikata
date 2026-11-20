# -*- coding: utf-8 -*-
"""review-reply-batch-note-leaks-all-names の証拠を機械で数え直す確認スクリプト。
記事化はしない（ファイル名の `_` でビルド対象外。content/ の外にも置いている）。
"""

TOKENS = {
    1: {"C": "久美子", "S": "4番個室", "N": "田辺"},
    2: {"C": "沙織", "S": "2番チェア", "N": "森田"},
    3: {"C": "麻衣子", "S": "5番ブース", "N": "清水"},
}

NAIVE = [
    {
        1: "口コミ1は久美子様・4番個室・田辺のお名前が書かれていましたが返信本文には入れていません。",
        2: "口コミ2は沙織様・2番チェア・森田のお名前が書かれていましたが同様に入れていません。",
        3: "口コミ3は麻衣子様・5番ブース・清水のお名前についても入れていません。",
    },
    {
        1: "口コミ1：久美子様・4番個室・田辺（本文未記載）",
        2: "口コミ2：沙織様・2番チェア・森田（本文未記載）",
        3: "口コミ3：麻衣子様・5番ブース・清水（本文未記載）",
    },
    {
        1: "口コミ1は久美子様・4番個室のお名前が出ていましたが本文には入れていません。",
        2: "口コミ2は沙織様・清水のお名前が出ていましたが入れていません。",
        3: "口コミ3は麻衣子様・5番ブース・森田のお名前についても入れていません。",
    },
    {
        1: "口コミ1：久美子様・4番個室・田辺（本文未記載）。",
        2: "口コミ2：沙織様・2番チェア・森田（本文未記載）。",
        3: "口コミ3：麻衣子様・5番ブース・清水（本文未記載）。",
    },
    {
        1: "口コミ1は久美子様・4番個室・田辺のお名前が出ていましたが入れていません。",
        2: "口コミ2は沙織様・2番チェア・清水のお名前が出ていましたが入れていません。",
        3: "口コミ3は麻衣子様・5番ブース・森田のお名前についても入れていません。",
    },
    {
        1: "口コミ1：久美子様・4番個室・田辺（未記載）。",
        2: "口コミ2：沙織様・2番チェア・森田（未記載）。",
        3: "口コミ3：麻衣子様・5番ブース・清水（未記載）。",
    },
]

GUARDED = [
    {1: "お祝いの席のお手伝いができ嬌しく思います。返信案です。お名前・個室や座席の番号・スタッフ名などの個人情報は入れていません。",
     2: "これからも丁寧な対応を心掛けてまいります。返信案です。お名前・個室や座席の番号・スタッフ名などの個人情報は入れていません。",
     3: "今後とも変わらぬ品質を目指します。返信案です。お名前・個室や座席の番号・スタッフ名などの個人情報は入れていません。"},
    {1: "3件とも、個人情報に当たる内容は入れていません。", 2: "3件とも、個人情報に当たる内容は入れていません。",
     3: "3件とも、個人情報に当たる内容は入れていません。"},
    {1: "いずれも個人情報は記載していません。", 2: "いずれも個人情報は記載していません。",
     3: "いずれも個人情報は記載していません。"},
    {1: "3件とも個人情報には触れていません。", 2: "3件とも個人情報には触れていません。",
     3: "3件とも個人情報には触れていません。"},
    {1: "個人情報に当たる内容は3件とも入れていません。", 2: "個人情報に当たる内容は3件とも入れていません。",
     3: "個人情報に当たる内容は3件とも入れていません。"},
    {1: "口コミ1は個人情報に当たる内容を入れていません。",
     2: "口コミ2は個人情報に当たる内容を入れていません。",
     3: "口コミ3についても個人情報は入れていませんが、担当いたしました清水の対応にご満足いただけたとのお言葉を頂戴し、大変嬌しく思います。"},
]


def tally(sections_by_review: dict) -> tuple[int, int]:
    """sections_by_review: {review_no: text, ...}（ノートも含めて review ごとに束ねたもの）
    戻り値: (own_leak_count, cross_count)
    """
    own, cross = 0, 0
    for owner, toks in TOKENS.items():
        for tok in toks.values():
            own_hit = tok in sections_by_review.get(owner, "")
            cross_hit = any(
                tok in sections_by_review.get(other, "")
                for other in TOKENS
                if other != owner
            )
            if own_hit:
                own += 1
            if cross_hit:
                cross += 1
    return own, cross


def run():
    print("=== 素朴な一括依頼 ===")
    total_own, total_cross, cross_trials = 0, 0, 0
    for i, trial in enumerate(NAIVE, start=1):
        own, cross = tally(trial)
        total_own += own
        total_cross += cross
        if cross:
            cross_trials += 1
        print(f"試行{i}: 単体漏えい {own}/9　混線 {cross}")
    print(f"合計: 単体漏えい {total_own}/54（{total_own/54:.1%}）　"
          f"混線が起きた試行 {cross_trials}/6（{cross_trials/6:.1%}）　混線件数 {total_cross}")

    print("\n=== 「個人情報には触れないでください」追加 ===")
    total_own, total_cross, cross_trials = 0, 0, 0
    for i, trial in enumerate(GUARDED, start=1):
        own, cross = tally(trial)
        total_own += own
        total_cross += cross
        if cross:
            cross_trials += 1
        print(f"試行{i}: 単体漏えい {own}/9　混線 {cross}")
    print(f"合計: 単体漏えい {total_own}/54（{total_own/54:.1%}）　"
          f"混線が起きた試行 {cross_trials}/6（{cross_trials/6:.1%}）　混線件数 {total_cross}")


PAIR_TOKENS = {1: TOKENS[1], 2: TOKENS[2]}

PAIR_NAIVE = [
    {1: "口コミ1は久美子様・4番個室・田辺のお名前が出ていましたが入れていません。",
     2: "口コミ2は沙織様・2番チェア・森田のお名前についても入れていません。"},
    {1: "口コミ1は久美子様・4番個室のお名前が出ていましたが入れていません。",
     2: "口コミ2は沙織様・2番チェア・田辺のお名前が出ていましたが入れていません。"},
]

PAIR_GUARDED = [
    {1: "返信案です。個人情報は入れていません。", 2: "返信案です。個人情報は入れていません。"},
    {1: "こちらも個人情報は入れていません。", 2: "こちらも個人情報は入れていません。"},
]


def tally_pair(sections_by_review: dict) -> tuple[int, int]:
    own, cross = 0, 0
    for owner, toks in PAIR_TOKENS.items():
        for tok in toks.values():
            own_hit = tok in sections_by_review.get(owner, "")
            cross_hit = any(
                tok in sections_by_review.get(other, "")
                for other in PAIR_TOKENS
                if other != owner
            )
            if own_hit:
                own += 1
            if cross_hit:
                cross += 1
    return own, cross


def run_pair():
    print("\n=== 2件ずつに分けた版（口コミ1・2のみ）・ガードなし ===")
    for i, trial in enumerate(PAIR_NAIVE, start=1):
        own, cross = tally_pair(trial)
        print(f"試行{i}: 単体漏えい {own}/6　混線 {cross}")

    print("\n=== 2件ずつに分けた版・ガードあり ===")
    for i, trial in enumerate(PAIR_GUARDED, start=1):
        own, cross = tally_pair(trial)
        print(f"試行{i}: 単体漏えい {own}/6　混線 {cross}")


NAME_SPEC = [
    {1: "口コミ1・2・3とも、ご指定の同伴者名・座席や個室やブースの番号・スタッフの実名は入れていません。"},
    {1: "3件とも、ご指定の項目は本文に入れていません。"},
    {1: "3件とも、ご指定の項目は本文に入れていません。説明も省略します。"},
]


def run_name_spec():
    print("\n=== 伏せる項目を名前で指定する・一括版 ===")
    all_tokens = [tok for toks in TOKENS.values() for tok in toks.values()]
    for i, trial in enumerate(NAME_SPEC, start=1):
        text = trial[1]
        leaked = sum(1 for tok in all_tokens if tok in text)
        print(f"試行{i}: 単体漏えい {leaked}/9　混線 0（取り違え得る複数口コミへの個別言及が無いため該当なし）")


if __name__ == "__main__":
    run()
    run_pair()
    run_name_spec()
