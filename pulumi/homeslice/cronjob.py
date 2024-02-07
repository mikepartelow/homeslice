"""kubernetes Cronjob factory"""
import pulumi_kubernetes as kubernetes
import homeslice


def cronjob(
    name: str,
    image: str,
    schedule: str,
    args: [str] = None,
    restart_policy: str = "Never",
    env_from: list[kubernetes.core.v1.EnvFromSourceArgs] = None,
    volumes: list[kubernetes.core.v1.VolumeArgs] = None,
    volume_mounts: list[kubernetes.core.v1.VolumeMountArgs] = None,
    metadata: kubernetes.meta.v1.ObjectMetaArgs = None,
) -> kubernetes.batch.v1.CronJob:
    # pylint: disable=too-many-arguments,R0801
    """THE kubernetes Cronjob factory"""

    for a in ("args", "env_from", "volume_mounts", "volumes"):
        if locals()[a] is None:
            locals()[a] = []

    if metadata is None:
        metadata = homeslice.metadata(name)

    return kubernetes.batch.v1.CronJob(
        name,
        metadata=metadata,
        spec=kubernetes.batch.v1.CronJobSpecArgs(
            schedule=schedule,
            job_template=kubernetes.batch.v1.JobTemplateSpecArgs(
                spec=kubernetes.batch.v1.JobSpecArgs(
                    ttl_seconds_after_finished=60*60*24,
                    template=kubernetes.core.v1.PodTemplateSpecArgs(
                        spec=kubernetes.core.v1.PodSpecArgs(
                            restart_policy=restart_policy,
                            containers=[
                                kubernetes.core.v1.ContainerArgs(
                                    name=name,
                                    image=image,
                                    args=args,
                                    env_from=env_from,
                                    volume_mounts=volume_mounts,
                                )
                            ],
                            volumes=volumes,
                        ),
                    ),
                ),
            ),
        ),
    )
