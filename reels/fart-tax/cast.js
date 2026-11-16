// The cast of The Fart Tax: toy-like people built from one pattern, and the machines.
// Every person: g (feet on the ground) > inner (bob, hop) > hips, legs and upper (bends at the hips) > torso, arms, head.
const darker = (c, k) => '#' + new THREE.Color(c).multiplyScalar(k).getHexString();
const FONT = 'Montserrat, sans-serif';

// ---------- faces: one mouth picture per mood ----------
function faceTextures() {
  const line = '#3b1f1f', dark = '#5a1828';
  const hole = (g, x, y, rx, ry, teeth) => {
    g.fillStyle = dark; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, 7); g.fill();
    g.save(); g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, 7); g.clip();
    g.fillStyle = '#ff7d8f'; g.beginPath(); g.ellipse(x, y + ry * 0.8, rx * 0.7, ry * 0.5, 0, 0, 7); g.fill();
    if (teeth) { g.fillStyle = '#fff'; g.fillRect(x - rx, y - ry, rx * 2, ry * 0.4); }
    g.restore();
    g.lineWidth = 8; g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, 7); g.stroke();
  };
  const shapes = {
    smile: (g, x, y) => { g.beginPath(); g.moveTo(x - 52, y - 10); g.quadraticCurveTo(x, y + 38, x + 52, y - 10); g.stroke(); },
    flat: (g, x, y) => { g.beginPath(); g.moveTo(x - 40, y + 2); g.lineTo(x + 40, y + 2); g.stroke(); },
    frown: (g, x, y) => { g.beginPath(); g.moveTo(x - 48, y + 18); g.quadraticCurveTo(x, y - 22, x + 48, y + 18); g.stroke(); },
    smirk: (g, x, y) => { g.beginPath(); g.moveTo(x - 44, y + 6); g.quadraticCurveTo(x + 8, y + 24, x + 52, y - 18); g.stroke(); },
    wavy: (g, x, y) => { g.beginPath(); g.moveTo(x - 50, y); g.bezierCurveTo(x - 30, y - 24, x - 14, y + 24, x, y);
      g.bezierCurveTo(x + 14, y - 24, x + 30, y + 24, x + 50, y); g.stroke(); },
    o: (g, x, y) => hole(g, x, y, 24, 30),
    yell: (g, x, y) => hole(g, x, y, 46, 54, true),
    grin: (g, x, y) => {
      const d = () => { g.beginPath(); g.moveTo(x - 60, y - 18); g.lineTo(x + 60, y - 18); g.bezierCurveTo(x + 58, y + 30, x + 30, y + 52, x, y + 52);
        g.bezierCurveTo(x - 30, y + 52, x - 58, y + 30, x - 60, y - 18); g.closePath(); };
      g.fillStyle = dark; d(); g.fill();
      g.save(); d(); g.clip();
      g.fillStyle = '#fff'; g.fillRect(x - 60, y - 18, 120, 24);
      g.fillStyle = '#ff7d8f'; g.beginPath(); g.ellipse(x, y + 52, 34, 20, 0, 0, 7); g.fill();
      g.restore();
      g.lineWidth = 8; d(); g.stroke();
    },
    grit: (g, x, y) => {
      g.fillStyle = '#fff'; g.beginPath(); g.roundRect(x - 50, y - 20, 100, 40, 16); g.fill();
      g.lineWidth = 8; g.stroke();
      g.lineWidth = 5; g.beginPath(); g.moveTo(x - 50, y); g.lineTo(x + 50, y);
      for (const dx of [-25, 0, 25]) { g.moveTo(x + dx, y - 20); g.lineTo(x + dx, y + 20); }
      g.stroke();
    },
    puff: (g, x, y) => { g.lineWidth = 10; g.beginPath(); g.arc(x, y, 9, 0, 7); g.stroke(); },
  };
  const out = {};
  for (const [name, draw] of Object.entries(shapes)) {
    out[name] = canvasTex(256, 192, (g, w, h) => { g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = line; g.lineWidth = 12; draw(g, w / 2, h / 2); });
  }
  return out;
}

function eye(parent, pos, r, iris) {
  const e = group(parent, pos);
  mesh(sphere(r), mat('#ffffff', { roughness: 0.3 }), e);
  mesh(sphere(r * 0.74), mat(iris, { roughness: 0.25 }), e, [0, -r * 0.05, r * 0.45]);
  mesh(sphere(r * 0.4), mat('#140a05', { roughness: 0.2 }), e, [0, -r * 0.05, r * 0.88]);
  e.userData.shine = mesh(sphere(r * 0.22), mat('#ffffff', { emissive: '#ffffff', emissiveIntensity: 0.8 }), e, [-r * 0.25, r * 0.3, r * 1.08]);
  return e;
}

// Cloth patterns that wrap around a body.
function stripesTex(a, b) {
  const tex = canvasTex(256, 32, (g) => { for (let i = 0; i < 16; i++) { g.fillStyle = i % 2 ? a : b; g.fillRect(i * 16, 0, 16, 32); } });
  tex.wrapS = THREE.RepeatWrapping;
  return tex;
}
function heartsTex() {
  const tex = canvasTex(256, 128, (g) => {
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, 256, 128);
    g.fillStyle = '#ff4d6d';
    [[32, 30], [96, 52], [160, 28], [224, 56], [64, 96], [128, 104], [192, 92]].forEach(([x, y]) => {
      g.beginPath(); g.moveTo(x, y + 14); g.bezierCurveTo(x - 22, y - 2, x - 10, y - 18, x, y - 6); g.bezierCurveTo(x + 10, y - 18, x + 22, y - 2, x, y + 14); g.fill();
    });
  });
  tex.wrapS = THREE.RepeatWrapping;
  return tex;
}

let SEED = 0;
function makePerson(o) {
  const w = o.belly || 1, c = { who: o.who, seed: ++SEED, o };
  const g = group(), inner = group(g);
  const skin = mat(o.skin, { roughness: 0.72 });
  const top = o.topMat || mat(o.top, { roughness: 0.85 });
  const pants = o.pantsMat || mat(o.pants, { roughness: 0.85 });
  const shoe = mat(o.shoes || '#3a3a44');
  const hairM = mat(o.hairColor || '#3b2a20', { roughness: 0.9 });
  const white = mat('#ffffff', { roughness: 0.8 });
  const gold = metal('#f5c542');

  // hips (straight down from the waist, rounded underneath) and legs
  const hips = group(inner, [0, 1.03, 0]);
  hips.scale.set(w, 1, 0.84 * w);
  c.pantsMeshes = [mesh(cyl(0.325, 0.31, 0.36, 32), pants, hips), mesh(sphere(0.31), pants, hips, [0, -0.18, 0], [1, 0.42, 1])];
  const legs = [-1, 1].map((sx) => {
    const l = group(inner, [sx * 0.17 * Math.sqrt(w), 0.95, 0]);
    const leg = mesh(capsule(0.125, 0.5), o.bareLegs ? skin : pants, l, [0, -0.42, 0]);
    if (!o.bareLegs) c.pantsMeshes.push(leg);
    if (o.bareLegs && !o.dress) c.pantsMeshes.push(mesh(cyl(0.165, 0.178, 0.3, 20), pants, l, [0, -0.17, 0]));   // boxer shorts
    if (o.socks) mesh(cyl(0.132, 0.132, 0.2, 16), mat(o.socks), l, [0, -0.66, 0]);
    mesh(sphere(0.16), shoe, l, [0, -0.83, 0.07], [1, 0.62, 1.5]);
    return l;
  });
  if (o.dress) mesh(cyl(0.33 * w, 0.56, 0.7, 28), top, inner, [0, 0.74, 0]);

  // upper body
  const upper = group(inner, [0, 1.0, 0]);
  const torso = mesh(capsule(0.33, 0.42), top, upper, [0, 0.5, 0], [w, 1, 0.84 * w]);
  // How far the chest sticks out at (x, y), to pin buttons and chains onto it.
  const chest = (x, y) => {
    const r2 = 0.33 * 0.33 - (y > 0.71 ? (y - 0.71) ** 2 : y < 0.29 ? (0.29 - y) ** 2 : 0);
    return 0.84 * w * Math.sqrt(Math.max(0, r2 - (x / w) ** 2));
  };
  const zf = chest(0, 0.5);
  if (o.hoodie) {
    const hood = mesh(new THREE.TorusGeometry(0.29, 0.09, 12, 28), top, upper, [0, 0.97, -0.08]);
    hood.rotation.x = Math.PI / 2 + 0.34;
    mesh(sphere(0.2), mat(darker(o.top, 0.86), { roughness: 0.85 }), upper, [0, 0.27, zf - 0.06], [1.25, 0.62, 0.5]);
    for (const sx of [-1, 1]) mesh(capsule(0.014, 0.2), white, upper, [sx * 0.08, 0.68, zf + 0.012]);
  }
  if (o.suit) {
    mesh(sphere(0.16), white, upper, [0, 0.72, zf - 0.055], [0.85, 1.4, 0.6]);
    if (o.tie) mesh(box(0.085, 0.36, 0.03), mat(o.tie), upper, [0, 0.6, zf + 0.045]);
    for (const y of [0.3, 0.14]) mesh(sphere(0.035, 12), o.tie ? mat('#15171c') : gold, upper, [0, y, chest(0, y) + 0.005]);
  }
  if (o.chain) {   // a mayor's chain of office: gold beads from shoulder to shoulder, a medallion in the middle
    for (let i = -7; i <= 7; i++) {
      const s = i / 7, x = s * 0.34 * w, y = 0.92 - 0.44 * (1 - Math.abs(s)) ** 0.8;
      mesh(sphere(0.042, 12), gold, upper, [x, y, chest(x, y) + 0.03]);
    }
    mesh(cyl(0.11, 0.11, 0.04, 24), gold, upper, [0, 0.4, chest(0, 0.4) + 0.05]).rotation.x = Math.PI / 2;
  }
  if (o.pajamas) for (const y of [0.66, 0.46, 0.26]) mesh(sphere(0.04, 12), white, upper, [0, y, chest(0, y) + 0.01]);
  const arms = [-1, 1].map((sx) => {
    const a = group(upper, [sx * (0.3 * w + 0.1), 0.76, 0]);
    mesh(capsule(0.1, 0.5), o.bareArms ? skin : top, a, [0, -0.3, 0]);
    mesh(sphere(0.12), skin, a, [0, -0.7, 0]);
    return a;
  });

  // head
  const head = group(upper, [0, 1.36, 0]);
  mesh(sphere(0.46, 48), skin, head);
  for (const sx of [-1, 1]) mesh(sphere(0.095, 16), skin, head, [sx * 0.45, -0.02, 0], [0.6, 1, 0.8]);
  mesh(sphere(0.062, 16), mat(darker(o.skin, 0.9), { roughness: 0.7 }), head, [0, -0.06, 0.455]);
  const eyes = [-1, 1].map((sx) => eye(head, [sx * 0.17, 0.07, 0.395], 0.09, o.iris || '#5b3a22'));
  if (o.lids) eyes.forEach((e) => {   // heavy eyelids: always a bit tired
    const lid = mesh(new THREE.SphereGeometry(0.098, 24, 12, 0, Math.PI * 2, 0, 1.15), skin, e);
    lid.rotation.x = 0.3; lid.castShadow = false;
    e.userData.shine.visible = false;
  });
  const brows = [-1, 1].map((sx) => {
    const b = group(head, [sx * 0.17, 0.2, 0.425]);
    const m = mesh(capsule(0.022, 0.12), hairM, b); m.rotation.z = Math.PI / 2; m.castShadow = false;
    return b;
  });
  const mouth = new THREE.Mesh(new THREE.PlaneGeometry(0.27, 0.2), decalMat(R.faces.smile));
  mouth.position.set(0, -0.215, 0.423); mouth.rotation.x = 0.45; head.add(mouth);
  for (const sx of [-1, 1]) mesh(sphere(0.075, 16), mat('#ff8fa3', { transparent: true, opacity: 0.4 }), head, [sx * 0.3, -0.1, 0.335], [1, 0.7, 0.4]).castShadow = false;
  const cheeks = [-1, 1].map((sx) => { const m = mesh(sphere(0.17, 20), skin, head, [sx * 0.27, -0.17, 0.26]); m.visible = false; return m; });

  // hair, hats, glasses
  const cap = (tilt = -0.72, r = 0.478) => { const m = mesh(new THREE.SphereGeometry(r, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), hairM, head); m.rotation.x = tilt; return m; };
  if (o.hair === 'messy') {
    cap();
    [[0, 0.47, 0.08, 0.17], [-0.2, 0.43, 0.12, 0.15], [0.21, 0.43, 0.1, 0.16], [-0.36, 0.31, 0, 0.14], [0.37, 0.3, -0.02, 0.15], [0.06, 0.45, -0.18, 0.18],
      [-0.18, 0.4, -0.24, 0.17], [0.1, 0.4, 0.27, 0.12], [-0.13, 0.41, 0.25, 0.115], [0.27, 0.36, 0.2, 0.1], [-0.3, 0.36, 0.17, 0.1]]
      .forEach(([x, y, z, r]) => mesh(sphere(r, 16), hairM, head, [x, y, z]));
  }
  if (o.hair === 'short') cap();
  if (o.hair === 'slick') { cap(-0.62, 0.487); mesh(sphere(0.15, 16), hairM, head, [0.1, 0.33, 0.3], [1.7, 0.5, 0.8]).rotation.z = 0.2; }
  if (o.hair === 'bun') { cap(-0.6); mesh(sphere(0.2, 20), hairM, head, [0, 0.54, -0.1]); }
  if (o.hair === 'long') { cap(-0.6); mesh(sphere(0.47, 24), hairM, head, [0, -0.22, -0.12], [1.04, 1.2, 0.8]); }
  if (o.hair === 'sides') for (const sx of [-1, 1]) mesh(sphere(0.14, 16), hairM, head, [sx * 0.4, 0.1, -0.1], [0.7, 1.1, 1.2]);
  const frame = (m) => {   // the bridge and the arms of a pair of glasses
    mesh(capsule(0.014, 0.08), m, head, [0, 0.08, 0.475]).rotation.z = Math.PI / 2;
    for (const sx of [-1, 1]) mesh(box(0.02, 0.02, 0.48), m, head, [sx * 0.37, 0.05, 0.245]).rotation.y = -sx * 0.342;
  };
  if (o.glasses) {
    const gm = mat('#2a2f3a', { roughness: 0.4 });
    for (const sx of [-1, 1]) mesh(new THREE.TorusGeometry(0.118, 0.017, 10, 32), gm, head, [sx * 0.17, 0.07, 0.47]);
    frame(gm);
  }
  if (o.shades) {
    const dm = mat('#15171c', { roughness: 0.15 });
    for (const sx of [-1, 1]) mesh(sphere(0.13, 24), dm, head, [sx * 0.175, 0.07, 0.41], [1.1, 0.78, 0.55]);
    frame(dm);
    eyes.forEach((e) => { e.visible = false; });
  }
  if (o.moustache) for (const sx of [-1, 1]) mesh(sphere(0.075, 16), hairM, head, [sx * 0.075, -0.13, 0.45], [1.45, 0.55, 0.6]).rotation.z = -sx * 0.35;
  if (o.topHat) {
    const hat = group(head, [0, 0.36, -0.02]), hm = mat(o.topHat, { roughness: 0.5 });
    hat.rotation.set(-0.12, 0, -0.1);
    mesh(cyl(0.5, 0.5, 0.05, 32), hm, hat);
    mesh(cyl(0.33, 0.31, 0.5, 32), hm, hat, [0, 0.27, 0]);
    mesh(cyl(0.335, 0.335, 0.1, 32), gold, hat, [0, 0.09, 0]);
  }
  if (o.phone) {
    c.phone = group(arms[1], [0, -0.78, 0.07]);
    c.phone.rotation.x = 1.15;   // upright when the arm is held out in front
    mesh(slab(0.21, 0.38, 0.035, 0.035), mat('#1c1f26', { roughness: 0.35 }), c.phone);
    picture(0.18, 0.34, R.phoneTex, c.phone, [0, 0, 0.02]);
  }
  if (o.bowl) {   // a bowl of plain rice, held in both hands
    c.bowl = group(upper, [0, 0.42, zf + 0.42]);
    mesh(new THREE.SphereGeometry(0.26, 24, 12, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), mat('#5aa9e6', { roughness: 0.4, side: THREE.DoubleSide }), c.bowl);
    mesh(sphere(0.235, 20), mat('#fffdf4', { roughness: 1 }), c.bowl, [0, -0.02, 0], [1, 0.55, 1]);
  }

  // the Silent Pants: a belt with a green light, a little fan on each hip, a filter can on the back
  const gadget = group(inner, [0, 1.0, 0]), steel = mat('#39424e', { roughness: 0.45 });
  mesh(new THREE.TorusGeometry(0.33, 0.04, 8, 32), steel, gadget, [0, 0.19, 0], [w, 0.84 * w, 1]).rotation.x = Math.PI / 2;
  mesh(sphere(0.045, 12), glow('#35e05a', 1.3), gadget, [0, 0.19, 0.277 * w + 0.045]);
  c.fans = [-1, 1].map((sx) => {
    const f = group(gadget, [sx * 0.26 * w, 0, 0.19 * w]);
    f.rotation.y = sx * 0.95;
    mesh(cyl(0.125, 0.125, 0.06, 24), steel, f).rotation.x = Math.PI / 2;
    mesh(new THREE.TorusGeometry(0.125, 0.02, 8, 24), metal('#e8edf2'), f, [0, 0, 0.035]);
    const blades = group(f, [0, 0, 0.04]);
    for (let i = 0; i < 3; i++) mesh(box(0.2, 0.045, 0.012), metal('#e8edf2'), blades).rotation.z = i * Math.PI / 3;
    return blades;
  });
  mesh(cyl(0.12, 0.12, 0.34, 20), metal('#cfd6de'), gadget, [0, 0, -0.3 * w]).rotation.z = Math.PI / 2;
  gadget.visible = false;

  return Object.assign(c, { g, inner, hips, upper, torso, head, eyes, brows, mouth, cheeks, armL: arms[0], armR: arms[1], legL: legs[0], legR: legs[1], gadget, pantsMat: pants, w });
}

// Put on (or take off) the Silent Pants.
function wear(c, on) {
  c.pantsMeshes.forEach((m) => { m.material = on ? R.silver : c.pantsMat; });
  c.gadget.visible = on;
}

// Stand a person at (x, z).
function place(c, x, z, o = {}) {
  scene.add(c.g);
  c.g.visible = true;
  c.g.position.set(x, o.y || 0, z);
  c.g.rotation.set(0, o.rotY || 0, o.rotZ || 0);
  c.g.scale.setScalar((c.o.s || 1) * (o.s || 1));
}

// Blink, breathe and pose. o: hop, walk (true or a speed), lean (bend forward), look / lookUp / tilt (head),
// armL / armR (out to the side), armLx / armRx (forward), mouth, brow (+ angry, − worried), squint, wide (eyes),
// puff (cheeks, 0-1), inflate (0-1), shake, sway, sit (legs out in front).
function act(c, t, o = {}) {
  const k = c.seed, P = c.o, w = c.w;
  const lid = (1 - 0.95 * blink(t, 3.1 + (k % 5) * 0.37, k * 1.7)) * (o.squint ?? 1), wide = o.wide || 1;
  c.eyes.forEach((e) => { e.scale.set(wide, wide * lid, wide); });
  c.mouth.material.map = R.faces[o.mouth || P.mouth || 'smile'];
  const brow = o.brow ?? P.brow ?? 0;
  c.brows.forEach((b, i) => { b.rotation.z = (i ? 1 : -1) * brow; b.position.y = 0.2 + (o.browUp || 0); });
  const breathe = Math.sin(t * 2.4 + k) * 0.012;
  const step = o.walk ? t * (o.walk === true ? 8 : o.walk) : 0, swing = o.walk ? Math.sin(step) * 0.55 : 0;
  c.inner.position.set(o.shake ? Math.sin(t * 47) * 0.02 * o.shake : 0, (o.hop || 0) + (o.walk ? Math.abs(Math.sin(step)) * 0.06 : 0), 0);
  c.inner.rotation.z = o.sway || 0;
  c.upper.scale.set(1 - breathe, 1 + breathe, 1 - breathe);
  c.upper.rotation.x = o.lean || 0;
  c.head.rotation.set(o.lookUp || 0, o.look || 0, (o.tilt || 0) + Math.sin(t * 1.6 + k) * 0.025);
  c.legL.rotation.x = o.sit ? -1.45 : swing; c.legR.rotation.x = o.sit ? -1.45 : -swing;
  c.armL.rotation.set((o.armLx || 0) - swing * 0.6, 0, o.armL ?? -0.14);
  c.armR.rotation.set((o.armRx || 0) + swing * 0.6, 0, o.armR ?? 0.14);
  const puff = o.puff || 0, big = o.inflate || 0;
  c.cheeks.forEach((m) => { m.visible = puff > 0.02; m.scale.setScalar(0.55 + 0.6 * puff); });
  c.torso.scale.set(w * (1 + 1.2 * big), 1 + 0.3 * big, 0.84 * w * (1 + 1.5 * big));
  c.hips.scale.set(w * (1 + 0.9 * big), 1 + 0.3 * big, 0.84 * w * (1 + 1.1 * big));
  c.armL.position.x = -(0.3 * w * (1 + 1.2 * big) + 0.1); c.armR.position.x = 0.3 * w * (1 + 1.2 * big) + 0.1;
  if (c.fans) c.fans.forEach((f, i) => { f.rotation.z = t * 9 * (i ? 1 : -1); });
}

// ---------- the people ----------
const PEOPLE = {
  toby: { skin: '#f4cdae', hair: 'messy', hairColor: '#6b4428', top: '#3fae63', pants: '#8b929c', shoes: '#f2f2f2', hoodie: true, glasses: true, lids: true,
    phone: true, iris: '#5b3a22', mouth: 'flat', belly: 0.92 },
  mayor: { skin: '#f1bfa0', hair: 'sides', hairColor: '#8d8d92', top: '#7a3db8', pants: '#6a32a3', shoes: '#22222a', suit: true, chain: true, moustache: true,
    topHat: '#4d2480', belly: 1.5, s: 0.84, iris: '#3b6ea8', mouth: 'grin', brow: 0.35 },
  puff: { skin: '#e9b792', hair: 'short', hairColor: '#4a3426', stripes: ['#7fbdf0', '#ffffff'], shoes: '#c9672b', pajamas: true, belly: 1.4, s: 1.1,
    iris: '#4a7a3a', mouth: 'smile' },
  rich: { skin: '#f3d3b3', hair: 'slick', hairColor: '#2a2320', gold: true, shoes: '#ffffff', suit: true, tie: '#15171c', shades: true, belly: 1.08, mouth: 'grin' },
  rice: { skin: '#dba77f', hair: 'bun', hairColor: '#2b1d16', top: '#ff8a5c', pants: '#ff8a5c', dress: true, bareLegs: true, shoes: '#ffffff', bowl: true,
    iris: '#3b2a1c', mouth: 'frown', brow: -0.3 },
  boxguy: { skin: '#a9744f', hair: 'short', hairColor: '#1d1b1b', top: '#4f8fe8', pants: '#394150', shoes: '#e8e8e8', iris: '#2b1d16', mouth: 'smile' },
  boxers: { skin: '#f2c8a8', hair: 'sides', hairColor: '#b0672e', top: '#ffffff', hearts: true, bareLegs: true, bareArms: true, socks: '#ffffff', shoes: '#4a4f5a',
    iris: '#3b6ea8', mouth: 'yell', brow: -0.35 },
};
function buildCast() {
  R.faces = faceTextures();
  R.silver = metal('#dfe5ec', { roughness: 0.22 });
  R.phoneTex = canvasTex(180, 340, (g, w, h) => {
    const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, '#eaf7ff'); grd.addColorStop(1, '#bfe3ff');
    g.fillStyle = grd; g.fillRect(0, 0, w, h);
    g.fillStyle = '#1e88e5'; g.fillRect(0, 0, w, 56);
    g.fillStyle = '#35c45a'; g.beginPath(); g.arc(w / 2, 190, 52, 0, 7); g.fill();
    g.fillStyle = '#fff'; g.font = `900 72px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText('$', w / 2, 194);
  });
  R.c = {};
  for (const [who, o] of Object.entries(PEOPLE)) {
    const p = { who, ...o };
    if (o.stripes) { const m = mat('#ffffff', { map: stripesTex(...o.stripes), roughness: 0.85 }); p.topMat = m; p.pantsMat = m; }
    if (o.gold) { p.topMat = metal('#f2c230', { roughness: 0.34 }); p.pantsMat = p.topMat; }
    if (o.hearts) p.pantsMat = mat('#ffffff', { map: heartsTex(), roughness: 0.85 });
    R.c[who] = makePerson(p);
  }
}

// ---------- the machines ----------
// A Sniffer: a little metal nose with sleepy eyes and a light on top. Green: asleep. Red: it caught one.
function makeSniffer() {
  const g = group(), silver = metal('#d5dbe2'), grey = mat('#5d6875', { roughness: 0.5 });
  mesh(slab(0.7, 0.66, 0.2, 0.14), grey, g);
  // The nose: a bridge that widens downward, a round tip, two wings and two nostrils facing out.
  const nose = group(g, [0, -0.02, 0.1]);
  mesh(cyl(0.04, 0.115, 0.3, 24), silver, nose, [0, 0.05, 0.05]).rotation.x = -0.4;
  mesh(sphere(0.125, 24), silver, nose, [0, -0.11, 0.13], [1.1, 0.9, 1]);
  for (const sx of [-1, 1]) mesh(sphere(0.085, 20), silver, nose, [sx * 0.125, -0.12, 0.06], [1, 0.85, 1.1]);
  const holes = [-1, 1].map((sx) => mesh(sphere(0.042, 16), mat('#20242b'), nose, [sx * 0.065, -0.165, 0.215], [1.25, 0.75, 0.9]));
  const eyes = [-1, 1].map((sx) => {
    const e = group(g, [sx * 0.2, 0.17, 0.11]);
    mesh(sphere(0.06, 16), mat('#ffffff', { roughness: 0.3 }), e);
    mesh(sphere(0.032, 12), mat('#15171c'), e, [0, 0, 0.045]);
    return e;
  });
  mesh(cyl(0.02, 0.02, 0.16, 8), grey, g, [0, 0.41, 0]);
  const lamp = mesh(sphere(0.085, 20), glow('#35d45a', 1.2), g, [0, 0.52, 0]);
  return { g, nose, holes, eyes, lamp };
}
// alarm 0 (asleep, green) to 1 (caught one: red, eyes wide, nostrils flaring).
function setSniffer(s, t, alarm = 0) {
  const col = alarm > 0.5 ? '#ff3b30' : '#35d45a';
  s.lamp.material.color.set(col); s.lamp.material.emissive.set(col);
  s.lamp.scale.setScalar(1 + alarm * (0.5 + 0.2 * Math.sin(t * 20)));
  s.eyes.forEach((e) => { e.scale.set(1 + alarm * 0.5, 0.14 + alarm * 1.36, 1); });
  const sniff = alarm ? 1 + 0.35 * Math.abs(Math.sin(t * 16)) : 1 + 0.05 * Math.sin(t * 2);
  s.holes.forEach((h) => { h.scale.set(1.25 * sniff, 0.75 * sniff, 0.9); });
  s.nose.scale.setScalar(1 + alarm * 0.12);
  s.g.rotation.z = alarm * Math.sin(t * 40) * 0.05;
}
function lampPost(parent, x, z, sniffer = true) {
  const g = group(parent, [x, 0, z]), dark = mat('#3d4654', { roughness: 0.5 });
  mesh(cyl(0.17, 0.22, 0.3, 16), dark, g, [0, 0.15, 0]);
  mesh(cyl(0.07, 0.09, 5.3, 12), dark, g, [0, 2.65, 0]);
  mesh(capsule(0.05, 0.9), dark, g, [0.45, 5.3, 0]).rotation.z = Math.PI / 2;
  mesh(cyl(0.12, 0.3, 0.16, 20), dark, g, [0.9, 5.22, 0]);
  const bulb = mesh(sphere(0.24, 20), glow('#fff3c4', 0.5), g, [0.9, 5.05, 0], [1, 0.7, 1]);
  const out = { g, bulb };
  if (sniffer) { out.sniffer = makeSniffer(); out.sniffer.g.position.set(0, 3.1, 0.16); g.add(out.sniffer.g); }
  return out;
}

// The mayor's face, for the drones' screens and the TV.
function mayorTex() {
  return canvasTex(450, 280, (g, w, h) => {
    const grd = g.createLinearGradient(0, 0, 0, h); grd.addColorStop(0, '#5a2d8f'); grd.addColorStop(1, '#2c1450');
    g.fillStyle = grd; g.fillRect(0, 0, w, h);
    const x = w / 2, y = 168;
    g.fillStyle = '#f1bfa0'; g.beginPath(); g.arc(x, y, 92, 0, 7); g.fill();
    g.fillStyle = '#3f1c6e'; g.fillRect(x - 108, y - 86, 216, 20); g.fillRect(x - 70, y - 190, 140, 110);
    g.fillStyle = '#f5c542'; g.fillRect(x - 70, y - 108, 140, 24);
    g.fillStyle = '#fff'; g.beginPath(); g.arc(x - 34, y - 12, 19, 0, 7); g.arc(x + 34, y - 12, 19, 0, 7); g.fill();
    g.fillStyle = '#16100c'; g.beginPath(); g.arc(x - 32, y - 9, 9, 0, 7); g.arc(x + 32, y - 9, 9, 0, 7); g.fill();
    g.strokeStyle = '#5a5a60'; g.lineWidth = 11; g.lineCap = 'round';
    g.beginPath(); g.moveTo(x - 62, y - 50); g.lineTo(x - 16, y - 34); g.moveTo(x + 62, y - 50); g.lineTo(x + 16, y - 34); g.stroke();
    g.fillStyle = '#6e6e74'; g.beginPath(); g.ellipse(x - 20, y + 26, 24, 10, 0.3, 0, 7); g.ellipse(x + 20, y + 26, 24, 10, -0.3, 0, 7); g.fill();
    g.fillStyle = '#5a1828'; g.beginPath(); g.moveTo(x - 42, y + 44); g.lineTo(x + 42, y + 44); g.quadraticCurveTo(x, y + 92, x - 42, y + 44); g.fill();
    g.fillStyle = '#fff'; g.fillRect(x - 36, y + 44, 72, 11);
  });
}
// A tax drone: black, one red eye, the mayor on its screen, two loudspeakers.
function makeDrone() {
  const g = group(), body = group(g), black = mat('#1b1e25', { roughness: 0.3 }), grey = mat('#6b7480', { roughness: 0.45, side: THREE.DoubleSide });
  mesh(sphere(0.5), black, body, [0, 0, 0], [1.25, 0.5, 1]);
  const rotors = [];
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) {
    mesh(box(1.12, 0.05, 0.09), black, body, [sx * 0.475, 0.05, sz * 0.3]).rotation.y = -Math.atan2(sz * 0.6, sx * 0.95);
    mesh(cyl(0.07, 0.08, 0.16, 16), black, body, [sx * 0.95, 0.1, sz * 0.6]);
    const r = group(body, [sx * 0.95, 0.2, sz * 0.6]);
    mesh(cyl(0.42, 0.42, 0.012, 32), mat('#aeb6c0', { transparent: true, opacity: 0.32 }), r).castShadow = false;
    mesh(box(0.84, 0.014, 0.07), mat('#3d4654'), r);
    rotors.push(r);
  }
  mesh(new THREE.TorusGeometry(0.2, 0.035, 10, 28), grey, body, [0, 0.02, 0.43]);
  const eyeM = glow('#ff2d2d', 1.3);
  mesh(sphere(0.165, 24), eyeM, body, [0, 0.02, 0.4]);
  for (const sx of [-1, 1]) mesh(cyl(0.025, 0.025, 0.4, 8), black, body, [sx * 0.3, -0.38, 0.08]);
  mesh(slab(1.02, 0.68, 0.08, 0.07), black, body, [0, -0.82, 0.1]);
  picture(0.92, 0.57, R.mayorTex || (R.mayorTex = mayorTex()), body, [0, -0.82, 0.145]);
  for (const sx of [-1, 1]) {
    const horn = mesh(cyl(0.22, 0.06, 0.32, 24, true), grey, body, [sx * 0.74, -0.82, 0.16]);
    horn.rotation.x = Math.PI / 2;
    mesh(sphere(0.07, 12), black, body, [sx * 0.74, -0.82, 0.04]);
  }
  return { g, body, rotors, eye: eyeM };
}
function flyDrone(d, t, k = 0) {
  d.rotors.forEach((r, i) => { r.rotation.y = t * 31 * (i % 2 ? 1 : -1) + i; });
  d.body.position.y = Math.sin(t * 2.2 + k) * 0.08;
  d.body.rotation.z = Math.sin(t * 1.3 + k) * 0.04;
  d.eye.emissiveIntensity = 1.0 + 0.5 * Math.sin(t * 6 + k);
}

// The Big Nose: the machine under City Hall that sniffs the whole town. A face plate with two dial eyes
// and a giant brass nose; about 6.5 wide and 8 tall, pipes rising from the top.
function makeBigNose() {
  const g = group(), brass = metal('#e0a83e', { roughness: 0.3 }), copper = metal('#c8733c', { roughness: 0.35 });
  const steel = mat('#3a4250', { roughness: 0.45 }), plate = mat('#4d5a6e', { roughness: 0.5 });
  mesh(box(6.4, 1.5, 3.2), steel, g, [0, 0.75, 0]);
  for (const y of [0.08, 1.5]) mesh(box(6.52, 0.16, 3.32), brass, g, [0, y, 0]);
  mesh(slab(5.9, 6.5, 0.5, 0.7), brass, g, [0, 4.6, -1.15]);
  mesh(slab(5.6, 6.2, 0.7, 0.6), plate, g, [0, 4.6, -1.0]);
  for (const sx of [-1, 1]) for (const y of [2.0, 7.2]) mesh(sphere(0.11, 12), brass, g, [sx * 2.45, y, -0.64]);
  // dials: three small ones on the base, two big ones on the plate (its eyes)
  const dial = canvasTex(256, 256, (c) => {
    c.fillStyle = '#f7f1df'; c.fillRect(0, 0, 256, 256);
    c.strokeStyle = '#3a4250'; c.lineWidth = 8;
    for (let i = 0; i <= 8; i++) { const a = Math.PI * (0.85 + i * 0.1625); c.beginPath(); c.moveTo(128 + Math.cos(a) * 82, 128 + Math.sin(a) * 82); c.lineTo(128 + Math.cos(a) * 106, 128 + Math.sin(a) * 106); c.stroke(); }
    c.fillStyle = '#e53935'; c.beginPath(); c.arc(128, 128, 106, Math.PI * 1.75, Math.PI * 2.15); c.arc(128, 128, 82, Math.PI * 2.15, Math.PI * 1.75, true); c.fill();
  });
  const dialAt = (x, y, z, r) => {
    mesh(cyl(r * 1.16, r * 1.16, 0.14, 40), brass, g, [x, y, z]).rotation.x = Math.PI / 2;
    disc(r, dial, g, [x, y, z + 0.08]);
    const n = group(g, [x, y, z + 0.1]);
    mesh(box(r * 0.1, r * 0.8, 0.02), mat('#1c1f26'), n, [0, r * 0.36, 0]);
    mesh(cyl(r * 0.13, r * 0.13, 0.05, 16), mat('#1c1f26'), n).rotation.x = Math.PI / 2;
    return n;
  };
  const needles = [[-2.1, 0.78, 1.6, 0.42], [0, 0.78, 1.6, 0.42], [2.1, 0.78, 1.6, 0.42], [-1.6, 6.15, -0.62, 0.78], [1.6, 6.15, -0.62, 0.78]].map((d) => dialAt(...d));
  const lamps = [[-1.05, 0.78, 1.64], [1.05, 0.78, 1.64], [-2.2, 7.45, -0.6], [2.2, 7.45, -0.6]]
    .map((p, i) => mesh(sphere(0.14, 16), glow(i % 2 ? '#ffd23b' : '#35d45a', 1.2), g, p));
  // the nose: a bridge that widens downward, a round tip, two wings and two nostrils facing out
  const nose = group(g);
  mesh(cyl(0.4, 1.0, 3.2, 40), brass, nose, [0, 4.75, -0.05], [1, 1, 0.85]).rotation.x = -0.32;
  const bulb = mesh(sphere(1.1, 40), brass, nose, [0, 3.15, 0.75], [1.05, 0.9, 1]);
  for (const sx of [-1, 1]) mesh(sphere(0.7, 32), brass, nose, [sx * 1.05, 3.1, 0.2], [1, 0.85, 1.15]);
  const holes = [-1, 1].map((sx) => mesh(sphere(0.33, 24), mat('#1a1410', { roughness: 0.9 }), nose, [sx * 0.5, 2.72, 1.44], [1.25, 0.75, 0.9]));
  // pipes to the whole town
  const pipe = (pts, r, m = copper) => mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts.map((p) => V(...p))), 48, r, 12), m, g);
  for (const x of [-2.1, -1.05, 0, 1.05, 2.1]) {
    pipe([[x, 7.4, -1.0], [x, 8.8, -1.0], [x * 1.55, 10.2, -1.0], [x * 1.55, 15, -1.0]], x ? 0.2 : 0.28, x % 2 ? brass : copper);
    mesh(cyl(0.34, 0.34, 0.18, 20), brass, g, [x, 7.95, -1.0]);
  }
  for (const sx of [-1, 1]) pipe([[sx * 1.6, 3.1, 0.1], [sx * 3.0, 3.2, -0.4], [sx * 3.5, 4.6, -0.9], [sx * 3.5, 15, -0.9]], 0.17, brass);
  return { g, nose, bulb, holes, needles, lamps };
}
function runBigNose(m, t, on = 1) {
  const sniff = on ? Math.abs(Math.sin(t * 3.2)) : 0;
  m.holes.forEach((h) => { h.scale.set(1.25 * (1 + 0.25 * sniff), 0.75 * (1 + 0.25 * sniff), 0.9); });
  m.bulb.scale.set(1.05 * (1 + 0.03 * sniff), 0.9 * (1 - 0.02 * sniff), 1 + 0.03 * sniff);
  m.needles.forEach((n, i) => { n.rotation.z = on ? -0.9 + 0.5 * Math.sin(t * (4 + i) + i) : 1.3; });
  m.lamps.forEach((l, i) => { l.material.emissiveIntensity = on ? 0.6 + 0.9 * (Math.sin(t * 5 + i * 2) > 0) : 0.1; });
}
// The big red button on its stand, with its sign.
function makeButton() {
  const g = group(), steel = mat('#3a4250', { roughness: 0.45 });
  const stripes = canvasTex(256, 64, (c) => {
    c.fillStyle = '#ffd23b'; c.fillRect(0, 0, 256, 64);
    c.fillStyle = '#1c1f26';
    for (let i = -2; i < 10; i++) { c.beginPath(); c.moveTo(i * 32, 64); c.lineTo(i * 32 + 16, 64); c.lineTo(i * 32 + 48, 0); c.lineTo(i * 32 + 32, 0); c.fill(); }
  });
  stripes.wrapS = THREE.RepeatWrapping; stripes.repeat.set(2, 1);
  mesh(cyl(0.55, 0.7, 1.5, 32), mat('#ffffff', { map: stripes, roughness: 0.6 }), g, [0, 0.75, 0]);
  mesh(cyl(0.64, 0.64, 0.12, 32), steel, g, [0, 1.56, 0]);
  const btn = mesh(cyl(0.42, 0.46, 0.3, 32), glow('#ff2a2a', 0.55), g, [0, 1.77, 0]);
  const sign = group(g, [0, 3.35, -0.75]);
  mesh(cyl(0.06, 0.06, 3.3, 10), steel, g, [0, 1.65, -0.78]);
  mesh(slab(2.5, 1.3, 0.1, 0.16), mat('#e53935', { roughness: 0.5 }), sign);
  picture(2.32, 1.12, canvasTex(928, 448, (c, w, h) => {
    c.fillStyle = '#ffffff'; c.fillRect(0, 0, w, h);
    c.fillStyle = '#1c1f26'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.font = `900 150px ${FONT}`; c.fillText('DISABLE', w / 2, 140);
    c.fillStyle = '#e53935'; c.fillText('FART TAX', w / 2, 316);
  }), sign, [0, 0, 0.06]);
  return { g, btn, sign };
}
// A soundproof box to live in: glass walls on a dark frame.
function glassBox(parent, w = 2.3, h = 3.5) {
  const g = group(parent), bar = mat('#39424e', { roughness: 0.5 });
  const glass = mat('#bfe8ff', { transparent: true, opacity: 0.2, roughness: 0.1, side: THREE.DoubleSide });
  mesh(box(w, h, w), glass, g, [0, h / 2, 0]).castShadow = false;
  for (const sx of [-1, 1]) for (const sz of [-1, 1]) mesh(box(0.09, h, 0.09), bar, g, [sx * w / 2, h / 2, sz * w / 2]);
  for (const y of [0.045, h]) for (const s of [-1, 1]) {
    mesh(box(w + 0.09, 0.09, 0.09), bar, g, [0, y, s * w / 2]);
    mesh(box(0.09, 0.09, w + 0.09), bar, g, [s * w / 2, y, 0]);
  }
  return g;
}
// A dollar bill, to rain out of rich pockets.
function bill(parent) {
  R.billTex = R.billTex || canvasTex(256, 120, (c, w, h) => {
    c.fillStyle = '#58b368'; c.fillRect(0, 0, w, h);
    c.strokeStyle = '#e9f7ec'; c.lineWidth = 8; c.strokeRect(10, 10, w - 20, h - 20);
    c.fillStyle = '#e9f7ec'; c.beginPath(); c.arc(w / 2, h / 2, 38, 0, 7); c.fill();
    c.fillStyle = '#2f7d43'; c.font = `900 60px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('$', w / 2, h / 2 + 4);
  });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.19), new THREE.MeshBasicMaterial({ map: R.billTex, side: THREE.DoubleSide }));
  if (parent) parent.add(m);
  return m;
}
