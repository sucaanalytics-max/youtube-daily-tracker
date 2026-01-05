import requests
import csv
import json
from datetime import datetime

CLIENT_ID = "YOUR_SB_CLIENT_ID"
TOKEN = "YOUR_SB_ACCESS_TOKEN"

with open("channels.json") as f:
    CHANNELS = json.load(f)

rows = []

for channel, meta in CHANNELS.items():
    print(f"Fetching SB history: {channel}")

    url = "https://api.socialblade.com/v2/youtube/statistics"
    params = {
        "query": meta["channel_id"],
        "clientid": CLIENT_ID,
        "token": TOKEN
    }

    r = requests.get(url, params=params).json()

    for d in r.get("data", []):
        rows.append({
            "date": d["date"],
            "channel": channel,
            "channel_id": meta["channel_id"],
            "views_total": d["views"],
            "daily_views": "",   # calculated later
            "source": "socialblade"
        })

with open("socialblade_backfill.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=rows[0].keys()
    )
    writer.writeheader()
    writer.writerows(rows)

print("✅ socialblade_backfill.csv created")
