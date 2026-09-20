# run05 — 指示文B（禁止項目を渡して10本）2回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

ストック素材サイトに出品するためのAI画像用プロンプトを、英語で10本作ってください。売れやすい人気のテーマとスタイルを選び、画像生成AIにそのまま貼れる形でお願いします。

ただし、出品先のガイドラインで次のものはプロンプトに使えません。
・アーティスト、実在の人物、架空のキャラクターの名前
・著作権で保護されているクリエイティブ作品への言及
・政府機関名
・サードパーティの知的財産への言及
・コンテンツが実際のニュース価値のある出来事を描写していることを示唆する説明
また、同じプロンプトや似たプロンプトから複数のバージョンを作って出すことも禁止されています。10本はそれぞれ別のテーマにしてください。

## 返ってきたもの（生・tool_uses: 0・71,435 tokens・91秒）

ストック素材で定番的に需要が高いカテゴリ（ビジネス・テクノロジー抽象・風景・料理・人物・インテリア・環境・背景素材・季節・商品モックアップ）から、テーマが重ならないように10本選びました。どれも固有名詞・ブランド・作品名を含まず、AI生成で崩れやすい文字やロゴを出さない指定を入れています。

**1. リモートワーク／ホームオフィス（人物なしのライフスタイル）**
```
Bright minimalist home office workspace, wooden desk beside a large window with soft morning sunlight, open generic laptop with a blank screen, ceramic coffee mug, small potted plant, notebook and pen, neutral beige and white tones, shallow depth of field, lifestyle stock photography, full-frame camera look with a 50mm lens, clean composition with copy space on the left, no people, no text, no logos, no watermarks
```

**2. AI・データネットワークの抽象3D**
```
Abstract 3D visualization of artificial intelligence and data networks, glowing blue and violet nodes connected by thin lines of light, floating in a dark navy space, subtle depth of field, fine particles and soft bloom, futuristic technology concept background, ultra-detailed 3D render, wide horizontal composition with empty space in the center for copy, no text, no letters, no logos
```

**3. 自然風景（朝の山岳湖）**
```
Serene alpine lake at sunrise, perfectly still water mirroring snow-capped mountains and a dense pine forest, thin morning mist drifting over the surface, warm golden light on the peaks and cool blue shadows, ultra-sharp landscape photography, wide-angle lens, high dynamic range, calm and peaceful travel mood, no people, no buildings, no text
```

**4. ヘルシーフードの俯瞰フラットレイ**
```
Overhead flat lay of a healthy vegetarian grain bowl on a rustic wooden table, quinoa, roasted sweet potato, avocado slices, cherry tomatoes, chickpeas, fresh herbs and a lemon wedge, linen napkin and wooden spoon beside the bowl, soft natural window light, vibrant fresh colors, professional food photography, top-down view, clean styling, no text, no labels, no packaging
```

**5. 多様なチームのビジネスシーン（架空の人物）**
```
Diverse group of four young professionals collaborating around a table in a bright modern coworking office, smiling and discussing ideas over a generic tablet whose screen faces away from the camera, large windows with natural light, green plants in the background, candid business lifestyle photography, shallow depth of field, warm and friendly atmosphere, fictional people in plain unbranded clothing, no logos, no text
```

**6. 北欧風リビングのインテリア**
```
Cozy Scandinavian-style living room interior, light oak floor, off-white sofa with textured cushions and a wool throw blanket, round wooden coffee table, large monstera plant, sheer linen curtains letting in soft daylight, plain walls, neutral warm palette, minimalist decor, interior design photography, eye-level wide shot, realistic materials, no people, no text, no framed pictures
```

**7. 再生可能エネルギーの風景（サステナビリティ）**
```
Field of solar panels and tall wind turbines on rolling green hills at golden hour, long soft shadows, clear sky with a few clouds, renewable energy and sustainability concept, aerial drone photography perspective, crisp details, wide horizontal composition, no text, no logos, no vehicles, no people
```

**8. 汎用の抽象グラデーション背景**
```
Smooth abstract background of flowing soft gradient waves in pastel peach, lavender and mint, silky fabric-like folds, gentle light and shadow, modern minimal 3D render, high resolution, seamless feel suitable for web banners and presentation backgrounds, wide 16:9 composition, no text, no objects, no logos
```

**9. クリスマスのギフト俯瞰（季節素材）**
```
Christmas holiday flat lay on a dark green background, kraft paper gift boxes tied with red ribbon, pine branches, pinecones, cinnamon sticks, dried orange slices, small golden baubles, soft warm fairy-light bokeh, top-down view, festive seasonal stock photo with copy space, no text, no figurines, no printed patterns with recognizable imagery
```

**10. 商品撮影用の空の3D台座（ECモックアップ）**
```
Minimal 3D product display scene, empty round white podium on a soft beige backdrop, gentle arched wall behind it, soft studio lighting with a single warm shadow, palm leaf shadow falling on the wall, clean e-commerce mockup style, photorealistic render, centered composition with space for placing a product, no text, no products, no logos
```

補足（出品時のポイント）
- 5番のように人物を含む画像は、出品先で「架空の人物」であることを申告する欄があれば必ずチェックしてください。人物なしのほうが審査は通りやすいので、迷ったら1〜4・6〜10を優先すると安全です。
- 各プロンプト末尾の「no text, no logos」は、AIが生成する文字やロゴが崩れて審査落ちの原因になるのを防ぐためです。お使いのツールがネガティブプロンプト欄や `--no` 指定に対応していれば、そちらに移しても構いません。
- 縦横比は用途に合わせて指定を足してください（例：バナー用は 16:9、SNS用は 1:1）。ツールによっては `--ar 16:9` のような書式になります。
- 同じプロンプトで複数枚生成した中から出品するのは1枚にし、別の1枚を出したい場合はテーマ自体を変えてください（類似バージョンの複数出品はガイドライン違反になります）。
