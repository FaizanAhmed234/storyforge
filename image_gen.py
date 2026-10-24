"""03A - Free AI visuals: Pollinations (no key). Motion is added in the editor (Ken Burns)."""
import time, urllib.parse, requests

def generate_image(prompt: str, out_path: str, seed: int) -> str:
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:900])
    for attempt in range(6):
        try:
            r = requests.get(url, timeout=180, params={
                "width": 1080, "height": 1920, "nologo": "true",
                "seed": seed, "model": "flux"})
            if r.ok and r.headers.get("content-type", "").startswith("image"):
                open(out_path, "wb").write(r.content)
                return out_path
        except requests.RequestException:
            pass
        time.sleep(8 * (attempt + 1))
    raise RuntimeError("Image generation failed after retries")