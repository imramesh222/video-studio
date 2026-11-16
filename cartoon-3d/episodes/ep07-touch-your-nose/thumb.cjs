// Episode 7 thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

const COLS = ['#e53935', '#1e88e5', '#43a047', '#f2b705', '#8e24aa', '#fb8c00'];
const letters = (text) => [...text].map((ch, i) => ch === ' ' ? ' ' : `<span style="color:${COLS[i % COLS.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:60px;top:130px;font:700 190px Fredoka;line-height:.95;-webkit-text-stroke:24px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="color:#ec407a">TOUCH</div><div style="color:#1e88e5">YOUR NOSE!</div></div>
      <div style="position:absolute;left:74px;top:640px;padding:14px 34px;border-radius:999px;background:#fff;font:700 54px Fredoka;color:#fb8c00;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">BODY PARTS FOR KIDS</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:700 140px Fredoka;-webkit-text-stroke:20px #fff;paint-order:stroke fill;padding-right:300px;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35))">${letters('COPY ME!')}</div>`,
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
      const s = T.scenes.find((x) => x.id === (kind === 'a' ? 's07' : 's16'));
      render(s.start + 0.2);
      const t = 1.0; // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      R.hide3.forEach((o) => { o.visible = false; }); R.hide4.forEach((o) => { o.visible = false; }); R.hide5.forEach((o) => { o.visible = false; }); R.hide6.forEach((o) => { o.visible = false; }); R.hide7.forEach((o) => { o.visible = false; });
      ['wordWrap', 'numWrap', 'end', 'title', 'pairWrap'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.querySelectorAll('.spark').forEach((el) => { el.style.display = 'none'; });
      R.rings.forEach((el) => { el.style.display = 'none'; }); R.ringI = 0; R.mw = false;
      document.getElementById('flash').style.opacity = 0;
      if (kind === 'a') {
        setSky('day');
        R.W.garden.visible = true;
        setBus(t, 5, 0, false, -3.5);
        place(R.c.pip, -1.4, 5.8, { rotY: -0.1 }); animate(R.c.pip, t, TOUCH.nose());
        place(R.c.kitty, 0.6, 5.6, { rotY: -0.3 }); animate(R.c.kitty, t, { tilt: 0.12 });
        look([-3.6, 2.2, 11.4, -2.2, 1.9, 5.6]);
        ring('pip', 'nose', 0, 1); ring('kitty', 'nose', 0, 1);
      } else {
        setSky('day');
        setBus(t, 0, 0, false, -3.6);
        const poses = { pip: TOUCH.ears(), kitty: {}, ducky: { flap: true }, froggy: {}, birdie: { flap: true } };
        ROW.forEach(([who, x, z]) => { place(R.c[who], x, z, { rotY: -x * 0.06, y: who === 'birdie' ? 0.75 : 0 }); animate(R.c[who], t, poses[who]); });
        look([0, 1.8, 10.4, 0, 1.6, 3.4]);
        ring('pip', 'ears', 0, 1);
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
