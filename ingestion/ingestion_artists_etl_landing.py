import logging
from typing import List
import random
import string
from musicbrainz_client import (
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


def fetch_artists(sample_size=10) :
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


def fetch_release_group(release_list:List[dict]):
    """Fetch release-group metadata from release MBIDs."""
    release_groups = []
    seen_release_group_ids = set()
    try:
        for release in release_list:
            release_group = release.get("release-group")
            if not release_group:
                logger.warning("No release-group found for release %s", release_group)
                continue

            rg_id = release_group.get("id")
            if rg_id in seen_release_group_ids:
                logger.debug("Skipping duplicate release-group %s for release %s", release_group, rg_id)
                continue

            rg_data = fetch_data(endpoint=f"release-group/{rg_id}", params={"fmt": "json"}, entity=f"release-group {rg_id}")
            if rg_data:
                release_groups.append(rg_data)
                seen_release_group_ids.add(rg_id)
            else:
                logger.warning("Failed to fetch release-group %s", rg_id)

    except Exception:
        logger.exception("Error fetching release groups")

    try:
        save_json(release_groups, "release_groups", "release_groups")
        logger.info("Saved release group data successfully")
        logger.info("Fetched %s unique release groups", len(release_groups))
    except Exception:
        logger.exception("Error saving release groups data")

    return release_groups

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
        
    # 3. Fetch Releases_Groups 
    if release_data:
        logger.info(f"\n.......Release_Groups Data API fetch started....... \n")
        fetch_release_group(release_data)
        logger.info(f"\n.......Release_Groups Data API fetch completed....... \n")

    
if __name__ == "__main__":
    main()    
        