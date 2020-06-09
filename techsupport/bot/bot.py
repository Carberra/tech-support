from os import getenv
from pathlib import Path
from typing import Final

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Activity, ActivityType, Status
from discord.ext import commands

from .config import Config
from ..database import Database
from ..utils import ActivityUtility


class Bot(commands.Bot):
    def __init__(self, loop=None):
        self.ready = False
        self.scheduler = AsyncIOScheduler()
        self.database = Database()

        super().__init__(loop=loop, command_prefix=Config.PREFIX, owner_ids=Config.OWNER_IDS)

    def setup(self):
        print("Running setup...")

        for cog in list(Path(".").glob("**/cogs/*.py")):
            self.load_extension(".".join(cog.with_suffix("").parts))
            print(f"loaded cog `{cog.with_suffix('').name}`")

    def run(self, *args, **kwargs):
        print("Running bot...")
        self.setup()
        super().run(*args, **kwargs)

    async def shutdown(self):
        print("Shutting down...")
        self.scheduler.shutdown()
        await self.database.close()
        await self.logout()

    async def process_commands(self, message):
        ctx = await self.get_context(message)

        if self.ready:
            if ctx.command is not None and ctx.guild is not None:
                await self.invoke(ctx)
        else:
            await ctx.send("Not ready to receive commands.")

    async def on_connect(self):
        print(f"bot connected, latency={self.latency*1000:,.0f} ms")
        await ActivityUtility.dnd(self)

        await self.database.connect()
        print(f"connected to database")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            print(f"scheduler started, {len(self.scheduler.get_jobs())} jobs scheduled")

            await ActivityUtility.update(self)

            self.ready = True
            print("bot ready")

    async def on_resumed(self):
        print("bot resumed")

    async def on_error(self, event, *args, **kwargs):
        raise

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)

    async def on_command_error(self, ctx, error):
        if any([isinstance(error, e) for e in Config.IGNORE_EXCEPTIONS]):
            pass
        elif hasattr(error, "original"):
            raise error.original
        else:
            raise error
