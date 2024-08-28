#!/venv/bin/python
"""chime.py plays an mp3 on a given Sonos Zone"""

import os
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

from soco import SoCo


def getenv_or_raise(name: str) -> str:
    """Return the value of an environment variable or raise RuntimeError."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"missing required environment variable: {name}")
    return val


LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = getenv_or_raise("LISTEN_PORT")
SONOS_IP = getenv_or_raise("SONOS_IP")


@dataclass
class Station:
    """An internet radio station."""

    url: str
    title: str

    def play(self):
        """Play the Station on os.environ[SONOS_IP]"""
        zone = SoCo(SONOS_IP)
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

    def send_ok(self, message: str = "OK"):
        """Send an HTTP 200 OK with an optional HTTP body"""
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def send_not_found(self, message: str = "NOT FOUND"):
        """Send an HTTP 404 Not Found with an optional HTTP body"""
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def do_GET(self):  # pylint:disable=[invalid-name]
        """Process HTTP GET"""
        logging.debug("do_GET: %s", self.path)
        parts = list(map(str.lower, self.path.split("/")))[1:]

        if len(parts) > 1 and parts[1] == "on":
            if station := STATIONS.get(parts[0], None):
                station.play()
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
