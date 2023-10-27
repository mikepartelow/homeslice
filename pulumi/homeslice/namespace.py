import pulumi_kubernetes as kubernetes
import homeslice


def namespace(name: str) -> kubernetes.core.v1.Namespace:
    return kubernetes.core.v1.Namespace(name, metadata=homeslice.metadata(name, name))
