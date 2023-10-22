import pulumi
import pulumi_kubernetes as kubernetes
import homeslice

NAME = "buttons"

def app(namespace: str, config: pulumi.Config) -> None:
    image = config["image"]
    container_port = int(config["container_port"])
    clocktime_url = config["clocktime_url"]
    ingress_enabled = config.get("ingress_enabled", "false") == True
    ingress_prefixes = config.get("ingress_prefixes")

    metadata=homeslice.metadata(NAME, namespace)

    configmap = kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data={
            "CLOCKTIME_URL": clocktime_url,
        }
    )

    env_from = [
        kubernetes.core.v1.EnvFromSourceArgs(
            config_map_ref=kubernetes.core.v1.ConfigMapEnvSourceArgs(
                name=configmap.metadata.name,
            )
        )
    ]

    ports = [
        kubernetes.core.v1.ContainerPortArgs(
            name="http",
            container_port=container_port,
        )
    ]

    deployment = homeslice.deployment(NAME, image, metadata, env_from=env_from, ports=ports)

    service = homeslice.service(NAME, metadata)

    if ingress_enabled:
        ingress = homeslice.ingress(NAME, metadata, ingress_prefixes)

    # these are here just so we don't get unused variable warnings
    pulumi.export("buttonDeploymentName", deployment.metadata.name)
    pulumi.export("buttonServiceName", service.metadata.name)
    if ingress_enabled:
        pulumi.export("buttonIngressName", ingress.metadata.name)
