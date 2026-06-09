from datetime import datetime
import json
from postgres_connection import get_connection
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def load_recordings():
    logging.info("Starting to load recordings data into the database")
    current_date = datetime.now().strftime("%Y_%m_%d")
    with open(f"/opt/project/data/raw/recordings/recordings_{current_date}.json","r") as file:
       recordings = json.load(file)

    conn = get_connection()
    cursor = conn.cursor()

    for recording in recordings:
      cursor.execute("""INSERT INTO lnd_recordings (payload) VALUES (%s)""",(json.dumps(recording),)) 

    conn.commit()

    logging.info("Successfully loaded recordings data into the database")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_recordings()