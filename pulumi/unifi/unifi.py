"""Resources for the Unifi auxiliary support."""

import homeslice_config
import homeslice

NAME = "unifi"


def app(config: homeslice_config.LmzConfig) -> None:
    """define resources for the unifi/unifi app"""
    redirect_url = config.redirect_url
    redirect_prefix = config.redirect_prefix

    homeslice.ingress(
        NAME,
        [redirect_prefix],
        metadata=homeslice.metadata(
            NAME,
            annotations={
                "nginx.ingress.kubernetes.io/permanent-redirect": f"{redirect_url}",
            },
        ),
    )
