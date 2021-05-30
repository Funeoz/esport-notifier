import json
import sys
import os
import threading
import asyncio
import pymongo
from pymongo import MongoClient
from csgo.scorebot.scorebot import Livescore
import discord
from discord.ext import commands, tasks


class MatchFeed(commands.Cog):
    """Connects to the HLTV scorebot and returns an embed for each round"""

    def __init__(self, client):
        with open("database/csgo/runningMatches.json") as f:
            self.running_matches = json.loads(f.read())
        self.client = client
        self.maps_list = {
            "de_inferno": "https://i.imgur.com/SJ3BLOO.png",
            "de_vertigo": "https://i.imgur.com/g3HgPax.png",
            "de_overpass": "https://i.imgur.com/dgbXzs5.png",
            "de_dust2": "https://i.imgur.com/BP2oMOB.png",
            "de_nuke": "https://i.imgur.com/kJrdrXg.png",
            "de_mirage": "https://i.imgur.com/ZZaOLgV.png",
            "de_train": "https://i.imgur.com/IOAqYjp.png",
        }
        scoreboard = None
        self.scoreboard = scoreboard
        mongo_DB_password = os.getenv("MONGODB_PASSWORD")
        self.mongo_DB_document = MongoClient()
        self.loop = asyncio.get_event_loop()

    def on_connect(self):
        print("Connected to scorebot !")

    def on_disconnect(self):
        print("Disconnected from scorebot !")

    def on_scoreboard(self, sb):
        """Update the global scoreboard on each event."""
        self.scoreboard = sb

    def on_round_end(self, data):
        """print out the winner of the round and the total score of the map"""
        winning_team = (
            self.scoreboard.terrorists
            if data["winner"] == Livescore.TEAM_TERRORIST
            else self.scoreboard.counter_terrorists
        )
        win_type = None
        if data["winType"] == "Bomb_Defused":
            win_type = "The bomb has been defused"
        elif data["winType"] == "Target_Bombed":
            win_type = "The bomb exploded"
        elif data["winType"] == "CTs_Win":
            win_type = "Terrorist team has been eliminated"
        elif data["winType"] == "Terrorists_Win":
            win_type = "Counter-terrorist team has been eliminated"
        self.end_round = {
            "map": self.scoreboard.map_name,
            "round_winner": winning_team.name,
            "win_type": win_type,
            "terrorists": {
                "name": self.scoreboard.terrorists.name,
                "score": self.scoreboard.terrorists.score,
            },
            "counter-terrorists": {
                "name": self.scoreboard.counter_terrorists.name,
                "score": self.scoreboard.counter_terrorists.score,
            },
        }
        asyncio.run_coroutine_threadsafe(self.send_embed(), self.loop)

    def main(self, arg):
        ls = Livescore(arg)
        ls.on(ls.EVENT_CONNECT, self.on_connect)
        ls.on(ls.EVENT_SCOREBOARD, self.on_scoreboard)
        ls.on(ls.EVENT_ROUND_END, self.on_round_end)
        ls.on(ls.EVENT_DISCONNECT, self.on_disconnect)
        ls.socket().wait()

    def create_thread(self, hltv_id):
        # we create the thread and call launch_match that will connect to
        # the scorebot
        new_thread = threading.Thread(target=self.main, args=(hltv_id,), daemon=True)
        # start the thread
        new_thread.start()

    def get_matches_feed(self):
        if len(self.running_matches) != 0:
            for item in self.running_matches:
                # we call the method that creates a new thread for each match and we
                # pass the HLTV ID of the match
                self.create_thread(item["hltv_id"])

    async def send_embed(self):
        try:
            for item in self.running_matches:
                if (
                    self.end_round["terrorists"]["name"] == item["team1"]["name"]
                    or self.end_round["counter-terrorists"]["name"]
                    == item["team1"]["name"]
                ):
                    event = item["event"]
                    maps = item["maps"]
                if self.end_round["terrorists"]["name"] == item["team1"]["name"]:
                    logo_two = item["team1"]["logo"]
                    match_score_two = item["team1"]["score"]
                    flag_two = (
                        f":flag_{item['team1']['location'].lower()}:"
                        if item["team1"]["location"] is not None
                        else "🇺🇳"
                    )
                    logo_one = item["team2"]["logo"]
                    match_score_one = item["team2"]["score"]
                    flag_one = (
                        f":flag_{item['team2']['location'].lower()}:"
                        if item["team2"]["location"] is not None
                        else "🇺🇳"
                    )
                elif self.end_round["terrorists"]["name"] == item["team2"]["name"]:
                    logo_two = item["team2"]["logo"]
                    match_score_two = item["team2"]["score"]
                    flag_two = (
                        f":flag_{item['team2']['location'].lower()}:"
                        if item["team2"]["location"] is not None
                        else "🇺🇳"
                    )
                    logo_one = item["team1"]["logo"]
                    match_score_one = item["team1"]["score"]
                    flag_one = (
                        f":flag_{item['team1']['location'].lower()}:"
                        if item["team1"]["location"] is not None
                        else "🇺🇳"
                    )

            embed = discord.Embed(
                title=f"{flag_one} {self.end_round['counter-terrorists']['name']} vs {self.end_round['terrorists']['name']} {flag_two}",
                description=event,
                colour=discord.Colour.dark_gold(),
            )
            embed.set_thumbnail(
                url=logo_one
                if self.end_round["round_winner"]
                == self.end_round["counter-terrorists"]["name"]
                else logo_two
            )
            embed.set_author(
                name=self.end_round["map"],
                icon_url=self.maps_list[self.end_round["map"]],
            )
            embed.add_field(
                name="Round winner",
                value=f"**{self.end_round['round_winner']}** - {self.end_round['win_type']}",
                inline=False,
            )
            embed.add_field(
                name="Map Score",
                value=f"**{self.end_round['counter-terrorists']['score']}-{self.end_round['terrorists']['score']}**",
                inline=True,
            )
            embed.add_field(
                name="Match Score",
                value=f"**{match_score_one}-{match_score_two}**",
                inline=True,
            )
            embed.add_field(name="Maps", value=maps, inline=False)
            embed.add_field(
                name="** **",
                value="[Support Server](https://discord.gg/vTyxDYy) | [Donate](https://esport-notifier.github.io/donate) - Funeoz#2915",
                inline=False,
            )
            for guild_with_feed in self.mongo_DB_document.find({"csgo_live": True}):
                channel = self.client.get_channel(guild_with_feed["channel"])
                if channel is not None:
                    await channel.send(embed=embed)
        except KeyError:
            pass
        except RuntimeError:
            pass


def setup(client):
    client.add_cog(MatchFeed(client))
