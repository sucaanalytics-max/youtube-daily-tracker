import os
import json
import time
import requests
from datetime import date
from googleapiclient.discovery import build

# =====================
# ENVIRONMENT VARIABLES
# =====================
API_KEY = os.environ.get("YOUTUBE_API_KEY")
SHEET_WEBHOOK = os.environ.get("GOOGLE_APPS_SCRIPT_URL")

if not API_KEY:
    raise ValueError("❌ YOUTUBE_API_KEY not found")

if not SHEET_WEBHOOK:
    raise ValueError("❌ GOOGLE_APPS_SCRIPT_URL not found")

# =====================
# LOAD CHANNELS (STATIC)
# =====================
with open("channels.json", "r") as f:
    CHANNELS = json.load(f)

# =====================
# YOUTUBE CLIENT
# =====================
youtube = build("youtube", "v3", developerKey=API_KEY)

# =====================
# FUNCTIONS
# =====================
def get_all_videos(playlist_id):
    video_ids = []
    token = None

    while True:
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=token
        ).execute()

        for item in res["items"]:
            video_ids.append(item["contentDetails"]["videoId"])

        token = res.get("nextPageToken")
        if not token:
            break

        time.sleep(0.2)

    return video_ids


def get_video_stats(video_ids):
    rows = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i+50]
        res = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(batch)
        ).execute()

        for v in res["items"]:
            rows.append({
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "published_at": v["snippet"]["publishedAt"],
                "views": int(v["statistics"].get("viewCount", 0))
            })

        time.sleep(0.2)

    return rows

# =====================
# MAIN EXECUTION
# =====================
today = date.today().isoformat()
payload = []

for channel_name, meta in CHANNELS.items():
    print(f"▶ Processing: {channel_name}")

    video_ids = get_all_videos(meta["uploads_playlist"])
    stats = get_video_stats(video_ids)

    for s in stats:
        payload.append({
            "date": today,
            "channel": channel_name,
            "channel_id": meta["channel_id"],
            "video_id": s["video_id"],
            "title": s["title"],
            "published_at": s["published_at"],
            "views": s["views"]
        })

print(f"⬆️ Sending {len(payload)} rows to Google Sheets")

requests.post(
    SHEET_WEBHOOK,
    headers={"Content-Type": "application/json"},
    data=json.dumps(payload),
    timeout=30
)
