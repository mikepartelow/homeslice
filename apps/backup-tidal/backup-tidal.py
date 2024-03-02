"""Fetch a Tidal playlist and write it to a JSON file."""
from datetime import datetime
from lib import auth
import json
import os
import time
import tidalapi

# time to sleep between tracks() API calls to avoid rate limits
RATE_LIMIT_SLEEP_SECONDS = os.environ.get("RATE_LIMIT_SLEEP_SECONDS", 8)

# a JSON file with playlist_id to downloand and playlist_name base filename to write
PATH_TO_CONFIG = os.environ["PATH_TO_CONFIG"]

PATH_TO_CREDS = os.environ["PATH_TO_CREDS"]

def write_playlist(session: tidalapi.Session, playlist_id: str, playlist_path: str) -> None:
    """Writes the given playlist as JSON to the given path."""
    playlist = session.playlist(playlist_id)

    playlist_tracks = []

    offset = 0

    while tracks := playlist.tracks(offset=offset):
        offset += len(tracks)

        for track in tracks:
            playlist_tracks.append(
                dict(
                    name=track.name,
                    artist=track.artist.name,
                    album=track.album.name,
                    version=track.version,
                    num=track.track_num,
                    id=track.id,
                    artists=[a.name for a in track.artists],
                )
            )
        time.sleep(RATE_LIMIT_SLEEP_SECONDS)

        with open(playlist_path, "w", encoding="utf-8") as tracks_f:
            json.dump(playlist_tracks, tracks_f, default=str)


def main():
    """Does the magic."""
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_f:
        config = json.load(config_f)

    session = tidalapi.Session()
    auth.login(session, PATH_TO_CREDS)

    datestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    playlist_path = f"{config['playlist_name']}.{datestamp}.json"

    write_playlist(session, config["playlist_id"], playlist_path)
    print(f"Wrote Tidal Playlist to {playlist_path}")


if __name__ == "__main__":
    main()
