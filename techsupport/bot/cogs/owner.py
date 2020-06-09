from datetime import datetime, timedelta

from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ctx.author.id in self.bot.owner_ids

    async def cog_operation(self, function, *cogs: str):
        if len(cogs) == 0:
            return

        cogs = tuple(f"techsupport.bot.cogs.{cog}" for cog in cogs)

        success, fail = [], []
        for cog in cogs:
            try:
                function(cog)
                success.append(cog)
            except Exception as e:
                fail.append((cog, e))

        return {"success": success, "fail": fail}

    @commands.command()
    async def load(self, ctx, *cogs: str):
        r = await self.cog_operation(self.bot.load_extension, *cogs)
        await ctx.send(f"Success {len(r['success'])} | Fail {len(r['fail'])}")

    @commands.command()
    async def unload(self, ctx, *cogs: str):
        r = await self.cog_operation(self.bot.unload_extension, *cogs)
        await ctx.send(f"Success {len(r['success'])} | Fail {len(r['fail'])}")

    @commands.command()
    async def reload(self, ctx, *cogs: str):
        r = await self.cog_operation(self.bot.reload_extension, *cogs)
        await ctx.send(f"Success {len(r['success'])} | Fail {len(r['fail'])}")

    @commands.command()
    async def purge(self, ctx, amount: int = 0):
        after = datetime.now() - timedelta(days=14)
        await ctx.channel.purge(limit=amount + 1, after=after)

    @commands.command()
    async def shutdown(self, ctx):
        await ctx.send("Shutting down...")
        await self.bot.shutdown()


def setup(bot):
    bot.add_cog(Owner(bot))
