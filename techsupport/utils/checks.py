from discord.ext import commands

from ..bot.config import Config


class WrongChannel(commands.CheckFailure):
    pass


def in_channel(_id):
    def predicate(ctx):
        if ctx.channel.id != _id:
            raise WrongChannel

        return True

    return commands.check(predicate)
