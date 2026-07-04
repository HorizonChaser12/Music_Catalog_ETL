from datetime import datetime
import json
import logging
import time
import requests

BASE_URL = "https://musicbrainz.org/ws/2"

HEADERS = {
    "User-Agent": "MusicAnalyticsETL/1.0 (bartakkepranoti14@gmail.com)"
}


def make_request(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=30
        )
        response.raise_for_status()
        time.sleep(1)
        return response.json()

    except requests.exceptions.RequestException as e:
        logging.error(f"API Request Failed: {e}")
        return None


def save_json(data, folder, file_prefix):
    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/{folder}/{file_prefix}_{current_date}.json"
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)
    logging.info(f"Saved {len(data)} records to {file_path}")