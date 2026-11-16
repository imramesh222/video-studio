"""Episode 7 soundtrack: original music, scene sounds, the voices, mixed: episode/out/mix.wav.

Everything is synthesised here, so there is nothing to license. The music
dips under the voices so every word is clear.
"""
import json, os, subprocess, wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
SR = 44100
T = json.load(open(os.path.join(OUT, 'timeline.json')))
N = int((T['total'] + 0.5) * SR)


def hz(note):
    names = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    n, octave = note[:-1], int(note[-1])
    semis = names[n[0]] + (1 if '#' in n else 0)
    return 440 * 2 ** ((semis + 12 * (octave - 4) - 9) / 12)


def env(n, attack=0.005, decay=0.25):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)


def pluck(f, dur, decay=0.35):
    """A ukulele-ish pluck: a few soft harmonics that die away."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(4 * np.pi * f * t) + 0.18 * np.sin(6 * np.pi * f * t))
    return tone * env(n, 0.004, decay)


def bell(f, dur, decay=0.6):
    """Glockenspiel: bright, with an inharmonic shimmer."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.15)
    return tone * env(n, 0.002, decay)


def add(track, sound, at, gain=1.0):
    i = int(at * SR)
    if i >= len(track):
        return
    j = min(len(track), i + len(sound))
    track[i:j] += sound[:j - i] * gain



SC = {s['id']: s for s in T['scenes']}
CUE = lambda sid, name: SC[sid]['cues'].get(name)

# ---- Music: 112 bpm, C major. Two original 8-bar tunes, A A B A ... ----
BPM = 112
beat = 60 / BPM
bar = 4 * beat
CHORDS_A = [['C4', 'E4', 'G4'], ['A3', 'C4', 'E4'], ['F3', 'A3', 'C4'], ['G3', 'B3', 'D4']] * 2
BASS_A = ['C3', 'A2', 'F2', 'G2'] * 2
CHORDS_B = [['F3', 'A3', 'C4'], ['G3', 'B3', 'D4'], ['E3', 'G3', 'B3'], ['A3', 'C4', 'E4'],
            ['F3', 'A3', 'C4'], ['G3', 'B3', 'D4'], ['C4', 'E4', 'G4'], ['C4', 'E4', 'G4']]
BASS_B = ['F2', 'G2', 'E2', 'A2', 'F2', 'G2', 'C3', 'C3']
TUNE_A = [('E5', 1), ('G5', 1), ('A5', 1), ('G5', 1), ('E5', 2), ('C5', 2),
          ('D5', 1), ('E5', 1), ('C5', 1), ('A4', 1), ('G4', 3), (None, 1),
          ('A4', 1), ('C5', 1), ('D5', 1), ('E5', 1), ('G5', 2), ('E5', 2),
          ('D5', 1), ('E5', 1), ('D5', 1), ('B4', 1), ('C5', 3), (None, 1)]
TUNE_B = [('C5', 1), ('A4', 1), ('C5', 1), ('F5', 1), ('D5', 2), ('B4', 2),
          ('E5', 1), ('D5', 1), ('B4', 1), ('G4', 1), ('A4', 3), (None, 1),
          ('C5', 1), ('D5', 1), ('E5', 1), ('F5', 1), ('G5', 1), ('F5', 1), ('E5', 1), ('D5', 1),
          ('E5', 1), ('G5', 1), ('E5', 1), ('D5', 1), ('C5', 3), (None, 1)]
music = np.zeros(N)
rngm = np.random.default_rng(5)
start, k = 0.0, 0
while start < T['total']:
    part_b = k % 4 == 2
    chords, bass, tune = (CHORDS_B, BASS_B, TUNE_B) if part_b else (CHORDS_A, BASS_A, TUNE_A)
    for b, chord in enumerate(chords):
        t0 = start + b * bar
        for j, off in enumerate([0, 1, 1.5, 2, 2.5, 3]):
            strum = sum(pluck(hz(n), 0.6, 0.22 if j else 0.35) for n in chord) / 3
            add(music, strum, t0 + off * beat + 0.012 * j, 0.16 if j else 0.22)
        add(music, pluck(hz(bass[b]), 1.2, 0.5), t0, 0.32)
        add(music, pluck(hz(bass[b]) * 1.5, 0.8, 0.35), t0 + 2 * beat, 0.2)
    t = start
    for note, beats in tune:
        if note:
            add(music, bell(hz(note), beats * beat + 0.4), t, 0.2)
        t += beats * beat
    for j in range(64):
        n = int(0.05 * SR)
        add(music, rngm.standard_normal(n) * env(n, 0.002, 0.015), start + j * beat / 2, 0.03)
    start += 8 * bar
    k += 1
fade = np.ones(N)
fi, fo = int(0.8 * SR), int(3.0 * SR)
fade[:fi] = np.linspace(0, 1, fi)
fade[-fo:] = np.linspace(1, 0, fo)
music *= fade


# ---- Sound effects ----
def tone(f0, f1, dur, shape='sine', decay=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = np.linspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    w = np.sin(ph) if shape == 'sine' else np.tanh(3 * np.sin(ph))
    e = np.minimum(1, t / 0.01) * (np.exp(-t / decay) if decay else np.minimum(1, (dur - t) / 0.03))
    return w * e


rng = np.random.default_rng(7)
fx = np.zeros(N)
amb = np.zeros(N)   # background sounds (birds, water, wind, rain, crickets, thunder): they dip under the voices


def horn(at):
    for j in range(2):
        add(fx, tone(392, 392, 0.17, 'soft') * 0.6 + tone(494, 494, 0.17, 'soft') * 0.5, at + j * 0.24, 0.35)


def pop(at, pitch=1.0, gain=0.45):
    add(fx, tone(320 * pitch, 980 * pitch, 0.13, decay=0.08), at, gain)


def sparkle(at, gain=0.12):
    for j, n in enumerate(['C6', 'E6', 'G6', 'C7', 'E7']):
        add(fx, bell(hz(n), 0.8, 0.35), at + j * 0.06, gain)


def chime(at):
    for j, n in enumerate(['C5', 'E5', 'G5', 'C6']):
        add(fx, bell(hz(n), 1.2, 0.5), at + j * 0.09, 0.16)


def boing(at):
    add(fx, tone(180, 520, 0.25, decay=0.18), at, 0.3)


def clap(at, gain=0.22):
    n = int(0.06 * SR)
    burst = np.convolve(rng.standard_normal(n), [1, -0.6], mode='same') * env(n, 0.001, 0.02)
    add(fx, burst, at, gain)


def birds(a, b, density=1.0):
    t = a + 0.4
    while t < b:
        for j in range(rng.integers(2, 4)):
            f0 = rng.uniform(2600, 3600)
            add(amb, tone(f0, f0 * 1.35, 0.07, decay=0.05), t + j * 0.1, 0.06)
        t += rng.uniform(0.7, 1.4) / density


def water(a, b):
    t = a
    while t < b:
        f0 = rng.uniform(300, 700)
        add(amb, tone(f0, f0 * 1.8, 0.06, decay=0.04), t, 0.05)
        t += rng.uniform(0.15, 0.5)


def wind(a, b):
    n = int((b - a) * SR)
    w = np.convolve(rng.standard_normal(n), np.ones(400) / 400, mode='same')
    add(fx, w * np.sin(np.linspace(0, np.pi, n)) * 3, a, 0.5)


def glissando(at):
    for j, n in enumerate(['C5', 'D5', 'E5', 'G5', 'A5', 'C6', 'D6', 'E6', 'G6', 'C7']):
        add(fx, bell(hz(n), 0.9, 0.4), at + j * 0.07, 0.11)


def crickets(a, b):
    t = a + 0.3
    while t < b:
        for j in range(3):
            add(amb, tone(4200, 4300, 0.03, decay=0.02), t + j * 0.05, 0.03)
        t += rng.uniform(0.5, 1.1)


def rumble(at, dur):
    n = int(dur * SR)
    w = np.convolve(rng.standard_normal(n), np.ones(200) / 200, mode='same')
    add(fx, w * np.sin(np.linspace(0, np.pi, n)) * 4, at, 0.35)


def block(at):
    add(fx, tone(520, 380, 0.09, decay=0.05), at, 0.4)


def splash(at, size=1.0):
    """Something dropping into water: a low plop that falls in pitch, a hiss of spray that fades, then a few drips."""
    add(fx, tone(420, 80, 0.18, decay=0.06), at, 0.75 * size)
    n = int(0.9 * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(48) / 48, mode='same')          # keep the bright part of the noise
    x = np.convolve(x, np.ones(3) / 3, mode='same')
    grain = 0.55 + 0.45 * np.convolve(rng.random(n), np.ones(300) / 300, mode='same') * 2   # uneven, like droplets
    add(fx, x * grain * np.minimum(1, t / 0.015) * (0.7 * np.exp(-t / 0.09) + 0.3 * np.exp(-t / 0.35)), at + 0.02, 0.3 * size)
    low = np.convolve(rng.standard_normal(n), np.ones(220) / 220, mode='same') * 12                # the body of the water moving
    add(fx, low * np.minimum(1, t / 0.03) * np.exp(-t / 0.2), at + 0.02, 0.3 * size)
    d = at + 0.16
    for j in range(int(7 * size)):
        f0 = rng.uniform(700, 1900)
        add(fx, tone(f0, f0 * rng.uniform(1.25, 1.6), rng.uniform(0.035, 0.06), decay=0.025), d, 0.11 * size * (1 - j / 9))
        d += rng.uniform(0.05, 0.13)


def ripple(a, b):
    """Soft lapping while something floats in the pond."""
    d = a
    while d < b:
        f0 = rng.uniform(500, 1100)
        add(amb, tone(f0, f0 * 1.5, 0.05, decay=0.03), d, 0.04)
        d += rng.uniform(0.25, 0.6)


def whoosh(a, b, gain=0.5):
    n = int((b - a) * SR)
    w = np.convolve(rng.standard_normal(n), np.ones(120) / 120, mode='same')
    add(fx, w * np.sin(np.linspace(0, np.pi, n)) ** 0.6 * 4, a, gain)


def fwip(at, gain=0.22):
    """A banana peel pulled down: a short rising swish."""
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(20) / 20, mode='same')
    add(fx, x * np.sin(np.pi * t / 0.22) ** 2 * (0.4 + 0.6 * t / 0.22), at, gain)


def crunch(at, gain=0.3, bites=3):
    """A bite of fruit: a few short crispy bursts."""
    for j in range(bites):
        n = int(0.07 * SR)
        x = rng.standard_normal(n)
        x = x - np.convolve(x, np.ones(8) / 8, mode='same')
        add(fx, x * env(n, 0.002, 0.025), at + j * 0.11 + rng.uniform(0, 0.02), gain * (1 - j * 0.2))


def thunk(at, gain=0.6):
    """Something round landing in a basket."""
    add(fx, tone(210, 90, 0.16, decay=0.06), at, gain)
    n = int(0.08 * SR)
    add(fx, np.convolve(rng.standard_normal(n), np.ones(30) / 30, mode='same') * env(n, 0.002, 0.03) * 4, at, 0.25)


def rain(a, b, level, muffled=False):
    """Rain from a to b: a soft hiss and scattered drips; level(x) gives the strength (0-1) x seconds in."""
    n = int((b - a) * SR)
    t = np.arange(n) / SR
    k = np.array([level(x) for x in t[::441]]).repeat(441)[:n]
    x = rng.standard_normal(n)
    x = np.convolve(x - np.convolve(x, np.ones(6) / 6, mode='same'), np.ones(30 if muffled else 3) / (30 if muffled else 3), mode='same')
    add(amb, x * k * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t) ** 2), a, 0.16 if muffled else 0.1)
    d = a
    while d < b:
        if rng.random() < level(d - a):
            f0 = rng.uniform(1600, 3800)
            add(amb, tone(f0, f0 * 0.7, 0.03, decay=0.012), d, 0.05 * (0.5 if muffled else 1))
        d += rng.uniform(0.02, 0.07)


def thunder(at, gain=0.5):
    """A soft, far-away rumble: low and rolling, no crack."""
    n = int(3.2 * SR)
    t = np.arange(n) / SR
    low = np.convolve(rng.standard_normal(n), np.ones(700) / 700, mode='same') * 26
    swell = np.minimum(1, t / 0.35) * np.exp(-t / 1.2) * (0.75 + 0.25 * np.sin(2 * np.pi * 1.7 * t)) + 0.5 * np.exp(-((t - 1.1) / 0.35) ** 2)
    add(amb, (low + 0.35 * np.sin(2 * np.pi * 42 * t)) * swell, at, gain)


def wind(a, b, strength=1.0):
    """Wind from a to b: a breathy band of noise that rises and falls."""
    n = int((b - a) * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    band = np.convolve(x, np.ones(25) / 25, mode='same') - np.convolve(x, np.ones(300) / 300, mode='same')
    lfo = 0.45 + 0.55 * np.sin(2 * np.pi * 0.28 * t + 1) ** 2
    add(amb, band * 9 * lfo * np.minimum(1, t / 0.8) * np.minimum(1, (b - a - t) / 0.8), a, 0.04 * strength)


def sniff(at, gain=0.12):
    """A little sniff: a short breathy rise."""
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = x - np.convolve(x, np.ones(12) / 12, mode='same')
    add(fx, x * np.sin(np.pi * t / 0.22) ** 2 * (0.3 + 0.7 * t / 0.22), at, gain)


def stomp(at, gain=0.5):
    add(fx, tone(110, 55, 0.18, decay=0.07), at, gain)
    n = int(0.05 * SR)
    add(fx, np.convolve(rng.standard_normal(n), np.ones(40) / 40, mode='same') * env(n, 0.002, 0.02) * 5, at, 0.2)


def tweet(at, gain=0.09):
    for j in range(3):
        f0 = 3000 + j * 250
        add(fx, tone(f0, f0 * 1.3, 0.08, decay=0.05), at + j * 0.12, gain)


BIRDS = ('s01', 's02', 's03', 's04', 's05', 's06', 's07', 's14', 's15', 's16')
WATER = ('s08', 's09')
NIGHT = ('s18', 's19', 's20', 's21', 's23', 's24')
SC = {x['id']: x for x in T['scenes']}
for s in T['scenes']:
    a, b, c = s['start'], s['start'] + s['dur'], s['cues']
    n_ = int(0.6 * SR)
    add(fx, np.convolve(rng.standard_normal(n_), np.ones(40) / 40, mode='same') * np.sin(np.linspace(0, np.pi, n_)), a - 0.3, 0.22)
    sid = s['id']
    if 'horn' in c: horn(c['horn'])
    if 'pop' in c: pop(c['pop'])
    for k in ('e', 'se', 'bt', 'wg', 'arms', 'le', 'lm', 'beak'):   # a body part lights up
        if k in c: pop(c[k], 1.25, 0.35)
    if 'w' in c: pop(c['w'], 1.2, 0.35)
    if 'answer' in c: sparkle(c['answer'])
    if 'found' in c: chime(c['found'])
    if 'jump' in c: boing(c['jump'])
    for j in range(1, 7):
        if f'f{j}' in c: pop(c[f'f{j}'], 0.9 + j * 0.1, 0.35)
        if f'r{j}' in c: sparkle(c[f'r{j}'], 0.14)
    for j in (1, 2):
        if f'b{j}' in c: add(fx, bell(hz('E6'), 0.4, 0.15), c[f'b{j}'] + 0.15, 0.12)   # a blink: a little "tink"
        if f'n{j}' in c: sniff(c[f'n{j}'])
        if f't{j}' in c: stomp(c[f't{j}'] + 0.05, 0.4)
    for j in (1, 2, 3):
        if f'c{j}' in c: clap(c[f'c{j}'] + 0.05, 0.3)
        if f's{j}' in c: stomp(c[f's{j}'] + 0.05)
        if f'p{j}' in c: add(fx, tone(180, 120, 0.1, decay=0.04), c[f'p{j}'] + 0.05, 0.35)   # a soft pat
    if 'tweet' in c: tweet(c['tweet'] + 0.2); tweet(c['tweet'] + 0.75, 0.07)
    if 'jmp' in c: boing(c['jmp'])
    if 'wide' in c: sparkle(c['smile'])
    if 'rumble' in c:   # Birdie's hungry tummy: a soft, low gurgle
        n = int(1.0 * SR)
        add(fx, np.convolve(rng.standard_normal(n), np.ones(400) / 400, mode='same') * 14 * (0.6 + 0.4 * np.sin(np.linspace(0, 30, n))) * np.sin(np.linspace(0, np.pi, n)), c['rumble'], 0.4)
    if 'flap' in c or 'wg' in c:
        at = c.get('wg', c.get('flap'))
        for j in range(8): add(fx, tone(900, 600, 0.05, decay=0.03), at + j * 0.11, 0.07)
    if 'body' in c: glissando(c['body'])
    if 'clap' in c:
        for j in range(6): clap(c['clap'] + j * 0.16)
    if 'land' in c: glissando(c['land'] - 1.2)
    if 'rainbow' in c: glissando(c['rainbow'])
    if 'thanks' in c: chime(c['thanks'])
    if sid in BIRDS: birds(a, b, 1.0)
    if sid in WATER: water(a, b)
    if sid in NIGHT: crickets(a, b)


# ---- Voices ----
def decode(path):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float64) / 32768


voices = np.zeros(N)
for key, line in T['lines'].items():
    # A chorus is several voices at once: each a little quieter.
    # Loud and quiet lines (Froggy's RIBBIT, a whisper) carry their own loudness.
    add(voices, decode(os.path.join(OUT, 'voice', f'{key}.wav')), line['start'], (0.55 if line['chorus'] else 1.0) * line.get('gain', 1.0))

speaking = np.zeros(N)
for line in T['lines'].values():
    i, j = int((line['start'] - 0.15) * SR), int((line['start'] + line['dur'] + 0.2) * SR)
    speaking[max(0, i):min(N, j)] = 1
k = int(0.25 * SR)
speaking = np.convolve(speaking, np.ones(k) / k, mode='same')
music *= 1 - 0.75 * speaking   # music drops to a quarter while anyone speaks
amb *= 1 - 0.8 * speaking    # background sounds drop to a fifth

mix = voices * 0.9 + music * 0.42 + fx + amb
mix /= max(1e-9, np.max(np.abs(mix))) / 0.89

# Check, scene by scene, while someone is talking: background sounds at least 15 dB and music at least 10 dB under the voices.
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
quiet = []
for sc in T['scenes']:
    i, j = int(sc['start'] * SR), int((sc['start'] + sc['dur']) * SR)
    on = speaking[i:j] > 0.5
    if on.sum() < SR * 0.3: continue
    v = db((voices * 0.9)[i:j][on])
    for name, x, need in (('background', amb, 15), ('music', music * 0.42, 10)):
        gap = v - db(x[i:j][on])
        if gap < need: quiet.append(f"{sc['id']} {name} only {gap:.1f} dB under")
print('levels OK: background 15+ dB and music 10+ dB under the voices in every scene' if not quiet else 'TOO LOUD: ' + ', '.join(quiet))
with wave.open(os.path.join(OUT, 'mix.wav'), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('mix.wav', round(N / SR, 1), 's')
