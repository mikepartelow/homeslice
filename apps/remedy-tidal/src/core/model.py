from pydantic import BaseModel


class Track(BaseModel):
    available: bool
    id: int
    name: str
