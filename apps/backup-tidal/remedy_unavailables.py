#!/venv/bin/python

import json
import os
import sys
from pathlib import Path

import tidalapi
from lib import auth
from collections import namedtuple
from typing import Optional

Track = namedtuple("Track", "id name artist album artists")

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
        id=ot.id,
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

    candidates = []

    for search_term in search_terms:
        results = session.search(search_term, models=[tidalapi.media.Track])

        for result in results["tracks"]:
            artist_group = ', '.join(sorted(a.name for a in result.artists))
            candidate = scrub(Track(id=result.id, name=result.name, artist=result.artist.name, album=result.album.name, artists=artist_group))

            if cscore := score(candidate, target) > 0:
                candidates.append((candidate, cscore))

    if len(candidates) == 0:
        return None

    return sorted(candidates, key=lambda e: -e[1])[0][0].id

def remedy_playlist(playlist_path: str, session: tidalapi.Session, cache: dict[str, int]):
    with open(playlist_path, "r", encoding="utf-8") as f:
        tracks = json.load(f)

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
                    id="",
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

def publish_corrections(session: tidalapi.Session, track_ids: list[str], new_playlist_name: str):
    playlist = None
    for candidate in session.user.playlists():
        if candidate.name == new_playlist_name:
            print(f"Found playlist {new_playlist_name}")
            playlist = candidate
            break

    if not playlist:
        print(f"Creating playlist {new_playlist_name}")
        playlist = session.user.create_playlist(new_playlist_name, new_playlist_name)

    MAX_ADD = min(100, len(track_ids))
    start, finish = 0, MAX_ADD
    while finish <= len(track_ids):
        print(f"adding {start}:{finish}")
        playlist.add(track_ids[start:finish])
        start, finish = finish, finish + MAX_ADD

def main():
    """Does the magic."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <path to playlist json> <new playlist name>")
        sys.exit(1)

    playlist_path = sys.argv[1]
    new_playlist_name = sys.argv[2]


    session = tidalapi.Session()
    auth.login(session, PATH_TO_CREDS)

    if not Path(PATH_TO_CACHE).exists():
        Path(PATH_TO_CACHE).write_text("{}")

    with open(PATH_TO_CACHE, "r", encoding="utf-8") as f:
        cache = json.load(f)

    remedy_playlist(playlist_path, session, cache)

    publish_corrections(session, [str(v) for v in cache.values()], new_playlist_name)


if __name__ == "__main__":
    main()
