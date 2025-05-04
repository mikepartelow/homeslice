import flytekit as fl  # type: ignore[import-untyped]
from core import model
from orchestration import image_spec
from typing import List


@fl.task(container_image=image_spec.DEFAULT, cache=True, cache_version="v2")
def fetch_playlist(playlist_id: str, path_to_creds: str) -> List[model.Track]:
    print(f"🔑 Reading credentials from {path_to_creds}")
    print(f"🥡 Fetching Tidal Playlist {playlist_id}")

    return [
        model.Track(id=1, name="foo", available=True),
        model.Track(id=2, name="bar", available=False),
        model.Track(id=3, name="baz", available=True),
        model.Track(id=3, name="thip", available=False),
    ]

    # import tidalapi
    # from tidal import auth, playlist

    # session = tidalapi.Session()
    # auth.login(session, path_to_creds)

    #     playlist.write(session, playlist_id, playlist_path)
    #     print(f"🎵 Wrote Tidal Playlist to {playlist_path}")
