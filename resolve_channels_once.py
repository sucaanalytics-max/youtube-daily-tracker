import os
import json
from googleapiclient.discovery import build

API_KEY = os.environ.get("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

channels = [
    "Saregama",
    "Saregama TV Shows Tamil",
    "Saregama Bhojpuri",
    "Saregama Tamil",
    "Saregama Telugu",
    "Saregama Bengali",
    "Saregama Karaoke",
    "Saregama Bhakti",
    "Saregama Gujarati",
    "Saregama Marathi",
    "Saregama Punjabi",
    "Saregama Malayalam",
    "Saregama Ghazal",
    "Saregama Movies",
    "Saregama Regional",
    "Saregama Carnatic",
    "Yoodlee Films",
    "Saregama Kannada",
    "Saregama Haryanvi",
    "Saregama Hindustani Classical",
    "Saregama Sufi",
    "Saregama Kids",
    "Saregama Assamese",
    "Tips Official",
    "90's Gaane",
    "Tips Jhankaar Gaane",
    "Tips Punjabi",
    "Tips Films",
    "Tips Bhojpuri",
    "Tips Bhakti Prem",
    "Tips Tamil",
    "Evergreen Bollywood Hits",
    "Bollywood Sadabahar",
    "Tips Haryanvi",
    "Tips Telugu",
    "Volume",
    "Tips Marathi",
    "Tips Gujarati",
    "Tips Malayalam",
    "Tips Rajasthani",
    "Tips Kannada",
    "Tips Sindhi"
]

mapping = {}

for ch in channels:
    print("Resolving:", ch)
    res = youtube.search().list(
        part="snippet",
        q=ch,
        type="channel",
        maxResults=1
    ).execute()

    if not res["items"]:
        print("❌ Not found:", ch)
        continue

    channel_id = res["items"][0]["snippet"]["channelId"]

    ch_details = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    uploads = ch_details["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    mapping[ch] = {
        "channel_id": channel_id,
        "uploads_playlist": uploads
    }

with open("channels.json", "w") as f:
    json.dump(mapping, f, indent=2)

print("✅ Saved channels.json")
