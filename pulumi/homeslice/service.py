"""kubernetes Service factory"""
import pulumi_kubernetes as kubernetes
import homeslice


def service(
    name: str,
) -> kubernetes.core.v1.Service:
    """THE kubernetes Service factory"""

    metadata = homeslice.metadata(name)

    return kubernetes.core.v1.Service(
        name,
        metadata=metadata,
        spec=kubernetes.core.v1.ServiceSpecArgs(
            selector=metadata.labels,
            type="NodePort",
            ports=[
                kubernetes.core.v1.ServicePortArgs(
                    name="http",
                    protocol="TCP",
                    port=80,
                    target_port="http",
                )
            ],
        ),
    )
