import requests
import json
import datetime
from bs4 import BeautifulSoup
from python_utils import converters

def get_world_ranking():
    """collect the top30 ranking from GosuGamers"""
    
    def update_data():
        """collect the top30 ranking from HLTV"""
        headers = {
            "referer": "https://www.hltv.org/stats",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        }
        page = BeautifulSoup(
            requests.get("http://www.hltv.org/ranking/teams/", headers=headers).text, "lxml"
        )
        teams = page.find("div", {"class": "ranking"})
        # the list will contain the date and the ranking
        teamlist = [{"data_date" : str(datetime.date.today())}]
        teamlist.append({"date": page.find("div", {"class": "regional-ranking-header"}).text})
        for team in teams.find_all("div", {"class": "ranked-team standard-box"}):
            newteam = {
                "name": team.find("div", {"class": "ranking-header"})
                .select(".name")[0]
                .text.strip(),
                "rank": converters.to_int(
                    team.select(".position")[0].text.strip(), regexp=True
                ),
                "rank-points": converters.to_int(
                    team.find("span", {"class": "points"}).text, regexp=True
                ),
            }
            teamlist.append(newteam)
        # save ranking to a json file
        with open("database/csgo/worldRanking.json", "w") as file:
            file.write(json.dumps(teamlist, indent=4))

    try:
        with open("database/csgo/worldRanking.json", "r") as file:
            file_dumped = json.load(file)
            if file_dumped[0]['data_date'] != str(datetime.date.today()):
                update_data()
            else:
                return
    except FileNotFoundError:
        update_data()