"""HTTP Server for this stuff."""

from collections import namedtuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import logging
from typing import Sequence, Mapping
from soco import SoCo

@dataclass
class SonosServer(BaseHTTPRequestHandler):
    """HTTP server for Sonos control"""

    coordinator: SoCo
    zones: Sequence[SoCo]
    volume: int
    playlists: Mapping[str, Playlist]
    stations: Mapping[str, Station]

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

        self.coordinator.unjoin()
        self.coordinator.volume = self.volume

        for zone in self.zones:
            zone.join(self.coordinator)
            zone.volume = self.volume

        if source.kind == "stations":
            if station := self.stations.get(source.id, None):
                station.play(self.coordinator)
                self.send_ok("ON")
                return

        if source.kind == "playlists":
            if playlist := self.playlists.get(source.id, None):
                playlist.play(self.coordinator)
                self.send_ok("ON")
            return

        self.send_not_found()
