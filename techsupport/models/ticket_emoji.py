from enum import Enum, unique


@unique
class TicketEmoji(Enum):
    ASSIGN = "<:assign:695294903676174466>"
    CLOSE = "<:close:695425197066551407>"
    OPEN = "<:open:695425196546457631>"
    REJECT = "<:reject:695294903542087710>"
    SOLVED = "<:solved:695294903646945400>"
    UNASSIGN = "<:unassign:695427251931578369>"
    UNSOLVED = "<:unsolved:695294903285973015>"

    def __str__(self):
        return self.name.title()
