"""Resources for the homeslice/chime app."""

import pulumi_kubernetes as kubernetes
from pulumi_command import local
import pulumi
import homeslice
import homeslice_config
from homeslice_secrets import chime as CHIME_SECRET  # pylint: disable=no-name-in-module


NAME = "chime"


def app(config: homeslice_config.ChimeConfig, k8s_context: str, namespace: str) -> None:
    """define resources for the homeslice/chime app"""
    # an nginx deployment serves up media from a persistent volume
    #
    # pylint: disable=R0801
    kubernetes.core.v1.PersistentVolumeClaim(
        NAME,
        metadata=homeslice.metadata(NAME),
        spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
            access_modes=["ReadWriteOnce"],
            resources=kubernetes.core.v1.ResourceRequirementsArgs(
                requests={
                    "storage": "256Mi",
                },
                limits={
                    "storage": "256Mi",
                },
            ),
        ),
    )

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name=NAME,
            persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                claim_name=NAME,
            ),
        ),
    ]

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name=NAME,
            mount_path=config.pvc_mount_path,
            read_only=True,
        ),
    ]

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=config.container_port,
        )
    ]

    nginx = homeslice.deployment(
        NAME, config.nginx, ports=ports, volumes=volumes, volume_mounts=volume_mounts
    )

    # populate the hostPath PV with the chime mp3
    # WARNING: makes heavy assumptions about the PVC's StorageClass!
    # FIXME: stopped working at some point. come up with a better solution.
    # pylint: disable=line-too-long
    local.Command(
        "populate",
        opts=pulumi.ResourceOptions(depends_on=[nginx]),
        create=f"""
            scp {CHIME_SECRET.PATH_TO_CHIME_MP3} \
                $(kubectl --context {k8s_context} \
                    get pv \
                        $(kubectl --context {k8s_context} \
                            get pvc {NAME} -n {namespace} \
                            -o jsonpath='{{.spec.volumeName}}' \
                        ) \
                    -o jsonpath='{{.spec.nodeAffinity.required.nodeSelectorTerms[0].matchExpressions[0].values[0]}}:{{.spec.local.path}}' \
                )
        """,
        triggers=[nginx],
    )

    # FIXME: update local.Command to work but keep this reminder
    pulumi.export(
        "chime mp3",
        "remember to manually populate chime.mp3 somewhere under /var/snap/microk8s/common/default-storage/ on the node, if using hostPathStorage",
    )

    homeslice.service(NAME)

    homeslice.ingress(
        NAME,
        [config.ingress_prefix],
        path_type="ImplementationSpecific",
        metadata=homeslice.metadata(
            NAME,
            annotations={
                "nginx.ingress.kubernetes.io/use-regex": "true",
                "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
            },
        ),
    )

    # cronjobs schedule the chimes.
    for chime in config.chimes:
        for zone in CHIME_SECRET.ZONES:
            name = make_name(NAME, chime, zone)
            args = [
                zone["ip_address"],
                chime["media_title"],
                chime["media_uri"].replace("{{ingress}}", CHIME_SECRET.INGRESS),
            ]

            homeslice.cronjob(
                name,
                config.image,
                chime["schedule"],
                args=args,
                metadata=homeslice.metadata(name),
            )


def make_name(name: str, chime: dict, zone: dict) -> str:
    """Combine the inputs and return a name suitable for a Pulumi URN"""
    boring_title = chime["media_title"].replace(" ", "-")
    boring_zone_name = zone["name"].replace(" ", "-")
    fancy_zone_ip_address = zone["ip_address"].replace(".", "-")
    return (
        name + "-" + boring_title + "-" + fancy_zone_ip_address + "-" + boring_zone_name
    ).lower()
