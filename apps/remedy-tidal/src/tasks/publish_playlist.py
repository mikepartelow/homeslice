"""Flyte task for publishing a new Tidal playlist."""

import flytekit as fl  # type: ignore[import-untyped]

from core import model
from core.tidal import auth
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
def publish_playlist(tracks: list[model.Track], new_playlist_name: str, path_to_creds: str) -> str:
    """Publish a Tidal playlist. Create a new playlist if needed. Return playlist id."""
    session = auth.login(path_to_creds)

    new_playlist = None
    for candidate in session.user.playlists():
        if candidate.name == new_playlist_name:
            new_playlist = candidate
            break

    if not new_playlist:
        new_playlist = session.user.create_playlist(new_playlist_name, new_playlist_name)

    track_ids = [t.id for t in tracks]

    max_add = min(100, len(track_ids))
    start, finish = 0, max_add
    while finish <= len(track_ids):
        new_playlist.add(track_ids[start:finish])
        start, finish = finish, finish + max_add

    return new_playlist.id
