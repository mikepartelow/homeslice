#!/venv/bin/python
"""Fetch a Tidal playlist and write it to a JSON file."""
from datetime import datetime
from lib import auth
import os
import tidalapi

PATH_TO_CREDS = os.environ["PATH_TO_CREDS"]


def main():
    """Does the magic."""
    session = tidalapi.Session()
    session.login_oauth_simple()

    auth.store_creds(session, PATH_TO_CREDS)


if __name__ == "__main__":
    main()
