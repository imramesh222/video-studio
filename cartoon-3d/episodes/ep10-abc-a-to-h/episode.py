"""Rainbow Rescue Bus, episode 10 (ABC with Pip, A to H): voices, word timings and the timeline.

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
CREW = ['pip', 'sunny'] + FRIENDS
NUM = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']


def count(k, p='n', first=1):
    """Word cues n1..nk for the numbers said in the last line."""
    return [('word', f'{p}{i}', NUM[i - 1]) for i in range(first, k + 1)]


def chant(whos, k, gap=0.15, last=()):
    """A counting chorus: everyone says each number together, one short line per number,
    so no voice runs ahead (one long line per voice drifts by seconds). `last` goes before the final number."""
    beats = []
    for i in range(1, k + 1):
        if i > 1:
            beats.append(('wait', gap))
        beats.append(('cue', f'n{i}'))
        if i == k:
            beats += last
        beats.append(('all', whos, NUM[i - 1].capitalize() + '!'))
    return beats


def ask(wait=2.0):
    """A question to the viewer: three dots, then a 2-second pause for the answer."""
    return [('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', wait)]


# Cue 'L' is when a scene's letter is said (its big letter pops up); 'w' when its word pops up; l1.. letters in a row; f1.. said together; r1..r8 the recap.
def parts(names, whos, gap):
    """Everyone says each word together, one short line each (like chant), so no voice runs ahead."""
    out = []
    for i, n in enumerate(names):
        out += [('cue', f'f{i + 1}'), ('all', whos, n + '!'), ('wait', gap)]
    return out


SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we learn our ABCs!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Let's find some letters!"),
        ('wait', 1.4)]),
    ('s02', 'The letter song', 1.2, [
        ('say', 'pip', "A, B, C, D!"), ('word', 'l1', 'a'), ('word', 'l2', 'b'), ('word', 'l3', 'c'), ('word', 'l4', 'd'),
        ('wait', 0.4),
        ('say', 'sunny', "E, F, G, H!"), ('word', 'l5', 'e'), ('word', 'l6', 'f'), ('word', 'l7', 'g'), ('word', 'l8', 'h'),
        ('wait', 1.5)]),
    ('s03', 'A is for apple', 1.2, [
        ('say', 'birdie', "Tweet! A is for apple!"), ('word', 'L', 'a'), ('word', 'w', 'apple'),
        ('wait', 0.6),
        ('say', 'pip', "A! Apple!"),
        ('wait', 1.4)]),
    ('s04', 'Say A', 1.0, [
        ('say', 'pip', "Can you say A?"), *ask(),
        ('cue', 'L'), ('all', ['pip', 'birdie'], "A!"),
        ('wait', 1.6)]),
    ('s05', 'B is for ball', 1.2, [
        ('say', 'pip', "B is for ball!"), ('word', 'L', 'b'), ('word', 'w', 'ball'),
        ('wait', 0.5),
        ('say', 'sunny', "And B is for bus! That's me!"), ('word', 'bus', 'bus'),
        ('wait', 0.5),
        ('say', 'pip', "B! Ball!"),
        ('wait', 1.3)]),
    ('s06', 'What else starts with B?', 1.0, [
        ('say', 'pip', "What else starts with B?"), *ask(),
        ('cue', 'w'), ('say', 'kitty', "Balloon!"),
        ('wait', 1.6)]),
    ('s07', 'C is for cat', 1.2, [
        ('say', 'kitty', "Meow! C is for cat!"), ('word', 'L', 'c'), ('word', 'w', 'cat'),
        ('wait', 0.5),
        ('say', 'pip', "And C is for cookie!"), ('word', 'cookie', 'cookie'),
        ('wait', 0.5),
        ('say', 'kitty', "C! Cat!"),
        ('wait', 1.3)]),
    ('s08', 'Which one is C?', 1.0, [
        ('say', 'pip', "Which one is the letter C?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Yes! This is C!"),
        ('wait', 1.4)]),
    ('s09', 'D is for duck', 1.2, [
        ('say', 'ducky', "Quack! D is for duck!"), ('word', 'L', 'd'), ('word', 'w', 'duck'),
        ('wait', 0.5),
        ('say', 'pip', "D! Duck!"),
        ('wait', 0.4),
        ('say', 'ducky', "That's me!"),
        ('wait', 1.3)]),
    ('s10', 'A, B, C, D', 1.0, [
        ('say', 'pip', "Let's say them again!"),
        ('wait', 0.6),
        *parts(['A', 'B', 'C', 'D'], CREW, 0.6),
        ('wait', 1.0)]),
    ('s11', 'E is for egg', 1.2, [
        ('say', 'ducky', "Quack! I found an egg!"), ('word', 'egg', 'egg'),
        ('wait', 0.5),
        ('say', 'pip', "E is for egg!"), ('word', 'L', 'e'), ('word', 'w', 'egg'),
        ('wait', 0.5),
        ('say', 'pip', "E! Egg!"),
        ('wait', 1.3)]),
    ('s12', 'Say E', 1.0, [
        ('say', 'pip', "Can you say E?"), *ask(),
        ('cue', 'L'), ('all', ['pip', 'ducky'], "E!"),
        ('wait', 1.6)]),
    ('s13', 'F is for frog', 1.2, [
        ('say', 'froggy', "Ribbit! F is for frog!"), ('word', 'L', 'f'), ('word', 'w', 'frog'),
        ('wait', 0.5),
        ('say', 'pip', "F is for fish and flower, too!"), ('word', 'fish', 'fish'), ('word', 'flower', 'flower'),
        ('wait', 0.5),
        ('say', 'froggy', "F! Frog!"),
        ('wait', 1.3)]),
    ('s14', 'Who starts with F?', 1.0, [
        ('say', 'pip', "Who starts with F?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Froggy! F is for frog!"),
        ('wait', 1.4)]),
    ('s15', 'G is for grapes', 1.2, [
        ('say', 'froggy', "G is for grapes!"), ('word', 'L', 'g'), ('word', 'w', 'grapes'),
        ('wait', 0.5),
        ('say', 'pip', "And G is for green grass!"), ('word', 'grass', 'grass'),
        ('wait', 0.5),
        ('say', 'pip', "G! Grapes!"),
        ('wait', 1.3)]),
    ('s16', 'H is for house', 1.2, [
        ('say', 'birdie', "Tweet! H is for house!"), ('word', 'L', 'h'), ('word', 'w', 'house'),
        ('wait', 0.5),
        ('say', 'pip', "And H is for hop! Hop, hop, hop!"), ('word', 'h1', 'hop', 1), ('word', 'h2', 'hop', 2), ('word', 'h3', 'hop', 3),
        ('wait', 0.5),
        ('say', 'birdie', "H! House!"),
        ('wait', 1.3)]),
    ('s17', 'Hop like Pip', 1.0, [
        ('say', 'pip', "Can you hop like me?"), *ask(),
        ('cue', 'w'), ('all', CREW, "Hop!"),
        ('wait', 1.8)]),
    ('s18', 'E, F, G, H', 1.0, [
        ('say', 'pip', "And the next four!"),
        ('wait', 0.6),
        *parts(['E', 'F', 'G', 'H'], CREW, 0.6),
        ('wait', 1.0)]),
    ('s19', 'Lumi loves letters', 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello, friends! I love letters!"),
        ('wait', 0.5),
        ('say', 'pip', "Lumi, play the letter game with us!"),
        ('wait', 1.4)]),
    ('s20', "Lumi's game: B", 1.0, [
        ('say', 'lumi', "Which one is the letter B?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! B is for ball!"),
        ('wait', 1.4)]),
    ('s21', "Lumi's game: H", 1.0, [
        ('say', 'lumi', "Which one is the letter H?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! H is for house!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'pip', "Hooray!"),
        ('wait', 1.2)]),
    ('s22', 'ABC recap', 0.9, [
        ('say', 'pip', "A, apple. B, ball. C, cat. D, duck."), ('word', 'r1', 'a'), ('word', 'r2', 'b'), ('word', 'r3', 'c'), ('word', 'r4', 'd'),
        ('wait', 0.7),
        ('say', 'pip', "E, egg. F, frog. G, grapes. H, house."), ('word', 'r5', 'e'), ('word', 'r6', 'f'), ('word', 'r7', 'g'), ('word', 'r8', 'h'),
        ('wait', 0.7),
        ('say', 'pip', "Eight letters!"), ('word', 'eight', 'eight'),
        ('wait', 1.5)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Next time, we find more letters!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "You know your first letters!"),
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
                hits = [w[1] for w in last['words'] if re.sub(r'\W', '', w[0].lower()) == word]
                k = b[3] if len(b) > 3 else 0
                if k >= len(hits):
                    sys.exit(f'{sid}: "{word}" is not said {k + 1} times in "{last["text"]}"')
                cues[b[1]] = round(last['start'] + hits[k], 3)
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
                                      start=round(start + u, 3), scene=sid, chorus=kind == 'all', gain=b[3] if len(b) > 3 else 1.0)
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
