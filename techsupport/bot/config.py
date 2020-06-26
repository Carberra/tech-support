from typing import Final
from os import getenv

from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()


class Config:
    with open(str(getenv("TOKEN"))) as f:
        TOKEN: Final = f.read()

    OWNER_IDS: Final[set] = set([385807530913169426, 102733198231863296])
    PREFIX: Final = "*"
    IGNORE_EXCEPTIONS: Final = (
        commands.CommandNotFound,
        commands.CheckFailure,
        commands.MissingRequiredArgument
    )

    GUILD_ID: Final = int(getenv("GUILD_ID", ""))
    SUPPORT_CHANNEL_ID: Final = int(getenv("SUPPORT_CHANNEL_ID", ""))
    TICKET_CATEGORY_ID: Final = int(getenv("TICKET_CATEGORY_ID", ""))
    TICKET_POOL_ID: Final = int(getenv("TICKET_POOL_ID", ""))
    STAFF_ROLE_ID: Final = int(getenv("STAFF_ROLE_ID", ""))
    HELPER_ROLE_ID: Final = int(getenv("HELPER_ROLE_ID", ""))
