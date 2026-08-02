import logging

from ingest_data import (
    fetch_artists,
    fetch_releases,
    fetch_recordings,
    fetch_urls
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    logging.info("Starting Artist Ingestion")
    artists = fetch_artists()
    logging.info("Starting Release Ingestion")
    releases = fetch_releases(artists)
    logging.info("Starting Recording Ingestion")
    fetch_recordings(releases)
    logging.info("Pipeline Completed Successfully")