from pydantic import BaseModel
from typing import List, TypeAlias

class Track(BaseModel):
    name: str
    id: int


Playlist: TypeAlias = List[Track]
