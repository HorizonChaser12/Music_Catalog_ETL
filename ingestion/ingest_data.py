import logging
import random
import string

from datetime import datetime

from musicbrainz_client import (
    make_request,
    save_json
)

logging.basicConfig(level=logging.INFO)

def discover_artists():

    letters = random.sample(string.ascii_lowercase, 3)
    candidates = []
    for letter in letters:

        params = {
            "query": f"artist:{letter}*",
            "fmt": "json",
            "limit": 100,
            "offset": random.randint(0, 500)
        }
        data = make_request(
            endpoint="artist",
            params=params
        )
        if data:
            candidates.extend(
                data.get("artists", [])
            )

    return candidates

def fetch_artists(sample_size=2):

    logging.info("Discovering artists...")
    candidates = discover_artists()
    logging.info(
        f"Discovered {len(candidates)} artists"
    )
    if len(candidates) > sample_size:

        artists = random.sample(
            candidates,
            sample_size
        )
    else:
        artists = candidates

    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = (
        f"/opt/project/data/raw/artists/"
        f"artists_{current_date}.json"
    )
    save_json(artists, "artists", "artists")

    return artists

def fetch_releases(artists):
    releases = []

    for artist in artists:
        artist_name = artist["name"]
        logging.info(f"Fetching releases for {artist_name}")
        params = {
            "query": f'arid:{artist["id"]}',
            "fmt": "json",
            "limit": 10
        }
        data = make_request(
            endpoint="release",
            params=params
        )
        if data:
            for release in data.get("releases", []):

                # Save queried artist
                release["queried_artist_id"] = artist["id"]

                logging.info("=" * 80)
                logging.info(
                    "Queried artist : %s (%s)",
                    artist["name"],
                    artist["id"]
                )

                logging.info("Artist credit:")

                for credit in release.get("artist-credit", []):
                    logging.info(
                        " - %s (%s)",
                        credit["artist"]["name"],
                        credit["artist"]["id"]
                    )

                print(release)
                releases.append(release)

    save_json(releases, "releases", "releases")
    return releases

def fetch_recordings(releases):
    recordings = []
    for release in releases:
        release_id = release["id"]
        logging.info(
            f"Fetching recordings for {release_id}"
        )
        data = make_request(
            endpoint=f"release/{release_id}",
            params={
                "inc": "recordings",
                "fmt": "json"
            }
        )
        if data:
            recordings.append(data)

    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = (
        f"/opt/project/data/raw/recordings/"
        f"recordings_{current_date}.json"
    )
    save_json(recordings, "recordings", "recordings")

def fetch_urls(releases):
    urls = []
    for release in releases:
        release_id = release["id"]
        logging.info(
            f"Fetching urls for {release_id}"
        )
        data = make_request(
            endpoint=f"release/{release_id}",
            params={
                "inc": "url-rels",
                "fmt": "json"
            }
        )
        if data:
            urls.append(data)

    current_date = datetime.now().strftime("%Y_%m_%d")
    file_path = (
        f"/opt/project/data/raw/urls/"
        f"urls_{current_date}.json"
    )
    save_json(urls, "urls", "urls")