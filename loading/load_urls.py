import json
from datetime import datetime
from postgres_connection import get_connection
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_urls():
    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = f"/opt/project/data/raw/urls/urls_{current_date}.json"
    with open(file_path,"r") as file:
        urls = json.load(file)
    conn = get_connection()
    cursor=conn.cursor()
    logging.info(f"Loading {len(urls)} URLs into the database")
    cursor.execute("TRUNCATE TABLE lnd_urls")
    for url in urls:
        cursor.execute("INSERT INTO lnd_urls (payload) VALUES (%s)", (json.dumps(url),))
    logging.info(f"Finished loading {len(urls)} URLs into the database")
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_urls()