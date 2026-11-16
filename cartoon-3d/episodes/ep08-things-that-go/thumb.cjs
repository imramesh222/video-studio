// Episode 8 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:60px;top:110px;font:700 190px Fredoka;line-height:.95;-webkit-text-stroke:24px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="color:#43a047">THINGS</div><div style="color:#e53935">THAT GO!</div></div>
      <div style="position:absolute;left:1180px;top:880px;padding:14px 34px;border-radius:999px;background:#fff;font:700 54px Fredoka;color:#8e24aa;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-3deg)">🚌 🚗 🚂 ⛵ ✈️</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:700 140px Fredoka;-webkit-text-stroke:20px #fff;paint-order:stroke fill;padding-right:300px;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))">${letters('CHOO CHOO!')}</div>`,
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
      const s = T.scenes.find((x) => x.id === (kind === 'a' ? 's17' : 's09'));
      render(s.start + 0.2);
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      [R.hide3, R.hide4, R.hide5, R.hide6, R.hide7, R.hide8].forEach((h) => h.forEach((o) => { o.visible = false; }));
      ['wordWrap', 'numWrap', 'end', 'title', 'pairWrap'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.querySelectorAll('.spark').forEach((el) => { el.style.display = 'none'; });
      R.tags.forEach((el) => { el.style.display = 'none'; }); R.tagN = 0;
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        R.W.valley.visible = true;
        setBus(t, 4.4, 0, false, 0);
        seat(R.c.pip, 0, { s: 0.85, dy: -0.1, dz: 0.3 }); animate(R.c.pip, t, WAVE(0.35));
        const car = R.p8.car; car.visible = true; car.scale.setScalar(1.7); car.rotation.set(0, 0, 0); car.position.set(-1.5, 0.03, 1.4);
        place(R.c.kitty, -1.5, 1.4, { y: 1.05, s: 0.55 }); animate(R.c.kitty, t, {});
        const tr = R.p8.train; tr.g.visible = true; tr.g.scale.setScalar(0.85); tr.g.position.set(0, 0, 0.4); setTrain(tr, -5.6, 0, 1.0, 0.8);
        place(R.c.froggy, -6.07, 0.4, { y: 1.33, s: 0.6 }); animate(R.c.froggy, t, {});
        const P = R.p8.plane; P.g.visible = true; P.g.scale.setScalar(1.1); P.g.position.set(3.2, 6.6, -1); P.g.rotation.set(0, 0, 0.08);
        const B = R.p8.boat; B.visible = true; B.scale.setScalar(1.0); B.position.set(8.2, 0, 3.4); B.rotation.set(0, -0.3, 0);
        look([1.6, 3.6, 17, 1.6, 3.0, 0]);
      } else {
        setSky('day');
        R.W.forest.visible = true; R.p8.track.visible = true;
        const tr = R.p8.train; tr.g.visible = true; tr.g.scale.setScalar(1.25); tr.g.position.set(0, 0, 0.6); setTrain(tr, 2.6, 0, 1.5, 1);
        place(R.c.froggy, 4.6, 3.6, { rotY: -0.4 }); animate(R.c.froggy, t, {});
        place(R.c.pip, -4.0, 3.8, { rotY: 0.45 }); animate(R.c.pip, t, WAVE(0.35));
        look([0, 2.2, 12.5, 0, 1.6, 1.6]);
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
