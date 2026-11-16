// Episode 3 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:70px;top:130px;font:700 200px Fredoka;line-height:.95;-webkit-text-stroke:22px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="color:#1e88e5">COUNT</div><div>${letters('TO 10!')}</div></div>
      <div style="position:absolute;left:84px;top:610px;padding:14px 34px;border-radius:999px;background:#fff;font:700 58px Fredoka;color:#e53935;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">1 · 2 · 3 · 4 · 5 · 6 · 7 · 8 · 9 · 10</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:34px;text-align:center;font:700 150px Fredoka;-webkit-text-stroke:20px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))">${letters('COUNT THE STARS!')}</div>`,
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
      const s = T.scenes.find((x) => x.id === (kind === 'a' ? 's11' : 's16'));
      render(s.start + 0.2);
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      R.hide3.forEach((o) => { o.visible = false; });
      R.tags.forEach((el) => { el.style.display = 'none'; }); R.tagN = 0; R.mw = false;
      ['wordWrap', 'numWrap', 'end', 'title'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        setBus(t, -9.5, 0, false, -4.5);
        place(R.c.pip, 1.0, 3.4, { rotY: -0.15 }); animate(R.c.pip, t, WAVE(0.35));
        place(R.c.kitty, -0.6, 3.9, { rotY: 0.25 }); animate(R.c.kitty, t, { tilt: 0.12 });
        place(R.c.ducky, 2.1, 4.5, { rotY: -0.25 }); animate(R.c.ducky, t, { flap: true });
        place(R.c.froggy, 2.85, 5.6, { rotY: -0.3 }); animate(R.c.froggy, t, {});
        place(R.c.birdie, -1.3, 3.4, { y: 2.6, rotY: 0.4 }); animate(R.c.birdie, 0.3, { flap: true });
        R.p3.party.forEach((x, i) => {
          x.visible = true;
          const row = i < 5 ? 0 : 1, k = i % 5;
          x.position.set(-0.6 + k * 1.0 + row * 0.5, 4.6 - row * 0.95 + (k % 2) * 0.15, 1.2 + row * 0.3);
          x.scale.setScalar(0.5); x.rotation.z = (k - 2) * 0.05;
        });
        look([-1.0, 2.3, 11.4, -0.1, 2.0, 2.4]);
      } else {
        setSky('night');
        setBus(t, 0, 0, false, -4.6);
        place(R.c.pip, -1.9, 3.9, { rotY: 0.45 }); animate(R.c.pip, t, WAVE(0.35));
        place(R.c.kitty, -3.5, 3.4, { rotY: 0.4 }); animate(R.c.kitty, t, { lookUp: -0.3 });
        place(R.c.ducky, 1.8, 3.9, { rotY: -0.3 }); animate(R.c.ducky, t, { lookUp: -0.3 });
        place(R.c.birdie, 3.5, 3.4, { y: 1.0, rotY: -0.45 }); animate(R.c.birdie, 0.3, { flap: true });
        look([0, 2.6, 15, 0, 3.0, 0]);
        stars9(5, 1.0);
        const p = SLOT(9);
        lumiAt(0.6, p.x, p.y, p.z, { s: 1.35, glow: 0.4, light: 1.4 });
        R.p3.stars.forEach((st, i) => tag(i + 1, st, -1, 1, { dy: 0.95 }));
        tag(10, R.c.lumi.g, -1, 1, { dy: 1.4 });
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
