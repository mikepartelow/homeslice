"""kubernetes Deployment factory"""

import pulumi_kubernetes as kubernetes
import homeslice
from typing import Any, List, Optional


def deployment(
    name: str,
    image: str,
    command: Optional[List[str]] = None,
    args: Optional[List[str]] = None,
    replicas: int = 1,
    env: Optional[List[kubernetes.core.v1.EnvVarArgs]] = None,
    env_from: Optional[List[kubernetes.core.v1.EnvFromSourceArgs]] = None,
    ports: Optional[List[kubernetes.core.v1.ContainerPortArgs]] = None,
    volumes: Optional[List[kubernetes.core.v1.VolumeArgs]] = None,
    volume_mounts: Optional[List[kubernetes.core.v1.VolumeMountArgs]] = None,
    host_network: bool = False,
    node_selector: Optional[Any] = None,
    strategy: Optional[kubernetes.apps.v1.DeploymentStrategyArgs] = None,
) -> kubernetes.apps.v1.Deployment:
    # pylint: disable=too-many-arguments
    """THE kubernetes Deployment factory"""

    metadata = homeslice.metadata(name)

    for a in ("args", "command", "env", "env_from", "ports", "volume_mounts", "volumes"):
        locals()[a] = locals()[a] or []

    tolerations = [
        kubernetes.core.v1.TolerationArgs(
            key="node.kubernetes.io/unreachable",
            operator="Exists",
            effect="NoExecute",
            toleration_seconds=2,
        ),
        kubernetes.core.v1.TolerationArgs(
            key="node.kubernetes.io/not-ready",
            operator="Exists",
            effect="NoExecute",
            toleration_seconds=2,
        ),
    ]

    return kubernetes.apps.v1.Deployment(
        name,
        metadata=metadata,
        spec=kubernetes.apps.v1.DeploymentSpecArgs(
            selector=kubernetes.meta.v1.LabelSelectorArgs(
                match_labels=metadata.labels,
            ),
            strategy=strategy,
            replicas=replicas,
            template=kubernetes.core.v1.PodTemplateSpecArgs(
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    labels=metadata.labels,
                ),
                spec=kubernetes.core.v1.PodSpecArgs(
                    node_selector=node_selector,
                    host_network=host_network,
                    containers=[
                        kubernetes.core.v1.ContainerArgs(
                            name=name,
                            image=image,
                            args=args,
                            command=command,
                            env=env,
                            env_from=env_from,
                            ports=ports,
                            volume_mounts=volume_mounts,
                        ),
                    ],
                    tolerations=tolerations,
                    volumes=volumes,
                ),
            ),
        ),
    )
