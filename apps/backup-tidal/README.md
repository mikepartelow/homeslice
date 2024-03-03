# Tidal Dumpus

Download a playlist from Tidal and store it in a local JSON file.

## Setup

1. Create auth and refresh tokens

```bash
% make login
```

2. Create config file `./backup-tidal.json`

```json
{
    "playlist_id": "4d056fb5-99f9-46ec-8ff3-f2dddd41821f",
    "playlist_name": "taylor_swift_essentials"
}
```

- `playlist_id` is the id from Tidal's `Share > Copy Playlist Link`
- `playlist_name` is the base name of the file that `tidal-dumpus` will create

3. Backup playlist

```bash
% export BACKUP_REPO=git@github.com:somebody/some-repo.git
% export GIT_AUTHOR='Your Name <your@email.address>'
% make backup
```

Playlist JSON will be committed and pushed to `$BACKUP_REPO`.

`make backup` uses a `readonly` bind mount to mount your local `$HOME/.ssh` into the container, so you can authenticate to `$BACKUP_REPO`.


## Credits

All the hard work was done by [tamland](https://github.com/tamland/python-tidal)
