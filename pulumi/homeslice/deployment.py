"""kubernetes Deployment factory"""
import pulumi_kubernetes as kubernetes


def deployment(
    name: str,
    image: str,
    metadata: kubernetes.meta.v1.ObjectMetaArgs,
    args: list[str] = None,
    replicas: int = 1,
    env_from: list[kubernetes.core.v1.EnvFromSourceArgs] = None,
    ports: list[kubernetes.core.v1.ContainerPortArgs] = None,
    volume_mounts: list[kubernetes.core.v1.VolumeMountArgs] = None,
    volumes: list[kubernetes.core.v1.VolumeArgs] = None,
) -> kubernetes.apps.v1.Deployment:
    """THE kubernetes Deployment factory"""

    for a in ("args", "env_from", "ports", "volume_mounts", "volumes"):
        if locals()[a] is None:
            locals()[a] = []

    return kubernetes.apps.v1.Deployment(
        name,
        metadata=metadata,
        spec=kubernetes.apps.v1.DeploymentSpecArgs(
            selector=kubernetes.meta.v1.LabelSelectorArgs(
                match_labels=metadata.labels,
            ),
            replicas=replicas,
            template=kubernetes.core.v1.PodTemplateSpecArgs(
                metadata=kubernetes.meta.v1.ObjectMetaArgs(
                    labels=metadata.labels,
                ),
                spec=kubernetes.core.v1.PodSpecArgs(
                    containers=[
                        kubernetes.core.v1.ContainerArgs(
                            name=name,
                            image=image,
                            args=args,
                            env_from=env_from,
                            ports=ports,
                            volume_mounts=volume_mounts,
                        )
                    ],
                    volumes=volumes,
                ),
            ),
        ),
    )
