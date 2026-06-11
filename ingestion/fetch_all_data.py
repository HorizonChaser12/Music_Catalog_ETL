from fetch_artists import fetch_artists
from fetch_release import fetch_releases
from fetch_recording import fetch_recordings
from fetch_urls import fetch_urls
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__=="__main__":
    logging.info("Starting data fetching process for artists") 
    fetch_artists()
    logging.info("Starting data fetching process for releases")
    fetch_releases()
    logging.info("Starting data fetching process for recordings")
    fetch_recordings()
    logging.info("Starting data fetching process for urls")
    fetch_urls()

