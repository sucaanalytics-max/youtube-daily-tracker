import json
import time
from googleapiclient.discovery import build
import os

API_KEY = os.environ.get("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

with open("channels.json") as f:
    CHANNELS = json.load(f)

def get_all_videos(playlist_id):
    vids, token = [], None
    while True:
        res = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=token
        ).execute()

        vids += [i["contentDetails"]["videoId"] for i in res["items"]]
        token = res.get("nextPageToken")

        if not token:
            break
        time.sleep(0.2)

    return vids

video_cache = {}

for channel, meta in CHANNELS.items():
    print("Caching videos for:", channel)
    video_cache[channel] = get_all_videos(meta["uploads_playlist"])

with open("videos_cache.json", "w") as f:
    json.dump(video_cache, f)

print("✅ videos_cache.json created")
