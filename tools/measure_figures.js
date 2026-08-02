// 図（SVG）の文字を、ブラウザで実寸計測して崩れを探す。
//
// src/figures.py はビルドで自動的に走るが、文字幅は推定なので
// 数pxのはみ出しは見逃す（誤検知を出さないため、わざと下限で判定している）。
// こちらは getBBox() の実寸なので厳密。図を足した・直したときに1回流す。
//
// 使い方:
//   1. python -m src.build
//   2. プレビュー（http://localhost:8791）を開く
//   3. このファイルの中身をコンソールに貼る、または Claude に
//      「図の厳密計測をして」と頼む
(async () => {
  const files = [
    'tracker-flow', 'tracker-bootstrap', 'tracker-mail', 'github-settings',
    'cron-fields', 'cron-congestion', 'cron-redundancy', 'actions-run-workflow',
    'yt-pipeline', 'yt-transcript-fallback', 'yt-shorts',
    'health-silent-failure', 'health-checks', 'health-timing', 'health-issue',
    'memory-layout', 'memory-what-to-write', 'memory-file-anatomy',
  ];

  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:-9999px;top:0;width:900px';
  document.body.appendChild(host);

  const problems = [];
  let texts = 0;

  for (const name of files) {
    const source = await (await fetch(`/static/images/${name}.svg?v=` + Math.random())).text();
    host.innerHTML = source;
    const svg = host.querySelector('svg');
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
  return JSON.stringify({ 図: files.length, 文字要素: texts, 問題: problems.length, 内訳: problems }, null, 1);
})()
