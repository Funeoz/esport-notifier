import os
import requests
import sys
import asyncio
import pymongo
from pymongo import MongoClient
import discord
import pytz
from discord.ext import commands, tasks


def get_status(URL, headers={}):
    """function to check the status of a web service"""
    status = requests.get(URL, headers=headers).status_code
    if status in [200, 201, 202, 203, 204, 205, 206]:
        return "`🟩 UP`"
    return "`🟥 DOWN`"


class Administration(commands.Cog):
    def __init__(self, client):
        self.client = client
        mongo_DB_password = os.getenv("MONGODB_PASSWORD")
        self.mongo_DB_document = MongoClient()

    @commands.command()
    async def status(self, ctx):
        """Return the status of Esport Notifier and its services"""
        embed = discord.Embed(
            title="Esport Notifier Status", colour=discord.Colour.dark_gold()
        )
        embed.set_thumbnail(url="https://i.imgur.com/zDBHobF.png")
        embed.add_field(
            name="PandaScore Status",
            value=get_status(
                f"https://api.pandascore.co/?token={os.getenv('PANDASCORE_TOKEN')}"
            ),
            inline=True,
        )
        embed.add_field(
            name="Servers", value=f"`{len(self.client.guilds)}`", inline=True,
        )
        embed.add_field(
            name="Latency", value=f"`{round(self.client.latency, 1)}s`", inline=True,
        )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        """To shut down the bot properly by the bot owner (Funeoz#2915)"""
        await ctx.send("😴 Turning off the bot in 5 seconds...")
        await asyncio.sleep(5)
        await ctx.bot.logout()
        await sys.exit()

    @commands.command()
    @commands.is_owner()
    async def check_dead(self, ctx):
        for guild_with_feed in self.mongo_DB_document.find({"csgo_live": True}):
            channel = self.client.get_channel(guild_with_feed["channel"])
            print(guild_with_feed["server"], channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def timezone(self, ctx, time_zone):
        """To set the timezone of the server"""
        if time_zone in pytz.all_timezones:
            self.mongo_DB_document.update_one(
                {"server": ctx.guild.id}, {"$set": {"timezone": time_zone}}
            )
            await ctx.send(f"Timezone set to `{time_zone}`")
        else:
            await ctx.send("Invalid timezone. See available timezone list !")

    @timezone.error
    async def timezone_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "Please send one of the available timezones. See https://esport-notifier.github.io/docs/timezones-list/."
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("⛔ You don't have the permissions to execute that command.")


def setup(client):
    client.add_cog(Administration(client))
