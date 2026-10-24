import base64, os, subprocess, threading, urllib.parse, requests
from config import CFG

_lock = threading.Lock()
_dead = {"poll": False, "gem": False}
GEM_IMAGE = ["gemini-3.1-flash-image", "gemini-3.1-flash-lite-image",
             "gemini-3.1-flash-image-preview"]

def _normalize(path):
    tmp = path + ".n.jpg"
    subprocess.run(["ffmpeg", "-y", "-i", path, "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-q:v", "2", tmp], check=True, capture_output=True)
    os.replace(tmp, path)

def _gemini(prompt, out):
    for m in GEM_IMAGE:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
        body = {"contents": [{"parts": [{"text": prompt + " Vertical 9:16 image."}]}],
                "generationConfig": {"responseModalities": ["IMAGE"]}}
        try:
            r = requests.post(url, params={"key": CFG.gemini_key},
                              json=body, timeout=120)
            if not r.ok:
                print("Gemini image", m, r.status_code, r.text[:150])
                continue
            for part in r.json()["candidates"][0]["content"]["parts"]:
                d = part.get("inlineData") or part.get("inline_data")
                if d:
                    open(out, "wb").write(base64.b64decode(d["data"]))
                    return True
        except Exception as e:
            print("Gemini image error:", m, e)
    _dead["gem"] = True
    return False

def _pollinations(prompt, out, seed):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:700])
    try:
        r = requests.get(url, timeout=90, params={
            "width": 720, "height": 1280, "nologo": "true", "seed": seed})
        if r.ok and r.headers.get("content-type", "").startswith("image"):
            open(out, "wb").write(r.content)
            return True
        print("Pollinations failed:", r.status_code, r.text[:200])
    except requests.RequestException as e:
        print("Pollinations error:", e)
    _dead["poll"] = True
    return False

def _fallback(out, seed):
    colors = ["0d1b2a", "1b263b", "2b1d3a", "1f2a1f", "3a1d1d"]
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
        f"color=c=0x{colors[seed % len(colors)]}:s=1080x1920",
        "-frames:v", "1", out], check=True, capture_output=True)
    print("WARNING: used plain fallback background")

def generate_image(prompt: str, out_path: str, seed: int) -> str:
    with _lock:
        ok = False
        if not _dead["gem"]:
            ok = _gemini(prompt, out_path)
        if not ok and not _dead["poll"]:
            ok = _pollinations(prompt, out_path, seed)
        if ok:
            _normalize(out_path)
        else:
            _fallback(out_path, seed)
    return out_path
