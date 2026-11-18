"""A fast opening for an episode: a 5-second hook from its most exciting moment, then straight into the episode
(the 3-second title card is cut). Toddlers on phones leave in the first seconds; ep 1 kept only 21% at 0:30.

The finished MP4 in Downloads becomes the hooked one; the old one is kept as `…-slow-start.mp4`.
youtube-details.txt times move by the same amount, and the .srt is remade to match.
Run: .venv/bin/python shorts/add_hook.py 5 6 7 …"""
import glob, os, re, shutil, subprocess, sys

LL = os.path.expanduser('~/Downloads/Lumi Land')
TITLE = 3.0
# episode: (hook start, hook end) in the original video, seconds
HOOKS = {5: (116.9, 121.9), 6: (147.6, 152.6), 7: (62.9, 67.6), 8: (71.6, 76.6), 9: (129.9, 135.0), 10: (16.4, 21.4)}


def shift_details(path, offset):
    """Move every m:ss time in the chapters, problems and sounds lists by `offset` seconds (0:00 stays 0:00)."""
    def fix(m):
        t = int(m.group(1)) * 60 + int(m.group(2))
        if t == 0:
            return m.group(0)
        t = round(t + offset)
        return f'{t // 60}:{t % 60:02d}{m.group(3)}'
    out = []
    for line in open(path).read().split('\n'):
        out.append(re.sub(r'(?<![\d:])(\d{1,2}):(\d{2})(\s|$|,)', fix, line) if not line.startswith('Video:') else line)
    open(path, 'w').write('\n'.join(out))


def shift_srt(path, offset):
    def t2s(s):
        h, m, rest = s.split(':'); sec, ms = rest.split(',')
        return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000
    def s2t(x):
        return '%02d:%02d:%02d,%03d' % (x // 3600, x % 3600 // 60, x % 60, round(x % 1 * 1000) % 1000)
    txt = open(path).read()
    txt = re.sub(r'(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)', lambda m: f'{s2t(t2s(m.group(1)) + offset)} --> {s2t(t2s(m.group(2)) + offset)}', txt)
    open(path, 'w').write(txt)


for n in map(int, sys.argv[1:]):
    folder = glob.glob(os.path.join(LL, f'Episode {n:02d} - *'))[0]
    mp4 = os.path.join(folder, f'lumi-land-rainbow-rescue-bus-ep{n}.mp4')
    slow = mp4.replace('.mp4', '-slow-start.mp4')
    if not os.path.exists(slow):
        shutil.copy2(mp4, slow)
        shutil.copy2(os.path.join(folder, 'youtube-details.txt'), os.path.join(folder, 'youtube-details-slow-start.txt'))
        srt = os.path.join(folder, f'lumi-land-ep{n}-english.srt')
        if os.path.exists(srt): shutil.copy2(srt, srt.replace('.srt', '-slow-start.srt'))
    a, b = HOOKS[n]
    hook = b - a
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', slow], capture_output=True, text=True).stdout)
    rest = dur - TITLE
    fc = (f"[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fade=out:st={hook - 0.2}:d=0.2[hv];"
          f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=in:d=0.05,afade=out:st={hook - 0.25}:d=0.25[ha];"
          f"[0:v]trim={TITLE}:{dur},setpts=PTS-STARTPTS,fade=in:d=0.2[ev];"
          f"[0:a]atrim={TITLE}:{dur},asetpts=PTS-STARTPTS,afade=in:d=0.2[ea];"
          f"[hv][ha][ev][ea]concat=n=2:v=1:a=1[v][au]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', slow, '-filter_complex', fc, '-map', '[v]', '-map', '[au]',
                    '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ac', '2',
                    '-movflags', '+faststart', mp4], check=True)
    offset = hook - TITLE
    det = os.path.join(folder, 'youtube-details.txt')
    open(det, 'w').write(open(os.path.join(folder, 'youtube-details-slow-start.txt')).read())
    shift_details(det, offset)
    total = round(hook + rest)
    txt = open(det).read()
    txt = re.sub(r'^(Video: \S+ \()\d+:\d\d\)', lambda m: f'{m.group(1)}{total // 60}:{total % 60:02d})', txt, flags=re.M)
    txt = txt.replace('\n\nTITLE', f'\nOpening: a 5-second hook ({a:.0f}-{b:.0f} s of the episode), then the episode without its title card. All times below already include it.\n\nTITLE', 1)
    open(det, 'w').write(txt)
    srt = os.path.join(folder, f'lumi-land-ep{n}-english.srt')
    if os.path.exists(srt):
        open(srt, 'w').write(open(srt.replace('.srt', '-slow-start.srt')).read())
        shift_srt(srt, offset)
    print(f'ep{n}: hook {hook:.1f}s, times +{offset:.1f}s, length {total // 60}:{total % 60:02d}')
