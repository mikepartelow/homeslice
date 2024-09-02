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
BACKUP_REPO = require_env("GITHUB_BACKUP_GIT_CLONE_URL")

GIT_AUTHOR_NAME = require_env("GITHUB_BACKUP_AUTHOR_NAME")
GIT_AUTHOR_EMAIL = require_env("GITHUB_BACKUP_AUTHOR_EMAIL")
GIT_PRIVATE_KEY_PATH = require_env("GITHUB_BACKUP_PRIVATE_KEY_PATH")

PATH_TO_SSH_KNOWN_HOSTS = require_env("GITHUB_BACKUP_SSH_KNOWN_HOSTS_PATH")

PATH_TO_CONFIG = require_env("PATH_TO_CONFIG")
PATH_TO_CREDS = require_env("PATH_TO_CREDS")


# Optional
# time to sleep between tracks() API calls to avoid rate limits
RATE_LIMIT_SLEEP_SECONDS = os.environ.get("RATE_LIMIT_SLEEP_SECONDS", 8)
CLONE_PATH = os.environ.get("CLONE_PATH", "/tmp")
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

    repo_name = Path(BACKUP_REPO.split("/")[-1]).stem
    clone_path = Path(CLONE_PATH) / Path(repo_name)

    os.environ["GIT_SSH_COMMAND"] = (
        f"ssh -i {GIT_PRIVATE_KEY_PATH} -o UserKnownHostsFile={PATH_TO_SSH_KNOWN_HOSTS}"
    )

    git.clone(BACKUP_REPO, clone_path)
    print(f"👯 Cloned {BACKUP_REPO} to {clone_path}")

    shutil.copy(playlist_path, clone_path)

    git.add(clone_path, playlist_filename)

    datestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    if git.commit(clone_path, GIT_AUTHOR_NAME, GIT_AUTHOR_EMAIL, datestamp):
        git.push(clone_path)
        print(f"🚢 Pushed {clone_path} to {BACKUP_REPO}")
    else:
        print("🧘 Nothing to do, backup is up to date.")


if __name__ == "__main__":
    main()
