"""Rainbow Rescue Bus, episode 8 (Things That Go): voices, word timings and the timeline.

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


# Cue 'w' is when a vehicle's name pops up; n1.. count; f1.. vehicles said together; r1..r5 the recap.
def parts(names, whos, gap):
    """Everyone says each word together, one short line each (like chant), so no voice runs ahead."""
    out = []
    for i, n in enumerate(names):
        out += [('cue', f'f{i + 1}'), ('all', whos, n + '!'), ('wait', gap)]
    return out


SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we look for things that go!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! I love to go!"),
        ('wait', 1.4)]),
    ('s02', 'Bus', 1.2, [
        ('say', 'sunny', "I am a bus!"), ('word', 'w', 'bus'),
        ('wait', 0.4),
        ('say', 'pip', "A bus carries many friends."), ('word', 'friends', 'friends'),
        ('wait', 0.5),
        ('say', 'pip', "Bus!"),
        ('wait', 1.3)]),
    ('s03', 'Wheels', 1.0, [
        ('say', 'pip', "How many wheels can you see?"), *ask(),
        ('say', 'pip', "One, two! Round and round!"), *count(2), ('word', 'round', 'round'),
        ('wait', 1.4)]),
    ('s04', 'Car', 1.0, [
        ('cue', 'drive'), ('wait', 2.0),
        ('say', 'kitty', "Meow! A little red car!"),
        ('wait', 0.4),
        ('say', 'pip', "A car goes vroom, vroom!"), ('word', 'v1', 'vroom', 0), ('word', 'v2', 'vroom', 1),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'kitty', "Car!"),
        ('wait', 1.3)]),
    ('s05', 'Big or small?', 1.0, [
        ('say', 'pip', "Which one is big?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "The bus is big!"), ('word', 'a', 'big'),
        ('wait', 0.4),
        ('say', 'kitty', "And the car is small!"), ('word', 'b', 'small'),
        ('wait', 1.3)]),
    ('s06', 'Stop and go', 1.2, [
        ('cue', 'red'), ('say', 'pip', "Red light. Stop!"), ('word', 'stop', 'stop'),
        ('wait', 0.8),
        ('cue', 'green'), ('say', 'pip', "Green light. Go!"), ('word', 'go', 'go'),
        ('wait', 0.6),
        ('cue', 'horn'), ('say', 'sunny', "Beep beep!"),
        ('wait', 1.3)]),
    ('s07', 'Stop or go?', 1.0, [
        ('say', 'pip', "The light is red. Do we stop or go?"), *ask(),
        ('cue', 'w'), ('all', CREW, "Stop!"),
        ('wait', 1.6)]),
    ('s08', 'Train', 1.0, [
        ('cue', 'arrive'), ('wait', 2.4),
        ('say', 'froggy', "Ribbit! I hear a train!"),
        ('wait', 0.4),
        ('say', 'pip', "A train rides on tracks."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'froggy', "Train!"),
        ('wait', 1.3)]),
    ('s09', 'Count the train cars', 1.0, [
        ('say', 'pip', "How many train cars?"), *ask(),
        ('say', 'pip', "One, two, three! Three train cars!"), *count(3),
        ('wait', 1.4)]),
    ('s10', 'Choo choo', 1.0, [
        ('say', 'pip', "Can you say choo choo?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'froggy'], "Choo choo!"), ('word', 'ch1', 'choo', 0), ('word', 'ch2', 'choo', 1),
        ('wait', 1.8)]),
    ('s11', 'Boat', 1.2, [
        ('say', 'ducky', "Quack! I have a boat!"),
        ('wait', 0.4),
        ('say', 'pip', "A boat floats on the water."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'ducky', "Boat!"),
        ('wait', 1.3)]),
    ('s12', 'Road or water?', 1.0, [
        ('say', 'pip', "Does a boat go on the road or on the water?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "On the water!"),
        ('wait', 0.3),
        ('say', 'ducky', "Splish, splash!"), ('word', 'sp', 'splash'),
        ('wait', 1.3)]),
    ('s13', 'Plane', 1.0, [
        ('cue', 'fly'), ('wait', 1.6),
        ('say', 'birdie', "Tweet! Look up! A plane!"),
        ('wait', 0.4),
        ('say', 'pip', "A plane flies in the sky."),
        ('wait', 0.4),
        ('cue', 'w'), ('say', 'birdie', "Plane! Just like me!"),
        ('wait', 1.3)]),
    ('s14', 'Fly like a plane', 1.0, [
        ('say', 'pip', "Can you fly like a plane?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'birdie'], "Zoom!"),
        ('wait', 2.0)]),
    ('s15', 'Up and down', 1.2, [
        ('say', 'pip', "The plane goes up."), ('word', 'a', 'up'),
        ('wait', 1.0),
        ('say', 'pip', "And the plane comes down."), ('word', 'b', 'down'),
        ('wait', 1.8)]),
    ('s16', 'Where does it go?', 1.0, [
        ('say', 'pip', "Road, water or sky?"), ('word', 'road', 'road'), ('word', 'water', 'water'), ('word', 'sky', 'sky'),
        ('wait', 0.4),
        ('say', 'pip', "Where does the plane go?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "In the sky!"),
        ('wait', 1.4)]),
    ('s17', 'The parade', 1.0, [
        ('cue', 'go'), ('wait', 1.0),
        ('cue', 'horn'), ('say', 'sunny', "Beep beep!"),
        ('wait', 0.4),
        ('say', 'kitty', "Vroom, vroom!"),
        ('wait', 0.4),
        ('cue', 'toot'), ('say', 'froggy', "Choo choo!"),
        ('wait', 1.8)]),
    ('s18', 'Lumi goes, too', 1.0, [
        ('cue', 'land'), ('wait', 0.5),
        ('say', 'lumi', "Hello, friends! I go across the sky!"),
        ('wait', 0.5),
        ('say', 'pip', "Like a shooting star!"),
        ('wait', 1.6)]),
    ('s19', "Lumi's game: the train", 1.0, [
        ('say', 'lumi', "Which one is the train?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! The green train!"),
        ('wait', 1.4)]),
    ('s20', "Lumi's game: the plane", 1.0, [
        ('say', 'lumi', "Which one flies in the sky?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! The purple plane!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'pip', "Hooray!"),
        ('wait', 1.2)]),
    ('s21', 'What goes?', 1.0, [
        ('say', 'pip', "What goes?"),
        ('wait', 0.5),
        *parts(['Bus', 'Car', 'Train', 'Boat', 'Plane'], CREW + ['lumi'], 0.45),
        ('wait', 0.2), ('cue', 'clap'),
        ('wait', 1.4)]),
    ('s22', 'Things that go recap', 0.9, [
        ('say', 'pip', "The bus and the car go on the road."), ('word', 'r1', 'bus'), ('word', 'r2', 'car'),
        ('wait', 0.7),
        ('say', 'pip', "The train goes on the tracks. The boat goes on the water."), ('word', 'r3', 'train'), ('word', 'r4', 'boat'),
        ('wait', 0.7),
        ('say', 'pip', "And the plane goes in the sky!"), ('word', 'r5', 'plane'),
        ('wait', 1.5)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for riding with us!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "You know so many things that go!"),
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
