"""04 - Editor: animate stills (Ken Burns), add narration, music, subtitles -> vertical MP4."""
import os, random, glob, subprocess
from config import CFG

def _run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode: raise RuntimeError(p.stderr[-1500:])

def _ts(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02}:{m:02}:{s:06.3f}".replace(".", ",")

def assemble(scenes, out_path: str, wd: str) -> str:
    W, H, FPS = CFG.width, CFG.height, CFG.fps
    segs, srt, t = [], [], 0.0
    for sc in scenes:
        seg = f"{wd}/seg_{sc.idx}.mp4"
        d = sc.duration + 0.3
        n = int(d * FPS)
        z = (f"1+0.22*on/{n}" if sc.idx % 2 == 0 else f"1.22-0.22*on/{n}")
        vf = (f"scale={W*2}:{H*2},zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
              f"fade=t=in:d=0.25,fade=t=out:st={d-0.25:.2f}:d=0.25,format=yuv420p")
        _run(["ffmpeg", "-y", "-i", sc.image, "-i", sc.audio, "-t", f"{d:.2f}",
              "-vf", vf, "-af", "apad", "-shortest", "-c:v", "libx264",
              "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-ar", "44100",
              "-ac", "2", seg])
        segs.append(seg)
        srt.append(f"{sc.idx+1}\n{_ts(t)} --> {_ts(t+sc.duration)}\n{sc.narration}\n")
        t += d
    lst, srt_path, joined = f"{wd}/list.txt", f"{wd}/subs.srt", f"{wd}/joined.mp4"
    open(lst, "w").write("".join(f"file '{os.path.abspath(s)}'\n" for s in segs))
    open(srt_path, "w").write("\n".join(srt))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])

    style = ("FontName=DejaVu Sans,FontSize=15,Bold=1,PrimaryColour=&H00FFFFFF,"
             "OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=200")
    sub = f"subtitles={srt_path}:force_style='{style}'"
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