"""Resources for the homeslice/clocktime app."""

import homeslice
from homeslice_config import ClocktimeConfig

NAME = "clocktime"


def app(config: ClocktimeConfig) -> None:
    """define resources for the homeslice/clocktime app"""
    image = config.image
    container_port = config.container_port
    location = config.location
    ingress_prefix = config.ingress_prefix

    homeslice.configmap(
        NAME,
        {
            "LOCATION": location,
        },
    )

    env_from = [homeslice.env_from_configmap(NAME)]

    ports = [homeslice.port(container_port, name="http")]

    homeslice.deployment(NAME, image, env_from=env_from, ports=ports)

    homeslice.service(NAME)

    if ingress_prefix:
        homeslice.ingress(NAME, [ingress_prefix])
