"""The Fart Tax soundtrack: sneaky plucked music, toots, cash sounds, the voices, mixed: out/mix.wav.

Everything is synthesised here (as in cartoon-3d's sound.py), so there is nothing to license.
The music dips under the narration and stops for one beat before the last line.
"""
import json, os, subprocess, wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
SR = 44100
T = json.load(open(os.path.join(OUT, 'timeline.json')))
N = int((T['total'] + 0.3) * SR)
SC = {s['id']: s for s in T['shots']}
rng = np.random.default_rng(11)


def hz(note):
    names = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
    n, octave = note[:-1], int(note[-1])
    return 440 * 2 ** ((names[n[0]] + (1 if '#' in n else 0) + 12 * (octave - 4) - 9) / 12)


def env(n, attack=0.005, decay=0.25):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-t / decay)


def pluck(f, dur, decay=0.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(4 * np.pi * f * t) + 0.2 * np.sin(6 * np.pi * f * t)) * env(n, 0.003, decay)


def bell(f, dur, decay=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.15)) * env(n, 0.002, decay)


def tone(f0, f1, dur, shape='sine', decay=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(np.linspace(f0, f1, n)) / SR
    w = np.sin(ph) if shape == 'sine' else np.tanh(4 * np.sin(ph))
    return w * np.minimum(1, t / 0.01) * (np.exp(-t / decay) if decay else np.minimum(1, (dur - t) / 0.03))


def noise(dur, smooth=40):
    n = int(dur * SR)
    return np.convolve(rng.standard_normal(n), np.ones(smooth) / smooth, mode='same') * np.sqrt(smooth)


def add(track, sound, at, gain=1.0):
    i = int(at * SR)
    if i >= len(track) or i < 0:
        return
    j = min(len(track), i + len(sound))
    track[i:j] += sound[:j - i] * gain


fx = np.zeros(N)


def toot(at, dur=None, pitch=None, gain=0.5, muffled=False):
    """A comic toot: a buzzy low note that wobbles, flutters and slides down."""
    dur = dur or rng.uniform(0.28, 0.5)
    pitch = pitch or rng.uniform(0.85, 1.35)
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 96 * pitch * np.linspace(1.18, 0.78, n) * (1 + 0.12 * np.sin(2 * np.pi * rng.uniform(5, 9) * t))
    saw = 2 * ((np.cumsum(f) / SR) % 1) - 1
    flutter = 0.55 + 0.45 * (np.sin(2 * np.pi * rng.uniform(22, 34) * t + rng.uniform(0, 6)) > -0.2)
    x = np.tanh(5 * saw) * flutter * np.minimum(1, t / 0.012) * np.minimum(1, (dur - t) / 0.06)
    x = np.convolve(x, np.ones(90 if muffled else 26) / (90 if muffled else 26), mode='same')
    add(fx, x, at, gain * (0.5 if muffled else 1))


def cash(at, gain=0.2):
    """Money leaving: a thump and a little register ring."""
    add(fx, tone(150, 45, 0.22, decay=0.07), at, 0.7)
    for j, n in enumerate(['E6', 'B6']):
        add(fx, bell(hz(n), 0.5, 0.18), at + 0.02 + j * 0.07, gain)


def ding(at, notes=('C6', 'E6', 'G6'), gain=0.16):
    for j, n in enumerate(notes):
        add(fx, bell(hz(n), 0.9, 0.4), at + j * 0.07, gain)


def alarm(at, k=3):
    for j in range(k):
        add(fx, tone(880 if j % 2 == 0 else 660, 880 if j % 2 == 0 else 660, 0.11, 'soft'), at + j * 0.14, 0.13)


def whoosh(at):
    n = int(0.45 * SR)
    add(fx, noise(0.45, 60)[:n] * np.sin(np.linspace(0, np.pi, n)) ** 2, at - 0.22, 0.05)


def hum(a, b, f=110, gain=0.07, trem=9):
    n = int((b - a) * SR)
    t = np.arange(n) / SR
    saw = 2 * ((f * t) % 1) - 1
    x = np.convolve(saw, np.ones(60) / 60, mode='same') * (0.75 + 0.25 * np.sin(2 * np.pi * trem * t))
    add(fx, x * np.minimum(1, t / 0.25) * np.minimum(1, (b - a - t) / 0.25), a, gain)


C = lambda sid, name: SC[sid]['cues'][name]
ST = lambda sid: SC[sid]['start']
LINE = lambda key: T['lines'][key]

for s in T['shots'][1:]:
    whoosh(s['start'])
for sid, extra in (('s01', 0.3), ('s05', 0.3), ('s06', 0.3), ('s07', 0.3), ('s10', 0.25), ('s03', 0.45)):
    for k, v in SC[sid]['cues'].items():
        if k[0] == 'f':
            toot(v, gain=0.55)
            cash(v + extra)
alarm(C('s02', 'alarm'))
alarm(C('s03', 'f1') + 0.25, 4)
n_ = int(1.2 * SR)   # Toby's stomach
add(fx, noise(1.2, 500)[:n_] * (0.6 + 0.4 * np.sin(np.linspace(0, 40, n_))) * np.sin(np.linspace(0, np.pi, n_)), C('s04', 'rumble'), 0.35)
toot(C('s09', 'puff'), 0.5, 0.9, muffled=True)
t0, t1 = ST('s11') + 0.1, C('s11', 'reveal') - 0.1   # welding
while t0 < t1:
    k = int(0.05 * SR)
    add(fx, rng.standard_normal(k) * env(k, 0.001, 0.012), t0, 0.1)
    t0 += rng.uniform(0.03, 0.09)
for j, n in enumerate(['C5', 'E5', 'G5', 'C6', 'E6', 'G6', 'C7']):
    add(fx, bell(hz(n), 1.0, 0.45), C('s11', 'reveal') + j * 0.06, 0.13)
add(fx, noise(0.25, 30)[:int(0.25 * SR)] * env(int(0.25 * SR), 0.05, 0.08), C('s12', 'puff'), 0.06)   # a tiny "pfft" that the fan swallows
ding(LINE('s12_03')['start'] + 0.1)
add(fx, tone(900, 180, 1.2), C('s13', 'chart'), 0.13)   # the income sliding down
hum(ST('s14') + 0.2, ST('s14') + SC['s14']['dur'], 118, 0.08, 23)
add(fx, tone(140, 40, 0.3, decay=0.1), LINE('s14_02')['start'] + 3.142, 0.9)
for j in range(14):   # running feet
    add(fx, tone(240, 120, 0.05, decay=0.03), ST('s15') + 0.15 + j * 0.13, 0.22)
for j in range(16):
    add(fx, tone(300, 150, 0.05, decay=0.03), C('s15', 'run') + j * 0.115, 0.25)
add(fx, tone(180, 620, C('s16', 'float') - ST('s16') - 0.2, 'soft'), ST('s16') + 0.2, 0.06)   # Mr. Puff filling up
add(fx, tone(500, 1500, 1.6), C('s16', 'float'), 0.1)
add(fx, noise(SC['s17']['dur'], 8), ST('s17'), 0.012)   # the TV
toot(C('s18', 'puff'), 0.6, 0.8, 0.6)
ding(C('s18', 'zero'))
hum(ST('s19'), ST('s19') + SC['s19']['dur'], 70, 0.09, 14)
hum(ST('s20'), ST('s22') + C('s22', 'press') - ST('s22'), 55, 0.06, 3.2)   # the machine, until the button
for j in range(4):   # sniff, sniff
    k = int(0.3 * SR)
    add(fx, noise(0.3, 14)[:k] * np.sin(np.linspace(0, np.pi, k)) ** 2, C('s20', 'sniff') + j * 0.38, 0.1)
for j in range(8):   # the button's heartbeat
    add(fx, tone(70, 50, 0.16, decay=0.06), ST('s21') + 0.2 + j * 0.45, 0.5)
add(fx, tone(1800, 900, 0.04, decay=0.02), C('s22', 'press'), 0.4)
add(fx, tone(150, 50, 0.25, decay=0.09), C('s22', 'press'), 0.9)
add(fx, tone(420, 35, 1.0), C('s22', 'press') + 0.05, 0.18)
ding(C('s23', 'green'), ('C5', 'E5', 'G5', 'C6'), 0.2)
bm = C('s24', 'boom')   # a thousand trumpets: a fanfare played in toots, and a town's worth of them underneath
add(fx, noise(3.5, 400)[:int(3.5 * SR)] * env(int(3.5 * SR), 0.05, 1.2), bm, 0.3)
for j in range(46):
    toot(bm + rng.uniform(0, 3.4) ** 1.0 * (0.25 + 0.75 * rng.uniform()), gain=rng.uniform(0.12, 0.28))
for at, note, dur in ((0, 'G3', 0.22), (0.24, 'G3', 0.22), (0.48, 'C4', 0.3), (0.82, 'E4', 0.3), (1.16, 'G4', 0.7), (1.95, 'E4', 0.25), (2.22, 'G4', 1.0)):
    toot(bm + 0.25 + at, dur, hz(note) / 96, 0.42)
cheer = noise(SC['s25']['dur'] + 0.3, 6)
add(fx, cheer * np.sin(np.linspace(0, np.pi, len(cheer))) * (0.7 + 0.3 * np.sin(np.linspace(0, 60, len(cheer)))), ST('s25') - 0.1, 0.03)
ding(ST('s25') + 0.25, ('C5', 'E5', 'G5', 'C6', 'E6'), 0.15)
for j in range(2):   # the phone buzzing on Toby's hand
    add(fx, tone(165, 165, 0.26, 'soft'), C('s26', 'buzz') + j * 0.36, 0.1)
ding(C('s26', 'notif'), ('E6', 'C6'), 0.2)
add(fx, tone(120, 60, 0.5, decay=0.2), LINE('s27_02')['start'] + LINE('s27_02')['dur'] + 0.25, 0.6)   # the last thud


# ---- Music: 100 bpm, A minor, tiptoeing plucks ----
beat = 60 / 100
PROG = [('A2', ['A3', 'C4', 'E4']), ('A2', ['A3', 'C4', 'E4']), ('D3', ['A3', 'D4', 'F4']), ('E3', ['G#3', 'B3', 'E4'])]
TUNE = ['E5', None, 'C5', 'A4', None, 'B4', 'C5', None, 'D5', None, 'F5', 'D5', None, 'E5', 'B4', None]
music = np.zeros(N)
bar, k = 0.0, 0
while bar < T['total']:
    bass, chord = PROG[k % 4]
    for b in range(4):
        add(music, pluck(hz(bass) * (1.5 if b == 2 else 1), 0.5, 0.16), bar + b * beat, 0.5 if b % 2 == 0 else 0.3)
        add(music, sum(pluck(hz(n), 0.3, 0.07) for n in chord) / 3, bar + (b + 0.5) * beat, 0.3)
        note = TUNE[(k % 4) * 4 + b]
        if note and k % 8 >= 4:
            add(music, bell(hz(note), 0.5, 0.18), bar + b * beat, 0.12)
        hat = int(0.03 * SR)
        add(music, rng.standard_normal(hat) * env(hat, 0.001, 0.008), bar + (b + 0.5) * beat, 0.04)
    bar += 4 * beat
    k += 1
hush = C('s27', 'hush')
gate = np.ones(N)
gate[:int(0.3 * SR)] = np.linspace(0, 1, int(0.3 * SR))
i = int((hush - 0.25) * SR)
gate[i:int(hush * SR)] = np.linspace(1, 0, int(hush * SR) - i)
gate[int(hush * SR):] = 0
for a, b in ((bm, bm + 3.6),):   # the town drowns out the band
    gate[int(a * SR):int(b * SR)] *= 0.35
music *= gate


# ---- Voices ----
def decode(path):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float64) / 32768


def megaphone(x):
    """A loudspeaker: only the middle of the voice, pushed until it rasps."""
    spec = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    spec[(f < 550) | (f > 3200)] = 0
    y = np.tanh(np.fft.irfft(spec, len(x)) * 9)
    return y * 0.5 + 0.12 * np.roll(y, int(0.09 * SR))


voices, speaking = np.zeros(N), np.zeros(N)
for key, line in T['lines'].items():
    v = decode(os.path.join(OUT, 'voice', f'{key}.wav'))
    add(voices, megaphone(v) if line['who'] == 'drone' else v, line['start'])
    i, j = int((line['start'] - 0.15) * SR), int((line['start'] + line['dur'] + 0.2) * SR)
    speaking[max(0, i):min(N, j)] = 1
kk = int(0.25 * SR)
music *= 1 - 0.5 * np.convolve(speaking, np.ones(kk) / kk, mode='same')

mix = voices * 0.95 + music * 0.5 + fx * 0.85
mix /= max(1e-9, np.max(np.abs(mix))) / 0.89
with wave.open(os.path.join(OUT, 'mix.wav'), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('mix.wav', round(N / SR, 1), 's')
