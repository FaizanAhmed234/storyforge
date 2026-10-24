import json, os, time, requests
from config import CFG

BASE = "https://generativelanguage.googleapis.com/v1beta"
PREFER = ["gemini-flash-latest", "gemini-3-flash-preview",
          "gemini-3.1-flash-lite", "gemini-2.5-flash",
          "gemini-2.5-flash-lite", "gemini-2.0-flash"]
_model = None

def _pick_model():
    global _model
    if _model:
        return _model
    if os.getenv("LLM_MODEL"):
        _model = os.getenv("LLM_MODEL")
        return _model
    r = requests.get(f"{BASE}/models", timeout=60,
                     params={"key": CFG.gemini_key, "pageSize": 200})
    r.raise_for_status()
    ok = [m["name"].split("/")[-1] for m in r.json().get("models", [])
          if "generateContent" in m.get("supportedGenerationMethods", [])]
    print("Available models:", ok)
    for p in PREFER:
        if p in ok:
            _model = p
            break
    else:
        flash = [m for m in ok if "flash" in m
                 and "image" not in m and "tts" not in m]
        if not flash:
            raise RuntimeError("No usable Gemini model for this key")
        _model = flash[0]
    print("Using model:", _model)
    return _model

def ask_json(system, user, max_tokens=8000):
    url = f"{BASE}/models/{_pick_model()}:generateContent"
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"responseMimeType": "application/json",
                                 "maxOutputTokens": max_tokens,
                                 "temperature": 1.0}}
    for attempt in range(5):
        r = requests.post(url, params={"key": CFG.gemini_key},
                          json=body, timeout=180)
        if r.status_code in (429, 503):
            time.sleep(20 * (attempt + 1))
            continue
        break
    r.raise_for_status()
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
