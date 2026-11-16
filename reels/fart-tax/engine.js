// Reel engine: the maths, mesh and texture helpers of cartoon-3d (episode.html), for a vertical 1080×1920 frame.
const W = 1080, H = 1920;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const ease = (x) => { x = clamp(x); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };
const easeOut = (x) => 1 - Math.pow(1 - clamp(x), 3);
const easeIn = (x) => Math.pow(clamp(x), 3);
const backOut = (x) => { x = clamp(x); const c1 = 2.2, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, k) => a + (b - a) * k;
const V = (x, y, z) => new THREE.Vector3(x, y, z);
function rng(seed) {
  return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}

THREE.ColorManagement.legacyMode = false;
let T, renderer, scene, cam, R = {}, SC = {};

const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.6, metalness: 0, ...o });
// Shiny metal (gold, silver, brass). It reflects the little studio made in setup(), so build it after setup().
const metal = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.3, metalness: 1, envMap: R.env, envMapIntensity: 1.25, ...o });
const glow = (color, k = 1) => mat(color, { emissive: color, emissiveIntensity: k, roughness: 0.4 });
function mesh(geo, material, parent, pos = [0, 0, 0], scale) {
  const m = new THREE.Mesh(geo, material);
  m.position.set(...pos);
  if (scale) m.scale.set(...scale);
  m.castShadow = true;
  m.receiveShadow = true;
  if (parent) parent.add(m);
  return m;
}
const sphere = (r, seg = 32) => new THREE.SphereGeometry(r, seg, Math.round(seg * 0.75));
const box = (w, h, d) => new THREE.BoxGeometry(w, h, d);
const cyl = (r0, r1, h, seg = 24, open = false) => new THREE.CylinderGeometry(r0, r1, h, seg, 1, open);
const capsule = (r, len) => new THREE.CapsuleGeometry(r, len, 8, 20);
const group = (parent, pos = [0, 0, 0]) => { const g = new THREE.Group(); g.position.set(...pos); if (parent) parent.add(g); return g; };
function roundedShape(w, h, r, cx = 0, cy = 0, path = new THREE.Shape()) {
  path.moveTo(cx - w / 2 + r, cy - h / 2);
  path.lineTo(cx + w / 2 - r, cy - h / 2); path.quadraticCurveTo(cx + w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + r);
  path.lineTo(cx + w / 2, cy + h / 2 - r); path.quadraticCurveTo(cx + w / 2, cy + h / 2, cx + w / 2 - r, cy + h / 2);
  path.lineTo(cx - w / 2 + r, cy + h / 2); path.quadraticCurveTo(cx - w / 2, cy + h / 2, cx - w / 2, cy + h / 2 - r);
  path.lineTo(cx - w / 2, cy - h / 2 + r); path.quadraticCurveTo(cx - w / 2, cy - h / 2, cx - w / 2 + r, cy - h / 2);
  return path;
}
// A box with rounded corners (walls, phones, signs), centred, facing +z.
function slab(w, h, d, r) {
  const geo = new THREE.ExtrudeGeometry(roundedShape(w, h, r), { depth: d, bevelEnabled: false, curveSegments: 8 });
  geo.translate(0, 0, -d / 2);
  return geo;
}
function canvasTex(w, h, draw) {
  const c = document.createElement('canvas');
  c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const tex = new THREE.CanvasTexture(c);
  tex.encoding = THREE.sRGBEncoding;
  tex.anisotropy = 8;
  return tex;
}
const decalMat = (map) => new THREE.MeshBasicMaterial({ map, transparent: true, polygonOffset: true, polygonOffsetFactor: -4 });
// A flat picture (sign, screen) that ignores the lights.
function picture(w, h, tex, parent, pos = [0, 0, 0]) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex }));
  m.position.set(...pos);
  if (parent) parent.add(m);
  return m;
}
// A round picture (a dial, a badge).
function disc(r, tex, parent, pos = [0, 0, 0]) {
  const m = new THREE.Mesh(new THREE.CircleGeometry(r, 48), new THREE.MeshBasicMaterial({ map: tex }));
  m.position.set(...pos);
  if (parent) parent.add(m);
  return m;
}
function gradientTex(stops) {
  return canvasTex(4, 512, (c) => {
    const g = c.createLinearGradient(0, 0, 0, 512);
    stops.forEach(([at, col]) => g.addColorStop(at, col));
    c.fillStyle = g; c.fillRect(0, 0, 4, 512);
  });
}

// What shiny things reflect: a bright sky, a warm floor and three soft lamps.
function makeEnv() {
  const s = new THREE.Scene();
  s.add(new THREE.Mesh(new THREE.SphereGeometry(50, 32, 16), new THREE.MeshBasicMaterial({ side: THREE.BackSide,
    map: gradientTex([[0, '#ffffff'], [0.45, '#bfe3ff'], [0.55, '#8a8f98'], [1, '#4a4038']]) })));
  [[0, 34, 6, 34], [30, 14, 22, 18], [-32, 12, -8, 16]].forEach(([x, y, z, size]) => {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshBasicMaterial({ color: '#ffffff', side: THREE.DoubleSide }));
    m.position.set(x, y, z); m.lookAt(0, 0, 0); s.add(m);
  });
  R.env = new THREE.PMREMGenerator(renderer).fromScene(s, 0.03).texture;
}

function setup() {
  renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('c'), antialias: true, preserveDrawingBuffer: true });
  renderer.setSize(W, H, false);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.toneMapping = THREE.NoToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  scene = new THREE.Scene();
  cam = new THREE.PerspectiveCamera(40, W / H, 0.1, 600);
  R.hemi = new THREE.HemisphereLight('#eaf6ff', '#9aa58c', 0.95);
  scene.add(R.hemi);
  const sun = new THREE.DirectionalLight('#fff4e0', 1.55);
  sun.castShadow = true;
  sun.shadow.mapSize.set(2048, 2048);
  Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 18, bottom: -8, near: 1, far: 90 });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -0.0004;
  sun.position.set(-8, 20, 14);
  scene.add(sun, sun.target);
  R.sunLight = sun;
  R.fill = new THREE.DirectionalLight('#cfe6ff', 0.3);
  R.fill.position.set(10, 6, 12);
  scene.add(R.fill);
  makeEnv();
}

// ---------- per-frame helpers ----------
// Camera: [x, y, z, lookX, lookY, lookZ, fov]. The frame is tall and narrow, so fov is the vertical angle.
function look(c) {
  cam.position.set(c[0], c[1], c[2]);
  cam.lookAt(c[3], c[4], c[5]);
  if (c[6] && cam.fov !== c[6]) { cam.fov = c[6]; cam.updateProjectionMatrix(); }
}
function camPath(u, keys) {
  if (u <= keys[0][0]) return keys[0].slice(1);
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i], b = keys[i + 1];
    if (u <= b[0]) { const k = ease((u - a[0]) / Math.max(0.001, b[0] - a[0])); return a.slice(1).map((v, j) => lerp(v, b[j + 1], k)); }
  }
  return keys[keys.length - 1].slice(1);
}
function blink(t, period, offset) {
  const k = ((t + offset) % period) / 0.16;
  return k < 1 ? Math.sin(k * Math.PI) : 0;
}
function hop(t, at, h = 0.5, d = 0.55) { const k = (t - at) / d; return k > 0 && k < 1 ? Math.sin(k * Math.PI) * h : 0; }
function bump(u, at, d = 0.5) { return Math.sin(Math.PI * clamp((u - at) / d)); }
// Where a 3D point lands in the picture, in pixels (for labels pinned over things). Call after look().
function toScreen(p) {
  cam.updateMatrixWorld();
  const v = p.clone().project(cam);
  return { x: (v.x + 1) / 2 * W, y: (1 - v.y) / 2 * H, front: v.z < 1 };
}
