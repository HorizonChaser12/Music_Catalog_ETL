import logging
import requests
import json
import time
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def fetch_recordings():
    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/releases/releases_{current_date}.json"
    with open(file_path,"r") as file:
       releases = json.load(file)
    all_recordings = []
    headers = {
        "User-Agent": "MusicAnalyticsETL/1.0 (bartakkepranoti14@gmail.com)"
    }
    for release in releases:
        release_id = release.get("id")
        logging.info(f"Fetching recordings for release_id={release_id}")
        url = f"https://musicbrainz.org/ws/2/release/{release_id}"   
        params = {
            "inc":"recordings",
            "fmt":"json"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            #print(response.url)
            release_data = response.json()
            all_recordings.append(release_data)
            logging.info(f"Successfully fetched recordings for release ID: {release_id}")
        else:
            logging.error(f"Failed to fetch recordings for release ID: {release_id}. Status code: {response.status_code}")
        time.sleep(1)  # Sleep for 1 second to respect rate limits
        
    logging.info(f"Total recording payloads collected: {len(all_recordings)}")
    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/recordings/recordings_{current_date}.json"

    with open(file_path,"w") as file:
        json.dump(all_recordings, file, indent=4)

