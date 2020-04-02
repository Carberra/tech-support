from discord import Activity, ActivityType

from src.cogs.support import TicketState


async def async_filter(pred, iterable):
    for item in iterable:
        r = await pred(item)
        if r:
            yield item

async def update(bot):
    support = bot.get_cog("Support")

    await bot.change_presence(activity=Activity(
        name=f"{len([t async for t in async_filter(lambda x: x.is_active(), support.tickets)])} tickets",
        type=ActivityType.watching
    ))
