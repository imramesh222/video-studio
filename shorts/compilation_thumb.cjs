// Compilation thumbnail: four episode scenes in a grid, "40 MINUTES" across the middle. `node shorts/compilation_thumb.cjs`
const path = require('path'), os = require('os');
const { chromium } = require('playwright');
const LL = path.join(os.homedir(), 'Downloads', 'Lumi Land');
const pics = ['Episode 01 - Learn Colors/lumi-land-ep1-thumbnail-a.jpg', 'Episode 08 - Things That Go/lumi-land-ep8-thumbnail-b.jpg',
  'Episode 05 - The Fruit Picnic/lumi-land-ep5-thumbnail-a.jpg', 'Episode 06 - The Weather Day/lumi-land-ep6-thumbnail-b.jpg'].map((p) => 'file://' + path.join(LL, p));
const html = `<html><head><link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@700&display=swap" rel="stylesheet"><style>
html,body{margin:0;width:1280px;height:720px;font-family:Fredoka;overflow:hidden}
.g{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:8px;background:#fff;width:1280px;height:720px}
.g div{background-size:cover;background-position:60% 50%}
.m{position:absolute;left:0;right:0;top:250px;text-align:center}
.m span{display:inline-block;padding:10px 46px 16px;border-radius:40px;background:#ffd43b;border:10px solid #fff;font-size:150px;line-height:1;color:#e53935;
 box-shadow:0 14px 30px rgba(0,0,0,.35);transform:rotate(-3deg)}
.s{position:absolute;left:0;right:0;top:470px;text-align:center;font-size:64px;color:#fff;-webkit-text-stroke:14px #1e88e5;paint-order:stroke fill}
</style></head><body><div class="g">${pics.map((p) => `<div style="background-image:url('${p}')"></div>`).join('')}</div>
<div class="m"><span>40 MINUTES</span></div><div class="s">10 learning adventures!</div></body></html>`;
(async () => {
  const b = await chromium.launch({ args: ['--allow-file-access-from-files'] });
  const page = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const file = path.join(__dirname, 'out', 'compilation-thumb.html');   // a file page, so it can show the file thumbnails
  require('fs').writeFileSync(file, html);
  await page.goto('file://' + file, { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(400);
  await page.screenshot({ path: path.join(LL, 'Compilation - Episodes 1 to 10', 'lumi-land-compilation-thumbnail.jpg'), type: 'jpeg', quality: 92 });
  await b.close();
})().catch((e) => { console.error(e); process.exit(1); });
