from operator import attrgetter

from .ticket import Ticket


class TicketStore:
    def __init__(self, bot, channel):
        self.bot = bot
        self.channel = channel
        self._tickets = []

    async def get(self, **attrs):
        c = [(attrgetter(attr.replace("__", ".")), value) for attr, value in attrs.items()]

        tickets = []

        for ticket in self._tickets:
            if all(pred(ticket) == value for pred, value in c):
                tickets.append(ticket)

        return tickets or None

    async def get_one(self, **attrs):
        if (r := await self.get(**attrs)) :
            return r[0]

    async def add(self, ticket):
        self._tickets.append(ticket)

    async def remove(self, ticket):
        self._tickets.remove(ticket)

    async def from_serialised(self):
        for ticket in await self.bot.database.get_all():
            await self.add(await Ticket.deserialise(self.bot, ticket))

    def as_serialised(self):
        for ticket in self._tickets:
            yield ticket.serialise()
