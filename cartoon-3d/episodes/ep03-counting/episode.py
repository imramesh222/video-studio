"""Rainbow Rescue Bus, episode 3 (Counting 1 to 10): voices, word timings and the timeline.

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


SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we are going to count to ten!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! We're going to Lumi's star party!"),
        ('wait', 1.4)]),
    ('s02', 'The number song', 1.2, [
        ('say', 'pip', "One, two, three, four, five!"), *count(5),
        ('wait', 0.3),
        ('say', 'sunny', "Six, seven, eight, nine, ten!"), *count(10, first=6),
        ('wait', 1.4)]),
    ('s03', 'One bus', 1.2, [
        ('say', 'sunny', "I am one big yellow bus!"), ('word', 'n1', 'one'),
        ('wait', 0.5),
        ('say', 'pip', "Can you hold up one finger?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('say', 'pip', "One!"), ('cue', 'sparkle'),
        ('wait', 1.2)]),
    ('s04', 'Two balloons', 1.4, [
        ('say', 'kitty', "Meow! I have two red balloons!"),
        ('wait', 0.5),
        ('say', 'pip', "One, two! Two balloons!"), *count(2),
        ('wait', 1.4)]),
    ('s05', 'Three fish', 1.4, [
        ('say', 'ducky', "Quack! Look, the fish are jumping!"),
        ('wait', 0.6), ('cue', 'n1'), ('say', 'pip', "One!"),
        ('wait', 0.7), ('cue', 'n2'), ('say', 'pip', "Two!"),
        ('wait', 0.7), ('cue', 'n3'), ('say', 'pip', "Three!"),
        ('wait', 0.5),
        ('say', 'ducky', "Three fish!"),
        ('wait', 1.3)]),
    ('s06', 'Four hops', 1.4, [
        ('say', 'froggy', "Ribbit! Watch me hop on the leaves!"),
        ('wait', 0.6), ('cue', 'n1'), ('all', ['pip', 'froggy'], "One!"),
        ('wait', 0.6), ('cue', 'n2'), ('all', ['pip', 'froggy'], "Two!"),
        ('wait', 0.6), ('cue', 'n3'), ('all', ['pip', 'froggy'], "Three!"),
        ('wait', 0.6), ('cue', 'n4'), ('all', ['pip', 'froggy'], "Four!"),
        ('wait', 0.5),
        ('say', 'froggy', "Four hops!"),
        ('wait', 1.3)]),
    ('s07', 'Five apples', 1.4, [
        ('say', 'birdie', "Tweet! How many apples are in my tree?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('say', 'pip', "One, two, three, four, five!"), *count(5),
        ('wait', 0.5),
        ('say', 'birdie', "Five apples!"),
        ('wait', 1.3)]),
    ('s08', 'Count the friends', 1.2, [
        ('say', 'pip', "Let's count our friends on the bus!"),
        ('wait', 0.5), ('cue', 'n1'), ('say', 'kitty', "One!"),
        ('wait', 0.4), ('cue', 'n2'), ('say', 'ducky', "Two!"),
        ('wait', 0.4), ('cue', 'n3'), ('say', 'froggy', "Three!"),
        ('wait', 0.4), ('cue', 'n4'), ('say', 'birdie', "Four!"),
        ('wait', 0.4),
        ('say', 'pip', "And me, five!"), ('word', 'n5', 'five'),
        ('wait', 1.4)]),
    ('s09', 'How many balls?', 1.0, [
        ('say', 'pip', "How many balls can you see?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('say', 'pip', "One, two, three! Three balls!"), *count(3),
        ('cue', 'found'),
        ('wait', 1.4)]),
    ('s10', 'Six cookies', 1.4, [
        ('say', 'kitty', "Meow! I made cookies for the party!"),
        ('wait', 0.5),
        *chant(['pip', 'kitty'], 6),
        ('wait', 0.5),
        ('say', 'kitty', "Six cookies!"),
        ('wait', 1.3)]),
    ('s11', 'Seven colors', 1.6, [
        ('cue', 'rainbow'),
        ('say', 'pip', "Look! A rainbow has seven colors!"),
        ('wait', 0.5),
        *chant(FRIENDS, 7),
        ('wait', 1.5)]),
    ('s12', 'Eight blocks', 1.2, [
        ('say', 'froggy', "Ribbit! Let's build a tall tower!"),
        ('wait', 0.5),
        *[b for i in range(8) for b in (('cue', f'n{i + 1}'), ('say', 'pip', NUM[i].capitalize() + ('!' if i == 7 else ',')), ('wait', 0.4))],
        ('cue', 'wobble'), ('wait', 1.2), ('cue', 'clap'), ('wait', 0.4),
        ('say', 'froggy', "Eight blocks!"),
        ('wait', 1.3)]),
    ('s13', 'Jump and count', 1.0, [
        ('say', 'pip', "Can you jump with us?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        *chant(CREW, 10, last=[('cue', 'jump')]),
        ('wait', 1.4)]),
    ('s14', 'Sunset', 1.8, [
        ('say', 'birdie', "Tweet! The sun is going to sleep!"),
        ('wait', 0.5),
        ('say', 'pip', "It's time for Lumi's party!"),
        ('wait', 1.4)]),
    ('s15', "Lumi's star party", 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello, friends! Welcome to my star party!"),
        ('wait', 0.5),
        ('all', CREW, "Hello, Lumi!"),
        ('wait', 1.4)]),
    ('s16', 'Nine star friends', 1.0, [
        ('say', 'lumi', "My star friends are coming! Let's count them!"),
        ('wait', 0.5),
        *chant(['pip', 'lumi'], 9),
        ('wait', 0.5),
        ('say', 'lumi', "Nine star friends!"),
        ('wait', 1.3)]),
    ('s17', 'Lumi makes ten', 1.0, [
        ('say', 'pip', "Nine stars and Lumi. How many stars now?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'n10'), ('all', CREW + ['lumi'], "Ten!"),
        ('wait', 0.4), ('cue', 'sparkle'),
        ('say', 'lumi', "Ten stars!"),
        ('wait', 1.3)]),
    ('s18', 'Ten fingers', 1.0, [
        ('say', 'pip', "Wiggle your fingers! Let's count them!"),
        ('wait', 0.5),
        ('say', 'pip', "One, two, three, four, five, six, seven, eight, nine, ten!"), *count(10),
        ('wait', 0.5),
        ('say', 'pip', "You have ten fingers!"),
        ('wait', 1.3)]),
    ('s19', 'Find number five', 1.0, [
        ('say', 'pip', "Which one is number five?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "Yes! The blue five!"),
        ('wait', 1.4)]),
    ('s20', 'Find number ten', 1.0, [
        ('say', 'pip', "Can you find number ten?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "Yes! The gold ten!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'lumi', "Hooray!"),
        ('wait', 1.2)]),
    ('s21', 'One more time', 1.0, [
        ('say', 'pip', "Let's count to ten one more time!"),
        ('wait', 0.6),
        *chant(ALL + ['sunny'], 10),
        ('wait', 0.3), ('cue', 'clap'),
        ('wait', 1.6)]),
    ('s22', 'Counting recap', 0.9, [
        ('say', 'pip', "One bus, two balloons, three fish, four hops!"), *count(4, 'r'),
        ('wait', 0.7),
        ('say', 'pip', "Five apples, six cookies, seven colors!"), *count(7, 'r', 5),
        ('wait', 0.7),
        ('say', 'pip', "Eight blocks, nine stars, and ten with Lumi!"), *count(10, 'r', 8),
        ('wait', 1.4)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for counting with us!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "You counted all the way to ten!"),
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
