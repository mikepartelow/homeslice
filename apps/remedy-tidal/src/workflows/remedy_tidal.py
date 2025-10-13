"""Flyte workflow for remedying Tidal playlists.

Over time, a Tidal playlist experiences bitrot, pointing to tracks that are no longer available.

This workflow scans a given playlist for unavailable tracks, publishes reasonable replacement tracks
to a new playlist, creating the new playlist if necessary.
"""

import functools
import logging

import flytekit as fl  # type: ignore[import-untyped]

import core.logging
import tasks
from orchestration import secrets


@fl.workflow
def remedy_tidal_wf(
    playlist_id: str,
    new_playlist_name: str,
    path_to_creds: str = secrets.TIDAL_CREDS_PATH,
) -> str:
    """Remedy a Tidal playlist. Publish remedied tracks to new_playlist_name and return its id.

    Tidal tracks can become unavailable. This workflow finds those tracks and publishes reasonable
    alternatives to a new playlist.
    """
    core.logging.init()

    logging.info("remedy tidal wf(%s, %s, %s)", playlist_id, new_playlist_name, path_to_creds)

    playlist = tasks.fetch_playlist(playlist_id, path_to_creds)

    unavailable = tasks.filter_unavailable(playlist)

    partial_task = functools.partial(tasks.find_new_track, path_to_creds=path_to_creds)

    new_tracks = fl.map_task(partial_task)(old_track=unavailable)

    remedied = tasks.filter_nones(new_tracks)

    new_playlist_id = tasks.publish_playlist(remedied, new_playlist_name, path_to_creds)

    return new_playlist_id


if __name__ == "__main__":
    import sys

    print(remedy_tidal_wf(sys.argv[1], sys.argv[2], sys.argv[3]))  # noqa: T201
