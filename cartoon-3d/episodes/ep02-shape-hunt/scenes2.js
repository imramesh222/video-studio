// ---------- episode 2: shapes, Lumi, evening and night ----------
const FRIENDS = ['kitty', 'ducky', 'froggy', 'birdie'];
const SHAPE = {
  circle: { word: 'CIRCLE', color: '#e53935' },
  square: { word: 'SQUARE', color: '#1e88e5' },
  triangle: { word: 'TRIANGLE', color: '#43a047' },
  star: { word: 'STAR', color: '#f2b705' },
};
const KINDS = ['circle', 'square', 'triangle', 'star'];

function shapePts(kind, r) {
  if (kind === 'square') return [[-r, -r], [r, -r], [r, r], [-r, r]];
  if (kind === 'triangle') return [[0, r * 1.15], [-r * 1.1, -r * 0.75], [r * 1.1, -r * 0.75]];
  if (kind === 'star') return [...Array(10)].map((_, i) => {
    const a = Math.PI / 2 + (i * Math.PI) / 5, rr = i % 2 ? r * 0.5 : r;
    return [Math.cos(a) * rr, Math.sin(a) * rr];
  });
  return null;
}
function shapeGeo(kind, r, depth = 0.24, bevel = 0.07) {
  const s = new THREE.Shape();
  if (kind === 'circle') s.absarc(0, 0, r, 0, Math.PI * 2, false);
  else shapePts(kind, r).forEach(([x, y], i) => (i ? s.lineTo(x, y) : s.moveTo(x, y)));
  const geo = new THREE.ExtrudeGeometry(s, { depth, bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel, bevelSegments: 5, curveSegments: 40 });
  geo.translate(0, 0, -depth / 2);
  return geo;
}
// A chunky shape toy standing up, facing the camera.
function shapeToy(parent, kind, r = 0.6, color) {
  const g = group(parent);
  const c = color || SHAPE[kind].color;
  mesh(shapeGeo(kind, r), mat(c, { roughness: 0.3, emissive: c, emissiveIntensity: 0.08 }), g);
  return g;
}
// An outline whose sides light up one at a time (counting sides).
function outline(parent, pts, color, closed = true) {
  const g = group(parent), segs = [], lit = [];
  const n = closed ? pts.length : pts.length - 1;
  for (let i = 0; i < n; i++) {
    const a = V(...pts[i], 0), b = V(...pts[(i + 1) % pts.length], 0);
    const curve = new THREE.LineCurve3(a, b);
    segs.push(mesh(new THREE.TubeGeometry(curve, 2, 0.045, 10), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.9 }), g));
    const l = mesh(new THREE.TubeGeometry(curve, 2, 0.11, 12), new THREE.MeshBasicMaterial({ color: '#fff7a8', transparent: true, opacity: 0 }), g);
    lit.push(l);
    for (const p of [a, b]) mesh(sphere(0.06, 12), new THREE.MeshBasicMaterial({ color }), g, [p.x, p.y, 0]);
  }
  return { g, segs, lit };
}
function lightSides(o, times, u) {
  o.lit.forEach((l, i) => { const k = u - times[i]; l.material.opacity = k > 0 ? Math.min(1, k * 4) * (0.75 + 0.25 * Math.sin(u * 8)) : 0; });
}
function gradientTex(stops) {
  return canvasTex(4, 512, (c) => {
    const g = c.createLinearGradient(0, 0, 0, 512);
    stops.forEach(([o, col]) => g.addColorStop(o, col));
    c.fillStyle = g; c.fillRect(0, 0, 4, 512);
  });
}
function glowSprite(color, size) {
  const tex = canvasTex(256, 256, (c) => {
    const g = c.createRadialGradient(128, 128, 10, 128, 128, 128);
    g.addColorStop(0, color); g.addColorStop(0.35, color + '88'); g.addColorStop(1, color + '00');
    c.fillStyle = g; c.fillRect(0, 0, 256, 256);
  });
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, fog: false }));
  s.scale.set(size, size, 1);
  return s;
}

function makeLumi() {
  const g = group(), inner = group(g), head = group(inner);
  const glow = glowSprite('#fff3a0', 2.6); glow.position.z = -0.25; head.add(glow);
  mesh(shapeGeo('star', 0.62, 0.3, 0.14), mat('#ffd43b', { roughness: 0.25, emissive: '#ffcc33', emissiveIntensity: 0.45 }), head);
  const eyes = [-1, 1].map((sx) => eye(head, [sx * 0.15, 0.07, 0.29], 0.075, '#4a2b12'));
  for (const sx of [-1, 1]) mesh(sphere(0.06), mat('#ff9d7a', { transparent: true, opacity: 0.6 }), head, [sx * 0.27, -0.06, 0.27], [1, 0.75, 0.4]);
  const mouth = new THREE.Mesh(new THREE.PlaneGeometry(0.2, 0.15), decalMat());
  mouth.position.set(0, -0.13, 0.3); head.add(mouth);
  const tips = shapePts('star', 0.62).filter((_, i) => i % 2 === 0).map(([x, y]) => {
    const s = glowSprite('#ffffff', 0.9); s.position.set(x * 1.05, y * 1.05, 0.2); s.material.opacity = 0; head.add(s); return s;
  });
  const light = new THREE.PointLight('#ffd970', 0, 9); light.position.set(0, 0, 0.8); head.add(light);
  return { who: 'lumi', g, inner, head, eyes, mouth, mouthStyle: 'pip', headY: 0, glow, tips, light };
}

function buildEpisode2() {
  const W = R.W;
  // Skies.
  R.skies = {
    day: R.sky,
    dusk: gradientTex([[0, '#3a4aa6'], [0.5, '#9a7fd6'], [0.85, '#ffb48a'], [1, '#ffd2a6']]),
    night: gradientTex([[0, '#08113a'], [0.6, '#16245e'], [1, '#2c3d82']]),
  };
  const starGeo = new THREE.BufferGeometry(), pts = [], r = rng(77);
  for (let i = 0; i < 700; i++) {
    const a = r() * Math.PI * 2, e = 0.12 + r() * 1.2, d = 220;
    pts.push(Math.cos(a) * Math.cos(e) * d, Math.sin(e) * d, Math.sin(a) * Math.cos(e) * d);
  }
  starGeo.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  R.starField = new THREE.Points(starGeo, new THREE.PointsMaterial({ color: '#fff8d0', size: 1.6, transparent: true, opacity: 0, fog: false }));
  scene.add(R.starField);
  R.moon = new THREE.Sprite(new THREE.SpriteMaterial({ map: canvasTex(256, 256, (c) => {
    const g = c.createRadialGradient(128, 128, 40, 128, 128, 128);
    g.addColorStop(0, 'rgba(255,248,214,1)'); g.addColorStop(0.5, 'rgba(255,248,214,1)'); g.addColorStop(0.52, 'rgba(255,248,214,.35)'); g.addColorStop(1, 'rgba(255,248,214,0)');
    c.fillStyle = g; c.fillRect(0, 0, 256, 256);
    c.strokeStyle = '#b8a77a'; c.lineWidth = 5; c.lineCap = 'round';
    c.beginPath(); c.moveTo(102, 120); c.quadraticCurveTo(110, 110, 118, 120); c.stroke();
    c.beginPath(); c.moveTo(138, 120); c.quadraticCurveTo(146, 110, 154, 120); c.stroke();
    c.beginPath(); c.moveTo(108, 146); c.quadraticCurveTo(128, 162, 148, 146); c.stroke();
  }), fog: false }));
  R.moon.position.set(-34, 36, -110); R.moon.scale.set(22, 22, 1); scene.add(R.moon);
  R.firstStar = group(scene, [7, 24, -60]);
  R.firstStar.add(glowSprite('#fff6b0', 7));
  mesh(shapeGeo('star', 1.1, 0.3, 0.12), mat('#ffe066', { emissive: '#ffd43b', emissiveIntensity: 0.9 }), R.firstStar);
  // Sun ring (scene 3) and the rest of the props.
  R.sunRing = mesh(new THREE.TorusGeometry(6.6, 0.75, 16, 96), new THREE.MeshBasicMaterial({ color: SHAPE.circle.color, transparent: true, opacity: 0, fog: false, depthTest: false }), scene);
  R.sunRing.renderOrder = 10;
  R.p = {};
  const P = R.p;
  P.float = group(W.road);
  P.floatToys = KINDS.map((k) => shapeToy(P.float, k, 0.55));
  P.duckBall = ball(W.pond, '#e53935', 0.45);
  P.game5 = group(W.valley);
  P.toys5 = [shapeToy(P.game5, 'circle', 0.55), mesh(new THREE.BoxGeometry(0.95, 0.95, 0.95), mat(SHAPE.square.color, { roughness: 0.3 }), P.game5), shapeToy(P.game5, 'triangle', 0.6)];
  P.ring5 = glowRing(P.game5, [-2.6, 0.08, 3.6], 0.9);
  // Kitty's present.
  P.present = group(W.meadow);
  mesh(new THREE.BoxGeometry(1.0, 1.0, 1.0), mat(SHAPE.square.color, { roughness: 0.35 }), P.present, [0, 0.5, 0]);
  const ribbon = mat('#ff6fae', { roughness: 0.4 });
  mesh(new THREE.BoxGeometry(1.04, 1.04, 0.16), ribbon, P.present, [0, 0.5, 0]);
  mesh(new THREE.BoxGeometry(0.16, 1.04, 1.04), ribbon, P.present, [0, 0.5, 0]);
  for (const s of [-1, 1]) mesh(sphere(0.16), ribbon, P.present, [s * 0.16, 1.1, 0], [1, 0.7, 0.45]).rotation.z = s * 0.4;
  // Counting sides: a square and a triangle with outlines.
  P.sq = group(W.meadow, [0, 2.4, 2.6]);
  shapeToy(P.sq, 'square', 0.85);
  P.sqLine = outline(P.sq, shapePts('square', 1.0), '#0d47a1');
  P.sqLine.g.position.z = 0.22;
  P.tri = group(W.forest, [0, 2.3, 2.6]);
  shapeToy(P.tri, 'triangle', 0.9);
  P.triLine = outline(P.tri, shapePts('triangle', 1.12), '#1b5e20');
  P.triLine.g.position.z = 0.22;
  // Picnic game (scene 9).
  P.game9 = group(W.meadow);
  const blanket = mesh(new THREE.PlaneGeometry(8, 2.8), new THREE.MeshStandardMaterial({ roughness: 0.9, map: canvasTex(256, 96, (c) => {
    for (let x = 0; x < 16; x++) for (let y = 0; y < 6; y++) { c.fillStyle = (x + y) % 2 ? '#ffffff' : '#ff8a80'; c.fillRect(x * 16, y * 16, 16, 16); }
  }) }), P.game9, [0, 0.03, 3.6]);
  blanket.rotation.x = -Math.PI / 2; blanket.castShadow = false;
  P.toys9 = [shapeToy(P.game9, 'circle', 0.55), mesh(new THREE.BoxGeometry(0.95, 0.95, 0.95), mat(SHAPE.square.color, { roughness: 0.3 }), P.game9), shapeToy(P.game9, 'star', 0.65)];
  P.ring9 = glowRing(P.game9, [0, 0.08, 3.6], 0.9);
  // Block tower (scene 10).
  const blockGeo = new THREE.ExtrudeGeometry(roundedShape(0.74, 0.74, 0.14), { depth: 0.74, bevelEnabled: true, bevelThickness: 0.07, bevelSize: 0.07, bevelSegments: 4 });
  blockGeo.translate(0, 0, -0.37);
  P.blocks = [0, 1, 2].map((i) => mesh(blockGeo, mat(i % 2 ? '#42a5f5' : SHAPE.square.color, { roughness: 0.35 }), W.meadow));
  // Triangle trees (scene 11): one pine with a green outline.
  P.pine = pine(W.forest, 7, -4.5, 1.45);
  P.pineLine = outline(W.forest, [[7, 6.1], [4.4, 0.9], [9.6, 0.9]], '#1b8a2a');
  P.pineLine.g.position.z = -2.0;
  // Froggy's watermelon slice.
  P.melon = group(W.forest);
  mesh(shapeGeo('triangle', 0.42, 0.14, 0.05), mat('#2e9e3a', { roughness: 0.5 }), P.melon);
  const inside = mesh(shapeGeo('triangle', 0.33, 0.16, 0.04), mat('#ff5a6a', { roughness: 0.45 }), P.melon, [0, 0.03, 0.02]);
  for (const [x, y] of [[-0.1, 0.0], [0.1, 0.0], [0, 0.18], [0, -0.14]]) mesh(sphere(0.03, 8), mat('#222'), inside, [x, y, 0.13], [0.8, 1.3, 0.5]);
  // Triangle game (scene 14): flag, button, block.
  P.game14 = group(W.forest);
  const flag = group(P.game14);
  mesh(new THREE.CylinderGeometry(0.04, 0.04, 1.6, 8), mat('#8d6e63'), flag, [-0.35, 0.8, 0]);
  const edge = mesh(shapeGeo('triangle', 0.5, 0.04, 0.02), mat('#ffffff', { roughness: 0.4 }), flag, [0.0, 1.25, -0.04]);
  edge.rotation.z = -Math.PI / 2;
  const cloth = mesh(shapeGeo('triangle', 0.42, 0.06, 0.03), mat('#2ecc40', { roughness: 0.4, emissive: '#2ecc40', emissiveIntensity: 0.15 }), flag, [0.0, 1.25, 0.02]);
  cloth.rotation.z = -Math.PI / 2;
  const btn = shapeToy(P.game14, 'circle', 0.5);
  for (const [x, y] of [[-0.12, 0.12], [0.12, 0.12], [-0.12, -0.12], [0.12, -0.12]]) mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.4, 12), mat('#7f1d1d'), btn, [x, y, 0]).rotation.x = Math.PI / 2;
  P.toys14 = [flag, btn, mesh(new THREE.BoxGeometry(0.95, 0.95, 0.95), mat(SHAPE.square.color, { roughness: 0.3 }), P.game14)];
  P.ring14 = glowRing(P.game14, [-2.6, 0.08, 3.6], 0.9);
  // Cookies on a plate (scene 18).
  P.game18 = group(W.meadow);
  mesh(new THREE.CylinderGeometry(2.6, 2.4, 0.1, 48), mat('#fafafa', { roughness: 0.3 }), P.game18, [0, 0.05, 3.6]);
  P.toys18 = ['circle', 'triangle', 'star'].map((k) => {
    const g = group(P.game18);
    mesh(shapeGeo(k, 0.5, 0.16, 0.06), mat(SHAPE[k].color, { roughness: 0.75 }), g);
    for (let i = 0; i < 5; i++) mesh(sphere(0.04, 8), mat('#5d3a1a'), g, [Math.cos(i * 1.3) * 0.2, Math.sin(i * 1.7) * 0.18, 0.14]);
    return g;
  });
  P.ring18 = glowRing(P.game18, [1.7, 0.12, 3.6], 0.75);
  // Parade and challenge shapes.
  P.carry = KINDS.map((k) => shapeToy(W.meadow, k, 0.5));
  P.big = KINDS.map((k) => shapeToy(W.meadow, k, 0.8));
  // The shape house.
  P.house = group(W.meadow, [0, 0, 1.2]);
  P.walls = mesh(new THREE.BoxGeometry(2.6, 1.9, 1.8), mat(SHAPE.square.color, { roughness: 0.4 }), P.house);
  const roofGeo = shapeGeo('triangle', 1.45, 1.8, 0.06);
  P.roof = mesh(roofGeo, mat(SHAPE.triangle.color, { roughness: 0.4 }), P.house);
  P.window = mesh(shapeGeo('circle', 0.42, 0.1, 0.04), mat(SHAPE.circle.color, { roughness: 0.3 }), P.house);
  P.topStar = mesh(shapeGeo('star', 0.42, 0.18, 0.06), mat('#ffd43b', { roughness: 0.3, emissive: '#ffcc33', emissiveIntensity: 0.3 }), P.house);
  // Recap: sun (circle), window (square), pine (triangle); Lumi joins for the star.
  P.recap = [group(W.recap), group(W.recap), group(W.recap)];
  P.recap[0].add(new THREE.Sprite(new THREE.SpriteMaterial({ map: R.sunTex, fog: false }))); P.recap[0].children[0].scale.set(5, 5, 1);
  mesh(new THREE.TorusGeometry(1.25, 0.09, 12, 64), new THREE.MeshBasicMaterial({ color: SHAPE.circle.color }), P.recap[0], [0, 0, 0.1]);
  const frame = mat(SHAPE.square.color, { roughness: 0.3 });
  for (const [x, y, w, h] of [[0, 1.1, 2.4, 0.2], [0, -1.1, 2.4, 0.2], [-1.1, 0, 0.2, 2.4], [1.1, 0, 0.2, 2.4], [0, 0, 0.12, 2.1], [0, 0, 2.1, 0.12]])
    mesh(new THREE.BoxGeometry(w, h, 0.25), frame, P.recap[1], [x, y, 0]);
  mesh(new THREE.PlaneGeometry(2.1, 2.1), mat('#cfeeff', { roughness: 0.1 }), P.recap[1], [0, 0, -0.05]);
  pine(P.recap[2], 0, 0, 0.75).position.y = -1.6;
  (R.recapObjs || []).forEach((o) => { o.parent && o.parent.remove(o); });
  R.c.lumi = makeLumi();
}

function setSky(mode) {
  scene.background = R.skies[mode];
  const day = mode === 'day', night = mode === 'night';
  scene.fog.color.set(day ? '#cbeeff' : night ? '#16224f' : '#c9a8d8');
  scene.fog.far = night ? 200 : 260;
  R.hemi.color.set(day ? '#dff4ff' : night ? '#93a8ff' : '#c7b5ff');
  R.hemi.groundColor.set(day ? '#6fa85a' : night ? '#2c3d3a' : '#6f7a5a');
  R.hemi.intensity = day ? 0.95 : night ? 0.62 : 0.82;
  R.sunLight.color.set(day ? '#fff6e0' : night ? '#c9d6ff' : '#ffb27a');
  R.sunLight.intensity = day ? 1.75 : night ? 0.75 : 1.35;
  R.sun.visible = day;
  R.moon.visible = night;
  R.starField.visible = !day;
  R.starField.material.opacity = night ? 1 : 0.4;
}

// ---------- per-frame helpers for this episode ----------
function word(kind, a, b, t, o = {}) {
  if (t < a || t >= b) return false;
  R.wordShown = true;
  const w = document.getElementById('wordWrap');
  w.style.display = 'block';
  const el = document.getElementById('wordText');
  el.textContent = SHAPE[kind].word;
  el.style.color = SHAPE[kind].color;
  document.getElementById('wordIcon').innerHTML = ICON[kind];
  document.getElementById('word').style.color = SHAPE[kind].color;
  const pop = backOut(seg(t, a, a + 0.5));
  const pulse = o.pulseFrom && t > o.pulseFrom && t < o.pulseTo ? 1 + 0.06 * Math.sin((t - o.pulseFrom) * 9) : 1;
  document.getElementById('wordInner').style.transform = `scale(${pop * pulse * (1 - seg(t, b - 0.35, b))})`;
  return true;
}
const ICON = {
  circle: `<svg viewBox="-60 -60 120 120"><circle r="46" fill="${SHAPE.circle.color}" stroke="#fff" stroke-width="12"/></svg>`,
  square: `<svg viewBox="-60 -60 120 120"><rect x="-44" y="-44" width="88" height="88" rx="10" fill="${SHAPE.square.color}" stroke="#fff" stroke-width="12"/></svg>`,
  triangle: `<svg viewBox="-60 -60 120 120"><path d="M0-50L50 40H-50Z" fill="${SHAPE.triangle.color}" stroke="#fff" stroke-width="12" stroke-linejoin="round"/></svg>`,
  star: `<svg viewBox="-60 -60 120 120"><path d="${shapePts('star', 52).map(([x, y], i) => (i ? 'L' : 'M') + x.toFixed(1) + ' ' + (-y).toFixed(1)).join('')}Z" fill="#ffd43b" stroke="#fff" stroke-width="10" stroke-linejoin="round"/></svg>`,
};
function dots(color, a, until, t) {
  if (t > a && t < until && !R.wordShown) {
    document.getElementById('wordWrap').style.display = 'block';
    document.getElementById('wordText').textContent = '';
    document.getElementById('wordIcon').innerHTML = '';
    document.getElementById('word').style.color = color;
  }
  document.querySelectorAll('.dot').forEach((d, i) => {
    const k = t - (a + i * 0.6);
    const on = k > 0 && t < until;
    d.style.visibility = on ? 'visible' : 'hidden';
    d.style.borderColor = color;
    d.style.transform = `scale(${on ? backOut(clamp(k / 0.3)) : 0})`;
  });
}
function bump(u, at, d = 0.5) { return Math.sin(Math.PI * clamp((u - at) / d)); }
function lumiAt(t, x, y, z, o = {}) {
  const L = R.c.lumi;
  place(L, x, z, { y: y + Math.sin(t * 2.2) * 0.12, rotY: o.rotY || 0, s: o.s || 1 });
  animate(L, t, {});
  L.head.rotation.z = Math.sin(t * 1.3) * 0.08;
  const tw = 1 + 0.12 * Math.sin(t * 5) + (o.glow || 0);
  L.glow.scale.set(2.6 * tw, 2.6 * tw, 1);
  L.light.intensity = o.light ?? 0.9;
  L.tips.forEach((tip, i) => { tip.material.opacity = o.tips ? o.tips[i] : 0; });
}
// The friends' "find it" game: Pip points, a friend jumps over, the right toy glows.
function game(s, u, t, toys, ring, right, friend, kind, o = {}) {
  const found = cu(s, 'found'), jump = s.cues.jump ? cu(s, 'jump') : found + 0.6;
  place(C().pip, -5.0, 4.6, { rotY: 0.5 });
  animate(C().pip, t, u < found ? POINT_R(t) : u < found + 1.5 ? WAVE(t) : {});
  if (friend) {
    const tx = [-2.6, 0, 2.6][right] + (right === 2 ? -1.2 : 1.2);
    place(C()[friend], lerp(4.9, tx, easeOut(seg(u, jump - 0.3, jump + 0.6))), 4.8, { rotY: -0.4, y: friend === 'birdie' ? 0.9 : 0 });
    animate(C()[friend], t, { hop: hop(u, jump, 0.6) + hop(u, jump + 0.7, 0.35), flap: friend === 'birdie' || (friend === 'ducky' && u > jump) });
  }
  toys.forEach((toy, i) => {
    toy.position.set([-2.6, 0, 2.6][i] * (o.spread || 1), o.y ? o.y[i] : 0.7, 3.6);
    if (i === right) highlight(toy, ring, u, found);
    else { toy.scale.setScalar(1 - 0.12 * easeOut(seg(u, found, found + 0.6))); toy.rotation.y = 0; }
  });
  if (ring) ring.position.x = [-2.6, 0, 2.6][right] * (o.spread || 1);
  const ly = o.lookY || 0.8;
  look(camPath(u, [[0, 0, 2.6, 12.5, 0, ly, 3.6], [found, 0, 2.2, 10.5, 0, ly, 3.6],
    [found + 1.0, [-2.6, 0, 2.6][right] * (o.spread || 1) * 0.7, 1.6 + (ly - 0.8), 8.0, [-2.6, 0, 2.6][right] * (o.spread || 1) * 0.8, ly, 3.6]]));
  dots(SHAPE[kind].color, s.cues.answer, s.cues.found, t);
  word(kind, s.cues.found, s.start + s.dur, t);
  sparkleAt(s.cues.found, t);
}
function seatAll(t, opts = {}) {
  seat(C().pip, 0, { s: 0.78, dy: -0.05, dz: 0.1 });
  animate(C().pip, t, { belt: true, ...(opts.wave ? WAVE(t) : {}) });
  seat(C().kitty, 1, { s: 0.7, dx: -0.3, dy: 0.5, dz: 0.2 });
  seat(C().ducky, 1, { s: 0.7, dx: 0.32, dy: 0.5, dz: 0.2 });
  seat(C().froggy, 2, { s: 0.75, dx: -0.28, dy: 0.95, dz: 0.2 });
  seat(C().birdie, 2, { s: 0.85, dx: 0.32, dy: 0.75, dz: 0.2 });
  FRIENDS.forEach((w) => animate(C()[w], t, { hop: Math.abs(Math.sin(t * 4 + w.length)) * 0.04 }));
}
const C = () => R.c;
const sh = (kind) => SHAPE[kind].color;

// ---------- the scenes ----------
const SCENES = {
  s01: { worlds: ['valley'], draw(s, u, t) {
    const d = s.dur, x = lerp(-24, -1.5, easeOut(seg(u, 0.2, 3.4))) + easeIn(seg(u, d - 1.4, d)) * 22;
    ambient(t, -1.5);
    setBus(t, x, x, u < 3.4 || u > d - 1.4);
    const pop = backOut(seg(u, cu(s, 'pop'), cu(s, 'pop') + 0.45)), l1 = ln(s, 1), l2 = ln(s, 2);
    seat(C().pip, 0, { s: Math.max(0.001, pop * 0.95), dy: -0.36 + pop * 0.15, dz: 0.5 + pop * 0.12 });
    animate(C().pip, t, u > cu(s, 'pop') + 0.3 && u < l1.b + 0.4 ? WAVE(t) : {});
    look(camPath(u, [[0, x + 2, 4.4, 18, x + 0.5, 2.2, 0], [l1.a + 0.2, 0.5, 4.4, 18, -1, 2.2, 0], [l1.a + 1.8, 0.3, 3.4, 6.2, -0.7, 2.95, 1.5],
      [l2.a - 0.7, 0.3, 3.4, 6.2, -0.7, 2.95, 1.5], [l2.a + 0.4, 9.0, 2.8, 7.5, 2.1, 2.2, 0], [d - 1.4, 9.0, 2.8, 7.5, 2.1, 2.2, 0], [d, 2.5, 4.6, 20, 6.5, 2.2, 0]]));
  } },
  s02: { worlds: ['road'], draw(s, u, t) {
    const dist = u * 7;
    R.scroll.position.x = -(dist % 50.6); R.scrollTrees.position.x = -((dist * 0.9) % 52.8);
    ambient(t, 0);
    setBus(t, 0, dist, true);
    seat(C().pip, 0, { s: 0.78, dy: -0.05, dz: 0.1 });
    animate(C().pip, t, { belt: true });
    R.p.float.visible = true;
    R.p.floatToys.forEach((toy, i) => {
      const at = cu(s, `w${i + 1}`);
      toy.position.set(-3.9 + i * 2.6, 5.0 + Math.sin(t * 2 + i) * 0.15 + bump(u, at) * 0.5, 2.0);
      toy.scale.setScalar(Math.max(0.001, backOut(seg(u, at - 0.4, at + 0.1))) * (1 + 0.25 * bump(u, at)));
      toy.rotation.y = Math.sin(t * 1.5 + i) * 0.4;
    });
    const l2 = ln(s, 2);
    look(camPath(u, [[0, -1.5, 3.6, 15.5, -0.2, 3.0, 0], [l2.a - 0.6, -1.0, 3.6, 15.5, 0, 3.0, 0], [l2.a + 0.8, 11.5, 2.7, 5.5, 2.8, 2.4, 0]]));
    KINDS.forEach((k, i) => word(k, s.cues[`w${i + 1}`], i < 3 ? s.cues[`w${i + 2}`] : s.cues.w4 + 0.9, t));
  } },
  s03: { worlds: ['valley'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, 2.6, 0, false);
    seat(C().pip, 0, { s: 0.9, dy: -0.15, dz: 0.35 });
    animate(C().pip, t, { armR: 2.3 + Math.sin(t * 3) * 0.08, lookUp: -0.3 });
    const c = cu(s, 'shape');
    look(camPath(u, [[0, 6.5, 3.0, 9.5, 3.4, 2.9, 1], [ln(s, 1).a + 0.4, 6.5, 3.0, 9.5, 3.4, 2.9, 1], [c, 5.5, 2.6, 11, 34, 34, -95]]));
    // Face the camera of this frame, after it has moved.
    R.sunRing.position.copy(R.sun.position);
    R.sunRing.lookAt(cam.position);
    R.sunRing.material.opacity = clamp((u - c) * 2) * (0.8 + 0.2 * Math.sin(u * 6));
    R.sunRing.scale.setScalar(Math.max(0.001, backOut(seg(u, c, c + 0.6))));
    word('circle', s.cues.shape, s.start + s.dur, t, { pulseFrom: s.cues.ask, pulseTo: s.cues.answer + 2.2 });
    dots(sh('circle'), s.cues.answer, s.cues.sparkle, t);
    sparkleAt(s.cues.shape, t); sparkleAt(s.cues.sparkle, t);
  } },
  s04: { worlds: ['pond'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, 9, 0, false, -6, -0.2);
    const roll = cu(s, 'roll'), k = easeOut(seg(u, roll, roll + 1.8));
    const bx = lerp(2.3, 4.6, k);
    R.p.duckBall.visible = true;
    R.p.duckBall.position.set(bx, 0.45, 3.9);
    R.p.duckBall.rotation.set(0, 0, -(bx - 2.3) / 0.45);
    place(C().ducky, 1.1, 3.6, { rotY: 0.2 });
    animate(C().ducky, t, { flap: u > roll - 0.3 && u < roll + 0.5, hop: hop(u, roll - 0.2, 0.25, 0.4) });
    place(C().pip, -1.7, 3.9, { rotY: 0.55 });
    animate(C().pip, t, u > ln(s, 2).a ? POINT_R(t) : {});
    look(camPath(u, [[0, 0.8, 1.6, 8.2, 1.0, 1.0, 3.7], [roll, 1.4, 1.6, 8.6, 1.8, 0.8, 3.8], [roll + 1.8, 1.6, 1.8, 9.4, 2.2, 0.8, 3.8]]));
  } },
  s05: { worlds: ['valley'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, 7.5, 0, false, -3.5);
    R.p.game5.visible = true;
    game(s, u, t, R.p.toys5, R.p.ring5, 0, 'kitty', 'circle', { y: [0.75, 0.55, 0.75] });
  } },
  s06: { worlds: ['valley'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, 0, 0, false);
    const ns = ['n1', 'n2', 'n3', 'n4'].map((n) => cu(s, n));
    const order = [1, 3, 2, 0]; // near rear, near front, far front, far rear
    R.bus.hubs.forEach((h, i) => {
      const k = order.indexOf(i);
      h.material.emissive.set('#ff5252');
      h.material.emissiveIntensity = u > ns[k] ? 0.6 + 0.3 * Math.sin(u * 7) : 0;
    });
    place(C().pip, 5.8, 2.8, { rotY: -0.6 });
    animate(C().pip, t, POINT(t));
    const l1 = ln(s, 1), w = (x, z) => [x, 1.25, z * 4.1, x, 0.7, z * 1.4];
    look(camPath(u, [[0, 9.5, 2.6, 5.5, 3.6, 2.2, 0], [l1.b, 9.5, 2.6, 5.5, 3.6, 2.2, 0], [ns[0] - 0.2, ...w(-2.45, 1)], [ns[1] - 0.1, ...w(2.45, 1)],
      [ns[1] + 0.8, 11.0, 2.2, 0, 3.0, 0.9, 0], [ns[2] - 0.1, ...w(2.45, -1)], [ns[3] - 0.1, ...w(-2.45, -1)], [s.dur - 0.2, 7.5, 3.0, 11, 0, 1.4, 0]]));
    ns.forEach((n, i) => number(i + 1, sh('circle'), s.start + n, t, i === 3 ? 1.8 : 1.0));
  } },
  s07: { worlds: ['meadow'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, -9, 0, false, -4);
    R.p.present.visible = true;
    R.p.present.position.set(0.4, bump(u, cu(s, 'shape'), 0.5) * 0.3, 3.9);
    R.p.present.rotation.y = -0.3;
    place(C().kitty, -0.9, 3.7, { rotY: 0.4 });
    animate(C().kitty, t, { hop: hop(u, ln(s, 1).a, 0.25, 0.4) });
    place(C().pip, -3.0, 3.9, { rotY: 0.55 });
    animate(C().pip, t, u > ln(s, 2).a ? POINT_R(t) : {});
    look(camPath(u, [[0, -0.2, 1.5, 8.0, -0.2, 0.9, 3.8], [ln(s, 2).a - 0.4, -0.3, 1.5, 8.0, -0.3, 0.9, 3.8], [ln(s, 2).a + 0.6, -1.3, 1.8, 9.8, -1.2, 1.0, 3.8]]));
    word('square', s.cues.shape, s.start + s.dur, t);
    sparkleAt(s.cues.shape, t);
  } },
  s08: { worlds: ['meadow'], draw(s, u, t) {
    ambient(t, 0);
    R.p.sq.visible = true;
    R.p.sq.position.y = 2.4 + Math.sin(t * 1.6) * 0.08;
    const ns = ['n1', 'n2', 'n3', 'n4'].map((n) => cu(s, n));
    lightSides(R.p.sqLine, [ns[0], ns[1], ns[2], ns[3]], u);
    place(C().pip, -2.5, 4.2, { rotY: 0.5 }); animate(C().pip, t, POINT_R(t));
    place(C().kitty, 2.5, 4.2, { rotY: -0.5 }); animate(C().kitty, t, { hop: ns.map((n) => hop(u, n, 0.15, 0.3)).reduce((a, b) => a + b, 0) });
    look([0, 2.2, 10.2, 0, 2.0, 2.6]);
    ns.forEach((n, i) => number(i + 1, sh('square'), s.start + n, t, i === 3 ? 1.8 : Math.min(1.0, ns[i + 1] - n)));
  } },
  s09: { worlds: ['meadow'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, -10, 0, false, -4);
    R.p.game9.visible = true;
    game(s, u, t, R.p.toys9, R.p.ring9, 1, 'kitty', 'square', { y: [0.75, 0.5, 0.8] });
  } },
  s10: { worlds: ['meadow'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, -10, 0, false, -4);
    const ns = ['n1', 'n2', 'n3'].map((n) => cu(s, n)), wob = cu(s, 'wobble'), clapAt = cu(s, 'clap');
    const sway = u > wob ? Math.sin((u - wob) * 9) * 0.09 * Math.exp(-(u - wob) * 1.6) : 0;
    R.p.blocks.forEach((b, i) => {
      const k = seg(u, ns[i] - 0.5, ns[i]);
      b.visible = u > ns[i] - 0.5;
      const y = 0.45 + i * 0.9;
      b.position.set(Math.sin(sway) * y, lerp(6, y, easeIn(k)), 3.8);
      b.rotation.set(0, (1 - k) * 0.8, sway);
    });
    place(C().pip, -1.9, 4.4, { rotY: 0.45 });
    animate(C().pip, t, u > clapAt && u < clapAt + 1.6 ? CLAP(t) : u < ns[2] + 0.3 ? POINT_R(t) : {});
    place(C().kitty, 1.9, 4.4, { rotY: -0.45 });
    animate(C().kitty, t, { hop: hop(u, clapAt, 0.45) + hop(u, clapAt + 0.6, 0.35), tilt: u > wob && u < wob + 1 ? 0.2 : 0 });
    look(camPath(u, [[0, 0, 1.8, 10.5, 0, 1.0, 3.8], [ns[2], 0, 2.3, 10.5, 0, 1.6, 3.8]]));
    ns.forEach((n, i) => number(i + 1, sh('square'), s.start + n, t, i === 2 ? 1.6 : Math.min(1.0, ns[i + 1] - n)));
    if (u > ln(s, 4).a) word('square', s.start + ln(s, 4).a, s.start + s.dur, t);
  } },
  s11: { worlds: ['forest'], draw(s, u, t) {
    const x = lerp(-16, 12, u / s.dur);
    ambient(t, 0);
    setBus(t, x, x, true);
    seat(C().pip, 0, { s: 0.9, dy: -0.15, dz: 0.35 });
    animate(C().pip, t, u > ln(s, 1).a && u < ln(s, 1).b + 0.3 ? WAVE(t) : {});
    const c = cu(s, 'shape'), l2 = ln(s, 2);
    R.p.pine.visible = true;
    R.p.pineLine.g.visible = u > c - 0.2;
    R.p.pineLine.segs.forEach((m) => { m.material.opacity = clamp((u - c) * 2); });
    lightSides(R.p.pineLine, [c, c, c], u);
    look(camPath(u, [[0, x - 4, 6, 20, x, 1.8, 0], [c - 0.6, 5.2, 3.0, 12.5, 7, 3.0, -4.5], [l2.a + 0.4, 6.0, 3.6, 9.5, 7, 4.4, -4.5]]));
    word('triangle', s.cues.shape, s.start + s.dur, t);
    sparkleAt(s.cues.shape, t);
  } },
  s12: { worlds: ['forest'], draw(s, u, t) {
    ambient(t, 0);
    R.froggyLeaf.visible = true;
    setBus(t, -9, 0, false, -1.5);
    place(C().froggy, 0.3, 4.3, { rotY: -0.15, y: 0.08 });
    animate(C().froggy, t, { hop: hop(u, ln(s, 1).a, 0.2, 0.4) });
    R.p.melon.visible = true;
    R.p.melon.position.set(0.95, 0.75 + C().froggy.inner.position.y + Math.sin(t * 2) * 0.03, 4.75);
    R.p.melon.rotation.set(0, -0.2, Math.sin(t * 1.4) * 0.1);
    const l2 = ln(s, 2);
    const k = easeOut(seg(u, l2.a - 2.0, l2.a + 0.1));
    place(C().pip, lerp(-6.5, -2.0, k), 4.6, { rotY: lerp(1.3, 0.6, k) });
    animate(C().pip, t, { walk: k > 0 && k < 1, ...(u > l2.a ? POINT_R(t) : {}) });
    look(camPath(u, [[0, 0.6, 1.0, 6.6, 0.5, 0.75, 4.4], [l2.a - 1.8, 0.6, 1.0, 6.6, 0.5, 0.75, 4.4], [l2.a + 0.3, -0.6, 1.8, 10.5, -0.6, 0.9, 4.4]]));
    if (u > ln(s, 1).a + 1.2) word('triangle', s.start + ln(s, 1).a + 1.2, s.start + s.dur, t);
  } },
  s13: { worlds: ['forest'], draw(s, u, t) {
    ambient(t, 0);
    R.p.tri.visible = true;
    R.p.tri.position.y = 2.3 + Math.sin(t * 1.6) * 0.08;
    const ns = ['n1', 'n2', 'n3'].map((n) => cu(s, n));
    lightSides(R.p.triLine, ns, u);
    place(C().pip, -2.5, 4.2, { rotY: 0.5 }); animate(C().pip, t, POINT_R(t));
    place(C().froggy, 2.5, 4.2, { rotY: -0.5 }); animate(C().froggy, t, { hop: hop(u, cu(s, 'jump'), 0.6) });
    look([0, 2.2, 10.2, 0, 2.0, 2.6]);
    ns.forEach((n, i) => number(i + 1, sh('triangle'), s.start + n, t, i === 2 ? 1.8 : Math.min(1.0, ns[i + 1] - n)));
  } },
  s14: { worlds: ['forest'], draw(s, u, t) {
    ambient(t, 0);
    setBus(t, -10, 0, false, -1.5);
    R.p.game14.visible = true;
    game(s, u, t, R.p.toys14, R.p.ring14, 0, 'froggy', 'triangle', { y: [0, 0.6, 0.5], lookY: 1.1 });
  } },
  s15: { worlds: ['meadow'], sky: 'dusk', draw(s, u, t) {
    ambient(t, 0);
    setBus(t, -6, 0, false, -1.5);
    R.firstStar.visible = true;
    R.firstStar.scale.setScalar(1 + 0.08 * Math.sin(t * 4));
    R.firstStar.lookAt(cam.position);
    place(C().pip, -0.6, 4.0, { rotY: 0.1 });
    animate(C().pip, t, { lookUp: -0.45, ...POINT_R(t) });
    place(C().birdie, 1.4, 4.2, { y: 1.3 + Math.sin(t * 3) * 0.1, rotY: -0.3 });
    animate(C().birdie, t, { flap: true, lookUp: -0.3 });
    const c = cu(s, 'shape');
    look(camPath(u, [[0, 0.6, 1.7, 10, 0.4, 1.4, 4], [c - 0.5, 0.6, 1.7, 10, 0.4, 1.6, 4], [c + 0.6, 0.4, 1.6, 11, 7, 24, -60], [ln(s, 2).a + 0.3, 0.4, 1.6, 11, 7, 24, -60], [s.dur, 0.6, 1.8, 10.5, 0.6, 2.0, 4]]));
    word('star', s.cues.shape, s.start + s.dur, t);
    sparkleAt(s.cues.shape, t);
  } },
  s16: { worlds: ['meadow'], sky: 'dusk', draw(s, u, t) {
    ambient(t, 0);
    setBus(t, -6, 0, false, -1.5);
    const land = cu(s, 'land'), k = easeOut(seg(u, 0, land));
    lumiAt(t, lerp(5, 0.7, k), lerp(10, 2.3, k), lerp(-6, 3.6, k), { glow: (1 - k) * 0.5, light: 1.1 });
    place(C().pip, -2.1, 3.5, { rotY: 0.35 });
    animate(C().pip, t, { lookUp: -0.4 * (1 - k), ...(u > ln(s, 2).a ? WAVE(t) : {}) });
    place(C().birdie, 2.8, 3.5, { y: 1.2 + Math.sin(t * 3) * 0.1, rotY: -0.4 });
    animate(C().birdie, t, { flap: true });
    look(camPath(u, [[0, 0.4, 1.6, 11, 3, 7.5, -3], [land, 0.4, 1.8, 10.5, 0.5, 2.1, 3.8], [ln(s, 1).b, 0.6, 2.0, 8.0, 0.6, 2.1, 3.8], [s.dur, 0.4, 1.9, 10.5, 0.4, 1.8, 3.8]]));
    if (u < land + 0.6) sparkleAt(s.start + land - 0.4, t);
  } },
  s17: { worlds: ['meadow'], sky: 'dusk', draw(s, u, t) {
    ambient(t, 0);
    const ns = ['n1', 'n2', 'n3', 'n4', 'n5'].map((n) => cu(s, n));
    const order = [0, 1, 4, 2, 3]; // top point, then around the star clockwise from the viewer
    const tips = [0, 1, 2, 3, 4].map((i) => clamp((u - ns[order.indexOf(i)]) * 4));
    lumiAt(t, 0.5, 2.2, 3.6, { tips, light: 1.2 });
    place(C().pip, -2.3, 4.0, { rotY: 0.5 });
    animate(C().pip, t, POINT_R(t));
    look([0.5, 2.25, 7.4, 0.5, 2.15, 3.6]);
    ns.forEach((n, i) => number(i + 1, sh('star'), s.start + n, t, i === 4 ? 1.8 : Math.min(1.0, ns[i + 1] - n)));
  } },
  s18: { worlds: ['meadow'], sky: 'dusk', draw(s, u, t) {
    ambient(t, 0);
    R.p.game18.visible = true;
    const found = cu(s, 'found');
    lumiAt(t, 4.2, 2.0, 3.8, { glow: u > found ? 0.4 : 0, light: 1.1 });
    game(s, u, t, R.p.toys18, R.p.ring18, 2, null, 'star', { y: [0.62, 0.66, 0.66], spread: 0.65 });
  } },
  s19: { worlds: ['meadow'], sky: 'dusk', draw(s, u, t) {
    const x0 = -5 + u * 1.3;
    ambient(t, x0);
    setBus(t, x0 + 1.5, x0 + 1.5, true, -1.8);
    const cs = ['c1', 'c2', 'c3', 'c4'].map((c) => cu(s, c));
    const parade = [['pip', 0], ['ducky', -1.9], ['kitty', -3.5], ['froggy', -5.1], ['birdie', -6.6]];
    const carry = { ducky: 0, kitty: 1, froggy: 2, birdie: 3 };
    parade.forEach(([who, dx], i) => {
      place(C()[who], x0 + dx + 0.5, 2.9, { rotY: 1.2, y: who === 'birdie' ? 0.8 + Math.sin(t * 3) * 0.12 : 0 });
      const k = carry[who];
      animate(C()[who], t, { walk: who === 'pip', hop: who !== 'pip' && who !== 'birdie' ? Math.abs(Math.sin(t * 6 + i)) * 0.16 : 0, flap: who === 'birdie', look: -0.9, ...(who === 'pip' ? WAVE(t) : {}) });
      if (k !== undefined) {
        const toy = R.p.carry[k];
        toy.visible = true;
        const c = C()[who];
        toy.position.set(c.g.position.x, (who === 'birdie' ? 1.3 : c.headY + 0.3) + 1.1 + bump(u, cs[k]) * 0.35, 2.9);
        toy.scale.setScalar(1 + 0.3 * bump(u, cs[k]));
        toy.rotation.y = 0.2 + Math.sin(t * 2 + k) * 0.2;
      }
    });
    lumiAt(t, x0 + 1.6, 3.4, 3.4, {});
    look([x0 - 2.6, 2.6, 13.5, x0 - 2.6, 2.0, 2]);
    cs.forEach((c, i) => word(KINDS[i], s.start + c, s.start + (cs[i + 1] ?? s.dur), t));
  } },
  s20: { worlds: ['meadow'], sky: 'dusk', draw(s, u, t) {
    ambient(t, 0);
    place(C().pip, 0, 4.0, {});
    animate(C().pip, t, u < ln(s, 1).b ? WAVE(t) : {});
    const ds = ['d1', 'd2', 'd3', 'd4'].map((d) => cu(s, d));
    FRIENDS.forEach((who, i) => {
      place(C()[who], [-3.9, -2.0, 2.0, 3.9][i], 3.0, { y: who === 'birdie' ? 0.25 : 0 });
      animate(C()[who], t, { hop: ds.map((d) => hop(u, d, 0.3, 0.4)).reduce((a, b) => a + b, 0), flap: who === 'birdie' && u > ds[0] });
    });
    lumiAt(t, 0, 2.9, 2.6, { s: 0.8 });
    const cs = ['c1', 'c2', 'c3', 'c4'];
    R.p.big.forEach((toy, i) => {
      toy.visible = true;
      const p = Math.max(bump(u, cu(s, cs[i])), bump(u, ds[i]));
      toy.position.set(-3.6 + i * 2.4, 4.6 + Math.sin(t * 1.8 + i) * 0.12 + p * 0.3, 1.0);
      toy.scale.setScalar(1 + 0.3 * p);
      toy.rotation.y = Math.sin(t * 1.2 + i) * 0.25;
    });
    look(camPath(u, [[0, 0, 2.3, 13.5, 0, 2.8, 2], [ln(s, 2).a, 0, 2.7, 12.5, 0, 3.1, 2]]));
    for (const ks of [cs, ['d1', 'd2', 'd3', 'd4']]) ks.forEach((k, i) => word(KINDS[i], s.cues[k], i < 3 ? s.cues[ks[i + 1]] : s.cues[k] + 0.9, t));
  } },
  s21: { worlds: ['meadow'], sky: 'dusk', draw(s, u, t) {
    ambient(t, 0);
    const hs = ['h1', 'h2', 'h3', 'h4'].map((h) => cu(s, h)), P = R.p;
    P.house.visible = true;
    const drop = (m, at, y, extra = {}) => {
      const k = seg(u, at - 0.6, at);
      m.visible = u > at - 0.6;
      m.position.set(extra.x || 0, lerp(y + 5, y, easeIn(k)) + bump(u, at, 0.35) * 0.08, extra.z || 0);
    };
    drop(P.walls, hs[0], 0.95);
    drop(P.roof, hs[1], 1.9 + 0.86, { z: -0.9 });
    drop(P.window, hs[2], 1.0, { z: 0.93 });
    drop(P.topStar, hs[3], 4.25);
    P.topStar.rotation.y = u > hs[3] ? Math.sin((u - hs[3]) * 2) * 0.3 : 0;
    const spots = [['pip', -2.9, 3.9], ['kitty', -4.4, 3.3], ['ducky', 2.9, 3.9], ['froggy', 4.4, 3.3]];
    spots.forEach(([who, x, z]) => {
      place(C()[who], x, z, { rotY: -x * 0.12 });
      animate(C()[who], t, { hop: hop(u, cu(s, 'done'), 0.4) + hop(u, cu(s, 'done') + 0.6, 0.3), ...(who === 'pip' ? POINT_R(t) : {}) });
    });
    place(C().birdie, 3.4, 2.4, { y: 2.0 + Math.sin(t * 3) * 0.12, rotY: -0.5 });
    animate(C().birdie, t, { flap: true });
    lumiAt(t, -1.6, 3.6, 2.6, { glow: u > hs[3] ? 0.3 : 0 });
    look(camPath(u, [[0, 0, 3.0, 13.5, 0, 2.0, 1.2], [s.dur, 0, 3.0, 11.5, 0, 2.2, 1.2]]));
    hs.forEach((h, i) => word(['square', 'triangle', 'circle', 'star'][i], s.start + h, s.start + (hs[i + 1] ?? s.dur), t));
    sparkleAt(s.cues.done, t);
  } },
  s22: { worlds: ['recap'], draw(s, u, t) {
    const rs = ['r1', 'r2', 'r3', 'r4'].map((r) => cu(s, r));
    let i = 0; rs.forEach((r, k) => { if (u >= r - 0.3) i = k; });
    R.backdrop.material.color.set(['#ffd6d4', '#d4e8ff', '#d6f5d0', '#fff1b8'][i]);
    R.p.recap.forEach((o, k) => {
      o.visible = k === i;
      const a = u - rs[k];
      o.scale.setScalar(Math.max(0.001, backOut(clamp((a + 0.3) / 0.6))));
      o.rotation.y = k === 0 ? 0 : Math.sin(a * 1.2) * 0.4;
      o.position.set(0, 1.5 + Math.sin(a * 2) * 0.1, 0);
    });
    if (i === 3) lumiAt(t, 0, 1.5, 0, { s: 1.6 * Math.max(0.001, backOut(clamp((u - rs[3] + 0.3) / 0.6))), light: 0.6 });
    look([0, 1.6, 9, 0, 1.4, 0]);
    rs.forEach((r, k) => word(KINDS[k], s.start + r, s.start + (rs[k + 1] ?? s.dur) - 0.3, t));
    rs.forEach((r) => sparkleAt(s.start + r, t));
  } },
  s23: { worlds: ['road'], sky: 'dusk', draw(s, u, t) {
    const dist = u * 7;
    R.scroll.position.x = -(dist % 50.6); R.scrollTrees.position.x = -((dist * 0.9) % 52.8);
    ambient(t, 0);
    setBus(t, 0, dist, true);
    seatAll(t, { wave: u < ln(s, 1).b + 0.6 });
    lumiAt(t, 1.6, 4.6, 2.3, { s: 0.8 });
    look(camPath(u, [[0, -0.8, 3.0, 10.5, -0.8, 2.6, 0], [ln(s, 1).b, 0.2, 3.0, 10.5, -0.2, 2.6, 0], [ln(s, 2).a + 0.3, 11.5, 2.7, 5.5, 2.8, 2.3, 0.2], [s.dur, 12.5, 2.7, 5.0, 2.9, 2.3, 0.2]]));
  } },
  s24: { worlds: ['meadow'], sky: 'night', draw(s, u, t) {
    ambient(t, 0);
    setBus(t, 4.6, 0, false, -1.6, -0.35);
    const spots = [['pip', -0.6, 4.2], ['kitty', -2.6, 3.8], ['ducky', 1.4, 4.0], ['froggy', -4.3, 3.4], ['birdie', 3.1, 3.6]];
    const bye = cu(s, 'rainbow');
    spots.forEach(([who, x, z], i) => {
      place(C()[who], x, z, { rotY: -x * 0.05, y: who === 'birdie' ? 0.9 + Math.sin(t * 3) * 0.12 : 0 });
      animate(C()[who], t, { hop: u > bye ? Math.abs(Math.sin(t * 4 + i)) * 0.2 : 0, flap: who === 'birdie' || (who === 'ducky' && u > bye), ...(who === 'pip' && u > ln(s, 1).a ? WAVE(t) : {}) });
    });
    lumiAt(t, -0.2, 3.7, 3.2, { glow: 0.3 + (u > bye ? 0.4 : 0), light: 1.8 });
    R.starField.material.opacity = 0.85 + 0.15 * Math.sin(t * 3);
    const th = cu(s, 'thanks');
    look(camPath(u, [[0, 0, 2.4, 13.5, 0, 1.8, 2], [bye, 0, 2.6, 15, 0, 2.4, 1], [th, 0, 3.0, 18, 0, 7, -10]]));
    const end = document.getElementById('end');
    end.style.display = u > th - 0.1 ? 'flex' : 'none';
    const sub = cu(s, 'subscribe');
    document.getElementById('end1').style.transform = `scale(${backOut(seg(u, th, th + 0.5))})`;
    document.getElementById('end2').style.transform = `scale(${backOut(seg(u, sub, sub + 0.5))})`;
    document.getElementById('brand').style.opacity = clamp((u - sub - 0.4) / 0.4);
    sparkleAt(s.cues.thanks, t); sparkleAt(s.cues.subscribe, t);
  } },
};

function render(t) {
  ['wordWrap', 'numWrap', 'end'].forEach((id) => { document.getElementById(id).style.display = 'none'; });
  document.querySelectorAll('.dot').forEach((d) => { d.style.visibility = 'hidden'; });
  R.sparks.forEach((s) => { s.el.style.display = 'none'; });
  R.flies.forEach((f) => { f.g.visible = false; });
  R.wordShown = false;
  Object.values(R.W).forEach((w) => { w.visible = false; });
  Object.values(R.c).forEach((c) => { c.g.visible = false; });
  R.balloons.forEach((b) => { b.visible = false; });
  R.fallLeaves.forEach((l) => { l.visible = false; });
  R.birdTree.visible = false; R.friendTree.visible = false; R.skyRainbow.visible = false;
  R.pondGame.visible = false; R.forestGame.visible = false; R.meadowGame.visible = false; R.froggyLeaf.visible = false;
  R.W.garden.visible = false; R.W.rby.visible = false;
  const P = R.p;
  [P.float, P.duckBall, P.game5, P.present, P.sq, P.tri, P.game9, P.melon, P.game14, P.game18, P.house, P.pine, P.pineLine.g, ...P.blocks, ...P.carry, ...P.big, ...P.recap]
    .forEach((o) => { o.visible = false; });
  R.firstStar.visible = false;
  R.sunRing.material.opacity = 0;
  R.bus.hubs.forEach((h) => { h.material.emissiveIntensity = 0; });
  R.bus.g.visible = false;
  setSky('day');

  const title = document.getElementById('title');
  title.style.display = t < T.title ? 'flex' : 'none';
  if (t < T.title) {
    [...title.children].forEach((d, i) => { d.style.transform = `translateY(${Math.sin(t * 3 + i) * 6}px) scale(${backOut(seg(t, 0.5 + i * 0.35, 1.2 + i * 0.35))})`; });
    R.W.valley.visible = true;
    R.skyRainbow.visible = true;
    R.skyRainbow.position.set(0, 0, -6);
    R.skyRainbow.scale.setScalar(Math.max(0.001, backOut(seg(t, 0.1, 1.0))));
    ambient(t, 0);
    look([0, 3.2 + t * 0.15, 17, 0, 4.2, -6]);
  } else {
    const s = T.scenes.find((x) => t >= x.start && t < x.start + x.dur) || T.scenes[T.scenes.length - 1];
    const def = SCENES[s.id];
    def.worlds.forEach((w) => { R.W[w].visible = true; });
    if (def.sky) setSky(def.sky);
    if (s.id === 's22') { scene.background = new THREE.Color('#ffffff'); scene.fog.far = 1000; R.sun.visible = false; R.starField.visible = false; }
    def.draw(s, t - s.start, t);
  }
  let flash = 0;
  for (const s of T.scenes) flash = Math.max(flash, 1 - Math.abs(t - s.start) / 0.3);
  document.getElementById('flash').style.opacity = clamp(flash) * 0.85;
  renderer.render(scene, cam);
}
