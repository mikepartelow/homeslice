"""Resources for the homeslice/sonos app."""

import pulumi_kubernetes as kubernetes
import pulumi
import homeslice

NAME = "sonos"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/sonos app"""
    image = config["image"]
    container_port = int(config["container_port"])
    ingress_prefix = config.get("ingress_prefix")

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=container_port,
        )
    ]

    homeslice.deployment( NAME, image, ports=ports )

    homeslice.service(NAME)

    homeslice.ingress(
        NAME,
        [ingress_prefix],
        path_type="ImplementationSpecific",
        metadata=homeslice.metadata(
            NAME,
            annotations={
                "nginx.ingress.kubernetes.io/use-regex": "true",
                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
            },
        ),
    )

    # {
    #     "accessory": "Http",
    #     "name": "Secret Agent",
    #     "switchHandling": "yes",
    #     "http_method": "GET",
    #     "on_url": "http://nucnuc.local/api/v0/sonos/secret-agent/ON",
    #     "off_url": "http://nucnuc.local/api/v0/sonos/secret-agent/OFF",
    #     "status_url": "http://nucnuc.local/api/v0/sonos/secret-agent/STATUS",
    #     "status_on": "ON",
    #     "status_off": "OFF",
    #     "service": "Switch",
    #     "sendimmediately": "",
    #     "username": "",
    #     "password": "",
    # }
