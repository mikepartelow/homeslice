""""An internet radio station."""

import os
import random
from dataclasses import dataclass, field
from typing import Sequence
from enum import Enum

from soco import SoCo
import soco.exceptions
from soco.data_structures import DidlObject, DidlResource

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
