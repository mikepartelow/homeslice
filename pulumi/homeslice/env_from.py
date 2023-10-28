"""kubernetes env_from factory"""

import pulumi_kubernetes as kubernetes


def env_from_configmap(name: str) -> kubernetes.core.v1.EnvFromSourceArgs:
    """THE kubernetes env_from (configmap) factory"""
    return kubernetes.core.v1.EnvFromSourceArgs(
        config_map_ref=kubernetes.core.v1.ConfigMapEnvSourceArgs(
            name=name,
        )
    )


def env_from_secret(name: str) -> kubernetes.core.v1.EnvFromSourceArgs:
    """THE kubernetes env_from (secret) factory"""
    return kubernetes.core.v1.EnvFromSourceArgs(
        secret_ref=kubernetes.core.v1.SecretEnvSourceArgs(
            name=name,
        )
    )
