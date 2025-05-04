import flytekit as fl  # type: ignore[import-untyped]
from orchestration import image_spec
from core import model
from typing import List, Optional


@fl.task(container_image=image_spec.DEFAULT)
def filter_nones(tracks: List[Optional[model.Track]]) -> List[model.Track]:
    return [t for t in tracks if t is not None]


@fl.task(container_image=image_spec.DEFAULT)
def filter_unavailable(playlist: List[model.Track]) -> List[model.Track]:
    return [t for t in playlist if not t.available]
