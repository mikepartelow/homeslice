"""Flyte image specs."""

import os

import flytekit as fl  # type: ignore[import-untyped]

DEFAULT = fl.ImageSpec(
    name="remedy-tidal-dev",
    requirements="uv.lock",
    registry=os.environ.get("FLYTE_IMAGE_REGISTRY"),
)
