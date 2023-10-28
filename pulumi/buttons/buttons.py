"""Resources for the homeslice/buttons app."""

import pulumi
import pulumi_kubernetes as kubernetes
import homeslice

NAME = "buttons"


def app(namespace: str, config: pulumi.Config) -> None:
    """define resources for the homeslice/buttons app"""
    image = config["image"]
    container_port = int(config["container_port"])
    clocktime_url = config["clocktime_url"]
    ingress_enabled = config.get("ingress_enabled", "false") is True
    ingress_prefixes = config.get("ingress_prefixes")

    metadata = homeslice.metadata(NAME, namespace)

    kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data={
            "CLOCKTIME_URL": clocktime_url,
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

    if ingress_enabled:
        homeslice.ingress(NAME, metadata, ingress_prefixes)
