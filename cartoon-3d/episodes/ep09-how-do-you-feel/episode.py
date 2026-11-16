"""Rainbow Rescue Bus, episode 9 (How Do You Feel?): voices, word timings and the timeline.

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


# Cue 'w' is when a feeling's name pops up; n1.. count; f1.. feelings said together; r1..r5 the recap.
def parts(names, whos, gap):
    """Everyone says each word together, one short line each (like chant), so no voice runs ahead."""
    out = []
    for i, n in enumerate(names):
        out += [('cue', f'f{i + 1}'), ('all', whos, n + '!'), ('wait', gap)]
    return out


SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we talk about feelings!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Let's find out how we feel!"),
        ('wait', 1.4)]),
    ('s02', 'Happy', 1.2, [
        ('say', 'pip', "I am smiling. I feel happy!"), ('word', 'w', 'happy'),
        ('wait', 0.4),
        ('say', 'sunny', "I feel happy when we ride together!"),
        ('wait', 0.4),
        ('say', 'pip', "Happy!"),
        ('wait', 1.3)]),
    ('s03', 'A happy face', 1.0, [
        ('say', 'pip', "Can you make a happy face?"), *ask(),
        ('cue', 'w'), ('say', 'pip', "What a big smile!"),
        ('wait', 1.4)]),
    ('s04', 'Sad', 1.0, [
        ('cue', 'float'), ('wait', 1.8),
        ('say', 'kitty', "Meow. My balloon flew away."),
        ('wait', 0.5),
        ('say', 'kitty', "I feel sad."), ('word', 'w', 'sad'),
        ('wait', 0.5),
        ('say', 'pip', "Kitty is sad."),
        ('wait', 1.3)]),
    ('s05', 'A hug helps', 1.0, [
        ('say', 'pip', "When a friend is sad, we give a hug."), ('word', 'hug', 'hug'),
        ('wait', 0.9),
        ('say', 'kitty', "Thank you, Pip."),
        ('wait', 0.4),
        ('say', 'kitty', "I feel better."),
        ('wait', 1.3)]),
    ('s06', 'Happy or sad?', 1.0, [
        ('say', 'pip', "Is Kitty happy or sad now?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Kitty is happy!"), ('word', 'w', 'happy'),
        ('wait', 1.4)]),
    ('s07', 'Angry', 1.0, [
        ('cue', 'tumble'), ('wait', 1.6),
        ('say', 'ducky', "Quack! My blocks fell down!"),
        ('wait', 0.4),
        ('cue', 'stomp'), ('say', 'ducky', "I feel angry!"), ('word', 'w', 'angry'),
        ('wait', 0.5),
        ('say', 'pip', "Ducky is angry."),
        ('wait', 1.3)]),
    ('s08', 'A big breath helps', 1.0, [
        ('say', 'pip', "When we are angry, we take a big breath."),
        ('wait', 0.5),
        ('say', 'pip', "Breathe in. And breathe out."), ('word', 'in', 'in'), ('word', 'out', 'out'),
        ('wait', 1.0),
        ('say', 'ducky', "I feel calm now."),
        ('wait', 1.3)]),
    ('s09', 'Breathe with us', 1.0, [
        ('say', 'pip', "Can you take a big breath?"), *ask(),
        ('say', 'pip', "In. And out. Well done!"), ('word', 'in', 'in'), ('word', 'out', 'out'), ('word', 'well', 'well'),
        ('wait', 1.4)]),
    ('s10', 'Build it again', 1.0, [
        ('say', 'pip', "Let's build it again, together!"),
        ('wait', 0.4),
        ('say', 'ducky', "One, two, three blocks!"), *count(3),
        ('wait', 0.5),
        ('say', 'ducky', "Now I am happy!"), ('word', 'w', 'happy'),
        ('wait', 1.3)]),
    ('s11', 'Scared', 1.0, [
        ('cue', 'rustle'), ('wait', 1.6),
        ('say', 'froggy', "Ribbit! What is that noise?"),
        ('wait', 0.4),
        ('say', 'froggy', "I feel scared."), ('word', 'w', 'scared'),
        ('wait', 0.5),
        ('say', 'pip', "I am here, Froggy. Hold my hand."), ('word', 'hand', 'hand'),
        ('wait', 1.3)]),
    ('s12', "It's only Birdie", 1.0, [
        ('cue', 'peek'), ('wait', 0.5),
        ('say', 'birdie', "Tweet! It's only me!"),
        ('wait', 0.4),
        ('say', 'froggy', "Oh! It's Birdie!"),
        ('wait', 0.4),
        ('say', 'pip', "Now Froggy feels safe."),
        ('wait', 1.3)]),
    ('s13', 'Who was it?', 1.0, [
        ('say', 'pip', "Who was in the bush?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "It was Birdie!"),
        ('wait', 1.4)]),
    ('s14', 'Surprised', 1.0, [
        ('say', 'birdie', "I have a surprise for you!"),
        ('wait', 0.3), ('cue', 'open'), ('wait', 0.6),
        ('cue', 'wow'), ('all', CREW, "Wow!"),
        ('wait', 0.6),
        ('say', 'pip', "We feel surprised!"), ('word', 'w', 'surprised'),
        ('wait', 1.4)]),
    ('s15', 'A surprised face', 1.0, [
        ('say', 'pip', "Can you make a surprised face?"), *ask(),
        ('cue', 'w'), ('all', CREW, "Wow!"),
        ('wait', 1.8)]),
    ('s16', 'Show me the faces', 1.0, [
        ('say', 'pip', "Show me the faces!"),
        ('wait', 0.6),
        *parts(['Happy', 'Sad', 'Surprised'], CREW, 1.0),
        ('wait', 0.6)]),
    ('s17', 'Sleepy', 1.4, [
        ('cue', 'yawn'), ('wait', 1.4),
        ('say', 'birdie', "Tweet. I feel sleepy."), ('word', 'w', 'sleepy'),
        ('wait', 0.5),
        ('say', 'pip', "When we are sleepy, we rest."),
        ('wait', 0.5),
        ('say', 'sunny', "Hop in. I will drive slowly."),
        ('wait', 1.4)]),
    ('s18', 'How do you feel tonight?', 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello, friends! How do you feel tonight?"),
        ('wait', 0.5),
        ('say', 'pip', "We feel happy to see you, Lumi!"), ('word', 'w', 'happy'),
        ('wait', 1.4)]),
    ('s19', "Lumi's game: sad", 1.0, [
        ('say', 'lumi', "Who feels sad?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! Kitty feels sad. A hug helps."), ('word', 'hug', 'hug'),
        ('wait', 1.4)]),
    ('s20', "Lumi's game: sleepy", 1.0, [
        ('say', 'lumi', "Who feels sleepy?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! Birdie feels sleepy."),
        ('wait', 0.4),
        ('say', 'pip', "Shh.", 0.6),
        ('wait', 1.4)]),
    ('s21', 'Name the feelings', 1.0, [
        ('say', 'pip', "How can we feel?"),
        ('wait', 0.5),
        *parts(['Happy', 'Sad', 'Angry', 'Scared', 'Sleepy'], CREW + ['lumi'], 0.6),
        ('wait', 1.2)]),
    ('s22', 'Feelings recap', 0.9, [
        ('say', 'pip', "Happy: we smile. Sad: we hug."), ('word', 'r1', 'happy'), ('word', 'r2', 'sad'),
        ('wait', 0.7),
        ('say', 'pip', "Angry: we breathe. Scared: we hold hands."), ('word', 'r3', 'angry'), ('word', 'r4', 'scared'),
        ('wait', 0.7),
        ('say', 'pip', "Sleepy: we rest."), ('word', 'r5', 'sleepy'),
        ('wait', 1.6)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for sharing your feelings!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "All your feelings are okay."),
        ('wait', 0.5),
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
