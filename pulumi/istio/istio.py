"""Resources for the homeslice/istio app."""

import pulumi_kubernetes as kubernetes
import pulumi
import homeslice

NAME = "istio"


def app(config: pulumi.Config) -> None:
    """define resources for the homeslice/istio app"""

    ns = homeslice.namespace(config.namespace)

    base = release(
        "istio/base",
        config.istio_chart_version,
        "https://istio-release.storage.googleapis.com/charts",
        config.namespace,
        {},
        pulumi.ResourceOptions(depends_on=[ns]),
    )

    istiod = release(
        "istio/istiod",
        config.istio_chart_version,
        "https://istio-release.storage.googleapis.com/charts",
        config.namespace,
        {
            "pilot": {"env": {"ENABLE_NATIVE_SIDECARS": "true"}},
        },
        pulumi.ResourceOptions(depends_on=[ns, base])
    )

    if config.kiali_chart_version:
        _ = release(
            "kiali/kiali-server",
            config.kiali_chart_version,
            "https://kiali.org/helm-charts",
            config.namespace,
            {
                "external_services": {
                    "prometheus": {
                        "url": "http://prometheus-server.observability.svc.cluster.local",
                    }
                }
            },
            pulumi.ResourceOptions(depends_on=[ns, istiod]),
        )
        # kubectl create token kiali -n istio-system

    for namespace in config.inject_namespaces:
        kubernetes.core.v1.NamespacePatch(
            f"patch-{namespace}",
            metadata={
                "name": namespace,
                "labels": { "istio-injection": "enabled" },
            },
        )


def release(
    name: str, version: str, repo: str, namespace: str, values: dict[str,any], opts: pulumi.ResourceOptions
) -> kubernetes.helm.v3.Release:
    short_name = name.split("/")[1]
    return kubernetes.helm.v3.Release(
        name,
        kubernetes.helm.v3.ReleaseArgs(
            chart=short_name,
            name=short_name,
            namespace=namespace,
            version=version,
            repository_opts=kubernetes.helm.v3.RepositoryOptsArgs(
                repo=repo,
            ),
            values=values,
        ),
        opts=opts,
    )
