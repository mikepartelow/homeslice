"""HTTP Server for this stuff."""

from dataclasses import dataclass

from collections import namedtuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import logging
from typing import Literal, Mapping, Sequence
from soco import SoCo
from .playlist import Playlist
from .station import Station
import datetime

def make_sonos_server(
    coordinator: SoCo,
    zones: Sequence[SoCo],
    volume: int,
    playlists: Mapping[str, Playlist],
    stations: Mapping[str, Station],
):

    last_on = datetime.datetime.now() - datetime.timedelta(days=1)

    def prepare_coordinator():
        coordinator.unjoin()
        coordinator.volume = volume

    def group_zones():
        for zone in zones:
            try:
                zone.join(coordinator)
            except Exception as e:
                logging.warning(f"error {str(e)} while joining {zone} to coordinator")
            try:
                zone.volume = volume
            except Exception as e:
                logging.warning(f"error {str(e)} while setting {zone} volume")

    class SonosServer(BaseHTTPRequestHandler):
        """HTTP server for Sonos control"""

        def respond(self, status_code: Literal, message) -> None:
            """Send an HTTP response with an HTTP body"""
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
            nonlocal last_on
            logging.warning("do_POST: %s", self.path)
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

            if datetime.datetime.now() - last_on < datetime.timedelta(seconds=60):
                self.send_ok("ON")
                return

            if source.kind == "stations":
                if station := stations.get(source.id, None):
                    last_on = datetime.datetime.now() # homekit/homebridge/homebridge-http sends two ON requests
                    self.send_ok("ON")  # homekit gets impatient, send OK ASAP
                    prepare_coordinator()
                    station.play(coordinator)
                    group_zones()
                    return

            if source.kind == "playlists":
                if playlist := playlists.get(source.id, None):
                    last_on = datetime.datetime.now() # homekit/homebridge/homebridge-http sends two ON requests
                    self.send_ok("ON") # homekit gets impatient, send OK ASAP
                    prepare_coordinator()
                    playlist.play(coordinator)
                    group_zones()
                    return

            self.send_not_found()

    return SonosServer
