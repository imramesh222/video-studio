"""Frames + wall-clock times -> a constant 30 fps clip: python3 clip.py <name>..."""
import json, subprocess, sys, os
for name in sys.argv[1:]:
    d = os.path.join('clips', name)
    m = json.load(open(os.path.join(d, 'meta.json')))
    frames, t0, t_end = m['frames'], m['t0'], m['tEnd']
    lines = []
    for i, (f, t) in enumerate(frames):
        start = t0 if i == 0 else t  # the first frame covers the very start
        nxt = frames[i + 1][1] if i + 1 < len(frames) else t_end
        lines += [f"file '{f}'", f"duration {max(nxt - start, 1) / 1000:.4f}"]
    lines.append(f"file '{frames[-1][0]}'")
    open(os.path.join(d, 'list.txt'), 'w').write('\n'.join(lines) + '\n')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(d, 'list.txt'),
                    '-vf', 'scale=1920:1080:flags=lanczos,fps=30,format=yuv420p', '-c:v', 'libx264', '-crf', '16',
                    '-preset', 'medium', os.path.join('clips', f'{name}.mp4')], check=True)
    print(name, subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                os.path.join('clips', f'{name}.mp4')], capture_output=True, text=True).stdout.strip())
