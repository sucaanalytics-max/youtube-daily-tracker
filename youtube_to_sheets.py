from googleapiclient.discovery import build
import requests
from datetime import date
import time
import json

API_KEY = "YOUTUBE_API_KEY"
SHEET_WEBHOOK = "GOOGLE_APPS_SCRIPT_URL"

channels = [
    "Saregama",
    "Tips Official"
    # add rest here (same as earlier)
]

youtube = build("youtube", "v3", developerKey=API_KEY)

def get_uploads_playlist(name):
    res = youtube.search().list(
        q=name, part="snippet", type="channel", maxResults=1
    ).execute()

    if not res["items"]:
        return None, None

    cid = res["items"][0]["snippet"]["channelId"]

    pl = youtube.channels().list(
        part="contentDetails", id=cid
    ).execute()

    uploads = pl["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return cid, uploads

def get_videos(pl):
    vids, token = [], None
    while True:
        r = youtube.playlistItems().list(
            part="contentDetails", playlistId=pl, maxResults=50, pageToken=token
        ).execute()
        vids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break
        time.sleep(0.2)
    return vids

def get_stats(video_ids):
    out = []
    for i in range(0, len(video_ids), 50):
        r = youtube.videos().list(
            part="snippet,statistics", id=",".join(video_ids[i:i+50])
        ).execute()
        for v in r["items"]:
            out.append({
                "video_id": v["id"],
                "title": v["snippet"]["title"],
                "published_at": v["snippet"]["publishedAt"],
                "views": int(v["statistics"].get("viewCount",0))
            })
        time.sleep(0.2)
    return out

rows = []
today = date.today().isoformat()

for ch in channels:
    cid, pl = get_uploads_playlist(ch)
    if not pl:
        continue
    vids = get_videos(pl)
    stats = get_stats(vids)

    for s in stats:
        rows.append({
            "date": today,
            "channel": ch,
            "channel_id": cid,
            **s
        })

requests.post(SHEET_WEBHOOK, data=json.dumps(rows))
