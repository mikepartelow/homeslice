"""kubernetes Configmap factory"""

import pulumi_kubernetes as kubernetes
import homeslice

def configmap(name: str, data: dict) -> kubernetes.core.v1.Namespace:
    """THE kubernetes Configmap factory"""
    return kubernetes.core.v1.ConfigMap(
        name,
        metadata=homeslice.metadata(name),
        data=data,
    )
