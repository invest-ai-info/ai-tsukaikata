# run09 — 指示文C（材料を渡す・3,000円×100本）3回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

Udemyの公式ヘルプ（英語）で確認した情報を貼ります。これ以外の数字は使わないでください。

・Sales occurring through instructor promotions: instructors receive 97% of the revenue when the student purchases their content using an instructor's coupon or referral link.
・Sales that do not occur through an instructor promotion: instructors receive 37% of the revenue for any Udemy sales where no instructor coupon or course referral link was used.
・these are revenue shares on the Net Amount, which is the amount a student paid less any applicable taxes or fees, such as the 30% fee imposed by Apple or Google for sales on iOS and Android.
・Each month, Udemy allocates 15% of monthly subscription revenue from Udemy Business customers as the instructor revenue pool. Each instructor's share of this amount is equal to their share of the total minutes consumed across all Udemy Business courses.

3,000円の講座が1か月に100本売れたとして、①全部が私の紹介リンク経由だった場合 ②全部がUdemyの検索経由（紹介リンクなし）だった場合、それぞれ講師の取り分を計算してください。iOS・Androidアプリ経由の販売はゼロで、税も考えないものとします。上に無い数字は使わず、必要なら「材料に無い」と書いてください。

## 返ってきたもの（生・tool_uses: 0・68,091 tokens・41秒）

**前提（材料から確定できるもの）**

- 売上総額＝3,000円 × 100本＝300,000円
- 取り分の計算基準は「Net Amount」＝受講生が払った額から税・手数料（例：Apple/Googleの30%）を引いた額。今回は「税は考えない」「アプリ経由ゼロ」なので差し引くものがなく、**Net Amount＝300,000円（1本あたり3,000円）**として計算します。

**① 全部が自分の紹介リンク（クーポン／リファラルリンク）経由の場合：97%**

- 1本あたり：3,000円 × 0.97＝**2,910円**
- 100本：300,000円 × 0.97＝**291,000円**
- （Udemy側の取り分：9,000円）

**② 全部がUdemyの検索経由（紹介リンクなし）の場合：37%**

- 1本あたり：3,000円 × 0.37＝**1,110円**
- 100本：300,000円 × 0.37＝**111,000円**
- （Udemy側の取り分：189,000円）

**①と②の差：180,000円**（同じ100本でも、紹介リンク経由のほうが約2.6倍になります）

**材料に無いもの（上の計算には入れていません）**

- **Udemy Businessの分配プール**：材料には「月間サブスク収入の15%をプールにし、全講座の視聴分数に占める自分の講座の分数シェアで配分」とありますが、この講座がUdemy Businessに入っているか、月のサブスク収入総額、視聴分数のシェアが材料に無いので、金額は計算できません。①②とは別枠の収入です。
- **3,000円が「実際に払われた額」かどうか**：Net Amountは「受講生が払った額」基準です。割引などで払った額が3,000円と違えば、その実額に97%／37%を掛けることになります。割引の扱いは材料に無いので、上の計算は「全員が3,000円を払った」前提です。
- **Apple/Google以外の手数料**：材料は「such as（例えば）」として30%の例を挙げているだけで、それ以外の手数料の有無・率は材料に無いため、今回はゼロとして計算しています。
- **講師への支払い時の振込手数料・為替**：材料に無いので、実際に口座に入る額は上の数字と一致しない可能性があります。
