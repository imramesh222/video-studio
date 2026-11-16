"""Rainbow Rescue Bus, episode 4 (Opposites): voices, word timings and the timeline.

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


# Word cues: 'a' is the first word of the pair (blue), 'b' its opposite (red).
# ('word', name, word, k) marks the k-th time the word is said in the last line; a 4th item on 'say' sets its loudness.
SCENES = [
    ('s01', 'Hello, friends', 3.6, [
        ('cue', 'pop'), ('wait', 0.4),
        ('say', 'pip', "Hello, friends! Today we are playing the opposite game!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Let's go!"),
        ('wait', 1.4)]),
    ('s02', 'Big and small', 1.2, [
        ('say', 'sunny', "I am big!"), ('word', 'a', 'big'),
        ('wait', 0.4),
        ('say', 'pip', "I am small!"), ('word', 'b', 'small'),
        ('wait', 0.5),
        ('say', 'pip', "Big and small are opposites!"),
        ('wait', 1.3)]),
    ('s03', 'Which one is big?', 1.2, [
        ('say', 'kitty', "Meow! Which balloon is big?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Yes! This balloon is big!"), ('word', 'a', 'big'),
        ('wait', 0.4),
        ('say', 'kitty', "And this balloon is small!"), ('word', 'b', 'small'),
        ('wait', 1.3)]),
    ('s04', 'Up and down', 1.2, [
        ('say', 'kitty', "My balloon goes up!"), ('word', 'a', 'up'),
        ('wait', 0.3),
        ('say', 'pip', "Up, up, up!"), ('word', 'u1', 'up', 0), ('word', 'u2', 'up', 1), ('word', 'u3', 'up', 2),
        ('wait', 0.5),
        ('say', 'pip', "And down it comes. Down, down, down."),
        ('word', 'b', 'down', 0), ('word', 'd1', 'down', 1), ('word', 'd2', 'down', 2), ('word', 'd3', 'down', 3),
        ('wait', 1.3)]),
    ('s05', 'Reach up, touch down', 1.0, [
        ('say', 'pip', "Can you reach up high?"), *ask(),
        ('cue', 'a'), ('all', ['pip', 'kitty'], "Up!"),
        ('wait', 0.9),
        ('cue', 'b'), ('all', ['pip', 'kitty'], "Down!"),
        ('wait', 1.4)]),
    ('s06', 'Fast and slow', 1.2, [
        ('say', 'sunny', "Now I go fast!"), ('word', 'a', 'fast'),
        ('wait', 0.4),
        ('say', 'pip', "Whee! Fast!"),
        ('wait', 0.8),
        ('say', 'sunny', "And now I go slow."), ('word', 'b', 'slow'),
        ('wait', 1.8)]),
    ('s07', 'Fast or slow?', 1.2, [
        ('say', 'ducky', "Quack! Look at me walk!"),
        ('wait', 0.5),
        ('say', 'pip', "Is Ducky fast or slow?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Ducky is slow!"), ('word', 'b', 'slow'),
        ('wait', 1.4)]),
    ('s08', 'In and out', 1.2, [
        ('say', 'ducky', "Quack! I jump in!"), ('word', 'a', 'in'),
        ('wait', 0.6),
        ('say', 'pip', "Ducky is in the water!"),
        ('wait', 0.5),
        ('say', 'ducky', "And I climb out!"), ('word', 'b', 'out'),
        ('wait', 1.4)]),
    ('s09', 'In or out?', 1.0, [
        ('cue', 'splash'),
        ('say', 'pip', "Is Ducky in or out?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Ducky is in!"), ('word', 'a', 'in'),
        ('wait', 1.4)]),
    ('s10', 'Loud and quiet', 1.2, [
        ('cue', 'ribbit'),
        ('say', 'froggy', "RIBBIT! That was loud!", 1.35), ('word', 'a', 'loud'),
        ('wait', 0.5),
        ('say', 'pip', "Shh. Now be quiet."), ('word', 'b', 'quiet'),
        ('wait', 0.6),
        ('cue', 'whisper'),
        ('say', 'froggy', "Ribbit.", 0.4),
        ('wait', 1.3)]),
    ('s11', 'Can you be quiet?', 1.0, [
        ('say', 'pip', "Can you whisper like Froggy?"), *ask(),
        ('say', 'pip', "So quiet!", 0.45), ('word', 'b', 'quiet'),
        ('wait', 0.7),
        ('cue', 'ribbit'),
        ('say', 'froggy', "RIBBIT! So loud!", 1.35), ('word', 'a', 'loud'),
        ('wait', 1.4)]),
    ('s12', 'Open and closed', 1.2, [
        ('say', 'froggy', "My box is closed."), ('word', 'b', 'closed'),
        ('wait', 0.5),
        ('say', 'pip', "Let's open it!"),
        ('wait', 0.2), ('cue', 'open'), ('wait', 0.9),
        ('say', 'froggy', "Now it is open! Cookies!"), ('word', 'a', 'open'),
        ('wait', 1.4)]),
    ('s13', 'Happy and sad', 1.2, [
        ('say', 'birdie', "Tweet. I have no cookie. I am sad."), ('word', 'b', 'sad'),
        ('wait', 0.5),
        ('say', 'pip', "Here is a cookie for you!"),
        ('cue', 'give'), ('wait', 0.7),
        ('say', 'birdie', "Tweet tweet! Now I am happy!"), ('word', 'a', 'happy'),
        ('wait', 1.4)]),
    ('s14', 'Happy or sad?', 1.0, [
        ('say', 'pip', "Is Birdie happy or sad?"), *ask(),
        ('cue', 'found'),
        ('say', 'pip', "Birdie is happy!"), ('word', 'a', 'happy'),
        ('wait', 1.4)]),
    ('s15', 'The opposite dance', 1.0, [
        ('say', 'pip', "Let's do the opposite dance!"),
        ('wait', 0.6),
        ('cue', 'u'), ('all', CREW, "Up!"), ('wait', 0.8),
        ('cue', 'd'), ('all', CREW, "Down!"), ('wait', 0.9),
        ('cue', 'f'), ('all', CREW, "Fast!"), ('wait', 1.3),
        ('cue', 's'), ('all', CREW, "Slow!"),
        ('wait', 2.0)]),
    ('s16', 'Sunset', 1.8, [
        ('say', 'birdie', "Tweet! Look at the sun!"),
        ('wait', 0.5),
        ('say', 'pip', "The day is almost over."), ('word', 'a', 'day'),
        ('wait', 1.5)]),
    ('s17', 'Day and night', 2.4, [
        ('cue', 'land'),
        ('say', 'lumi', "Hello, friends! Now it is night!"), ('word', 'b', 'night'),
        ('wait', 0.6),
        ('say', 'pip', "Day and night are opposites!"), ('word', 'a', 'day'),
        ('wait', 1.5)]),
    ('s18', "Lumi's game: big or small", 1.0, [
        ('say', 'lumi', "Which star is small?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! This star is small!"),
        ('wait', 1.4)]),
    ('s19', "Lumi's game: up or down", 1.0, [
        ('say', 'lumi', "Which balloon is up?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! This balloon is up!"),
        ('wait', 1.4)]),
    ('s20', "Lumi's game: open or closed", 1.0, [
        ('say', 'lumi', "Which box is open?"), *ask(),
        ('cue', 'found'),
        ('say', 'lumi', "Yes! This box is open!"),
        ('wait', 0.3), ('cue', 'jump'),
        ('say', 'pip', "Hooray!"),
        ('wait', 1.2)]),
    ('s21', 'Say the opposite', 1.0, [
        ('cue', 'a1'), ('say', 'pip', "Big!"), ('wait', 0.45), ('cue', 'b1'), ('all', ALL + ['sunny'], "Small!"), ('wait', 0.9),
        ('cue', 'a2'), ('say', 'pip', "Up!"), ('wait', 0.45), ('cue', 'b2'), ('all', ALL + ['sunny'], "Down!"), ('wait', 0.9),
        ('cue', 'a3'), ('say', 'pip', "Fast!"), ('wait', 0.45), ('cue', 'b3'), ('all', ALL + ['sunny'], "Slow!"),
        ('wait', 0.5), ('cue', 'clap'),
        ('wait', 1.6)]),
    ('s22', 'Opposites recap', 0.9, [
        ('say', 'pip', "Big and small. Up and down. Fast and slow."),
        ('word', 'p1a', 'big'), ('word', 'p1b', 'small'), ('word', 'p2a', 'up'), ('word', 'p2b', 'down'), ('word', 'p3a', 'fast'), ('word', 'p3b', 'slow'),
        ('wait', 0.7),
        ('say', 'pip', "In and out. Loud and quiet."),
        ('word', 'p4a', 'in'), ('word', 'p4b', 'out'), ('word', 'p5a', 'loud'), ('word', 'p5b', 'quiet'),
        ('wait', 0.7),
        ('say', 'pip', "Open and closed. Happy and sad. Day and night!"),
        ('word', 'p6a', 'open'), ('word', 'p6b', 'closed'), ('word', 'p7a', 'happy'), ('word', 'p7b', 'sad'), ('word', 'p8a', 'day'), ('word', 'p8b', 'night'),
        ('wait', 1.5)]),
    ('s23', 'The ride home', 1.4, [
        ('say', 'pip', "Thank you for playing with us!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "Beep beep! Time to go home!"),
        ('wait', 1.6)]),
    ('s24', 'Goodnight, friends', 1.4, [
        ('say', 'lumi', "You know so many opposites!"),
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
