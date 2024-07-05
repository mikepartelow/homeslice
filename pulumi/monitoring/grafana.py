"""Resources for the homeslice/monitoring app."""

import pulumi_kubernetes as kubernetes
import pulumi
import homeslice

NAME = "grafana"

# FIXME:
# - import dashboard like: https://github.com/grafana/helm-charts/blob/main/charts/grafana/values.yaml#L741

def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/monitoring app"""
    namespace_name = config["namespace"]
    chart_version = config["grafana_chart_version"]
    prometheus_datasource = config["prometheus_datasource"]

    kubernetes.helm.v3.Release(
        "grafana",
        kubernetes.helm.v3.ReleaseArgs(
            chart="grafana",
            name=NAME,
            namespace=namespace_name,
            version=chart_version,
            repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                repo="https://grafana.github.io/helm-charts",
            ),
            values={
                "ingress": {
                    "enabled": True,
                    "ingressClassName": "public",
                    "annotations": {
                        "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                    },
                    "path": "/grafana(/|$)(.*)",
                    "hosts": [""],
                },
                "datasources": {
                    "datasources.yaml": {
                        "apiVersion": 1,
                        "datasources": [
                            {
                                "name": "Prometheus",
                                "type": "prometheus",
                                "url": prometheus_datasource,
                                "access": "proxy",
                                "isDefault": "true",
                            }
                        ],
                    },
                },
                "grafana.ini": {"server": {"root_url": "http://nucnuc.local/grafana"}},
            },
        ),
    )
