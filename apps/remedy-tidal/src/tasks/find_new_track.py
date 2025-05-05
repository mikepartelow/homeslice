"""Flyte task for finding tracks in Tidal that match a given model.Track."""

import flytekit as fl  # type: ignore[import-untyped]

from core import model
from core.tidal import auth, track
from orchestration import image_spec, secrets
import logging

@fl.task(
    container_image=image_spec.DEFAULT,
    secret_requests=[
        fl.Secret(
            group=secrets.TIDAL_CREDS_GROUP,
            key=secrets.TIDAL_CREDS_KEY,
            mount_requirement=fl.Secret.MountType.FILE,
        )
    ],
    cache=True,
    cache_version="v5",
)
def find_new_track(old_track: model.Track, path_to_creds: str) -> model.Track | None:
    """Find a reasonable replacement for the given track."""
    logging.debug("path_to_creds: %s", path_to_creds)
    session = auth.login(path_to_creds)
    return track.find(session, old_track)
