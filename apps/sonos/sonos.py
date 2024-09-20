#!/venv/bin/python
"""sonos.py controls Sonos Zones"""

import os
import random
from dataclasses import dataclass, field
from collections import namedtuple
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
from typing import Literal, Sequence
from enum import Enum

from soco import SoCo
import soco.exceptions
from soco.data_structures import DidlObject,DidlResource


def getenv_or_raise(name: str) -> str:
    """Return the value of an environment variable or raise RuntimeError."""
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"missing required environment variable: {name}")
    return val


LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = os.environ.get("LISTEN_PORT", 8000)
SONOS_IPS = getenv_or_raise("SONOS_IPS").split(",")
PLAYLIST_LENGTH = int(os.environ.get("PLAYLIST_LENGTH", 42))

class MusicService(Enum):
    TIDAL = 44551 # this value would normally get populated by SoCo, but only if discovery works, which it won't inside k8s

@dataclass
class Playlist:
    """An online music service playlist."""

    service: MusicService
    id: str
    title: str

    didl_desc: str = field(init=False)
    track_ids: Sequence[str] = field(init=False)

    def __post_init__(self):
        # this is the secret sauce mising from soco, obtained via wireshark + sonos desktop app. without this, forget it (at least for Tidal).
        self.didl_desc = f"SA_RINCON{self.service.value}_X_#Svc{self.service.value}-0-Token"

        with open(f"./playlists/{self.id}") as f:
            self.track_ids = f.read().splitlines()

    def make_obj(self, track_id: int) -> DidlObject:
        # obtained via wireshark
        item_id=f"10036028track/{track_id}" # unclear if the item_id prefix code actually matters. it might!
        uri = f"x-sonos-http:track%2f{track_id}.flac?sid=174&amp;flags=24616&amp;sn=34"

        res = [DidlResource(uri=uri, protocol_info="x-rincon-playlist:*:*:*")]
        return DidlObject(resources=res, title="", parent_id="", item_id=item_id, desc=self.didl_desc)

    def play(self, sonos_ip: str):
        """Play the Playlist on sonos_ip"""
        random.shuffle(self.track_ids)

        zone = SoCo(sonos_ip)
        zone.clear_queue()

        # first, enqueue a single song, and play it
        i = 0
        for i, track_id in enumerate(self.track_ids):
            obj = self.make_obj(track_id)
            try:
                zone.add_to_queue(obj)
            except soco.exceptions.SoCoUPnPException:
                pass
            else:
                zone.play_from_queue(index=0)
                break

        # now that we're listening to some music, continue adding tracks
        for track_id in self.track_ids[i+1:PLAYLIST_LENGTH]:
            obj = self.make_obj(track_id)
            try:
                zone.add_to_queue(obj)
            except soco.exceptions.SoCoUPnPException:
                pass


@dataclass
class Station:
    """An internet radio station."""

    url: str
    title: str

    def play(self, sonos_ip: str):
        """Play the Station on sonos_ip"""
        zone = SoCo(sonos_ip)
        try:
            zone.play_uri(uri=self.url, title=self.title, force_radio=True)
        except Exception as e:  # pylint:disable=[broad-exception-caught]
            print(e)


# FIXME: make this a ConfigMap
STATIONS = {
    "secret-agent": Station(
        url="https://somafm.com/m3u/secretagent130.m3u",
        title="SomaFM Secret Agent (Powered by Kubernetes)",
    )
}

PLAYLISTS = {
    "mega-playlist": Playlist(
        service=MusicService.TIDAL,
        id="8427c6cc-12cf-43c5-84ce-77fbc095e455",
        title="Tidal Mega Playlist (Powered by Kubernetes)",
    )
}


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
                    # FIXME: group all, or group most, but anyways, make it an env var
                    station.play(sonos_ip)
                self.send_ok("ON")
                return

        if source.kind == "playlists":
            if playlist := PLAYLISTS.get(source.id, None):
                for sonos_ip in SONOS_IPS:
                    # FIXME: group all, or group most, but anyways, make it an env var
                    playlist.play(sonos_ip)
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
