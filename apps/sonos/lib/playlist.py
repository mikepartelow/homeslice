""""An online music service playlist."""

from dataclasses import dataclass, field
from typing import Sequence
from enum import Enum
from threading import Thread

from soco import SoCo
import soco.exceptions
from soco.data_structures import DidlObject, DidlResource
import random


class MusicService(Enum):
    """Supported music services."""

    # this value would normally get populated by SoCo, but only if discovery works,
    # which it won't inside k8s
    TIDAL = 44551


@dataclass
class Playlist:
    """An online music service playlist."""

    service: MusicService
    title: str
    track_ids: Sequence[str]
    playlist_length: int

    didl_desc: str = field(init=False)

    def __post_init__(self):
        # this is the secret sauce mising from soco, obtained via wireshark + sonos desktop app.
        # without this, forget it (at least for Tidal).
        self.didl_desc = (
            f"SA_RINCON{self.service.value}_X_#Svc{self.service.value}-0-Token"
        )

    def make_obj(self, track_id: int) -> DidlObject:
        """Returns a DidlObject for track_id."""
        # obtained via wireshark
        # unclear if the item_id prefix code actually matters. it might!
        item_id = f"10036028track/{track_id}"
        uri = f"x-sonos-http:track%2f{track_id}.flac?sid=174&amp;flags=24616&amp;sn=34"

        res = [DidlResource(uri=uri, protocol_info="x-rincon-playlist:*:*:*")]
        return DidlObject(
            resources=res, title="", parent_id="", item_id=item_id, desc=self.didl_desc
        )

    def play(self, zone: SoCo):
        """Play the Playlist on zone"""
        zone.clear_queue()

        random.shuffle(self.track_ids)
        track_ids = self.track_ids[: self.playlist_length]

        # first, enqueue a single song, and play it
        i = 0
        for i, track_id in enumerate(track_ids):
            obj = self.make_obj(track_id)
            try:
                zone.add_to_queue(obj)
            except soco.exceptions.SoCoUPnPException:
                pass
            else:
                zone.play_from_queue(index=0)
                break

        Thread(
            target=self.play_the_rest,
            args=(
                zone,
                track_ids[i + 1 :],
            ),
        ).start()

    def play_the_rest(self, zone: SoCo, track_ids: Sequence[str]):
        # now that we're listening to some music, continue adding tracks
        for track_id in track_ids:
            obj = self.make_obj(track_id)
            try:
                zone.add_to_queue(obj)
            except soco.exceptions.SoCoUPnPException:
                pass
