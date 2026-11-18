"""English subtitles (.srt) for every Lumi Land episode, from each timeline: the exact words, at the exact times.
Lines said together (choruses) appear once. Saved next to each episode's MP4. Run: .venv/bin/python shorts/make_srt.py"""
import glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
LL = os.path.expanduser('~/Downloads/Lumi Land')
ts = lambda x: '%02d:%02d:%02d,%03d' % (x // 3600, x % 3600 // 60, x % 60, round(x % 1 * 1000) % 1000)
for folder in sorted(glob.glob(os.path.join(HERE, '..', 'cartoon-3d', 'episodes', 'ep*', 'out', 'timeline.json'))):
    n = int(re.search(r'ep(\d+)-', folder).group(1))
    T = json.load(open(folder))
    seen, cues = set(), []
    for l in sorted(T['lines'].values(), key=lambda l: l['start']):
        key = (round(l['start'], 2), l['text'])
        if key in seen: continue
        seen.add(key)
        cues.append([l['start'], l['start'] + max(l['dur'], 0.8), l['text']])
    for i in range(len(cues) - 1):   # never overlap the next line
        cues[i][1] = min(cues[i][1] + 0.3, cues[i + 1][0] - 0.02)
    out = glob.glob(os.path.join(LL, f'Episode {n:02d} - *'))[0]
    with open(os.path.join(out, f'lumi-land-ep{n}-english.srt'), 'w') as f:
        for i, (a, b, text) in enumerate(cues, 1):
            f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{text}\n\n')
    print(n, len(cues), 'subtitles')
