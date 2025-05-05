"""Resources for the homeslice/flyte app."""
import yaml
import pulumi_kubernetes as kubernetes
import pulumi
import homeslice
import importlib.resources

NAME = "flyte"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/flyte app"""

    ns = homeslice.namespace(config["namespace"])

    for chart in config["charts"]:

        if filename := config.get("values-resource"):
            with importlib.resources.open_text('flyte', filename) as f:
                values = yaml.load(f)
        else:
            values = config.get("values")

        kubernetes.helm.v3.Release(
            chart["name"],
            kubernetes.helm.v3.ReleaseArgs(
                chart=chart["name"],
                name=chart["name"],
                namespace=config["namespace"],
                version=chart["version"],
                repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                    repo=chart["repo"],
                ),
                values=values,
            ),
            pulumi.ResourceOptions(depends_on=[ns])
        )
