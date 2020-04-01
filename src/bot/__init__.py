from os import getenv
from typing import Final

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Status, Activity, ActivityType
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

TOKEN: Final = getenv('TOKEN')
OWNER_IDS: Final[set] = set([385807530913169426, 102733198231863296])
IGNORE_EXCEPTIONS = (commands.CommandNotFound, commands.BadArgument, commands.CheckFailure)


class Bot(commands.Bot):
    def __init__(self):
        self.DEFAULT_PREFIX = "+"

        self.ready = False
        self.scheduler = AsyncIOScheduler()

        super().__init__(command_prefix=self.DEFAULT_PREFIX, owner_ids=OWNER_IDS)

    def setup(self):
        for cog in ['support', 'owner']:
            self.load_extension(f"src.cogs.{cog}")
            print(f" {cog} cog loaded")

        print("setup complete")

    def run(self):
        print("running setup...")
        self.setup()

        print("running bot...")
        super().run(TOKEN, reconnect=True)

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls=commands.Context)

        if self.ready:
            if ctx.command is not None and ctx.guild is not None:
                await self.invoke(ctx)

        else:
            await ctx.send("Not ready to receive commands.")

    async def on_connect(self):
        print(f" bot connected (DWSP latency: {self.latency*1000:,.0f} ms)")
        await self.change_presence(status=Status.dnd)

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            print(f" scheduler started ({len(self.scheduler.get_jobs()):,} job(s) scheduled)")

            # await self.change_presence(activity=Activity(
            #     name="{} active tickets",
            #     type=Activity.playing
            # ))
            self.ready = True
            print(" bot ready")

    async def on_disconnect(self):
        print("bot disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong.")

        raise

    async def on_command_error(self, ctx, exc):
        # handle these per command
        if any([isinstance(exc, error) for error in IGNORE_EXCEPTIONS]):
            pass

        else:
            raise exc.original

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)


bot = Bot()
