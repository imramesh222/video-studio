"""Original music, sound effects and the final mix: kids/out/mix.wav.

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


# ---- Music: 112 bpm, C major, an original 8-bar tune that loops. ----
BPM = 112
beat = 60 / BPM
chords = [['C4', 'E4', 'G4'], ['A3', 'C4', 'E4'], ['F3', 'A3', 'C4'], ['G3', 'B3', 'D4']] * 2
bass = ['C3', 'A2', 'F2', 'G2'] * 2
tune = [  # (note or None, beats): two bars per line
    ('E5', 1), ('G5', 1), ('A5', 1), ('G5', 1), ('E5', 2), ('C5', 2),
    ('D5', 1), ('E5', 1), ('C5', 1), ('A4', 1), ('G4', 3), (None, 1),
    ('A4', 1), ('C5', 1), ('D5', 1), ('E5', 1), ('G5', 2), ('E5', 2),
    ('D5', 1), ('E5', 1), ('D5', 1), ('B4', 1), ('C5', 3), (None, 1),
]
music = np.zeros(N)
bar = 4 * beat
loop = 8 * bar
start = 0.0
while start < T['total']:
    for b, chord in enumerate(chords):
        t0 = start + b * bar
        # Strum pattern: down on 1, up-down on 2 and 3, down on 4.
        for k, off in enumerate([0, 1, 1.5, 2, 2.5, 3]):
            strum = sum(pluck(hz(n), 0.6, 0.22 if k else 0.35) for n in chord) / 3
            add(music, strum, t0 + off * beat + 0.012 * k, 0.16 if k else 0.22)
        add(music, pluck(hz(bass[b]), 1.2, 0.5), t0, 0.32)
        add(music, pluck(hz(bass[b]) * 1.5, 0.8, 0.35), t0 + 2 * beat, 0.2)
    t = start
    for note, beats in tune:
        if note:
            add(music, bell(hz(note), beats * beat + 0.4), t, 0.2)
        t += beats * beat
    # A soft shaker on the off-beats.
    for k in range(int(loop / (beat / 2))):
        n = int(0.05 * SR)
        add(music, np.random.default_rng(k).standard_normal(n) * env(n, 0.002, 0.015), start + k * beat / 2, 0.03)
    start += loop

# Fade the music in and out.
fade = np.ones(N)
fi, fo = int(0.8 * SR), int(2.0 * SR)
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


fx = np.zeros(N)
# The horn: two friendly beeps, a major third apart, layered.
for k in range(2):
    beep = tone(392, 392, 0.17, 'soft') * 0.6 + tone(494, 494, 0.17, 'soft') * 0.5
    add(fx, beep, T['cues']['horn'] + k * 0.24, 0.35)
# Pip pops up.
add(fx, tone(320, 980, 0.13, decay=0.08), T['cues']['pop'], 0.5)
# Birds in scene 1.
rng = np.random.default_rng(7)
s1 = T['scenes']['s1']
for k in range(9):
    at = s1['start'] + 0.4 + k * 0.85 + rng.uniform(0, 0.3)
    for j in range(rng.integers(2, 4)):
        f0 = rng.uniform(2600, 3400)
        add(fx, tone(f0, f0 * 1.35, 0.07, decay=0.05), at + j * 0.1, 0.07)
# Sparkles when RED appears, and on "beautiful red".
for cue in ('redWord', 'sparkle', 'answer'):
    for j, n in enumerate(['C6', 'E6', 'G6', 'C7', 'E7']):
        add(fx, bell(hz(n), 0.8, 0.35), T['cues'][cue] + j * 0.06, 0.12)
# A soft whoosh into each scene.
for name in ('s1', 's2', 's3'):
    n = int(0.6 * SR)
    noise = np.convolve(rng.standard_normal(n), np.ones(40) / 40, mode='same')
    add(fx, noise * np.sin(np.linspace(0, np.pi, n)), T['scenes'][name]['start'] - 0.3, 0.25)


# ---- Voices ----
def decode(path):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float64) / 32768


voices = np.zeros(N)
for key, line in T['lines'].items():
    add(voices, decode(os.path.join(OUT, 'voice', f'{key}.mp3')), line['start'], 1.0)

# Duck the music under speech, smoothly.
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
