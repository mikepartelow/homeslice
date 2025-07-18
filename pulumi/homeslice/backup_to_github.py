"""Abstract common resources for backing things up to Github"""

from pathlib import Path
from typing import List
import pulumi_kubernetes as kubernetes
import homeslice
import homeslice_config


class BackupToGithub:
    """Abstract common resources for backing things up to Github.

    Each @property is required to be read by callers."""

    def __init__(self, app_name: str, config: homeslice_config.GithubBackupConfig):
        self.app_name = app_name
        self.config = config

        self.ssh_secret_name = f"{self.app_name}-ssh"
        self.ssh_known_hosts_name = f"{self.app_name}-known-hosts"

        self.ssh_known_hosts = "github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl"  # pylint:disable=line-too-long

    @property
    def configmap_items(self) -> dict:
        """Required configmap items. Use with env_from()."""
        return {
            self.config.ssh_private_key_path_env_var_name: self.config.ssh_private_key_path,
            self.config.ssh_known_hosts_path_env_var_name: self.config.ssh_known_hosts_path,
            str(Path(self.config.ssh_known_hosts_path).name): self.ssh_known_hosts,
            self.config.git_author_name_env_var_name: self.config.git_author_name,
            self.config.git_author_email_env_var_name: self.config.git_author_email,
        }

    @property
    def secret_items(self) -> dict:
        """Required secret items. Use with env_from()."""
        return {
            self.config.git_clone_url_env_var_name: str(self.config.git_clone_url) if self.config.git_clone_url is not None else "",
        }

    @property
    def ssh_secret(self) -> kubernetes.core.v1.Secret:
        """Required SSH secret. Callers should read this property to create the secret,
        but don't need to directly reference it."""
        key = self.config.ssh_private_key
        if isinstance(key, bytes):
            key_str = key.decode()
        elif key is None:
            key_str = ""
        else:
            key_str = key  # type: ignore
        return kubernetes.core.v1.Secret(
            self.ssh_secret_name,
            metadata=homeslice.metadata(self.ssh_secret_name),
            type="kubernetes.io/ssh-auth",
            string_data={
                "ssh-privatekey": key_str,
            },
        )

    @property
    def volume_mounts(self) -> List[kubernetes.core.v1.VolumeMountArgs]:
        """Required volume mounts, including the SSH secret."""
        return [
            kubernetes.core.v1.VolumeMountArgs(
                name=self.ssh_secret_name,
                mount_path=str(Path(self.config.ssh_private_key_path).parent),
                read_only=True,
            ),
            kubernetes.core.v1.VolumeMountArgs(
                name=self.ssh_known_hosts_name,
                mount_path=str(Path(self.config.ssh_known_hosts_path).parent),
                read_only=True,
            ),
        ]

    @property
    def volumes(self) -> List[kubernetes.core.v1.VolumeArgs]:
        """Required volumes, including SSH secret."""
        return [
            kubernetes.core.v1.VolumeArgs(
                name=self.ssh_secret_name,
                secret=kubernetes.core.v1.SecretVolumeSourceArgs(
                    secret_name=self.ssh_secret_name,
                    default_mode=0o444,
                ),
            ),
            kubernetes.core.v1.VolumeArgs(
                name=self.ssh_known_hosts_name,
                config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                    name=self.app_name,
                    default_mode=0o444,
                    items=[
                        kubernetes.core.v1.KeyToPathArgs(
                            key=str(Path(self.config.ssh_known_hosts_path).name),
                            path=str(Path(self.config.ssh_known_hosts_path).name),
                        )
                    ],
                ),
            ),
        ]

    @property
    def env_from(self) -> List[kubernetes.core.v1.EnvFromSourceArgs]:
        """Required env_from items, including required configmaps and secrets."""
        return [
            homeslice.env_from_configmap(self.app_name),
            homeslice.env_from_secret(self.app_name),
        ]
