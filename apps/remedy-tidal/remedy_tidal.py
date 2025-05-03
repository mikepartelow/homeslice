# Hello World

import flytekit as fl  # type: ignore[import-not-found]
import os


PATH_TO_CACHE = "/tmp/remedy.cache.json"


image_spec = fl.ImageSpec(
    name="remedy-tidal-image",
    requirements="uv.lock",
    registry=os.environ.get("FLYTE_IMAGE_REGISTRY")
)


# https://www.union.ai/docs/flyte/user-guide/development-cycle/project-structure/

@fl.task(container_image=image_spec)
# FIXME: cache it
# TODO: can we return a pydantic model?
def fetch_playlist(playlist_id: str, path_to_creds: str) -> list[dict[str, str]]:

    # FIXME: for now, just return a dict, don't call any api

    print(f"🔑 Reading credentials from {path_to_creds}")
    print(f"🥡 Fetching Tidal Playlist {playlist_id}")

    return [
        {
            "name": "bar",
            "baz": "thip",
        },
        {
            "name": "wingle",
            "bar": "zazzle",
        },
    ]

    # import tidalapi
    # from tidal import auth, playlist

    # session = tidalapi.Session()
    # auth.login(session, path_to_creds)

    #     playlist.write(session, playlist_id, playlist_path)
    #     print(f"🎵 Wrote Tidal Playlist to {playlist_path}")


# TODO: playlist should be pydantic
@fl.task(container_image=image_spec)
def get_last_title(playlist: list[dict[str, str]]) -> str:
    return playlist[-1]["name"]


@fl.task(container_image=image_spec)
def decorate_title(title: str) -> str:
    return f"🎬 Last title: {title}"

@fl.workflow
def remedy_tidal_wf(playlist_id: str, path_to_creds: str) -> str:
    # FIXME: must be fetch_playlist not write_playlist: no side effects
    playlist = fetch_playlist(playlist_id, path_to_creds)

    last_title = get_last_title(playlist=playlist)

    return decorate_title(last_title)

if __name__ == "__main__":
    import sys
    print(remedy_tidal_wf(sys.argv[1], sys.argv[2]))
