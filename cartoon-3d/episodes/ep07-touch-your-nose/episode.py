"""Rainbow Rescue Bus, episode 7 (Touch Your Nose): voices, word timings and the timeline.

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


# Cue 'e' is when a body part is named and lights up; 'w' when everyone says it together; f1.. the parts said together; r1..r6 the recap.
def parts(names, whos, gap):
    """Everyone says each body part together, one short line each (like chant), so no voice runs ahead."""
    out = []
    for i, n in enumerate(names):
        out += [('cue', f'f{i + 1}'), ('all', whos, n + '!'), ('wait', gap)]
    return out


SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we learn about our body!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Let's play copy me!"),
        ('wait', 1.4)]),
    ('s02', 'Eyes', 1.2, [
        ('say', 'pip', "I have two eyes."), ('word', 'e', 'eyes'),
        ('wait', 0.4),
        ('say', 'pip', "I see with my eyes!"),
        ('wait', 0.5),
        ('say', 'sunny', "I have big blue eyes!"), ('word', 'se', 'eyes'),
        ('wait', 1.3)]),
    ('s03', 'Blink', 1.0, [
        ('say', 'pip', "Can you blink your eyes?"), *ask(),
        ('say', 'pip', "Blink, blink!"), ('word', 'b1', 'blink', 0), ('word', 'b2', 'blink', 1),
        ('wait', 1.4)]),
    ('s04', 'Ears', 1.2, [
        ('say', 'kitty', "Meow! I have two ears."), ('word', 'e', 'ears'),
        ('wait', 0.4),
        ('say', 'pip', "We hear with our ears."),
        ('wait', 0.3), ('cue', 'tweet'), ('wait', 1.0),
        ('say', 'kitty', "Listen! A little bird!"),
        ('wait', 1.4)]),
    ('s05', 'Touch your ears', 1.0, [
        ('say', 'pip', "Can you touch your ears?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'kitty'], "Ears!"),
        ('wait', 1.6)]),
    ('s06', 'Nose', 1.2, [
        ('say', 'pip', "This is my nose."), ('word', 'e', 'nose'),
        ('wait', 0.4),
        ('say', 'pip', "I smell with my nose."),
        ('wait', 0.5),
        ('say', 'kitty', "Sniff, sniff. A flower!"), ('word', 'n1', 'sniff', 0), ('word', 'n2', 'sniff', 1),
        ('wait', 1.3)]),
    ('s07', 'Touch your nose', 1.0, [
        ('say', 'pip', "Can you touch your nose?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'kitty'], "Nose!"),
        ('wait', 1.6)]),
    ('s08', 'Mouth', 1.2, [
        ('say', 'ducky', "Quack! This is my beak."), ('word', 'beak', 'beak'),
        ('wait', 0.4),
        ('say', 'pip', "I have a mouth."), ('word', 'e', 'mouth'),
        ('wait', 0.4),
        ('say', 'pip', "I eat and talk with my mouth!"),
        ('wait', 1.3)]),
    ('s09', 'Open wide', 1.0, [
        ('say', 'pip', "Can you open your mouth wide?"), *ask(),
        ('cue', 'wide'), ('say', 'pip', "Aaah! And now a big smile!"), ('word', 'smile', 'smile'),
        ('wait', 1.4)]),
    ('s10', 'Hands', 1.2, [
        ('say', 'froggy', "Ribbit! I have two hands."), ('word', 'e', 'hands'),
        ('wait', 0.4),
        ('say', 'pip', "I clap with my hands."),
        ('wait', 0.4),
        ('say', 'pip', "Clap, clap, clap!"), ('word', 'c1', 'clap', 0), ('word', 'c2', 'clap', 1), ('word', 'c3', 'clap', 2),
        ('wait', 1.4)]),
    ('s11', 'Wave your hands', 1.0, [
        ('say', 'pip', "Can you wave your hands?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'froggy'], "Wave!"),
        ('wait', 1.8)]),
    ('s12', 'Feet', 1.2, [
        ('say', 'froggy', "I have two feet. I jump with my feet!"), ('word', 'e', 'feet'), ('word', 'jmp', 'jump'),
        ('wait', 0.4),
        ('say', 'pip', "I walk with my feet."),
        ('wait', 0.4),
        ('say', 'pip', "Stomp, stomp, stomp!"), ('word', 's1', 'stomp', 0), ('word', 's2', 'stomp', 1), ('word', 's3', 'stomp', 2),
        ('wait', 1.4)]),
    ('s13', 'Stomp your feet', 1.0, [
        ('say', 'pip', "Can you stomp your feet?"), *ask(),
        ('cue', 'w'), ('all', ['pip', 'froggy'], "Stomp, stomp!"), ('word', 't1', 'stomp', 0), ('word', 't2', 'stomp', 1),
        ('wait', 1.6)]),
    ('s14', 'Tummy', 1.2, [
        ('cue', 'rumble'), ('wait', 1.2),
        ('say', 'birdie', "Tweet! My tummy is hungry."), ('word', 'bt', 'tummy'),
        ('wait', 0.4),
        ('say', 'pip', "This is my tummy."), ('word', 'e', 'tummy'),
        ('wait', 0.4),
        ('say', 'pip', "Pat, pat, pat!"), ('word', 'p1', 'pat', 0), ('word', 'p2', 'pat', 1), ('word', 'p3', 'pat', 2),
        ('wait', 1.4)]),
    ('s15', 'Wings and arms', 1.2, [
        ('say', 'birdie', "I have two wings!"), ('word', 'wg', 'wings'),
        ('wait', 0.5),
        ('say', 'pip', "I have two arms!"), ('word', 'arms', 'arms'),
        ('wait', 0.5),
        ('say', 'pip', "Can you flap your arms?"), *ask(),
        ('cue', 'flap'), ('wait', 1.0)]),
    ('s16', 'Copy me', 1.0, [
        ('say', 'pip', "Let's play copy me!"),
        ('wait', 0.6),
        *parts(['Nose', 'Ears', 'Tummy', 'Feet'], CREW, 0.7),
        ('wait', 1.0)]),
    ('s17', 'Sunset', 1.8, [
        ('say', 'birdie', "Tweet! The sun is going down."),
        ('wait', 0.5),
        ('say', 'pip', "I can see it with my eyes!"), ('word', 'e', 'eyes'),
        ('wait', 1.5)]),
    ('s18', 'Lumi has a face', 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello, friends! I have eyes and a mouth, too!"), ('word', 'le', 'eyes'), ('word', 'lm', 'mouth'),
        ('wait', 0.5),
        ('say', 'pip', "And you shine, Lumi!"),
        ('wait', 1.4)]),
    ('s19', "Lumi's game: ears", 1.0, [
        ('say', 'lumi', "Where are Pip's ears?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! Two ears!"),
        ('wait', 1.4)]),
    ('s20', "Lumi's game: feet", 1.0, [
        ('say', 'lumi', "Where are Froggy's feet?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! Two feet!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'pip', "Hooray!"),
        ('wait', 1.2)]),
    ('s21', 'Touch them with me', 1.0, [
        ('say', 'pip', "Touch them with me!"),
        ('wait', 0.6),
        *parts(['Eyes', 'Ears', 'Nose', 'Mouth', 'Hands', 'Feet'], CREW + ['lumi'], 0.55),
        ('wait', 0.2), ('cue', 'clap'),
        ('wait', 1.4)]),
    ('s22', 'Body recap', 0.9, [
        ('say', 'pip', "Eyes to see. Ears to hear. A nose to smell."), ('word', 'r1', 'eyes'), ('word', 'r2', 'ears'), ('word', 'r3', 'nose'),
        ('wait', 0.7),
        ('say', 'pip', "A mouth to eat. Hands to clap. Feet to walk."), ('word', 'r4', 'mouth'), ('word', 'r5', 'hands'), ('word', 'r6', 'feet'),
        ('wait', 0.7),
        ('say', 'pip', "That is my body!"), ('word', 'body', 'body'),
        ('wait', 1.5)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for playing copy me!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "Now close your eyes."), ('word', 'close', 'eyes'),
        ('wait', 0.6),
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
