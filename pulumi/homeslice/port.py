"""kubernetes port factory"""

import pulumi_kubernetes as kubernetes


def port(
    container_port: int,
    name: str = "http",
) -> kubernetes.core.v1.ContainerPortArgs:
    """THE kubernetes port factory"""

    return kubernetes.core.v1.ContainerPortArgs(
        container_port=container_port,
        name=name,
    )
