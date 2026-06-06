from datetime import datetime
import json
from postgres_connection import get_connection

current_date = datetime.now().strftime("%Y_%m_%d")
with open(f"/opt/project/data/raw/artists/artists_{current_date}.json","r") as file:
    artists = json.load(file)

conn = get_connection()
cursor = conn.cursor()

for artist in artists:
    print(f"loading artist: {artist.get('name')}")
    artist_id = artist.get("artist_id")
    name = artist.get("name")
    gender = artist.get("gender")
    country = artist.get("country")
    score = artist.get("score")
    cursor.execute("""INSERT INTO artists (artist_id,name,gender,country,score) VALUES (%s, %s, %s, %s, %s) """,(artist_id,name,gender,country,score))


conn.commit()

cursor.close()
conn.close()