from discord.ext import commands


class Helper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return commands.has_any_role("Staff", "Helper")

    @commands.command(aliases=["solve"])
    async def solved(self, ctx):
        ctx.command = self.bot.get_command("resolve")
        await ctx.invoke(ctx.command, "solved")

    @commands.command(aliases=["unsolve"])
    async def unsolved(self, ctx):
        ctx.command = self.bot.get_command("resolve")
        await ctx.invoke(ctx.command, "unsolved")

    @commands.command(aliases=["unassigned"])
    async def unassign(self, ctx):
        ctx.command = self.bot.get_command("resolve")
        await ctx.invoke(ctx.command, "unassign")

    @commands.command(aliases=["opened"])
    async def open(self, ctx):
        ctx.command = self.bot.get_command("resolve")
        await ctx.invoke(ctx.command, "open")

    @commands.command(aliases=["closed"])
    async def close(self, ctx):
        ctx.command = self.bot.get_command("resolve")
        await ctx.invoke(ctx.command, "close")


def setup(bot):
    bot.add_cog(Helper(bot))
