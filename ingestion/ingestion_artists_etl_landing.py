import requests
import json
from datetime import datetime
import logging
import os
from typing import List
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

url = "https://musicbrainz.org/ws/2/"

artists = [
    "Coldplay",
    "Lord Huron",
    "Zara Larsson"
    
]

headers = {
    "User-Agent": "MusicAnalyticsETL/1.0 (suryakant.mangaraj@gmail.com)"
}



def fetch_artists(artists: List) :
    """_summary_
         Fetches a List of Artist and then loads the data from API to landing tables
    """
    url_with_filter = url+"artist"
    artists_data = []
    
    try:
        for artist in artists:

            params = {
                "query": f'artist:"{artist}"',
                "fmt": "json",
                "limit": 1
            }

            logger.info(f"Fetching {artist}")

            response = requests.get(
                url_with_filter,
                params=params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            logger.info(f"API Fetched successfully with status code: {response.status_code}")

            data = response.json()
            
            for artist in data.get("artists", []):
                artists_data.append(artist)

    except Exception as e:
        logger.error(f"{e}")

    os.makedirs("/opt/project/data/raw/artists", exist_ok=True)

    current_date = datetime.now().strftime("%Y_%m_%d")

    file_path = f"/opt/project/data/raw/artists/artists_{current_date}.json"

    logger.info(f"Saving the fetched data in {file_path}")
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            artists_data,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info(f"Saved to {file_path}")
    
    return  artists_data
    
    
def fetch_releases(artist_list:List[str]):
    """_summary_
    fetch all the release with the artists data
    """
    url_with_filter = url+"release"
    releases = []
    try:
        for artist in artist_list:
            
            params = {
            "artist": artist,
            "fmt": "json",
            "limit": 100
            }

            logger.info(f"Fetching releases for {artist}")

            response = requests.get(
                url_with_filter,
                params=params,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            logger.info(f"API Fetched successfully with status code: {response.status_code}")

            data = response.json()

            for release in data.get("releases", []):
                releases.append(release)
                
                
    except Exception as e:
        logger.error(f"Error: {e}")

    os.makedirs("opt/project/data/raw/releases", exist_ok=True)

    current_date = datetime.now().strftime("%Y_%m_%d")

    file_path = f"opt/project/data/raw/releases/releases_{current_date}.json"

    logger.info(f"Saving the fetched data in {file_path}")
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            releases,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info(f"Saved to {file_path}")
    
    return releases


def main():
    # 1. Fetch Artists
    logger.info(f"\n.......Artist Data API fetch started....... \n")
    artist_data = fetch_artists(artists)
    artist_list = []
    if artist_data:
        for artist in artist_data:
            artist_list.append(artist["id"])
    else:
        print("No artists found.")
       
    logger.info(f"\n.......Artist Data API fetch completed....... \n")
    
    if artist_data:
        logger.info(f"\n.......Release Data API fetch started....... \n")
        release_data = fetch_releases(artist_list)
        release_list = []
        if release_data:
            for release in release_data:
                release_list.append(release["id"])
        else:
            print("No releases found.")

        logger.info(f"\n.......Release Data API fetch completed....... \n")

    
if __name__ == "__main__":
    main()    
        