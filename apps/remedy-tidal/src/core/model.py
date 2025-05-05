"""Pydantic models for our business logic."""

from typing import Self

import tidalapi  # type: ignore[import-untyped]
from pydantic import BaseModel, Field


class Track(BaseModel):
    """Track is a Tidal track."""

    id: int
    name: str
    artist: str = Field(default="")
    album: str = Field(default="")
    artists: list[str] = Field(default_factory=list)
    num: int = Field(default=0)
    version: str | None = Field(default=None)
    available: bool = Field(default=True)

    @classmethod
    def from_tidal(cls, ttrack: tidalapi.Track) -> Self:
        """Convert a tidalapi.Track to a model.Track."""
        return cls(
            name=ttrack.name,
            artist=ttrack.artist.name,
            album=ttrack.album.name,
            version=ttrack.version,
            num=ttrack.track_num,
            id=ttrack.id,
            artists=sorted([a.name for a in ttrack.artists]),
            available=ttrack.available,
        )
