// Episode 10 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:60px;top:140px;font:700 230px Fredoka;line-height:.92;-webkit-text-stroke:24px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">${letters('ABC')}</div>
      <div style="position:absolute;left:74px;top:390px;font:700 120px Fredoka;-webkit-text-stroke:18px #fff;paint-order:stroke fill;color:#1e88e5;
        filter:drop-shadow(0 10px 14px rgba(0,0,0,.3));transform:rotate(-4deg)">with Pip!</div>
      <div style="position:absolute;left:84px;top:640px;padding:14px 34px;border-radius:999px;background:#fff;font:700 54px Fredoka;color:#e53935;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">A is for APPLE 🍎</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:700 140px Fredoka;-webkit-text-stroke:20px #fff;paint-order:stroke fill;padding-right:300px;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))">${letters('A TO H!')}</div>`,
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
      const s = T.scenes.find((x) => x.id === (kind === 'a' ? 's03' : 's19'));
      render(s.start + 0.2);
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      [R.hide3, R.hide4, R.hide5, R.hide6, R.hide7, R.hide8, R.hide9, R.hide10].forEach((h) => h.forEach((o) => { o.visible = false; }));
      Object.values(R.brows).forEach((bs) => bs.forEach((b) => { b.visible = false; }));
      ['wordWrap', 'numWrap', 'end', 'title', 'pairWrap'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.querySelectorAll('.spark').forEach((el) => { el.style.display = 'none'; });
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        setBus(t, -9.5, 0, false, -4.5); R.birdTree.visible = true;
        place(R.c.pip, 1.6, 4.4, { rotY: -0.25 }); animate(R.c.pip, t, WAVE(0.35)); feel(R.c.pip, 'happy', t);
        place(R.c.birdie, 3.4, 4.2, { y: 1.0, rotY: -0.4 }); animate(R.c.birdie, 0.3, { flap: true });
        const ap = R.p10.apple; ap.visible = true; ap.position.set(2.9, 0.42, 4.6); ap.scale.setScalar(0.72); ap.rotation.set(0, 0.6, 0);
        const A = R.p10.big.A; A.visible = true; A.position.set(4.2, 2.4, 3.4); A.scale.set(2.2, 2.2, 1);
        look([0.4, 2.2, 11.6, 1.6, 2.0, 3.6]);
      } else {
        setSky('night');
        setBus(t, 0, 0, false, -4.6);
        crowd(t, { wave: true });
        lumiAt(0.6, 0.3, 2.5, 3.4, { glow: 0.4, light: 1.5 });
        R.p10.sky.forEach((b, i) => { b.visible = true; const x = -7 + i * 2; b.position.set(x, 5.2 - (x / 8) ** 2 * 1.2, -1); b.scale.setScalar(1.0); b.rotation.z = (i - 3.5) * 0.04; });
        look([0, 2.6, 15.5, 0, 3.4, 0]);
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
