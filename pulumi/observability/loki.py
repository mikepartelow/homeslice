"""Resources for the homeslice/observability app."""

import pulumi_kubernetes as kubernetes
from homeslice_config import LokiConfig

NAME = "loki"


def app(config: LokiConfig) -> None:
    """define resources for the homeslice/observability app"""
    namespace_name = config.namespace
    chart_version = config.loki_chart_version

    kubernetes.helm.v3.Release(
        NAME,
        kubernetes.helm.v3.ReleaseArgs(
            chart="loki",
            name=NAME,
            namespace=namespace_name,
            version=chart_version,
            repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                repo="https://grafana.github.io/helm-charts",
            ),
            values={
                "deploymentMode": "SingleBinary",
                "loki": {
                    "auth_enabled": False,
                    "commonConfig": {"replication_factor": 1},
                    "storage": {"type": "filesystem"},
                    "schemaConfig": {
                        "configs": [
                            {
                                "from": "2024-01-01",
                                "store": "tsdb",
                                "index": {"prefix": "loki_index_", "period": "24h"},
                                "object_store": "filesystem",  # Warning: no persistence
                                "schema": "v13",
                            }
                        ]
                    },
                },
                "chunksCache": {
                    "enabled": False,
                },
                "lokiCanary": {
                    "enabled": False,
                },
                "resultsCache": {
                    "enabled": False,
                },
                "test": {
                    "enabled": False,
                },
                "singleBinary": {"replicas": 1},
                "read": {"replicas": 0},
                "backend": {"replicas": 0},
                "write": {"replicas": 0},
            },
        ),
    )
