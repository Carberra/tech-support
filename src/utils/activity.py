from discord import Activity, ActivityType


async def update(bot):
    support = bot.get_cog("Support")

    await bot.change_presence(activity=Activity(
        # that right? I want the number of open tickets here
        name=f"{len(support.tickets)} active tickets",
        type=ActivityType.playing
    ))
