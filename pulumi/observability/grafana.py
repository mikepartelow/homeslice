"""Resources for the homeslice/observability app."""

import os
import pulumi_kubernetes as kubernetes
import pulumi
from homeslice_config import GrafanaConfig

DASHBOARDS_ROOT = "observability/dashboards"


class Grafana(pulumi.ComponentResource):
    """Grafana observability resources."""

    def __init__(self, name: str, config: GrafanaConfig, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:observability:Grafana", name, {}, opts)

        namespace_name = config.namespace
        chart_version = config.grafana_chart_version
        ingress_prefix = config.grafana_ingress_prefix
        loki_datasource = config.loki_datasource
        prometheus_datasource = config.prometheus_datasource

        dashboards = []

        for filename in os.listdir(DASHBOARDS_ROOT):
            name = os.path.splitext(filename)[0]
            filename = os.path.join(DASHBOARDS_ROOT, filename)
            with open(filename, encoding="utf-8") as f:
                dashboards.append((name, f.read()))

        self.release = kubernetes.helm.v3.Release(
            name,
            kubernetes.helm.v3.ReleaseArgs(
                # pylint: disable=R0801
                chart="grafana",
                name=name,
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
                            item[0].replace(".json", ""): {"json": item[1]}
                            for item in dashboards
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
                    "grafana.ini": {
                        "server": {"root_url": "http://moe.localdomain/grafana"}
                    },
                },
            ),
        )

        self.register_outputs({})


def app(config: GrafanaConfig) -> None:
    """Define resources for the homeslice/observability app.
    
    Creates a Grafana ComponentResource with Helm release for dashboard visualization.
    """
    Grafana("grafana", config)
