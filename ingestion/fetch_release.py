import logging
import requests
import json
from datetime import datetime
import time
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_releases():
    url="https://musicbrainz.org/ws/2/release"
    artists = [
        "Shreya Ghoshal",
        "Arijit Singh",
        "Sonu Nigam",
        "KK",
        "Sunidhi Chauhan"
   ]
    headers = {
    "User-Agent": "MusicAnalyticsETL/1.0 (bartakkepranoti14@gmail.com)" 
   }
    
    logging.info("Starting release extraction")

all_releases = []

release_id = "c9a8647a-d97c-4982-bf20-3ede7b39f568"
url = f"https://musicbrainz.org/ws/2/release/{release_id}"

params = {
    "inc": "recordings",
    "fmt": "json"
}

response = requests.get(
    url,
    params=params,
    headers=headers
)

print(json.dumps(response.json(), indent=4))