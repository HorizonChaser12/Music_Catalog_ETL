import json
from postgres_connection import get_connection

with open("data/raw/artists/artists_2026_06_03.json","r") as file:
    artists = json.load(file)

conn = get_connection()
cursor = conn.cursor()

for artist in artists:

    id = artist.get("id")
    name = artist.get("name")
    gender = artist.get("gender")
    country = artist.get("country")
    score = artist.get("score")

cursor.execute("""INSERT INTO raw_artists (id,name,gender,country,score) VALUES (%s, %s, %s, %s, %s) """,(id,name,gender,country,score))

conn.commit()

cursor.close()
conn.close()