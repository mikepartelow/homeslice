#!/venv/bin/python

import os
import sys
import time
import socket
from threading import Thread
from random import choice

from urllib.parse import quote
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

from soco.discovery import by_name, discover
from soco import snapshot


def parse_args():
    """Parse the command line arguments"""
    import argparse

    description = "Play local files with Sonos by running a local web server"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("zone", help="The name of the zone to play from")

    return parser.parse_args()


def main():
    args = parse_args()
    print(
        " Will use the following settings:\n"
        " Zone: {args.zone}".format(args=args)
    )

    zone_names = [zone_.player_name for zone_ in discover()]
    print(zone_names)
    print(dir(zone_names[0]))

    # Get the zone
    zone = by_name(args.zone)

    # Check if a zone by the given name was found
    if zone is None:
        zone_names = [zone_.player_name for zone_ in discover()]
        print(
            "No Sonos player named '{}'. Player names are {}".format(
                args.zone, zone_names
            )
        )
        sys.exit(1)

    # Check whether the zone is a coordinator (stand alone zone or
    # master of a group)
    if not zone.is_coordinator:
        print(
            "The zone '{}' is not a group master, and therefore cannot "
            "play music. Please use '{}' in stead".format(
                args.zone, zone.group.coordinator.player_name
            )
        )
        sys.exit(2)


    url = "http://192.168.1.5/api/v0/chime/swed.mp3"
    title = "4:20"


# - http: // nucnuc.local/api/v0/chime/swed.mp3 renders the wrong thing!
# - by_name() seems not to work in container, can init zone elsewise?


    # number_in_queue = zone.add_uri_to_queue(url)
    # # play_from_queue indexes are 0-based
    # zone.play_from_queue(number_in_queue - 1)

    snapshots = []

    for member in zone.group.members:
        print(f" member: {member.player_name}")

        snap = snapshot.Snapshot(member)
        try:
            snap.snapshot()
        except:
            print(f"  exception: snap {member.player_name}")
        snapshots.append(snap)
        if member.is_coordinator and \
                member.get_current_transport_info()['current_transport_state'] == 'PLAYING':
            try:
                member.pause()
            except:
                print(f"  exception: pause {member.player_name}")
    for member in zone.group.members:
        if not member.mute:
            member.volume = 40
    zone.play_uri(url, title=title)

    time.sleep(6)
    for snap in snapshots:
        try:
            snap.restore(fade=False)
        except:
            print(f"  exception: restore {member.player_name}")

main()
