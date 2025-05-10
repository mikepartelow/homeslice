"""Flyte task for fetching Tidal playlists."""

import flytekit as fl  # type: ignore[import-untyped]

from core import model
from core.tidal import auth, playlist
from orchestration import image_spec, secrets


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
def fetch_playlist(playlist_id: str, path_to_creds: str) -> list[model.Track]:
    """Fetch the given playlist from Tidal."""
    session = auth.login(path_to_creds)
    return playlist.fetch(session, playlist_id)
