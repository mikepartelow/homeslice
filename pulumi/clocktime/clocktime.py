"""Resources for the homeslice/clocktime app."""

import pulumi
import pulumi_kubernetes as kubernetes
import homeslice

NAME = "clocktime"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/clocktime app"""
    image = config["image"]
    container_port = int(config["container_port"])
    location = config["location"]
    ingress_prefix = config.get("ingress_prefix")

    homeslice.configmap(NAME, {
        "LOCATION": location,
    })

    env_from = [homeslice.env_from_configmap(NAME)]

    ports = [homeslice.port(container_port, name="http")]

    homeslice.deployment(NAME, image, env_from=env_from, ports=ports)

    homeslice.service(NAME)

    homeslice.ingress(NAME, [ingress_prefix])
