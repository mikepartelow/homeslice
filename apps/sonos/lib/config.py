from typing import Sequence, Mapping
from pydantic import BaseModel

class PlaylistConfig(BaseModel):
    service: str # FIXME: validate this is TIDAL
    title: str
    track_ids: Sequence[int|str]

class StationConfig(BaseModel):
    url: str
    title: str

class SonosConfig(BaseModel):
    playlists: Mapping[str, PlaylistConfig]
    stations: Mapping[str, StationConfig]
