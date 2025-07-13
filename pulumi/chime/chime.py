"""Resources for the homeslice/chime app."""

from typing import Mapping
import pulumi
import pulumi_kubernetes as kubernetes
from pulumi_command import local
import homeslice
import homeslice_config
from homeslice_secrets import chime as CHIME_SECRET  # pylint: disable=no-name-in-module


class Chime(pulumi.ComponentResource):
    """Chime app resources."""

    def __init__(self, name: str, config: homeslice_config.ChimeConfig, k8s_context: str, namespace: str, opts: pulumi.ResourceOptions | None = None):
        super().__init__("homeslice:chime:Chime", name, {}, opts)

        # an nginx deployment serves up media from a persistent volume
        #
        # pylint: disable=R0801
        self.pvc = kubernetes.core.v1.PersistentVolumeClaim(
            name,
            metadata=homeslice.metadata(name),
            spec=kubernetes.core.v1.PersistentVolumeClaimSpecArgs(
                access_modes=["ReadWriteOnce"],
                resources=kubernetes.core.v1.VolumeResourceRequirementsArgs(
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
                name=name,
                persistent_volume_claim=kubernetes.core.v1.PersistentVolumeClaimVolumeSourceArgs(
                    claim_name=name,
                ),
            ),
        ]

        volume_mounts = [
            kubernetes.core.v1.VolumeMountArgs(
                name=name,
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
            name, config.nginx, ports=ports, volumes=volumes, volume_mounts=volume_mounts
        )

        # populate the hostPath PV with the chime mp3
        # WARNING: makes heavy assumptions about the PVC's StorageClass!
        # pylint: disable=W0511
        # FIXME: stopped working at some point. come up with a better solution.
        # pylint: disable=line-too-long
        self.populate_command = local.Command(
            "populate",
            opts=pulumi.ResourceOptions(depends_on=[nginx]),
            create=f"""
                scp {CHIME_SECRET.PATH_TO_CHIME_MP3} \
                    $(kubectl --context {k8s_context} \
                        get pv \
                            $(kubectl --context {k8s_context} \
                                get pvc {name} -n {namespace} \
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

        self.service = homeslice.service(name)

        self.ingress = homeslice.ingress(
            name,
            [config.ingress_prefix],
            path_type="ImplementationSpecific",
            metadata=homeslice.metadata(
                name,
                annotations={
                    "nginx.ingress.kubernetes.io/use-regex": "true",
                    "nginx.ingress.kubernetes.io/rewrite-target": "/$2",
                },
            ),
        )

        # cronjobs schedule the chimes.
        self.cronjobs = []
        for chime in config.chimes:
            for zone in CHIME_SECRET.ZONES:
                cronjob_name = make_name(name, chime, zone)
                args = [
                    zone["ip_address"],
                    chime["media_title"],
                    chime["media_uri"].replace("{{ingress}}", CHIME_SECRET.INGRESS),
                ]

                cronjob = homeslice.cronjob(
                    cronjob_name,
                    config.image,
                    chime["schedule"],
                    args=args,
                    metadata=homeslice.metadata(cronjob_name),
                )
                self.cronjobs.append(cronjob)

        self.register_outputs({})


def make_name(name: str, chime: Mapping[str, str], zone: Mapping[str, str]) -> str:
    """Combine the inputs and return a name suitable for a Pulumi URN.
    
    Creates a sanitized name by replacing spaces with hyphens and dots with hyphens
    in the chime media title and zone name, and dots with hyphens in the zone IP.
    """
    boring_title = chime["media_title"].replace(" ", "-")
    boring_zone_name = zone["name"].replace(" ", "-")
    fancy_zone_ip_address = zone["ip_address"].replace(".", "-")
    return (
        name + "-" + boring_title + "-" + fancy_zone_ip_address + "-" + boring_zone_name
    ).lower()


def app(config: homeslice_config.ChimeConfig, k8s_context: str, namespace: str) -> None:
    """Define resources for the homeslice/chime app.
    
    Creates a Chime ComponentResource with PVC, deployment, service, ingress, and cronjobs
    for audio chime functionality across multiple zones.
    """
    Chime("chime", config, k8s_context, namespace)
