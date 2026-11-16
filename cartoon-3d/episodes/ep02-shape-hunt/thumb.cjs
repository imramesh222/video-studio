// Episode 2 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:70px;top:140px;font:700 190px Fredoka;line-height:.95;-webkit-text-stroke:22px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="color:#1e88e5">LEARN</div><div>${letters('SHAPES!')}</div></div>
      <div style="position:absolute;left:84px;top:600px;padding:14px 34px;border-radius:999px;background:#fff;font:700 54px Fredoka;color:#e53935;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">circle · square · triangle · star</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:700 160px Fredoka;-webkit-text-stroke:20px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))">${letters('MEET LUMI!')}</div>
      <div style="position:absolute;left:0;right:0;bottom:46px;text-align:center"><span style="padding:16px 40px;border-radius:999px;background:#fff;
        font:700 64px Fredoka;color:#1e88e5;box-shadow:0 10px 24px rgba(0,0,0,.25)">Let's learn shapes! ⭐</span></div>`,
};
const BRAND = `<div style="position:absolute;right:40px;top:34px;display:flex;align-items:center;gap:12px;padding:10px 24px 10px 12px;border-radius:999px;
  background:rgba(255,255,255,.92);font:700 44px Fredoka;color:#1f4f8a;box-shadow:0 8px 20px rgba(0,0,0,.2)">
  <img src="../../lib/lumi-star.png" width="64" height="64">Lumi Land</div>`;

(async () => {
  const b = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
  const page = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  page.on('pageerror', (e) => { console.error('page error:', e.message); process.exit(1); });
  await page.goto('file://' + path.join(HERE, 'episode.html'));
  await page.evaluate(([t, v]) => init(t, v), [T, VIS]);
  await page.evaluate(() => document.fonts.ready);
  for (const kind of ['a', 'b']) {
    await page.evaluate(([kind, overlay, brand]) => {
      const s = T.scenes.find((x) => x.id === (kind === 'a' ? 's20' : 's17'));
      render(s.start + 0.2);
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      R.p.big.forEach((x) => { x.visible = false; });
      ['wordWrap', 'numWrap', 'end', 'title'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        setBus(t, 5.0, 0, false, -3.4, -1.4);
        place(R.c.pip, 1.0, 3.4, { rotY: -0.15 }); animate(R.c.pip, t, WAVE(0.35));
        place(R.c.kitty, -0.6, 3.9, { rotY: 0.25 }); animate(R.c.kitty, t, { tilt: 0.12 });
        place(R.c.ducky, 2.1, 4.5, { rotY: -0.25 }); animate(R.c.ducky, t, { flap: true });
        place(R.c.froggy, 2.85, 5.6, { rotY: -0.3 }); animate(R.c.froggy, t, {});
        place(R.c.birdie, -1.3, 3.4, { y: 2.6, rotY: 0.4 }); animate(R.c.birdie, 0.3, { flap: true });
        lumiAt(1.0, -0.2, 3.25, 3.2, { s: 0.6, light: 0.6 });
        KINDS.forEach((k, i) => {
          const x = R.p.big[i]; x.visible = true;
          x.position.set(0.3 + i * 1.15, 4.05 + (i % 2) * 0.3, 1.4); x.scale.setScalar(0.62); x.rotation.y = 0.15;
        });
        look([-1.0, 2.3, 11.4, -0.1, 2.0, 2.4]);
      } else {
        setSky('dusk');
        lumiAt(0.6, 0.6, 2.3, 3.6, { s: 1.15, glow: 0.3, light: 1.2 });
        place(R.c.pip, -1.9, 3.9, { rotY: 0.45 }); animate(R.c.pip, t, WAVE(0.35));
        place(R.c.birdie, 2.7, 3.9, { y: 1.3, rotY: -0.45 }); animate(R.c.birdie, 0.3, { flap: true });
        look([0.4, 2.0, 9.6, 0.4, 2.3, 3.6]);
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
