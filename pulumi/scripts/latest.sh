#!/bin/bash

set -e

CR=ghcr.io
CR_USER=mikepartelow
CR_REPO=homeslice
CR_APPS=("backup-todoist" "buttons" "chime" "clocktime" "switches")

for CR_APP in "${CR_APPS[@]}"; do
    TAG=$(docker run --rm quay.io/skopeo/stable list-tags "docker://ghcr.io/$CR_USER/$CR_REPO/$CR_APP" | jq -r '.Tags[] | select(startswith("main."))')
    TAGGED_IMAGE="$CR/$CR_USER/$CR_REPO/$CR_APP:$TAG"
    SHA256=$(docker manifest inspect "$TAGGED_IMAGE" -v | jq -r '.Descriptor.digest')
    IMAGE="$CR/$CR_USER/$CR_REPO/$CR_APP:$TAG@$SHA256"
    echo "$IMAGE"
done
