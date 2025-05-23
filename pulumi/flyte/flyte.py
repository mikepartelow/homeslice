"""Resources for the homeslice/flyte app."""

import yaml
import json
import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
import importlib.resources
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    flyte as FLYTE_SECRETS,
)

NAME = "flyte"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/flyte app"""
    ns = homeslice.namespace(config["namespace"])

    db_secret = kubernetes.core.v1.Secret(
        config["secret-name"],
        metadata=homeslice.metadata(config["secret-name"], namespace=NAME),
        type="Opaque",
        string_data={
            "202-database-secrets.yaml": json.dumps(
                {
                    "database": {
                        "postgres": {
                            "password": FLYTE_SECRETS.DB_PASSWORD,
                        }
                    }
                }
            )
        },
    )

    for chart in config["charts"]:
        if filename := chart.get("values-resource"):
            with importlib.resources.open_text("flyte", filename) as f:
                values = yaml.safe_load(render_values(f.read()))
        else:
            values = render_values(chart.get("values"))

        kubernetes.helm.v3.Release(
            chart["name"],
            kubernetes.helm.v3.ReleaseArgs(
                chart=chart["chart"],
                name=chart["name"],
                namespace=config["namespace"],
                version=chart["version"],
                repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                    repo=chart.get("repo"),
                ),
                values=values,
            ),
            pulumi.ResourceOptions(depends_on=[ns, db_secret]),
        )


def render_values(thing: str | dict | list) -> str | dict | None:
    if thing is None:
        return None
    if isinstance(thing, dict):
        for k, v in thing.items():
            thing[k] = render_values(v)
    elif isinstance(thing, list):
        for i in range(0, len(thing)):
            thing[i] = render_values(thing[i])
    else:
        thing = thing.replace("%DB_PASSWORD%", FLYTE_SECRETS.DB_PASSWORD).replace(
            "%MINIO_PASSWORD%", FLYTE_SECRETS.MINIO_PASSWORD
        )
    return thing
