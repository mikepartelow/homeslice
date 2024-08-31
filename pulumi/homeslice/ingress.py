"""kubernetes Ingress factory"""

import pulumi_kubernetes as kubernetes
import homeslice


def ingress(
    name: str,
    ingress_prefixes: [str],
    path_type: str = "Prefix",
    metadata: kubernetes.meta.v1.ObjectMetaArgs = None,
) -> kubernetes.core.v1.Service:
    """THE kubernetes Ingress factory"""

    metadata = metadata or homeslice.metadata(name)

    return kubernetes.networking.v1.Ingress(
        name,
        metadata=metadata,
        spec=kubernetes.networking.v1.IngressSpecArgs(
            ingress_class_name="public",
            rules=[
                kubernetes.networking.v1.IngressRuleArgs(
                    http=kubernetes.networking.v1.HTTPIngressRuleValueArgs(
                        paths=[
                            kubernetes.networking.v1.HTTPIngressPathArgs(
                                backend=kubernetes.networking.v1.IngressBackendArgs(
                                    service=kubernetes.networking.v1.IngressServiceBackendArgs(
                                        name=name,
                                        port=kubernetes.networking.v1.ServiceBackendPortArgs(
                                            name="http",
                                        ),
                                    ),
                                ),
                                path=ingress_prefix,
                                path_type=path_type,
                            )
                            for ingress_prefix in ingress_prefixes
                        ]
                    )
                )
            ]
        ),
    )
