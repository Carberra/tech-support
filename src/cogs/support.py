from enum import Enum, auto, unique
from hashlib import sha256
from time import time

import discord
from discord import PermissionOverwrite as PermOW
from discord.ext import commands


class Ticket:
    def __init__(self, id=None, author_id=None, message_id=None):
        self.id = id
        self.author_id = author_id
        self.agent_id = None
        self.message_id = message_id
        self.channel_id = None
        self.state = TicketState.UNASSIGNED

    def __str__(self):
        # author.id should really be author.name, but get it
        return f"{self.author_id}-ticket-{self.id[:7]}"


class TicketState(Enum):
    UNASSIGNED = auto()
    ASSIGNED = auto()
    SOLVED = auto()


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = []

    async def make_id(self, id):
        hash = sha256()
        hash.update(bytes(f"{id}{time()}", encoding='utf-8'))
        return hash.hexdigest()

    async def get_ticket(self, message_id):
        return next((ticket for ticket in self.tickets if ticket.message_id == message_id), None)

    @commands.command()
    async def support(self, ctx, *, description):
        id = await self.make_id(ctx.author.id)

        ticket = Ticket(id=id, author_id=ctx.author.id, message_id=ctx.message.id)

        self.tickets.append(ticket)

        await ctx.send(f"Created ticket #{str(ticket)}")

    @commands.command()
    async def resolve(self, ctx, state):
        await ctx.send(f"Ticket resolved with state: {state}")

    @commands.command()
    async def tickets(self, ctx):
        await ctx.send(self.tickets)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):

        ticket = await self.get_ticket(payload.message_id)


        if str(payload.emoji) == "✅":
            ow = PermOW(read_messages=True, send_messages=True, embed_links=True, attach_files=True)
            channel = await (guild := self.bot.get_guild(695021594430668882)).create_text_channel(
                str(ticket), overwrites={
                    guild.get_role(626614466376630282): ow,
                    guild.get_member(ticket.author_id): ow,
                    guild.get_member(payload.member_id): ow
            })

        elif str(payload.emoji) == "❎":
            pass

def setup(bot):
    bot.add_cog(Support(bot))
