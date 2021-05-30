import json
import requests
import datetime
from bs4 import BeautifulSoup


def get_world_ranking():
    """collect the top30 ranking from GosuGamers"""

    def update_data():
        try:
            page = BeautifulSoup(
                requests.get("https://www.gosugamers.net/dota2/rankings").text, "lxml"
            )
            teams = page.find("ul", {"class": "ranking-list"})
            # the list will contain the date and the ranking
            teamlist = [{"data_date": str(datetime.date.today())}]
            for team in teams.find_all("li")[:30]:
                newteam = {
                    "name": "".join(team.find("a").find_all(text=True, recursive=False))
                    .strip()
                    .encode("ascii", "ignore")
                    .decode(),
                    "rank": team.find("a")
                    .find("span", {"class": "ranking"})
                    .text.strip(),
                    "rank-points": team.find("a")
                    .find("span", {"class": "elo"})
                    .text.strip(),
                }
                teamlist.append(newteam)
            # save ranking to a json file
            with open("database/dota2/worldRanking.json", "w") as file:
                file.write(json.dumps(teamlist, indent=4))
        except AttributeError:
            pass

    try:
        with open("database/dota2/worldRanking.json", "r") as file:
            file_dumped = json.load(file)
            if file_dumped[0]["data_date"] != str(datetime.date.today()):
                update_data()
            else:
                return
    except FileNotFoundError:
        update_data()

