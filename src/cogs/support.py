from enum import Enum, auto, unique
from hashlib import sha256
from operator import attrgetter
from time import time

import discord
from discord.ext import commands

from src.utils import activity


class Ticket:
    def __init__(self, id=None, author=None, message_id=None):
        self.id = id
        self.author = author
        self.agent = None
        self.message_id = message_id
        self.channel_id = None
        self.state = TicketState.UNASSIGNED

    async def is_active(self):
        return self.state != TicketState.SOLVED

    async def solved(self, bot):
        self.state = TicketState.SOLVED
        await self.author.guild.get_channel(self.channel_id).delete()
        await activity.update(bot)

    async def unsolved(self, bot):
        # edit channel permissions

        self.state = TicketState.UNSOLVED
        self.agent = None

    async def assign(self, agent):
        ow = discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            embed_links=True,
            attach_files=True
        )

        channel = await (guild := agent.guild).create_text_channel(
            str(self),
            overwrites={
                guild.get_role(695021769521627266): ow,
                guild.get_role(695059530752720996): ow,
                self.author: ow,
                agent: ow
            },
            category=guild.get_channel(695091841401356358)
        )

        self.agent = agent
        self.state = TicketState.ASSIGNED
        self.channel_id = channel.id

    async def unassign(self):
        self.state = TicketState.UNASSIGNED
        self.agent = None

    def __str__(self):
        return f"{self.author.name}-{self.id[:7]}"

    def __repr__(self):
        return f"[TICKET] id={self.id}, author={self.author}, agent={self.agent}, message_id={self.message_id}, channel_id={self.channel_id}, state={self.state}"

@unique
class TicketState(Enum):
    UNASSIGNED = auto()
    ASSIGNED = auto()
    UNSOLVED = auto()
    SOLVED = auto()


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = []

    async def make_id(self, id):
        hash = sha256()
        hash.update(bytes(f"{id}{time()}", encoding='utf-8'))
        return hash.hexdigest()

    async def get_ticket(self, **kwargs):
        if len(kwargs) == 1:
            k, v = kwargs.popitem()
            pred = attrgetter(k.replace('__', '.'))
            for ticket in self.tickets:
                if pred(ticket) == v:
                    return ticket

        return None

    @commands.command()
    async def support(self, ctx, *, description):
        id = await self.make_id(ctx.author.id)

        ticket = Ticket(id=id, author=ctx.author, message_id=ctx.message.id)

        self.tickets.append(ticket)
        await activity.update(self.bot)

        await ctx.send(f"Created ticket #{str(ticket)}")

    @commands.command()
    async def resolve(self, ctx, state: str):
        state = state.upper()
        if state not in ['SOLVED', 'UNSOLVED']:
            # invalid resolution
            pass

        ticket = await self.get_ticket(channel_id=ctx.channel.id)
        await getattr(ticket, state.lower())(self.bot)

    @commands.command()
    async def tickets(self, ctx):
        await ctx.send(self.tickets)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        ticket = await self.get_ticket(message_id=payload.message_id)

        if str(payload.emoji) == "✅":
            await ticket.assign(payload.member.guild.get_member(payload.user_id))

        elif str(payload.emoji) == "❎":
            pass


def setup(bot):
    bot.add_cog(Support(bot))
