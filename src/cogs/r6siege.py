import os
import json
import asyncio
import datetime
import dateutil.parser
import pymongo
from pymongo import MongoClient
import discord
import pytz
from discord.ext import tasks, commands
from .templates.events import GameEvents
from .templates.matches import GameMatches


class R6siege(commands.Cog):
    def __init__(self, client):
        self.client = client
        with open("database/r6siege/pastMatches.json", "r") as file:
            self.past_matches = json.loads(file.read())
        with open("database/r6siege/runningMatches.json", "r") as file:
            self.running_matches = json.loads(file.read())
        with open("database/r6siege/upcomingMatches.json", "r") as file:
            self.upcoming_matches = json.loads(file.read())
        with open("database/r6siege/pastEvents.json", "r") as file:
            self.past_events = json.loads(file.read())
        with open("database/r6siege/upcomingEvents.json", "r") as file:
            self.upcoming_events = json.loads(file.read())
        with open("database/r6siege/runningEvents.json", "r") as file:
            self.running_events = json.loads(file.read())
        mongo_DB_password = os.getenv("MONGODB_PASSWORD")
        self.mongo_DB_document = MongoClient()

    @commands.group()
    async def r6siege(self, ctx):
        pass

    @r6siege.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="R6Siege Commands Help",
            description="Every command below starts with `.en r6siege`",
            colour=discord.Colour.dark_gold(),
        )
        embed.add_field(
            name="`matches past`",
            value="Show the results of the matches of the past week.",
            inline=True,
        )
        embed.add_field(
            name="`matches running`",
            value="Show the ongoing matches and the score.",
            inline=True,
        )
        embed.add_field(
            name="`matches upcoming`",
            value="Show the matches for the next two days.",
            inline=True,
        )
        embed.add_field(
            name="`events past`",
            value="Show the past events and their respective winner.",
            inline=True,
        )
        embed.add_field(
            name="`events running`", value="Show the ongoing events.", inline=True,
        )
        embed.add_field(
            name="`events upcoming`", value="Show the upcoming events.", inline=True,
        )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        await ctx.send(embed=embed)

    @r6siege.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def matches(self, ctx, arg):

        if arg == "past":

            self.date_past_embed = datetime.date.today()

            async def wait_for_reaction_pe(ctx, embed):
                def check(reaction, user):
                    if user == ctx.author and str(reaction.emoji) in ("➡️", "⬅️"):
                        return reaction.emoji, user

                try:
                    reaction, user = await self.client.wait_for(
                        "reaction_add", timeout=25.0, check=check
                    )
                    if str(reaction.emoji) == "⬅️":
                        # we limit the embed to access only the past week
                        if self.date_past_embed == datetime.date.today() - datetime.timedelta(
                            days=7
                        ):
                            await self.msg1.clear_reaction("⬅️")
                            await edit_past_embed()
                        else:
                            await self.msg1.add_reaction("➡️")
                            await self.msg1.remove_reaction("⬅️", user)
                            self.date_past_embed = (
                                self.date_past_embed - datetime.timedelta(days=1)
                            )
                            await edit_past_embed()
                    elif str(reaction.emoji) == "➡️":
                        if self.date_past_embed == datetime.date.today():
                            await self.msg1.clear_reaction("➡️")
                            await edit_past_embed()
                        else:
                            await self.msg1.add_reaction("⬅️")
                            await self.msg1.remove_reaction("➡️", user)
                            self.date_past_embed = (
                                self.date_past_embed + datetime.timedelta(days=1)
                            )
                            await edit_past_embed()

                except asyncio.TimeoutError:
                    await self.msg1.clear_reactions()

            async def edit_past_embed():
                # we create a new embed to replace the old one
                new_embed = GameMatches(
                    title="Past R6Siege Matches",
                    thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                    matches=self.past_matches,
                ).past_matches_embed(date=self.date_past_embed)
                # modify the old embed and send it
                await self.msg1.edit(embed=new_embed)
                await wait_for_reaction_pe(ctx, new_embed)

            # we create an embed that displays the matches of a past day
            embed = GameMatches(
                title="Past R6Siege Matches",
                thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                matches=self.past_matches,
            ).past_matches_embed(date=self.date_past_embed)
            self.msg1 = await ctx.send(embed=embed)
            await self.msg1.add_reaction(emoji="⬅️")
            await self.msg1.add_reaction(emoji="➡️")
            await wait_for_reaction_pe(ctx, embed)

        elif arg == "running":

            embed = GameMatches(
                title="Running R6Siege Matches",
                thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                matches=self.running_matches,
            ).running_matches_embed()

            await ctx.send(embed=embed)

        elif arg == "upcoming":

            self.date_upcoming_embed = datetime.date.today()
            guild_timezone = self.mongo_DB_document.find_one({"server": ctx.guild.id})[
                "timezone"
            ]

            async def wait_for_reaction_ue(ctx, embed):
                def check(reaction, user):
                    if user == ctx.author and str(reaction.emoji) in ("➡️", "⬅️"):
                        return reaction.emoji, user

                try:
                    reaction, user = await self.client.wait_for(
                        "reaction_add", timeout=25.0, check=check
                    )
                    if str(reaction.emoji) == "⬅️":
                        if self.date_upcoming_embed == datetime.date.today():
                            await self.msg2.clear_reaction("⬅️")
                            await edit_upcoming_embed()
                        else:
                            await self.msg2.add_reaction("➡️")
                            await self.msg2.remove_reaction("⬅️", user)
                            self.date_upcoming_embed = (
                                self.date_upcoming_embed - datetime.timedelta(days=1)
                            )
                            await edit_upcoming_embed()
                    elif str(reaction.emoji) == "➡️":
                        if self.date_upcoming_embed == datetime.date.today() + datetime.timedelta(
                            days=2
                        ):
                            await self.msg2.clear_reaction("➡️")
                            await edit_upcoming_embed()
                        else:
                            await self.msg2.add_reaction("⬅️")
                            await self.msg2.remove_reaction("➡️", user)
                            self.date_upcoming_embed = (
                                self.date_upcoming_embed + datetime.timedelta(days=1)
                            )
                            await edit_upcoming_embed()

                except asyncio.TimeoutError:
                    await self.msg2.clear_reactions()

            async def edit_upcoming_embed():
                # we create a new embed to replace the old one
                new_embed = GameMatches(
                    title="Upcoming R6Siege Matches",
                    thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                    matches=self.upcoming_matches,
                ).upcoming_matches_embed(
                    date=self.date_upcoming_embed, guild_timezone=guild_timezone
                )
                await self.msg2.edit(embed=new_embed)
                await wait_for_reaction_ue(ctx, new_embed)

            # we create an embed that displays the matches of an upcoming day

            embed = GameMatches(
                title="Upcoming R6Siege Matches",
                thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                matches=self.upcoming_matches,
            ).upcoming_matches_embed(
                date=self.date_upcoming_embed, guild_timezone=guild_timezone
            )
            self.msg2 = await ctx.send(embed=embed)
            await self.msg2.add_reaction(emoji="⬅️")
            await self.msg2.add_reaction(emoji="➡️")
            await wait_for_reaction_ue(ctx, embed)

        else:
            ctx.command.reset_cooldown(ctx)

    @matches.error
    async def matches_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⛔ Missing argument. See `.en r6siege help`.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⛔ Active cooldown ! Please try again in {error.retry_after:.2f}s"
            )

    @r6siege.command()
    async def events(self, ctx, arg):
        if arg == "past":

            embed = GameEvents(
                title="Past R6Siege Events",
                thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                events=self.past_events,
            ).past_events_embed()

        elif arg == "upcoming":

            embed = GameEvents(
                title="Upcoming R6Siege Events",
                thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                events=self.upcoming_events,
            ).upcoming_events_embed()

        elif arg == "running":

            embed = GameEvents(
                title="Running R6Siege Events",
                thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                events=self.running_events,
            ).running_events_embed()

        else:
            return ctx.command.reset_cooldown(ctx)
        await ctx.send(embed=embed)

    @events.error
    async def events_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⛔ Missing argument. See `.en r6siege help`.")


def setup(client):
    client.add_cog(R6siege(client))
