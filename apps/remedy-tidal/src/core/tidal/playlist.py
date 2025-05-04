"""Functions for manipulating Tidal playlists."""

import time
import tidalapi  # type: ignore[import-untyped]
from .. import model
from typing import List


def fetch(
    session: tidalapi.Session,
    playlist_id: str,
    rate_limit_sleep_seconds: int = 8,
) -> List[model.Track]:
    print(f"🥡 Fetching Tidal Playlist {playlist_id}")

    playlist = session.playlist(playlist_id)

    playlist_tracks = []

    offset = 0

    while tracks := playlist.tracks(offset=offset):
        offset += len(tracks)

        for track in tracks:
            playlist_tracks.append(
                model.Track(
                    name=track.name,
                    artist=track.artist.name,
                    album=track.album.name,
                    version=track.version,
                    num=track.track_num,
                    id=track.id,
                    artists=[a.name for a in track.artists],
                    available=track.available,
                )
            )
        time.sleep(rate_limit_sleep_seconds)

    return playlist_tracks
