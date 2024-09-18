#!/venv/bin/python
"""Backup a Tidal playlist to GitHub"""

from pathlib import Path
import json
import os
import sys

import tidalapi

from lib import auth, github_backup, playlist


def require_env(name: str) -> str:
    """Returns the value of the given environment variable or prints a message and exits."""
    if (val := os.environ[name]) != "":
        return val

    print(f"{name} is required")
    sys.exit(1)


# Required
PATH_TO_CONFIG = require_env("PATH_TO_CONFIG")
PATH_TO_CREDS = require_env("PATH_TO_CREDS")


# Optional
# time to sleep between tracks() API calls to avoid rate limits
RATE_LIMIT_SLEEP_SECONDS = os.environ.get("RATE_LIMIT_SLEEP_SECONDS", 8)
PLAYLIST_PATH = os.environ.get("PLAYLIST_PATH", "/tmp")


def main():
    """Does the magic."""
    with open(PATH_TO_CONFIG, "r", encoding="utf-8") as config_f:
        config = json.load(config_f)

    session = tidalapi.Session()
    auth.login(session, PATH_TO_CREDS)

    playlist_filename = f"{config['playlist_name']}.json"
    playlist_path = Path(PLAYLIST_PATH) / Path(playlist_filename)

    print(
        f"🥡 Fetching Tidal Playlist {config['playlist_name']} to {str(playlist_path)}"
    )
    playlist.write(
        session, config["playlist_id"], playlist_path, RATE_LIMIT_SLEEP_SECONDS
    )
    print(f"🎵 Wrote Tidal Playlist to {str(playlist_path)}")

    ghb = github_backup.GithubBackup()
    ghb.backup([playlist_path])


if __name__ == "__main__":
    main()
