import requests
import json
from datetime import datetime
import time

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def fetch_artists():
    url="https://musicbrainz.org/ws/2/artist"
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

    all_artists = []
    logging.info("Starting artist extraction")

    for artist_name in artists:
        params={
               "query":f"artist:{artist_name}",
               "fmt":"json"
      } 
        logging.info(f"Fetching data for artist: {artist_name}") 
        response = requests.get(url,params=params,headers=headers)
        if response.status_code == 200:
           logging.info(f"Status code {response.status_code} received. Processing data for artist: {artist_name}")
           data = response.json()
           all_artists.extend(data.get("artists", []))
           artist_count = len(data.get("artists", []))
           logging.info(f"Fetched {artist_count} artist records for {artist_name}")
        else:
            logging.error(f"Failed to fetch data for {artist_name}. Status code: {response.status_code}")
        time.sleep(2)  # Sleep for 2 second to respect rate limits

    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/artists/artists_{current_date}.json"

    try:
        with open(file_path,"w") as file:
            json.dump(all_artists, file , indent=4)
        logging.info(f"File saved successfully at {file_path}")

    except Exception as e:
        logging.error(f"Error occurred while writing to file: {e}")