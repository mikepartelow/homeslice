"""Discover Sonoses on local network.
"""

from soco.discovery import discover

for zone in discover():
    print(zone.player_name, zone.ip_address, zone.is_coordinator)
