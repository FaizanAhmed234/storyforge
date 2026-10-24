"""05 - Caption & Hashtag Engine."""
from llm import ask_json

SYSTEM = """You write tasteful, high-retention social copy for cinematic short stories.
Return ONLY JSON: {"hook": str (<=8 words), "title": str (<=60 chars),
"caption": str (2-3 lines, ends with a question or reflection),
"hashtags": [8-12 strings without '#', broad + niche mix]}"""

def make_caption(story: dict) -> dict:
    d = ask_json(SYSTEM, f"Title: {story['title']}\nLogline: {story['logline']}\n"
                         f"Theme: {story['theme']}\nTwist: {story['twist']}", 800)
    d["hashtags"] = [h.lstrip("#").replace(" ", "") for h in d["hashtags"]]
    return d