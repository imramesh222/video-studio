// Episode 5 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:70px;top:120px;font:700 230px Fredoka;line-height:.92;-webkit-text-stroke:24px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="color:#e53935">FRUIT</div><div style="color:#43a047">PICNIC!</div></div>
      <div style="position:absolute;left:84px;top:650px;padding:14px 34px;border-radius:999px;background:#fff;font:700 54px Fredoka;color:#fb8c00;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">LEARN FRUITS 🍎🍌🍉</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:700 128px Fredoka;-webkit-text-stroke:18px #fff;paint-order:stroke fill;padding-right:300px;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))">${letters('WHAT FRUIT IS IT?')}</div>`,
};
const BRAND = `<div style="position:absolute;right:40px;top:34px;display:flex;align-items:center;gap:12px;padding:10px 24px 10px 12px;border-radius:999px;
  background:rgba(255,255,255,.92);font:700 44px Fredoka;color:#1f4f8a;box-shadow:0 8px 20px rgba(0,0,0,.2)">
  <img src="../../lib/lumi-star.png" width="64" height="64">Lumi Land</div>`;

(async () => {
  const b = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
  const page = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', (e) => { console.error('page error:', e.message); process.exit(1); });
  await page.goto('file://' + path.join(HERE, 'episode.html'));
  await page.evaluate(() => document.fonts.load('700 100px Fredoka'));
  await page.evaluate(([t, v]) => init(t, v), [T, VIS]);
  await page.evaluate(() => document.fonts.ready);
  for (const kind of ['a', 'b']) {
    await page.evaluate(([kind, overlay, brand]) => {
      const s = T.scenes.find((x) => x.id === (kind === 'a' ? 's15' : 's22'));
      render(s.start + 0.2);
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      R.hide3.forEach((o) => { o.visible = false; }); R.hide4.forEach((o) => { o.visible = false; }); R.hide5.forEach((o) => { o.visible = false; });
      ['wordWrap', 'numWrap', 'end', 'title', 'pairWrap'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.querySelectorAll('.spark').forEach((el) => { el.style.display = 'none'; });
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        setBus(t, -9.5, 0, false, -4.5);
        picnic(t, { spots: [['pip', -0.2, 5.0], ['kitty', 3.6, 4.0], ['ducky', -0.4, 2.0], ['froggy', 4.6, 2.6], ['birdie', 2.4, 2.4]], pose: (who) => (who === 'pip' ? WAVE(0.35) : {}) });
        R.p5.blanket.position.set(2.0, 0.03, 3.4);
        R.p5.basket.g.position.set(2.0, 0, 3.4); R.p5.basket.g.scale.setScalar(1.7);
        R.p5.melon.g.position.set(4.0, 0, 3.6); R.p5.melon.g.scale.setScalar(0.75); setMelon(R.p5.melon, 1);
        look([-1.2, 2.6, 11.0, 0.4, 1.7, 3.4]);
      } else {
        R.W.recap.visible = true;
        R.backdrop.material.color.set('#fff3c4');
        const row = R.p5.recap;
        [[0, -4.6, 1.0], [1, -1.6, 2.6], [2, 1.4, 1.0], [4, 4.2, 2.0], [5, 0, -0.6], [3, -4.0, -1.2]].forEach(([k, x, y]) => {
          const o = row[k]; o.visible = true; o.position.set(x, y, 0); o.rotation.set(0, 0.2, 0); o.scale.setScalar(k === 5 ? 0.9 : k === 4 ? 0.65 : 0.75);
        });
        look([0, 0.9, 13, 0, 0.9, 0]);
      }
      renderer.render(scene, cam);
      let o = document.getElementById('thumb');
      if (!o) { o = document.createElement('div'); o.id = 'thumb'; o.className = 'ov'; document.body.appendChild(o); }
      o.innerHTML = overlay + brand;
    }, [kind, OVERLAY[kind], BRAND]);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(OUT, `thumb-${kind}.png`) });
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
