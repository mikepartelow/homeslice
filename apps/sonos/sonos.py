#!/venv/bin/python
"""sonos.py controls Sonos Zones"""

import os
from http.server import HTTPServer
import logging
from soco import SoCo
import yaml
from lib import (
    make_sonos_server,
    MusicService,
    Playlist,
    Station,
    StationConfig,
    SonosConfig,
    PlaylistConfig,
)


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
    """Load config and validate it with Pydantic."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = yaml.safe_load(f)
        return SonosConfig.model_validate(config)


def make_playlist(config: PlaylistConfig) -> Playlist:
    """Construct a playlist from config."""
    service = getattr(MusicService, config.service)
    return Playlist(service, config.title, config.track_ids, PLAYLIST_LENGTH)


def make_station(config: StationConfig) -> Station:
    """Construct a Station from config"""
    return Station(url=config.url, title=config.title)


def main():
    """ye olde main()"""

    logging.basicConfig(level=logging.INFO)

    config = load_config()

    playlists = {k: make_playlist(v) for k, v in config.playlists.items()}
    logging.info("playlists: %s", ", ".join(playlists.keys()))

    stations = {k: make_station(v) for k, v in config.stations.items()}
    logging.info("stations: %s", ", ".join(stations.keys()))

    coordinator = SONOS_IPS[0]
    zones = SONOS_IPS[1:]
    logging.info("coordinator: %s zones: %s", coordinator, zones)

    logging.info("volume: %s", VOLUME)

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
