#!/usr/bin/env python

from pathlib import Path
from typing import Generator
import logging
import requests
import yaml
from coregio.registry_api import ContainerRegistry


def find_keys(haystack: dict, needle: str) -> Generator[str, None, None]:
    if isinstance(haystack, dict):
        for key, value in haystack.items():
            if key == needle:
                yield value
            yield from find_keys(value, needle)
    elif isinstance(haystack, list):
        for item in haystack:
            yield from find_keys(item, needle)

def get_latest_main(image: str) -> str:
    registry = ContainerRegistry("ghcr.io")

    tags = registry.get_tags(image.replace("ghcr.io/", ""))
    tags = [t for t in tags if t.startswith("main.")]

    latest_tag = sorted(tags)[-1]
    manifest = registry.get_manifest_headers(image, latest_tag)
    digest = manifest['docker-content-digest']

    return f"{image}:{latest_tag}@{digest}"

CACHE_FILE = "./bump-cache.yaml"
IMAGE_BASE = "ghcr.io/mikepartelow/homeslice"
IMAGE_PREFIX = "ghcr.io/mikepartelow"
LOCAL_REGISTRY = "registry.localdomain:32000"

def get_latest_images(config: dict[any, any]) -> dict[str, str]:
    if Path(CACHE_FILE).exists():
        with open(CACHE_FILE, "r") as f:
            return yaml.safe_load(f)
    else:
        latest_images: dict[str, str] = {}

        for image in find_keys(config, "image"):
            logging.info("found image '%s'", image)

            if image.startswith(IMAGE_PREFIX):
                base_image = image.split(":")[0]
            elif image.startswith(LOCAL_REGISTRY):
                logging.warning("image '%s' hosted locally", image)
                name = image.split("/")[1].split(":")[0]
                base_image = f"{IMAGE_BASE}/{name}"
            else:
                logging.warning("image '%s' not bumpable", image)
                continue

            latest = get_latest_main(base_image)
            latest_images[image] = latest
            logging.info("got latest: '%s' : '%s'", image, latest)

        with open(CACHE_FILE, "w") as f:
            yaml.safe_dump(latest_images, f)

        return latest_images


PULUMI_FILE = "Pulumi.prod.yaml"

def main():
    with open(PULUMI_FILE, "r") as f:
        config = yaml.safe_load(f)

    with open(PULUMI_FILE, "r") as f:
        text = f.read()

    for (image, latest) in get_latest_images(config).items():
        logging.info("bumping '%s' to '%s'", image, latest)
        text = text.replace(image, latest)

    with open(PULUMI_FILE, "w") as f:
        f.write(text)

if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    main()
