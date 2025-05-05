"""Tidal authentication helpers."""

import json
import logging
from pathlib import Path

import tidalapi  # type: ignore[import-untyped]


def load_creds(path_to_creds: str) -> dict[str, str]:
    """Load Tidal session credentials from a JSON file."""
    logging.debug("reading tidal creds from %s", path_to_creds)
    if Path(path_to_creds).exists():
        with open(path_to_creds, encoding="utf-8") as creds_f:
            return json.load(creds_f)

    raise OSError(f"no such file: {path_to_creds}")


def login(session: tidalapi.Session, path_to_creds: str):
    """Login to Tidal with stored or fresh credentials."""
    logging.debug("logging in to tidal")
    creds = load_creds(path_to_creds)
    session.load_oauth_session(
        creds["token_type"],
        creds["access_token"],
        creds["refresh_token"],
        creds["expiry_time"],
    )
