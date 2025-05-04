from pydantic import BaseModel, Field
from typing import List, Optional


class Track(BaseModel):
    id: int
    name: str
    artist: str = Field(default="")
    album: str = Field(default="")
    artists: List[str] = Field(default=[])
    num: int = Field(default=0)
    version: Optional[str] = Field(default=None)
    available: bool
