"""Rainbow Rescue Bus, episode 2 (The Shape Hunt): voices, word timings and the timeline.

Each scene is a list of beats; the timeline follows the voices, so no line is
ever rushed. Writes episode/out/voice/*.mp3 and episode/out/timeline.json.
"""
import asyncio, json, os, re, subprocess, sys

import edge_tts
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(os.path.join(OUT, 'voice'), exist_ok=True)
FPS = 30
VOICES = {
    'pip': dict(voice='en-US-AnaNeural', rate='-6%', pitch='+0Hz'),
    'sunny': dict(voice='en-US-RogerNeural', rate='+0%', pitch='+12Hz'),
    'kitty': dict(voice='en-GB-MaisieNeural', rate='-4%', pitch='+25Hz'),
    'ducky': dict(voice='en-NZ-MollyNeural', rate='+6%', pitch='+45Hz'),
    'froggy': dict(voice='en-NZ-MitchellNeural', rate='+4%', pitch='+35Hz'),
    'birdie': dict(voice='en-CA-ClaraNeural', rate='+10%', pitch='+70Hz'),
    'lumi': dict(voice='en-GB-LibbyNeural', rate='-6%', pitch='+22Hz'),
}
FRIENDS = ['kitty', 'ducky', 'froggy', 'birdie']

# Beats: ('say', who, text) · ('all', [who...], text) · ('wait', s) · ('cue', name)
# ('cue', name) marks "now"; ('word', name, word) marks a word in the last line.
ALL = ['pip'] + FRIENDS + ['lumi']
SCENES = [
    ('s01', 'A new adventure', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we are going on a shape hunt!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Let's find shapes!"),
        ('wait', 1.4)]),
    ('s02', 'The shape song', 1.2, [
        ('say', 'pip', "Circle, square, triangle, star!"),
        ('word', 'w1', 'circle'), ('word', 'w2', 'square'), ('word', 'w3', 'triangle'), ('word', 'w4', 'star'),
        ('wait', 0.5),
        ('say', 'sunny', "Let's find them near and far!"),
        ('wait', 1.4)]),
    ('s03', 'The circle sun', 1.2, [
        ('say', 'pip', "Look! The sun is round. It's a circle!"), ('word', 'shape', 'circle'),
        ('wait', 0.6),
        ('say', 'pip', "Can you say circle?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'sparkle'), ('wait', 1.2)]),
    ('s04', "Ducky's ball", 1.4, [
        ('say', 'ducky', "Quack! My ball is a circle! It rolls round and round!"),
        ('wait', 0.2), ('cue', 'roll'), ('wait', 0.3),
        ('say', 'pip', "Round and round, like a circle!"),
        ('wait', 1.4)]),
    ('s05', 'Find the circle', 1.0, [
        ('say', 'pip', "Which one is a circle?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "Yes! The red circle!"),
        ('wait', 1.4)]),
    ('s06', "Sunny's wheels", 1.2, [
        ('say', 'sunny', "My wheels are circles too!"),
        ('wait', 0.6), ('cue', 'n1'), ('say', 'pip', "One!"),
        ('wait', 0.9), ('cue', 'n2'), ('say', 'pip', "Two!"),
        ('wait', 1.6), ('cue', 'n3'), ('say', 'pip', "Three!"),
        ('wait', 0.9), ('cue', 'n4'), ('say', 'pip', "Four!"),
        ('wait', 1.6)]),
    ('s07', "Kitty's present", 1.2, [
        ('say', 'kitty', "Meow! My present is a square!"), ('word', 'shape', 'square'),
        ('wait', 0.5),
        ('say', 'pip', "A square has four sides!"),
        ('wait', 1.3)]),
    ('s08', 'Count the sides', 1.0, [
        ('say', 'pip', "Let's count the sides!"),
        ('wait', 0.5),
        ('all', ['pip', 'kitty'], "One, two, three, four!"),
        ('word', 'n1', 'one'), ('word', 'n2', 'two'), ('word', 'n3', 'three'), ('word', 'n4', 'four'),
        ('wait', 1.6)]),
    ('s09', 'Find the square', 1.0, [
        ('say', 'pip', "Can you find the square?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "Yes! The blue square!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'kitty', "Meow! Hooray!"),
        ('wait', 1.2)]),
    ('s10', 'The block tower', 1.0, [
        ('cue', 'n1'), ('say', 'pip', "One,"), ('wait', 0.5),
        ('cue', 'n2'), ('say', 'pip', "two,"), ('wait', 0.5),
        ('cue', 'n3'), ('say', 'pip', "three!"),
        ('wait', 0.4), ('cue', 'wobble'), ('wait', 1.2), ('cue', 'clap'), ('wait', 0.6),
        ('say', 'kitty', "A square tower!"),
        ('wait', 1.3)]),
    ('s11', 'The triangle trees', 1.6, [
        ('say', 'pip', "Look! These trees are triangles!"), ('word', 'shape', 'triangles'),
        ('wait', 0.5),
        ('say', 'sunny', "Pointy at the top!"),
        ('wait', 1.4)]),
    ('s12', "Froggy's snack", 1.0, [
        ('say', 'froggy', "Ribbit! My snack is a triangle!"),
        ('wait', 0.5),
        ('say', 'pip', "A triangle has three sides!"),
        ('wait', 1.2)]),
    ('s13', 'Count the sides', 1.0, [
        ('all', ['pip', 'froggy'], "One, two, three!"),
        ('word', 'n1', 'one'), ('word', 'n2', 'two'), ('word', 'n3', 'three'),
        ('wait', 0.5), ('cue', 'jump'),
        ('say', 'froggy', "Three sides!"),
        ('wait', 1.3)]),
    ('s14', 'Find the triangle', 1.0, [
        ('say', 'pip', "Which one is a triangle?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "Yes! The green triangle!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'froggy', "Ribbit! Wonderful!"),
        ('wait', 1.2)]),
    ('s15', 'The evening sky', 1.8, [
        ('say', 'birdie', "Tweet! Look, a star!"), ('word', 'shape', 'star'),
        ('wait', 0.5),
        ('say', 'pip', "A star has five points!"),
        ('wait', 1.4)]),
    ('s16', 'Meet Lumi', 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello! I'm Lumi, the little star!"),
        ('wait', 0.5),
        ('all', ['pip', 'birdie'], "Hello, Lumi!"),
        ('wait', 1.4)]),
    ('s17', "Count Lumi's points", 1.0, [
        ('say', 'pip', "Let's count Lumi's points!"),
        ('wait', 0.5),
        ('say', 'pip', "One, two, three, four, five!"),
        ('word', 'n1', 'one'), ('word', 'n2', 'two'), ('word', 'n3', 'three'), ('word', 'n4', 'four'), ('word', 'n5', 'five'),
        ('wait', 0.5),
        ('say', 'lumi', "Five points!"),
        ('wait', 1.3)]),
    ('s18', 'Find the star', 1.0, [
        ('say', 'pip', "Can you find the star?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "Yes! The yellow star!"),
        ('wait', 1.6)]),
    ('s19', 'The shape parade', 1.2, [
        ('cue', 'c1'), ('say', 'ducky', "Circle!"), ('wait', 0.4),
        ('cue', 'c2'), ('say', 'kitty', "Square!"), ('wait', 0.4),
        ('cue', 'c3'), ('say', 'froggy', "Triangle!"), ('wait', 0.4),
        ('cue', 'c4'), ('say', 'birdie', "Star!"),
        ('wait', 1.6)]),
    ('s20', 'The shape challenge', 1.0, [
        ('say', 'pip', "Can you say all the shapes with me?"),
        ('wait', 0.6),
        ('say', 'pip', "Circle! Square! Triangle! Star!"),
        ('word', 'c1', 'circle'), ('word', 'c2', 'square'), ('word', 'c3', 'triangle'), ('word', 'c4', 'star'),
        ('wait', 0.6),
        ('all', FRIENDS + ['lumi'], "Circle! Square! Triangle! Star!"),
        ('word', 'd1', 'circle'), ('word', 'd2', 'square'), ('word', 'd3', 'triangle'), ('word', 'd4', 'star'),
        ('wait', 1.4)]),
    ('s21', 'Build a house', 1.2, [
        ('say', 'pip', "A square house, a triangle roof, a circle window..."),
        ('word', 'h1', 'square'), ('word', 'h2', 'triangle'), ('word', 'h3', 'circle'),
        ('wait', 0.2),
        ('say', 'lumi', "...and a star on top!"), ('word', 'h4', 'star'),
        ('wait', 0.4), ('cue', 'done'), ('wait', 1.8)]),
    ('s22', 'Shape recap', 0.9, [
        ('cue', 'r1'), ('say', 'pip', "A circle, like the sun!"), ('wait', 0.9),
        ('cue', 'r2'), ('say', 'pip', "A square, like a window!"), ('wait', 0.9),
        ('cue', 'r3'), ('say', 'pip', "A triangle, like a tree!"), ('wait', 0.9),
        ('cue', 'r4'), ('say', 'pip', "A star, like Lumi!"), ('wait', 1.2)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for hunting shapes with us!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'pip', "You did a wonderful job today!"),
        ('wait', 0.4),
        ('say', 'lumi', "Goodnight, friends! See you soon!"),
        ('wait', 0.4), ('cue', 'rainbow'),
        ('all', ['pip', 'sunny'] + FRIENDS, "Bye-bye!"),
        ('wait', 1.2), ('cue', 'thanks'), ('wait', 2.6), ('cue', 'subscribe'), ('wait', 3.4)]),
]
TITLE = 3.0


async def speak(key, who, text):
    v = VOICES[who]
    words, path = [], os.path.join(OUT, 'voice', f'{key}.mp3')
    if os.path.exists(path) and os.path.exists(path + '.json'):
        cached = json.load(open(path + '.json'))
        if cached['text'] == text and cached['voice'] == v:
            return path, cached['words']
    for attempt in range(4):
        try:
            com = edge_tts.Communicate(text, v['voice'], rate=v['rate'], pitch=v['pitch'], boundary='WordBoundary')
            words = []
            with open(path, 'wb') as f:
                async for chunk in com.stream():
                    if chunk['type'] == 'audio':
                        f.write(chunk['data'])
                    elif chunk['type'] == 'WordBoundary':
                        words.append([chunk['text'], chunk['offset'] / 1e7])
            break
        except Exception as e:  # the free service is occasionally busy
            print('retry', key, e, file=sys.stderr)
            await asyncio.sleep(2 + attempt * 2)
    json.dump({'text': text, 'voice': v, 'words': words}, open(path + '.json', 'w'))
    return path, words


def trim(path, words):
    """Cut the silence the voice service leaves at both ends; shift the word times to match."""
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '24000', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    loud = np.nonzero(np.abs(x) > 0.012)[0]
    a = max(0, loud[0] - int(0.04 * 24000)) if len(loud) else 0
    b = min(len(x), loud[-1] + int(0.08 * 24000)) if len(loud) else len(x)
    x = x[a:b]
    wav = path.replace('.mp3', '.wav')
    import wave
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    return wav, [[t, round(max(0, o - a / 24000), 3)] for t, o in words]


def envelope(path):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '24000', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768
    step = 24000 // FPS
    rms = [float(np.sqrt(np.mean(x[i:i + step] ** 2))) for i in range(0, len(x), step)]
    top = max(rms) or 1
    return [round(min(1, r / top * 1.4), 3) for r in rms], len(x) / 24000


async def main():
    lines, scenes = {}, []
    t = TITLE
    for sid, name, lead, beats in SCENES:
        start, u, cues, n = t, lead, {}, 0
        last = None
        for b in beats:
            kind = b[0]
            if kind == 'wait':
                u += b[1]
            elif kind == 'cue':
                cues[b[1]] = round(start + u, 3)
            elif kind == 'word':
                word = b[2].lower()
                hit = next((w[1] for w in last['words'] if re.sub(r'\W', '', w[0].lower()) == word), None)
                cues[b[1]] = round(last['start'] + (hit if hit is not None else 0), 3)
            elif kind in ('say', 'all'):
                n += 1
                whos = [b[1]] if kind == 'say' else b[1]
                longest = 0
                for who in whos:
                    key = f'{sid}_{n:02d}' + ('' if kind == 'say' else f'_{who}')
                    path, words = await speak(key, who, b[2])
                    path, words = trim(path, words)
                    env, dur = envelope(path)
                    lines[key] = dict(who=who, text=b[2], dur=round(dur, 3), words=words, env=env,
                                      start=round(start + u, 3), scene=sid, chorus=kind == 'all')
                    longest = max(longest, dur)
                    if last is None or kind == 'say' or who == whos[0]:
                        last = lines[key]
                u += longest
        scenes.append(dict(id=sid, name=name, start=round(start, 3), dur=round(u, 3), cues=cues))
        t += u
    total = round(t, 3)
    json.dump(dict(fps=FPS, title=TITLE, total=total, scenes=scenes, lines=lines),
              open(os.path.join(OUT, 'timeline.json'), 'w'))
    for s in scenes:
        print(f"{s['id']} {s['start']:7.2f} {s['dur']:5.2f}  {s['name']}")
    print('total', total, 's =', f'{int(total // 60)}:{int(total % 60):02d}', '·', len(lines), 'voice lines')

asyncio.run(main())
