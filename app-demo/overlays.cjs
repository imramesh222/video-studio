// Renders the still layers of the video (backgrounds, masks, captions, cards) to PNG.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

// LANG=ne: Nepali captions and cards, into layers-ne/.
const LANG = process.env.LANG_CODE || 'en';
const NE = LANG === 'ne';
const OUT = path.join(__dirname, NE ? 'layers-ne' : 'layers');
fs.mkdirSync(OUT, { recursive: true });
const ICON = 'data:image/png;base64,' +
  fs.readFileSync('/Users/rameshrawat/gymbahi/frontend/public/icon-512.png').toString('base64');

// Layout (1920x1080). Shared with compose.sh.
const L = require('./layout.json');

const FONT = `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&display=swap" rel="stylesheet">`;
const BASE = `*{margin:0;padding:0;box-sizing:border-box}html,body{width:1920px;height:1080px;font-family:Inter,'Noto Sans Devanagari',-apple-system,sans-serif;-webkit-font-smoothing:antialiased}`;
const BG = `background:radial-gradient(1200px 700px at 75% 15%, #1d3d8f 0%, rgba(29,61,143,0) 60%),radial-gradient(900px 600px at 10% 100%, #12306e 0%, rgba(18,48,110,0) 60%),#070d22;`;

const rect = (r, extra = '') =>
  `position:absolute;left:${r.x}px;top:${r.y}px;width:${r.w}px;height:${r.h}px;${extra}`;

const pages = {
  // Background behind a full-width desk shot, with the screen's shadow.
  'bg-web': `<body style="${BG}"><div style="${rect(L.web, `border-radius:${L.web.r}px;box-shadow:0 30px 80px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08);background:#0b1430`)}"></div></body>`,
  // Background for the phone + desk split, with the phone's body.
  'bg-split': `<body style="${BG}">
    <div style="${rect({ x: L.phone.x - 14, y: L.phone.y - 14, w: L.phone.w + 28, h: L.phone.h + 28 }, `border-radius:${L.phone.r + 14}px;background:#0a0a0c;box-shadow:0 30px 80px rgba(0,0,0,.6),0 0 0 2px #2b2f3a,inset 0 0 0 1px #3a3f4c`)}"></div>
    <div style="${rect(L.desk, `border-radius:${L.desk.r}px;box-shadow:0 30px 80px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.08);background:#0b1430`)}"></div>
    <div style="position:absolute;left:${L.phone.x}px;width:${L.phone.w}px;top:${L.phone.y - 52}px;text-align:center;color:#93a7d6;font:600 22px Inter,'Noto Sans Devanagari';letter-spacing:.08em;text-transform:uppercase">${NE ? 'सदस्यको फोन' : "Member's phone"}</div>
    <div style="position:absolute;left:${L.desk.x}px;width:${L.desk.w}px;top:${L.desk.y - 52}px;text-align:center;color:#93a7d6;font:600 22px Inter,'Noto Sans Devanagari';letter-spacing:.08em;text-transform:uppercase">${NE ? 'तपाईंको काउन्टर' : 'Your desk'}</div>
  </body>`,
  // Masks: white where the video shows, with rounded corners.
  'mask-web': `<body style="background:#000"><div style="${rect({ x: 0, y: 0, w: L.web.w, h: L.web.h }, `border-radius:${L.web.r}px;background:#fff`)}"></div></body>`,
  'mask-phone': `<body style="background:#000"><div style="${rect({ x: 0, y: 0, w: L.phone.w, h: L.phone.h }, `border-radius:${L.phone.r}px;background:#fff`)}"></div></body>`,
  'mask-desk': `<body style="background:#000"><div style="${rect({ x: 0, y: 0, w: L.desk.w, h: L.desk.h }, `border-radius:${L.desk.r}px;background:#fff`)}"></div></body>`,
  title: `<body style="${BG};display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff">
    <img src="${ICON}" style="width:150px;height:150px;border-radius:34px;box-shadow:0 20px 60px rgba(37,99,235,.45)">
    <div style="font:800 110px Inter;letter-spacing:-.03em;margin-top:40px">GymBhai</div>
    <div style="font:500 42px Inter,'Noto Sans Devanagari';color:#b8c6ea;margin-top:14px">${NE ? 'नेपालका जिमका लागि बनाइएको सफ्टवेयर' : 'Gym software made for Nepal'}</div>
  </body>`,
  end: `<body style="${BG};display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;text-align:center">
    <img src="${ICON}" style="width:120px;height:120px;border-radius:28px;box-shadow:0 20px 60px rgba(37,99,235,.45)">
    <div style="font:800 84px Inter,'Noto Sans Devanagari';letter-spacing:-.03em;margin-top:40px;line-height:1.1">${NE ? 'रजिस्टर होइन,<br>आफ्नो जिम चलाउनुहोस्।' : 'Run your gym,<br>not a register.'}</div>
    <div style="font:500 38px Inter,'Noto Sans Devanagari';color:#b8c6ea;margin-top:34px">${NE ? '१४ दिन निःशुल्क &nbsp;·&nbsp; नेपाली र English' : 'Free for 14 days &nbsp;·&nbsp; English and नेपाली'}</div>
    <div style="font:700 44px Inter;color:#fff;margin-top:26px;padding:16px 36px;border-radius:999px;background:#2563eb">${L.address}</div>
  </body>`,
};

// One caption per file, centred in the band under the screen.
const captions = require(NE ? './captions.ne.json' : './captions.json');
for (const [id, text] of Object.entries(captions)) {
  pages[`cap-${id}`] = `<body style="background:transparent">
    <div style="position:absolute;left:0;right:0;top:${L.captionY}px;height:${1080 - L.captionY}px;display:flex;align-items:center;justify-content:center">
      <div style="font:600 40px Inter,'Noto Sans Devanagari';color:#fff;letter-spacing:-.01em;text-align:center;max-width:1700px;text-shadow:0 2px 12px rgba(0,0,0,.5)">${text}</div>
    </div></body>`;
}

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const [name, body] of Object.entries(pages)) {
    await page.setContent(`<!doctype html><html><head><meta charset="utf-8">${FONT}<style>${BASE}</style></head>${body}</html>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(150);
    const transparent = name.startsWith('cap-');
    const clip = name === 'mask-web' ? { x: 0, y: 0, width: L.web.w, height: L.web.h }
      : name === 'mask-phone' ? { x: 0, y: 0, width: L.phone.w, height: L.phone.h }
      : name === 'mask-desk' ? { x: 0, y: 0, width: L.desk.w, height: L.desk.h } : undefined;
    await page.screenshot({ path: path.join(OUT, `${name}.png`), omitBackground: transparent, clip });
  }
  await browser.close();
  console.log('layers:', Object.keys(pages).length);
})().catch((e) => { console.error(e); process.exit(1); });
