"""Resources for the homeslice/lmz app."""

from pathlib import Path
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    lmz as LMZ_SECRETS,
)


class Lmz(pulumi.ComponentResource):
    """Lmz app resources."""

    def __init__(self, name: str, config: homeslice_config.LmzConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:lmz:Lmz", name, {}, opts)

        installation_key_secret_name = f"{name}-installation-key"
        self.installation_key_secret = homeslice.secret(
            installation_key_secret_name,
            string_data={
                Path(config.installation_key_json_path).name: LMZ_SECRETS.INSTALLATION_KEY_JSON,
            },
        )

        creds_secret_name = f"{name}-creds"
        self.creds_secret = homeslice.secret(
            creds_secret_name,
            string_data={
                Path(config.creds_txt_path).name: LMZ_SECRETS.CREDS_TXT,
            },
        )

        volumes = [
            kubernetes.core.v1.VolumeArgs(
                name=installation_key_secret_name,
                secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                    secret_name=installation_key_secret_name,
                ),
            ),
            kubernetes.core.v1.VolumeArgs(
                name=creds_secret_name,
                secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                    secret_name=creds_secret_name,
                ),
            ),
        ]

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=installation_key_secret_name,
                mount_path=str(Path(config.installation_key_json_path).parent),
                read_only=True,
            ),
            kubernetes.core.v1.VolumeMountArgs(
                name=creds_secret_name,
                mount_path=str(Path(config.creds_txt_path).parent),
                read_only=True,
            ),
        ]

        ports = [homeslice.port(config.container_port)]

        self.deployment = homeslice.deployment(  # pylint: disable=R0801
            name,
            config.image,
            args=["serve"],
            ports=ports,
            volumes=volumes,
            volume_mounts=volume_mounts,
            env=[
                kubernetes.core.v1.EnvVarArgs(
                    name="INSTALLATION_KEY_PATH",
                    value=config.installation_key_json_path,
                ),
                kubernetes.core.v1.EnvVarArgs(
                    name="CREDS_PATH",
                    value=config.creds_txt_path,
                ),
            ],
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
