// Draws the text overlays for the Shorts (transparent 1080×1920 PNGs): `node overlays.cjs list.json out/`
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const [list, outDir] = process.argv.slice(2);
const items = JSON.parse(fs.readFileSync(list, 'utf8'));
const html = (title, color) => `<html><head><link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@600;700&display=swap" rel="stylesheet">
<style>html,body{margin:0;width:1080px;height:1920px;background:transparent;font-family:Fredoka}
.t{position:absolute;left:40px;right:40px;top:250px;text-align:center;font-weight:700;font-size:118px;line-height:1.02;color:${color};
 -webkit-text-stroke:20px #fff;paint-order:stroke fill;filter:drop-shadow(0 10px 16px rgba(0,0,0,.35))}
.b{position:absolute;left:0;right:0;top:1390px;text-align:center}
.b span{display:inline-block;padding:18px 40px;border-radius:999px;background:#fff;color:#1f4f8a;font-weight:700;font-size:52px;box-shadow:0 10px 24px rgba(0,0,0,.3)}
</style></head><body><div class="t">${title}</div><div class="b"><span>⭐ Full episode on Lumi Land</span></div></body></html>`;
(async () => {
  const b = await chromium.launch();
  const page = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  for (const it of items) {
    await page.setContent(html(it.title, it.color));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(outDir, it.id + '.png'), omitBackground: true });
  }
  await b.close();
  console.log('overlays', items.length);
})().catch((e) => { console.error(e); process.exit(1); });
