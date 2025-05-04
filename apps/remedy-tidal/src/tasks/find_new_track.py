"""Flyte task for finding tracks in Tidal that match a given model.Track."""

import flytekit as fl  # type: ignore[import-untyped]
import tidalapi  # type: ignore[import-untyped]

from core import model
from core.tidal import auth, track
from orchestration import image_spec


@fl.task(container_image=image_spec.DEFAULT, cache_version="v2")
def find_new_track(old_track: model.Track, path_to_creds: str) -> model.Track | None:
    """Find a reasonable replacement for the given track."""
    session = tidalapi.Session()
    auth.login(session, path_to_creds)
    return track.find(session, old_track)
