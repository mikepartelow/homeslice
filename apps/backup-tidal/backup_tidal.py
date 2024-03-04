#!/venv/bin/python
"""Fetch a Tidal playlist and write it to a JSON file."""
from datetime import datetime
from pathlib import Path
import json
import os
import shutil
import sys

import tidalapi

from lib import auth, git, playlist


def require_env(name: str) -> str:
    """Returns the value of the given environment variable or prints a message and exits."""
    if (val := os.environ[name]) != "":
        return val

    print(f"{name} is required")
    sys.exit(1)


# Required
BACKUP_REPO = require_env("BACKUP_REPO")
CLONE_PATH = require_env("CLONE_PATH")
GIT_AUTHOR = require_env("GIT_AUTHOR")
PATH_TO_CONFIG = require_env("PATH_TO_CONFIG")
PATH_TO_CREDS = require_env("PATH_TO_CREDS")
PLAYLIST_PATH = require_env("PLAYLIST_PATH")

# Optional
# time to sleep between tracks() API calls to avoid rate limits
RATE_LIMIT_SLEEP_SECONDS = os.environ.get("RATE_LIMIT_SLEEP_SECONDS", 8)


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
    # playlist.write(
    #     session, config["playlist_id"], playlist_path, RATE_LIMIT_SLEEP_SECONDS
    # )

    with open(playlist_path, "w"):
        pass

    print(f"🎵 Wrote Tidal Playlist to {str(playlist_path)}")

    repo_name = Path(BACKUP_REPO.split("/")[-1]).stem
    clone_path = Path(CLONE_PATH) / Path(repo_name)

    git.clone(BACKUP_REPO, clone_path)
    print(f"👯 Cloned {BACKUP_REPO} to {clone_path}")

    shutil.copy(playlist_path, clone_path)

    git.add(clone_path, playlist_filename)

    datestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if git.commit(clone_path, GIT_AUTHOR, datestamp):
        git.push(clone_path)
        print(f"🚢 Pushed {clone_path} to {BACKUP_REPO}")
    else:
        print("🧘 Nothing to do, backup is up to date.")


if __name__ == "__main__":
    main()
