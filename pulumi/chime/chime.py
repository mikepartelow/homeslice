import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
from secrets import backup_todoist
from pathlib import Path

NAME = "chime"

def app(namespace: str, config: pulumi.Config) -> None:
    # image = config["image"]
    nginx = config["nginx"]
    pvc_mount_path = config["pvc_mount_path"]
    container_port = int(config["container_port"])
    ingress_enabled = config.get("ingress_enabled", "false") == True
    ingress_prefix = config.get("ingress_prefix")

    metadata=homeslice.metadata(NAME, namespace)

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

# kubectl cp /local/path/to/file my-pod:/path/in/container

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
                                        "nginx.ingress.kubernetes.io/rewrite-target": "/",
                                    }),
                                    [ingress_prefix]
        )
