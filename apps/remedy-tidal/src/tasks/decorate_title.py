import flytekit as fl  # type: ignore[import-untyped]
from orchestration import image_spec

@fl.task(container_image=image_spec.DEFAULT)
def decorate_title(title: str) -> str:
    return f"🎬 Last title: {title}"
