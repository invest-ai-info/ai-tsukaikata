// 図（SVG）の文字を、ブラウザで実寸計測して崩れを探す。
//
// src/figures.py はビルドで自動的に走るが、文字幅は推定なので
// 数pxのはみ出しは見逃す（誤検知を出さないため、わざと下限で判定している）。
// こちらは getBBox() の実寸なので厳密。図を足した・直したときに1回流す。
//
// ⚠️ 測る図の一覧を手で書かないこと。2026-08-08 まで18枚を名前で並べていたが、
// そのあいだに図は48枚に増えていて、30枚が黙って測られないまま「問題なし」と
// 出ていた。いまは sitemap.xml → 各ページ → <img> の順にたどって、
// 実際にサイトに貼られている図を全部拾う。記事を足しても直さなくてよい。
//
// 使い方:
//   1. python -m src.build
//   2. プレビュー（http://localhost:8791）を開く
//   3. このファイルの中身をコンソールに貼る、または Claude に
//      「図の厳密計測をして」と頼む
(async () => {
  // ① sitemap から全ページの path を取る（本番URLで書かれているので pathname だけ使う）
  const sitemap = await (await fetch('/sitemap.xml?v=' + Math.random())).text();
  const paths = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)]
    .map(m => new URL(m[1]).pathname);

  // ② 各ページに貼ってある図を集める（同じ図が複数ページにあっても1回だけ測る）
  const used = new Map();   // svgのpath -> それを貼っているページ
  for (const path of paths) {
    const html = await (await fetch(path + '?v=' + Math.random())).text();
    for (const m of html.matchAll(/<img[^>]+src="(\/static\/images\/[^"]+\.svg)"/g)) {
      if (!used.has(m[1])) used.set(m[1], path);
    }
  }

  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:-9999px;top:0;width:900px';
  document.body.appendChild(host);

  const problems = [];
  let texts = 0;

  for (const [src, page] of used) {
    const response = await fetch(src + '?v=' + Math.random());
    if (!response.ok) { problems.push(`${src}: 取得できません（${page} に貼ってある）`); continue; }
    host.innerHTML = await response.text();
    const svg = host.querySelector('svg');
    if (!svg) { problems.push(`${src}: SVGとして読めません`); continue; }
    const name = src.split('/').pop().replace('.svg', '');
    const [, , W, H] = svg.getAttribute('viewBox').split(' ').map(Number);

    // 枠とみなすのは線のある矩形だけ（figures.py と同じ規則）。
    // 角を四角く見せるための当て板は塗りだけなので囲いではない。
    const boxes = [...svg.querySelectorAll('rect')]
      .filter(r => {
        const s = getComputedStyle(r).stroke;
        return s && s !== 'none' && !s.includes('rgba(0, 0, 0, 0)');
      })
      .map(r => ({
        x: +r.getAttribute('x'), y: +r.getAttribute('y'),
        w: +r.getAttribute('width'), h: +r.getAttribute('height'),
      }))
      .filter(b => b.w * b.h < W * H * 0.95);

    for (const t of svg.querySelectorAll('text')) {
      let b;
      try { b = t.getBBox(); } catch (e) { continue; }
      texts++;
      const label = t.textContent.slice(0, 20);
      const right = b.x + b.width, top = b.y, bottom = b.y + b.height;

      if (right > W - 2 || bottom > H - 2 || b.x < -2 || top < -2) {
        problems.push(`${name}: 画面外 「${label}」`);
      }

      const inside = boxes.filter(k =>
        k.x <= b.x + 1 && b.x + 1 <= k.x + k.w &&
        k.y <= +t.getAttribute('y') && +t.getAttribute('y') <= k.y + k.h);
      if (!inside.length) continue;

      const box = inside.reduce((a, c) => (c.w * c.h < a.w * a.h ? c : a));
      if (right > box.x + box.w + 2) {
        problems.push(`${name}: 枠から右へ ${(right - box.x - box.w).toFixed(0)}px 「${label}」`);
      }
      if (top < box.y - 2 || bottom > box.y + box.h + 2) {
        problems.push(`${name}: 枠から上下へ 「${label}」`);
      }
    }
  }

  host.remove();
  return JSON.stringify({
    ページ: paths.length, 図: used.size, 文字要素: texts,
    問題: problems.length, 内訳: problems,
  }, null, 1);
})()
