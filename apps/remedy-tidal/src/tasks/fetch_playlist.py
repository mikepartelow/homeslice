import flytekit as fl  # type: ignore[import-untyped]
from core import model
from orchestration import image_spec


@fl.task(container_image=image_spec.DEFAULT, cache=True, cache_version="v1")
def fetch_playlist(playlist_id: str, path_to_creds: str) -> model.Playlist:
    print(f"🔑 Reading credentials from {path_to_creds}")
    print(f"🥡 Fetching Tidal Playlist {playlist_id}")

    return [
        model.Track(name="foo", id=1),
        model.Track(name="bar", id=2),
    ]

    # import tidalapi
    # from tidal import auth, playlist

    # session = tidalapi.Session()
    # auth.login(session, path_to_creds)

    #     playlist.write(session, playlist_id, playlist_path)
    #     print(f"🎵 Wrote Tidal Playlist to {playlist_path}")
