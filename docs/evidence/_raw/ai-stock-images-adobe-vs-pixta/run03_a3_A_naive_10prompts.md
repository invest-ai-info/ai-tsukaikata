# run03 — 指示文A（禁止項目を渡さずに10本）3回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

ストック素材サイトに出品するためのAI画像用プロンプトを、英語で10本作ってください。売れやすい人気のテーマとスタイルを選び、画像生成AIにそのまま貼れる形でお願いします。

## 返ってきたもの（生・tool_uses: 0・71,521 tokens・93秒）

## ストック素材向け・AI画像プロンプト10本（英語・そのまま貼れる形）

売れ筋の定番カテゴリ（ビジネス／テクノロジー／ウェルネス／食／風景／背景素材／季節物／サステナビリティ／金融／商品モックアップ）から1本ずつ選びました。**顔が写らない構図**にしてあるので、モデルリリースの問題や、AI特有の顔・指の崩れを避けやすくしています。Midjourneyなら末尾に `--ar 3:2`（写真）や `--ar 16:9`（バナー用）を足してください。

---

**1. リモートワーク／ビジネス（写真風・顔なし）**
```
Close-up of a person's hands typing on a modern laptop at a clean white desk, a cup of coffee and a small green plant beside it, soft natural window light from the left, minimalist home office, shallow depth of field, shot on 50mm lens, realistic commercial stock photography, bright and airy, neutral tones, no visible face, no text, no logos, no watermark
```

**2. AI・テクノロジー概念（3Dアブストラクト）**
```
Abstract 3D render of a glowing digital neural network, interconnected nodes and light trails forming the silhouette of a human brain, deep navy background with cyan and violet accents, futuristic technology concept, clean composition with copy space on the right side, ultra detailed, octane render, no text, no logos, no watermark
```

**3. ウェルネス／ライフスタイル（写真風・後ろ姿）**
```
Woman seen from behind sitting in a meditation pose on a yoga mat in a bright living room, morning sunlight streaming through large windows, potted plants, calm and peaceful atmosphere, soft pastel tones, wide shot with copy space, realistic lifestyle stock photography, face not visible, no text, no logos
```

**4. ヘルシーフード（俯瞰フラットレイ）**
```
Top-down flat lay of a colorful healthy grain bowl with quinoa, avocado, cherry tomatoes, chickpeas and fresh greens on a rustic wooden table, linen napkin and wooden fork beside it, soft natural daylight, vibrant yet natural colors, professional food photography, sharp focus, no text, no logos
```

**5. 風景（バナー・壁紙向け）**
```
Breathtaking wide-angle landscape of misty mountain peaks at sunrise, layers of fog in the valleys, golden light breaking through clouds, pine forest in the foreground, epic and serene mood, high dynamic range, ultra sharp, professional travel photography, 16:9 composition, no people, no text
```

**6. 抽象背景（プレゼン・Web用。最も回転が速い定番）**
```
Smooth abstract gradient background with soft flowing waves in pastel pink, lavender and light blue, subtle grain texture, minimal and elegant, ideal for presentation slides and website hero banners, high resolution, no text, no objects, no logos
```

**7. クリスマス（季節物・需要は9〜11月に集中）**
```
Cozy Christmas flat lay on a white wooden table, gift boxes wrapped in kraft paper with red ribbon, pine branches, cinnamon sticks, dried orange slices and warm string lights, top-down view, soft warm lighting, festive yet minimal Scandinavian style, copy space in the center, no text, no logos
```

**8. サステナビリティ／再生可能エネルギー**
```
Close-up of hands gently holding a small green seedling in rich soil, blurred solar panels and wind turbines in the background under a clear blue sky, sustainability and renewable energy concept, warm golden hour light, shallow depth of field, realistic commercial photography, no face, no text, no logos
```

**9. 金融・成長イメージ（アイソメトリック3D）**
```
Isometric 3D illustration of a rising bar chart with an upward arrow, stacks of plain gold coins and a small growing plant, soft blue and white color palette, clean minimal business and finance growth concept, studio lighting, smooth clay render style, plenty of negative space, no text, no currency symbols, no logos
```

**10. 商品ディスプレイ用ポディウム（コスメ・EC向けモックアップ）**
```
Minimal 3D product display podium, round beige cylinder stage on a soft cream background, natural sunlight casting palm leaf shadows on the wall, empty podium ready for cosmetic product placement, warm neutral tones, photorealistic render, centered composition, no product, no text, no logos
```

---

### 出品前に押さえておきたい点

- **投稿先の規約を先に確認。** Adobe Stock・Freepik・Dreamstime は「AI生成」と申告すれば受け付けますが、Shutterstock・Getty/iStock・PIXTA は外部の生成AI画像を受け付けていません（規約は変わるので投稿直前に最新版を見てください）。
- **文字・ロゴ・実在ブランドを入れない。** AIの文字は崩れやすく、ロゴや商標は審査で落ちます。プロンプトの `no text, no logos` はそのためです。
- **写実的な人物はリリースが必要になることがある。** Adobe Stock では架空の人物でもモデルリリースを求められるため、上の10本は顔を出さない構図にしています。
- **解像度を上げてから出す。** 多くの生成AIは1024px前後（約1MP）で出力しますが、Adobe Stock は最低4MP必要です。アップスケールしてから投稿してください。
- **手・指・物の重なりを目視で確認。** 指の本数や不自然な接合は審査落ちの定番理由です。
- **タイトルとキーワードは英語で丁寧に。** 売れるかどうかは画像そのものと同じくらい、検索に引っかかるかで決まります。
