"""kubernetes Service factory"""

import pulumi_kubernetes as kubernetes
import homeslice


def service(
    name: str, port: int = 80, type_: str = "ClusterIP"
) -> kubernetes.core.v1.Service:
    """THE kubernetes Service factory"""

    metadata = homeslice.metadata(name)

    return kubernetes.core.v1.Service(
        name,
        metadata=metadata,
        spec=kubernetes.core.v1.ServiceSpecArgs(
            selector=metadata.labels,
            type=type_,
            ports=[
                kubernetes.core.v1.ServicePortArgs(
                    name="http",
                    protocol="TCP",
                    port=port,
                    target_port="http",
                )
            ],
        ),
    )
