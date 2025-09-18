"""Homeslice Config"""

from typing import Mapping, Optional, Sequence
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


class ChimeConfig(BaseModel):
    """Chime Config"""

    image: str
    chimes: Sequence[Mapping[str, str]]
    nginx: str
    pvc_mount_path: str
    container_port: int
    ingress_prefix: str


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
    installation_key_json_path: str
    creds_txt_path: str
    ingress_prefix: Optional[str]


class SonosConfig(BaseModel):
    """Sonos Config"""

    config_path: str
    container_port: int
    image: str
    ingress_prefix: Optional[str]
    volume: int


class UnifiConfig(GithubBackupConfig):
    """Unifi Config"""

    image: str
    redirect_prefix: str
    redirect_url: str
    node_selector: dict[str, str]
    schedule: str


class SwitchesConfig(BaseModel):
    """Switches Config"""

    image: str
    container_port: int
    switches_json: str
    switches_json_path: str
    ingress_prefix: Optional[str] = None


class ClocktimeConfig(BaseModel):
    """Clocktime Config"""
    image: str
    container_port: int
    location: str
    ingress_prefix: Optional[str] = None


class ButtonsConfig(BaseModel):
    """Buttons Config"""
    image: str
    container_port: int
    clocktime_url: str
    ingress_prefixes: Optional[list[str]] = None


class LokiConfig(BaseModel):
    """Loki Config"""
    namespace: str
    loki_chart_version: str


class PrometheusConfig(BaseModel):
    """Prometheus Config"""
    namespace: str
    prometheus_chart_version: str
    prometheus_ingress_prefix: str
    hostname: str


class GrafanaConfig(BaseModel):
    """Grafana Config"""
    namespace: str
    grafana_chart_version: str
    grafana_ingress_prefix: str
    loki_datasource: str
    prometheus_datasource: str


class PromtailConfig(BaseModel):
    """Promtail Config"""
    namespace: str
    promtail_chart_version: str
    loki_push_url: str


class FlyteConfig(BaseModel):
    """Flyte Config"""
    namespace: str
    secret_name: str = Field(alias="secret-name")
    charts: list[dict]
