"""Narration over the finished segments -> gymbhai-demo-voice.mp4.

Run compose.py first (it makes segments/). Each line starts at its moment in
the scene, or after the line before it; a scene that is too short for its
lines holds its last frame until they finish.
"""
import asyncio, json, os, subprocess, sys

import edge_tts

os.chdir(os.path.dirname(os.path.abspath(__file__)))
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'en-IN-NeerjaExpressiveNeural'
NE = VOICE.startswith('ne-')
OUT = sys.argv[2] if len(sys.argv) > 2 else f"gymbhai-demo-voice-{VOICE.split('-')[2].replace('Neural', '').lower()}.mp4"
SEG = 'segments-ne' if NE else 'segments'
LINES = f'voice-{VOICE}'
FADE = 0.4
GAP = 0.25  # between two lines
TAIL = 0.6  # after a scene's last line, before the cut

marks = lambda name: json.load(open(f'clips/{name}/meta.json'))['marks']
today, add = marks('today'), marks('add')
SPLIT = {'app2': 8.0, 'app3': 22.2, 'app4': 29.8}  # printed by compose.py

# (scene, seconds into the scene, what is said). Spelled for the voice.
SCRIPT = [
    ('title', 0.3, "Meet Gym Bhai: gym software, made for Nepal."),
    ('landing', 0.4, "Memberships, payments and check-ins for your gym, all in one place."),
    ('today', 0.3, "Open Gym Bhai and see your day at a glance: check-ins, money collected, and who owes you."),
    ('today', today['today2'], "Your to-do list shows payments to approve, and members to call back."),
    ('members', 0.3, "One tap shows who is expiring this week, who has expired, and who owes you money."),
    ('add', 0.3, "Adding a member is one form: their details, their plan, and the first payment."),
    ('add', add['add2'], "Cash, e-Sewa, Khalti, Phone-pay or bank: the money comes straight to you."),
    ('add', add['add3'], "Every payment gets a receipt you can print or share."),
    ('door', 0.3, "At the door, members show their QR code, or the desk finds them by name."),
    ('split', 0.3, "Every member gets your gym's own app, with their membership and a personal QR code."),
    ('split', SPLIT['app2'], "When it's time to renew, they pick a plan on their phone, pay your e-Sewa or bank QR, and send the transaction ID."),
    ('split', 17.3, "Then one tap on: I've paid."),
    ('split', SPLIT['app3'], "The request reaches your desk instantly. Check your wallet, then approve."),
    ('split', SPLIT['app4'], "And their membership is renewed. Nobody had to queue at the desk."),
    ('reports', 0.3, "Every month, Gym Bhai works out your income, expenses, profit and renewal rate."),
    ('nepali', 0.3, "And all of it works in Nepali, with Bikram Sambat dates."),
    ('end', 0.4, "Gym Bhai. Run your gym, not a register. Try it free for fourteen days."),
]
# Nepali: the app's own words (ne.json); names spelled as they are said.
SCRIPT_NE = [
    ('title', 0.3, "जिमभाइ। नेपालका जिमका लागि बनाइएको सफ्टवेयर।"),
    ('landing', 0.4, "सदस्यता, भुक्तानी र चेक-इन, सबै एकै ठाउँमा।"),
    ('today', 0.3, "जिमभाइ खोल्नुहोस्, र आजको सबै कुरा एकै नजरमा: कति जना आए, कति पैसा उठ्यो, र कसको बाँकी छ।"),
    ('today', today['today2'], "स्वीकृत गर्नुपर्ने भुक्तानी र फोन गर्नुपर्ने सदस्यहरूको सूची पनि यहीँ छ।"),
    ('members', 0.3, "एकै ट्यापमा हेर्नुहोस्: कसको सदस्यता यो हप्ता सकिँदैछ, कसको सकियो, र कसले तिर्न बाँकी छ।"),
    ('add', 0.3, "नयाँ सदस्य थप्न एउटै फारम: विवरण, प्लान र पहिलो भुक्तानी, सबै सँगै।"),
    ('add', add['add2'], "नगद, इसेवा, खल्ती, फोनपे वा बैंक: पैसा सिधै तपाईंकहाँ आउँछ।"),
    ('add', add['add3'], "हरेक भुक्तानीको रसिद, छाप्न वा सेयर गर्न तयार।"),
    ('door', 0.3, "ढोकामा सदस्यले आफ्नो क्यूआर कोड देखाउँछन्, वा काउन्टरबाट नामले खोजिन्छ।"),
    ('split', 0.3, "हरेक सदस्यले तपाईंको जिमको आफ्नै एप पाउँछन्, सदस्यता र आफ्नै क्यूआर कोडसहित।"),
    ('split', SPLIT['app2'], "नवीकरणको बेला, फोनबाटै प्लान छान्छन्, तपाईंको इसेवा वा बैंकको क्यूआरमा तिर्छन्, र ट्रान्जेक्सन आईडी पठाउँछन्।"),
    ('split', 17.3, "अनि, मैले तिरें, मा एक ट्याप।"),
    ('split', SPLIT['app3'], "अनुरोध तुरुन्तै तपाईंको काउन्टरमा आइपुग्छ। वालेट हेर्नुहोस्, अनि स्वीकृत गर्नुहोस्।"),
    ('split', SPLIT['app4'], "सदस्यता नवीकरण भयो। कोही काउन्टरमा लाइन बस्नु परेन।"),
    ('reports', 0.3, "हरेक महिनाको आम्दानी, खर्च, नाफा र नवीकरण दर, जिमभाइ आफैं हिसाब गर्छ।"),
    ('nepali', 0.3, "र यो सबै नेपाली र अंग्रेजी दुवैमा, विक्रम सम्वत् मितिसहित।"),
    ('end', 0.4, "जिमभाइ। रजिस्टर होइन, आफ्नो जिम चलाउनुहोस्। चौध दिन निःशुल्क प्रयोग गर्नुहोस्।"),
]
if NE:
    SCRIPT = SCRIPT_NE
SCENES = ['title', 'landing', 'today', 'members', 'add', 'door', 'split', 'reports', 'nepali', 'end']


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def duration(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                capture_output=True, text=True).stdout)


async def speak():
    os.makedirs(LINES, exist_ok=True)
    for i, (_, _, text) in enumerate(SCRIPT):
        await edge_tts.Communicate(text, VOICE, rate='+0%' if NE else '+4%').save(f'{LINES}/{i:02d}.mp3')

asyncio.run(speak())

# Place the lines inside their scenes; lengthen scenes that need it.
length = {s: duration(f'{SEG}/{s}.mp4') for s in SCENES}
need = dict(length)
placed, last_end = [], {}
for i, (scene, at, _) in enumerate(SCRIPT):
    start = max(at, last_end.get(scene, -GAP) + GAP)
    end = start + duration(f'{LINES}/{i:02d}.mp3')
    last_end[scene] = end
    placed.append((i, scene, start))
    need[scene] = max(need[scene], end + TAIL + (FADE if scene != 'end' else 0.8))

offsets, t = {}, 0.0
for s in SCENES:
    offsets[s] = t
    t += need[s] - FADE
total = t + FADE

for s in SCENES:
    if need[s] > length[s] + 0.01:
        print(f'{s}: held {need[s] - length[s]:.1f}s longer for the voice')

# Video: the same crossfades as compose.py, with held scenes padded.
args, f = [], []
for i, s in enumerate(SCENES):
    args += ['-i', f'{SEG}/{s}.mp4']
    f.append(f'[{i}:v]tpad=stop_mode=clone:stop_duration={need[s] - length[s] + 0.05:.3f},'
             f'trim=0:{need[s]:.3f},setpts=PTS-STARTPTS[s{i}]')
prev = 's0'
for i in range(1, len(SCENES)):
    f.append(f'[{prev}][s{i}]xfade=transition=fade:duration={FADE}:offset={offsets[SCENES[i]]:.3f}[x{i}]')
    prev = f'x{i}'
f.append(f'[{prev}]fade=in:st=0:d=0.5,fade=out:st={total - 0.8:.3f}:d=0.8,format=yuv420p[vout]')

# Audio: each line at its moment, mixed and levelled.
n = len(SCENES)
for k, (i, scene, start) in enumerate(placed):
    args += ['-i', f'{LINES}/{i:02d}.mp3']
    ms = int((offsets[scene] + start) * 1000)
    f.append(f'[{n + k}:a]aresample=48000,adelay={ms}|{ms}[a{k}]')
f.append(''.join(f'[a{k}]' for k in range(len(placed))) +
         f'amix=inputs={len(placed)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,'
         f'apad,atrim=0:{total:.3f}[aout]')

run([*args, '-filter_complex', ';'.join(f), '-map', '[vout]', '-map', '[aout]',
     '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
     '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', OUT])
print('total', round(duration(OUT), 1), 's ->', OUT)
