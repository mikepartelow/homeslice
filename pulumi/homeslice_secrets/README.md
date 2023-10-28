# homeslice secrets

We store our secrets in Python files that don't get committed in this repo.

## backup_todoist.py

```python
TODOIST_BACKUP_GIT_CLONE_URL="git@github.com:username/some-repo.git",
TODOIST_BACKUP_TODOIST_TOKEN="Todoist auth token",
SSH_PRIVATE_KEY="""an SSH private key with write permissions to $TODOIST_BACKUP_GIT_CLONE"
```

## chime.py

```python
ZONES = [
    {
        "ip_address": "1.2.3.4",
        "name": "Vault 13",
    },
    {
        "ip_address": "6.5.4.3",
        "name": "Rooftop Pool",
    },
]

INGRESS = "ip address of your ingress, so sonos can play the mp3 hosted on your persistent volume"
```

## switches

```python
IP_ADDRESSES = {
    "the fake ip address in Pulumi.prod.yaml": "the real ip address on your network"
}
```
