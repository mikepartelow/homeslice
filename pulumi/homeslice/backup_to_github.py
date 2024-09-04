from pathlib import Path
import homeslice_config
import pulumi_kubernetes as kubernetes
import homeslice


class BackupToGithub:
    def __init__(self, app_name: str, config: homeslice_config.GithubBackupConfig):
        self.app_name = app_name
        self.config = config

        self.ssh_secret_name = f"{self.app_name}-ssh"
        self.ssh_known_hosts_name = f"{self.app_name}-known-hosts"

        self.ssh_known_hosts = "github.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOMqqnkVzrm0SdG6UOoqKLsabgH5C9okWi0dh2l9GKJl"

    @property
    def configmap_items(self) -> dict:
        return {
            self.config.ssh_private_key_path_env_var_name: self.config.ssh_private_key_path,
            self.config.ssh_known_hosts_path_env_var_name: self.config.ssh_known_hosts_path,
            str(Path(self.config.ssh_known_hosts_path).name): self.ssh_known_hosts,
            self.config.git_author_name_env_var_name: self.config.git_author_name,
            self.config.git_author_email_env_var_name: self.config.git_author_email,
        }

    @property
    def secret_items(self) -> dict:
        return {
            self.config.git_clone_url_env_var_name: self.config.git_clone_url,  # secret
        }

    @property
    def ssh_secret(self) -> dict:
        return kubernetes.core.v1.Secret(
            self.ssh_secret_name,
            metadata=homeslice.metadata(self.ssh_secret_name),
            type="kubernetes.io/ssh-auth",
            string_data={
                "ssh-privatekey": self.config.ssh_private_key,
            },
        )

    @property
    def volume_mounts(self) -> [kubernetes.core.v1.VolumeMountArgs]:
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
    def volumes(self) -> [kubernetes.core.v1.VolumeArgs]:
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
                        {
                            "key": str(Path(self.config.ssh_known_hosts_path).name),
                            "path": str(Path(self.config.ssh_known_hosts_path).name),
                        }
                    ],
                ),
            ),
        ]

    @property
    def env_from(self) -> [kubernetes.core.v1.EnvFromSourceArgs]:
        return [
            homeslice.env_from_configmap(self.app_name),
            homeslice.env_from_secret(self.app_name),
        ]
