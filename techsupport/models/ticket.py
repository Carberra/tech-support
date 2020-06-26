from datetime import datetime, timezone
from hashlib import sha256

from discord import Colour, Embed

from .ticket_emoji import TicketEmoji
from .ticket_state import TicketState
from ..bot import Config
from ..utils import OverwritesUtility


class Ticket:
    @property
    def active(self):
        return self.state != TicketState.SOLVED

    @property
    def colour(self):
        return self.state.value["colour"]

    @property
    def lead_agent(self):
        try:
            return self.agents[0]
        except IndexError:
            return

    def __init__(self, **kwargs):
        self.guild = kwargs.get("guild", None)
        self.author = kwargs.get("author", None)
        self.agents = kwargs.get("agents", [])
        self.language = kwargs.get("language", None)
        self.description = kwargs.get("description", None)
        self.message = kwargs.get("message", None)
        self.channel = kwargs.get("channel", None)
        self.state = kwargs.get("state", TicketState.UNASSIGNED)
        self.created_at = kwargs.get("created_at", None)
        self.id = kwargs.get("id", self._id(self.author.id, self.created_at))

    def serialise(self):
        return {
            "id": self.id,
            "guild_id": getattr(self.guild, "id", None),
            "author_id": self.author.id,
            "agents": "\n".join([f"{a.id}" for a in self.agents]),
            "language": self.language,
            "description": self.description,
            "message_id": getattr(self.message, "id", None),
            "channel_id": getattr(self.channel, "id", None),
            "created_at": self.created_at,
            "state_name": self.state.name,
        }

    @classmethod
    async def deserialise(cls, bot, serialised_ticket):
        return cls(
            id=serialised_ticket[0],
            guild=(guild := bot.get_guild(serialised_ticket[1])),
            author=guild.get_member(serialised_ticket[2]),
            agents=[guild.get_member(int(id)) for id in serialised_ticket[3].splitlines()],
            language=serialised_ticket[4],
            description=serialised_ticket[5],
            message=await bot.get_channel(Config.TICKET_POOL_ID).fetch_message(serialised_ticket[6]),
            channel=bot.get_channel(serialised_ticket[7]),
            created_at=datetime.fromisoformat(serialised_ticket[8]),
            state=TicketState[serialised_ticket[9]],
        )

    @staticmethod
    def _id(author_id, created_at):
        hash = sha256()
        hash.update(bytes(f"{author_id}{created_at}", encoding="utf-8"))
        return hash.hexdigest()

    async def valid_agent(self, member):
        return not len(self.agents) or member in self.agents or self.state is TicketState.OPEN

    async def create_channel(self):
        channel = await self.guild.create_text_channel(
            f"{self}",
            overwrites={
                self.guild.me: OverwritesUtility._access,
                self.guild.default_role: OverwritesUtility._no_access,
                self.guild.get_role(Config.STAFF_ROLE_ID): OverwritesUtility._access,
                self.author: OverwritesUtility._access,
            },
            category=self.guild.get_channel(Config.TICKET_CATEGORY_ID),
        )
        self.channel = channel

        return channel

    async def create_embed(self):
        embed = Embed(title=f"Ticket #{self}", type="rich", colour=Colour(self.colour))

        embed.set_footer(
            text=f"Requested: {self.created_at.strftime('%H:%M:%S %d/%m/%Y')} • Updated: {datetime.now(timezone.utc).strftime('%H:%M:%S %d/%m/%Y')}"
        )
        embed.set_author(name=self.state)

        embed.add_field(name="Client", value=self.author.mention)
        embed.add_field(name="Agent", value=(self.lead_agent.mention if self.lead_agent else None))
        embed.add_field(name="Language", value=self.language)
        embed.add_field(name="Problem Description", value=self.description, inline=False)

        if getattr(self, "reason", None):
            embed.add_field(name="Termination Reason", value=self.reason, inline=False)

        return embed

    async def update_embed(self):
        await self.message.edit(embed=await self.create_embed())

    async def update_reactions(self):
        await self.message.clear_reactions()

        for emoji in self.state.value.get("emoji", ()):
            await self.message.add_reaction(emoji.value)

    async def solved(self, *args):
        self.state = TicketState.SOLVED
        await self.channel.delete(reason="Ticket solved")
        self.channel = None

    async def unsolved(self, *args):
        try:
            agent = args[0]
            await OverwritesUtility.remove(agent, channel=self.channel)
        except:
            pass

        self.state = TicketState.UNSOLVED

        embed = Embed(
            type="rich",
            title=f"Ticket #{self}",
            description=f"This ticket has been marked as unsolved.\nThe assigned agent{'s' if len(self.agents) > 1 else ''} ha{'ve' if len(self.agents) > 1 else 's'} been removed.",
            colour=Colour(self.colour)
        )
        embed.set_author(name=self.state)

        self.agents = []

        await self.channel.send(self.author.mention, embed=embed)

    async def assign(self, *args):
        agent = args[0]

        self.agents.append(agent)
        await OverwritesUtility.add(channel=self.channel, overwrites={agent: OverwritesUtility._access})

        if self.state != TicketState.OPEN:
            self.state = TicketState.ASSIGNED

            await self.channel.send(f"{self.author.mention}, {agent.mention} is now available to help.")

    async def unassign(self, *args):
        agent = args[0]

        self.agents.remove(agent)
        await OverwritesUtility.remove(agent, channel=self.channel)

        if not len(self.agents):
            await self.unsolved()

    async def reject(self, *args):
        self.state = TicketState.REJECTED
        await self.channel.delete(reason="Ticket rejected")
        self.channel = None

        embed = Embed(
            type="rich",
            title=f"Ticket #{self}",
            description="Your ticket has been rejected.\nPlease provide a better description of your problem.",
            colour=Colour(self.colour)
        )
        embed.set_author(name=self.state)

        await self.guild.get_channel(Config.SUPPORT_CHANNEL_ID).send(self.author.mention, embed=embed)

    async def open(self, *args):
        self.state = TicketState.OPEN

    async def close(self, *args):
        self.agents = self.agents[:1]
        self.state = TicketState.ASSIGNED

    async def abandoned(self, *args):
        self.state = TicketState.ABANDONED
        await self.channel.delete(reason="Ticket abandoned")
        self.channel = None

    async def terminate(self, *args):
        agent = args[0]
        reason = args[1]

        if "Staff" in [x.name for x in agent.roles]:
            self.state = TicketState.TERMINATED
            self.reason = reason
            await self.channel.delete(reason="Ticket terminated")
            self.channel = None

            embed = Embed(
                type="rich",
                title=f"Ticket #{self}",
                description=f"Your ticket has been terminated.\nReason: {reason}",
                colour=Colour(self.colour)
            )
            embed.set_author(name=self.state)
            await self.guild.get_channel(Config.SUPPORT_CHANNEL_ID).send(self.author.mention, embed=embed)

    def __str__(self):
        return f"{self.author.name.lower()}-{self.id[:7]}"

    def __repr__(self):
        return f"<Ticket({self.__dict__})>"
