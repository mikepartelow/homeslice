#!/venv/bin/python
"""Backup unifi backups to GitHub"""

import sys
import os
import glob
from lib import github_backup


def main():
    """Does the magic."""
    if len(sys.argv) < 2:
        print("Usage: ./backup_unifi.py /path/to/backups")
        sys.exit(1)

    path_to_backups = sys.argv[1]

    files = glob.glob(path_to_backups + "/*.unf")
    latest = max(files, key=os.path.getctime)

    print("Latest:", latest)

    ghb = github_backup.GithubBackup()
    ghb.backup([latest])


if __name__ == "__main__":
    main()
