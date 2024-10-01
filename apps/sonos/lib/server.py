"""HTTP Server for this stuff."""

from threading import Thread
from collections import namedtuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
import datetime
import logging
from typing import Literal, Mapping, Sequence
from soco import SoCo
from .playlist import Playlist
from .station import Station


def make_sonos_server(
    coordinator: SoCo,
    zones: Sequence[SoCo],
    volume: int,
    playlists: Mapping[str, Playlist],
    stations: Mapping[str, Station],
) -> BaseHTTPRequestHandler:
    """Construct and return a BaseHTTPRequestHandler subclass that implements the magic."""

    last_on = datetime.datetime.now() - datetime.timedelta(days=1)

    def prepare_coordinator():
        coordinator.unjoin()
        coordinator.volume = volume

    def group_zones():
        for zone in zones:
            try:
                zone.join(coordinator)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logging.warning(
                    "error %s while joining %s to coordinator", str(e), zone
                )
            try:
                zone.volume = volume
            except Exception as e:  # pylint: disable=broad-exception-caught
                logging.warning("error %s while setting %s volume", str(e), zone)

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

        def do_GET(self):  # pylint:disable=[invalid-name]
            """Process HTTP GET"""
            logging.warning("do_GET: %s", self.path)
            parts = list(map(str.lower, self.path.split("/")))[1:]

            # /playlists/foo/status
            # /stations/bar/status

            if len(parts) != 3:
                self.send_not_found()
                return

            Source = namedtuple("Source", ["kind", "id", "operation"])
            source = Source(*parts)

            if source.operation.lower() != "status":
                self.send_bad_request()
                return

            music_source = None

            if source.kind == "playlists":
                music_source = playlists.get(source.id, None)

            if source.kind == "stations":
                music_source = stations.get(source.id, None)

            if music_source is None:
                self.send_not_found()

            self.send_ok(music_source.status(coordinator).value)

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

            if source.state.lower() != "on":
                self.send_bad_request()
                return

            if datetime.datetime.now() - last_on < datetime.timedelta(seconds=60):
                self.send_ok("ON")
                return

            music_source = None

            if source.kind == "playlists":
                music_source = playlists.get(source.id, None)

            if source.kind == "stations":
                music_source = stations.get(source.id, None)

            if music_source is None:
                self.send_not_found()

            # homekit/homebridge/homebridge-http sends two ON requests
            last_on = datetime.datetime.now()
            prepare_coordinator()
            music_source.play(coordinator)
            Thread(target=group_zones).start()
            self.send_ok("ON")  # homekit gets impatient, send OK ASAP

    return SonosServer
