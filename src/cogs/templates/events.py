import discord
from discord.ext import commands


class GameEvents(object):
    def __init__(self, title, thumbnail_url, events):
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.events = events

    def past_events_embed(self):
        embed = discord.Embed(
            title=self.title, value="\u200b", colour=discord.Colour.dark_gold(),
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        for item in self.events:
            winner = (
                f"- Winner : **{item['winner']}**" if item["winner"] is not None else ""
            )
            prizepool = (
                f"- Prizepool : **{item['prizepool']}**"
                if item["prizepool"] is not None
                else ""
            )
            embed.add_field(
                name=item["name"],
                value=f"`{item['start_date']}` to `{item['end_date']}` {winner} {prizepool}",
                inline=False,
            )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        return embed

    def running_events_embed(self):
        embed = discord.Embed(
            title=self.title, value="\u200b", colour=discord.Colour.dark_gold(),
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        for item in self.events:
            end_date = item["end_date"] if item["end_date"] is not None else "n/a"
            prizepool = (
                f"- Prizepool : **{item['prizepool']}**"
                if item["prizepool"] is not None
                else ""
            )
            embed.add_field(
                name=item["name"],
                value=f"`{item['start_date']}` to `{end_date}` {prizepool}",
                inline=False,
            )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        return embed

    def upcoming_events_embed(self):
        embed = discord.Embed(
            title=self.title, value="\u200b", colour=discord.Colour.dark_gold(),
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        for item in self.events:
            end_date = item["end_date"] if item["end_date"] is not None else "n/a"
            prizepool = (
                f"- Prizepool : **{item['prizepool']}**"
                if item["prizepool"] is not None
                else ""
            )
            embed.add_field(
                name=item["name"],
                value=f"`{item['start_date']}` to `{end_date}` {prizepool}",
                inline=False,
            )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        return embed
