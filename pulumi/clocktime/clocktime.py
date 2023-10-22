import pulumi
import pulumi_kubernetes as kubernetes
import homeslice

NAME = "clocktime"

def app(namespace: str, config: pulumi.Config) -> None:
    image = config["image"]
    container_port = int(config["container_port"])
    location = config["location"]
    ingress_enabled = config.get("ingress_enabled", "false") == True
    ingress_prefix = config.get("ingress_prefix")

    metadata=homeslice.metadata(NAME, namespace)

    configmap = kubernetes.core.v1.ConfigMap(
        NAME,
        metadata=metadata,
        data={
            "LOCATION": location,
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
        ingress = homeslice.ingress(NAME, metadata, [ingress_prefix])

    # these are here just so we don't get unused variable warnings
    pulumi.export("clocktimeDeploymentName", deployment.metadata.name)
    pulumi.export("clocktimeServiceName", service.metadata.name)
    if ingress_enabled:
        pulumi.export("clocktimeIngressName", ingress.metadata.name)
