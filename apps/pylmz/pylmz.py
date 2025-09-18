"""web api to turn a la marzocco on and off"""

import asyncio
import signal
from pathlib import Path

from aiohttp import ClientSession

from pylamarzocco import LaMarzoccoCloudClient, LaMarzoccoMachine
from pylamarzocco.util import InstallationKey

import logging
import os
import sys

from aiohttp import web

PORT = 8000


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

    def __init__(self, installation_key_path: Path, creds_path: Path):
        logger.info("Loading key")
        with open(installation_key_path, "r", encoding="utf-8") as f:
            self.installation_key = InstallationKey.from_json(f.read())

        logger.info("Loading creds")
        with open(creds_path, "r", encoding="utf-8") as f:
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


def create_app(machine: Machine) -> web.Application:
    async def on_handler(_: web.Request) -> web.Response:
        try:
            await machine.set_power(True)
        except Exception:
            return web.Response(status=500)
        return web.Response(status=204)

    async def off_handler(_: web.Request) -> web.Response:
        try:
            await machine.set_power(False)
        except Exception:
            return web.Response(status=500)
        return web.Response(status=204)

    async def status_handler(_: web.Request) -> web.Response:
        try:
            status = await machine.status()
        except Exception:
            return web.Response(status=500)

        if status == "PoweredOn":
            return web.Response(text="1", status=200)
        if status == "StandBy":
            return web.Response(text="0", status=200)
        return web.Response(status=500)

    app = web.Application()
    # add_get() is case sensitive
    app.router.add_get("/ON", on_handler)
    app.router.add_get("/OFF", off_handler)
    app.router.add_get("/STATUS", status_handler)

    return app


async def run_app_async(app: web.Application, host: str = "0.0.0.0", port: int = PORT):
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, host=host, port=port)
    await site.start()

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            pass

    try:
        await stop.wait()
    finally:
        await runner.cleanup()


async def main():
    creds = Credentials(
        installation_key_path=Path(os.environ["INSTALLATION_KEY_PATH"]),
        creds_path=Path(os.environ["CREDS_PATH"])
    )

    async with ClientSession() as session:
        machine = Machine(session, creds)
        app = create_app(machine)

        await run_app_async(app, host="0.0.0.0", port=PORT)


if __name__ == "__main__":
    asyncio.run(main())
