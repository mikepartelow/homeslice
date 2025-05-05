"""Flyte tasks for filtering playlists of model.Tracks."""

import flytekit as fl  # type: ignore[import-untyped]

from core import model
from orchestration import image_spec


@fl.task(container_image=image_spec.DEFAULT)
def filter_nones(tracks: list[model.Track | None]) -> list[model.Track]:
    """Return the given list of tracks with any None elements removed."""
    return [t for t in tracks if t is not None]


@fl.task(
    container_image=image_spec.DEFAULT,
    cache=True,
    cache_version="v5",
)
def filter_unavailable(playlist: list[model.Track]) -> list[model.Track]:
    """Return a list of unavailable tracks from playlist."""
    return [t for t in playlist if not t.available]
