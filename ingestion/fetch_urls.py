import requests
import json
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_urls():
    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/releases/releases_{current_date}.json"
    with open (file_path, "r") as file:
        releases = json.load(file)
    headers = {
        "User-Agent": "MusicAnalyticsETL/1.0 (bartakkepranoti14@gmail.com)"
    }
    all_urls=[]
    logging.info(f"Starting to fetch URLs for {len(releases)} releases")
    for release in releases:
        release_id=release.get("id") 
        logging.info(f"Fetching URLs for release_id={release_id}")
        url=f"https://musicbrainz.org/ws/2/release/{release_id}"
        params={
            "inc":"url-rels",
            "fmt":"json"
        }
        response = requests.get(url,headers=headers,params=params) 
        data = response.json()
        logging.info(f"Successfully fetched URLs for release ID: {release_id}")
        all_urls.append(data)
    logging.info(f"Finished fetching URLs for {len(releases)} releases")
    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/urls/urls_{current_date}.json"
    logging.info(f"Saving URLs to {file_path}")
    with open(file_path,"w") as file:
        json.dump(all_urls,file,indent=4) 
    logging.info(f"Finished saving URLs to {file_path}")

          
        
import requests
import json
from datetime import datetime

url="https://musicbrainz.org/ws/2/url"
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

all_urls = []

for artist in artists:
    params={
    "query":f"artist:{artist}",
    "fmt":"json"
   }
    response = requests.get(url,params=params,headers=headers)
    if response.status_code == 200:
        data = response.json()
        all_urls.extend(data["urls"])

current_date = datetime.now().strftime("%Y_%m_%d")
file_path = f"data/raw/urls/urls_{current_date}.json"

try:
    with open(file_path,"w") as file:
        json.dump(all_urls, file , indent=4)
    print("file saved successfully") 

except Exception as e:
    print(f"Error occurred while writing to file: {e}")