""""An internet radio station."""

from dataclasses import dataclass
from soco import SoCo
from .status import Status


@dataclass
class Station:
    """An internet radio station."""

    url: str
    title: str

    def play(self, zone: SoCo):
        """Play the Station on zone"""
        try:
            zone.play_uri(uri=self.url, title=self.title, force_radio=True)
        except Exception as e:  # pylint:disable=[broad-exception-caught]
            print(e)

    # pylint: disable=R0801
    def status(self, zone: SoCo) -> Status:
        """Status returns ON if the given station is more-or-less playing on the controller.
        Does not consider grouping."""
        if not zone.is_coordinator:
            return Status.OFF

        if zone.get_current_transport_info()["current_transport_state"] != "PLAYING":
            return Status.OFF

        # could also mangle then check ["uri"]: 'uri': 'x-rincon-mp3radio://somafm.com/m3u/groovesalad130.m3u'
        # but the x-rincon prefix may vary depending on who-knows-what, so this is simpler
        if zone.get_current_media_info()["channel"] != self.title:
            return Status.OFF

        # Here we could check if the group remains the same as when we turned
        # the playlist ON, but that makes a problematic method even more problematic.

        return Status.ON
