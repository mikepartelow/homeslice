"""Homeslice Config"""

from typing import Optional
from pydantic import BaseModel, Field


class GithubBackupConfig(BaseModel):
    """GithubBackup Config, to be used as base class for other configs."""

    ssh_private_key_path_env_var_name: str = Field(
        default="GITHUB_BACKUP_PRIVATE_KEY_PATH"
    )
    ssh_private_key_path: str = Field(default="/var/run/ssh-privatekey/ssh-privatekey")
    ssh_private_key: Optional[bytes] = Field(default=None)

    ssh_known_hosts_path_env_var_name: str = Field(
        default="GITHUB_BACKUP_SSH_KNOWN_HOSTS_PATH"
    )
    ssh_known_hosts_path: str = Field(default="/var/run/known_hosts/known_hosts")

    git_author_name_env_var_name: str = Field(default="GITHUB_BACKUP_AUTHOR_NAME")
    git_author_name: str

    git_author_email_env_var_name: str = Field(default="GITHUB_BACKUP_AUTHOR_EMAIL")
    git_author_email: str

    git_clone_url_env_var_name: str = Field(default="GITHUB_BACKUP_GIT_CLONE_URL")
    git_clone_url: Optional[str] = Field(default=None)


class BackupTidalConfig(GithubBackupConfig):
    """BackupTidal Config. Inherits from GithubBackupConfig."""

    image: str
    schedule: str


class BackupTodoistConfig(GithubBackupConfig):
    """BackupTodoist Config. Inherits from GithubBackupConfig."""

    image: str
    schedule: str


class HomeBridgeConfig(BaseModel):
    """HomeBridge Config"""

    image: str
    redirect_host: str
    redirect_prefix: str
    node_selector: dict[str, str]


class LmzConfig(BaseModel):
    """LMZ Config"""

    image: str
    container_port: int
    lmz_yaml_path: str
    ingress_prefix: Optional[str]


class UnifiConfig(BaseModel):
    """Unifi Config"""

    redirect_prefix: str
    redirect_url: str
