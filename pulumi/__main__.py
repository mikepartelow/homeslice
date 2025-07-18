"""The center of the homeslice deployment multiverse."""

import pulumi
import homeslice
from backup_tidal.backup_tidal import BackupTidal
from backup_todoist.backup_todoist import BackupTodoist
from buttons.buttons import Buttons
from chime.chime import Chime
from clocktime.clocktime import Clocktime
from flyte.flyte import Flyte
from homebridge.homebridge import Homebridge
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
from lmz.lmz import Lmz
from observability.grafana import Grafana
from observability.loki import Loki
from observability.prometheus import Prometheus
from observability.promtail import Promtail
from sonos.sonos import Sonos
from switches.switches import Switches
from unifi.unifi import Unifi

config = pulumi.Config("homeslice")
name = config.require("namespace")

namespace = homeslice.namespace(name)

if cfg := config.get_object("backup_tidal"):
    BackupTidal("backup-tidal", BackupTidalConfig(**dict(cfg)))

if cfg := config.get_object("backup_todoist"):
    BackupTodoist("backup-todoist", BackupTodoistConfig(**dict(cfg)))

if cfg := config.get_object("buttons"):
    Buttons("buttons", ButtonsConfig(**dict(cfg)))

if cfg := config.get_object("chime"):
    k8s_context = pulumi.Config("kubernetes").require("context")
    Chime(
        "chime",
        ChimeConfig(**dict(cfg)),
        k8s_context,
        config.require("namespace"),
    )

if cfg := config.get_object("clocktime"):
    Clocktime("clocktime", ClocktimeConfig(**dict(cfg)))

if cfg := config.get_object("flyte"):
    Flyte("flyte", FlyteConfig(**dict(cfg)))

if cfg := config.get_object("homebridge"):
    Homebridge("homebridge", HomeBridgeConfig(**dict(cfg)))

if cfg := config.get_object("lmz"):
    Lmz("lmz", LmzConfig(**dict(cfg)))

if cfg := config.get_object("observability"):
    homeslice.namespace(cfg["namespace"])  # pylint: disable=E1136
    Grafana("grafana", GrafanaConfig(**dict(cfg)))
    Loki("loki", LokiConfig(**dict(cfg)))
    Prometheus("prometheus", PrometheusConfig(**dict(cfg)))
    Promtail("promtail", PromtailConfig(**dict(cfg)))

if cfg := config.get_object("sonos"):
    Sonos("sonos", SonosConfig(**dict(cfg)))

if cfg := config.get_object("switches"):
    Switches("switches", SwitchesConfig(**dict(cfg)))

if cfg := config.get_object("unifi"):
    Unifi("unifi", UnifiConfig(**dict(cfg)))
