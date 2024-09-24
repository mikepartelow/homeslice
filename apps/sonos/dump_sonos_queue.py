#!/venv/bin/python
"""dumps the track ids of the sonos queue on a given zone player"""

import os
from soco import SoCo


def getenv_or_raise(name: str) -> str:
    """Return the value of an environment variable or raise RuntimeError."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"missing required environment variable: {name}")
    return val


SONOS_IP = getenv_or_raise("SONOS_IP")


def main():
    """do the thing"""
    zone = SoCo(SONOS_IP)
    for item in zone.get_queue():
        uri = item.resources[0].uri
        print(uri.split("%2f")[1].split(".")[0])


if __name__ == "__main__":
    main()
