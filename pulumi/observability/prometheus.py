"""Resources for the homeslice/observability app."""

import pulumi_kubernetes as kubernetes
import pulumi
from homeslice_config import PrometheusConfig


class Prometheus(pulumi.ComponentResource):
    """Prometheus observability resources."""

    def __init__(self, name: str, config: PrometheusConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:observability:Prometheus", name, {}, opts)

        namespace_name = config.namespace
        chart_version = config.prometheus_chart_version
        ingress_prefix = config.prometheus_ingress_prefix
        hostname = config.hostname

        self.release = kubernetes.helm.v3.Release(
            name,
            kubernetes.helm.v3.ReleaseArgs(
                chart="prometheus",
                name=name,
                namespace=namespace_name,
                version=chart_version,
                repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                    repo="https://prometheus-community.github.io/helm-charts",
                ),
                values={
                    "server": {
                        "extraFlags": [
                            "web.enable-lifecycle",
                            "web.route-prefix=/",
                            f"web.external-url=http://{hostname}/prometheus",
                        ],
                        # pylint: disable=R0801
                        "ingress": {
                            "enabled": True,
                            "ingressClassName": "public",
                            "annotations": {
                                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                            },
                            "hosts": [""],
                            "path": f"{ingress_prefix}(/|$)(.*)",
                        },
                    },
                    "prometheus-pushgateway": {
                        "enabled": False,
                    },
                },
            ),
        )

        self.register_outputs({})


def app(config: PrometheusConfig) -> None:
    """define resources for the homeslice/observability app"""
    Prometheus("prometheus", config)
