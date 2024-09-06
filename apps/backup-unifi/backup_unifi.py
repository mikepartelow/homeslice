#!/venv/bin/python


from pathlib import Path

from lib import github_backup

def main():
    """Does the magic."""
    backup_path = Path(PATH_TO_BACKUPS) / "FIXME: get the most recent"

    # FIXME: also refactor backup_tidal
    ghb = github_backup.GithubBackup()
    ghb.backup([backup_path])


if __name__ == "__main__":
    main()
