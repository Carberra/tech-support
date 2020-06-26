from discord.ext import commands


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return commands.has_role("Staff")

    @commands.command()
    async def terminate(self, ctx, reason):
        ctx.command = self.bot.get_command("resolve")
        await ctx.invoke(ctx.command, "terminate", reason=reason)


def setup(bot):
    bot.add_cog(Staff(bot))
