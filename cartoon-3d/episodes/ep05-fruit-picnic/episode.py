"""Rainbow Rescue Bus, episode 5 (The Fruit Picnic): voices, word timings and the timeline.

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


# Cue 'w' is the moment a fruit's name pops up on screen. n1..nk count; f1..f6 the fruits said together.
SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we are having a fruit picnic!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Let's find some fruit!"),
        ('wait', 1.4)]),
    ('s02', 'The empty basket', 1.2, [
        ('say', 'pip', "Oh no! My basket is empty."), ('word', 'empty', 'empty'),
        ('wait', 0.5),
        ('say', 'pip', "Let's fill it with fruit!"),
        ('wait', 1.4)]),
    ('s03', 'Apple', 1.2, [
        ('say', 'birdie', "Tweet! I have an apple!"),
        ('wait', 0.2), ('cue', 'drop'), ('wait', 0.9),
        ('say', 'pip', "An apple is red and round."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'pip', "Apple!"),
        ('wait', 1.3)]),
    ('s04', 'Say apple', 1.0, [
        ('say', 'pip', "Can you say apple?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'birdie'], "Apple!"),
        ('wait', 1.4)]),
    ('s05', 'Banana', 1.2, [
        ('say', 'kitty', "Meow! I have a banana!"),
        ('wait', 0.4),
        ('say', 'pip', "A banana is yellow and long."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'kitty', "Banana!"),
        ('wait', 1.3)]),
    ('s06', 'Peel the banana', 1.2, [
        ('say', 'kitty', "First we peel it."),
        ('wait', 0.4),
        ('say', 'pip', "Peel, peel, peel!"), ('word', 'p1', 'peel', 0), ('word', 'p2', 'peel', 1), ('word', 'p3', 'peel', 2),
        ('wait', 0.6),
        ('cue', 'bite'), ('say', 'kitty', "Yum!"),
        ('wait', 1.3)]),
    ('s07', 'Orange', 1.0, [
        ('cue', 'roll'), ('wait', 1.4),
        ('say', 'ducky', "Quack! I have an orange!"),
        ('wait', 0.4),
        ('say', 'pip', "An orange is orange and round."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'ducky', "Orange!"),
        ('wait', 1.3)]),
    ('s08', 'Which one is the orange?', 1.0, [
        ('say', 'pip', "Which one is the orange?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Yes! This is the orange!"),
        ('wait', 1.4)]),
    ('s09', 'Strawberry', 1.0, [
        ('cue', 'lift'), ('wait', 1.2),
        ('say', 'froggy', "Ribbit! I found strawberries!"),
        ('wait', 0.4),
        ('say', 'pip', "A strawberry is red and small."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'froggy', "Strawberry!"),
        ('wait', 1.3)]),
    ('s10', 'Count the strawberries', 1.0, [
        ('say', 'pip', "How many strawberries?"), *ask(),
        ('say', 'pip', "One, two, three! Three strawberries!"), *count(3),
        ('wait', 1.4)]),
    ('s11', 'Grapes', 1.0, [
        ('say', 'froggy', "Look up! Grapes!"),
        ('wait', 0.5),
        ('say', 'pip', "Grapes are purple and tiny."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'pip', "Grapes!"),
        ('wait', 1.3)]),
    ('s12', 'Watermelon', 1.0, [
        ('cue', 'horn'), ('wait', 2.6),
        ('say', 'sunny', "Beep beep! I have a watermelon!"),
        ('wait', 0.4),
        ('say', 'pip', "A watermelon is big and green!"),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'sunny', "Watermelon!"),
        ('wait', 1.3)]),
    ('s13', 'Inside the watermelon', 1.0, [
        ('say', 'pip', "What color is it inside?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 0.6), ('cue', 'crack'), ('wait', 1.4),
        ('cue', 'w'), ('say', 'pip', "Red! With little black seeds."),
        ('wait', 1.4)]),
    ('s14', 'Big or small?', 1.0, [
        ('say', 'pip', "Which fruit is big?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "The watermelon is big!"), ('word', 'a', 'big'),
        ('wait', 0.4),
        ('say', 'froggy', "And the strawberry is small!"), ('word', 'b', 'small'),
        ('wait', 1.3)]),
    ('s15', 'Picnic time', 1.2, [
        ('say', 'pip', "Look! The basket is full!"),
        ('wait', 0.5),
        ('cue', 'cheer'), ('all', CREW, "Picnic time!"),
        ('wait', 1.6)]),
    ('s16', 'Sharing', 1.0, [
        ('say', 'kitty', "An apple for you, Birdie."), ('cue', 'give1'),
        ('wait', 0.9),
        ('say', 'birdie', "A banana for you, Kitty."), ('cue', 'give2'),
        ('wait', 0.9),
        ('say', 'pip', "Sharing is fun!"),
        ('wait', 1.3)]),
    ('s17', 'Yum, yum', 1.0, [
        ('say', 'pip', "Can you rub your tummy?"), *ask(),
        ('cue', 'yum'), ('all', CREW, "Yum, yum!"),
        ('wait', 1.6)]),
    ('s18', 'Lumi comes', 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello, friends! What a yummy picnic!"),
        ('wait', 0.5),
        ('say', 'pip', "Lumi, play the fruit game with us!"),
        ('wait', 1.4)]),
    ('s19', "Lumi's game: the banana", 1.0, [
        ('say', 'lumi', "Which one is the banana?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! The yellow banana!"),
        ('wait', 1.4)]),
    ('s20', "Lumi's game: the grapes", 1.0, [
        ('say', 'lumi', "Where are the grapes?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! The purple grapes!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'pip', "Hooray!"),
        ('wait', 1.2)]),
    ('s21', 'Say the fruits', 1.0, [
        ('say', 'pip', "Let's say them all!"),
        ('wait', 0.5),
        *[b for i, fr in enumerate(['Apple', 'Banana', 'Orange', 'Strawberry', 'Grapes', 'Watermelon'])
          for b in (('cue', f'f{i + 1}'), ('all', CREW + ['lumi'], fr + '!'), ('wait', 0.35))],
        ('wait', 0.3), ('cue', 'clap'),
        ('wait', 1.5)]),
    ('s22', 'Fruit recap', 0.9, [
        ('say', 'pip', "A red apple. A yellow banana. An orange orange."),
        ('word', 'r1', 'apple'), ('word', 'r2', 'banana'), ('word', 'r3', 'orange', 1),
        ('wait', 0.7),
        ('say', 'pip', "Red strawberries. Purple grapes."), ('word', 'r4', 'strawberries'), ('word', 'r5', 'grapes'),
        ('wait', 0.7),
        ('say', 'pip', "And a big green watermelon!"), ('word', 'r6', 'watermelon'),
        ('wait', 1.5)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for our fruit picnic!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "You know so many fruits!"),
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
