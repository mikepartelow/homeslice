"""kubernetes Secret factory"""

import pulumi_kubernetes as kubernetes
import homeslice


def secret(
    name: str, data: dict | None = None, string_data: dict | None = None
) -> kubernetes.core.v1.Secret:
    """THE kubernetes Secret factory"""
    return kubernetes.core.v1.Secret(
        name,
        metadata=homeslice.metadata(name),
        type="Opaque",
        data=data,
        string_data=string_data,
    )
