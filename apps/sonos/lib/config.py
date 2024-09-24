"""Pydantic models for our configuration."""

from typing import Literal, Mapping, Sequence
from pydantic import BaseModel


class PlaylistConfig(BaseModel):
    """A Playlist."""

    service: Literal["TIDAL",]
    title: str
    track_ids: Sequence[int | str]


class StationConfig(BaseModel):
    """A streaming radio station."""

    url: str
    title: str


class SonosConfig(BaseModel):
    """Configuration for this application."""

    playlists: Mapping[str, PlaylistConfig]
    stations: Mapping[str, StationConfig]
