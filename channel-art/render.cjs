// Renders the Lumi Land channel art to PNG.
const path = require('path');
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [kind, w, h, transparent] of [['profile', 800, 800], ['banner', 2560, 1440], ['watermark', 150, 150, true]]) {
    const p = await b.newPage({ viewport: { width: w, height: h } });
    await p.goto('file://' + path.join(__dirname, 'brand.html'));
    await p.evaluate(() => document.fonts.ready);
    await p.evaluate((k) => draw(k), kind);
    await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(400);
    await p.screenshot({ path: path.join(__dirname, `lumi-land-${kind}.png`), omitBackground: !!transparent });
    await p.close();
  }
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
