"""06 - Publisher: YouTube Shorts upload (free API quota ~6 uploads/day) + JSON log."""
import os, json, datetime as dt
from config import CFG

def past_titles():
    return [e["title"] for e in json.load(open(CFG.log_path))] if os.path.exists(CFG.log_path) else []

def log(entry: dict):
    data = json.load(open(CFG.log_path)) if os.path.exists(CFG.log_path) else []
    entry["time"] = dt.datetime.utcnow().isoformat()
    data.append(entry)
    json.dump(data, open(CFG.log_path, "w"), indent=1)

def upload_youtube(path, title, caption, hashtags) -> str:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                        token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"],
                        client_secret=os.environ["YT_CLIENT_SECRET"],
                        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = build("youtube", "v3", credentials=creds)
    body = {"snippet": {"title": f"{title[:90]} #Shorts",
                        "description": f"{caption}\n\n" + " ".join("#" + h for h in hashtags),
                        "categoryId": "24"},
            "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": True}}   # AI-content disclosure
    res = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(path, resumable=True)).execute()
    return res["id"]

def publish(path, title, caption, hashtags):
    if not os.getenv("YT_REFRESH_TOKEN"):
        return "skipped (no YouTube credentials; download the video artifact)"
    return upload_youtube(path, title, caption, hashtags)
