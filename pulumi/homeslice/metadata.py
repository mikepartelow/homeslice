"""kubernetes metadata factory"""

import pulumi_kubernetes as kubernetes
import homeslice


def metadata(
    name: str,
    labels: dict[str, str] | None = None,
    annotations: dict[str, str] | None = None,
    namespace: str | None = None,
) -> kubernetes.meta.v1.ObjectMetaArgs:
    """THE kubernetes metadata factory"""

    labels = labels or {"app.kubernetes.io/name": name}
    namespace = namespace or homeslice.HOMESLICE

    return kubernetes.meta.v1.ObjectMetaArgs(
        annotations=annotations,
        labels=labels,
        name=name,
        namespace=namespace,
    )
