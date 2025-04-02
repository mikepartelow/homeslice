#!/usr/bin/env uv run --no-project

# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "coregio",
#     "pyyaml",
# ]
# ///

"""bump all homeslice images in Pulumi.prod.yaml to the latest from ghcr.io"""


from pathlib import Path
from typing import Generator
import logging
import yaml
from coregio.registry_api import ContainerRegistry  # pylint: disable=import-error

CACHE_FILE = "./bump-cache.yaml"
IMAGE_BASE = "ghcr.io/mikepartelow/homeslice"
IMAGE_PREFIX = "ghcr.io/mikepartelow"
LOCAL_REGISTRY = "registry.localdomain:32000"


def find_keys(haystack: dict, needle: str) -> Generator[str, None, None]:
    """yield all values of key needle in dict haystack"""
    if isinstance(haystack, dict):
        for key, value in haystack.items():
            if key == needle:
                yield value
            yield from find_keys(value, needle)
    elif isinstance(haystack, list):
        for item in haystack:
            yield from find_keys(item, needle)


def get_latest_main(image: str) -> str:
    """return the latest ghcr.io image uri for image"""
    registry = ContainerRegistry("ghcr.io")

    tags = registry.get_tags(image.replace("ghcr.io/", ""))
    tags = [t for t in tags if t.startswith("main.")]

    latest_tag = sorted(tags)[-1]
    manifest = registry.get_manifest_headers(image, latest_tag)
    digest = manifest["docker-content-digest"]

    return f"{image}:{latest_tag}@{digest}"


def get_latest_images(config: dict[any, any]) -> tuple[dict[str, str], bool]:
    """return [{image: latest_image}, used_cache] for all homeslice images in the pulumi config"""
    if Path(CACHE_FILE).exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f), True
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

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(latest_images, f)

        return latest_images, False


PULUMI_FILE = "Pulumi.prod.yaml"


def main():
    """main()"""
    with open(PULUMI_FILE, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    with open(PULUMI_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    latest_images, used_cache = get_latest_images(config)
    for image, latest in latest_images.items():
        logging.info("bumping '%s' to '%s'", image, latest)
        text = text.replace(image, latest)

    with open(PULUMI_FILE, "w", encoding="utf-8") as f:
        f.write(text)

    if used_cache:
        print("WARNING: used cache")


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    main()
