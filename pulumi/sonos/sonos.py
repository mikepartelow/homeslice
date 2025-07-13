"""Resources for the homeslice/sonos app."""

from pathlib import Path
from pulumi_command import local
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    sonos as SONOS_SECRETS,
)


class Sonos(pulumi.ComponentResource):
    """Sonos app resources."""

    def __init__(self, name: str, config: homeslice_config.SonosConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:sonos:Sonos", name, {}, opts)

        ports = [
            kubernetes.core.v1.ContainerPortArgs(
                name="http",
                container_port=config.container_port,
            )
        ]

        self.configmap = homeslice.configmap(
            name,
            {
                "CONFIG_PATH": config.config_path,
                "SONOS_IPS": ",".join(SONOS_SECRETS.ZONE_IPS),
                "VOLUME": str(config.volume),
            },
        )

        with open("homeslice_secrets/gosonos-config.yaml", encoding="utf-8") as f:
            self.config_configmap = homeslice.configmap(
                f"{name}-config",
                {
                    Path(config.config_path).name: f.read(),
                },
            )

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=f"{name}-config",
                mount_path=str(Path(config.config_path).parent),
                read_only=True,
            )
        ]

        volumes = [
            kubernetes.core.v1.VolumeArgs(
                name=f"{name}-config",
                config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                    name=f"{name}-config",
                ),
            ),
        ]

        env_from = [homeslice.env_from_configmap(name)]

        self.deployment = homeslice.deployment(
            name,
            config.image,
            args=["serve"],
            env_from=env_from,
            ports=ports,
            volume_mounts=volume_mounts,
            volumes=volumes,
        )

        kconfig = pulumi.Config("kubernetes")
        context = kconfig.require("context")

        self.roll_command = local.Command(
            "roll-sonos",
            opts=pulumi.ResourceOptions(depends_on=[self.config_configmap]),
            create=f"zsh -c 'kubectl --context {context} rollout restart deployment/{name} -n homeslice'",  # pylint: disable=C0301
            triggers=[self.config_configmap],
        )

        self.service = homeslice.service(name)

        if config.ingress_prefix:
            # pylint: disable=R0801
            self.ingress = homeslice.ingress(
                name,
                [config.ingress_prefix],
                path_type="ImplementationSpecific",
                metadata=homeslice.metadata(
                    name,
                    annotations={
                        "nginx.ingress.kubernetes.io/use-regex": "true",
                        "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                    },
                ),
            )

        self.register_outputs({})


def app(config: homeslice_config.SonosConfig) -> None:
    """Define resources for the homeslice/sonos app.
    
    Creates a Sonos ComponentResource with deployment, service, ingress, and configmap
    for serving Sonos control functionality.
    """
    Sonos("sonos", config)


# avoid "name" that could confuse siri

# {
#     "accessory": "Http",
#     "name": "gabbagool",
#     "switchHandling": "yes",
#     "http_method": "POST",
#     "on_url": "http://moe.localdomain/api/v0/sonos/playlists/mega-playlist/on",
#     "off_url": "http://moe.localdomain/api/v0/sonos/playlists/mega-playlist/off",
#     "status_url": "http://moe.localdomain/api/v0/sonos/playlists/mega-playlist/status"
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
#     "switchHandling": "yes",
#     "http_method": "POST",
#     "on_url": "http://moe.localdomain/api/v0/sonos/playlists/dog-nap/on",
#     "off_url": "http://moe.localdomain/api/v0/sonos/playlists/dog-nap/off",
#     "status_url": "http://moe.localdomain/api/v0/sonos/playlists/dog-nap/status",
#     "status_on": "ON",
#     "status_off": "OFF",
#     "service": "Switch",
#     "sendimmediately": "",
#     "username": "",
#     "password": "",
# }
