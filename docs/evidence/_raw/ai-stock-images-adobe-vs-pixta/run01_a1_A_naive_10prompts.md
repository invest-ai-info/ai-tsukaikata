# run01 — 指示文A（禁止項目を渡さずに10本）1回目 — 2026-09-18

## 送った指示文（定型の前置き＋質問。前置きは evidence 本体に記載）

ストック素材サイトに出品するためのAI画像用プロンプトを、英語で10本作ってください。売れやすい人気のテーマとスタイルを選び、画像生成AIにそのまま貼れる形でお願いします。

## 返ってきたもの（生・tool_uses: 0・70,092 tokens・75秒）

ストック素材サイトで売れ筋なのは「ビジネス／リモートワーク」「テクノロジー／AI」「食」「背景・抽象」「ウェルネス」「シニア」「サステナビリティ」「季節もの」「3Dアイコン」「フラットなイラスト」あたりです。各ジャンルから1本ずつ、**余白（copy space）あり・文字なし・ロゴなし**を指定した10本を作りました。そのまま貼って使えます。

---

### 1. ビジネス｜多様なチームのミーティング
```
Diverse group of business professionals collaborating around a laptop in a bright modern open-plan office, natural window light, candid genuine expressions, shallow depth of field, shot on 50mm lens, photorealistic corporate stock photo, clean neutral color palette, generous copy space on the left side, no text, no logos, no watermark
```

### 2. リモートワーク｜自宅で働く女性
```
Young woman working on a laptop at a cozy home desk beside a large window, warm morning sunlight, indoor plants and a ceramic coffee mug, relaxed casual lifestyle mood, photorealistic editorial photography, soft natural tones, shallow depth of field, plenty of negative space, no text, no brand logos
```

### 3. 抽象背景｜テック系グラデーション
```
Abstract futuristic background with flowing glowing blue and violet gradient waves, soft floating light particles, smooth glass-like surfaces, high-end 3D render, ultra high resolution, clean minimal composition suitable as a website hero background, wide horizontal format, no text, no watermark
```

### 4. フード｜ヘルシーボウルの俯瞰
```
Overhead flat lay of a colorful healthy grain bowl with quinoa, avocado, cherry tomatoes, chickpeas and fresh greens on a light marble table, soft diffused daylight, minimalist food photography, vibrant natural colors, crisp details, top-down view, copy space on one side, no text, no watermark
```

### 5. シニア｜タブレットを使う夫婦
```
Happy senior couple in their 70s sitting on a sofa and using a tablet together, laughing naturally, bright living room with soft daylight, warm and welcoming atmosphere, photorealistic lifestyle stock photo, natural skin tones, shallow depth of field, copy space on the right, no text, no logos
```

### 6. イラスト｜AI・DXのアイソメトリック
```
Isometric flat vector illustration of a small business team using AI and cloud technology, people working on laptops, floating charts, chatbot icons and a friendly robot assistant, clean modern style, soft pastel palette with blue accents, plain white background, no text, no logos, high resolution
```

### 7. ウェルネス｜朝の瞑想
```
Woman practicing yoga meditation on a wooden deck at sunrise, calm ocean in the background, soft golden light, peaceful atmosphere, wellness and self-care concept, photorealistic lifestyle photography, muted natural tones, wide composition with copy space, no text, no watermark
```

### 8. 3Dアイコンセット｜ビジネス・金融
```
Set of six 3D rendered minimalist icons for business and finance: shopping cart, credit card, rising bar chart, target with arrow, lightbulb, calendar; soft clay style, pastel colors, smooth rounded shapes, gentle studio lighting, each icon isolated on a plain white background, clean and modern, no text
```

### 9. サステナビリティ｜再生可能エネルギー
```
Wind turbines and solar panels across green rolling fields under a clear blue sky, soft morning light, sustainable clean energy concept, photorealistic aerial drone perspective, crisp details, hopeful and clean mood, wide horizontal composition, no people, no text, no logos
```

### 10. 季節もの｜ミニマルなクリスマス背景
```
Minimalist Christmas background with a small fir tree, warm golden bokeh lights and gently falling snow, neutral beige and white color palette, cozy Scandinavian style, soft product-photography lighting, large empty copy space in the center, no text, no watermark
```

---

### 使うときのコツ

- **縦横比の指定**は各ツールの流儀で足してください。Midjourney なら末尾に `--ar 16:9`、Stable Diffusion 系は解像度設定で。横長16:9はWeb用途で一番使われます。
- **Stable Diffusion 系のネガティブプロンプト**（共通で使えます）:
  `text, watermark, logo, signature, blurry, lowres, deformed hands, extra fingers, distorted face, duplicate`
- **「no text」は必須**です。AIが描く文字は崩れるうえ、審査で落ちる主因になります。ロゴ・ブランド品・有名人・実在の建築物やキャラクターも同じ理由で避けてください。
- **人物入りは売れる一方で審査落ちも多い**（指・歯・目の崩れ）。アップロード前に拡大して確認し、崩れがあれば生成し直すか、人物なしの構図に振り替えるのが確実です。
- **出品先の規約を先に確認**してください。Adobe Stock は「生成AIで作成」のチェックを付ければ受け付けますが、Shutterstock・Getty Images・PIXTA などは生成AI画像の投稿を認めていない（または制限している）のが私の知る範囲での状況です。規約は変わるので、投稿前に必ず最新の規定を読んでください。
- **解像度**は最低でも4MP以上（例: 2560×1440）に拡大してから出すと、審査基準をほぼ満たせます。
