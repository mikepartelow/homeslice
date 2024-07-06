"""Resources for the homeslice/monitoring app."""

import pulumi_kubernetes as kubernetes
import pulumi

NAME = "prometheus"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/monitoring app"""
    namespace_name = config["namespace"]
    chart_version = config["prometheus_chart_version"]
    hostname = config["hostname"]

    kubernetes.helm.v3.Release(
        "prometheus",
        kubernetes.helm.v3.ReleaseArgs(
            chart="prometheus",
            name=NAME,
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
                        "path": "/prometheus(/|$)(.*)",
                    },
                },
                "prometheus-pushgateway": {
                    "enabled": False,
                },
            },
        ),
    )
