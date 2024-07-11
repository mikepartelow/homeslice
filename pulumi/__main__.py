"""The center of the homeslice deployment multiverse."""

import pulumi
import homeslice
from backup_tidal import backup_tidal
from backup_todoist import backup_todoist
from buttons import buttons
from chime import chime
from clocktime import clocktime
from homebridge import homebridge
from observability import grafana, prometheus
from switches import switches

config = pulumi.Config("homeslice")
name = config.require("namespace")

namespace = homeslice.namespace(name)

if cfg := config.get_object("backup_tidal"):
    backup_tidal.app(cfg)

if cfg := config.get_object("backup_todoist"):
    backup_todoist.app(cfg)

if cfg := config.get_object("buttons"):
    buttons.app(cfg)

if cfg := config.get_object("chime"):
    chime.app(cfg)

if cfg := config.get_object("clocktime"):
    clocktime.app(cfg)

if cfg := config.get_object("homebridge"):
    homebridge.app(cfg)

if cfg := config.get_object("observability"):
    homeslice.namespace(cfg["namespace"])
    prometheus.app(cfg)
    grafana.app(cfg)

if cfg := config.get_object("switches"):
    switches.app(cfg)
