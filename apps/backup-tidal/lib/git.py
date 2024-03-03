import re
import subprocess
from pathlib import Path


def add(clone_dir: str, filename: str) -> None:
    run(f"git -C {clone_dir} add {filename}")


def clone(repo_name: str, clone_dir: str) -> None:
    if Path.exists(clone_dir):
        print(f"⚠️  clone already exists at {clone_dir}, not replacing it.")
        return
    run(f"git clone {repo_name} {clone_dir}")


# returns False if there is nothing to commit, otherwise, commits and returns True
def commit(clone_dir: str, author: str, message: str) -> bool:
    out = run(f"git -C {clone_dir} status")
    if "nothing to commit, working tree clean" in out:
        return False

    match = re.match(r"(.*) <(.*)>", author)
    name = match.group(1)
    email = match.group(2)

    env = f"GIT_AUTHOR_NAME='{name}' GIT_AUTHOR_EMAIL='{email}' GIT_COMMITTER_NAME='{name}' GIT_COMMITTER_EMAIL='{email}'"
    run(f"{env} git -C {clone_dir} commit -am '{message}'")
    return True


def push(clone_dir: str) -> None:
    run(f"git -C {clone_dir} push")


def run(cmd: str) -> str:
    print("% ", cmd)
    out = subprocess.check_output(cmd, shell=True).decode("utf-8")
    print("->", out)
    return out
