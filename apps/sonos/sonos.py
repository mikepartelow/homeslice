#!/venv/bin/python
"""chime.py plays an mp3 on a given Sonos Zone"""

from soco import SoCo
import soco.groups
import soco.core
from http.server import BaseHTTPRequestHandler, HTTPServer


class SonosServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # zone = SoCo(args.zone_ip_address)
        zone = SoCo("192.168.1.166")

        uri = "https://somafm.com/m3u/secretagent130.m3u"
        title = "Secret Agent"
        g: soco.groups.ZoneGroup = zone.group
        if g:
            for m in g.members:
                assert isinstance(m, soco.core.SoCo)
                if m.is_coordinator:
                    try:
                        m.play_uri(uri=uri, title=title, force_radio=True)
                    except Exception as e:
                        print(e)

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(bytes("OK", "utf-8"))


def main():
    """ye olde main()"""

    host, port = "0.0.0.0", 8000
    s = HTTPServer((host, port), SonosServer)
    print("Server started http://%s:%s" % (host, port))

    try:
        s.serve_forever()
    except KeyboardInterrupt:
        pass

    s.server_close()
    print("Server stopped.")


main()
