"""Rainbow Rescue Bus, episode 6 (The Weather Day): voices, word timings and the timeline.

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


# Cue 'w' is the moment the weather word pops up on screen. n1..nk count; f1..f4 the weather said together; r1..r6 the recap.
SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we look at the weather!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Look up at the sky!"),
        ('wait', 1.4)]),
    ('s02', 'Sunny', 1.2, [
        ('say', 'pip', "The sun is shining."),
        ('wait', 0.4),
        ('say', 'pip', "It is sunny!"), ('word', 'w', 'sunny'),
        ('wait', 0.5),
        ('cue', 'me'), ('say', 'sunny', "Sunny, just like me!"),
        ('wait', 1.3)]),
    ('s03', 'A sun hat', 1.2, [
        ('say', 'kitty', "Meow! The sun is warm."),
        ('wait', 0.4),
        ('say', 'pip', "On a sunny day, we wear a hat."),
        ('wait', 0.4),
        ('say', 'kitty', "My sun hat!"), ('word', 'hat', 'hat'),
        ('wait', 1.3)]),
    ('s04', 'Is it sunny?', 1.0, [
        ('say', 'pip', "Is it sunny?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Yes! It is sunny!"), ('word', 'w', 'sunny'),
        ('wait', 1.3)]),
    ('s05', 'Cloudy', 1.0, [
        ('cue', 'cover'), ('wait', 2.2),
        ('say', 'kitty', "Where did the sun go?"),
        ('wait', 0.4),
        ('say', 'pip', "The clouds are hiding the sun."),
        ('wait', 0.4),
        ('say', 'pip', "It is cloudy!"), ('word', 'w', 'cloudy'),
        ('wait', 1.3)]),
    ('s06', 'Count the clouds', 1.0, [
        ('say', 'pip', "How many clouds can you see?"), *ask(),
        ('say', 'pip', "One, two, three! Three clouds!"), *count(3),
        ('wait', 1.4)]),
    ('s07', 'Windy', 1.0, [
        ('cue', 'gust'), ('wait', 1.2),
        ('say', 'ducky', "Quack! My feathers!"),
        ('wait', 0.4),
        ('say', 'pip', "The wind is blowing."),
        ('wait', 0.4),
        ('say', 'pip', "It is windy!"), ('word', 'w', 'windy'),
        ('wait', 1.3)]),
    ('s08', 'Blow like the wind', 1.0, [
        ('say', 'pip', "Can you blow like the wind?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'ducky'], "Whoosh!"),
        ('wait', 1.6)]),
    ('s09', 'The kite', 1.2, [
        ('say', 'ducky', "Quack! My kite flies in the wind!"),
        ('wait', 0.5),
        ('say', 'pip', "Up, up, up!"), ('word', 'u1', 'up', 0), ('word', 'u2', 'up', 1), ('word', 'u3', 'up', 2),
        ('wait', 2.0)]),
    ('s10', 'Rainy', 1.0, [
        ('cue', 'drop'), ('wait', 0.9),
        ('say', 'froggy', "Ribbit! I feel a drop!"),
        ('wait', 0.3), ('cue', 'rain'), ('wait', 0.3),
        ('say', 'pip', "Drip, drop. The rain is falling."),
        ('wait', 0.4),
        ('say', 'pip', "It is rainy!"), ('word', 'w', 'rainy'),
        ('wait', 1.3)]),
    ('s11', 'The umbrella', 1.0, [
        ('say', 'pip', "The rain makes us wet."),
        ('wait', 0.4),
        ('say', 'pip', "Open the umbrella!"), ('word', 'open', 'open'),
        ('wait', 0.9),
        ('say', 'froggy', "Now we are dry!"),
        ('wait', 1.3)]),
    ('s12', 'Puddles', 1.0, [
        ('say', 'froggy', "Ribbit! I love puddles!"),
        ('wait', 0.4),
        ('say', 'pip', "Can you jump in a puddle?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'froggy'], "Splash!"),
        ('wait', 1.6)]),
    ('s13', 'Thunder', 1.0, [
        ('cue', 'rumble'), ('wait', 2.2),
        ('say', 'froggy', "Ribbit! What was that?"),
        ('wait', 0.4),
        ('say', 'pip', "That is thunder. It is only a loud sound."), ('word', 'w', 'thunder'),
        ('wait', 0.5),
        ('say', 'pip', "Boom! Let's get in the bus!"), ('word', 'boom', 'boom'),
        ('wait', 1.3)]),
    ('s14', 'Wipers', 1.2, [
        ('say', 'sunny', "Swish, swish go my wipers!"), ('word', 's1', 'swish', 0), ('word', 's2', 'swish', 1),
        ('wait', 0.6),
        ('say', 'pip', "We are warm and dry in the bus!"),
        ('wait', 1.6)]),
    ('s15', 'The rain stops', 1.2, [
        ('say', 'birdie', "Tweet! The rain is stopping."),
        ('wait', 0.6),
        ('say', 'pip', "Here comes the sun again!"), ('word', 'sun', 'sun'),
        ('wait', 1.8)]),
    ('s16', 'A rainbow', 1.0, [
        ('say', 'pip', "Sun and rain together make a..."), *ask(),
        ('cue', 'w'), ('all', CREW, "Rainbow!"),
        ('wait', 2.0)]),
    ('s17', 'Hat or umbrella?', 1.0, [
        ('say', 'pip', "It is rainy. Do we take a hat or an umbrella?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "An umbrella!"),
        ('wait', 1.4)]),
    ('s18', 'A clear night', 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello, friends! The sky is clear tonight."),
        ('wait', 0.5),
        ('say', 'pip', "We can see all the stars!"),
        ('wait', 1.4)]),
    ('s19', "Lumi's game: rainy", 1.0, [
        ('say', 'lumi', "Which one is rainy?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! Drip, drop. Rainy!"),
        ('wait', 1.4)]),
    ('s20', "Lumi's game: windy", 1.0, [
        ('say', 'lumi', "Which one is windy?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! Whoosh. Windy!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'pip', "Hooray!"),
        ('wait', 1.2)]),
    ('s21', "What's the weather?", 1.0, [
        ('say', 'pip', "What's the weather?"),
        ('wait', 0.5),
        *[b for i, w in enumerate(['Sunny', 'Cloudy', 'Windy', 'Rainy'])
          for b in (('cue', f'f{i + 1}'), ('all', CREW + ['lumi'], w + '!'), ('wait', 0.4))],
        ('wait', 0.3), ('cue', 'clap'),
        ('wait', 1.5)]),
    ('s22', 'Weather recap', 0.9, [
        ('say', 'pip', "Sunny: the sun shines. Cloudy: the clouds hide the sun."), ('word', 'r1', 'sunny'), ('word', 'r2', 'cloudy'),
        ('wait', 0.7),
        ('say', 'pip', "Windy: the wind blows. Rainy: drip, drop. Thunder: boom!"), ('word', 'r3', 'windy'), ('word', 'r4', 'rainy'), ('word', 'r5', 'thunder'),
        ('wait', 0.7),
        ('say', 'pip', "And after the rain, a rainbow!"), ('word', 'r6', 'rainbow'),
        ('wait', 1.5)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for watching the weather with us!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "Sunny or rainy, every day is a good day!"),
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
