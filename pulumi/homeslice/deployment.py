import pulumi_kubernetes as kubernetes

def deployment(name: str,
               image: str,
               metadata: kubernetes.meta.v1.ObjectMetaArgs,
               args: list[str] = [],
               replicas: int = 1,
               env_from: list[kubernetes.core.v1.EnvFromSourceArgs] = [],
               ports: list[kubernetes.core.v1.ContainerPortArgs] = [],
               volume_mounts: list[kubernetes.core.v1.VolumeMountArgs] = [],
               volumes: list[kubernetes.core.v1.VolumeArgs] = [],
               ) -> kubernetes.apps.v1.Deployment:

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
                )
            )
        )
    )
