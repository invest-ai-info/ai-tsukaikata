# run04 — 指示文B（禁止項目を渡して10本）1回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

ストック素材サイトに出品するためのAI画像用プロンプトを、英語で10本作ってください。売れやすい人気のテーマとスタイルを選び、画像生成AIにそのまま貼れる形でお願いします。

ただし、出品先のガイドラインで次のものはプロンプトに使えません。
・アーティスト、実在の人物、架空のキャラクターの名前
・著作権で保護されているクリエイティブ作品への言及
・政府機関名
・サードパーティの知的財産への言及
・コンテンツが実際のニュース価値のある出来事を描写していることを示唆する説明
また、同じプロンプトや似たプロンプトから複数のバージョンを作って出すことも禁止されています。10本はそれぞれ別のテーマにしてください。

## 返ってきたもの（生・tool_uses: 0・73,220 tokens・114秒）

売れ筋のジャンル（ビジネス・食・風景・抽象背景・サステナビリティ・インテリア・商品モックアップ・パターン・ベクターイラスト・季節もの）から1本ずつ選び、テーマもスタイルも重ならないようにしました。各プロンプトは固有名詞・ブランド名・作品名・ソフト名を含みません。

**1. ビジネス／チームワーク（写真・横長）**
```
Photorealistic candid photo of a diverse team of four professionals collaborating around a large table in a bright modern open-plan office, one person pointing at a whiteboard covered with blank colorful sticky notes, others taking notes on laptops and tablets, natural window light, glass walls, green plants in the background, genuine relaxed smiles, shallow depth of field, shot with a 35mm lens, warm neutral color grading, editorial corporate photography, high resolution
```

**2. ヘルシーフード（俯瞰フラットレイ写真・正方形）**
```
Overhead flat lay food photography of a healthy Mediterranean grain bowl with quinoa, roasted chickpeas, cherry tomatoes, cucumber, avocado slices, feta crumbles, and fresh herbs, arranged on a light gray linen tablecloth with a wooden fork, a small bowl of olive oil, and scattered lemon wedges, soft natural daylight from the side, crisp details, vibrant but natural colors, minimalist styling with generous negative space for copy, editorial food magazine style, 4k
```

**3. 自然風景（風景写真・横長）**
```
Breathtaking landscape photograph of a calm alpine lake at sunrise, jagged snow-capped mountain peaks perfectly mirrored in the still water, a thin layer of mist drifting over the surface, pine forest along the shoreline, golden and pink light on the peaks, wide-angle composition, ultra sharp, long exposure feel, high dynamic range, serene and peaceful atmosphere, fine art landscape photography
```

**4. 抽象背景（3Dレンダー・横長）**
```
Abstract 3D render background of soft translucent glass shapes, rounded blobs, tori, and spheres floating gently, pastel gradient of lavender, peach, and mint, frosted glass material with subtle refraction and caustics, soft studio lighting, smooth shadows, clean minimal composition with empty space in the center for text overlay, modern tech website hero banner, physically based rendering, ultra high resolution
```

**5. 再生可能エネルギー（ドローン空撮写真・横長）**
```
Aerial drone photograph of a large solar panel farm and a row of white wind turbines set among rolling green farmland, late afternoon golden hour light casting long shadows, a winding country road, patchwork of fields, clear blue sky with a few soft clouds, angled top-down perspective, crisp detail, renewable energy and sustainability concept, environmental stock photography, high resolution
```

**6. インテリア（建築写真・横長）**
```
Interior design photograph of a bright Scandinavian-style living room, light oak wood floor, cream linen sofa with textured throw pillows, a round wooden coffee table with a ceramic vase of dried pampas grass, large window with sheer white curtains letting in soft daylight, a potted fiddle-leaf fig in the corner, neutral beige and white palette, minimalist and cozy, wide-angle architectural photography, straight vertical lines, realistic materials and textures, 4k
```

**7. 商品モックアップ（スタジオ物撮り・縦長または正方形）**
```
Studio product photograph of an unlabeled frosted glass skincare serum bottle with a matte white dropper cap, standing on a round travertine stone podium, soft beige background, hard sunlight casting crisp palm leaf shadows across the wall, small water droplets on the bottle, minimal luxury cosmetic mockup, centered clean composition, photorealistic, high resolution, commercial beauty advertising style
```

**8. 水彩ボタニカルパターン（イラスト・正方形）**
```
Seamless repeating pattern of delicate hand-painted watercolor wildflowers, chamomile, lavender sprigs, poppies, and eucalyptus leaves, loose brush strokes with soft color bleeding, muted sage green, dusty pink, and cream palette, evenly scattered on a white background, botanical textile and wallpaper design, tileable, flat even lighting, no cast shadows, high resolution
```

**9. オンラインショッピング（フラットベクターイラスト・横長）**
```
Flat vector illustration of an online shopping concept, a young woman sitting cross-legged on a sofa holding a smartphone, a large floating shopping cart icon, parcel boxes, a credit card, price tags, and chat bubbles around her, simple geometric shapes, smooth flat shapes without outlines, cheerful limited palette of coral, teal, mustard yellow, and navy, white background, modern corporate illustration style, ideal for website banners and app onboarding screens
```

**10. クリスマス／季節もの（写真・横長）**
```
Festive Christmas holiday photograph of neatly wrapped gift boxes in kraft paper with red and white ribbons, stacked beside a decorated fir tree, warm fairy lights softly glowing in the background, pine cones, cinnamon sticks, and dried orange slices scattered on a rustic wooden table, cozy warm color tones, shallow depth of field with dreamy bokeh, copy space on the left, seasonal greeting card and advertising style, high resolution
```

**出品前の補足**

- Midjourney なら末尾に `--ar 3:2 --no text, logo, watermark` のように比率と除外指定を足してください。Stable Diffusion 系はネガティブプロンプトに `text, logo, watermark, signature, brand, blurry, deformed hands` を入れると審査落ちが減ります。
- 生成後は、文字やロゴらしきものが写り込んでいないか、人物の手・目・歯、パターンの継ぎ目を拡大して確認してください。AIが描く文字は崩れやすく、ロゴ類は却下の主な原因です。
- 各プロンプトから採用するのは1枚（ベストカット）だけにし、色違いや構図違いを並べて出品しないでください。
- 出品時は「生成AI」の区分にチェックを入れ、サイトごとのAIコンテンツ方針（受け付けていないサイトもあります）を確認してください。
- 10番の季節ものは、需要のピークの2〜3か月前に出すのが定石なので、今の時期の投稿に向いています。
