"""kubernetes Deployment factory"""

import pulumi_kubernetes as kubernetes
import homeslice


def deployment(
    name: str,
    image: str,
    command: list[str] = None,
    args: list[str] = None,
    replicas: int = 1,
    env_from: list[kubernetes.core.v1.EnvFromSourceArgs] = None,
    ports: list[kubernetes.core.v1.ContainerPortArgs] = None,
    volumes: list[kubernetes.core.v1.VolumeArgs] = None,
    volume_mounts: list[kubernetes.core.v1.VolumeMountArgs] = None,
    host_network: bool = False,
    node_selector: any = None,
    strategy: kubernetes.apps.v1.DeploymentStrategyArgs | None = None,
) -> kubernetes.apps.v1.Deployment:
    # pylint: disable=too-many-arguments
    """THE kubernetes Deployment factory"""

    metadata = homeslice.metadata(name)

    for a in ("args", "command", "env_from", "ports", "volume_mounts", "volumes"):
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
