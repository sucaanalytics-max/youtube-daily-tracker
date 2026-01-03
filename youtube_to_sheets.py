import os
import json
import time
import requests
from datetime import date
from googleapiclient.discovery import build

API_KEY = os.environ.get("YOUTUBE_API_KEY")
SHEET_WEBHOOK = os.environ.get("GOOGLE_APPS_SCRIPT_URL")

youtube = build("youtube", "v3", developerKey=API_KEY)

with open("channels.json") as f:
    CHANNELS = json.load(f)

with open("videos_cache.json") as f:
    VIDEO_CACHE = json.load(f)

BATCH_SIZE = 500  # SAFE size for Apps Script

def get_video_stats(video_ids):
    out = []
    for i in range(0, len(video_ids), 50):
        res = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids[i:i+50])
        ).execute()

        for v in res["items"]:
            out.append({
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "published_at": v["snippet"]["publishedAt"],
                "views": int(v["statistics"].get("viewCount", 0))
            })

        time.sleep(0.2)
    return out


def post_in_batches(rows):
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        print(f"⬆️ Sending rows {i+1}–{i+len(batch)}")

        requests.post(
            SHEET_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps(batch),
            timeout=30
        )

        time.sleep(1)  # IMPORTANT: prevent Apps Script overload


today = date.today().isoformat()
payload = []

for channel, meta in CHANNELS.items():
    print("▶ Processing:", channel)

    video_ids = VIDEO_CACHE.get(channel, [])
    stats = get_video_stats(video_ids)

    for s in stats:
        payload.append({
            "date": today,
            "channel": channel,
            "channel_id": meta["channel_id"],
            "video_id": s["video_id"],
            "title": s["title"],
            "published_at": s["published_at"],
            "views": s["views"]
        })

print(f"📦 Total rows to send: {len(payload)}")
post_in_batches(payload)

print("✅ All batches sent successfully")
