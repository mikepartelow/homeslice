"""Resources for the homeslice/buttons app."""

import homeslice
from homeslice_config import ButtonsConfig

NAME = "buttons"


def app(config: ButtonsConfig) -> None:
    """define resources for the homeslice/buttons app"""
    image = config.image
    container_port = config.container_port
    clocktime_url = config.clocktime_url
    ingress_prefixes = config.ingress_prefixes

    homeslice.configmap(
        NAME,
        {
            "CLOCKTIME_URL": clocktime_url,
        },
    )

    env_from = [homeslice.env_from_configmap(NAME)]

    ports = [homeslice.port(container_port, name="http")]

    homeslice.deployment(NAME, image, env_from=env_from, ports=ports)

    homeslice.service(NAME)

    if ingress_prefixes:
        homeslice.ingress(NAME, ingress_prefixes)
