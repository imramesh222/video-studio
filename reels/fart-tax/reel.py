"""The Fart Tax (vertical reel): narration, word timings and the timeline.

Like cartoon-3d's episode.py: each shot is a list of beats and the timeline follows the voice,
so the cuts land on the narration. Writes out/voice/*.mp3 and out/timeline.json.
"""
import asyncio, json, os, re, subprocess, sys, wave

import edge_tts
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'out')
os.makedirs(os.path.join(OUT, 'voice'), exist_ok=True)
FPS = 30
VOICES = {
    'toby': dict(voice='en-US-BrianNeural', rate='+8%', pitch='+0Hz'),       # dry, tired narrator
    'drone': dict(voice='en-US-ChristopherNeural', rate='+4%', pitch='-4Hz'),  # the loudspeaker (made tinny in sound.py)
}

# Beats: ('say', who, text) · ('wait', s) · ('cue', name) = now · ('word', name, word) = a word in the last line.
# Cue names: f1..fN a toot that costs $10 (the "−$10" lands 0.3 s later) · puff a toot that costs nothing.
SHOTS = [
    ('s01', 'street', 0.5, [('say', 'toby', "In this town, farting costs $10."), ('word', 'f1', 'costs'), ('wait', 0.6)]),
    ('s02', 'sniffers', 0.2, [('say', 'toby', "Sensors are everywhere."), ('wait', 0.15), ('cue', 'alarm'), ('wait', 0.7)]),
    ('s03', 'bus stop', 0.2, [('say', 'toby', "One tiny toot, and $10 disappears from your bank account."), ('word', 'f1', 'toot'), ('wait', 0.4)]),
    ('s04', 'beans', 0.3, [('say', 'toby', "My name is Toby, and last night I ate beans."), ('wait', 0.3),
                           ('cue', 'rumble'), ('say', 'toby', "Big mistake."), ('wait', 0.6)]),
    ('s05', 'bed', 0.2, [('say', 'toby', "I got out of bed."), ('wait', 0.15), ('cue', 'f1'), ('wait', 0.6),
                         ('say', 'toby', "Minus $10."), ('wait', 0.3)]),
    ('s06', 'shoe', 0.2, [('say', 'toby', "I tied my shoe."), ('wait', 0.15), ('cue', 'f1'), ('wait', 0.6),
                          ('say', 'toby', "Another $10."), ('wait', 0.3)]),
    ('s07', 'breakfast', 0.2, [('cue', 'f1'), ('wait', 0.4), ('cue', 'f2'), ('wait', 0.4), ('cue', 'f3'), ('wait', 0.35),
                               ('say', 'toby', "By breakfast, I was almost broke."), ('wait', 0.6)]),
    ('s08', 'rice', 0.2, [('say', 'toby', "People here got creative."), ('wait', 0.2), ('say', 'toby', "Some ate only plain rice."), ('wait', 0.4)]),
    ('s09', 'box', 0.2, [('say', 'toby', "One guy lived inside a soundproof box."), ('word', 'puff', 'soundproof'), ('wait', 0.5)]),
    ('s10', 'rich', 0.2, [('say', 'toby', "And the rich?"), ('wait', 0.15),
                          ('say', 'toby', "They farted all day, because $10 meant nothing to them."),
                          ('word', 'f1', 'farted'), ('word', 'f2', 'day'), ('word', 'f3', 'meant'), ('wait', 0.15), ('cue', 'f4'), ('wait', 0.5)]),
    ('s11', 'garage', 0.3, [('say', 'toby', "So I spent all night building the Silent Pants."), ('word', 'reveal', 'silent'), ('wait', 0.6)]),
    ('s12', 'silent', 0.3, [('cue', 'puff'), ('wait', 0.4), ('say', 'toby', "No sound."), ('wait', 0.15), ('say', 'toby', "No smell."), ('wait', 0.15),
                            ('say', 'toby', "No bill."), ('wait', 0.5)]),
    ('s13', 'town', 0.2, [('say', 'toby', "Soon the whole town was wearing them, and the government was losing millions."), ('word', 'chart', 'government'), ('wait', 0.6)]),
    ('s14', 'drones', 0.3, [('say', 'toby', "The next morning, drones filled the sky."), ('wait', 0.25), ('cue', 'sign'),
                            ('say', 'drone', "New rule! Pants without a license cost $1,000!"), ('wait', 0.6)]),
    ('s15', 'panic', 0.1, [('say', 'toby', "Everyone panicked."), ('wait', 0.1), ('cue', 'run'), ('say', 'toby', "One man ran home in his underwear."), ('wait', 0.4)]),
    ('s16', 'balloon', 0.2, [('say', 'toby', "My neighbor held it in so long, he floated away like a balloon."), ('word', 'float', 'floated'), ('wait', 0.9)]),
    ('s17', 'sofa', 0.2, [('say', 'toby', "Then I noticed something strange."), ('wait', 0.3)]),
    ('s18', 'mayor', 0.2, [('say', 'toby', "The mayor farted on live TV, and he wasn't charged a single dollar."),
                           ('word', 'puff', 'farted'), ('word', 'zero', 'dollar'), ('wait', 0.5)]),
    ('s19', 'follow', 0.3, [('say', 'toby', "That night, I followed his car"), ('wait', 0.25)]),
    ('s20', 'machine', 0.1, [('say', 'toby', "to a secret room under City Hall."), ('wait', 0.15),
                             ('say', 'toby', "Inside, a giant machine was sniffing the whole town."), ('word', 'sniff', 'sniffing'), ('wait', 0.4)]),
    ('s21', 'button', 0.2, [('say', 'toby', "And in the middle, a big red button."), ('wait', 0.15), ('say', 'toby', "Disable fart tax."), ('wait', 0.4)]),
    ('s22', 'press', 0.2, [('say', 'toby', "No guards."), ('wait', 0.1), ('say', 'toby', "No cameras."), ('wait', 0.3),
                           ('say', 'toby', "I pressed it."), ('word', 'press', 'pressed'), ('wait', 0.5)]),
    ('s23', 'green', 0.2, [('say', 'toby', "Every screen in town turned green."), ('word', 'green', 'turned'), ('wait', 0.6)]),
    ('s24', 'eruption', 0.2, [('say', 'toby', "And the whole town let go at once."), ('word', 'boom', 'once'), ('wait', 0.3),
                              ('say', 'toby', "It sounded like a thousand trumpets."), ('wait', 1.0)]),
    ('s25', 'hero', 0.2, [('say', 'toby', "I was a hero."), ('wait', 0.9)]),
    ('s26', 'phone', 0.3, [('say', 'toby', "But the next morning, my phone buzzed."), ('word', 'buzz', 'buzzed'), ('wait', 0.3),
                           ('cue', 'notif'), ('say', 'toby', "New tax: burping."), ('wait', 0.1), ('say', 'toby', "$20 each."), ('wait', 0.5)]),
    ('s27', 'soda', 0.3, [('say', 'toby', "I looked at the soda in my hand."), ('wait', 0.3), ('cue', 'hush'), ('wait', 0.7),
                          ('cue', 'talk'), ('say', 'toby', "You've got to be kidding me."), ('wait', 1.3)]),
]


async def speak(key, who, text):
    v = VOICES[who]
    path = os.path.join(OUT, 'voice', f'{key}.mp3')
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


def pcm(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 's16le', '-ac', '1', '-ar', '24000', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768


def trim(path, words):
    """Cut the silence the voice service leaves at both ends; shift the word times to match."""
    x = pcm(path)
    loud = np.nonzero(np.abs(x) > 0.012)[0]
    a = max(0, loud[0] - int(0.04 * 24000)) if len(loud) else 0
    b = min(len(x), loud[-1] + int(0.08 * 24000)) if len(loud) else len(x)
    x = x[a:b]
    out = path.replace('.mp3', '.wav')
    with wave.open(out, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    step = 24000 // FPS
    rms = [float(np.sqrt(np.mean(x[i:i + step] ** 2))) for i in range(0, len(x), step)]
    top = max(rms) or 1
    return out, [[t, round(max(0, o - a / 24000), 3)] for t, o in words], [round(min(1, r / top * 1.4), 3) for r in rms], len(x) / 24000


async def main():
    lines, shots, t = {}, [], 0.0
    for sid, name, lead, beats in SHOTS:
        start, u, cues, n, last = t, lead, {}, 0, None
        for b in beats:
            if b[0] == 'wait':
                u += b[1]
            elif b[0] == 'cue':
                cues[b[1]] = round(start + u, 3)
            elif b[0] == 'word':
                hit = next((w[1] for w in last['words'] if re.sub(r'\W', '', w[0].lower()) == b[2]), None)
                if hit is None:
                    sys.exit(f'{sid}: no word "{b[2]}" in "{last["text"]}"')
                cues[b[1]] = round(last['start'] + hit, 3)
            elif b[0] == 'say':
                n += 1
                key = f'{sid}_{n:02d}'
                path, words = await speak(key, b[1], b[2])
                path, words, env, dur = trim(path, words)
                lines[key] = last = dict(who=b[1], text=b[2], dur=round(dur, 3), words=words, env=env, start=round(start + u, 3), shot=sid)
                u += dur
        shots.append(dict(id=sid, name=name, start=round(start, 3), dur=round(u, 3), cues=cues))
        t += u
    total = round(t, 3)
    json.dump(dict(fps=FPS, total=total, shots=shots, lines=lines), open(os.path.join(OUT, 'timeline.json'), 'w'))
    for s in shots:
        print(f"{s['id']} {s['start']:6.2f} {s['dur']:5.2f}  {s['name']}")
    print('total', total, 's ·', len(lines), 'lines')

asyncio.run(main())
