import json, os, time, requests
from config import CFG

BASE = "https://generativelanguage.googleapis.com/v1beta"
PREFER = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite",
          "gemini-2.5-flash", "gemini-3-flash-preview",
          "gemini-flash-lite-latest"]
_cands = None

def _candidates():
    global _cands
    if _cands:
        return _cands
    if os.getenv("LLM_MODEL"):
        _cands = [os.getenv("LLM_MODEL")]
        return _cands
    r = requests.get(f"{BASE}/models", timeout=60,
                     params={"key": CFG.gemini_key, "pageSize": 200})
    r.raise_for_status()
    ok = [m["name"].split("/")[-1] for m in r.json().get("models", [])
          if "generateContent" in m.get("supportedGenerationMethods", [])]
    _cands = [m for m in PREFER if m in ok]
    skip = ("image", "tts", "transcribe", "omni", "robotics",
            "compute", "customtools", "pro")
    _cands += [m for m in ok if "flash" in m and m not in _cands
               and not any(x in m for x in skip)]
    print("Models to try:", _cands[:8])
    return _cands

def ask_json(system, user, max_tokens=8000):
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"responseMimeType": "application/json",
                                 "maxOutputTokens": max_tokens,
                                 "temperature": 1.0}}
    last = None
    for model in _candidates()[:6]:
        url = f"{BASE}/models/{model}:generateContent"
        for attempt in range(2):
            try:
                r = requests.post(url, params={"key": CFG.gemini_key},
                                  json=body, timeout=90)
                if r.status_code in (429, 503):
                    time.sleep(15)
                    continue
                r.raise_for_status()
                text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
                out = json.loads(text)
                print("Model OK:", model)
                return out
            except Exception as e:
                last = e
                print(f"{model} failed: {e}")
                break
    raise RuntimeError(f"All models failed: {last}")
