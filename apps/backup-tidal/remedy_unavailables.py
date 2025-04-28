#!/venv/bin/python

import json
import os
import sys
from pathlib import Path

import tidalapi
from lib import auth
from collections import namedtuple
from typing import Optional

Track = namedtuple("Track", "name artist album artists")

def require_env(name: str) -> str:
    """Returns the value of the given environment variable or prints a message and exits."""
    if (val := os.environ[name]) != "":
        return val

    print(f"{name} is required")
    sys.exit(1)


# Required
PATH_TO_CREDS = require_env("PATH_TO_CREDS")
PATH_TO_CACHE = "/tmp/remedy.cache.json"

# Optional
# time to sleep between tracks() API calls to avoid rate limits
RATE_LIMIT_SLEEP_SECONDS = os.environ.get("RATE_LIMIT_SLEEP_SECONDS", 8)
PLAYLIST_PATH = os.environ.get("PLAYLIST_PATH", "/tmp")

def scrub(ot: Track) -> Track:
    return Track(
        name=ot.name,
        artist=ot.artist,
        album=ot.album.replace(" (Remastered)", ""),
        artists=None,
    )


def score(candidate: Track, target: Track) -> int:
    if candidate.name != target.name:
        return 0

    s = 10

    if candidate.artist == target.artist:
        s += 10

    if candidate.album == target.album:
        s += 10

    return s

def find_track(session: tidalapi.Session, target: Track) -> Optional[str]:

    target = scrub(target)

    search_terms = [f"{target.artist} {target.name}", target.name]
    print(search_terms)

    candidates = []

    for search_term in search_terms:
        results = session.search(search_term, models=[tidalapi.media.Track])

        for result in results["tracks"]:
            artist_group = ', '.join(sorted(a.name for a in result.artists))
            candidate = scrub(Track(name=result.name, artist=result.artist.name, album=result.album.name, artists=artist_group))

            print(f"{candidate} ?== {target}")

            if cscore := score(candidate, target) > 0:
                candidates.append((candidate, cscore))

    if len(candidates) == 0:
        return None

    return sorted(candidates, key=lambda e: -e[1])[0]

def main():
    """Does the magic."""
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path to playlist json>")
        sys.exit(1)

    playlist_path = sys.argv[1]

    session = tidalapi.Session()
    auth.login(session, PATH_TO_CREDS)

    with open(playlist_path, "r", encoding="utf-8") as f:
        tracks = json.load(f)

    if not Path(PATH_TO_CACHE).exists():
        Path(PATH_TO_CACHE).write_text("{}")

    with open(PATH_TO_CACHE, "r", encoding="utf-8") as f:
        cache = json.load(f)

    try:
        for track in tracks:
            # json keys are always strings
            if str(track["id"]) in cache:
                print(f"⏭️ Skipping track {track["name"]}")
                continue

            if track.get("remedied"):
                cache[track["id"]] = 12345
                continue

            if not track["available"]:
                print(f"🧑‍⚕️ Attempting to remedy track {track["name"]}")
                if new_track_id := find_track(session, Track(
                    name=track["name"],
                    artist=track["artist"],
                    album=track["album"],
                    artists=', '.join(sorted(a for a in track["artists"]))
                )):
                    if track["id"] == new_track_id:
                        print(f"  ⁉️ WTF track {track["name"]} found same id, weird")
                    else:
                        print(f"  👍 found new id {new_track_id} for track {track["name"]} {track["id"]}")
                        cache[track["id"]] = new_track_id
                else:
                    print(f"  ❌ couldn't find new id for track {track["name"]}")
                    break
    finally:
        with open(PATH_TO_CACHE, "w", encoding="utf-8") as f:
            json.dump(cache, f)

            # sys.exit(1)

if __name__ == "__main__":
    main()
