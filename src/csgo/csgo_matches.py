import json
import requests
from bs4 import BeautifulSoup
import os
import sys
import inspect

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from matches import Matches


class CsgoMatches(Matches):
    def __init__(self):
        Matches.__init__(self, game="csgo")

    def get_running_matches(self):
        """get currently ongoing matches"""
        # To display the live data, HLTV uses scorebots (e.g: https://scorebot-secure.hltv.org).
        # To be able to communicate with them, we need the ID of the match. Using Bs4,
        #  we get the details of ongoing matches from the HLTV website and return them into a list.
        hltv_data = BeautifulSoup(
            requests.get(
                "https://www.hltv.org/matches",
                headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            ).text,
            "lxml",
        )
        pandascore_data = json.loads(
            requests.get(
                f"https://api.pandascore.co/csgo/matches/running?token={self.token}"
            ).content
        )
        matches = []
        list2 = []
        # we collect the ID from HLTV
        for match in hltv_data.find_all("div", class_="liveMatch-container"):
            info = {
                "hltv_id": match.get("data-scorebot-id"),
                "maps": match.get("data-maps").replace(",", ", "),
                "team1": {
                    "name": match.find("div", {"class": "matchTeams text-ellipsis"})
                    .find("div", {"class": "matchTeam"})
                    .find("img")["title"]
                },
                "team2": {
                    "name": match.find("div", {"class": "matchTeams text-ellipsis"})
                    .find_all("div", {"class": "matchTeam"})[1]
                    .find("img")["title"]
                },
            }
            matches.append(info)
        # we take some more data from pandascore
        for match in pandascore_data:
            info2 = {
                "event": match["tournament"]["slug"].replace("-", " ").upper(),
                "format": "bo" + str(match["number_of_games"]),
                "date": match["scheduled_at"],
                "stream": match["official_stream_url"],
                "team1": {
                    "name": match["opponents"][0]["opponent"]["name"],
                    "logo": match["opponents"][0]["opponent"]["image_url"],
                    "location": match["opponents"][0]["opponent"]["location"],
                    "score": match["results"][0]["score"],
                },
                "team2": {
                    "name": match["opponents"][1]["opponent"]["name"],
                    "logo": match["opponents"][1]["opponent"]["image_url"],
                    "location": match["opponents"][1]["opponent"]["location"],
                    "score": match["results"][1]["score"],
                },
            }
            list2.append(info2)
        # we merge the data
        for elem1 in matches:
            for elem2 in list2:
                if elem1["team1"]["name"] == elem2["team1"]["name"]:
                    elem1.update(elem2)
        # write the result to a json file
        with open("database/csgo/runningMatches.json", "w") as file:
            file.write(json.dumps(matches, indent=4))

