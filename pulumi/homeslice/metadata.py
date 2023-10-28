"""kubernetes metadata factory"""

import pulumi_kubernetes as kubernetes


def metadata(
    name: str,
    namespace: str,
    labels: dict[str, str] = None,
    annotations: dict[str, str] = None,
) -> kubernetes.meta.v1.ObjectMetaArgs:
    """THE kubernetes metadata factory"""

    if labels is None:
        labels = {"app.kubernetes.io/name": name}

    return kubernetes.meta.v1.ObjectMetaArgs(
        annotations=annotations,
        labels=labels,
        name=name,
        namespace=namespace,
    )
