import flytekit as fl  # type: ignore[import-untyped]
from core import model
from orchestration import image_spec, secrets
from typing import List
import tidalapi  # type: ignore[import-untyped]
from core.tidal import auth, playlist


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
def fetch_playlist(playlist_id: str, path_to_creds: str) -> List[model.Track]:
    session = tidalapi.Session()
    auth.login(session, path_to_creds)
    return playlist.fetch(session, playlist_id)
