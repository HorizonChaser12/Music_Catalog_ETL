import logging
from typing import List
import random
import string
from generic_scripts.utils.musicbrainz_client import (
    make_request,
    save_json
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)


def fetch_data(endpoint: str, params: dict, entity: str):
    logger.info("Fetching %s", entity)
    data = make_request(endpoint=endpoint, params=params)
    if data is None:
        logger.error("API fetch failed for %s", entity)
    return data


def discover_artists():
    """_summary_
        Fetches 300 random artists to randomize the input everytime the dag runs
        Returns:
        list : returns a list with all the artits id with randomness included
    """
    letters = random.sample(string.ascii_uppercase, 10)
    candidates = []
    for letter in letters:
        params = {
            "query": f"artist:{letter}*",
            "fmt": "json",
            "limit": 100,
            # "offset": random.randint(0, 500),
            "timeout": 30
        }
        data = fetch_data("artist", params, entity=f"data for artist's name starting with {letter}")
        artists = data.get("artists", []) if data else []
        for artist in artists:
            if artist.get("score", 0) >= 80:
                candidates.append(artist)

    return candidates


def fetch_artists(sample_size=random.randint(0,30)) :
    """_summary_
        Fetches sample_sized artists from the discovered artists and stores locally
       Returns:
        list : returns a list of artists
    """
    
    logger.info("Starting API service to discover Artist Data")
    candidates = discover_artists()
    logger.info("Discovered %s artists", len(candidates))
    artists = random.sample(candidates, sample_size) if len(candidates) > sample_size else candidates

    try:
        save_json(artists, "artists", "artists")
        logger.info("Saved artist data successfully")
    except Exception as e:
        logger.exception("Error saving artists data")

    return artists
    
    
def fetch_releases(artist_list):
    """_summary_
        fetch all the release with the artists data we got from the fetch_artists
       Returns:
        list : returns a list of releases
    """
    releases = []
    
    try:
        for artist in artist_list:
            artist_name = artist["name"]
            params = {
                "query": f'arid:{artist["id"]}',
                "fmt": "json",
                "limit": 10
            }
            data = fetch_data(
                endpoint="release",
                params=params,
                entity=f"release details for {artist_name}"
            )
            if data:
                for release in data.get("releases", []):
                    releases.append(release)
    except Exception:
        logger.exception("Error fetching releases")

    try:
        save_json(releases, "releases", "releases")
        logger.info("Saved release data successfully")
    except Exception:
        logger.exception("Error saving releases data")

    return releases

def fetch_urls(releases):
    """Fetch URL relations for a list of releases and save them to raw storage."""
    urls = []

    try:
        for release in releases:
            try:
                release_id = release.get("id")
                if not release_id:
                    logger.warning("Skipping release without id: %s", release)
                    continue

                logger.info("Fetching urls for release %s", release_id)
                data = make_request(
                    endpoint=f"release/{release_id}",
                    params={
                        "inc": "url-rels",
                        "fmt": "json"
                    }
                )

                if data:
                    urls.append(data)
                else:
                    logger.warning("No urls returned for release %s", release_id)

            except Exception as exc:
                logger.exception("Failed to fetch urls for release %s", release)
                continue
        try:   
            save_json(urls, "urls", "urls")
            logger.info("Saved url data successfully")
        except Exception:
            logger.exception("Error saving url data")
        return urls

    except Exception as exc:
        logger.exception("Failed to fetch urls")
        return []
 
def main():
    # 1. Fetch Artists
    logger.info(f"\n.......Artist Data API fetch started.......")
    artist_data = fetch_artists()
    logger.info(f"\n.......Artist Data API fetch completed.......")
    
    # 2. Fetch Releases
    if artist_data:
        logger.info(f"\n.......Release Data API fetch started.......")
        release_data = fetch_releases(artist_data)
        logger.info(f"\n.......Release Data API fetch completed....... \n")
        
    # 3. Fetch urls 
    if release_data:
        logger.info(f"\n.......URLs Data API fetch started....... \n")
        fetch_urls(release_data)
        logger.info(f"\n.......URLs Data API fetch completed....... \n")

    
if __name__ == "__main__":
    main()    
        