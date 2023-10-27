import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from homeslice_secrets import chime as chime_secret
from pathlib import Path

NAME = "chime"

def app(namespace: str, config: pulumi.Config) -> None:
    image = config["image"]
    chimes = config["chimes"]
    nginx = config["nginx"]
    pvc_mount_path = config["pvc_mount_path"]
    container_port = int(config["container_port"])
    ingress_enabled = config.get("ingress_enabled", "false") == True
    ingress_prefix = config.get("ingress_prefix")

    metadata=homeslice.metadata(NAME, namespace)

    # an nginx deployment serves up media from a persistent volume
    #
    pvc = kubernetes.core.v1.PersistentVolumeClaim(
        NAME,
        metadata=metadata,
        spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
            access_modes=["ReadWriteOnce", "ReadOnlyMany"],
            resources=kubernetes.core.v1.ResourceRequirementsArgs(
                requests={
                    "storage": "256Mi",
                },
                limits={
                    "storage": "256Mi",
                }
            )
        )
    )

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=NAME,
            persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                claim_name=NAME,
            )
        ),
    ]

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=NAME,
            mount_path=pvc_mount_path,
            read_only=True,
        ),
    ]

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=container_port,
        )
    ]

    deployment = homeslice.deployment(NAME,
                                      nginx,
                                      metadata,
                                      ports=ports,
                                      volumes=volumes,
                                      volume_mounts=volume_mounts)

    service = homeslice.service(NAME, metadata)

    if ingress_enabled:
        ingress = homeslice.ingress(NAME,
                                    homeslice.metadata(NAME, namespace, annotations={
                                        "nginx.ingress.kubernetes.io/use-regex": "true",
                                        "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                                    }),
                                    [ingress_prefix],
                                    path_type="ImplementationSpecific",
        )

    # cronjobs schedule the chimes.
    for chime in chimes:
        for zone in chime_secret.ZONES:
            name = make_name(NAME, chime, zone)

            zone_cronjob = kubernetes.batch.v1.CronJob(
                name,
                metadata=homeslice.metadata(name, namespace),
                spec=kubernetes.batch.v1.CronJobSpecArgs(
                    schedule=chime["schedule"],
                    job_template=kubernetes.batch.v1.JobTemplateSpecArgs(
                        spec=kubernetes.batch.v1.JobSpecArgs(
                            template=kubernetes.core.v1.PodTemplateSpecArgs(
                                spec=kubernetes.core.v1.PodSpecArgs(
                                    restart_policy="Never",
                                    containers=[
                                        kubernetes.core.v1.ContainerArgs(
                                            name=name,
                                            image=image,
                                            args=[
                                                zone["ip_address"],
                                                chime["media_title"],
                                                chime["media_uri"].replace("{{ingress}}", chime_secret.INGRESS),
                                            ]
                                        )
                                    ]
                                )
                            )
                        )
                    )
                )
            )

def make_name(name: str, chime: dict, zone: dict) -> str:
    boring_title = chime["media_title"].replace(" ", "-")
    boring_zone_name = zone["name"].replace(" ", "-")
    fancy_zone_ip_address = zone["ip_address"].replace('.', '-')
    return (name+"-"+boring_title+"-"+fancy_zone_ip_address+"-"+boring_zone_name).lower()
