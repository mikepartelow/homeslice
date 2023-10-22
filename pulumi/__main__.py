import pulumi
import homeslice
from buttons import buttons
from clocktime import clocktime
from switches import switches

# Get some values from the Pulumi stack configuration, or use defaults
config = pulumi.Config("homeslice")
name = config.require("namespace")

namespace = homeslice.namespace(name)

if cfg := config.get_object("buttons"):
    buttons.app(name, cfg)

if cfg := config.get_object("clocktime"):
    clocktime.app(name, cfg)

if cfg := config.get_object("switches"):
    switches.app(name, cfg)
