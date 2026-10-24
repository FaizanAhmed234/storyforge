"""01 - Story Intelligence Engine (long-form, scroll-stopping)."""
from llm import ask_json

MIN_WORDS = 175

SYSTEM = """You are an award-winning screenwriter of short cinematic stories for vertical video.
Each story is narrated and runs 80-90 seconds: 190-230 spoken words in total.

RULES
- HOOK: Scene 1 must stop the scroll within the first 8 words: a shocking
  statement, an impossible situation, or a sharp question. Never start with
  "Once upon a time" or a slow setup.
- LANGUAGE: moderate, natural spoken English that a teenager understands.
  Short punchy sentences mixed with a few longer ones. Use vivid, impactful
  words (shatter, hollow, relentless, vanish, defy) but no jargon, no rare
  vocabulary, no vague poetry. It should sound human and authentic.
- STORY: one clear main character with a real want, rising tension, a turning
  point, one twist that changes how we see everything before it, and a final
  line that hits like a gut-punch and echoes the opening.
- CONNECTED: every scene continues directly from the previous one with clear
  cause and effect. Keep names, places and details consistent.
- Original, thought-provoking, emotionally real. No cliches, no copyrighted
  characters, no real people.
- The last scene leaves the viewer with a haunting question or idea they will
  want to comment on or rewatch.
- VISUALS: in EVERY visual_prompt repeat the main character's fixed look (age,
  hair, clothes) and the setting, so images stay consistent across scenes.

Return ONLY JSON:
{"title": str, "logline": str, "theme": str, "twist": str, "ending": str,
 "scenes": [{"narration": str (16-24 words), "visual_prompt": str,
 "camera": str, "transition": str, "mood": str}]}
Exactly 10 scenes."""

def _words(story):
    return sum(len(s["narration"].split()) for s in story.get("scenes", []))

def generate_story(past_titles=(), theme_hint: str = "") -> dict:
    user = (f"Theme hint: {theme_hint or 'surprise me'}.\n"
            f"Avoid these past titles/concepts: {list(past_titles)[-30:]}")
    best = None
    for attempt in range(3):
        story = ask_json(SYSTEM, user)
        n = _words(story)
        print(f"Story attempt {attempt+1}: {n} words, {len(story['scenes'])} scenes")
        if best is None or n > _words(best):
            best = story
        if n >= MIN_WORDS and len(story["scenes"]) >= 9:
            return story
        user += (f"\nYour last draft had only {n} words. Rewrite it fuller: "
                 "10 scenes, each narration 18-24 words, 200+ words total.")
    return best
