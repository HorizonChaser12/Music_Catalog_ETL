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