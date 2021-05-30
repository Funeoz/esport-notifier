import json
import asyncio
import datetime
import discord
from pymongo import MongoClient
import pymongo
import os
from discord.ext import tasks, commands


class Notifications(commands.Cog):
    def __init__(self, client):
        self.client = client
        mongo_DB_password = os.getenv("MONGODB_PASSWORD")
        self.mongo_DB_document = MongoClient()
        with open("database/csgo/upcomingMatches.json") as file:
            self.csgo_matches = json.loads(file.read())
        with open("database/dota2/upcomingMatches.json") as file:
            self.dota2_matches = json.loads(file.read())
        with open("database/r6siege/upcomingMatches.json") as file:
            self.r6siege_matches = json.loads(file.read())
        with open("database/lol/upcomingMatches.json") as file:
            self.lol_matches = json.loads(file.read())

    @commands.group()
    async def notifications(self, ctx):
        pass

    @notifications.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Notifications Commands Help",
            description="Every command below starts with `.en notifications`",
            colour=discord.Colour.dark_gold(),
        )
        embed.add_field(
            name="`channel [channel_ID]`",
            value="Set up the channel for notifications. [channel_ID] is the 18 digits number obtainable with Developer Mode: see the [documentation](https://esport-notifier.github.io/docs/commands/csgo/). Required to make it working.",
            inline=False,
        )
        embed.add_field(
            name="`csgo [parameter]`",
            value="Enable or disable notifications for CSGO. Replace [parameter] with `enable` or `disable`.",
            inline=False,
        )
        embed.add_field(
            name="`lol [parameter]`",
            value="Enable or disable notifications for LOL. Replace [parameter] with `enable` or `disable`.",
            inline=False,
        )
        embed.add_field(
            name="`dota2 [parameter]`",
            value="Enable or disable notifications for Dota2. Replace [parameter] with `enable` or `disable`.",
            inline=False,
        )
        embed.add_field(
            name="`r6siege [parameter]`",
            value="Enable or disable notifications for R6Siege. Replace [parameter] with `enable` or `disable`.",
            inline=False,
        )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        await ctx.send(embed=embed)

    @notifications.command()
    @commands.has_permissions(administrator=True)
    async def channel(self, ctx, arg):
        if arg.isdigit() and len(arg) == 18:
            self.mongo_DB_document.update_one(
                {"server": ctx.guild.id}, {"$set": {"notifications.channel": int(arg)}}
            )
            await ctx.send(f"✅ Notifications channel set to `{arg}` !")

    @notifications.command()
    @commands.has_permissions(administrator=True)
    async def csgo(self, ctx, arg):
        guild_data = self.mongo_DB_document.find_one({"server": ctx.guild.id})
        if arg == "enable":
            if guild_data["notifications"]["channel"] is None:
                await ctx.send(
                    "Please set up the channel with `.en notifications channel [channel ID]` before enabling it."
                )
            else:
                if guild_data["notifications"]["csgo"] is True:
                    await ctx.send("Notifications for CSGO are already enabled !")
                else:
                    self.mongo_DB_document.update_one(
                        {"server": ctx.guild.id}, {"$set": {"notifications.csgo": True}}
                    )
                    await ctx.send("✅ Notifications for CSGO enabled !")

        elif arg == "disable":
            if guild_data["notifications"]["csgo"] is False:
                await ctx.send("Notifications for CSGO are already disabled !")
            else:
                self.mongo_DB_document.update_one(
                    {"server": ctx.guild.id}, {"$set": {"notifications.csgo": False}}
                )
                await ctx.send("✅ Notifications for CSGO disabled !")

    @notifications.command()
    @commands.has_permissions(administrator=True)
    async def lol(self, ctx, arg):
        guild_data = self.mongo_DB_document.find_one({"server": ctx.guild.id})
        if arg == "enable":
            if guild_data["notifications"]["channel"] is None:
                await ctx.send(
                    "Please set up the channel with `.en notifications channel [channel ID]` before enabling it."
                )
            else:
                if guild_data["notifications"]["lol"] is True:
                    await ctx.send("Notifications for LOL are already enabled !")
                else:
                    self.mongo_DB_document.update_one(
                        {"server": ctx.guild.id}, {"$set": {"notifications.lol": True}}
                    )
                    await ctx.send("✅ Notifications for LOL enabled !")

        elif arg == "disable":
            if guild_data["notifications"]["lol"] is False:
                await ctx.send("Notifications for LOL are already disabled !")
            else:
                self.mongo_DB_document.update_one(
                    {"server": ctx.guild.id}, {"$set": {"notifications.lol": False}}
                )
                await ctx.send("✅ Notifications for LOL disabled !")

    @notifications.command()
    @commands.has_permissions(administrator=True)
    async def dota2(self, ctx, arg):
        guild_data = self.mongo_DB_document.find_one({"server": ctx.guild.id})
        if arg == "enable":
            if guild_data["notifications"]["channel"] is None:
                await ctx.send(
                    "Please set up the channel with `.en notifications channel [channel ID]` before enabling it."
                )
            else:
                if guild_data["notifications"]["dota2"] is True:
                    await ctx.send("Notifications for Dota2 are already enabled !")
                else:
                    self.mongo_DB_document.update_one(
                        {"server": ctx.guild.id},
                        {"$set": {"notifications.dota2": True}},
                    )
                    await ctx.send("✅ Notifications for Dota2 enabled !")

        elif arg == "disable":
            if guild_data["notifications"]["dota2"] is False:
                await ctx.send("Notifications for Dota2 are already disabled !")
            else:
                self.mongo_DB_document.update_one(
                    {"server": ctx.guild.id}, {"$set": {"notifications.dota2": False}}
                )
                await ctx.send("✅ Notifications for Dota2 disabled !")

    @notifications.command()
    @commands.has_permissions(administrator=True)
    async def r6siege(self, ctx, arg):
        guild_data = self.mongo_DB_document.find_one({"server": ctx.guild.id})
        if arg == "enable":
            if guild_data["notifications"]["channel"] is None:
                await ctx.send(
                    "Please set up the channel with `.en notifications channel [channel ID]` before enabling it."
                )
            else:
                if guild_data["notifications"]["r6siege"] is True:
                    await ctx.send("Notifications for R6Siege are already enabled !")
                else:
                    self.mongo_DB_document.update_one(
                        {"server": ctx.guild.id},
                        {"$set": {"notifications.r6siege": True}},
                    )
                    await ctx.send("✅ Notifications for R6Siege enabled !")

        elif arg == "disable":
            if guild_data["notifications"]["r6siege"] is False:
                await ctx.send("Notifications for R6Siege are already disabled !")
            else:
                self.mongo_DB_document.update_one(
                    {"server": ctx.guild.id}, {"$set": {"notifications.r6siege": False}}
                )
                await ctx.send("✅ Notifications for R6Siege disabled !")

    @csgo.error
    @dota2.error
    @lol.error
    @r6siege.error
    async def notifications_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ You don't have the permissions to execute that command.")

    async def send_notification(self, game, match, thumbnail_url):
        embed = discord.Embed(
            title="Match in 5 minutes !",
            description="\u200b",
            colour=discord.Colour.dark_gold(),
        )
        embed.set_thumbnail(url=thumbnail_url)
        flag1 = (
            f":flag_{match['team1']['location'].lower()}:"
            if match["team1"]["location"] is not None
            else "🇺🇳"
        )
        flag2 = (
            f":flag_{match['team2']['location'].lower()}:"
            if match["team2"]["location"] is not None
            else "🇺🇳"
        )
        stream = f"[Watch]({match['stream']}) -" if match["stream"] is not None else ""
        embed.add_field(
            name=f"{flag1} {match['team1']['name']} vs {match['team2']['name']} {flag2}",
            value=f"{match['format']} - {stream} {match['event']}",
            inline=False,
        )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        for document in self.mongo_DB_document.find(
            {
                "$and": [
                    {f"notifications.{game}": True},
                    {"notifications.channel": {"$ne": None}},
                ]
            }
        ):
            channel = self.client.get_channel(document["notifications"]["channel"])
            await channel.send(embed=embed)

    async def check_for_matches(self):
        def get_datetime_object(date):
            return datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")

        current_time = datetime.datetime(
            year=datetime.datetime.utcnow().year,
            month=datetime.datetime.utcnow().month,
            day=datetime.datetime.utcnow().day,
            hour=datetime.datetime.utcnow().hour,
            minute=datetime.datetime.utcnow().minute,
        )
        for i in range(8):
            try:
                time_diff = (
                    get_datetime_object(self.csgo_matches[i]["date"]) - current_time
                ).total_seconds() / 60
                if time_diff <= 5 and time_diff > 0:
                    await self.send_notification(
                        game="csgo",
                        match=self.csgo_matches[i],
                        thumbnail_url="https://i.imgur.com/k4WFkk6.png",
                    )
            except IndexError:
                pass
            try:
                time_diff = (
                    get_datetime_object(self.csgo_matches[i]["date"]) - current_time
                ).total_seconds() / 60
                if time_diff <= 5 and time_diff > 0:
                    await self.send_notification(
                        game="dota2",
                        match=self.dota2_matches[i],
                        thumbnail_url="https://i.imgur.com/iOhWN0s.png",
                    )
            except IndexError:
                pass
            try:
                time_diff = (
                    get_datetime_object(self.csgo_matches[i]["date"]) - current_time
                ).total_seconds() / 60
                if time_diff <= 5 and time_diff > 0:
                    await self.send_notification(
                        game="r6siege",
                        match=self.r6siege_matches[i],
                        thumbnail_url="https://i.imgur.com/hwtQZAL.jpg",
                    )
            except IndexError:
                pass
            try:
                time_diff = (
                    get_datetime_object(self.csgo_matches[i]["date"]) - current_time
                ).total_seconds() / 60
                if time_diff <= 5 and time_diff > 0:
                    await self.send_notification(
                        game="lol",
                        match=self.lol_matches[i],
                        thumbnail_url="https://i.imgur.com/v12TmMh.png",
                    )
            except IndexError:
                pass
            i += 1


def setup(client):
    client.add_cog(Notifications(client))
