# run06 — 指示文B（禁止項目を渡して10本）3回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

ストック素材サイトに出品するためのAI画像用プロンプトを、英語で10本作ってください。売れやすい人気のテーマとスタイルを選び、画像生成AIにそのまま貼れる形でお願いします。

ただし、出品先のガイドラインで次のものはプロンプトに使えません。
・アーティスト、実在の人物、架空のキャラクターの名前
・著作権で保護されているクリエイティブ作品への言及
・政府機関名
・サードパーティの知的財産への言及
・コンテンツが実際のニュース価値のある出来事を描写していることを示唆する説明
また、同じプロンプトや似たプロンプトから複数のバージョンを作って出すことも禁止されています。10本はそれぞれ別のテーマにしてください。

## 返ってきたもの（生・tool_uses: 0・69,677 tokens・68秒）

ストックサイトで需要が安定している10ジャンル（ビジネス・抽象背景・食・風景・テクノロジー・ウェルネス・インテリア・再生可能エネルギー・商品モックアップ・ペット）から1本ずつ作りました。固有名詞・ブランド・作品名・報道を連想させる描写は一切入れず、末尾に「no text, no logo, no watermark」を付けて商標や文字の混入を防いでいます。そのままコピーして貼れます。

---

**1. ビジネス（チームワーク）**
```
Diverse group of young professionals collaborating around a laptop in a bright modern open-plan office, large windows with soft natural daylight, green plants, candid smiling expressions, shallow depth of field, 50mm lens, clean corporate lifestyle photography, high resolution, no text, no logo, no watermark
```

**2. 抽象背景（バナー用）**
```
Abstract 3D background with smooth flowing glossy waves in a gradient of deep blue, purple and teal, soft studio lighting, subtle grain, minimalist futuristic design, wide composition with plenty of empty space for text, ultra high resolution render, no text, no logo, no watermark
```

**3. フード（俯瞰の朝食）**
```
Overhead flat lay of a healthy breakfast bowl with yogurt, fresh blueberries, sliced strawberries, granola and a drizzle of honey, on a light gray linen tablecloth, soft morning window light, minimal props, natural colors, editorial food photography, sharp focus, no text, no logo, no watermark
```

**4. 風景（山と湖の朝）**
```
Serene mountain lake at sunrise with mist rising over calm water, pine forest reflected in the surface, soft pink and golden sky, ultra wide angle landscape photography, crisp detail, tranquil atmosphere, no people, no text, no watermark
```

**5. テクノロジー（AI・データの概念図）**
```
Conceptual illustration of artificial intelligence and data networks, glowing neural network of connected nodes and lines floating above a dark navy background, subtle cyan and orange light accents, clean isometric digital art style, generous negative space for headlines, high resolution, no text, no logo, no watermark
```

**6. ウェルネス（ヨガ）**
```
Woman practicing yoga in tree pose on a quiet beach at golden hour, silhouette against a warm sunset sky, gentle waves, sense of calm and balance, cinematic backlight, medium telephoto lens, lifestyle photography, no text, no logo, no watermark
```

**7. インテリア（北欧風リビング）**
```
Scandinavian style living room interior with light oak wooden floor, beige linen sofa, white walls, large window with sheer curtains, potted monstera plant, minimalist decor, soft daylight, wide angle architectural photography, photorealistic, no text, no logo, no watermark
```

**8. 再生可能エネルギー**
```
Field of solar panels and white wind turbines under a clear blue sky with soft clouds, rolling green hills in the background, bright sunny day, clean renewable energy concept, aerial drone perspective, sharp and vibrant colors, no text, no logo, no watermark
```

**9. 商品モックアップ（無地のコスメボトル）**
```
Minimalist product photography of a blank frosted glass cosmetic bottle with a wooden cap on a round stone podium, beige background, soft shadows, a few dried pampas grass stems, neutral natural tones, studio lighting, clean space for branding, ultra realistic, no text, no logo, no watermark
```

**10. ペット（子犬）**
```
Golden retriever puppy sitting on a white bed in soft morning light, fluffy fur detail, joyful expression, pastel bedroom background, shallow depth of field, cute pet photography, high resolution, no text, no logo, no watermark
```

---

**出品前に確認しておくとよい点**

- **縦横比はツール側で指定**してください（例: 1と5は横長の16:9、3と9は正方形1:1が使いやすい）。プロンプト本文には特定ツール専用の記号を入れていません。
- ネガティブプロンプトが使えるツールなら、`text, watermark, logo, signature, blurry, deformed hands, extra fingers` を入れると失敗が減ります。
- 生成後に**手の指・文字っぽい模様・ロゴ風の形**が混ざっていないか必ず目で確認してください。AI画像で却下される原因の大半はここです。
- 人物は架空でも「実在の人物に似ている」と判断されることがあります。1・6のような人物入りは、顔が特定の誰かを思わせないか確認してから出すと安全です。
- 同じプロンプトの色違い・構図違いを複数出すのは禁止なので、量を増やしたいときは**ジャンル自体を変える**（例: 教育・医療・季節行事・リモートワーク）方向で追加してください。
