"""Resources for the homeslice/observability app."""

import pulumi_kubernetes as kubernetes
import pulumi
import os

NAME = "grafana"
DASHBOARDS_ROOT = "observability/dashboards"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/observability app"""
    namespace_name = config["namespace"]
    chart_version = config["grafana_chart_version"]
    ingress_prefix = config["grafana_ingress_prefix"]
    loki_datasource = config["loki_datasource"]
    prometheus_datasource = config["prometheus_datasource"]

    dashboards = []

    for filename in os.listdir(DASHBOARDS_ROOT):
        name = os.path.splitext(filename)[0]
        filename = os.path.join(DASHBOARDS_ROOT, filename)
        with open(filename, encoding="utf-8") as f:
            dashboards.append((name, f.read()))

    kubernetes.helm.v3.Release(
        NAME,
        kubernetes.helm.v3.ReleaseArgs(
            chart="grafana",
            name=NAME,
            namespace=namespace_name,
            version=chart_version,
            repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                repo="https://grafana.github.io/helm-charts",
            ),
            values={
                "adminPassword": "admin",
                # pylint: disable=R0801
                "ingress": {
                    "enabled": True,
                    "ingressClassName": "public",
                    "annotations": {
                        "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                    },
                    "path": f"{ingress_prefix}(/|$)(.*)",
                    "hosts": [""],
                },
                "dashboardProviders": {
                    "dashboardproviders.yaml": {
                        "apiVersion": 1,
                        "providers": [
                            {
                                "name": "homeslice",
                                "orgId": 1,
                                "type": "file",
                                "disableDeletion": False,
                                "editable": True,
                                "options": {
                                    "path": "/var/lib/grafana/dashboards/homeslice",
                                },
                            },
                        ],
                    },
                },
                "dashboards": {
                    "homeslice": {
                        item[0].replace(".json", ""): {
                            "json": item[1]
                        } for item in dashboards
                    },
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
                            },
                            {
                                "name": "Loki",
                                "type": "loki",
                                "url": loki_datasource,
                            },
                        ],
                    },
                },
                "grafana.ini": {"server": {"root_url": "http://nucnuc.local/grafana"}},
            },
        ),
    )
