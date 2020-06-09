from discord import Activity, ActivityType, Status


class ActivityUtility:
    @staticmethod
    async def online(bot):
        await bot.change_presence(status=Status.online)

    @staticmethod
    async def offline(bot):
        await bot.change_presence(status=Status.offline)

    @staticmethod
    async def idle(bot):
        await bot.change_presence(status=Status.idle)

    @staticmethod
    async def dnd(bot):
        await bot.change_presence(status=Status.dnd)

    @staticmethod
    async def invisible(bot):
        await bot.change_presence(status=Status.invisible)

    @staticmethod
    async def update(bot):
        await bot.change_presence(activity=Activity(name=f"*support", type=ActivityType.watching,))
