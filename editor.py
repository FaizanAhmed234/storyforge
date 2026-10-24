import os, re, random, glob, subprocess
from config import CFG

def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-1500:])

def _t(x):
    cs = int(round(x * 100))
    return f"{cs//360000}:{cs%360000//6000:02}:{cs%6000//100:02}.{cs%100:02}"

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,80,&H000AD6FF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,2,0,1,7,3,2,60,60,520,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def _events(text, start, dur, per=3):
    words = [re.sub(r"[{}\\]", "", w).upper() for w in text.split()]
    words = [w for w in words if w]
    if not words:
        return []
    wts = [len(w) + 2 for w in words]
    tot, t, times = sum(wts), start, []
    for wt in wts:
        d = dur * wt / tot
        times.append((t, d))
        t += d
    out = []
    for i in range(0, len(words), per):
        ch = list(zip(words[i:i+per], times[i:i+per]))
        s = ch[0][1][0]
        e = ch[-1][1][0] + ch[-1][1][1]
        body = "".join(f"{{\\k{max(1, int(d*100))}}}{w} " for w, (st, d) in ch).strip()
        fx = "{\\fad(60,60)\\fscx88\\fscy88\\t(0,140,\\fscx100\\fscy100)}"
        out.append(f"Dialogue: 0,{_t(s)},{_t(e)},Cap,,0,0,0,,{fx}{body}")
    return out

def assemble(scenes, out_path: str, wd: str) -> str:
    W, H, FPS = CFG.width, CFG.height, CFG.fps
    segs, ev, t = [], [], 0.0
    for sc in scenes:
        seg = f"{wd}/seg_{sc.idx}.mp4"
        d = sc.duration + 0.3
        n = int(d * FPS)
        z = f"1+0.22*on/{n}" if sc.idx % 2 == 0 else f"1.22-0.22*on/{n}"
        vf = (f"scale={W*2}:{H*2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},vignette=PI/5,"
              f"fade=t=in:d=0.25,fade=t=out:st={d-0.25:.2f}:d=0.25,format=yuv420p")
        _run(["ffmpeg", "-y", "-i", sc.image, "-i", sc.audio, "-t", f"{d:.2f}",
              "-vf", vf, "-af", "apad", "-shortest", "-c:v", "libx264",
              "-preset", "veryfast", "-crf", "20", "-c:a", "aac",
              "-ar", "44100", "-ac", "2", seg])
        segs.append(seg)
        ev += _events(sc.narration, t, sc.duration)
        t += d
    lst, ass, joined = f"{wd}/list.txt", f"{wd}/subs.ass", f"{wd}/joined.mp4"
    open(lst, "w").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
    open(ass, "w").write(HEADER + "\n".join(ev) + "\n")
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    sub = f"ass={ass}"
    tracks = glob.glob(f"{CFG.music_dir}/*.mp3")
    if tracks:
        _run(["ffmpeg", "-y", "-i", joined, "-stream_loop", "-1", "-i", random.choice(tracks),
              "-filter_complex",
              f"[0:v]{sub}[v];[1:a]volume=0.35[m];"
              "[m][0:a]sidechaincompress=threshold=0.03:ratio=8[d];"
              "[0:a][d]amix=inputs=2:duration=first[a]",
              "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20",
              "-c:a", "aac", "-shortest", out_path])
    else:
        _run(["ffmpeg", "-y", "-i", joined, "-vf", sub, "-c:v", "libx264",
              "-crf", "20", "-c:a", "copy", out_path])
    return out_path
