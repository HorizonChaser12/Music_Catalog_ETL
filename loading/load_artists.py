from datetime import datetime
import json
from postgres_connection import get_connection

current_date = datetime.now().strftime("%Y_%m_%d")
with open(f"/opt/project/data/raw/artists/artists_{current_date}.json","r") as file:
    artists = json.load(file)

conn = get_connection()
cursor = conn.cursor()

for artist in artists:
    cursor.execute("""INSERT INTO lnd_artists (payload) VALUES (%s)""",(json.dumps(artist),)) 

conn.commit()

cursor.close()
conn.close()