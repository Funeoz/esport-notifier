import os
import json
import asyncio
import datetime
import pymongo
from pymongo import MongoClient
import discord
import dateutil.parser
import pytz
from discord.ext import tasks, commands
from .templates.events import GameEvents
from .templates.matches import GameMatches


class Csgo(commands.Cog):
    def __init__(self, client):
        self.client = client
        with open("database/csgo/worldRanking.json", "r") as file:
            self.ranking = json.loads(file.read())
        with open("database/csgo/pastMatches.json", "r") as file:
            self.past_matches = json.loads(file.read())
        with open("database/csgo/runningMatches.json", "r") as file:
            self.running_matches = json.loads(file.read())
        with open("database/csgo/upcomingMatches.json", "r") as file:
            self.upcoming_matches = json.loads(file.read())
        with open("database/csgo/pastEvents.json", "r") as file:
            self.past_events = json.loads(file.read())
        with open("database/csgo/upcomingEvents.json", "r") as file:
            self.upcoming_events = json.loads(file.read())
        with open("database/csgo/runningEvents.json", "r") as file:
            self.running_events = json.loads(file.read())
        mongo_DB_password = os.getenv("MONGODB_PASSWORD")
        self.mongo_DB_document = MongoClient()

    @commands.group()
    async def csgo(self, ctx):
        pass

    @csgo.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="CS:GO Commands Help",
            description="Every command below starts with `.en csgo`",
            colour=discord.Colour.dark_gold(),
        )
        embed.add_field(
            name="`live [parameter]`",
            value="Choose if you want the live feed for CS:GO matches. Replace [parameter] with `enable` or `disable`.",
            inline=False,
        )
        embed.add_field(
            name="`live_channel [channel_ID]`",
            value="Set up the channel for the live feed for CS:GO matches. [channel_ID] is the 18 digits number obtainable with Developer Mode: see the [documentation](https://esport-notifier.github.io/docs/commands/csgo/). Required to make it working.",
            inline=False,
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
            name="`events running`", value="Show the ongoing events.", inline=True
        )
        embed.add_field(
            name="`events upcoming`", value="Show the upcoming events.", inline=True
        )
        embed.add_field(
            name="`ranking`", value="Show the HLTV Top 30 ranking.", inline=False
        )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        await ctx.send(embed=embed)

    @csgo.command()
    @commands.has_permissions(administrator=True)
    async def live(self, ctx, arg):
        guild_data = self.mongo_DB_document.find_one({"server": ctx.guild.id})
        if arg == "enable":
            if guild_data["channel"] is None:
                await ctx.send(
                    "Please set up the channel with `.en csgo live_channel [channel ID]` before enabling it."
                )
            else:
                if guild_data["csgo_live"] is True:
                    await ctx.send("Live feed is already enabled !")
                else:
                    self.mongo_DB_document.update_one(
                        {"server": ctx.guild.id}, {"$set": {"csgo_live": True}}
                    )
                    await ctx.send("✅ Live feed enabled !")
        elif arg == "disable":
            if guild_data["csgo_live"] is False:
                await ctx.send("Live feed is already disabled !")
            else:
                self.mongo_DB_document.update_one(
                    {"server": ctx.guild.id}, {"$set": {"csgo_live": False}}
                )
                await ctx.send("✅ Live feed disabled !")

    @live.error
    async def live_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ You don't have the permissions to execute that command.")

    @csgo.command()
    async def live_channel(self, ctx, arg):
        if any(c.isalpha() for c in arg):
            await ctx.send("Wrong channel format ! Please send the ID.")
        else:
            self.mongo_DB_document.update_one(
                {"server": ctx.guild.id}, {"$set": {"channel": int(arg)}}
            )
            await ctx.send(f"✅ Live feed channel for CS:GO set to `{arg}` !")

    @live_channel.error
    async def live_channel_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ You don't have the permissions to execute that command.")

    @csgo.command()
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
                    title="Past CS:GO Matches",
                    thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                    matches=self.past_matches,
                ).past_matches_embed(date=self.date_past_embed)
                # modify the old embed and send it
                await self.msg1.edit(embed=new_embed)
                await wait_for_reaction_pe(ctx, new_embed)

            # we create an embed that displays the matches of a past day
            embed = GameMatches(
                title="Past CS:GO Matches",
                thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                matches=self.past_matches,
            ).past_matches_embed(date=self.date_past_embed)
            self.msg1 = await ctx.send(embed=embed)
            await self.msg1.add_reaction(emoji="⬅️")
            await self.msg1.add_reaction(emoji="➡️")
            await wait_for_reaction_pe(ctx, embed)

        elif arg == "running":

            embed = GameMatches(
                title="Running CS:GO Matches",
                thumbnail_url="https://i.imgur.com/k4WFkk6.png",
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
                    title="Upcoming CS:GO Matches",
                    thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                    matches=self.upcoming_matches,
                ).upcoming_matches_embed(
                    date=self.date_upcoming_embed, guild_timezone=guild_timezone
                )
                await self.msg2.edit(embed=new_embed)
                await wait_for_reaction_ue(ctx, new_embed)

            # we create an embed that displays the matches of an upcoming day

            embed = GameMatches(
                title="Upcoming CS:GO Matches",
                thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                matches=self.upcoming_matches,
            ).upcoming_matches_embed(
                date=self.date_upcoming_embed, guild_timezone=guild_timezone
            )
            self.msg2 = await ctx.send(embed=embed)
            await self.msg2.add_reaction(emoji="⬅️")
            await self.msg2.add_reaction(emoji="➡️")
            await wait_for_reaction_ue(ctx, embed)

        else:
            return ctx.command.reset_cooldown(ctx)

    @matches.error
    async def matches_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⛔ Missing argument. See `.en csgo help`.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⛔ Active cooldown ! Please try again in {error.retry_after:.2f}s"
            )

    @csgo.command()
    async def events(self, ctx, arg):
        if arg == "past":

            embed = GameEvents(
                title="Past CS:GO Events",
                thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                events=self.past_events,
            ).past_events_embed()

        elif arg == "upcoming":

            embed = GameEvents(
                title="Upcoming CS:GO Events",
                thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                events=self.upcoming_events,
            ).upcoming_events_embed()

        elif arg == "running":

            embed = GameEvents(
                title="Running CS:GO Events",
                thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                events=self.running_events,
            ).running_events_embed()

        else:
            return ctx.command.reset_cooldown(ctx)
        await ctx.send(embed=embed)

    @events.error
    async def events_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⛔ Missing argument. See `.en csgo help`.")

    @csgo.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ranking(self, ctx):
        # create an embed for the first 15 teams
        # (Discord limits the characters' number)
        embed = discord.Embed(
            title="HLTV CS:GO World Ranking",
            url="https://www.hltv.org/ranking/teams/",
            description=self.ranking[1]["date"],
            colour=discord.Colour.dark_gold(),
        )
        for item in self.ranking[2:17]:
            embed.add_field(
                name="\u200b",
                value=f"#{item['rank']} : **{item['name']}** - {item['rank-points']} points",
                inline=False,
            )
        embed.set_thumbnail(
            url="https://pbs.twimg.com/profile_images/766575292441845760/ySDr_slD_400x400.jpg"
        )
        # second embed for the other 15 teams
        embed_2 = discord.Embed(title="", colour=discord.Colour.dark_gold())
        for item in self.ranking[17:]:
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
    client.add_cog(Csgo(client))
