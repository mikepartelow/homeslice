#!/venv/bin/python
"""chime.py plays an mp3 on a given Sonos Zone"""

import time
import argparse
from soco import exceptions, snapshot, SoCo


def parse_args():
    """Parse the command line arguments"""

    description = "Interrupt a Zone, play a media file, then attempt to resume the Zone"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("zone_ip_address")
    parser.add_argument("media_title")
    parser.add_argument("media_uri")
    parser.add_argument("--player-volume", type=int, required=False, default=40)

    return parser.parse_args()


def main():
    """ye olde main()"""
    args = parse_args()
    print(
        " zone_ip_address: {args.zone_ip_address}\n"
        " media_title: {args.media_title}\n"
        " media_uri: {args.media_uri}\n"
        " player_volume: {args.player_volume}".format(args=args)
    )

    zone = SoCo(args.zone_ip_address)

    snapshots = []
    for member in zone.group.members:
        print(f" member: {member.player_name}")

        snap = snapshot.Snapshot(member)
        try:
            snap.snapshot()
        except:  # pylint: disable=bare-except
            print(f"  exception: snap {member.player_name}")
            continue
        snapshots.append(snap)
        if (
            member.is_coordinator
            and member.get_current_transport_info()["current_transport_state"]
            == "PLAYING"
        ):
            try:
                member.pause()
            except:  # pylint: disable=bare-except
                print(f"  exception: pause {member.player_name}")
                continue
    for member in zone.group.members:
        if not member.mute:
            member.volume = args.player_volume

    try:
        zone.play_uri(args.media_uri, title=args.media_title)
    except exceptions.SoCoSlaveException as e:
        print(f"  exception: zone.play_uri {e}")

    time.sleep(6)

    for snap in snapshots:
        try:
            snap.restore(fade=False)
        except:  # pylint: disable=bare-except
            print(f"  exception: restore {member.player_name}")
            continue


main()
