import flytekit as fl  # type: ignore[import-untyped]
from orchestration import image_spec
from core import model

# TODO: playlist should be pydantic
@fl.task(container_image=image_spec.DEFAULT)
def get_last_title(playlist: model.Playlist) -> str:
    return playlist[-1].name
