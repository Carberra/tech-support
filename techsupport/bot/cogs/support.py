from discord import Colour, Embed, PartialEmoji
from discord.ext import commands

from techsupport import (
    checks,
    ActivityUtility,
    Config,
    ContextUtility,
    LanguageUtility,
    Ticket,
    TicketEmoji,
    TicketStore,
)


class Support(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.tickets = TicketStore(self.bot, self.bot.get_channel(Config.TICKET_POOL_ID))
        await self.tickets.from_serialised()

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        tickets = await self.tickets.get(author__id=member.id)

        for ticket in tickets:
            ctx = await ContextUtility.transform(self.bot, ticket, "member_remove")
            ctx.author = ticket.author
            await ctx.invoke(self.bot.get_command("resolve"), "abandoned", reason="Resolved via abandon")

    @commands.command()
    @checks.in_channel(Config.SUPPORT_CHANNEL_ID)
    async def support(self, ctx, language, *, description):
        if len(description) > 50:
            ticket = Ticket(
                guild=ctx.guild,
                author=ctx.author,
                description=description,
                language=await LanguageUtility.resolve(language),
                created_at=ctx.message.created_at,
            )
            channel = await ticket.create_channel()

            message = await self.tickets.channel.send(embed=await ticket.create_embed())
            ticket.message = message

            await self.tickets.add(ticket)
            await ticket.update_reactions()
            await self.bot.database.update(ticket)

            embed = Embed(
                type="rich",
                title=f"Ticket #{ticket}",
                description=f"Your ticket has been created.\nIdentifier: {ticket}",
                colour=Colour(ticket.colour)
            )
            embed.set_footer(text=f"Requested: {ticket.created_at.strftime('%H:%M:%S %d/%m/%Y')}")
            embed.set_author(name="Created")

            await ctx.send(ctx.author.mention, embed=embed)
            await channel.send(f"{ctx.author.mention}, I'll let you know when an agent is available to help.")
        else:
            await ctx.send("Your description needs to be at least 50 characters long.")

    @support.error
    async def support_error(self, ctx, exc):
        if isinstance(exc, checks.WrongChannel):
            await ctx.message.delete()
            await ctx.send(
                f"Wrong channel. Direct this to <#{Config.SUPPORT_CHANNEL_ID}> instead.", delete_after=30,
            )
        elif isinstance(exc, commands.MissingRequiredArgument):
            await ctx.send("You need to specify the language and provide a problem description.")

    @commands.command()
    async def resolve(self, ctx, state, *, reason=None):
        if ctx.invoked_with == "raw_reaction":
            ticket = await self.tickets.get_one(message=ctx.message)
        else:
            ticket = await self.tickets.get_one(channel=ctx.channel)

        if ctx.channel == ticket.channel:
            await getattr(ticket, state)(ctx.author, reason)

            await ticket.update_embed()
            await ticket.update_reactions()
            await self.bot.database.update(ticket)
        else:
            await ctx.send("You are not able to resolve this ticket.")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.member.bot and f"{payload.emoji}" in [e.value for e in TicketEmoji]:
            ticket = await self.tickets.get_one(message__id=payload.message_id)

            if await ticket.valid_agent(payload.member):
                ctx = await ContextUtility.transform(self.bot, ticket, "raw_reaction")
                ctx.author = payload.member
                await ctx.invoke(self.bot.get_command("resolve"), payload.emoji.name, reason="Resolved via reaction")
            else:
                await ticket.message.remove_reaction(payload.emoji, payload.member)


def setup(bot):
    bot.add_cog(Support(bot))
