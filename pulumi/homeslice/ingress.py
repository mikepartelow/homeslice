"""kubernetes Ingress factory"""
import pulumi_kubernetes as kubernetes


def ingress(
    name: str,
    metadata: kubernetes.meta.v1.ObjectMetaArgs,
    ingress_prefixes: [str],
    path_type: str = "Prefix",
) -> kubernetes.core.v1.Service:
    """THE kubernetes Ingress factory"""

    return kubernetes.networking.v1.Ingress(
        name,
        metadata=metadata,
        spec=kubernetes.networking.v1.IngressSpecArgs(
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
