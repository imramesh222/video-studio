// Episode 6 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:60px;top:130px;font:700 210px Fredoka;line-height:.92;-webkit-text-stroke:24px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="color:#1e88e5">RAINY</div><div style="color:#f2b705">DAY!</div></div>
      <div style="position:absolute;left:74px;top:640px;padding:14px 34px;border-radius:999px;background:#fff;font:700 54px Fredoka;color:#00897b;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">LEARN THE WEATHER</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:700 140px Fredoka;-webkit-text-stroke:20px #fff;paint-order:stroke fill;padding-right:300px;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))">${letters('SUN OR RAIN?')}</div>`,
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
      render(s.start + (kind === 'a' ? 3.5 : 0.2));
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      R.hide3.forEach((o) => { o.visible = false; }); R.hide4.forEach((o) => { o.visible = false; }); R.hide5.forEach((o) => { o.visible = false; }); R.hide6.forEach((o) => { o.visible = false; });
      ['wordWrap', 'numWrap', 'end', 'title', 'pairWrap'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.querySelectorAll('.spark').forEach((el) => { el.style.display = 'none'; });
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        weather(3.5, 4.2, { grey: 1, cover: 1, rain: 0.7, puddles: true, cx: 2 });
        place(R.c.pip, 1.6, 4.9, { rotY: -0.1 }); animate(R.c.pip, t, { armR: 2.4 });
        place(R.c.froggy, 3.6, 4.9, { rotY: -0.3 }); animate(R.c.froggy, t, {});
        holdUmbrella(2.45, 1.35, 4.8, 1, 0.15);
        look([0.6, 2.1, 11.2, 1.6, 1.8, 4.6]);
      } else {
        setSky('day');
        const R7 = R.p3.rainbow; R7.g.visible = true; R7.g.scale.setScalar(1); R7.g.position.set(1.5, 0, -9);
        R7.bands.forEach((b) => { b.material.emissiveIntensity = 0.35; b.position.z = 0; });
        place(R.c.pip, 0.4, 3.6, { rotY: 0 }); animate(R.c.pip, t, ARMS_UP(0.3));
        place(R.c.kitty, -1.6, 3.4, { rotY: 0.2 }); R.p6.hat.visible = true; animate(R.c.kitty, t, {});
        place(R.c.ducky, 2.4, 3.4, { rotY: -0.2 }); animate(R.c.ducky, t, { flap: true });
        const U = R.p6.umb; U.g.visible = true; U.g.position.set(-3.4, 0, 3.6); U.g.rotation.set(0, 0, 0.25); setUmbrella(U, 1);
        look([0.6, 1.9, 13.5, 0.8, 3.2, 0]);
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
