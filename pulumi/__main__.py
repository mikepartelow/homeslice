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
from lmz import lmz
from observability import grafana, loki, prometheus, promtail
from switches import switches
from sonos import sonos
from homeslice_config import (
    BackupTidalConfig,
    BackupTodoistConfig,
    ChimeConfig,
    HomeBridgeConfig,
    LmzConfig,
    SonosConfig,
    UnifiConfig,
)
from unifi import unifi

config = pulumi.Config("homeslice")
name = config.require("namespace")

namespace = homeslice.namespace(name)

if cfg := config.get_object("backup_tidal"):
    backup_tidal.app(BackupTidalConfig(**dict(cfg)))

if cfg := config.get_object("backup_todoist"):
    backup_todoist.app(BackupTodoistConfig(**dict(cfg)))

if cfg := config.get_object("buttons"):
    buttons.app(cfg)

if cfg := config.get_object("chime"):
    chime.app(
        ChimeConfig(**dict(cfg)),
        pulumi.Config("kubernetes").get("context"),
        config.require("namespace"),
    )

if cfg := config.get_object("clocktime"):
    clocktime.app(cfg)

if cfg := config.get_object("flyte"):
    flyte.app(cfg)

if cfg := config.get_object("homebridge"):
    homebridge.app(HomeBridgeConfig(**dict(cfg)))

if cfg := config.get_object("lmz"):
    lmz.app(LmzConfig(**dict(cfg)))

if cfg := config.get_object("observability"):
    homeslice.namespace(cfg["namespace"])  # pylint: disable=E1136
    grafana.app(cfg)
    loki.app(cfg)
    prometheus.app(cfg)
    promtail.app(cfg)

if cfg := config.get_object("sonos"):
    sonos.app(SonosConfig(**dict(cfg)))

if cfg := config.get_object("switches"):
    switches.app(cfg)

if cfg := config.get_object("unifi"):
    unifi.app(UnifiConfig(**dict(cfg)))
