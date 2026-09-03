# homeslice secrets

We store our secrets in Python files that don't get committed in this repo.

## backup_todoist.py

```python
TODOIST_BACKUP_GIT_CLONE_URL="git@github.com:username/some-repo.git",
TODOIST_BACKUP_TODOIST_TOKEN="Todoist auth token",
SSH_PRIVATE_KEY="""an SSH private key with write permissions to $TODOIST_BACKUP_GIT_CLONE"
```

## switches

```python
IP_ADDRESSES = {
    "the fake ip address in Pulumi.prod.yaml": "the real ip address on your network"
}
```
