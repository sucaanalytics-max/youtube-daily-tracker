import os
import time
import json
import requests
from datetime import date
from googleapiclient.discovery import build

# =====================
# ENVIRONMENT VARIABLES
# =====================
API_KEY = os.environ.get("YOUTUBE_API_KEY")
SHEET_WEBHOOK = os.environ.get("GOOGLE_APPS_SCRIPT_URL")

if not API_KEY:
    raise ValueError("❌ YOUTUBE_API_KEY not found in environment variables")

if not SHEET_WEBHOOK:
    raise ValueError("❌ GOOGLE_APPS_SCRIPT_URL not found in environment variables")

# =====================
# YOUTUBE CLIENT
# =====================
youtube = build("youtube", "v3", developerKey=API_KEY)

# =====================
# CHANNEL LIST
# =====================
channels = [
    "Saregama",
    "Tips Official"
    # add remaining channels once verified
]

# =====================
# FUNCTIONS
# =====================
def get_uploads_playlist(channel_name):
    res = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    ).execute()

    if not res["items"]:
        return None, None

    channel_id = res["items"][0]["snippet"]["channelId"]

    ch = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return channel_id, uploads


def get_all_videos(playlist_id):
    videos = []
    token = None

    while True:
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=token
        ).execute()

        for item in res["items"]:
            videos.append(item["contentDetails"]["videoId"])

        token = res.get("nextPageToken")
        if not token:
            break

        time.sleep(0.2)

    return videos


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

for ch in channels:
    print(f"▶ Processing: {ch}")
    cid, uploads = get_uploads_playlist(ch)

    if not uploads:
        print(f"⚠️ Channel not found: {ch}")
        continue

    video_ids = get_all_videos(uploads)
    stats = get_video_stats(video_ids)

    for s in stats:
        payload.append({
            "date": today,
            "channel": ch,
            "channel_id": cid,
            "video_id": s["video_id"],
            "title": s["title"],
            "published_at": s["published_at"],
            "views": s["views"]
        })

print(f"⬆️ Sending {len(payload)} rows to Google Sheets")
requests.post(SHEET_WEBHOOK, data=json.dumps(payload))
