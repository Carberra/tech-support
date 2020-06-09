from datetime import date, datetime

import aiofiles
import aiofiles.os

from discord import File
from discord.ext import commands


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return commands.has_role("Staff")

    @commands.command()
    async def tickets(self, ctx):
        t = datetime.now().timestamp()

        async with aiofiles.open(f"./data/tickets-{t}.txt", mode="w") as f:
            await f.write("\n".join(map(repr, self.bot.get_cog("Support").tickets._tickets)))

        await ctx.author.send(content=f"Tickets as at {date.today()}", file=File(f"./data/tickets-{t}.txt"))

        await aiofiles.os.remove(f"./data/tickets-{t}.txt")


def setup(bot):
    bot.add_cog(Staff(bot))
