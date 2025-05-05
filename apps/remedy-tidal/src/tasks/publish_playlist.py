"""Flyte task for publishing a new Tidal playlist."""

import flytekit as fl  # type: ignore[import-untyped]

from core import model
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
)
def publish_playlist(
    playlist: list[model.Track], new_playlist_name: str, path_to_creds: str
) -> str:
    """Publish a Tidal playlist. Create a new playlist if needed. Return playlist id."""
    return "1"
