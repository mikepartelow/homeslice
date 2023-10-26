import pulumi
import pulumi_kubernetes as kubernetes
import homeslice
import json
import sys

NAME = "switches"
SWITCHES_JSON_ROOT = "/var/run/"

def app(namespace: str, config: pulumi.Config) -> None:
    image = config["image"]
    container_port = int(config["container_port"])
    ingress_enabled = config.get("ingress_enabled", "false") == True
    ingress_prefix = config.get("ingress_prefix")
    switches_json = subst_address(config["switches_json"])

    metadata=homeslice.metadata(NAME, namespace)

    configmap = kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data={
            "switches.json" : switches_json,
        }
    )

    volumes = [
        kubernetes.core.v1.VolumeArgs(
            name="switches-json",
            config_map=kubernetes.core.v1.ConfigMapVolumeSourceArgs(
                name=NAME,
            )
        ),
    ]

    volume_mounts = [
        kubernetes.core.v1.VolumeMountArgs(
            name="switches-json",
            mount_path=SWITCHES_JSON_ROOT,
            read_only=True,
        ),
    ]

    ports=[
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=container_port,
        )
    ]

    deployment = homeslice.deployment(NAME,
                                      image,
                                      metadata,
                                      args=[SWITCHES_JSON_ROOT+"switches.json"],
                                      ports=ports,
                                      volumes=volumes,
                                      volume_mounts=volume_mounts)


    service = homeslice.service(NAME, metadata)

    if ingress_enabled:
        ingress = homeslice.ingress(NAME, metadata, [ingress_prefix])

# I don't want to publish IP addresses to GitHub
def subst_address(s: str) -> str:
    from secrets import switches

    for k, v in switches.SECRETS.items():
        s = s.replace(k, v)

    return s
