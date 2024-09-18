#!/venv/bin/python
"""sonos.py controls Sonos Zones"""

import os
from dataclasses import dataclass
from collections import namedtuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from typing import Literal

from soco import SoCo


def getenv_or_raise(name: str) -> str:
    """Return the value of an environment variable or raise RuntimeError."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"missing required environment variable: {name}")
    return val


LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = os.environ.get("LISTEN_PORT", 8000)
SONOS_IPS = getenv_or_raise("SONOS_IPS").split(",")


@dataclass
class Station:
    """An internet radio station."""

    url: str
    title: str

    def play(self, sonos_ip: str):
        """Play the Station on sonos_ip"""
        zone = SoCo(sonos_ip)
        if zone.group:
            for member in zone.group.members:
                if member.is_coordinator:
                    try:
                        logger.debug("[%s].play_uri(%s)", member.player_name, self.url)
                        member.play_uri(
                            uri=self.url, title=self.title, force_radio=True
                        )
                    except Exception as e:  # pylint:disable=[broad-exception-caught]
                        print(e)


STATIONS = {
    "secret-agent": Station(
        url="https://somafm.com/m3u/secretagent130.m3u",
        title="SomaFM Secret Agent (Powered by Kubernetes)",
    )
}

logger = logging.getLogger(__name__)


class SonosServer(BaseHTTPRequestHandler):
    """HTTP server for Sonos control"""

    def respond(self, status_code: Literal, message: str) -> None:
        self.send_response(status_code)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def send_ok(self, message: str = "OK"):
        """Send an HTTP 200 OK with an optional HTTP body"""
        self.respond(HTTPStatus.OK, message)

    def send_bad_request(self, message: str = "BAD REQUEST"):
        """Send an HTTP 400 Bad Request with an optional HTTP body"""
        self.respond(HTTPStatus.BAD_REQUEST, message)

    def send_not_found(self, message: str = "NOT FOUND"):
        """Send an HTTP 404 Not Found with an optional HTTP body"""
        self.respond(HTTPStatus.NOT_FOUND, message)

    def do_POST(self):  # pylint:disable=[invalid-name]
        """Process HTTP POST"""
        logging.debug("do_POST: %s", self.path)
        parts = list(map(str.lower, self.path.split("/")))[1:]

        # /playlists/foo/on
        # /stations/bar/on

        if len(parts) != 3:
            self.send_not_found()
            return

        Source = namedtuple("Source", ["kind", "id", "state"])
        source = Source(*parts)

        if source.state != "on":
            self.send_bad_request()
            return

        if source.kind == "stations":
            if station := STATIONS.get(source.id, None):
                for sonos_ip in SONOS_IPS:
                    station.play(sonos_ip)
                self.send_ok("ON")
                return

        if source.kind == "playlists":
            raise("NIY")
            self.send_ok("ON")
            return

        self.send_not_found()


def main():
    """ye olde main()"""

    logging.basicConfig()
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), SonosServer)
    logging.warning("listening on http://%s:%s", LISTEN_HOST, LISTEN_PORT)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    logging.warning("exit")


main()
