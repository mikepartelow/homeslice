"""Resources for the homeslice/sonos app."""

from pathlib import Path

import pulumi_kubernetes as kubernetes
import homeslice_config
import homeslice
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    sonos as SONOS_SECRETS,
)

NAME = "sonos"


def app(config: homeslice_config.SonosConfig) -> None:
    """define resources for the homeslice/sonos app"""

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=config.container_port,
        )
    ]

    homeslice.configmap(
        NAME,
        {
            "CONFIG_PATH": config.config_path,
            "SONOS_IPS": ",".join(SONOS_SECRETS.ZONE_IPS),
            "VOLUME": str(config.volume),
        },
    )

    with open("../apps/sonos/config/config.yaml", encoding="utf-8") as f:
        homeslice.configmap(
            f"{NAME}-config",
            {
                Path(config.config_path).name: f.read(),
            },
        )

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=f"{NAME}-config",
            mount_path=str(Path(config.config_path).parent),
            read_only=True,
        )
    ]

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=f"{NAME}-config",
            config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                name=f"{NAME}-config",
            ),
        ),
    ]

    env_from = [homeslice.env_from_configmap(NAME)]

    homeslice.deployment(
        NAME,
        config.image,
        env_from=env_from,
        ports=ports,
        volume_mounts=volume_mounts,
        volumes=volumes,
    )

    homeslice.service(NAME)

    # pylint: disable=R0801
    homeslice.ingress(
        NAME,
        [config.ingress_prefix],
        path_type="ImplementationSpecific",
        metadata=homeslice.metadata(
            NAME,
            annotations={
                "nginx.ingress.kubernetes.io/use-regex": "true",
                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
            },
        ),
    )


# avoid "name" that could confuse siri

# {
#     "accessory": "Http",
#     "name": "gabbagool",
#     "switchHandling": "no",
#     "http_method": "POST",
#     "on_url": "http://moe.localdomain/api/v0/sonos/playlists/mega-playlist/on",
#     "off_url": "http://moe.localdomain/api/v0/sonos/status",
#     "status_on": "ON",
#     "status_off": "OFF",
#     "service": "Switch",
#     "sendimmediately": "",
#     "username": "",
#     "password": "",
# }

# {
#     "accessory": "Http",
#     "name": "dog nap",
#     "switchHandling": "no",
#     "http_method": "POST",
#     "on_url": "http://moe.localdomain/api/v0/sonos/playlists/dog-nap/on",
#     "off_url": "http://moe.localdomain/api/v0/sonos/status",
#     "status_on": "ON",
#     "status_off": "OFF",
#     "service": "Switch",
#     "sendimmediately": "",
#     "username": "",
#     "password": "",
# }
