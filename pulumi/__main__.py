"""The center of the homeslice deployment multiverse."""

import pulumi
import homeslice
from backup_tidal import backup_tidal
from backup_todoist import backup_todoist
from buttons import buttons
from chime import chime
from clocktime import clocktime
from flyte import flyte
from homebridge import homebridge
from homeslice_config import (
    BackupTodoistConfig,
    BackupTidalConfig,
    ButtonsConfig,
    ChimeConfig,
    ClocktimeConfig,
    FlyteConfig,
    GrafanaConfig,
    HomeBridgeConfig,
    LokiConfig,
    LmzConfig,
    PrometheusConfig,
    PromtailConfig,
    SonosConfig,
    SwitchesConfig,
    UnifiConfig,
)
from lmz import lmz
from observability import grafana, loki, prometheus, promtail
from sonos import sonos
from switches import switches
from unifi import unifi

config = pulumi.Config("homeslice")
name = config.require("namespace")

namespace = homeslice.namespace(name)

if cfg := config.get_object("backup_tidal"):
    backup_tidal.app(BackupTidalConfig(**dict(cfg)))

if cfg := config.get_object("backup_todoist"):
    backup_todoist.app(BackupTodoistConfig(**dict(cfg)))

if cfg := config.get_object("buttons"):
    buttons.app(ButtonsConfig(**dict(cfg)))

if cfg := config.get_object("chime"):
    k8s_context = pulumi.Config("kubernetes").get("context")
    if k8s_context:
        chime.app(
            ChimeConfig(**dict(cfg)),
            k8s_context,
            config.require("namespace"),
        )

if cfg := config.get_object("clocktime"):
    clocktime.app(ClocktimeConfig(**dict(cfg)))

if cfg := config.get_object("flyte"):
    flyte.app(FlyteConfig(**dict(cfg)))

if cfg := config.get_object("homebridge"):
    homebridge.app(HomeBridgeConfig(**dict(cfg)))

if cfg := config.get_object("lmz"):
    lmz.app(LmzConfig(**dict(cfg)))

if cfg := config.get_object("observability"):
    homeslice.namespace(cfg["namespace"])  # pylint: disable=E1136
    grafana.app(GrafanaConfig(**dict(cfg)))
    loki.app(LokiConfig(**dict(cfg)))
    prometheus.app(PrometheusConfig(**dict(cfg)))
    promtail.app(PromtailConfig(**dict(cfg)))

if cfg := config.get_object("sonos"):
    sonos.app(SonosConfig(**dict(cfg)))

if cfg := config.get_object("switches"):
    switches.app(SwitchesConfig(**dict(cfg)))

if cfg := config.get_object("unifi"):
    unifi.app(UnifiConfig(**dict(cfg)))
