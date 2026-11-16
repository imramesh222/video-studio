// Episode 4 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:80px;top:150px;font:700 330px Fredoka;line-height:.9;-webkit-text-stroke:26px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="color:#1e88e5">BIG</div><div style="color:#e53935;font-size:150px;-webkit-text-stroke-width:18px;margin:18px 0 0 16px">small</div></div>
      <div style="position:absolute;left:96px;top:700px;padding:14px 38px;border-radius:999px;background:#fff;font:700 62px Fredoka;color:#8e24aa;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">LEARN OPPOSITES</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:150px;text-align:center;font:700 170px Fredoka;-webkit-text-stroke:22px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))"><span style="color:#1e88e5">OPEN</span> <span style="color:#f2b705;font-size:110px">or</span> <span style="color:#e53935">CLOSED?</span></div>`,
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
      const s = T.scenes.find((x) => x.id === (kind === 'a' ? 's03' : 's20'));
      render(s.start + 0.2);
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      R.hide3.forEach((o) => { o.visible = false; }); R.hide4.forEach((o) => { o.visible = false; });
      ['wordWrap', 'numWrap', 'end', 'title', 'pairWrap'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        setBus(t, 5.5, 0, false, -3.5);
        place(R.c.kitty, -3.0, 5.6, { rotY: -0.1 }); animate(R.c.kitty, t, { tilt: 0.1 });
        place(R.c.pip, -1.5, 5.9, { rotY: -0.3 }); animate(R.c.pip, t, WAVE(0.35));
        R.p3.kittyBalloons.forEach((bl, i) => { bl.visible = true; bl.position.set(i ? -2.0 : -4.2, i ? 2.45 : 3.75, 5.5); bl.rotation.z = i ? -0.28 : 0.2; bl.scale.setScalar(i ? 0.6 : 1.8); });
        look([-5.6, 2.5, 14.2, -5.2, 2.8, 5.4]);
      } else {
        setSky('night');
        setBus(t, 0, 0, false, -4.6);
        R.p4.boxes.forEach((bx, i) => { bx.g.visible = true; bx.g.position.set(i ? 2.0 : -2.2, 0, 3.8); bx.g.scale.setScalar(1.35); bx.g.rotation.set(0, i ? -0.25 : 0.25, 0); setLid(bx, i ? 0 : 1); });
        lumiAt(0.6, -4.6, 2.5, 3.2, { glow: 0.4, light: 1.5, rotY: 0.3 });
        place(R.c.pip, 4.6, 4.2, { rotY: -0.5 }); animate(R.c.pip, t, WAVE(0.35));
        place(R.c.kitty, 0.5, 4.9, { rotY: 0 }); animate(R.c.kitty, t, { tilt: -0.1 });
        place(R.c.froggy, -6.2, 4.6, { rotY: 0.5 }); animate(R.c.froggy, t, {});
        look([0, 1.9, 13.4, 0, 2.2, 3.8]);
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
