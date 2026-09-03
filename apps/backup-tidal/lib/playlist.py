"""Functions for manipulating Tidal playlists."""

import json
import time
import tidalapi


def write(
    session: tidalapi.Session,
    playlist_id: str,
    playlist_path: str,
    rate_limit_sleep_seconds: int,
) -> None:
    """Writes the given playlist as JSON to the given path."""
    playlist = session.playlist(playlist_id)

    playlist_tracks = []

    offset = 0

    while tracks := playlist.tracks(offset=offset):
        offset += len(tracks)

        for track in tracks:
            playlist_tracks.append(
                {
                    "name": track.name,
                    "artist": track.artist.name,
                    "album": track.album.name,
                    "version": track.version,
                    "num": track.track_num,
                    "id": track.id,
                    "artists": [a.name for a in track.artists],
                    "available": track.available,
                }
            )
        time.sleep(rate_limit_sleep_seconds)

        with open(playlist_path, "w", encoding="utf-8") as tracks_f:
            json.dump(playlist_tracks, tracks_f, default=str, indent=2)
