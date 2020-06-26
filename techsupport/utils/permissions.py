from sys import exc_info, stderr

from discord import PermissionOverwrite


class OverwritesUtility:
    _access = PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True, attach_files=True)
    _no_access = PermissionOverwrite(read_messages=False)

    @staticmethod
    async def get(channel=None):
        try:
            return channel.overwrites
        except:
            return {}

    @staticmethod
    async def set(channel=None, **kwargs):
        try:
            await channel.edit(overwrites=kwargs.get("overwrites", await OverwritesUtility.get(channel=channel)))
        except:
            print(exc_info(), file=stderr)

    @staticmethod
    async def add(channel=None, **kwargs):
        ows = await OverwritesUtility.get(channel=channel)

        ows.update(kwargs.get("overwrites", {}))

        await OverwritesUtility.set(channel=channel, overwrites=ows)

    @staticmethod
    async def remove(*targets, channel=None):
        ows = await OverwritesUtility.get(channel=channel)

        for target in targets:
            ows.pop(target, None)

        await OverwritesUtility.set(channel=channel, overwrites=ows)
