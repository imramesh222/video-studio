"""Rainbow Rescue Bus (Hindi), the full episode: voices, word timings and the timeline.

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
    'pip': dict(voice='hi-IN-SwaraNeural', rate='-8%', pitch='+10Hz'),
    'sunny': dict(voice='hi-IN-MadhurNeural', rate='+0%', pitch='+8Hz'),
    'kitty': dict(voice='hi-IN-SwaraNeural', rate='-2%', pitch='+40Hz'),
    'ducky': dict(voice='hi-IN-SwaraNeural', rate='+8%', pitch='+60Hz'),
    'froggy': dict(voice='hi-IN-MadhurNeural', rate='+6%', pitch='+45Hz'),
    'birdie': dict(voice='hi-IN-SwaraNeural', rate='+12%', pitch='+85Hz'),
}
FRIENDS = ['kitty', 'ducky', 'froggy', 'birdie']

# Beats: ('say', who, text) · ('all', [who...], text) · ('wait', s) · ('cue', name)
# ('cue', name) marks "now"; ('word', name, word) marks a word in the last line.
SCENES = [
    ('s01', 'The big surprise', 3.6, [
        ('cue', 'pop'),
        ('wait', 0.4),
        ('say', 'pip', "नमस्ते दोस्तों! क्या आप मज़ेदार सफ़र के लिए तैयार हो?"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "बीप बीप! चलो चलें!"),
        ('wait', 1.4)]),
    ('s02', 'The rainbow road', 1.2, [
        ('say', 'pip', "वाह! देखो कितने सुंदर रंग!"),
        ('wait', 0.5),
        ('say', 'sunny', "चलो साथ में रंग सीखें!"),
        ('wait', 1.4)]),
    ('s03', 'The red flowers', 1.4, [
        ('say', 'pip', "देखो दोस्तों! Red! लाल!"), ('word', 'color', 'red'),
        ('wait', 0.7),
        ('say', 'pip', "क्या तुम Red बोल सकते हो?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'sparkle'),
        ('say', 'pip', "Red, Red, सुंदर Red!"),
        ('wait', 1.6)]),
    ('s04', 'Baby Kitty', 1.6, [
        ('say', 'pip', "नमस्ते, छोटी Kitty! क्या तुम कुछ ढूंढ रही हो?"),
        ('wait', 0.5),
        ('say', 'kitty', "म्याऊँ! मुझे मेरे Red फूल नहीं मिल रहे!"),
        ('wait', 0.5),
        ('say', 'pip', "चिंता मत करो! हम तुम्हारी मदद करेंगे!"),
        ('wait', 1.2)]),
    ('s05', 'Find the red', 1.0, [
        ('say', 'pip', "कौन सा फूल Red है?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "हाँ! Red फूल!"),
        ('wait', 0.5), ('cue', 'jump'),
        ('say', 'kitty', "म्याऊँ! धन्यवाद, Pip!"),
        ('wait', 1.2)]),
    ('s06', 'Count the red flowers', 1.0, [
        ('say', 'pip', "चलो साथ में गिनें!"),
        ('wait', 0.5), ('cue', 'n1'),
        ('say', 'pip', "One!"),
        ('wait', 0.45), ('cue', 'n2'),
        ('say', 'kitty', "Two!"),
        ('wait', 0.45), ('cue', 'n3'),
        ('say', 'pip', "Three!"),
        ('wait', 0.3), ('cue', 'clap'), ('wait', 1.0),
        ('say', 'pip', "तीन सुंदर Red फूल!"),
        ('wait', 1.3)]),
    ('s07', 'The yellow pond', 2.6, [
        ('say', 'pip', "वाह! ये फूल किस रंग के हैं?"),
        ('wait', 0.5),
        ('say', 'sunny', "ये Yellow हैं! पीले!"), ('word', 'color', 'yellow'),
        ('wait', 0.5),
        ('say', 'pip', "Yellow! Yellow! धूप जैसा Yellow!"),
        ('wait', 1.4)]),
    ('s08', 'Baby Ducky', 1.2, [
        ('say', 'ducky', "क्वैक क्वैक! मेरे Yellow फूल कहाँ हैं?"),
        ('wait', 0.5),
        ('say', 'pip', "नमस्ते Ducky! हम उन्हें ढूंढने में मदद करेंगे!"),
        ('wait', 0.2), ('cue', 'flap'), ('wait', 1.6)]),
    ('s09', 'Yellow matching game', 1.0, [
        ('say', 'pip', "क्या तुम कुछ Yellow ढूंढ सकते हो?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "हाँ! Yellow तारा!"),
        ('wait', 0.4), ('cue', 'jump'),
        ('say', 'ducky', "क्वैक! Yellow! Yellow!"),
        ('wait', 1.2)]),
    ('s10', "Ducky's happy dance", 1.0, [
        ('cue', 'dance'),
        ('say', 'pip', "चलो नाचें! Yellow, Yellow, ताली बजाओ!"),
        ('cue', 'clap'),
        ('wait', 3.6)]),
    ('s11', 'The green forest', 1.6, [
        ('say', 'pip', "देखो, कितना सारा Green! हरा!"), ('word', 'color', 'green'),
        ('wait', 0.5),
        ('say', 'sunny', "Green पेड़! Green पत्तियाँ! Green घास!"),
        ('wait', 1.4)]),
    ('s12', 'Baby Froggy', 1.0, [
        ('say', 'froggy', "रिबिट! रिबिट!"),
        ('wait', 0.4),
        ('say', 'pip', "नमस्ते Froggy! तुम यहाँ क्यों बैठे हो?"),
        ('wait', 0.5),
        ('say', 'froggy', "मैं अपनी Green पत्ती ढूंढ रहा हूँ!"),
        ('wait', 0.5),
        ('say', 'pip', "चलो साथ में ढूंढें!"),
        ('wait', 1.2)]),
    ('s13', 'Find the green', 1.0, [
        ('say', 'pip', "कौन सा Green है?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "Green पत्ती! तुमने ढूंढ लिया!"),
        ('wait', 0.4), ('cue', 'jump'),
        ('say', 'froggy', "रिबिट! बहुत बढ़िया!"),
        ('wait', 1.2)]),
    ('s14', 'Five little leaves', 1.6, [
        ('say', 'pip', "One, two, three, four, five!"),
        ('word', 'n1', 'one'), ('word', 'n2', 'two'), ('word', 'n3', 'three'), ('word', 'n4', 'four'), ('word', 'n5', 'five'),
        ('wait', 0.5),
        ('say', 'froggy', "पाँच Green पत्तियाँ!"),
        ('wait', 1.3)]),
    ('s15', 'The blue sky', 1.6, [
        ('say', 'pip', "वाह! आसमान को देखो!"),
        ('wait', 0.4),
        ('say', 'sunny', "आसमान किस रंग का है?"),
        ('wait', 0.5), ('cue', 'color'),
        ('say', 'pip', "Blue!"),
        ('wait', 2.0)]),
    ('s16', 'Baby Birdie', 1.0, [
        ('say', 'birdie', "ट्वीट! ट्वीट!"),
        ('wait', 0.4),
        ('say', 'pip', "नमस्ते Birdie! क्या तुम अपना Blue घर ढूंढ रही हो?"),
        ('wait', 0.5),
        ('say', 'birdie', "ट्वीट! हाँ!"),
        ('wait', 0.4),
        ('say', 'pip', "चलो मदद करें!"),
        ('wait', 1.2)]),
    ('s17', 'Find the blue', 1.0, [
        ('say', 'pip', "क्या तुम Blue ढूंढ सकते हो?"),
        ('cue', 'ask'), ('wait', 0.3), ('cue', 'answer'), ('wait', 2.0),
        ('cue', 'found'),
        ('say', 'pip', "हाँ! Blue तितली!"),
        ('wait', 0.4), ('cue', 'jump'),
        ('say', 'birdie', "ट्वीट! Blue! Blue!"),
        ('wait', 1.2)]),
    ('s18', 'All four friends', 1.2, [
        ('say', 'pip', "देखो! हमें सारे दोस्त मिल गए!"),
        ('wait', 0.4), ('cue', 'f1'),
        ('say', 'kitty', "म्याऊँ!"), ('wait', 0.25), ('cue', 'f2'),
        ('say', 'ducky', "क्वैक!"), ('wait', 0.25), ('cue', 'f3'),
        ('say', 'froggy', "रिबिट!"), ('wait', 0.25), ('cue', 'f4'),
        ('say', 'birdie', "ट्वीट!"),
        ('wait', 0.3), ('cue', 'laugh'), ('wait', 1.8)]),
    ('s19', 'The color parade', 1.0, [
        ('say', 'pip', "चलो अपने रंग याद करें!"),
        ('wait', 0.5), ('cue', 'c1'),
        ('say', 'kitty', "Red!"), ('wait', 0.35), ('cue', 'c2'),
        ('say', 'ducky', "Yellow!"), ('wait', 0.35), ('cue', 'c3'),
        ('say', 'froggy', "Green!"), ('wait', 0.35), ('cue', 'c4'),
        ('say', 'birdie', "Blue!"),
        ('wait', 1.5)]),
    ('s20', 'The color challenge', 1.0, [
        ('say', 'pip', "क्या तुम मेरे साथ सारे रंग बोलोगे?"),
        ('wait', 0.6),
        ('say', 'pip', "Red! Yellow! Green! Blue!"),
        ('word', 'c1', 'red'), ('word', 'c2', 'yellow'), ('word', 'c3', 'green'), ('word', 'c4', 'blue'),
        ('wait', 0.6),
        ('all', FRIENDS, "Red! Yellow! Green! Blue!"),
        ('word', 'd1', 'red'), ('word', 'd2', 'yellow'), ('word', 'd3', 'green'), ('word', 'd4', 'blue'),
        ('wait', 1.4)]),
    ('s21', 'The friendship tree', 1.4, [
        ('say', 'pip', "आज हमने रंग सीखे और दोस्तों की मदद की!"),
        ('wait', 0.5),
        ('say', 'kitty', "दोस्तों की मदद करना मज़ेदार है!"),
        ('wait', 0.4),
        ('say', 'ducky', "क्वैक! हम बहुत खुश हैं!"),
        ('wait', 1.4)]),
    ('s22', 'The happy bus ride', 1.4, [
        ('say', 'pip', "हमारे सफ़र में आने के लिए धन्यवाद!"),
        ('wait', 0.35), ('cue', 'horn'), ('wait', 0.15),
        ('say', 'sunny', "बीप बीप! फिर मिलेंगे!"),
        ('wait', 1.6)]),
    ('s23', 'Color recap', 0.9, [
        ('cue', 'r1'), ('say', 'pip', "Red, सेब जैसा!"), ('wait', 0.9),
        ('cue', 'r2'), ('say', 'pip', "Yellow, सूरज जैसा!"), ('wait', 0.9),
        ('cue', 'r3'), ('say', 'pip', "Green, पत्ती जैसा!"), ('wait', 0.9),
        ('cue', 'r4'), ('say', 'pip', "Blue, आसमान जैसा!"), ('wait', 1.2)]),
    ('s24', 'Goodbye friends', 1.4, [
        ('say', 'pip', "आज तुमने बहुत अच्छा किया!"),
        ('wait', 0.4),
        ('say', 'sunny', "सीखते रहो, मुस्कुराते रहो!"),
        ('wait', 0.4), ('cue', 'rainbow'),
        ('all', ['pip', 'sunny'] + FRIENDS, "बाय-बाय दोस्तों! फिर मिलेंगे!"),
        ('wait', 1.0), ('cue', 'thanks'), ('wait', 2.6), ('cue', 'subscribe'), ('wait', 3.4)]),
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
