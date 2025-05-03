import flytekit as fl  # type: ignore[import-untyped]
import os

DEFAULT = fl.ImageSpec(
    name="remedy-tidal-image",
    requirements="uv.lock",
    registry=os.environ.get("FLYTE_IMAGE_REGISTRY"),
)
