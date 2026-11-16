"""Mouth shapes for every line, from the voice's own word timings.

The same nine shapes as Rhubarb Lip Sync (A-H, X): letters become shapes,
spread over each word's time, and the mouth rests wherever the voice is
quiet. Writes kids3d/visemes.json: {line: [[time, shape], ...]}.
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
T = json.load(open(os.path.join(HERE, 'out', 'timeline.json')))

# A closed (m b p) · B teeth (s t d k n ee) · C open (eh) · D wide (ah)
# E round (aw er) · F pucker (oo w) · G f/v · H l · X rest
DIGRAPHS = [('th', 'B'), ('sh', 'B'), ('ch', 'B'), ('ee', 'B'), ('ea', 'B'), ('oo', 'F'), ('ou', 'F'),
            ('ow', 'F'), ('oa', 'F'), ('ue', 'F'), ('ew', 'F'), ('ar', 'D'), ('or', 'E'), ('er', 'E'),
            ('ur', 'E'), ('ir', 'E'), ('ph', 'G'), ('ck', 'B'), ('ng', 'B'), ('ai', 'C'), ('ay', 'C'),
            ('igh', 'C')]
LETTER = {**{c: 'A' for c in 'mbp'}, **{c: 'B' for c in 'stdkgnczxjyrq'}, 'f': 'G', 'v': 'G', 'l': 'H',
          'w': 'F', 'a': 'D', 'e': 'C', 'i': 'C', 'o': 'E', 'u': 'F', 'h': None}


def shapes(word):
    w = re.sub(r'[^a-z]', '', word.lower())
    if len(w) > 2 and w.endswith('e') and w[-2] not in 'aeiou':
        w = w[:-1]  # silent e
    out, i = [], 0
    while i < len(w):
        for dg, s in DIGRAPHS:
            if w.startswith(dg, i):
                out.append(s)
                i += len(dg)
                break
        else:
            s = LETTER.get(w[i], 'B')
            if s:
                out.append(s)
            i += 1
    # Two of the same in a row read as one longer shape.
    return [s for k, s in enumerate(out) if k == 0 or s != out[k - 1]] or ['C']


result = {}
for key, line in T['lines'].items():
    fps, env, dur = T['fps'], line['env'], line['dur']
    words = line['words']
    cues = []
    for k, (word, start) in enumerate(words):
        end = words[k + 1][1] if k + 1 < len(words) else dur
        # Each word's own time, minus the pause that may follow it.
        end = min(end, start + 0.12 + 0.085 * len(word))
        seq = shapes(word)
        step = (end - start) / len(seq)
        for j, s in enumerate(seq):
            cues.append([round(start + j * step, 3), s])
        cues.append([round(end, 3), 'X'])
    # Rest wherever it is quiet, however the words were split.
    frames = []
    for f in range(int(dur * fps) + 1):
        t = f / fps
        s = 'X'
        for c in cues:
            if c[0] <= t:
                s = c[1]
        loud = env[f] if f < len(env) else 0
        if loud < 0.05 and s != 'A':
            s = 'X'
        frames.append(s)
    # No shape shorter than two frames: it would flicker.
    for f in range(1, len(frames) - 1):
        if frames[f] != frames[f - 1] and frames[f] != frames[f + 1]:
            frames[f] = frames[f - 1]
    result[key] = ''.join(frames)
json.dump(result, open(os.path.join(HERE, 'out', 'visemes.json'), 'w'))
for k, v in result.items():
    pass
