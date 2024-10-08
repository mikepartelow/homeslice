"""Fuctions for cloning and pushing a Git repo"""

import subprocess
from pathlib import Path


def add(clone_dir: str, filename: str) -> None:
    """Add files to a commit."""
    run(f"git -C {clone_dir} add {filename}")


def clone(repo_name: str, clone_dir: str) -> None:
    """Clone a repo, possibly remote."""
    if Path(clone_dir).exists():
        print(f"⚠️  clone already exists at {clone_dir}, not replacing it.")
        return
    run(f"git clone {repo_name} {clone_dir}")


def commit(clone_dir: str, author_name: str, author_email: str, message: str) -> bool:
    """Commit. Returns False if there is nothing to commit, otherwise, returns True."""
    out = run(f"git -C {clone_dir} status")
    if "nothing to commit, working tree clean" in out:
        return False

    env = (
        f"GIT_AUTHOR_NAME='{author_name}' GIT_AUTHOR_EMAIL='{author_email}' "
        + f"GIT_COMMITTER_NAME='{author_name}' GIT_COMMITTER_EMAIL='{author_email}'"
    )
    run(f"{env} git -C {clone_dir} commit -am '{message}'")
    return True


def push(clone_dir: str) -> None:
    """Push commits to the remote."""
    run(f"git -C {clone_dir} push")


def run(cmd: str) -> str:
    """Run cmd in a shell and return its output."""
    print("% ", cmd)
    out = subprocess.check_output(cmd, shell=True).decode("utf-8")
    print("->", out)
    return out
