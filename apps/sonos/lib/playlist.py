""""An online music service playlist."""

from dataclasses import dataclass, field
from typing import Optional, Sequence
from enum import Enum
from threading import Thread

import random

from soco import SoCo
import soco.exceptions
from soco.data_structures import DidlObject, DidlResource


class MusicService(Enum):
    """Supported music services."""

    # this value would normally get populated by SoCo, but only if discovery works,
    # which it won't inside k8s
    TIDAL = 44551

class Status(Enum):
    ON = "ON"
    OFF = "OFF"


@dataclass
class Playlist:
    """An online music service playlist."""

    service: MusicService
    title: str
    track_ids: Sequence[str]
    playlist_length: int

    didl_desc: str = field(init=False)
    playing_track_ids: Optional[Sequence[str]] = field(init=False)

    def __post_init__(self):
        # this is the secret sauce mising from soco, obtained via wireshark + sonos desktop app.
        # without this, forget it (at least for Tidal).
        self.didl_desc = (
            f"SA_RINCON{self.service.value}_X_#Svc{self.service.value}-0-Token"
        )
        self.playing_track_ids = None

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
        self.playing_track_ids = self.track_ids[: self.playlist_length]

        # first, enqueue a single song, and play it
        i = 0
        for i, track_id in enumerate(self.playing_track_ids):
            if self.play_track_ids(
                zone,
                [
                    track_id,
                ],
            ):
                break

        zone.play_from_queue(index=0)

        # now that we're listening to some music, continue adding tracks
        Thread(
            target=self.play_track_ids,
            args=(
                zone,
                self.playing_track_ids[i + 1 :],
            ),
        ).start()

    def play_track_ids(self, zone: SoCo, track_ids: Sequence[str]) -> bool:
        """Play track ids on a zone. Returns True if any tracks were added."""
        tracks_added = False

        for track_id in track_ids:
            obj = self.make_obj(track_id)
            try:
                zone.add_to_queue(obj)
                tracks_added = True
            except soco.exceptions.SoCoUPnPException:
                pass

        return tracks_added

    def status(self, zone: SoCo) -> Status:
        # ON if:
        # NOTE: potential false negative if this app crashes between play() and status()
        # - self.playing_track_ids is not None
        # - zone is coordinator
        # - zone is playing
        # - queue len == len(self.playing_track_ids)
        # - sorted(queue) == sorted(self.playing_track_ids)
        # - zone.group == self.group
        if self.playing_track_ids is None:
            return Status.OFF
        if not zone.is_coordinator:
            return Status.OFF
        if zone.get_current_transport_info()["current_transport_state"] != "PLAYING":
            return Status.OFF

        queue = zone.get_queue()
        if len(queue) != len(self.playing_track_ids):
            return Status.OFF

        queue_track_ids = [
            # 'x-sonos-http:track%2f337718679.flac?sid=174&flags=8232&sn=34'
            int(track.get_uri().split("%2f")[1].split(".flac")[0]) for track in queue
        ]

        if list(sorted(queue_track_ids)) != list(sorted(self.playing_track_ids)):
            print(sorted(queue_track_ids))
            print("----")
            print(sorted(self.playing_track_ids))
            return Status.OFF

        return Status.ON
