#!/venv/bin/python
"""sonos.py controls Sonos Zones"""

# - FIXME: sonos.group(SONOS_IPS), set all to volume == 20, then play on the controller. that's what this app does, by def. creates its own group.

import os
from http.server import HTTPServer
import logging

def getenv_or_raise(name: str) -> str:
    """Return the value of an environment variable or raise RuntimeError."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"missing required environment variable: {name}")
    return val


LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = os.environ.get("LISTEN_PORT", 8000)
SONOS_IPS = getenv_or_raise("SONOS_IPS").split(",")
VOLUME = os.environ.get("LISTEN_PORT", 20)

# FIXME: make this a ConfigMap
stations = {
    "secret-agent": Station(
        url="https://somafm.com/m3u/secretagent130.m3u",
        title="SomaFM Secret Agent (Powered by Kubernetes)",
    )
}

# FIXME: make this a ConfigMap, read it from filesystem
playlists = {
    "mega-playlist": Playlist(
        service=MusicService.TIDAL,
        id="8427c6cc-12cf-43c5-84ce-77fbc095e455",
        title="Tidal Mega Playlist (Powered by Kubernetes)",
    )
}

def main():
    """ye olde main()"""

    logging.basicConfig()
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    sonos_server = SonosServer(
        coordinator=SoCo(SONOS_IPS[0]),
        zones=[SoCo(ip) for ip in SONOS_IPS[1:]],
        volume=VOLUME,
        playlists=playlists,
        stations=stations,
    )

    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), sonos_server)
    logging.warning("listening on http://%s:%s", LISTEN_HOST, LISTEN_PORT)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    logging.warning("exit")


main()
