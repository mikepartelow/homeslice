"""Homeslice Config"""

from typing import Optional
from pydantic import BaseModel


class HomeBridgeConfig(BaseModel):
    """HomeBridge Config"""

    image: str
    redirect_host: str
    redirect_prefix: str


class LmzConfig(BaseModel):
    """LMZ Config"""

    image: str
    container_port: int
    lmz_yaml_path: str
    ingress_prefix: Optional[str]
