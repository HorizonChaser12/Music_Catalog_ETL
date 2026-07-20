import logging
import random
import string

from datetime import datetime

from musicbrainz_client import (
    make_request,
    save_json
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def discover_artists():
    """Discover artists from MusicBrainz using random letter prefixes."""
    try:
        letters = random.sample(string.ascii_uppercase, 3)
        candidates = []

        for letter in letters:
            params = {
                "query": f"artist:{letter}*",
                "fmt": "json",
                "limit": 100,
                #"offset": random.randint(0, 500)
            }
            data = make_request(endpoint="artist", params=params)
            artists = data.get("artists", []) if isinstance(data, dict) else []

            for artist in artists:
                if artist.get("score", 0) >= 80:
                    candidates.append(artist)

        return candidates

    except Exception as exc:
        logger.exception("Failed to discover artists")
        return []


def fetch_artists(sample_size=2):
    """Fetch a sample of discovered artists and save them to raw storage."""
    try:
        logger.info("Starting artist discovery")
        candidates = discover_artists()
        logger.info("Discovered %d candidate artists", len(candidates))

        if len(candidates) > sample_size:
            artists = random.sample(candidates, sample_size)
        else:
            artists = candidates

        current_date = datetime.now().strftime("%Y_%m_%d")
        file_path = f"/opt/project/data/raw/artists/artists_{current_date}.json"

        save_json(artists, "artists", "artists")
        logger.info("Saved %d artists to %s", len(artists), file_path)

        return artists

    except Exception as exc:
        logger.exception("Failed to fetch artists")
        return []


def fetch_releases(artists):
    """Fetch releases for a list of artists and save them to raw storage."""
    releases = []

    try:
        for artist in artists:
            try:
                artist_name = artist.get("name", "unknown")
                artist_id = artist.get("id")

                if not artist_id:
                    logger.warning("Skipping artist without id: %s", artist_name)
                    continue

                logger.info("Fetching releases for artist '%s' (%s)", artist_name, artist_id)
                params = {
                    "query": f"arid:{artist_id}",
                    "fmt": "json",
                    "limit": 10
                }
                data = make_request(endpoint="release", params=params)

                if not isinstance(data, dict):
                    logger.warning("No release data returned for artist %s", artist_id)
                    continue

                for release in data.get("releases", []):
                    release["queried_artist_id"] = artist_id
                    logger.info("Queried artist: %s (%s)", artist_name, artist_id)

                    logger.info("Artist credit:")
                    for credit in release.get("artist-credit", []):
                        credit_artist = credit.get("artist", {})
                        logger.info(
                            " - %s (%s)",
                            credit_artist.get("name", "unknown"),
                            credit_artist.get("id", "unknown")
                        )

                    releases.append(release)

            except Exception as exc:
                logger.exception("Failed to fetch releases for artist %s", artist)
                continue

        save_json(releases, "releases", "releases")
        logger.info("Saved %d releases", len(releases))

        return releases

    except Exception as exc:
        logger.exception("Failed to fetch releases")
        return []


def fetch_recordings(releases):
    """Fetch recordings for a list of releases and save them to raw storage."""
    recordings = []

    try:
        for release in releases:
            try:
                release_id = release.get("id")
                if not release_id:
                    logger.warning("Skipping release without id: %s", release)
                    continue

                logger.info("Fetching recordings for release %s", release_id)
                data = make_request(
                    endpoint=f"release/{release_id}",
                    params={
                        "inc": "recordings",
                        "fmt": "json"
                    }
                )

                if data:
                    recordings.append(data)
                else:
                    logger.warning("No recordings returned for release %s", release_id)

            except Exception as exc:
                logger.exception("Failed to fetch recordings for release %s", release)
                continue

        current_date = datetime.now().strftime("%Y_%m_%d")
        file_path = f"/opt/project/data/raw/recordings/recordings_{current_date}.json"
        save_json(recordings, "recordings", "recordings")
        logger.info("Saved %d recordings to %s", len(recordings), file_path)

        return recordings

    except Exception as exc:
        logger.exception("Failed to fetch recordings")
        return []


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

        current_date = datetime.now().strftime("%Y_%m_%d")
        file_path = f"/opt/project/data/raw/urls/urls_{current_date}.json"
        save_json(urls, "urls", "urls")
        logger.info("Saved %d urls to %s", len(urls), file_path)

        return urls

    except Exception as exc:
        logger.exception("Failed to fetch urls")
        return []
