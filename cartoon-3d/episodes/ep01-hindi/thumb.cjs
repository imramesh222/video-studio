// Episode thumbnails from the real 3D scene: two versions for YouTube's Test & compare.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname, OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const VIS = JSON.parse(fs.readFileSync(path.join(OUT, 'visemes.json'), 'utf8'));

// Big rainbow letters with a thick white outline, like the channel art.
const RAINBOW = ['#e53935', '#fb8c00', '#f2b705', '#43a047', '#1e88e5', '#8e24aa'];
const letters = (text, size) => [...text].map((ch, i) => ch === ' ' ? ' ' :
  `<span style="color:${RAINBOW[i % RAINBOW.length]}">${ch}</span>`).join('');
const OVERLAY = {
  a: `<div style="position:absolute;left:70px;top:150px;font:700 190px Fredoka;line-height:.95;-webkit-text-stroke:22px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));transform:rotate(-4deg)">
        <div style="font-family:'Baloo 2';font-weight:800;font-size:200px;line-height:1.1"><span style="color:#e53935">रंग</span> <span style="color:#43a047">सीखें!</span></div><div style="color:#1e88e5;font-size:130px">COLORS</div></div>
      <div style="position:absolute;left:84px;top:600px;padding:14px 34px;border-radius:999px;background:#fff;font:700 54px Fredoka;color:#e53935;
        box-shadow:0 10px 24px rgba(0,0,0,.25);transform:rotate(-4deg)">Red · Yellow · Green · Blue</div>`,
  b: `<div style="position:absolute;left:0;right:0;top:40px;text-align:center;font:700 150px Fredoka;-webkit-text-stroke:20px #fff;paint-order:stroke fill;
        filter:drop-shadow(0 12px 18px rgba(0,0,0,.35));font-family:'Baloo 2';font-weight:800"><span style="color:#e53935">बीप</span> <span style="color:#1e88e5">बीप!</span></div>
      <div style="position:absolute;left:0;right:0;bottom:46px;text-align:center"><span style="padding:16px 40px;border-radius:999px;background:#fff;
        font:800 64px 'Baloo 2';color:#1e88e5;box-shadow:0 10px 24px rgba(0,0,0,.25)">चलो रंग सीखें! 🌈</span></div>`,
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
  await page.evaluate(() => document.fonts.load("800 100px 'Baloo 2'", 'रंग सीखें'));
  await page.evaluate(() => document.fonts.ready);
  for (const kind of ['a', 'b']) {
    await page.evaluate(([kind, overlay, brand]) => {
      const s24 = T.scenes.find((s) => s.id === 's24');
      render(s24.start + 1.0);            // the meadow, lit as in the episode
      const t = 1.0;                       // nobody is talking: closed, smiling mouths
      Object.values(R.c).forEach((c) => { c.g.visible = false; });
      R.balloons.forEach((x) => { x.visible = false; });
      ['wordWrap', 'numWrap', 'end', 'title'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
      document.getElementById('flash').style.opacity = 0;
      R.skyRainbow.visible = true;
      if (kind === 'a') {
        R.skyRainbow.position.set(3, 1.5, -24); R.skyRainbow.scale.setScalar(1.7);
        setBus(t, 5.0, 0, false, -3.4, -1.4);   // Sunny's face toward the camera
        place(R.c.pip, 1.0, 3.4, { rotY: -0.15 }); animate(R.c.pip, t, WAVE(0.35));
        place(R.c.kitty, -0.6, 3.9, { rotY: 0.25 }); animate(R.c.kitty, t, { tilt: 0.12 });
        place(R.c.ducky, 2.1, 4.5, { rotY: -0.25 }); animate(R.c.ducky, t, { flap: true });
        place(R.c.froggy, 2.85, 5.6, { rotY: -0.3 }); animate(R.c.froggy, t, {});
        place(R.c.birdie, -1.3, 3.4, { y: 2.6, rotY: 0.4 }); animate(R.c.birdie, 0.3, { flap: true });
        ['#e53935', '#ffd43b', '#43a047', '#1e88e5'].forEach((c, i) => {
          const x = R.balloons[i]; x.visible = true;
          x.position.set(0.0 + i * 0.7, 4.2 + (i % 2) * 0.4, 2.6); x.scale.setScalar(1.1);
        });
        look([-1.0, 2.3, 11.4, -0.1, 2.0, 2.4]);
      } else {
        R.skyRainbow.position.set(-2, 3, -26); R.skyRainbow.scale.setScalar(1.6);
        setBus(t, 0, 0, false, 0, -0.5);       // face and windows both in view
        seat(R.c.pip, 0, { s: 0.92, dy: -0.2, dz: 0.45 }); animate(R.c.pip, t, WAVE(0.35));
        seat(R.c.kitty, 1, { s: 0.7, dx: -0.3, dy: 0.5, dz: 0.2 }); animate(R.c.kitty, t, {});
        seat(R.c.ducky, 1, { s: 0.7, dx: 0.32, dy: 0.5, dz: 0.2 }); animate(R.c.ducky, t, {});
        seat(R.c.froggy, 2, { s: 0.75, dx: -0.28, dy: 0.95, dz: 0.2 }); animate(R.c.froggy, t, {});
        seat(R.c.birdie, 2, { s: 0.85, dx: 0.32, dy: 0.75, dz: 0.2 }); animate(R.c.birdie, t, {});
        R.bus.mouth.material.map = R.mouths.bus.D; R.bus.mouth.material.needsUpdate = true;
        look([7.4, 2.7, 9.8, 1.0, 2.35, 0.2]);
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
