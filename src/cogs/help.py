import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, ctx):
        """Display help for Esport Notifier"""
        embed = discord.Embed(
            title="Esport Notifier Help",
            description="Every command below starts with `.en`",
            colour=discord.Colour.dark_gold(),
        )
        embed.add_field(
            name="`timezone`",
            value="Set the timezone according to yours. See [https://esport-notifier.github.io/docs/timezones-list/](https://esport-notifier.github.io/docs/timezones-list/).",
            inline=False,
        )
        embed.add_field(name="`help`", value="Display this help message.", inline=False)
        embed.add_field(
            name="`<game> help`",
            value="Display the help message for a game (`csgo`, `valorant`, `lol`, `dota2`, `r6siege`).",
            inline=False,
        )
        embed.add_field(
            name="`notifications help`",
            value="Display the help for notifications.",
            inline=False,
        )
        embed.add_field(
            name="`status`",
            value="Display the current status of the bot and its services.",
            inline=False,
        )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))
