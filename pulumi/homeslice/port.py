"""kubernetes port factory"""

import pulumi_kubernetes as kubernetes


def port(
    container_port: str,
    name: str = "http",
) -> kubernetes.meta.v1.ObjectMetaArgs:
    """THE kubernetes port factory"""

    return kubernetes.core.v1.ContainerPortArgs(
        container_port=container_port,
        name=name,
    )
