#!/venv/bin/python
"""sonos.py controls Sonos Zones"""

import os
from http.server import HTTPServer
import logging
from soco import SoCo
from lib import (
    make_sonos_server,
    MusicService,
    Playlist,
    Station,
    StationConfig,
    SonosConfig,
    PlaylistConfig,
)
import yaml


def getenv_or_raise(name: str) -> str:
    """Return the value of an environment variable or raise RuntimeError."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"missing required environment variable: {name}")
    return val


CONFIG_PATH = getenv_or_raise("CONFIG_PATH")
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = os.environ.get("LISTEN_PORT", 8000)
PLAYLIST_LENGTH = int(os.environ.get("PLAYLIST_LENGTH", 42))
SONOS_IPS = getenv_or_raise("SONOS_IPS").split(",")
VOLUME = os.environ.get("VOLUME", 20)


def load_config() -> SonosConfig:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)
        return SonosConfig(**config)


def make_playlist(config: PlaylistConfig) -> Playlist:
    service = getattr(MusicService, config.service)
    return Playlist(service, config.title, config.track_ids, PLAYLIST_LENGTH)


def make_station(config: StationConfig) -> Station:
    return Station(url=config.url, title=config.title)


def main():
    """ye olde main()"""

    logging.basicConfig(level=logging.INFO)

    config = load_config()

    playlists = {k: make_playlist(v) for k, v in config.playlists.items()}
    logging.info(f"playlists: {', '.join(playlists.keys())}")

    stations = {k: make_station(v) for k, v in config.stations.items()}
    logging.info(f"stations: {','.join(stations.keys())}")

    coordinator = SONOS_IPS[0]
    zones = SONOS_IPS[1:]
    logging.info(f"coordinator: {coordinator} zones: {zones}")

    logging.info(f"volume: {VOLUME}")

    sonos_server = make_sonos_server(
        coordinator=SoCo(coordinator),
        zones=[SoCo(ip) for ip in zones],
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

# FIXME:
# - fixed IPs for sonoses in unifi (less necessary)
# - new algo:
#   - init coordinator
#   - play one song on coordinator
#   - spawn thread and return HTTP OK
#     - group zones
#     - enqueue the rest
