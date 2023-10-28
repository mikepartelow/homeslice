# Put these files on chime's PV

## Choice A
1. set the PVC to read/write in chime's pod OR add an ephemeral container
2. `kubectl cp whatever.mp3 $POD:/usr/share/nginx/html -n homeslice`

## Choice B

Find the PV's backing directory on the `microk8s` host filesystem and just copy it there, like `/var/snap/microk8s/common/default-storage/homeslice-chime-pvc-fc0acffe-1234-41e5-beef-1e7d9ac6dec0/`
