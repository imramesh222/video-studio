"""Rainbow Rescue Bus sample: the voices, their timing and the scene timeline.

Writes kids/out/voice/*.mp3 and kids/out/timeline.json (scenes, lines, word
times and a loudness curve per line for the mouths).
"""
import asyncio, json, os, subprocess

import edge_tts
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(os.path.join(OUT, 'voice'), exist_ok=True)
FPS = 30
VOICES = {
    'pip': dict(voice='en-US-AnaNeural', rate='-6%', pitch='+0Hz'),
    'sunny': dict(voice='en-US-RogerNeural', rate='+0%', pitch='+12Hz'),
}
LINES = [
    ('s1a', 'pip', "Hello, friends! Are you ready for an adventure?"),
    ('s1b', 'sunny', "Beep beep! Let's go!"),
    ('s2a', 'pip', "Wow! Look at all those beautiful colors!"),
    ('s2b', 'sunny', "Let's learn colors together!"),
    ('s3a', 'pip', "Look, friends! Red!"),
    ('s3b', 'pip', "Can you say red?"),
    ('s3c', 'pip', "Red, red, beautiful red!"),
]


async def speak(key, who, text):
    v = VOICES[who]
    words, path = [], os.path.join(OUT, 'voice', f'{key}.mp3')
    com = edge_tts.Communicate(text, v['voice'], rate=v['rate'], pitch=v['pitch'], boundary='WordBoundary')
    with open(path, 'wb') as f:
        async for chunk in com.stream():
            if chunk['type'] == 'audio':
                f.write(chunk['data'])
            elif chunk['type'] == 'WordBoundary':
                words.append([chunk['text'], chunk['offset'] / 1e7])
    return path, words


def envelope(path):
    """Loudness per video frame, 0..1, for the mouth."""
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '24000', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    step = 24000 // FPS
    rms = [float(np.sqrt(np.mean(x[i:i + step] ** 2))) for i in range(0, len(x), step)]
    top = max(rms) or 1
    return [round(min(1, r / top * 1.4), 3) for r in rms], len(x) / 24000


async def main():
    lines = {}
    for key, who, text in LINES:
        path, words = await speak(key, who, text)
        env, dur = envelope(path)
        lines[key] = dict(who=who, text=text, dur=dur, words=words, env=env)

    # The timeline: each line starts after what comes before it.
    T = {}
    title = 3.0
    # Scene 1: the bus drives in (0-3.4), Pip pops out, says hello; horn; Sunny.
    s1 = dict(start=title)
    s1a = 3.9
    hornAt = s1a + lines['s1a']['dur'] + 0.35
    s1b = hornAt + 0.15
    s1['dur'] = s1b + lines['s1b']['dur'] + 1.4
    # Scene 2: driving along the rainbow road.
    s2 = dict(start=s1['start'] + s1['dur'])
    s2a = 1.2
    s2b = s2a + lines['s2a']['dur'] + 0.5
    s2['dur'] = max(8.0, s2b + lines['s2b']['dur'] + 1.4)
    # Scene 3: the red flowers, a pause for children to answer.
    s3 = dict(start=s2['start'] + s2['dur'])
    s3a = 1.4
    s3b = s3a + lines['s3a']['dur'] + 0.7
    pause = s3b + lines['s3b']['dur'] + 2.2   # children say "red"
    s3c = pause
    s3['dur'] = s3c + lines['s3c']['dur'] + 2.2

    starts = {'s1a': s1['start'] + s1a, 's1b': s1['start'] + s1b, 's2a': s2['start'] + s2a,
              's2b': s2['start'] + s2b, 's3a': s3['start'] + s3a, 's3b': s3['start'] + s3b,
              's3c': s3['start'] + s3c}
    for k, v in lines.items():
        v['start'] = round(starts[k], 3)
    red_word = next((w[1] for w in lines['s3a']['words'] if w[0].lower().startswith('red')), lines['s3a']['dur'] - 0.5)
    timeline = dict(
        fps=FPS, title=title, total=round(s3['start'] + s3['dur'], 3),
        scenes=dict(s1=s1, s2=s2, s3=s3), lines=lines,
        cues=dict(horn=round(s1['start'] + hornAt, 3), redWord=round(starts['s3a'] + red_word, 3),
                  ask=round(starts['s3b'], 3), answer=round(starts['s3b'] + lines['s3b']['dur'] + 0.3, 3),
                  sparkle=round(starts['s3c'], 3), pop=round(s1['start'] + 3.5, 3)),
    )
    json.dump(timeline, open(os.path.join(OUT, 'timeline.json'), 'w'))
    print('total', timeline['total'], 's;', {k: (v['start'], round(v['dur'], 2)) for k, v in lines.items()})
    print('words s3a', lines['s3a']['words'])

asyncio.run(main())
