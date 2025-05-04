"""Tidal authentication helpers."""

import json
from pathlib import Path

import tidalapi  # type: ignore[import-untyped]


def load_creds(path_to_creds: str):
    """Load Tidal session credentials from a JSON file."""
    if Path(path_to_creds).exists():
        with open(path_to_creds, encoding="utf-8") as creds_f:
            return json.load(creds_f)

    return None


def login(session: tidalapi.Session, path_to_creds: str):
    """Login to Tidal with stored or fresh credentials."""
    creds = load_creds(path_to_creds)
    session.load_oauth_session(
        creds["token_type"],
        creds["access_token"],
        creds["refresh_token"],
        creds["expiry_time"],
    )
