// Drives the real web app like a person would, and records it frame by frame.
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BASE = 'http://localhost:3000';
const VIEW = { width: 1440, height: 810 };
const SCALE = 1920 / 1440; // frames come out at 1920x1080
const CLIPS = path.join(__dirname, 'clips');

// A visible pointer and click ripple; Playwright's mouse is otherwise invisible.
// The dev-only Next.js badge is hidden.
const CURSOR = () => {
  const install = () => {
    if (document.getElementById('__cur')) return;
    const style = document.createElement('style');
    style.textContent = `nextjs-portal{display:none!important}
      #__cur{position:fixed;left:0;top:0;width:26px;height:26px;z-index:2147483647;pointer-events:none;transform:translate(-3px,-2px);filter:drop-shadow(0 2px 3px rgba(0,0,0,.35))}
      .__rip{position:fixed;width:44px;height:44px;margin:-22px 0 0 -22px;border-radius:50%;background:rgba(37,99,235,.35);border:2px solid rgba(37,99,235,.8);z-index:2147483646;pointer-events:none;animation:__rip .5s ease-out forwards}
      @keyframes __rip{from{transform:scale(.3);opacity:1}to{transform:scale(1.4);opacity:0}}`;
    document.head.appendChild(style);
    const cur = document.createElement('div');
    cur.id = '__cur';
    cur.innerHTML = `<svg viewBox="0 0 24 24" width="26" height="26"><path d="M4 2l15 11.5-6.6.9 3.9 7.4-2.9 1.5-3.9-7.5L4 20.3z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
    const saved = JSON.parse(sessionStorage.getItem('__cur') || '[720,420]');
    cur.style.left = saved[0] + 'px';
    cur.style.top = saved[1] + 'px';
    document.body.appendChild(cur);
    if (window.__curListening) return;
    window.__curListening = true;
    addEventListener('mousemove', (e) => {
      const cur = document.getElementById('__cur');
      if (!cur) return;
      cur.style.left = e.clientX + 'px';
      cur.style.top = e.clientY + 'px';
      sessionStorage.setItem('__cur', JSON.stringify([e.clientX, e.clientY]));
    }, true);
    addEventListener('mousedown', (e) => {
      const r = document.createElement('div');
      r.className = '__rip';
      r.style.left = e.clientX + 'px';
      r.style.top = e.clientY + 'px';
      document.body.appendChild(r);
      setTimeout(() => r.remove(), 600);
    }, true);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
  // React can replace body children on navigation; put the pointer back.
  setInterval(install, 300);
};

async function launch() {
  const browser = await chromium.launch();
  const context = async (opts = {}) => {
    const ctx = await browser.newContext({ viewport: VIEW, deviceScaleFactor: SCALE, ...opts });
    await ctx.addInitScript(CURSOR);
    return ctx;
  };
  return { browser, context };
}

async function signIn(page, phone = '9800000200') {
  await page.goto(BASE + '/staff/login');
  await page.getByLabel('Email or mobile number').fill(phone);
  await page.getByLabel('Password', { exact: true }).fill('demo-password-123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.waitForURL('**/staff', { timeout: 60000 });
}

/** Record `page` into clips/<name>/: JPEG frames plus their wall-clock times. */
async function record(page, name) {
  const dir = path.join(CLIPS, name);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
  const frames = [];
  const marks = {};
  const t0 = Date.now();
  let n = 0;
  await page.screencast.start({
    size: { width: 1920, height: 1080 },
    quality: 92,
    onFrame: ({ data }) => {
      const file = `${String(++n).padStart(6, '0')}.jpg`;
      fs.writeFileSync(path.join(dir, file), data);
      frames.push([file, Date.now()]);
    },
  });
  // Keep frames coming while nothing moves, so the start is never missing.
  const nudge = setInterval(() => page.evaluate(() => {
    const c = document.getElementById('__cur');
    if (c) c.style.opacity = c.style.opacity === '0.999' ? '1' : '0.999';
  }).catch(() => {}), 250);
  return {
    mark: (label) => { marks[label] = (Date.now() - t0) / 1000; },
    async stop() {
      const tEnd = Date.now();
      clearInterval(nudge);
      await page.screencast.stop();
      fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify({ t0, tEnd, frames, marks }));
      console.log(`${name}: ${frames.length} frames, ${((tEnd - t0) / 1000).toFixed(1)}s`, marks);
    },
  };
}

const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
const pos = new WeakMap();

/** Glide the pointer to a point, as a hand would. */
async function glide(page, x, y, ms = 700) {
  const [x0, y0] = pos.get(page) ?? [720, 420];
  const steps = Math.max(8, Math.round(ms / 16));
  for (let i = 1; i <= steps; i++) {
    const k = ease(i / steps);
    await page.mouse.move(x0 + (x - x0) * k, y0 + (y - y0) * k);
    await page.waitForTimeout(ms / steps);
  }
  pos.set(page, [x, y]);
}

async function centre(locator) {
  await locator.scrollIntoViewIfNeeded();
  const b = await locator.boundingBox();
  return [b.x + b.width / 2, b.y + b.height / 2];
}

async function hover(page, locator, ms = 700) {
  const [x, y] = await centre(locator);
  await glide(page, x, y, ms);
}

async function click(page, locator, ms = 700) {
  await hover(page, locator, ms);
  await page.waitForTimeout(150);
  await page.mouse.down();
  await page.waitForTimeout(60);
  await page.mouse.up();
}

async function type(page, locator, text, delay = 75) {
  await click(page, locator);
  await locator.pressSequentially(text, { delay });
}

async function select(page, locator, option) {
  await hover(page, locator);
  await page.waitForTimeout(200);
  await page.mouse.down();
  await page.mouse.up();
  await locator.selectOption(option);
}

/** Scroll the page smoothly by dy pixels. */
async function scroll(page, dy, ms = 1200) {
  const steps = Math.round(ms / 16);
  let done = 0;
  for (let i = 1; i <= steps; i++) {
    const target = Math.round(dy * ease(i / steps));
    await page.mouse.wheel(0, target - done);
    done = target;
    await page.waitForTimeout(ms / steps);
  }
}

const wait = (page, ms) => page.waitForTimeout(ms);

module.exports = { BASE, launch, signIn, record, glide, hover, click, type, select, scroll, wait };
