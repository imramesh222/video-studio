"""Clips + layers -> gymbhai-demo.mp4 (1920x1080, 30 fps)."""
import json, os, subprocess

os.chdir(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open('layout.json'))
# LANG_CODE=ne: Nepali layers into segments-ne/.
NE = os.environ.get('LANG_CODE') == 'ne'
LAYERS = 'layers-ne' if NE else 'layers'
SEG = 'segments-ne' if NE else 'segments'
os.makedirs(SEG, exist_ok=True)
FADE = 0.4  # crossfade between scenes


def run(args):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], check=True)


def duration(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                         capture_output=True, text=True).stdout
    return float(out)


def still(png, d):
    return ['-loop', '1', '-framerate', '30', '-t', f'{d:.3f}', '-i', png]


def captions_filter(base, first_input, caps, d):
    """Overlay caption PNGs (inputs from first_input on), each fading in and out."""
    parts, cur = [], base
    for i, (_, start, end) in enumerate(caps):
        end = min(end, d)
        k = first_input + i
        parts.append(f'[{k}:v]format=rgba,fade=in:st={start:.2f}:d=0.25:alpha=1,'
                     f'fade=out:st={max(end - 0.3, start):.2f}:d=0.25:alpha=1[c{i}]')
        parts.append(f'[{cur}][c{i}]overlay=0:0[o{i}]')
        cur = f'o{i}'
    return parts, cur


def web(name, caps):
    clip = f'clips/{name}.mp4'
    d = duration(clip)
    w = L['web']
    args = [*still(f'{LAYERS}/bg-web.png', d), '-i', clip, *still(f'{LAYERS}/mask-web.png', d)]
    for cap, _, _ in caps:
        args += still(f'{LAYERS}/cap-{cap}.png', d)
    f = [f"[1:v]fps=30,scale={w['w']}:{w['h']}:flags=lanczos,format=rgba[v]",
         '[2:v]format=gray[m]', '[v][m]alphamerge[vm]',
         f"[0:v][vm]overlay={w['x']}:{w['y']}:shortest=1[b]"]
    parts, out = captions_filter('b', 3, caps, d)
    run([*args, '-filter_complex', ';'.join(f + parts) + f';[{out}]format=yuv420p[out]', '-map', '[out]',
         '-t', f'{d:.3f}', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', f'{SEG}/{name}.mp4'])
    return f'{SEG}/{name}.mp4'


def card(name, d):
    run([*still(f'{LAYERS}/{name}.png', d), '-vf', 'format=yuv420p', '-c:v', 'libx264', '-crf', '17',
         '-t', f'{d:.3f}', f'{SEG}/{name}.mp4'])
    return f'{SEG}/{name}.mp4'


def split():
    # Window on the shared clock (seconds from the start of both recordings),
    # with the typing stretch sped up.
    start, end = 14.0, 55.9
    fast_from, fast_to, speed = 22.0, 42.0, 1.6
    p, k = L['phone'], L['desk']
    win = end - start
    raw = f'{SEG}/split-raw.mp4'
    run([*still(f'{LAYERS}/bg-split.png', win), '-ss', f'{start}', '-t', f'{win}', '-i', 'clips/phone.mp4',
         '-ss', f'{start}', '-t', f'{win}', '-i', 'clips/desk.mp4',
         *still(f'{LAYERS}/mask-phone.png', win), *still(f'{LAYERS}/mask-desk.png', win),
         '-filter_complex', ';'.join([
             f"[1:v]fps=30,scale={p['w']}:{p['h']}:flags=lanczos,format=rgba[pv]", '[3:v]format=gray[pm]',
             '[pv][pm]alphamerge[pa]',
             f"[2:v]fps=30,scale={k['w']}:{k['h']}:flags=lanczos,format=rgba[dv]", '[4:v]format=gray[dm]',
             '[dv][dm]alphamerge[da]',
             f"[0:v][pa]overlay={p['x']}:{p['y']}:eof_action=repeat[b1]",
             f"[b1][da]overlay={k['x']}:{k['y']}:eof_action=repeat,format=yuv420p[out]"]),
         '-map', '[out]', '-t', f'{win:.3f}', '-c:v', 'libx264', '-crf', '14', raw])

    a, b = fast_from - start, fast_to - start
    timed = f'{SEG}/split-timed.mp4'
    run(['-i', raw, '-filter_complex',
         f'[0:v]trim=0:{a},setpts=PTS-STARTPTS[x];'
         f'[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{speed}[y];'
         f'[0:v]trim={b},setpts=PTS-STARTPTS[z];[x][y][z]concat=n=3:v=1[v];[v]fps=30[out]',
         '-map', '[out]', '-c:v', 'libx264', '-crf', '14', timed])

    def out_t(t):  # shared clock -> time in the edited scene
        t -= start
        if t <= a:
            return t
        if t <= b:
            return a + (t - a) / speed
        return a + (b - a) / speed + (t - b)

    log = {what: (when - 0) for when, what in json.load(open('clips/split-log.json'))}
    t0 = log['sim-start']
    arrived = out_t((log['desk: request arrived'] - t0) / 1000)
    approved = out_t((log['desk: approved'] - t0) / 1000)
    d = duration(timed)
    caps = [('app1', 0.2, a - 0.1), ('app2', a, arrived), ('app3', arrived + 0.1, approved + 0.6),
            ('app4', approved + 0.7, d)]
    args = ['-i', timed]
    for cap, _, _ in caps:
        args += still(f'{LAYERS}/cap-{cap}.png', d)
    parts, out = captions_filter('0:v', 1, caps, d)
    run([*args, '-filter_complex', ';'.join(parts) + f';[{out}]format=yuv420p[out]', '-map', '[out]',
         '-t', f'{d:.3f}', '-c:v', 'libx264', '-crf', '17', f'{SEG}/split.mp4'])
    print('split', round(d, 1), 'arrived', round(arrived, 1), 'approved', round(approved, 1))
    return f'{SEG}/split.mp4'


def marks(name):
    return json.load(open(f'clips/{name}/meta.json'))['marks']


today, add = marks('today'), marks('add')
BIG = 999
segments = [
    card('title', 3.4),
    web('landing', [('landing', 0.4, BIG)]),
    web('today', [('today1', 0.3, today['today2']), ('today2', today['today2'] + 0.1, BIG)]),
    web('members', [('members', 0.3, BIG)]),
    web('add', [('add1', 0.3, add['add2']), ('add2', add['add2'] + 0.1, add['add3']), ('add3', add['add3'] + 0.1, BIG)]),
    web('door', [('door', 0.3, BIG)]),
    split(),
    web('reports', [('reports', 0.3, BIG)]),
    web('nepali', [('nepali', 0.3, BIG)]),
    card('end', 5.0),
]

# Crossfade them together.
args, f, offset, prev = [], [], 0.0, '0:v'
for i, s in enumerate(segments):
    args += ['-i', s]
for i in range(1, len(segments)):
    offset += duration(segments[i - 1]) - FADE
    f.append(f'[{prev}][{i}:v]xfade=transition=fade:duration={FADE}:offset={offset:.3f}[x{i}]')
    prev = f'x{i}'
total = offset + duration(segments[-1])
f.append(f'[{prev}]fade=in:st=0:d=0.5,fade=out:st={total - 0.8:.3f}:d=0.8,format=yuv420p[out]')
run([*args, '-f', 'lavfi', '-t', f'{total:.3f}', '-i', 'anullsrc=r=48000:cl=stereo',
     '-filter_complex', ';'.join(f), '-map', '[out]', '-map', f'{len(segments)}:a',
     '-c:v', 'libx264', '-crf', '18', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
     '-c:a', 'aac', '-b:a', '64k', '-shortest', ('gymbhai-demo-ne.mp4' if NE else 'gymbhai-demo.mp4')])
print('total', round(duration(('gymbhai-demo-ne.mp4' if NE else 'gymbhai-demo.mp4')), 1), 's')
