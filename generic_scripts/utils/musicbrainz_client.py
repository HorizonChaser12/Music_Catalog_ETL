from datetime import datetime
import json
import logging
import time
import requests
from requests.adapters import HTTPAdapter
from sqlalchemy import exists
from urllib3.util.retry import Retry
import os

BASE_URL = "https://musicbrainz.org/ws/2"

HEADERS = {
    "User-Agent": "MusicAnalyticsETL/1.0 (bartakkepranoti14@gmail.com)"
}

RETRY_STRATEGY = Retry(
    total=5,
    connect=5,
    read=5,
    status=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=frozenset(["GET"]),
    raise_on_status=False,
)

SESSION = requests.Session()
ADAPTER = HTTPAdapter(max_retries=RETRY_STRATEGY)
SESSION.mount("https://", ADAPTER)
SESSION.mount("http://", ADAPTER)


def make_request(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = SESSION.get(
            url,
            params=params,
            headers=HEADERS,
            timeout=30,
            verify=True,
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
    os.makedirs(f"/opt/project/data/raw/{folder}", exist_ok = True)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    logging.info(f"Saved {len(data)} records to {file_path}")
   