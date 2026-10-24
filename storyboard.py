"""02 - Scene & Storyboard Engine."""
from dataclasses import dataclass

STYLE = ("cinematic still, 35mm film look, dramatic lighting, shallow depth of field, "
         "consistent teal-and-amber color grade, vertical composition, no text, no watermark")

@dataclass
class Scene:
    idx: int
    narration: str
    prompt: str
    camera: str
    image: str = ""
    audio: str = ""
    duration: float = 0.0

def build_storyboard(story: dict) -> list[Scene]:
    motif = story.get("theme", "")
    return [Scene(i, s["narration"],
                  f"{s['visual_prompt']}. Mood: {s['mood']}. {STYLE}. Motif: {motif}",
                  s["camera"]) for i, s in enumerate(story["scenes"])]