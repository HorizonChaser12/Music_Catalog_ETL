from datetime import datetime
import json
from postgres_connection import get_connection
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def load_releases():
    logging.info("Starting to load releases data into the database")
    current_date = datetime.now().strftime("%Y_%m_%d")
    with open(f"/opt/project/data/raw/releases/releases_{current_date}.json","r") as file:
       releases = json.load(file)

    conn = get_connection()
    cursor = conn.cursor() 
    cursor.execute("TRUNCATE TABLE lnd_releases") 
    for release in releases:
      cursor.execute("""INSERT INTO lnd_releases (payload) VALUES (%s)""",(json.dumps(release),)) 

    conn.commit()
    logging.info(f"Loaded {len(releases)} release records into lnd_releases")
    logging.info("Successfully loaded releases data into the database")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_releases()
