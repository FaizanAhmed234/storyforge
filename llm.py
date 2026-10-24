"""Free LLM: Google Gemini API (free tier from aistudio.google.com)."""
import json, time, requests
from config import CFG

def ask_json(system: str, user: str, max_tokens: int = 4000) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{CFG.llm_model}:generateContent"
    body = {"systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"responseMimeType": "application/json",
                                 "maxOutputTokens": max_tokens, "temperature": 1.0}}
    for attempt in range(5):
        r = requests.post(url, params={"key": CFG.gemini_key}, json=body, timeout=120)
        if r.status_code in (429, 503):      # free-tier rate limit: wait and retry
            time.sleep(20 * (attempt + 1)); continue
        break
    r.raise_for_status()
    return json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])