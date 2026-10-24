"""01 - Story Intelligence Engine."""
from llm import ask_json

SYSTEM = """You are an award-winning screenwriter of ultra-short cinematic stories
(45-60 seconds, narrated). Write ORIGINAL, thought-provoking stories: a strong
hook in the first line, rising tension, one unforeseen but inevitable twist,
and an ending that lingers and reframes the opening. Philosophical, emotional,
visual. No cliches, no copyrighted characters, no real people.
Return ONLY JSON:
{"title": str, "logline": str, "theme": str, "twist": str, "ending": str,
 "scenes": [{"narration": str (<=14 words), "visual_prompt": str (concrete, visual),
 "camera": str, "transition": str, "mood": str}]}
Use 8-10 scenes. Narration is spoken, lyrical, concise."""

def generate_story(past_titles=(), theme_hint: str = "") -> dict:
    return ask_json(SYSTEM, f"Theme hint: {theme_hint or 'surprise me'}.\n"
                            f"Avoid these past titles/concepts: {list(past_titles)[-30:]}")