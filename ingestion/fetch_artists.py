import requests
import json
from datetime import datetime
import time

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

for artist in artists:
    params={
    "query":f"artist:{artist}",
    "fmt":"json"
   }
    response = requests.get(url,params=params,headers=headers)
    if response.status_code == 200:
        data = response.json()
        for artist_data in data["artists"]:
            all_artists.append({
                "artist_id": artist_data.get("id"),
                "name": artist_data.get("name"),
                "country": artist_data.get("country"),
                "gender": artist_data.get("gender"),
                "score": artist_data.get("score")
            })
    else:
        print(f"Failed to fetch data for {artist}. Status code: {response.status_code}")
    time.sleep(1)  # Sleep for 1 second to respect rate limits

current_date = datetime.now().strftime("%Y_%m_%d")
file_path = f"/opt/project/data/raw/artists/artists_{current_date}.json"

try:
    with open(file_path,"w") as file:
        json.dump(all_artists, file , indent=4)
    print("file saved successfully") 

except Exception as e:
    print(f"Error occurred while writing to file: {e}")