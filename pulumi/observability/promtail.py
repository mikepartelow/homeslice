"""Resources for the homeslice/observability app."""

import pulumi_kubernetes as kubernetes
import pulumi

NAME = "promtail"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/observability app"""
    namespace_name = config["namespace"]
    chart_version = config["promtail_chart_version"]
    push_url = config["loki_push_url"]

    kubernetes.helm.v3.Release(
        NAME,
        kubernetes.helm.v3.ReleaseArgs(
            # pylint: disable=R0801
            chart="promtail",
            name=NAME,
            namespace=namespace_name,
            version=chart_version,
            repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                repo="https://grafana.github.io/helm-charts",
            ),
            values={
                "clients": {
                    "url": push_url,
                },
            },
        ),
    )
