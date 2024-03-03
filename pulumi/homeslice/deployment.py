"""kubernetes Deployment factory"""
import pulumi_kubernetes as kubernetes
import homeslice


def deployment(
    name: str,
    image: str,
    args: list[str] = None,
    replicas: int = 1,
    env: list[kubernetes.core.v1.EnvVarArgs] = None,
    env_from: list[kubernetes.core.v1.EnvFromSourceArgs] = None,
    ports: list[kubernetes.core.v1.ContainerPortArgs] = None,
    volumes: list[kubernetes.core.v1.VolumeArgs] = None,
    volume_mounts: list[kubernetes.core.v1.VolumeMountArgs] = None,
) -> kubernetes.apps.v1.Deployment:
    # pylint: disable=too-many-arguments
    """THE kubernetes Deployment factory"""

    metadata = homeslice.metadata(name)

    for a in ("args", "env", "env_from", "ports", "volume_mounts", "volumes"):
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
                            env=env,
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
