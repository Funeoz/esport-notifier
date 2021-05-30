import os
import sys
import inspect
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

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from dota2 import dota2_ranking


class Dota2(commands.Cog):
    def __init__(self, client):
        self.client = client
        try:
            with open("database/dota2/worldRanking.json", "r") as file:
                self.ranking = json.loads(file.read())
        except FileNotFoundError:
            dota2_ranking.get_world_ranking()
        with open("database/dota2/pastMatches.json", "r") as file:
            self.past_matches = json.loads(file.read())
        with open("database/dota2/runningMatches.json", "r") as file:
            self.running_matches = json.loads(file.read())
        with open("database/dota2/upcomingMatches.json", "r") as file:
            self.upcoming_matches = json.loads(file.read())
        with open("database/dota2/pastEvents.json", "r") as file:
            self.past_events = json.loads(file.read())
        with open("database/dota2/upcomingEvents.json", "r") as file:
            self.upcoming_events = json.loads(file.read())
        with open("database/dota2/runningEvents.json", "r") as file:
            self.running_events = json.loads(file.read())
        mongo_DB_password = os.getenv("MONGODB_PASSWORD")
        self.mongo_DB_document = MongoClient()

    @commands.group()
    async def dota2(self, ctx):
        pass

    @dota2.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Dota2 Commands Help",
            description="Every command below starts with `.en dota2`",
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
            name="`ranking`", value="Show the GosuGamers Top 30 ranking.", inline=False,
        )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        await ctx.send(embed=embed)

    @dota2.command()
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
                    title="Past Dota2 Matches",
                    thumbnail_url="https://i.imgur.com/iOhWN0s.png",
                    matches=self.past_matches,
                ).past_matches_embed(date=self.date_past_embed)
                # modify the old embed and send it
                await self.msg1.edit(embed=new_embed)
                await wait_for_reaction_pe(ctx, new_embed)

            # we create an embed that displays the matches of a past day
            embed = GameMatches(
                title="Past Dota2 Matches",
                thumbnail_url="https://i.imgur.com/iOhWN0s.png",
                matches=self.past_matches,
            ).past_matches_embed(date=self.date_past_embed)
            self.msg1 = await ctx.send(embed=embed)
            await self.msg1.add_reaction(emoji="⬅️")
            await self.msg1.add_reaction(emoji="➡️")
            await wait_for_reaction_pe(ctx, embed)

        elif arg == "running":

            date_re = datetime.date.today()

            # we create an embed that displays the matches of an upcoming day
            running_matches_embed = discord.Embed(
                title="Running Dota2 Matches",
                description=f"📅 {date_re}",
                colour=discord.Colour.dark_gold(),
            )
            running_matches_embed.set_thumbnail(url="https://i.imgur.com/iOhWN0s.png")

            if self.running_matches == []:
                running_matches_embed.add_field(
                    name="**No ongoing matches**", value="\u200b", inline=False
                )
            else:
                # go through all the running matches
                for item in self.running_matches:

                    if str(date_re) == item["date"][:10]:
                        # we create a new field if the date of the next match equals
                        # the date of the precedent one
                        # to handle "null" values for location and avoid blocking
                        # the script, we put the emoji of the united nations
                        flag1_re = (
                            f":flag_{item['team1']['location'].lower()}:"
                            if item["team1"]["location"] is not None
                            else "🇺🇳"
                        )
                        flag2_re = (
                            f":flag_{item['team2']['location'].lower()}:"
                            if item["team2"]["location"] is not None
                            else "🇺🇳"
                        )
                        stream_re = (
                            f"- [Watch]({item['stream']})"
                            if item["stream"] is not None
                            else ""
                        )
                        running_matches_embed.add_field(
                            name=f"{flag1_re} {item['team1']['name']} vs {item['team2']['name']} {flag2_re}",
                            value=f"{item['format']} - Live result : `{item['team1']['score']}-{item['team2']['score']}` - {item['event']} {stream_re}",
                            inline=False,
                        )
            running_matches_embed.add_field(
                name="** **",
                value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
                inline=False,
            )

            await ctx.send(embed=running_matches_embed)

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
                    title="Upcoming Dota2 Matches",
                    thumbnail_url="https://i.imgur.com/iOhWN0s.png",
                    matches=self.upcoming_matches,
                ).upcoming_matches_embed(
                    date=self.date_upcoming_embed, guild_timezone=guild_timezone
                )
                await self.msg2.edit(embed=new_embed)
                await wait_for_reaction_ue(ctx, new_embed)

            # we create an embed that displays the matches of an upcoming day

            embed = GameMatches(
                title="Upcoming Dota2 Matches",
                thumbnail_url="https://i.imgur.com/iOhWN0s.png",
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
            await ctx.send("⛔ Missing argument. See `.en dota2 help`.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⛔ Active cooldown ! Please try again in {error.retry_after:.2f}s"
            )

    @dota2.command()
    async def events(self, ctx, arg):

        if arg == "past":

            embed = GameEvents(
                title="Past Dota2 Events",
                thumbnail_url="https://i.imgur.com/iOhWN0s.png",
                events=self.past_events,
            ).past_events_embed()

        elif arg == "upcoming":

            embed = GameEvents(
                title="Upcoming Dota2 Events",
                thumbnail_url="https://i.imgur.com/iOhWN0s.png",
                events=self.upcoming_events,
            ).upcoming_events_embed()

        elif arg == "running":

            embed = GameEvents(
                title="Running Dota2 Events",
                thumbnail_url="https://i.imgur.com/iOhWN0s.png",
                events=self.running_events,
            ).running_events_embed()

        else:
            return ctx.command.reset_cooldown(ctx)
        await ctx.send(embed=embed)

    @events.error
    async def events_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⛔ Missing argument. See `.en dota2 help`.")

    @dota2.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ranking(self, ctx):
        # create an embed for the first 15 teams
        # (Discord limits the characters' number)
        embed = discord.Embed(
            title="GosuGamers Dota2 World Ranking",
            url="https://www.gosugamers.net/dota2/rankings",
            description="**  **",
            colour=discord.Colour.dark_gold(),
        )
        for item in self.ranking[1:16]:
            embed.add_field(
                name="\u200b",
                value=f"#{item['rank']} : **{item['name']}** - {item['rank-points']} points",
                inline=False,
            )
        embed.set_thumbnail(
            url="https://pbs.twimg.com/profile_images/654606694719164416/5VJqSQXc_400x400.jpg"
        )
        # second embed for the other 15 teams
        embed_2 = discord.Embed(title="", colour=discord.Colour.dark_gold())
        for item in self.ranking[16:]:
            embed_2.add_field(
                name="\u200b",
                value=f"#{item['rank']} : **{item['name']}** - {item['rank-points']} points",
                inline=False,
            )
        embed_2.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        # send both embeds
        await ctx.send(embed=embed)
        await ctx.send(embed=embed_2)

    @ranking.error
    async def ranking_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⛔ Active cooldown ! Please try again in {error.retry_after:.2f}s"
            )


def setup(client):
    client.add_cog(Dota2(client))
