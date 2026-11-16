// The desk scenes, recorded one after another: `node scenes.cjs [name ...]`.
const { BASE, launch, signIn, record, glide, hover, click, type, select, scroll, wait } = require('./lib.cjs');

const only = process.argv.slice(2);
const want = (name) => only.length === 0 || only.includes(name);

const nav = (page, name) =>
  page.getByRole('link', { name, exact: true }).filter({ visible: true }).first();

async function settle(page, ms = 1200) {
  // Not 'networkidle': the desk keeps a live connection open.
  await page.waitForLoadState('load').catch(() => {});
  await wait(page, ms);
}

(async () => {
  const { browser, context } = await launch();

  if (want('landing')) {
    const page = await (await context()).newPage();
    await page.goto(BASE + '/');
    await settle(page, 2500);
    const rec = await record(page, 'landing');
    await wait(page, 1200);
    await hover(page, page.getByRole('link', { name: /See how it works/ }).first(), 1200);
    await wait(page, 900);
    await scroll(page, 760, 1800);
    await wait(page, 1600);
    await rec.stop();
    await page.close();
  }

  const ctx = await context();
  const page = await ctx.newPage();
  await signIn(page);
  await settle(page);
  // The setup checklist is for a new gym; the demo is past it.
  const hide = page.getByRole('button', { name: 'Hide this' });
  if (await hide.isVisible().catch(() => false)) await hide.click();

  if (want('today')) {
    await page.goto(BASE + '/staff');
    await settle(page, 2000);
    const rec = await record(page, 'today');
    await wait(page, 800);
    for (const label of ['Check-ins today', 'Collected today', 'Active members', /Owed by/]) {
      await hover(page, page.getByText(label).first(), 650);
      await wait(page, 450);
    }
    rec.mark('today2');
    await scroll(page, 330, 1100);
    await hover(page, page.getByText(/app payments? to approve/).first(), 800);
    await wait(page, 1200);
    await hover(page, page.getByText(/stopped coming/).first(), 700);
    await wait(page, 1300);
    await rec.stop();
  }

  if (want('members')) {
    await page.goto(BASE + '/staff');
    await settle(page, 1500);
    const rec = await record(page, 'members');
    await wait(page, 500);
    await click(page, nav(page, 'Members'));
    await settle(page, 1300);
    await click(page, page.getByRole('button', { name: /^Expiring this week/ }).first());
    await settle(page, 1700);
    await click(page, page.getByRole('button', { name: /^Owe money/ }).first());
    await settle(page, 1700);
    await rec.stop();
  }

  if (want('add')) {
    await page.goto(BASE + '/staff/members');
    await settle(page, 1500);
    const rec = await record(page, 'add');
    await wait(page, 400);
    await click(page, page.getByRole('link', { name: 'Add member' }).or(page.getByRole('button', { name: 'Add member' })).filter({ visible: true }).first());
    await page.getByLabel('Full name').waitFor();
    await wait(page, 600);
    await type(page, page.getByLabel('Full name'), 'Sanjay Thapa');
    const phone = '98' + String(Math.floor(Math.random() * 1e8)).padStart(8, '0');
    await type(page, page.getByLabel('Mobile number'), phone, 55);
    await wait(page, 300);
    await scroll(page, 520, 1100);
    await select(page, page.getByLabel('Plan'), { label: '1 month — Rs 2,500' });
    await wait(page, 900);
    rec.mark('add2');
    await select(page, page.getByLabel('Paid by'), 'esewa');
    await wait(page, 500);
    const ref = page.getByLabel(/Transaction ID/);
    if (await ref.isVisible().catch(() => false)) {
      await scroll(page, 260, 700);
      // Each ID can be used once, so a fresh one per take.
      await type(page, ref, 'ESW' + String(Date.now()).slice(-7), 60);
    }
    await wait(page, 600);
    await click(page, page.getByRole('button', { name: 'Save member' }));
    await page.getByRole('heading', { name: /Sanjay Thapa/ }).waitFor({ timeout: 20000 });
    rec.mark('add3');
    await settle(page, 1200);
    await click(page, page.getByRole('link', { name: 'Print receipt' }));
    await page.getByText('Payment receipt', { exact: true }).waitFor({ timeout: 20000 });
    await settle(page, 2600);
    await rec.stop();
  }

  if (want('door')) {
    await page.goto(BASE + '/staff/door');
    await settle(page, 1500);
    const rec = await record(page, 'door');
    await wait(page, 500);
    await type(page, page.getByLabel(/Find a member/), 'Aashish Rai', 110);
    await settle(page, 900);
    await click(page, page.getByRole('button', { name: 'Check in' }).first());
    await settle(page, 2600);
    await rec.stop();
  }

  if (want('reports')) {
    await page.goto(BASE + '/staff/reports');
    await settle(page, 2000);
    const rec = await record(page, 'reports');
    await wait(page, 600);
    await hover(page, page.getByText('Profit', { exact: true }).first(), 900);
    await wait(page, 600);
    await hover(page, page.getByText('Renewal rate', { exact: true }).first(), 700);
    await wait(page, 500);
    await scroll(page, 520, 1500);
    await hover(page, page.getByText('Money in and out by month').first(), 900);
    await wait(page, 1800);
    await rec.stop();
  }

  if (want('nepali')) {
    await page.goto(BASE + '/staff/profile');
    await settle(page, 1200);
    await page.getByLabel('Show GymBhai in').selectOption('ne');
    await settle(page, 1200);
    await page.goto(BASE + '/staff');
    await settle(page, 2500);
    const rec = await record(page, 'nepali');
    await wait(page, 700);
    await glide(page, 700, 330, 1400);
    await wait(page, 500);
    await glide(page, 1100, 330, 1200);
    await wait(page, 1600);
    await rec.stop();
    await page.goto(BASE + '/staff/profile');
    await settle(page, 1200);
    await page.locator('select:has(option[value="gym"])').first().selectOption('gym');
    await settle(page, 800);
  }

  await browser.close();
})().catch((e) => { console.error(e); process.exit(1); });
