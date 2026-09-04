"""Functions for authenticating to Tidal."""

from pathlib import Path
import json
import tidalapi


class TidalAuthError(RuntimeError):
    """Raised when stored Tidal credentials cannot authenticate a session."""


def store_creds(session: tidalapi.Session, path_to_creds: str):
    """Store Tidal session credentials to a JSON file."""
    creds = {
        "token_type": session.token_type,
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "expiry_time": session.expiry_time,
    }

    with open(path_to_creds, "w", encoding="utf-8") as creds_f:
        json.dump(creds, creds_f, default=str)


def load_creds(path_to_creds: str):
    """Load Tidal session credentials from a JSON file."""
    if Path(path_to_creds).exists():
        with open(path_to_creds, "r", encoding="utf-8") as creds_f:
            return json.load(creds_f)
    return None


def login(session: tidalapi.Session, path_to_creds: str):
    """Login to Tidal with stored or fresh credentials."""
    creds = load_creds(path_to_creds)
    if creds is None:
        raise TidalAuthError(
            "Tidal credentials are missing; run `make login` and update the deployment secret."
        )

    try:
        session.load_oauth_session(
            creds["token_type"],
            creds["access_token"],
            creds["refresh_token"],
            creds["expiry_time"],
        )
        if not session.check_login():
            raise TidalAuthError(
                "Tidal credentials are expired; run `make login` and update the deployment secret."
            )
    except TidalAuthError:
        raise
    except Exception as exc:
        raise TidalAuthError(
            "Tidal authentication failed; run `make login` and update the deployment secret."
        ) from exc
