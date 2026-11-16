// The places of The Fart Tax (street, Toby's flat, garage, the room under City Hall), their light, and the effects
// (gas puffs, sparks, confetti, birds, bills). Each place is a group in R.W; render() shows one per shot.
const PASTEL = ['#ffd3c4', '#cfe8ff', '#fff0b8', '#d8f2d0', '#f3d6f5', '#ffe0cc', '#cdeee6', '#ffe9a8', '#e0dcff', '#ffd0d8', '#d6f0ff'];
const ROOF = ['#c0605a', '#5f7fa8', '#b5774a', '#6d9a6a', '#8a6aa8', '#c98a4a', '#4f8f8a', '#a8584f', '#6a73b5', '#b8616f', '#5a8fb0'];

function house(parent, x, z, y, i) {
  const g = group(parent, [x, y, z]), w = 4.6, h = 3.4, d = 4.4;
  mesh(box(w, h, d), mat(PASTEL[i % PASTEL.length], { roughness: 0.9 }), g, [0, h / 2, 0]);
  const tri = new THREE.Shape(); tri.moveTo(-w / 2 - 0.35, 0); tri.lineTo(w / 2 + 0.35, 0); tri.lineTo(0, 1.9); tri.closePath();
  const roof = mesh(new THREE.ExtrudeGeometry(tri, { depth: d + 0.5, bevelEnabled: false }), mat(ROOF[i % ROOF.length], { roughness: 0.85 }), g, [0, h, -(d + 0.5) / 2]);
  const white = mat('#ffffff', { roughness: 0.7 });
  const door = i % 2 ? -1 : 1;
  mesh(box(1.0, 1.8, 0.1), mat(ROOF[(i + 3) % ROOF.length], { roughness: 0.6 }), g, [door * 1.1, 0.9, d / 2 + 0.03]);
  mesh(sphere(0.06, 8), metal('#f5c542'), g, [door * 1.1 + 0.3, 0.9, d / 2 + 0.1]);
  for (const [wx, wy] of [[-door * 1.0, 1.9], [door * 1.1, 2.75]]) {
    mesh(box(1.16, wy > 2.5 ? 0.66 : 1.16, 0.08), white, g, [wx, wy, d / 2 + 0.02]);
    mesh(box(0.96, wy > 2.5 ? 0.46 : 0.96, 0.1), R.winMat, g, [wx, wy, d / 2 + 0.03]);
  }
  mesh(cyl(0.34, 0.34, 0.08, 24), white, g, [0, h + 0.75, d / 2 + 0.27]).rotation.x = Math.PI / 2;
  mesh(cyl(0.25, 0.25, 0.1, 24), R.winMat, g, [0, h + 0.75, d / 2 + 0.28]).rotation.x = Math.PI / 2;
  mesh(box(0.5, 1.3, 0.5), mat('#b9856a', { roughness: 0.9 }), g, [-door * 1.3, h + 1.1, -0.6]);
  g.userData = { x, y, z, roof };
  return g;
}
function tree(parent, x, z, s, color = '#6cc26a') {
  const g = group(parent, [x, 0, z]); g.scale.setScalar(s);
  mesh(cyl(0.22, 0.32, 2.2, 10), mat('#9a6a3a', { roughness: 0.9 }), g, [0, 1.1, 0]);
  const leaves = mat(color, { roughness: 0.85 });
  [[0, 3.0, 0, 1.3], [-0.9, 2.5, 0.2, 1.0], [0.9, 2.5, -0.1, 1.0], [0.2, 2.3, 0.8, 0.9]].forEach(([a, b, c, r]) => mesh(sphere(r, 18), leaves, g, [a, b, c]));
  return g;
}
function cloud(parent, x, y, z, s) {
  const g = group(parent, [x, y, z]); g.scale.setScalar(s);
  const m = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: 1, emissive: '#dfefff', emissiveIntensity: 0.35 });
  [[0, 0, 0, 1.6], [1.6, 0.4, 0, 1.9], [3.2, 0, 0, 1.5], [1.6, -0.5, 0.5, 1.4], [-1.3, -0.3, 0, 1.1], [4.4, -0.3, 0, 1.0]]
    .forEach(([a, b, c, r]) => { mesh(sphere(r, 18), m, g, [a, b, c]).castShadow = false; });
  return g;
}
const sign = (w, h, bg, draw) => canvasTex(w, h, (c) => { c.fillStyle = bg; c.fillRect(0, 0, w, h); c.textAlign = 'center'; c.textBaseline = 'middle'; draw(c); });

function buildStreet() {
  const g = group(scene);
  const plane = (w, d, color, x, y, z) => { const m = mesh(box(w, 0.1, d), mat(color, { roughness: 0.95 }), g, [x, y - 0.05, z]); m.castShadow = false; return m; };
  plane(240, 200, '#8fd16a', 0, -0.03, -60);
  plane(240, 3.4, '#e9e4da', 0, 0, 0);
  plane(240, 0.3, '#cfc8ba', 0, 0.02, 1.85);
  plane(240, 12, '#737b8a', 0, -0.012, 8);
  for (let i = -20; i <= 20; i++) plane(1.6, 0.18, '#f4f1e6', i * 3.4, -0.004, 6.5);
  // Three rows of houses, each row a little higher up the hill, so the town fills a tall frame.
  R.houses = [];
  [[-6, 0, 0], [-15.5, 1.3, 2.8], [-25, 2.7, 0.9], [-35, 4.2, 3.4]].forEach(([z, y, off], row) => {
    if (y) { const hill = plane(240, 10.5, '#86c962', 0, 0, z - 0.6); hill.scale.y = y * 10; hill.position.y = y / 2 - 0.02; }
    for (let i = 0; i < 11; i++) R.houses.push(house(g, -28 + i * 5.6 + off, z, y, i + row * 4));
  });
  for (let i = 0; i < 12; i++) tree(g, -30.8 + i * 5.6, -4.6, 0.75 + (i % 3) * 0.08, i % 2 ? '#6cc26a' : '#84d07a');
  for (let i = 0; i < 24; i++) mesh(sphere(0.5, 14), mat(i % 2 ? '#5fb85a' : '#79c872', { roughness: 0.9 }), g, [-32 + i * 2.8 + (i % 3) * 0.3, 0.3, -2.75], [1.3, 0.9, 1]);
  R.posts = {};
  for (const x of [-8.4, -2.8, 2.8, 8.4, 14, 19.6, 43.9]) R.posts[x] = lampPost(g, x, -1.2);
  // bus stop
  mesh(cyl(0.05, 0.05, 3.2, 10), mat('#3d4654'), g, [6.5, 1.6, -1.1]);
  mesh(cyl(0.42, 0.42, 0.06, 28), mat('#1e88e5'), g, [6.5, 3.1, -1.1]).rotation.x = Math.PI / 2;
  disc(0.36, sign(256, 256, '#1e88e5', (c) => { c.fillStyle = '#fff'; c.font = `900 96px ${FONT}`; c.fillText('BUS', 128, 134); }), g, [6.5, 3.1, -1.06]);
  mesh(box(1.9, 0.12, 0.6), mat('#b9856a'), g, [5.6, 0.62, -1.15]);
  for (const sx of [-0.8, 0.8]) mesh(box(0.1, 0.6, 0.5), mat('#3d4654'), g, [5.6 + sx, 0.3, -1.15]);
  // the big screen
  const bb = group(g, [22, 0, -1.7]);
  for (const sx of [-1.5, 1.5]) mesh(cyl(0.09, 0.09, 3.9, 10), mat('#3d4654'), bb, [sx, 1.95, 0]);
  mesh(slab(4.0, 2.5, 0.2, 0.2), mat('#1c1f26', { roughness: 0.4 }), bb, [0, 4.9, 0]);
  R.screenRed = picture(3.7, 2.2, sign(740, 440, '#e53935', (c) => { c.fillStyle = '#fff'; c.font = `900 96px ${FONT}`; c.fillText('FART TAX', 370, 110);
    c.font = `900 150px ${FONT}`; c.fillText('−$10', 370, 270); c.font = `700 44px ${FONT}`; c.fillText('PER TOOT', 370, 390); }), bb, [0, 4.9, 0.11]);
  R.screenGreen = picture(3.7, 2.2, sign(740, 440, '#2fbf5b', (c) => { c.fillStyle = '#fff'; c.font = `900 96px ${FONT}`; c.fillText('FART TAX', 370, 130);
    c.font = `900 110px ${FONT}`; c.fillText('DISABLED', 370, 280); }), bb, [0, 4.9, 0.11]);
  // City Hall, with the mayor's podium in front
  const hall = group(g, [42, 0, -6]), cream = mat('#f6ecd6', { roughness: 0.85 });
  mesh(box(13, 5.4, 5), cream, hall, [0, 2.7, 0]);
  for (let i = 0; i < 3; i++) mesh(box(13.6 - i * 0.5, 0.25, 1.4 + (2 - i) * 0.5), mat('#e2d6bb'), hall, [0, 0.125 + i * 0.25, 3.1 - i * 0.1]);
  for (let i = 0; i < 6; i++) mesh(cyl(0.3, 0.34, 4.3, 16), mat('#fffaf0'), hall, [-5 + i * 2, 2.9, 3.0]);
  mesh(box(13.4, 0.9, 1.4), cream, hall, [0, 5.5, 2.9]);
  picture(6.4, 0.7, sign(1024, 112, '#f6ecd6', (c) => { c.fillStyle = '#6a32a3'; c.font = `900 84px ${FONT}`; c.fillText('CITY HALL', 512, 60); }), hall, [0, 5.5, 3.61]);
  const ped = new THREE.Shape(); ped.moveTo(-6.9, 0); ped.lineTo(6.9, 0); ped.lineTo(0, 2.2); ped.closePath();
  mesh(new THREE.ExtrudeGeometry(ped, { depth: 1.4, bevelEnabled: false }), mat('#efe3c8'), hall, [0, 5.95, 2.2]);
  mesh(new THREE.SphereGeometry(2.1, 28, 14, 0, Math.PI * 2, 0, Math.PI / 2), mat('#7a3db8', { roughness: 0.5 }), hall, [0, 5.4, -0.4]);
  mesh(box(1.3, 1.35, 0.8), mat('#9a6a3a', { roughness: 0.7 }), g, [42, 0.68, 0.5]);
  mesh(box(1.5, 0.1, 1.0), mat('#7d5430'), g, [42, 1.4, 0.5]);
  for (const sx of [-0.3, 0, 0.3]) { mesh(cyl(0.02, 0.02, 0.5, 6), mat('#22252c'), g, [42 + sx, 1.68, 0.75]).rotation.x = 0.5; mesh(sphere(0.07, 10), mat('#22252c'), g, [42 + sx, 1.9, 0.87]); }
  // sky things
  R.clouds = [[-24, 21, -70, 1.5], [-4, 26, -85, 1.9], [16, 20, -75, 1.3], [34, 25, -90, 1.7], [52, 22, -80, 1.5]].map(([x, y, z, s]) => cloud(g, x, y, z, s));
  R.sun = new THREE.Mesh(sphere(6, 24), new THREE.MeshBasicMaterial({ color: '#ffe27a', fog: false }));
  R.sun.position.set(26, 44, -130); g.add(R.sun);
  const r = rng(9), pts = [];
  for (let i = 0; i < 260; i++) pts.push((r() - 0.5) * 400, 14 + r() * 120, -150 - r() * 40);
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
  R.stars = new THREE.Points(sg, new THREE.PointsMaterial({ color: '#ffffff', size: 0.9, fog: false })); g.add(R.stars);
  // the mayor's car, Toby's bicycle
  const car = group(g), black = mat('#4a2a78', { roughness: 0.2 });
  mesh(box(4.4, 0.75, 1.7), black, car, [0, 0.72, 0]);
  mesh(sphere(1, 24), black, car, [-0.2, 1.1, 0], [1.5, 0.62, 0.8]);
  mesh(box(1.9, 0.36, 1.72), mat('#9fd0ff', { roughness: 0.1 }), car, [-0.2, 1.22, 0]);
  R.wheels = [];
  for (const sx of [-1.35, 1.35]) for (const sz of [-0.85, 0.85]) { const wh = mesh(cyl(0.4, 0.4, 0.26, 20), mat('#2a2d33'), car, [sx, 0.4, sz]); wh.rotation.x = Math.PI / 2; R.wheels.push(wh); }
  for (const sz of [-0.55, 0.55]) { mesh(sphere(0.14, 12), glow('#fff3c4', 1.6), car, [2.2, 0.78, sz]); mesh(sphere(0.12, 12), glow('#ff2a2a', 1.3), car, [-2.2, 0.8, sz]); }
  const bike = group(g), steel = mat('#e5533d', { roughness: 0.4 });
  R.bikeWheels = [-0.7, 0.7].map((sx) => { const wh = group(bike, [sx, 0.45, 0]); mesh(new THREE.TorusGeometry(0.42, 0.045, 8, 28), mat('#22252c'), wh);
    for (let i = 0; i < 3; i++) mesh(box(0.8, 0.02, 0.02), mat('#aeb6c0'), wh).rotation.z = i * Math.PI / 3; return wh; });
  [[0, 0.72, 1.3, 0.25], [-0.32, 0.72, 0.8, -0.7], [0.35, 0.78, 0.82, 0.75], [0.62, 0.9, 0.9, 1.35]].forEach(([x, y, len, a]) => { mesh(box(len, 0.06, 0.06), steel, bike, [x, y, 0]).rotation.z = a; });
  mesh(box(0.34, 0.08, 0.2), mat('#22252c'), bike, [-0.45, 1.12, 0]);
  mesh(box(0.06, 0.06, 0.6), mat('#22252c'), bike, [0.72, 1.32, 0]);
  Object.assign(R, { car, bike });
  return g;
}

// Toby's flat: bedroom (x −12), hall door (x −6), kitchen (x 0), living room (x 12), all along one back wall.
function buildRoom() {
  const g = group(scene), wood = mat('#b98652', { roughness: 0.7 });
  mesh(box(48, 0.2, 14), mat('#d9a86c', { roughness: 0.8 }), g, [0, -0.1, 2]).castShadow = false;
  [[-12, '#bcd9f2'], [0, '#ffe7b0'], [12, '#cfe8c5']].forEach(([x, c]) => { mesh(box(12, 9, 0.3), mat(c, { roughness: 0.95 }), g, [x, 4.5, -3.15]); mesh(box(12, 0.5, 0.36), mat('#ffffff'), g, [x, 0.25, -3.1]); });
  R.roomWin = mat('#bfe6ff', { emissive: '#bfe6ff', emissiveIntensity: 0.5 });
  const windowAt = (x, y) => { mesh(box(2.3, 2.3, 0.1), mat('#ffffff'), g, [x, y, -2.98]); mesh(box(2.0, 2.0, 0.12), R.roomWin, g, [x, y, -2.97]);
    mesh(box(0.08, 2.0, 0.14), mat('#ffffff'), g, [x, y, -2.96]); mesh(box(2.0, 0.08, 0.14), mat('#ffffff'), g, [x, y, -2.96]); };
  // kitchen
  windowAt(-1.5, 3.9);
  mesh(box(3.0, 0.14, 1.5), wood, g, [0, 1.12, 0.5]);
  for (const sx of [-1.3, 1.3]) for (const sz of [-0.15, 1.1]) mesh(box(0.14, 1.1, 0.14), wood, g, [sx, 0.55, sz]);
  mesh(box(1.7, 3.9, 1.3), mat('#a8dce0', { roughness: 0.4 }), g, [2.9, 1.95, -2.3]);
  mesh(box(0.08, 1.2, 0.08), metal('#e8edf2'), g, [2.3, 2.6, -1.62]);
  mesh(box(3.2, 1.3, 1.2), mat('#ffffff', { roughness: 0.6 }), g, [-3.2, 0.65, -2.4]); mesh(box(3.3, 0.12, 1.3), wood, g, [-3.2, 1.36, -2.4]);
  mesh(cyl(0.02, 0.02, 2.4, 6), mat('#22252c'), g, [0.3, 7.6, 0.4]);
  mesh(cyl(0.2, 0.6, 0.4, 24, true), mat('#3fae63', { side: THREE.DoubleSide }), g, [0.3, 6.3, 0.4]);
  R.bulb = mesh(sphere(0.16, 12), glow('#fff3c4', 1.4), g, [0.3, 6.2, 0.4]);
  // the bowl of beans and the tower of cans
  R.beans = group(g, [-0.25, 1.19, 0.6]); R.beans.scale.setScalar(0.78);
  mesh(new THREE.SphereGeometry(0.62, 28, 14, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), mat('#ffffff', { roughness: 0.4, side: THREE.DoubleSide }), R.beans, [0, 0.5, 0]);
  const br = rng(3), beanM = mat('#c8642a', { roughness: 0.5 });
  mesh(sphere(0.56, 20), mat('#b4531f'), R.beans, [0, 0.42, 0], [1, 0.42, 1]);
  for (let i = 0; i < 46; i++) { const a = br() * 6.28, d = Math.sqrt(br()) * 0.5; mesh(sphere(0.075, 8), beanM, R.beans, [Math.cos(a) * d, 0.56 + (0.5 - d) * 0.5 + br() * 0.05, Math.sin(a) * d], [1.4, 0.8, 1]); }
  R.cans = group(g, [1.0, 1.19, 0.45]);
  const label = canvasTex(256, 128, (c) => { c.fillStyle = '#e53935'; c.fillRect(0, 0, 256, 128); c.fillStyle = '#fff'; c.font = `900 54px ${FONT}`; c.textAlign = 'center'; c.fillText('BEANS', 64, 82); c.fillText('BEANS', 192, 82); });
  [[-0.2, 0], [0.2, 0], [0, 1], [0, 2], [0.02, 3], [-0.03, 4]].forEach(([x, k]) => { mesh(cyl(0.19, 0.19, 0.42, 24), metal('#d5dbe2'), R.cans, [x, 0.21 + k * 0.42, 0]); mesh(cyl(0.195, 0.195, 0.3, 24, true), mat('#fff', { map: label }), R.cans, [x, 0.21 + k * 0.42, 0]); });
  // hall door
  mesh(slab(1.9, 3.9, 0.12, 0.1), mat('#9a6a3a', { roughness: 0.6 }), g, [-6, 1.95, -2.95]);
  mesh(sphere(0.09, 12), metal('#f5c542'), g, [-5.3, 1.9, -2.85]);
  mesh(box(1.9, 0.06, 1.1), mat('#7fb8a8', { roughness: 1 }), g, [-6, 0.03, -1.9]);
  // bedroom
  windowAt(-10.2, 3.9);
  mesh(box(3.6, 0.5, 2.1), mat('#ffffff'), g, [-13.2, 0.75, -1.7]); mesh(box(3.7, 0.5, 2.2), wood, g, [-13.2, 0.25, -1.7]);
  mesh(box(2.5, 0.2, 2.16), mat('#6a8fe0', { roughness: 0.95 }), g, [-12.7, 1.08, -1.7]);
  mesh(sphere(0.45, 16), mat('#fff8e8'), g, [-14.5, 1.15, -1.7], [0.9, 0.4, 1.4]);
  mesh(box(0.2, 1.9, 2.3), wood, g, [-15.05, 0.95, -1.7]);
  mesh(box(0.9, 1.0, 0.8), wood, g, [-10.6, 0.5, -2.4]);
  mesh(cyl(0.9, 0.9, 0.04, 32), mat('#f2b8c6', { roughness: 1 }), g, [-11.6, 0.02, 0.4]).castShadow = false;
  // living room
  const sofa = mat('#4fa3a5', { roughness: 0.9 });
  mesh(box(3.8, 0.7, 1.5), sofa, g, [12, 0.45, -1.4]); mesh(box(3.8, 1.5, 0.5), sofa, g, [12, 1.3, -2.1]);
  for (const sx of [-2.05, 2.05]) mesh(box(0.5, 1.2, 1.5), sofa, g, [12 + sx, 0.7, -1.4]);
  mesh(slab(1.8, 1.3, 0.08, 0.08), mat('#fff'), g, [12.2, 4.6, -2.97]);
  mesh(cyl(1.6, 1.6, 0.04, 32), mat('#f4c97a', { roughness: 1 }), g, [12, 0.02, 0.6]).castShadow = false;
  return g;
}

function buildGarage() {
  const g = group(scene), wood = mat('#8a6a48', { roughness: 0.8 });
  mesh(box(30, 0.2, 14), mat('#7b828c', { roughness: 0.9 }), g, [0, -0.1, 2]).castShadow = false;
  mesh(box(30, 9, 0.3), mat('#4a5568', { roughness: 0.95 }), g, [0, 4.5, -3.15]);
  mesh(box(4.0, 0.16, 1.4), wood, g, [0, 1.25, 0.3]);
  for (const sx of [-1.8, 1.8]) for (const sz of [-0.3, 0.9]) mesh(box(0.16, 1.2, 0.16), wood, g, [sx, 0.6, sz]);
  mesh(slab(4.4, 2.2, 0.1, 0.1), mat('#c9a878', { roughness: 0.9 }), g, [0, 4.4, -2.95]);
  [[-1.6, 4.6, 0.12, 1.2, '#e53935'], [-1.0, 4.5, 0.5, 0.14, '#aeb6c0'], [0, 4.6, 0.14, 1.0, '#f2b705'], [0.9, 4.4, 0.6, 0.6, '#1e88e5'], [1.7, 4.6, 0.12, 1.3, '#aeb6c0']]
    .forEach(([x, y, w, h, c]) => mesh(box(w, h, 0.08), mat(c), g, [x, y, -2.86]));
  mesh(box(0.5, 0.3, 0.4), mat('#e5533d'), g, [-1.4, 1.48, 0.3]); mesh(cyl(0.12, 0.12, 0.3, 12), metal('#d5dbe2'), g, [1.3, 1.48, 0.1]);
  // the finished Silent Pants on a stand
  R.stand = group(g, [6, 0, 0.4]);
  mesh(cyl(0.5, 0.6, 0.12, 24), mat('#3d4654'), R.stand, [0, 0.06, 0]); mesh(cyl(0.05, 0.05, 1.3, 10), mat('#3d4654'), R.stand, [0, 0.7, 0]);
  R.pants = group(R.stand, [0, 1.25, 0]);
  mesh(cyl(0.34, 0.32, 0.4, 32), R.silver, R.pants, [0, 1.0, 0], [1, 1, 0.84]); mesh(sphere(0.32), R.silver, R.pants, [0, 0.8, 0], [1, 0.42, 0.84]);
  for (const sx of [-1, 1]) {
    mesh(capsule(0.13, 0.55), R.silver, R.pants, [sx * 0.18, 0.4, 0]);
    const f = group(R.pants, [sx * 0.27, 0.98, 0.2]); f.rotation.y = sx * 0.95;
    mesh(cyl(0.13, 0.13, 0.06, 24), mat('#39424e'), f).rotation.x = Math.PI / 2; mesh(new THREE.TorusGeometry(0.13, 0.02, 8, 24), metal('#e8edf2'), f, [0, 0, 0.035]);
  }
  mesh(new THREE.TorusGeometry(0.34, 0.04, 8, 32), mat('#39424e'), R.pants, [0, 1.18, 0], [1, 0.84, 1]).rotation.x = Math.PI / 2;
  mesh(sphere(0.05, 12), glow('#35e05a', 1.4), R.pants, [0, 1.18, 0.33]);
  return g;
}

function buildVault() {
  const g = group(scene), stone = mat('#27404a', { roughness: 0.95 });
  mesh(box(40, 0.2, 30), mat('#1d2f38', { roughness: 0.9 }), g, [0, -0.1, 0]).castShadow = false;
  mesh(box(40, 22, 0.4), stone, g, [0, 11, -7]);
  for (const sx of [-1, 1]) mesh(box(0.4, 22, 30), stone, g, [sx * 7.5, 11, 0]);
  R.nose = makeBigNose(); R.nose.g.position.set(0, 0, -4.2); g.add(R.nose.g);
  R.button = makeButton(); R.button.g.position.set(0, 0, 2.4); g.add(R.button.g);
  return g;
}

// ---------- light ----------
const MOODS = {
  day: { sky: [[0, '#4fb2fb'], [0.6, '#a9dfff'], [1, '#e4f7ff']], hemi: [0.95, '#eaf6ff', '#9aa58c'], sun: [1.55, '#fff4e0'], win: 0, fog: '#d7f0ff' },
  dawn: { sky: [[0, '#7fb6f2'], [0.55, '#ffd9c0'], [1, '#fff0d8']], hemi: [0.9, '#ffeede', '#a89a8c'], sun: [1.4, '#ffe0bf'], win: 0.15, fog: '#ffe9d6' },
  night: { sky: [[0, '#070b24'], [0.6, '#1b2760'], [1, '#33407e']], hemi: [0.5, '#93a8ff', '#262c4a'], sun: [0.55, '#a9bcff'], win: 1, fog: '#1b2550' },
  room: { bg: '#ffe7b0', hemi: [0.95, '#fff6e8', '#b79c7c'], sun: [1.15, '#fff1d6'], win: 0 },
  roomNight: { bg: '#3a2f2a', hemi: [0.5, '#ffd9a8', '#3a2f2a'], sun: [0.45, '#ffc98a'], win: 0 },
  garage: { bg: '#1d2430', hemi: [0.4, '#9db4ff', '#20263f'], sun: [0.35, '#a9bcff'], win: 0 },
  vault: { bg: '#0f1b22', hemi: [0.5, '#8fd8cf', '#122028'], sun: [0.7, '#ffd9a0'], win: 0 },
};
function setMood(name, fx = 0, fz = 0) {
  const m = MOODS[name];
  R.skyTex = R.skyTex || {};
  scene.background = m.sky ? (R.skyTex[name] = R.skyTex[name] || gradientTex(m.sky)) : new THREE.Color(m.bg);
  scene.fog = m.fog ? new THREE.Fog(m.fog, 70, 260) : null;
  R.hemi.intensity = m.hemi[0]; R.hemi.color.set(m.hemi[1]); R.hemi.groundColor.set(m.hemi[2]);
  R.sunLight.intensity = m.sun[0]; R.sunLight.color.set(m.sun[1]);
  R.sunLight.position.set(fx - 8, 20, fz + 14); R.sunLight.target.position.set(fx, 0, fz);
  R.fill.intensity = name === 'day' || name === 'dawn' || name === 'room' ? 0.3 : 0.12;
  R.winMat.emissiveIntensity = m.win; R.winMat.color.set(m.win > 0.5 ? '#ffe2a0' : '#bfe6ff');
  const night = name === 'night';
  R.stars.visible = night; R.sun.material.color.set(night ? '#f4f1e0' : '#ffe27a'); R.sun.scale.setScalar(night ? 0.6 : 1);
  R.clouds.forEach((c) => { c.visible = !night; });
  Object.values(R.posts).forEach((p) => { p.bulb.material.emissiveIntensity = night ? 1.6 : 0.3; });
  R.roomWin.color.set(name === 'roomNight' ? '#1b2760' : '#bfe6ff'); R.roomWin.emissive.set(name === 'roomNight' ? '#1b2760' : '#bfe6ff');
  R.bulb.material.emissiveIntensity = name === 'roomNight' ? 1.8 : 0.2;
}

// ---------- effects ----------
function buildFx() {
  const soft = (m) => { m.castShadow = false; m.receiveShadow = false; return m; };
  R.puffs = Array.from({ length: 110 }, () => {
    const g = group(scene), m = new THREE.MeshStandardMaterial({ color: '#8fe35e', emissive: '#4aa82e', emissiveIntensity: 0.4, transparent: true, roughness: 1, depthWrite: false });
    [[0, 0, 0, 0.3], [0.26, 0.1, 0.02, 0.22], [-0.24, 0.08, 0, 0.2], [0.05, 0.24, 0, 0.2], [-0.08, -0.17, 0.05, 0.17], [0.2, -0.12, 0, 0.15]].forEach(([x, y, z, r]) => soft(mesh(sphere(r, 14), m, g, [x, y, z])));
    return { g, m };
  });
  R.sparks = Array.from({ length: 26 }, () => soft(mesh(sphere(0.045, 6), glow('#ffd23b', 2.2), scene)));
  const cols = ['#ff5a5f', '#ffd23b', '#35c45a', '#1e88e5', '#c06cf0', '#ff8a3c'];
  R.confetti = Array.from({ length: 80 }, (_, i) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.1), new THREE.MeshBasicMaterial({ color: cols[i % 6], side: THREE.DoubleSide })); scene.add(m); return m; });
  R.birds = Array.from({ length: 12 }, () => { const g = group(scene); g.userData.w = [-1, 1].map((sx) => { const w = group(g); soft(mesh(box(0.5, 0.04, 0.2), mat('#3a4250'), w, [sx * 0.25, 0, 0])); return w; }); return g; });
  R.bills = Array.from({ length: 12 }, () => bill(scene));
  R.fx = [...R.puffs.map((p) => p.g), ...R.sparks, ...R.confetti, ...R.birds, ...R.bills];
  R.lamp = new THREE.PointLight('#ffd9a0', 0, 22, 1.4); scene.add(R.lamp);
  R.lamp2 = new THREE.PointLight('#8fc8ff', 0, 18, 1.4); scene.add(R.lamp2);
}
// A puff of green gas let out at `at`: it swells, drifts along o.dir and fades. o.size 1 is about 0.7 wide.
function puff(u, at, x, y, z, o = {}) {
  const a = u - at, life = o.life || 1.5;
  if (a < 0 || a > life || R.puffN >= R.puffs.length) return;
  const p = R.puffs[R.puffN++], k = a / life, d = o.dir || [-0.55, 0.5, -0.1];
  p.g.visible = true;
  p.g.position.set(x + d[0] * a, y + d[1] * a + 0.06 * Math.sin(a * 6), z + d[2] * a);
  p.g.scale.setScalar((o.size || 1) * (0.2 + 1.15 * easeOut(k * 2.4)));
  p.g.rotation.z = a * 0.9;
  p.m.opacity = 0.92 * (1 - easeIn(k));
}
const light = (l, x, y, z, k, color) => { l.position.set(x, y, z); l.intensity = k; if (color) l.color.set(color); };
function sparks(t, x, y, z, on = 1) {
  R.sparks.forEach((s, i) => {
    const a = ((t * 2.2 + i * 0.37) % 1), ang = i * 2.4, sp = 1.2 + (i % 5) * 0.35;
    s.visible = on > 0 && (i % 3 !== Math.floor(t * 7) % 3);
    s.position.set(x + Math.cos(ang) * sp * a, y + sp * 1.5 * a - 2.6 * a * a, z + Math.sin(ang) * sp * a * 0.6 + 0.2);
    s.scale.setScalar(1.2 - a);
  });
}
function confetti(t, x, z, on) {
  R.confetti.forEach((c, i) => {
    const r = rng(i + 1), px = x + (r() - 0.5) * 5, pz = z + (r() - 0.5) * 3 + 0.5, sp = 1.3 + r() * 1.2, ph = r() * 9;
    c.visible = on;
    c.position.set(px + Math.sin(t * 2 + ph) * 0.3, 7.5 - ((t * sp + ph) % 8), pz);
    c.rotation.set(t * 4 + ph, t * 3 + ph, ph);
  });
}
