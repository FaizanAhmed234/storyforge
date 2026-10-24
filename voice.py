import asyncio, os, subprocess, time, edge_tts
from config import CFG

VOICES = [CFG.voice, "en-US-GuyNeural", "en-GB-RyanNeural",
          "en-US-ChristopherNeural"]

def duration(path: str) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path]).strip())

def narrate(text: str, out_path: str) -> float:
    last = None
    for i in range(8):
        voice = VOICES[i % len(VOICES)]
        kw = {"rate": "-8%", "pitch": "-3Hz"} if i < 2 else {}
        async def _go():
            await edge_tts.Communicate(text, voice, **kw).save(out_path)
        try:
            asyncio.run(_go())
            if os.path.getsize(out_path) > 1000:
                return duration(out_path)
        except Exception as e:
            last = e
            print(f"Voice try {i+1} ({voice}) failed: {e}")
        time.sleep(2 + 2 * i)
    raise RuntimeError(f"Voice failed: {last}")
