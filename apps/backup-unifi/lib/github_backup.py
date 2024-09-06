import os
import sys
from typing import Sequence

def require_env(name: str) -> str:
    """Returns the value of the given environment variable or prints a message and exits."""
    if (val := os.environ[name]) != "":
        return val

    print(f"{name} is required")
    sys.exit(1)


class GithubBackup:
    def __init__(self):
        # Required
        self.backup_repo = require_env("GITHUB_BACKUP_GIT_CLONE_URL")

        self.git_author_name = require_env("GITHUB_BACKUP_AUTHOR_NAME")
        self.git_author_email = require_env("GITHUB_BACKUP_AUTHOR_EMAIL")
        self.git_private_key_path = require_env("GITHUB_BACKUP_PRIVATE_KEY_PATH")

        self.path_to_ssh_known_hosts = require_env("GITHUB_BACKUP_SSH_KNOWN_HOSTS_PATH")

        self.path_to_backups = require_env("PATH_TO_BACKUPS")

        # Optional
        self.clone_path = os.environ.get("CLONE_PATH", "/tmp")

    def backup(self, backup_files: Sequence[str]):
        # FIXME: put this bit into lib/ and share it with backup-tidal
        os.environ["GIT_SSH_COMMAND"] = (
            f"ssh -i {self.git_private_key_path} -o UserKnownHostsFile={self.path_to_ssh_known_hosts}"
        )

        clone(self.backup_repo, clone_path)
        print(f"👯 Cloned {self.backup_repo} to {self.clone_path}")

        for filename in backup_files:
            shutil.copy(filename, self.clone_path)
            add(self.clone_path, Path(filename).name)

        datestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if commit(clone_path, self.git_author_name, self.git_author_email, datestamp):
            push(clone_path)
            print(f"🚢 Pushed {clone_path} to {BACKUP_REPO}")
        else:
            print("🧘 Nothing to do, backup is up to date.")
