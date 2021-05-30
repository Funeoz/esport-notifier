import json
import datetime
import asyncio
import discord
from discord.ext import commands


class Valorant(commands.Cog):
    def __init__(self, client):
        self.client = client
        """with open("database/valorant/worldRanking.json", "r") as file:
            self.ranking = json.loads(file.read())"""
        with open("database/valorant/pastEvents.json", "r") as file:
            self.past_events = json.loads(file.read())
        with open("database/valorant/runningEvents.json", "r") as file:
            self.running_events = json.loads(file.read())
        with open("database/valorant/upcomingEvents.json", "r") as file:
            self.upcoming_events = json.loads(file.read())
        with open("database/valorant/pastMatches.json", "r") as file:
            self.past_matches = json.loads(file.read())

    @commands.group()
    async def valorant(self, ctx):
        pass

    @valorant.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Valorant Commands Help",
            description="Every command below starts with `.en valorant`",
            colour=discord.Colour.dark_gold(),
        )
        embed.add_field(
            name="`matches past`",
            value="Show the results of past matches.",
            inline=False,
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
        """embed.add_field(
            name="`ranking`", value="Show the VLR.gg Top 30 ranking.", inline=False
        )"""
        embed.add_field(
            name="** **",
            value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
            inline=False,
        )
        await ctx.send(embed=embed)

    @valorant.command()
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
                            days=3
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
                new_embed = discord.Embed(
                    title="Past Valorant Matches",
                    description=f"📅 {self.date_past_embed}",
                    colour=discord.Colour.dark_gold(),
                )
                new_embed.set_thumbnail(url="https://i.imgur.com/v7H8IrP.png")
                for item in self.past_matches:
                    if item["date"] == str(self.date_past_embed):
                        new_embed.add_field(
                            name=f"{item['team1']['name']} vs {item['team2']['name']}",
                            value=f"`{item['team1']['score']}-{item['team2']['score']}` - Winner : **{item['winner']}** - {item['event']}",
                            inline=False,
                        )
                new_embed.add_field(
                    name="** **",
                    value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
                    inline=False,
                )
                # modify the old embed and send it
                await self.msg1.edit(embed=new_embed)
                await wait_for_reaction_pe(ctx, new_embed)

            past_matches_embed = discord.Embed(
                title="Past Valorant Matches",
                value="\u200b",
                colour=discord.Colour.dark_gold(),
            )
            past_matches_embed.set_thumbnail(url="https://i.imgur.com/v7H8IrP.png")

            for item in self.past_matches:

                if str(self.date_past_embed) == item["date"]:
                    past_matches_embed.add_field(
                        name=f"{item['team1']['name']} vs {item['team2']['name']}",
                        value=f"`{item['team1']['score']}-{item['team2']['score']}` - Winner : **{item['winner']}** - {item['event']}",
                        inline=False,
                    )
                else:
                    pass
            past_matches_embed.add_field(
                name="** **",
                value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
                inline=False,
            )
            self.msg1 = await ctx.send(embed=past_matches_embed)
            await self.msg1.add_reaction(emoji="⬅️")
            await self.msg1.add_reaction(emoji="➡️")
            await wait_for_reaction_pe(ctx, past_matches_embed)

        else:
            ctx.command.reset_cooldown(ctx)

    @matches.error
    async def matches_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⛔ Missing argument. See `.en valorant help`.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"⛔ Active cooldown ! Please try again in {error.retry_after:.2f}s"
            )

    @valorant.command()
    async def events(self, ctx, arg):

        if arg == "past":

            past_events_embed = discord.Embed(
                title="Past Valorant Events",
                value="\u200b",
                colour=discord.Colour.dark_gold(),
            )
            past_events_embed.set_thumbnail(url="https://i.imgur.com/v7H8IrP.png")
            for item in self.past_events:
                past_events_embed.add_field(
                    name=item["name"],
                    value=f"{item['dates']} - Prizepool: **{item['prizepool']}**",
                    inline=False,
                )
            past_events_embed.add_field(
                name="** **",
                value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
                inline=False,
            )
            await ctx.send(embed=past_events_embed)

        elif arg == "running":

            running_events_embed = discord.Embed(
                title="Running Valorant Events",
                value="\u200b",
                colour=discord.Colour.dark_gold(),
            )
            running_events_embed.set_thumbnail(url="https://i.imgur.com/v7H8IrP.png")
            for item in self.running_events:
                running_events_embed.add_field(
                    name=item["name"],
                    value=f"{item['dates']} - Prizepool: **{item['prizepool']}**",
                    inline=False,
                )
            running_events_embed.add_field(
                name="** **",
                value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
                inline=False,
            )
            await ctx.send(embed=running_events_embed)

        elif arg == "upcoming":

            upcoming_events_embed = discord.Embed(
                title="Upcoming Valorant Events",
                value="\u200b",
                colour=discord.Colour.dark_gold(),
            )
            upcoming_events_embed.set_thumbnail(url="https://i.imgur.com/v7H8IrP.png")
            for item in self.upcoming_events:
                upcoming_events_embed.add_field(
                    name=item["name"],
                    value=f"{item['dates']} - Prizepool: **{item['prizepool']}**",
                    inline=False,
                )
            upcoming_events_embed.add_field(
                name="** **",
                value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Made by Funeoz#2915",
                inline=False,
            )
            await ctx.send(embed=upcoming_events_embed)

        else:
            ctx.command.reset_cooldown(ctx)

    @events.error
    async def events_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⛔ Missing argument. See `.en valorant help`.")

    """@valorant.command()
    async def ranking(self, ctx):
        # create an embed for the first 15 teams
        # (Discord limits the characters' number)
        embed = discord.Embed(
            title="VLR.gg Valorant World Ranking",
            url="https://www.vlr.gg/rankings",
            colour=discord.Colour.dark_gold(),
        )
        for item in self.ranking[:16]:
            embed.add_field(
                name="\u200b",
                value=f"#{item['rank']} : **{item['name']}** - {item['rank-points']} points",
                inline=False,
            )
        embed.set_thumbnail(url="https://www.vlr.gg/img/vlr/logo_header.png")
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
        await ctx.send(embed=embed_2)"""


def setup(client):
    client.add_cog(Valorant(client))
