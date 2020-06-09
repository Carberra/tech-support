from datetime import date, datetime

from discord import File
from discord.ext import commands


class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def cog_check(self, ctx):
        return commands.has_role("Staff")


def setup(bot):
    bot.add_cog(Staff(bot))
