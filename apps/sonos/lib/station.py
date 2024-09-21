""""An internet radio station."""

from dataclasses import dataclass

from soco import SoCo


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
