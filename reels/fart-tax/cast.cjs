// Saves the character sheets (cast.html) as pictures: `node cast.cjs` → out/cast/*.png, or `node cast.cjs toby mayor` for some.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname;
const OUT = path.join(HERE, 'out', 'cast');
fs.mkdirSync(OUT, { recursive: true });
const ALL = ['toby', 'mayor', 'puff', 'rich', 'town', 'machines', 'bignose'];
const want = process.argv.slice(2).length ? process.argv.slice(2) : ALL;

(async () => {
  const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', (e) => { console.error('page error:', e.message); process.exit(1); });
  page.on('console', (m) => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.goto('file://' + path.join(HERE, 'cast.html'));
  // Signs are drawn with Montserrat, so it must load before init.
  await page.evaluate(() => Promise.all([document.fonts.load('900 100px Montserrat'), document.fonts.load('700 40px Montserrat')]));
  await page.evaluate(() => init());
  await page.waitForTimeout(300);
  for (const id of want) {
    await page.evaluate((x) => show(x), id);
    await page.screenshot({ path: path.join(OUT, `${String(ALL.indexOf(id) + 1)}-${id}.png`) });
  }
  console.log('sheets', want.join(' '));
  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
