#!/venv/bin/python
"""chime.py plays an mp3 on a given Sonos Zone"""

import os
from dataclasses import dataclass
from http import HTTPStatus
from soco import SoCo
import soco.groups
import soco.core
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging

def getenv_or_raise(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        raise RuntimeError(f"missing required environment variable: {name}")
    return val

LISTEN_HOST="0.0.0.0"
LISTEN_PORT=getenv_or_raise("LISTEN_PORT")
SONOS_IP=getenv_or_raise("SONOS_IP")

@dataclass
class Station:
    url: str
    title: str

    def play(self):
        zone = SoCo(SONOS_IP)
        if zone.group:
            for member in zone.group.members:
                if member.is_coordinator:
                    try:
                        logger.debug(f"[{member.player_name}].play_uri({self.url})")
                        member.play_uri(uri=self.url, title=self.title, force_radio=True)
                    except Exception as e:
                        print(e)


STATIONS = {
    "secret-agent": Station(url="https://somafm.com/m3u/secretagent130.m3u", title="SomaFM Secret Agent (Powered by Kubernetes)")
}

logger = logging.getLogger(__name__)


class SonosServer(BaseHTTPRequestHandler):
    def send_ok(self, message:str="OK"):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def send_not_found(self, message:str="NOT FOUND"):
        self.send_response(HTTPStatus.NOT_FOUND)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def do_GET(self):
        logging.debug(f"do_GET: {self.path}")
        parts = list(map(str.lower, self.path.split("/")))[1:]
        logger.debug(f"parts={parts}")

        if len(parts) > 1 and parts[1] == "on":
            if station := STATIONS.get(parts[0], None):
                station.play()
                return self.send_ok("ON")

        self.send_not_found()

def main():
    """ye olde main()"""

    logging.basicConfig()
    logging.getLogger(__name__).setLevel(logging.DEBUG)

    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), SonosServer)
    logging.warning(f"listening on http://{LISTEN_HOST}:{LISTEN_PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
    logging.warning("exit")


main()
