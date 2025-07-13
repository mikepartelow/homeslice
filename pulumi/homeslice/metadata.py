"""kubernetes metadata factory"""

import pulumi_kubernetes as kubernetes
import homeslice
from typing import Optional, Dict


def metadata(
    name: str,
    labels: Optional[Dict[str, str]] = None,
    annotations: Optional[Dict[str, str]] = None,
    namespace: Optional[str] = None,
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
