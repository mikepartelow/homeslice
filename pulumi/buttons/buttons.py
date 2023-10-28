"""Resources for the homeslice/buttons app."""

import pulumi
import pulumi_kubernetes as kubernetes
import homeslice

NAME = "buttons"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/buttons app"""
    image = config["image"]
    container_port = int(config["container_port"])
    clocktime_url = config["clocktime_url"]
    ingress_prefixes = config.get("ingress_prefixes")

    homeslice.configmap(NAME, {
        "CLOCKTIME_URL": clocktime_url,
    })

    env_from = [homeslice.env_from_configmap(NAME)]

    ports = [homeslice.port(container_port, name="http")]

    homeslice.deployment(NAME, image, env_from=env_from, ports=ports)

    homeslice.service(NAME)

    homeslice.ingress(NAME, ingress_prefixes)
