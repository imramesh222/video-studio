"""Episode 4 soundtrack: original music, scene sounds, the voices, mixed: episode/out/mix.wav.

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
            add(fx, tone(f0, f0 * 1.35, 0.07, decay=0.05), t + j * 0.1, 0.06)
        t += rng.uniform(0.7, 1.4) / density


def water(a, b):
    t = a
    while t < b:
        f0 = rng.uniform(300, 700)
        add(fx, tone(f0, f0 * 1.8, 0.06, decay=0.04), t, 0.05)
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
            add(fx, tone(4200, 4300, 0.03, decay=0.02), t + j * 0.05, 0.03)
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
        add(fx, tone(f0, f0 * 1.5, 0.05, decay=0.03), d, 0.04)
        d += rng.uniform(0.25, 0.6)


def whoosh(a, b, gain=0.5):
    n = int((b - a) * SR)
    w = np.convolve(rng.standard_normal(n), np.ones(120) / 120, mode='same')
    add(fx, w * np.sin(np.linspace(0, np.pi, n)) ** 0.6 * 4, a, gain)


BIRDS = ('s01', 's02', 's03', 's04', 's05', 's13', 's14', 's15')
WATER = ('s07',)
NIGHT = ('s17', 's18', 's19', 's20', 's21', 's23', 's24')
for s in T['scenes']:
    a, b, c = s['start'], s['start'] + s['dur'], s['cues']
    n_ = int(0.6 * SR)
    add(fx, np.convolve(rng.standard_normal(n_), np.ones(40) / 40, mode='same') * np.sin(np.linspace(0, np.pi, n_)), a - 0.3, 0.22)
    sid = s['id']
    if 'horn' in c: horn(c['horn'])
    if 'pop' in c: pop(c['pop'])
    if 'answer' in c: sparkle(c['answer'])
    if 'found' in c: chime(c['found'])
    if 'jump' in c: boing(c['jump'])
    # The pair words: a bright pop for the first, a lower one for its opposite.
    for k, v in c.items():
        if k == 'a' or (k[0] == 'p' and k[-1] == 'a') or (k[0] == 'a' and k[1:].isdigit()): pop(v, 1.3, 0.4)
        if k == 'b' or (k[0] == 'p' and k[-1] == 'b') or (k[0] == 'b' and k[1:].isdigit()): pop(v, 0.8, 0.4)
    for j in (1, 2, 3):   # the balloon climbing and coming down
        if f'u{j}' in c: add(fx, tone(500 + j * 120, 700 + j * 160, 0.22, decay=0.12), c[f'u{j}'], 0.16)
        if f'd{j}' in c: add(fx, tone(900 - j * 130, 650 - j * 130, 0.22, decay=0.12), c[f'd{j}'], 0.16)
    if 'clap' in c:
        for j in range(6): clap(c['clap'] + j * 0.16)
    if 'land' in c: glissando(c['land'] - 1.2)
    if 'rainbow' in c: glissando(c['rainbow'])
    if 'thanks' in c: chime(c['thanks'])
    if 'open' in c: sparkle(c['open'] + 0.5)
    if 'give' in c: pop(c['give'] + 0.5, 1.5, 0.3)
    if sid == 's05' or sid == 's15':   # stretch up, squash down
        for k in ('a', 'u'):
            if k in c: add(fx, tone(300, 900, 0.3, decay=0.2), c[k], 0.14)
        for k in ('b', 'd'):
            if k in c: add(fx, tone(700, 220, 0.3, decay=0.2), c[k], 0.14)
    if sid == 's06': whoosh(c['a'], c['b'] + 0.2, 0.5)
    if sid == 's15':   # running feet on "Fast!"
        d = c['f']
        while d < c['s']:
            add(fx, tone(260, 140, 0.05, decay=0.03), d, 0.2); d += 0.09
    if sid == 's08':
        splash(c['a'])
        ripple(c['a'] + 0.8, c['b'] - 0.5)
        splash(c['b'] - 0.45, 0.45)
    if sid == 's09':
        splash(c['splash'] + 0.5, 0.5)
        ripple(a + 1.2, b)
        splash(c['found'] + 0.2, 0.6)
    if sid in BIRDS: birds(a, b, 1.2)
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
music *= 1 - 0.55 * speaking

mix = voices * 0.9 + music * 0.55 + fx
mix /= max(1e-9, np.max(np.abs(mix))) / 0.89
with wave.open(os.path.join(OUT, 'mix.wav'), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('mix.wav', round(N / SR, 1), 's')
