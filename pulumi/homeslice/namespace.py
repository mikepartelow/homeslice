"""kubernetes Namespace factory"""

import pulumi_kubernetes as kubernetes
import homeslice


def namespace(name: str) -> kubernetes.core.v1.Namespace:
    """THE kubernetes Namespace factory"""
    return kubernetes.core.v1.Namespace(name, metadata=homeslice.metadata(name, name))
