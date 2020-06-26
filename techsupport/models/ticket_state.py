from enum import Enum

from .ticket_emoji import TicketEmoji


class TicketState(Enum):
    UNASSIGNED = {
        "colour": 0x757575,
        "emoji": (TicketEmoji.ASSIGN, TicketEmoji.REJECT,),
    }
    ASSIGNED = {
        "colour": 0x2979FF,
        "emoji": (TicketEmoji.SOLVED, TicketEmoji.UNSOLVED, TicketEmoji.OPEN,),
    }
    OPEN = {
        "colour": 0x4A148C,
        "emoji": (TicketEmoji.ASSIGN, TicketEmoji.UNASSIGN, TicketEmoji.SOLVED, TicketEmoji.CLOSE,),
    }
    UNSOLVED = {"colour": 0xFFAB00, "emoji": (TicketEmoji.ASSIGN,)}
    SOLVED = {"colour": 0x64DD17}
    REJECTED = {"colour": 0xD50000}
    ABANDONED = {"colour": 0xFFFFFF}
    TERMINATED = {"colour": 0x000000}

    def __str__(self):
        return self.name.title()
