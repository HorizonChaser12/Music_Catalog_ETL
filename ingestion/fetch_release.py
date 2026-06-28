import logging
import requests
import json
from datetime import datetime
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
    for artist_name in artists:
        params = {
        "query": f'artist:"{artist_name}"',
        "fmt": "json",
        "limit": 1
        }
        logging.info(f"Fetching data for artist: {artist_name}")
        response = requests.get(url,params=params,headers=headers)
        if response.status_code==200:
          data = response.json()
          logging.info(f"Status code {response.status_code} received. Processing data for artist: {artist_name}")
          all_releases.extend(data.get("releases", []))
          release_count = len(data.get("releases", []))
          logging.info(f"Fetched {release_count} releases for {artist_name}")
        else:
           logging.error(f"Failed to fetch data for {artist_name}.status code: {response.status_code}")
        time.sleep(2)
    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/releases/releases_{current_date}.json"

    try:
        with open(file_path,"w") as f:   
          json.dump(all_releases,f,indent=4)
        logging.info(f"File saved successfully at {file_path}") 
    except Exception as e:
       logging.error(f"Error occurred while writing the file:{e}") 

