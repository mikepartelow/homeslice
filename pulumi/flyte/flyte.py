"""Resources for the homeslice/flyte app."""

import importlib.resources
import json
import yaml
import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from homeslice_config import FlyteConfig
from homeslice_secrets import (  # pylint: disable=no-name-in-module
    flyte as FLYTE_SECRETS,
)


class Flyte(pulumi.ComponentResource):
    """Flyte app resources."""

    def __init__(self, name: str, config: FlyteConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:flyte:Flyte", name, {}, opts)

        ns = homeslice.namespace(config.namespace)

        db_secret = kubernetes.core.v1.Secret(
            config.secret_name,
            metadata=homeslice.metadata(config.secret_name, namespace=name),
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

        self.releases = []
        for chart in config.charts:
            if filename := chart.get("values-resource"):
                with importlib.resources.open_text("flyte", filename) as f:
                    values = yaml.safe_load(f.read())
                    values = render_values(values)
            else:
                values = render_values(chart.get("values"))

            release = kubernetes.helm.v3.Release(
                chart["name"],
                kubernetes.helm.v3.ReleaseArgs(
                    chart=chart["chart"],
                    name=chart["name"],
                    namespace=config.namespace,
                    version=chart["version"],
                    repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                        repo=chart.get("repo"),
                    ),
                    values=values if isinstance(values, dict) else None,
                ),
                pulumi.ResourceOptions(depends_on=[ns, db_secret]),
            )
            self.releases.append(release)

        self.register_outputs({})


def render_values(thing: str | dict | list | None) -> str | dict | list | None:
    """Render values by substituting placeholders with secrets.
    
    Recursively processes nested dictionaries and lists, replacing
    %DB_PASSWORD% and %MINIO_PASSWORD% placeholders with actual values.
    """
    if thing is None:
        return None
    if isinstance(thing, dict):
        for k, v in thing.items():
            thing[k] = render_values(v)
    elif isinstance(thing, list):
        for i in range(0, len(thing)):
            thing[i] = render_values(thing[i])
    elif isinstance(thing, str):
        thing = thing.replace("%DB_PASSWORD%", FLYTE_SECRETS.DB_PASSWORD).replace(
            "%MINIO_PASSWORD%", FLYTE_SECRETS.MINIO_PASSWORD
        )
    return thing
