import os
from dataclasses import dataclass

@dataclass
class Config:
    gemini_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-2.5-flash")
    voice: str = os.getenv("TTS_VOICE", "en-US-AndrewMultilingualNeural")
    music_dir: str = "assets/music"
    out_dir: str = "output"
    log_path: str = "published.json"
    width: int = 1080
    height: int = 1920
    fps: int = 30

CFG = Config()
os.makedirs(CFG.out_dir, exist_ok=True)
