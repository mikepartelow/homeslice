"""Resources for the homeslice/observability app."""

import pulumi
import pulumi_kubernetes as kubernetes
from homeslice_config import PromtailConfig


class Promtail(pulumi.ComponentResource):
    """Promtail observability resources."""

    def __init__(self, name: str, config: PromtailConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:observability:Promtail", name, {}, opts)

        namespace_name = config.namespace
        chart_version = config.promtail_chart_version
        push_url = config.loki_push_url

        self.release = kubernetes.helm.v3.Release(
            name,
            kubernetes.helm.v3.ReleaseArgs(
                # pylint: disable=R0801
                chart="promtail",
                name=name,
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

        self.register_outputs({})


def app(config: PromtailConfig) -> None:
    """Define resources for the homeslice/observability app.
    
    Creates a Promtail ComponentResource with Helm release for log shipping to Loki.
    """
    Promtail("promtail", config)
