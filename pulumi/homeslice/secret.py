"""kubernetes Secret factory"""

import pulumi_kubernetes as kubernetes
import homeslice
from typing import Optional, Dict, Any


def secret(
    name: str, data: Optional[Dict[str, Any]] = None, string_data: Optional[Dict[str, Any]] = None
) -> kubernetes.core.v1.Secret:
    """THE kubernetes Secret factory"""
    return kubernetes.core.v1.Secret(
        name,
        metadata=homeslice.metadata(name),
        type="Opaque",
        data=data,
        string_data=string_data,
    )
