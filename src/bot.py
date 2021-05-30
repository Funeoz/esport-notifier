import os
import sys
from pymongo import MongoClient
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from cogs.live_score import MatchFeed
from cogs.notifications import Notifications
from data_update import update_all_data

load_dotenv()
update_all_data()


mongo_DB_password = os.getenv("MONGODB_PASSWORD")
mongo_DB_document = MongoClient()

intents = discord.Intents.default()

client = commands.Bot(command_prefix=".en ", intents=intents)
client.remove_command("help")
live_csgo = MatchFeed(client)
live_csgo.get_matches_feed()


@client.event
async def on_guild_join(guild):
    mongo_DB_document.insert_one(
        {
            "server": guild.id,
            "timezone": "Etc/GMT+0",
            "channel": None,
            "csgo_live": False,
            "notifications": {
                "channel": None,
                "csgo": False,
                "lol": False,
                "r6siege": False,
                "dota2": False,
            },
        }
    )
    logs_channel = client.get_channel(757515957441790082)
    await logs_channel.send(f"🟢 Joined a server: {guild.name} - {str(guild.id)}")


async def fix_db():
    guilds_list = [guild.id for guild in client.guilds]
    channel = client.get_channel(778264104417755156)
    for document in mongo_DB_document.find({}):
        if document["server"] not in guilds_list:
            await channel.send(document)
    for guild in guilds_list:
        searched_document = mongo_DB_document.find_one({"server": guild})
        if searched_document is None:
            mongo_DB_document.insert_one(
                {
                    "server": guild,
                    "timezone": "Etc/GMT+0",
                    "channel": None,
                    "csgo_live": False,
                    "notifications": {
                        "channel": None,
                        "csgo": False,
                        "lol": False,
                        "r6siege": False,
                        "dota2": False,
                    },
                }
            )
            await channel.send(f"Added server : {guild}")
    for guild_with_feed in mongo_DB_document.find({"csgo_live": True}):
        channel = client.get_channel(guild_with_feed["channel"])
        if channel is None:
            mongo_DB_document.update_one(
                {"server": guild_with_feed["server"]},
                {"$set": {"csgo_live": False, "channel": None}},
            )


@client.event
async def on_guild_remove(guild):
    mongo_DB_document.delete_one({"server": guild.id})
    logs_channel = client.get_channel(757515957441790082)
    await logs_channel.send(f"🔴 Left a server: {guild.name} - {str(guild.id)}")


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(".en help"))
    await Notifications(client).check_for_matches()
    print("Fixing DB !")
    await fix_db()
    print("Bot is ready !")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("⛔ Invalid command. See `.en help`.")


@tasks.loop(minutes=5)
async def stop_script():
    # temporary workaround to get live feed for
    # ongoing matches
    if stop_script.current_loop != 0:
        os.execl(sys.executable, sys.executable, *sys.argv)


stop_script.start()

for filename in os.listdir("src/cogs"):
    if filename.endswith(".py") and filename not in "__init__.py":
        client.load_extension(f"cogs.{filename[:-3]}")

client.run(os.getenv("DISCORD_TOKEN"))

