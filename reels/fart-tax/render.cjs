// Draws every frame of reel.html (GPU): `node render.cjs` (all), `--from A --to B` (frames), or `--still 5,12.3` (PNGs to check).
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname;
const OUT = path.join(HERE, 'out');
const T = JSON.parse(fs.readFileSync(path.join(OUT, 'timeline.json'), 'utf8'));
const still = process.argv.includes('--still') ? process.argv[process.argv.indexOf('--still') + 1].split(',').map(Number) : null;

(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', (e) => { console.error('page error:', e.message); process.exit(1); });
  await page.goto('file://' + path.join(HERE, 'reel.html'));
  // Signs are drawn with Montserrat, so it must load before init.
  await page.evaluate(() => Promise.all([document.fonts.load('900 100px Montserrat'), document.fonts.load('700 40px Montserrat')]));
  await page.evaluate((t) => init(t), T);
  await page.waitForTimeout(300);
  if (still) {
    for (const t of still) {
      await page.evaluate((x) => render(x), t);
      await page.screenshot({ path: path.join(OUT, `still-${t}.png`) });
    }
    console.log('stills', still.join(' '));
  } else {
    const dir = path.join(OUT, 'frames');
    fs.mkdirSync(dir, { recursive: true });
    const n = Math.ceil(T.total * T.fps);
    const arg = (k, d) => (process.argv.includes(k) ? Number(process.argv[process.argv.indexOf(k) + 1]) : d);
    for (let i = arg('--from', 0); i < Math.min(n, arg('--to', n)); i++) {
      await page.evaluate((x) => render(x), i / T.fps);
      await page.screenshot({ path: path.join(dir, `${String(i).padStart(5, '0')}.jpg`), type: 'jpeg', quality: 93 });
      if (i % 300 === 0) console.log(`frame ${i}/${n}`);
    }
    console.log('frames', n);
  }
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
