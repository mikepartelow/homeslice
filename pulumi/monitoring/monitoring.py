"""Resources for the homeslice/monitoring app."""

import pulumi_kubernetes as kubernetes
import pulumi
import homeslice

NAME = "monitoring"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/monitoring app"""
    namespace_name = config["namespace"]
    prometheus_chart_version = config["prometheus-chart-version"]

    namespace = homeslice.namespace(namespace_name)

    # https://github.com/prometheus-community/helm-charts/tree/main/charts/prometheus
    prometheus = kubernetes.helm.v3.Release(
        "prometheus",
        kubernetes.helm.v3.ReleaseArgs(
            chart="prometheus",
            namespace=namespace_name,
            version=prometheus_chart_version,
            repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                repo="https://prometheus-community.github.io/helm-charts",
            ),
            values={
                "prometheus-pushgateway": {
                    "enabled": False,
                },
            },
        ),
    )
