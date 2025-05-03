# Hello World

from pydantic import BaseModel
from typing import List, TypeAlias
import flytekit as fl  # type: ignore[import-untyped]
import os


PATH_TO_CACHE = "/tmp/remedy.cache.json"


image_spec = fl.ImageSpec(
    name="remedy-tidal-image",
    requirements="uv.lock",
    registry=os.environ.get("FLYTE_IMAGE_REGISTRY")
)


# FIXME: move these to a model.py
# FIXME: https://www.union.ai/docs/flyte/user-guide/development-cycle/project-structure/
class Track(BaseModel):
    name: str
    id: int

Playlist: TypeAlias = List[Track]


@fl.task(container_image=image_spec, cache=True, cache_version="v1")
def fetch_playlist(playlist_id: str, path_to_creds: str) -> Playlist:
    print(f"🔑 Reading credentials from {path_to_creds}")
    print(f"🥡 Fetching Tidal Playlist {playlist_id}")

    return [
        Track(name="foo", id=1),
        Track(name="bar", id=2),
    ]

    # import tidalapi
    # from tidal import auth, playlist

    # session = tidalapi.Session()
    # auth.login(session, path_to_creds)

    #     playlist.write(session, playlist_id, playlist_path)
    #     print(f"🎵 Wrote Tidal Playlist to {playlist_path}")


# TODO: playlist should be pydantic
@fl.task(container_image=image_spec)
def get_last_title(playlist: Playlist) -> str:
    return playlist[-1].name


@fl.task(container_image=image_spec)
def decorate_title(title: str) -> str:
    return f"🎬 Last title: {title}"

@fl.workflow
def remedy_tidal_wf(playlist_id: str, path_to_creds: str) -> str:
    playlist = fetch_playlist(playlist_id, path_to_creds)

    last_title = get_last_title(playlist=playlist)

    return decorate_title(last_title)

if __name__ == "__main__":
    import sys
    print(remedy_tidal_wf(sys.argv[1], sys.argv[2]))
