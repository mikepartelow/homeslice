"""web api to turn a la marzocco on and off"""

import asyncio
import uuid
from pathlib import Path

from aiohttp import ClientSession

from pylamarzocco import LaMarzoccoCloudClient, LaMarzoccoMachine
from pylamarzocco.util import InstallationKey

import logging
import os
import sys

log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class Credentials:
    installation_key: InstallationKey
    username: str
    password: str
    serial: str

    def __init__(self):
        key_file = Path("installation_key.json")
        creds_file = Path("creds.txt")

        logger.info("Loading key")
        with open(key_file, "r", encoding="utf-8") as f:
            self.installation_key = InstallationKey.from_json(f.read())

        logger.info("Loading creds")
        with open(creds_file, "r", encoding="utf-8") as f:
            self.username = f.readline().strip()
            self.password = f.readline().strip()
            self.serial = f.readline().strip()

class Machine(LaMarzoccoMachine):
    def __init__(self, session: ClientSession, creds: Credentials):
        client = LaMarzoccoCloudClient(
            username=creds.username,
            password=creds.password,
            installation_key=creds.installation_key,
            client=session,
        )

        super().__init__(creds.serial, client)

    async def status(self) -> str:
        await self.get_dashboard()
        for widget in self.to_dict()["dashboard"]["widgets"]:
            if widget["code"] == "CMMachineStatus":
                return widget["output"]["status"] # StandBy or PoweredOn
        raise IndexError("oops")


async def main():
    creds = Credentials()

    async with ClientSession() as session:
        machine = Machine(session, creds)
        status = await machine.status()

        print("status", status)

        if status == "StandBy":
            await machine.set_power(True)
        elif status == "PoweredOn":
            await machine.set_power(False)


asyncio.run(main())
