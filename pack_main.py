"""Story-pack mode: automated script + narration + caption. Visuals are made by hand."""
import os, re, sys, json, subprocess, datetime as dt
import story_engine, storyboard, voice, captions, publisher

GAP = 0.3
FENCE = "`" * 3

def ts(t):
    ms = int(round(t * 1000))
    return f"{ms//3600000:02}:{ms%3600000//60000:02}:{ms%60000//1000:02},{ms%1000:03}"

def make_pack():
    story = story_engine.generate_story(publisher.past_titles())
    scenes = storyboard.build_storyboard(story)
    cap = captions.make_caption(story)
    slug = re.sub(r"[^a-z0-9]+", "-", story["title"].lower()).strip("-")[:40] or "story"
    wd = f"packs/{dt.date.today().isoformat()}/{slug}"
    os.makedirs(wd, exist_ok=True)

    srt, parts, t = [], [], 0.0
    for sc in scenes:
        a = f"{wd}/scene_{sc.idx+1:02}.mp3"
        sc.duration = voice.narrate(sc.narration, a)
        padded = f"{wd}/_p{sc.idx}.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", a, "-af", f"apad=pad_dur={GAP}",
                        "-c:a", "libmp3lame", padded], check=True, capture_output=True)
        parts.append(padded)
        srt.append(f"{sc.idx+1}\n{ts(t)} --> {ts(t+sc.duration)}\n{sc.narration}\n")
        t += sc.duration + GAP

    lst = f"{wd}/_list.txt"
    open(lst, "w").write("".join(f"file '{os.path.abspath(p)}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-c:a", "libmp3lame", f"{wd}/full_narration.mp3"],
                   check=True, capture_output=True)
    for p in parts + [lst]:
        os.remove(p)

    open(f"{wd}/subtitles.srt", "w").write("\n".join(srt))
    json.dump({"story": story, "caption": cap}, open(f"{wd}/story.json", "w"), indent=1)

    tags = " ".join("#" + h for h in cap["hashtags"])
    md = [f"# {cap['title']}", "",
          f"**Opening hook text:** {cap['hook']}", "",
          "## Caption (tap copy)", "", FENCE, cap["caption"], "", tags, FENCE, "",
          f"Total length: about {t:.0f}s. Use full_narration.mp3 as your voice track.", "",
          "## Scenes", ""]
    for sc in scenes:
        md += [f"### Scene {sc.idx+1} (clip needs {sc.duration+GAP:.1f}s)",
               f"Narration: {sc.narration}", "",
               FENCE, sc.prompt + " Vertical 9:16.", FENCE, ""]
    open(f"{wd}/pack.md", "w").write("\n".join(md))
    publisher.log({"title": story["title"], "status": "pack"})
    print("Pack ready:", wd)

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    ok = 0
    for i in range(n):
        try:
            make_pack(); ok += 1
        except Exception as e:
            print(f"Pack {i+1} failed: {e}")
    sys.exit(0 if ok else 1)
