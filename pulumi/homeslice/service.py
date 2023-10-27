"""kubernetes Service factory"""
import pulumi_kubernetes as kubernetes


def service(
    name: str, metadata: kubernetes.meta.v1.ObjectMetaArgs
) -> kubernetes.core.v1.Service:
    """THE kubernetes Service factory"""
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
