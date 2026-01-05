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

BATCH_SIZE = 300   # smaller = safer

def get_video_stats(video_ids):
    rows = []
    for i in range(0, len(video_ids), 50):
        res = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids[i:i+50])
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

def post_batches(rows):
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        requests.post(
            SHEET_WEBHOOK,
            headers={"Content-Type": "application/json"},
            data=json.dumps(batch),
            timeout=20
        )
        time.sleep(1)

today = date.today().isoformat()

for channel, meta in CHANNELS.items():
    print(f"▶ Processing channel: {channel}")

    video_ids = VIDEO_CACHE.get(channel, [])
    stats = get_video_stats(video_ids)

    channel_rows = []
    for s in stats:
        channel_rows.append({
            "date": today,
            "channel": channel,
            "channel_id": meta["channel_id"],
            "video_id": s["video_id"],
            "title": s["title"],
            "published_at": s["published_at"],
            "views": s["views"]
        })

    print(f"⬆️ Sending {len(channel_rows)} rows for {channel}")
    post_batches(channel_rows)

    # CRITICAL pause between channels
    time.sleep(5)

print("✅ All channels sent successfully")
