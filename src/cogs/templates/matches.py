import datetime
import dateutil
import discord
import pytz
from discord.ext import commands


class GameMatches(object):
    def __init__(self, title, thumbnail_url, matches):
        self.title = title
        self.thumbnail_url = thumbnail_url
        self.matches = matches

    def past_matches_embed(self, date):

        # we create an embed that displays the matches of a past day
        embed = discord.Embed(
            title=self.title,
            description=f"📅 {date}",
            colour=discord.Colour.dark_gold(),
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        # go through all the past matches
        for item in self.matches:
            if str(date) == item["date"]:
                # we create a new field if the date of the next match equals
                # the date of the precedent one
                # to handle "null" values for location and avoid blocking
                # the script, we put the emoji of the united nations
                flag1_pe = (
                    f":flag_{item['team1']['location'].lower()}:"
                    if item["team1"]["location"] is not None
                    else "🇺🇳"
                )
                flag2_pe = (
                    f":flag_{item['team2']['location'].lower()}:"
                    if item["team2"]["location"] is not None
                    else "🇺🇳"
                )
                embed.add_field(
                    name=f"{flag1_pe} {item['team1']['name']} vs {item['team2']['name']} {flag2_pe}",
                    value=f"{item['format']} - `{item['team1']['score']}-{item['team2']['score']}` - Winner : **{item['winner']}** - {item['event']}",
                    inline=False,
                )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        return embed

    def running_matches_embed(self):
        date = datetime.date.today()

        # we create an embed that displays the matches of an upcoming day
        embed = discord.Embed(
            title=self.title,
            description=f"📅 {date}",
            colour=discord.Colour.dark_gold(),
        )
        embed.set_thumbnail(url=self.thumbnail_url)

        if self.matches == []:
            embed.add_field(name="**No ongoing matches**", value="\u200b", inline=False)

        else:
            # go through all the running matches
            for item in self.matches:

                if str(date) == item["date"][:10]:
                    # we create a new field if the date of the next match equals
                    # the date of the precedent one
                    # to handle "null" values for location and avoid blocking
                    # the script, we put the emoji of the united nations
                    flag1 = (
                        f":flag_{item['team1']['location'].lower()}:"
                        if item["team1"]["location"] is not None
                        else "🇺🇳"
                    )
                    flag2 = (
                        f":flag_{item['team2']['location'].lower()}:"
                        if item["team2"]["location"] is not None
                        else "🇺🇳"
                    )
                    stream = (
                        f"- [Watch]({item['stream']})"
                        if item["stream"] is not None
                        else ""
                    )
                    embed.add_field(
                        name=f"{flag1} {item['team1']['name']} vs {item['team2']['name']} {flag2}",
                        value=f"{item['format']} - Live result : `{item['team1']['score']}-{item['team2']['score']}` - Maps : {item['maps'].replace(',',', ')}\n {item['event']} {stream}",
                        inline=False,
                    )
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )

        return embed

    def upcoming_matches_embed(self, date, guild_timezone):
        embed = discord.Embed(
            title=self.title,
            description=f"📅 {date}",
            colour=discord.Colour.dark_gold(),
        )
        embed.set_thumbnail(url=self.thumbnail_url)
        # go through all the upcoming matches
        for item in self.matches:
            localtime = str(
                dateutil.parser.parse(item["date"])
                .astimezone(pytz.timezone(guild_timezone))
                .isoformat()
            )
            if str(date) == localtime[:10]:
                # we create a new field if the date of the next match equals
                # the date of the precedent one
                # to handle "null" values for location and avoid blocking
                # the script, we put the emoji of the united nations
                flag1 = (
                    f":flag_{item['team1']['location'].lower()}:"
                    if item["team1"]["location"] is not None
                    else "🇺🇳"
                )
                flag2 = (
                    f":flag_{item['team2']['location'].lower()}:"
                    if item["team2"]["location"] is not None
                    else "🇺🇳"
                )
                stream = (
                    f"[Watch]({item['stream']}) -" if item["stream"] is not None else ""
                )
                embed.add_field(
                    name=f"{localtime[11:16]} - {flag1} {item['team1']['name']} vs {item['team2']['name']} {flag2}",
                    value=f"{item['format']} - {stream} {item['event']}",
                    inline=False,
                )
        embed.add_field(
            name="** **",
            value=f"`{guild_timezone}`- [Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        return embed
