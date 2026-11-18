"""Lumi Land Shorts: a 30-45 s vertical clip (a question and its answer) cut from each finished episode.

The episode plays full width in the middle of a 1080x1920 frame, over a blurred, zoomed copy of itself,
with a big title at the top and "Full episode on Lumi Land" below. Times come from each episode's timeline,
so a clip always starts and ends on a scene change. Run: ../.venv/bin/python make_shorts.py
"""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
EPS = os.path.join(HERE, '..', 'cartoon-3d', 'episodes')
LL = os.path.expanduser('~/Downloads/Lumi Land')
OUT = os.path.join(LL, 'Shorts')
TMP = os.path.join(HERE, 'out')
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)

# episode folder, Downloads folder, scenes (first to last), title on screen (<br> breaks), colour, YouTube title
SHORTS = [
    ('ep01-learn-colors', 'Episode 01 - Learn Colors', 1, 's04', 's05', 'Find the<br>RED one!', '#e53935', 'Find the RED one! 🔴 Learn Colors for Toddlers'),
    ('ep02-shape-hunt', 'Episode 02 - The Shape Hunt', 2, 's04', 's05', 'Find the<br>CIRCLE!', '#e53935', 'Find the Circle! ⭕ Learn Shapes for Toddlers'),
    ('ep03-counting', 'Episode 03 - Counting 1 to 10', 3, 's08', 's09', 'How many<br>balls?', '#fb8c00', 'How Many Balls? 🔢 Counting for Toddlers'),
    ('ep04-opposites', 'Episode 04 - Opposites', 4, 's08', 's09', 'In or<br>OUT?', '#1e88e5', 'In or Out? 🦆 Learn Opposites for Toddlers'),
    ('ep05-fruit-picnic', 'Episode 05 - The Fruit Picnic', 5, 's12', 's13', 'What is<br>inside?', '#43a047', 'What Is Inside the Watermelon? 🍉 Learn Fruits for Toddlers'),
    ('ep06-weather-day', 'Episode 06 - The Weather Day', 6, 's15', 's16', 'Sun + rain<br>= ?', '#ec407a', 'Sun and Rain Make a... RAINBOW! 🌈 Weather for Toddlers'),
    ('ep07-touch-your-nose', 'Episode 07 - Touch Your Nose', 7, 's06', 's07', 'Touch your<br>NOSE!', '#ec407a', 'Can You Touch Your Nose? 👃 Body Parts for Toddlers'),
    ('ep08-things-that-go', 'Episode 08 - Things That Go', 8, 's08', 's09', 'Choo choo!<br>Count them!', '#43a047', 'Count the Train Cars! 🚂 Things That Go for Toddlers'),
    ('ep09-how-do-you-feel', 'Episode 09 - How Do You Feel', 9, 's04', 's05', 'A hug<br>helps!', '#1e88e5', 'Kitty Is Sad... A Hug Helps! 🤗 Feelings for Toddlers'),
    ('ep10-abc-a-to-h', 'Episode 10 - ABC with Pip (A to H)', 10, 's03', 's04', 'A is for<br>APPLE!', '#e53935', 'A Is for Apple! 🍎 ABC for Toddlers'),
]

items, jobs = [], []
for folder, dl, n, a, b, title, color, yt in SHORTS:
    T = json.load(open(os.path.join(EPS, folder, 'out', 'timeline.json')))
    S = {s['id']: s for s in T['scenes']}
    start, end = S[a]['start'] - 0.15, S[b]['start'] + S[b]['dur'] - 0.25
    if end - start > 58:
        end = start + 58
    sid = f'short-ep{n:02d}'
    items.append({'id': sid, 'title': title, 'color': color})
    jobs.append((sid, os.path.join(LL, dl, f'lumi-land-rainbow-rescue-bus-ep{n}.mp4'), start, end, yt, n, dl))
json.dump(items, open(os.path.join(TMP, 'list.json'), 'w'))
subprocess.run(['node', os.path.join(HERE, 'overlays.cjs'), os.path.join(TMP, 'list.json'), TMP], check=True, cwd=os.path.join(HERE, '..'))

notes = ['LUMI LAND SHORTS: one a day, same time. Each one: Made for kids · title below · description: the line under it.', '']
for sid, src, start, end, yt, n, dl in jobs:
    d = end - start
    out = os.path.join(OUT, f'{sid}.mp4')
    vf = (f"[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=24:2,eq=brightness=-0.05[bg];"
          f"[b]scale=1400:-2,crop=1080:ih[fg];[bg][fg]overlay=0:(H-h)/2-40[v1];[v1][1:v]overlay=0:0,"
          f"fade=in:st=0:d=0.3,fade=out:st={d - 0.5:.2f}:d=0.5,format=yuv420p[v]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{start:.2f}', '-t', f'{d:.2f}', '-i', src, '-i', os.path.join(TMP, sid + '.png'),
                    '-filter_complex', vf, '-map', '[v]', '-map', '0:a', '-af', f'afade=in:d=0.3,afade=out:st={d - 0.5:.2f}:d=0.5',
                    '-c:v', 'libx264', '-crf', '19', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out], check=True)
    notes += [f'{sid}.mp4  ({d:.0f} s)', f'Title: {yt} #shorts',
              f'Description: Watch the full episode "{dl.split(" - ", 1)[1]}" on Lumi Land! Pip the panda and Sunny the bus help toddlers learn. #shorts #toddlerlearning #kidsvideos', '']
    print(sid, f'{d:.1f}s')
open(os.path.join(OUT, 'shorts-details.txt'), 'w').write('\n'.join(notes))
