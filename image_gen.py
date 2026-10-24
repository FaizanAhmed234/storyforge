import base64, os, shutil, subprocess, threading, time, urllib.parse, requests
from config import CFG

_lock = threading.Lock()
_s = {"gem_dead": False, "last": None, "t": 0.0}
GAP = 47  # free tier: 1 image per 45s
GEM_IMAGE = ["gemini-3.1-flash-image", "gemini-3.1-flash-lite-image",
             "gemini-3.1-flash-image-preview"]

def _normalize(path):
    tmp = path + ".n.jpg"
    subprocess.run(["ffmpeg", "-y", "-i", path, "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-q:v", "2", tmp], check=True, capture_output=True)
    os.replace(tmp, path)

def _poll(prompt, out, seed):
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt[:600])
    for i in range(5):
        wait = GAP - (time.time() - _s["t"])
        if wait > 0:
            time.sleep(wait)
        _s["t"] = time.time()
        try:
            r = requests.get(url, timeout=120, params={
                "width": 864, "height": 1536, "nologo": "true",
                "seed": seed, "model": "flux"})
            if r.ok and r.headers.get("content-type", "").startswith("image"):
                open(out, "wb").write(r.content)
                return True
            print(f"Pollinations try {i+1}: {r.status_code} {r.text[:100]!r}")
        except requests.RequestException as e:
            print(f"Pollinations try {i+1} error: {e}")
    return False

def _gemini(prompt, out):
    for m in GEM_IMAGE:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
        body = {"contents": [{"parts": [{"text": prompt + " Vertical 9:16 image."}]}],
                "generationConfig": {"responseModalities": ["IMAGE"]}}
        try:
            r = requests.post(url, params={"key": CFG.gemini_key},
                              json=body, timeout=120)
            if not r.ok:
                print("Gemini image", m, r.status_code, r.text[:120])
                continue
            for part in r.json()["candidates"][0]["content"]["parts"]:
                d = part.get("inlineData") or part.get("inline_data")
                if d:
                    open(out, "wb").write(base64.b64decode(d["data"]))
                    return True
        except Exception as e:
            print("Gemini image error:", m, e)
    _s["gem_dead"] = True
    return False

def generate_image(prompt: str, out_path: str, seed: int) -> str:
    with _lock:
        ok = _poll(prompt, out_path, seed)
        if not ok and not _s["gem_dead"]:
            ok = _gemini(prompt, out_path)
        if ok:
            _normalize(out_path)
            _s["last"] = out_path
        elif _s["last"]:
            print("WARNING: reusing previous image")
            shutil.copy(_s["last"], out_path)
        else:
            print("WARNING: plain background")
            subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i",
                "color=c=0x1b263b:s=1080x1920", "-frames:v", "1", out_path],
                check=True, capture_output=True)
    return out_path
