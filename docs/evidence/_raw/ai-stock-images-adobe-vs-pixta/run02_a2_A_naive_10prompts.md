# run02 — 指示文A（禁止項目を渡さずに10本）2回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

ストック素材サイトに出品するためのAI画像用プロンプトを、英語で10本作ってください。売れやすい人気のテーマとスタイルを選び、画像生成AIにそのまま貼れる形でお願いします。

## 返ってきたもの（生・tool_uses: 0・70,529 tokens・77秒）

ストック素材で継続的に売れやすいのは「ビジネス」「背景・抽象」「テクノロジー」「サステナビリティ」「ライフスタイル」「食」「季節もの」「イラスト」「商品モックアップ」あたりです。以下、そのままコピーして貼れる形で10本まとめました。

## 1. ビジネス（多様なチームの打ち合わせ）
```
Diverse group of young professionals collaborating around a laptop in a bright modern open-plan office, large windows with soft natural daylight, glass walls and green plants, candid natural expressions, relaxed business casual clothing, editorial corporate photography, shot on 35mm lens, shallow depth of field, clean neutral color palette, photorealistic, high resolution, 3:2 aspect ratio, no text, no logos, no watermarks
```

## 2. リモートワーク（在宅で働く女性）
```
Woman in her thirties working from home on a laptop at a wooden desk by a window, cozy Scandinavian interior with houseplants and a mug of coffee, warm morning sunlight, relaxed genuine smile, lifestyle photography, 50mm lens, soft natural light, muted warm tones, photorealistic, sharp focus, 3:2 aspect ratio, no text, no logos, no brand names
```

## 3. 抽象背景（コピースペース付き）
```
Abstract background of soft flowing gradient waves in pastel blue, lavender and peach, smooth silky shapes, minimal and elegant, subtle grain, plenty of empty copy space in the center, suitable for presentation slides and web banners, clean modern design, ultra high resolution, 16:9 aspect ratio, no text, no objects, no watermarks
```

## 4. AI・データのコンセプト
```
Futuristic concept of artificial intelligence and data networks, glowing blue and cyan nodes connected by thin light lines forming a neural network, dark navy background with depth of field, floating particles, sleek 3D render, cinematic lighting, high-tech and clean, copy space on the left side, ultra detailed, 16:9 aspect ratio, no text, no logos, no human faces
```

## 5. 再生可能エネルギー（ドローン俯瞰）
```
Aerial drone view of a large solar farm and wind turbines on rolling green hills at golden hour, long soft shadows, clear sky with a few clouds, renewable energy and sustainability concept, wide angle, crisp detail, natural colors, photorealistic landscape photography, 16:9 aspect ratio, no text, no logos
```

## 6. ヘルシー朝食のフラットレイ
```
Top-down flat lay of a healthy breakfast on a light marble table: granola bowl with fresh berries and yogurt, avocado toast, a glass of orange juice and a small bouquet of flowers, bright airy natural light, clean minimal styling, soft shadows, fresh and appetizing, food photography, high resolution, 1:1 aspect ratio, no text, no packaging, no brand names
```

## 7. ウェルネス（朝のヨガ・瞑想）
```
Woman practicing yoga in a peaceful seated meditation pose on a wooden deck overlooking calm water at sunrise, soft golden light and light mist, minimal composition with lots of negative space, wellness and mindfulness concept, calm pastel tones, shot from behind, lifestyle photography, 3:2 aspect ratio, no text, no logos
```

## 8. フラットベクター風イラスト（チームワーク）
```
Flat vector illustration of a diverse team of people assembling large puzzle pieces together, teamwork and collaboration concept, simple geometric shapes, limited palette of navy, coral, mustard and off-white, clean lines, minimal shading, plain white background, modern corporate illustration style, suitable for websites and presentations, 16:9 aspect ratio, no text, no logos
```

## 9. 商品モックアップ（無地の化粧品ボトル）
```
Minimal product mockup of a blank white cosmetic bottle and jar standing on a round beige stone podium, soft studio lighting with gentle shadow, natural elements like a dried palm leaf and a small pebble, warm neutral background, elegant skincare branding presentation, 3D render, photorealistic, high resolution, 1:1 aspect ratio, no label text, no logos
```

## 10. 季節もの（クリスマス背景・コピースペース付き）
```
Christmas holiday background with a softly blurred decorated fir tree and warm golden bokeh lights, wrapped gift boxes in the foreground, cozy festive atmosphere, wide empty copy space on the right side for text, shallow depth of field, warm red and gold tones, photorealistic, 16:9 aspect ratio, no text, no logos, no characters
```

## 使うときのコツ

- **Midjourney** なら末尾の「16:9 aspect ratio」等を `--ar 16:9` に置き換え、`--no text, logo, watermark` を付けると安定します。**Stable Diffusion系**なら「no text, no logos...」の部分を外し、ネガティブプロンプト欄に `text, watermark, logo, signature, blurry, deformed hands, extra fingers, lowres` を入れてください。
- **文字は画像に入れない。** AIは文字が崩れやすく、審査で落ちる定番の原因です。代わりに「copy space（余白）」を指定すると、購入者が自分で文字を載せられるので売れやすくなります。
- **実在のブランド・ロゴ・有名人・キャラクター・著名建築物は避ける。** 知的財産の理由で却下されます。人物は「架空の人物」として生成し、特定の誰かに似せないでください。
- **手・指・目のアップは要チェック。** 生成後に拡大して崩れがないか確認し、必要なら再生成やアップスケールをかけてから出品します。
- **サイトごとにAI画像の扱いが違います。** 私の知る範囲では、Adobe Stock は「生成AI」と申告すれば受け付け、一方で受け付けないサイト（Getty/iStock など）もあります。出品先の最新の規約を先に確認してください。
