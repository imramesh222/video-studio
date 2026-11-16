// The member renews on the phone while the desk approves: both recorded at once.
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { BASE, launch, signIn, record, hover, click, wait } = require('./lib.cjs');

const DIR = path.join(__dirname, 'clips');
const SIM = path.join(DIR, 'phone.mp4');
const MEMBER = 'Aashish Rai';
const log = [];
const stamp = (what) => { log.push([Date.now(), what]); console.log(new Date().toISOString().slice(11, 23), what); };

(async () => {
  const { browser, context } = await launch();
  const page = await (await context()).newPage();
  await signIn(page);
  await page.goto(BASE + '/staff/payment-requests');
  await page.getByText(/Members who paid your QR/).waitFor();
  await wait(page, 1500);

  // The simulator's own screen recording.
  fs.rmSync(SIM, { force: true });
  const sim = spawn('xcrun', ['simctl', 'io', 'booted', 'recordVideo', '--codec=h264', '--force', SIM]);
  process.on('exit', () => sim.kill('SIGINT'));
  await new Promise((resolve) => {
    const onData = (b) => { if (/Recording started/.test(String(b))) { stamp('sim-start'); resolve(); } };
    sim.stdout.on('data', onData);
    sim.stderr.on('data', onData);
  });

  const rec = await record(page, 'desk');
  stamp('desk-start');

  const code = fs.readFileSync('/Users/rameshrawat/gymbahi/.env', 'utf8').match(/^MASTER_OTP=(.*)$/m)[1];
  const maestro = spawn('maestro', ['test', path.join(__dirname, 'flows/member.yaml'),
    '-e', `REF=ESW${String(Date.now()).slice(-8)}`, '-e', `CODE=${code}`], { cwd: path.join(__dirname, 'flows') });
  let buf = '';
  maestro.stdout.on('data', (b) => {
    buf += b;
    const lines = buf.split('\n');
    buf = lines.pop();
    for (const line of lines) {
      const m = line.match(/^\s*(Tap on .*?|Input text .*?|Assert .*?|Run pause\.yaml|Scroll.*?)\.\.\.\s*$/);
      if (m) stamp('phone: ' + m[1]);
      if (/FAILED/.test(line)) stamp('phone FAILED: ' + line.trim());
    }
  });
  const done = new Promise((resolve) => maestro.on('exit', (c) => { stamp('maestro-exit ' + c); resolve(c); }));

  // The desk: the request arrives by itself, then the owner approves it.
  // The nearest box around the member's name that has its own Approve button.
  const card = page.getByText(new RegExp(MEMBER)).first()
    .locator('xpath=ancestor::*[.//button[normalize-space()="Approve"]][1]');
  await card.waitFor({ timeout: 180000 });
  stamp('desk: request arrived');
  rec.mark('arrived');
  await wait(page, 600);
  await hover(page, page.getByText(new RegExp(MEMBER)).first(), 900);
  await wait(page, 1600);
  await click(page, card.getByRole('button', { name: 'Approve' }));
  const dialog = page.getByRole('dialog');
  await dialog.waitFor();
  await wait(page, 1200);
  await click(page, dialog.getByRole('button', { name: 'Approve' }), 600);
  stamp('desk: approved');
  rec.mark('approved');

  const exit = await done;
  await wait(page, 800);
  await rec.stop();
  sim.kill('SIGINT');
  await new Promise((r) => sim.on('exit', r));
  stamp('sim-stopped');
  fs.writeFileSync(path.join(DIR, 'split-log.json'), JSON.stringify(log, null, 1));
  await browser.close();
  process.exit(exit);
})().catch((e) => { console.error(e); process.exit(1); });
