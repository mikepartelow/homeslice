import flytekit as fl  # type: ignore[import-untyped]
from orchestration import image_spec
from core import model
from typing import Optional


@fl.task(container_image=image_spec.DEFAULT, cache_version="v2")
def find_new_track(old_track: model.Track, path_to_creds: str) -> Optional[model.Track]:
    if old_track.name == "bar":
        return model.Track(id=5, name=old_track.name, available=True)
    return None
