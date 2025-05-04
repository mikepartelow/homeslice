import flytekit as fl  # type: ignore[import-untyped]
import tasks
from core import model
from typing import List
import functools
from orchestration import secrets


@fl.workflow
def remedy_tidal_wf(
    playlist_id: str, path_to_creds: str = secrets.TIDAL_CREDS_PATH
) -> List[model.Track]:
    playlist = tasks.fetch_playlist(playlist_id, path_to_creds)

    unavailable = tasks.filter_unavailable(playlist)

    partial_task = functools.partial(tasks.find_new_track, path_to_creds=path_to_creds)

    new_tracks = fl.map_task(partial_task)(old_track=unavailable)

    remedied = tasks.filter_nones(new_tracks)

    return remedied


if __name__ == "__main__":
    import sys

    print(remedy_tidal_wf(sys.argv[1], sys.argv[2]))
