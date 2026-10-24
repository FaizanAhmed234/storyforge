"""One run = one finished video, uploaded. GitHub Actions calls this 5x/day."""
import os, time, json, random
from concurrent.futures import ThreadPoolExecutor
from config import CFG
import story_engine, storyboard, image_gen, voice, editor, captions, publisher

def main():
    story = story_engine.generate_story(publisher.past_titles())
    scenes = storyboard.build_storyboard(story)
    wd = f"{CFG.out_dir}/{int(time.time())}"; os.makedirs(wd)
    seed = random.randint(1, 10**6)       # shared seed keeps the look consistent

    def do_scene(sc):
        sc.audio, sc.image = f"{wd}/a_{sc.idx}.mp3", f"{wd}/i_{sc.idx}.jpg"
        sc.duration = voice.narrate(sc.narration, sc.audio)
        image_gen.generate_image(sc.prompt, sc.image, seed)
    with ThreadPoolExecutor(max_workers=3) as ex:
        list(ex.map(do_scene, scenes))

    final = editor.assemble(scenes, f"{wd}/final.mp4", wd)
    cap = captions.make_caption(story)
    json.dump({"story": story, "caption": cap}, open(f"{wd}/meta.json", "w"), indent=1)
    status = publisher.publish(final, cap["title"], cap["caption"], cap["hashtags"])
    publisher.log({"title": story["title"], "status": status})
    print("Done:", story["title"], status)
    open(os.getenv("GITHUB_ENV", "/dev/null"), "a").write(f"VIDEO_DIR={wd}\n")

if __name__ == "__main__":
    main()