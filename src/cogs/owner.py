from datetime import datetime, timedelta

import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ctx.author.id in self.bot.owner_ids

    async def cog_operation(self, function, *cogs: str):
        if len(cogs) == 0:
            return

        cogs = tuple(f"src.cogs.{cog}" for cog in cogs)

        success, fail = [], []

        for cog in cogs:
            try:
                function(cog)
                success.append(cog)
            except Exception as e:
                fail.append(cog)

        return (len(success), len(fail))

    @commands.command()
    async def load(self, ctx, *cogs: str):
        r = await self.cog_operation(self.bot.load_extension, *cogs)
        await ctx.send(f"Success: {r[0]} | Fail: {r[1]}")

    @commands.command()
    async def unload(self, ctx, *cogs: str):
        r = await self.cog_operation(self.bot.unload_extension, *cogs)
        await ctx.send(f"Success: {r[0]} | Fail: {r[1]}")

    @commands.command()
    async def reload(self, ctx, *cogs: str):
        r = await self.cog_operation(self.bot.reload_extension, *cogs)
        await ctx.send(f"Success: {r[0]} | Fail: {r[1]}")

    @commands.command()
    async def purge(self, ctx, amount: int = 0):
        """Purge messages"""
        after = datetime.now() - timedelta(days=14)
        await ctx.channel.purge(limit=amount + 1, after=after)

    @commands.command()
    async def shutdown(self, ctx):
        self.bot.scheduler.shutdown()
        await self.bot.logout()


def setup(bot):
    bot.add_cog(Owner(bot))
