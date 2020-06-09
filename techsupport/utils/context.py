from discord.ext.commands import Context


class ContextUtility:
    @staticmethod
    async def transform(bot, ticket, invoked_with):
        ctx = await bot.get_context(ticket.message, cls=Context)
        ctx.channel = ticket.channel
        ctx.invoked_with = invoked_with
        return ctx
