import requests
import json
from datetime import datetime
import logging
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "MusicAnalyticsETL/1.0 (suryakant.mangaraj@gmail.com)"
}

import requests
import json

ARTIST_MBID = "cc197bad-dc9c-440d-a5b5-d52ba2e14234"  # KK

headers = {
    "User-Agent": "MusicAnalyticsETL/1.0 (suryakant.mangaraj@gmail.com)"
}

url = "https://musicbrainz.org/ws/2/release"

params = {
    "artist": ARTIST_MBID,
    "fmt": "json",
    "limit": 100
}

response = requests.get(
    url,
    params=params,
    headers=headers,
    timeout=30
)

data = response.json()

releases = []

for release in data.get("releases", []):

    releases.append({
        "release_id": release.get("id"),
        "artist_id": ARTIST_MBID,
        "title": release.get("title"),
        "date": release.get("date"),
        "country": release.get("country"),
        "status": release.get("status")
    })

print(json.dumps(releases[:5], indent=4))