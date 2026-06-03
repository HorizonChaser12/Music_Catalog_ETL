import requests
import json
from datetime import datetime
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

url = "https://musicbrainz.org/ws/2/artist"

artists = [
    "Coldplay",
    "Lord Huron",
    "Zara Larsson"
    
]

headers = {
    "User-Agent": "MusicAnalyticsETL/1.0 (suryakant.mangaraj@gmail.com)"
}

all_artists = []

try:
    for artist in artists:

        params = {
            "query": f'artist:"{artist}"',
            "fmt": "json",
            "limit": 1
        }

        logger.info(f"Fetching {artist}")

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("artists"):
            logger.warning(f"No result found for {artist}")
            continue

        artist_data = data["artists"][0]

        cleaned_artist = {
            "artist_id": artist_data.get("id"),
            "artist_name": artist_data.get("name"),
            "artist_type": artist_data.get("type"),
            "country": artist_data.get("country"),
            "disambiguation": artist_data.get("disambiguation"),
            "score": artist_data.get("score")
        }

        all_artists.append(cleaned_artist)

except Exception as e:
    logger.error(f"Error: {e}")

os.makedirs("data/raw/artists", exist_ok=True)

current_date = datetime.now().strftime("%Y_%m_%d")

file_path = f"data/raw/artists/artists_{current_date}.json"

with open(file_path, "w", encoding="utf-8") as file:
    json.dump(
        all_artists,
        file,
        indent=4,
        ensure_ascii=False
    )

logger.info(f"Saved to {file_path}")