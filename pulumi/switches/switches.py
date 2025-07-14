"""Resources for the homeslice/switches app."""

from pathlib import Path
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from homeslice_config import SwitchesConfig
from homeslice_secrets import (  # pylint: disable=no-name-in-module  # type: ignore
    switches as SWITCHES_SECRETS,
)


class Switches(pulumi.ComponentResource):
    """Switches app resources."""

    def __init__(self, name: str, config: SwitchesConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:switches:Switches", name, {}, opts)

        image = config.image
        container_port = config.container_port
        ingress_prefix = config.ingress_prefix
        switches_json = subst_address(config.switches_json)
        switches_json_path = config.switches_json_path
        switches_json_name = str(Path(switches_json_path).name)
        volume_name = switches_json_name.replace(".", "-")

        self.configmap = homeslice.configmap(
            name,
            {
                switches_json_name: switches_json,
            },
        )

        volumes = [
            kubernetes.core.v1.VolumeArgs(
                name=volume_name,
                config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                    name=name,
                ),
            ),
        ]

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=volume_name,
                mount_path=str(Path(switches_json_path).parent),
                read_only=True,
            ),
        ]

        ports = [homeslice.port(container_port)]

        self.deployment = homeslice.deployment(
            name,
            image,
            args=[switches_json_path],
            ports=ports,
            volumes=volumes,
            volume_mounts=volume_mounts,
        )

        self.service = homeslice.service(name)

        if ingress_prefix:
            self.ingress = homeslice.ingress(name, [ingress_prefix])

        self.register_outputs({})


# I don't want to publish IP addresses to GitHub
def subst_address(s: str) -> str:
    """Returns the given string with secrets substituted in.
    
    Replaces placeholder keys with actual IP addresses from SWITCHES_SECRETS.IP_ADDRESSES.
    """
    for k, v in SWITCHES_SECRETS.IP_ADDRESSES.items():
        s = s.replace(k, v)

    return s
