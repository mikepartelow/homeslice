"""Resources for the homeslice/buttons app."""

import pulumi
import homeslice
from homeslice_config import ButtonsConfig


class Buttons(pulumi.ComponentResource):
    """Buttons app resources."""

    def __init__(self, name: str, config: ButtonsConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:buttons:Buttons", name, {}, opts)

        image = config.image
        container_port = config.container_port
        clocktime_url = config.clocktime_url
        ingress_prefixes = config.ingress_prefixes

        self.configmap = homeslice.configmap(
            name,
            {
                "CLOCKTIME_URL": clocktime_url,
            },
        )

        env_from = [homeslice.env_from_configmap(name)]

        ports = [homeslice.port(container_port, name="http")]

        self.deployment = homeslice.deployment(name, image, env_from=env_from, ports=ports)

        self.service = homeslice.service(name)

        if ingress_prefixes:
            self.ingress = homeslice.ingress(name, ingress_prefixes)

        self.register_outputs({})


def app(config: ButtonsConfig) -> None:
    """define resources for the homeslice/buttons app"""
    Buttons("buttons", config)
