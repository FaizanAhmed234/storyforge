"""03B - Free narration: Microsoft Edge neural voices via edge-tts (no key)."""
import asyncio, subprocess, edge_tts
from config import CFG

def duration(path: str) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path]).strip())

def narrate(text: str, out_path: str) -> float:
    async def _go():
        await edge_tts.Communicate(text, CFG.voice, rate="-8%", pitch="-3Hz").save(out_path)
    asyncio.run(_go())
    return duration(out_path)