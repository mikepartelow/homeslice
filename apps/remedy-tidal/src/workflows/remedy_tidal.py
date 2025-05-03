import flytekit as fl  # type: ignore[import-untyped]
import tasks

@fl.workflow
def remedy_tidal_wf(playlist_id: str, path_to_creds: str) -> str:
    playlist = tasks.fetch_playlist(playlist_id, path_to_creds)

    last_title = tasks.get_last_title(playlist=playlist)

    return tasks.decorate_title(last_title)

if __name__ == "__main__":
    import sys
    print(remedy_tidal_wf(sys.argv[1], sys.argv[2]))
