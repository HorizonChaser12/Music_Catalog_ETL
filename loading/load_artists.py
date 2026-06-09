from datetime import datetime
import json
from postgres_connection import get_connection
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def load_artists(): 
    logging.info("Starting to load artists data into the database")
    current_date = datetime.now().strftime("%Y_%m_%d")
    with open(f"/opt/project/data/raw/artists/artists_{current_date}.json","r") as file:
       artists = json.load(file)

    conn = get_connection()
    cursor = conn.cursor()

    for artist in artists:
      cursor.execute("""INSERT INTO lnd_artists (payload) VALUES (%s)""",(json.dumps(artist),)) 

    conn.commit()

    logging.info("Successfully loaded artists data into the database")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_artists()