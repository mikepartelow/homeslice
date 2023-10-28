"""Resources for the homeslice/clocktime app."""

import pulumi
import pulumi_kubernetes as kubernetes
import homeslice

NAME = "clocktime"


def app(namespace: str, config: pulumi.Config) -> None:
    """define resources for the homeslice/clocktime app"""

    image = config["image"]
    container_port = int(config["container_port"])
    location = config["location"]
    ingress_prefix = config.get("ingress_prefix")

    metadata = homeslice.metadata(NAME, namespace)

    kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data={
            "LOCATION": location,
        },
    )

    env_from = [
        kubernetes.core.v1.EnvFromSourceArgs(
            config_map_ref=kubernetes.core.v1.ConfigMapEnvSourceArgs(
                name=NAME,
            )
        )
    ]

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=container_port,
        )
    ]

    homeslice.deployment(NAME, image, metadata, env_from=env_from, ports=ports)

    homeslice.service(NAME, metadata)

    homeslice.ingress(NAME, metadata, [ingress_prefix])
