#!/bin/bash

set -e

export CR=ghcr.io
export CR_USER=mikepartelow
export CR_REPO=homeslice
export CR_APPS=("backup-todoist" "buttons" "chime" "clocktime" "switches")

for CR_APP in "${CR_APPS[@]}"; do
    export TAG=$(docker run --rm quay.io/skopeo/stable list-tags --creds $CR_USER:$CR_PAT docker://ghcr.io/$CR_USER/$CR_REPO/$CR_APP | jq -r '.Tags[] | select(startswith("main."))')
    export TAGGED_IMAGE="$CR/$CR_USER/$CR_REPO/$CR_APP:$TAG"
    export SHA256=$(docker manifest inspect $TAGGED_IMAGE -v | jq -r '.Descriptor.digest')
    export IMAGE=$CR/$CR_USER/$CR_REPO/$CR_APP:$TAG@$SHA256
    echo $IMAGE
done
