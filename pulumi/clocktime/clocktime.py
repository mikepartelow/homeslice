"""Resources for the homeslice/clocktime app."""

import pulumi
import homeslice
from homeslice_config import ClocktimeConfig


class Clocktime(pulumi.ComponentResource):
    """Clocktime app resources."""

    def __init__(self, name: str, config: ClocktimeConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:clocktime:Clocktime", name, {}, opts)

        image = config.image
        container_port = config.container_port
        location = config.location
        ingress_prefix = config.ingress_prefix

        self.configmap = homeslice.configmap(
            name,
            {
                "LOCATION": location,
            },
        )

        env_from = [homeslice.env_from_configmap(name)]

        ports = [homeslice.port(container_port, name="http")]

        self.deployment = homeslice.deployment(name, image, env_from=env_from, ports=ports)

        self.service = homeslice.service(name)

        if ingress_prefix:
            self.ingress = homeslice.ingress(name, [ingress_prefix])

        self.register_outputs({})


def app(config: ClocktimeConfig) -> None:
    """define resources for the homeslice/clocktime app"""
    Clocktime("clocktime", config)
