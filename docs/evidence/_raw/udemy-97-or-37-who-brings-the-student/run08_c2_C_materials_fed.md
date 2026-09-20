# run08 — 指示文C（材料を渡す・3,000円×100本）2回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

Udemyの公式ヘルプ（英語）で確認した情報を貼ります。これ以外の数字は使わないでください。

・Sales occurring through instructor promotions: instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.
・Sales that do not occur through an instructor promotion: instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.
・these are revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google for sales on iOS and Android.
・Each month, Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed across all Udemy Business courses.

3,000円の講座が1か月に100本売れたとして、①全部が私の紹介リンク経由だった場合 ②全部がUdemyの検索経由（紹介リンクなし）だった場合、それぞれ講師の取り分を計算してください。iOS・Androidアプリ経由の販売はゼロで、税も考えないものとします。上に無い数字は使わず、必要なら「材料に無い」と書いてください。

## 返ってきたもの（生・tool_uses: 0・68,125 tokens・41秒）

**前提の整理**

- 学生が支払った金額の合計: 3,000円 × 100本 = 300,000円
- iOS・Android経由の販売がゼロで税も考えないので、差し引くものが無く、Net Amount = 300,000円（1本あたり3,000円）のまま率をかけます

**① 全部が自分の紹介リンク（またはクーポン）経由 → 97%**

| | 計算 | 講師の取り分 |
|---|---|---|
| 1本あたり | 3,000円 × 97% | 2,910円 |
| 100本 | 300,000円 × 97% | **291,000円** |

**② 全部がUdemyの検索経由（紹介リンクなし） → 37%**

| | 計算 | 講師の取り分 |
|---|---|---|
| 1本あたり | 3,000円 × 37% | 1,110円 |
| 100本 | 300,000円 × 37% | **111,000円** |

同じ100本でも、経路の違いだけで 291,000円 − 111,000円 = **180,000円** の差になります。

**材料に無いこと（上の計算に入れていないもの）**

1. **学生が実際に支払う金額が3,000円かどうか。** 材料は「学生が支払った金額（Net Amount）」に率をかけると書いているだけなので、上の計算は「100人全員が3,000円ちょうど支払った」という仮定です。実際の支払額が違えば、その分だけ結果が変わります。
2. **Apple/Googleの30%以外の手数料。** 材料は「税や手数料（例としてAppleやGoogleの30%）」としか書いておらず、それ以外の手数料があるか、あるとして何%かは材料に無いので、ゼロとして計算しています。
3. **Udemy Business の分配。** 「購読収入の15%を、全講座の視聴分数に占める自分の講座の割合で分配」という仕組みは、①②の講座販売とは別枠です。購読収入の総額も、自分の講座の視聴分数の割合も材料に無いので、金額は計算できません。①②に足しても引いてもいません。
4. **受け取り時の条件**（円で受け取れるか、出金に手数料がかかるか等）も材料に記述が無いので、上の金額は「Udemy側で計算される取り分」であって、手元に入る金額と同じかどうかは材料からは言えません。
