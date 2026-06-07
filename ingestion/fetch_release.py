import requests
import json
from datetime import datetime
import time

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

all_releases = []
for artist in artists:
    params={
        "query": f"artists{artist}",
        "fmt" : "json" 
    }
    response = requests.get(url,params=params,headers=headers)
    data = response.json()
    if response.status_code==200:
        #print(data)   
        for release in data["releases"]:
            artist_id = release["artist-credit"][0]["artist"]["id"]
            all_releases.append({
                "id":release.get("id"),
                "title":release.get("title"),
                "status":release.get("status"),
                "date":release.get("date"),
                "artist_id":artist_id
            })    
    else:
        print(f"Failed to fetch data for {artist}.status code: {response.status_code}")
    time.sleep(1)
current_date = datetime.now().strftime("%Y_%m_%d")
file_path = f"/opt/project/data/raw/releases/releases_{current_date}.json"

try:
    with open(file_path,"w") as f:
        json.dump(all_releases,f,indent=4)
        print("File saved successfully") 
except Exception as e:
    print(f"Error occurred while writing the file:{e}") 

