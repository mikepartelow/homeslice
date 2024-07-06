"""Resources for the homeslice/monitoring app."""

import pulumi_kubernetes as kubernetes
import pulumi

NAME = "grafana"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/monitoring app"""
    namespace_name = config["namespace"]
    chart_version = config["grafana_chart_version"]
    prometheus_datasource = config["prometheus_datasource"]

    with open("monitoring/dashboards/cronjobs.json", encoding="utf-8") as f:
        cronjobs_json = f.read()

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
                "adminPassword": "admin",
                # pylint: disable=R0801
                "ingress": {
                    "enabled": True,
                    "ingressClassName": "public",
                    "annotations": {
                        "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                    },
                    "path": "/grafana(/|$)(.*)",
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
                        "cronjobs": {
                            "json": cronjobs_json,
                        },
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
                            }
                        ],
                    },
                },
                "grafana.ini": {"server": {"root_url": "http://nucnuc.local/grafana"}},
            },
        ),
    )
