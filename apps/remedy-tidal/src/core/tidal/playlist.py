"""Tidal playlist helpers."""

import time

import tidalapi  # type: ignore[import-untyped]

from .. import model


def fetch(
    session: tidalapi.Session,
    playlist_id: str,
    rate_limit_sleep_seconds: int = 8,
) -> list[model.Track]:
    """Fetch a playlist from Tidal."""
    playlist = session.playlist(playlist_id)

    playlist_tracks = []

    offset = 0

    while tracks := playlist.tracks(offset=offset):
        offset += len(tracks)

        for track in tracks:
            playlist_tracks.append(model.Track.from_tidal(track))

        time.sleep(rate_limit_sleep_seconds)

    return playlist_tracks
