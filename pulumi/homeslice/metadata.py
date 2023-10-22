import pulumi_kubernetes as kubernetes

def metadata(name: str, namespace: str) -> kubernetes.meta.v1.ObjectMetaArgs :
    return kubernetes.meta.v1.ObjectMetaArgs(
        labels={
            "app.kubernetes.io/name": name,
        },
        name=name,
        namespace=namespace,
    )
