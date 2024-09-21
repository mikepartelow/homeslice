""""An online music service playlist."""
import os
import random
from dataclasses import dataclass, field
from typing import Sequence
from enum import Enum

from soco import SoCo
import soco.exceptions
from soco.data_structures import DidlObject, DidlResource

PLAYLIST_LENGTH = int(os.environ.get("PLAYLIST_LENGTH", 42))

class MusicService(Enum):
    TIDAL = 44551  # this value would normally get populated by SoCo, but only if discovery works, which it won't inside k8s


@dataclass
class Playlist:
    """An online music service playlist."""

    service: MusicService
    id: str
    title: str

    didl_desc: str = field(init=False)
    track_ids: Sequence[str] = field(init=False)

    def __post_init__(self, playlist_length: int = PLAYLIST_LENGTH):
        # this is the secret sauce mising from soco, obtained via wireshark + sonos desktop app. without this, forget it (at least for Tidal).
        self.didl_desc = (
            f"SA_RINCON{self.service.value}_X_#Svc{self.service.value}-0-Token"
        )

        with open(f"./playlists/{self.id}") as f:
            self.track_ids = f.read().splitlines()

            random.shuffle(self.track_ids)
            self.track_ids = self.track_ids[:playlist_length]

    def make_obj(self, track_id: int) -> DidlObject:
        # obtained via wireshark
        item_id = f"10036028track/{track_id}"  # unclear if the item_id prefix code actually matters. it might!
        uri = f"x-sonos-http:track%2f{track_id}.flac?sid=174&amp;flags=24616&amp;sn=34"

        res = [DidlResource(uri=uri, protocol_info="x-rincon-playlist:*:*:*")]
        return DidlObject(
            resources=res, title="", parent_id="", item_id=item_id, desc=self.didl_desc
        )

    def play(self, sonos_ip: str):
        """Play the Playlist on sonos_ip"""
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
        for track_id in self.track_ids[i+1:]:
            obj = self.make_obj(track_id)
            try:
                zone.add_to_queue(obj)
            except soco.exceptions.SoCoUPnPException:
                pass
