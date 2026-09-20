# run07 — 指示文C（材料を渡す・3,000円×100本）1回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

Udemyの公式ヘルプ（英語）で確認した情報を貼ります。これ以外の数字は使わないでください。

・Sales occurring through instructor promotions: instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.
・Sales that do not occur through an instructor promotion: instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.
・these are revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google for sales on iOS and Android.
・Each month, Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed across all Udemy Business courses.

3,000円の講座が1か月に100本売れたとして、①全部が私の紹介リンク経由だった場合 ②全部がUdemyの検索経由（紹介リンクなし）だった場合、それぞれ講師の取り分を計算してください。iOS・Androidアプリ経由の販売はゼロで、税も考えないものとします。上に無い数字は使わず、必要なら「材料に無い」と書いてください。

## 返ってきたもの（生・tool_uses: 0・67,529 tokens・33秒）

**前提の整理**

- 売上合計：3,000円 × 100本 = 300,000円
- iOS・Android経由の販売がゼロで、税も考えないので、差し引く手数料・税が無い。したがって取り分の計算の土台になる「Net Amount（受講生の支払額から税や手数料を引いた額）」は 300,000円 そのまま（1本あたり3,000円）。

**① 全部が自分の紹介リンク（またはクーポン）経由の場合：97%**

- 1本あたり：3,000円 × 97% = 2,910円
- 100本：2,910円 × 100 = **291,000円**（= 300,000円 × 0.97）

**② 全部がUdemyの検索経由（紹介リンク・クーポンなし）の場合：37%**

- 1本あたり：3,000円 × 37% = 1,110円
- 100本：1,110円 × 100 = **111,000円**（= 300,000円 × 0.37）

**両者の差**

291,000円 − 111,000円 = 180,000円。同じ100本でも、経路だけで取り分が180,000円変わります（比率は 97 ÷ 37 ≈ 2.6倍）。

**材料に無いため、計算に入れていないもの**

- 3,000円が「受講生が実際に支払った額」かどうか。受講生が3,000円より安い価格で買った場合はNet Amountが変わりますが、材料にはその点の記述が無いので、ここでは3,000円がそのまま支払額と仮定しています。
- Udemy Business向けの配分（月額サブスク収入の15%を、全講座の視聴分数に占める自分の講座の割合で分ける仕組み）は、上の100本の販売とは別枠です。配分元の総額と自分の視聴分数の割合が材料に無いので、金額は出せません。①②にも含めていません。
- 送金時の手数料や為替など、材料に書かれていない項目は考慮していません。
