import json
import requests
import datetime
import time
import os


class Matches(object):
    def __init__(self, game):
        self.game = game
        self.token = os.getenv("PANDASCORE_TOKEN")
        self.today_date = datetime.date.today()
        self.week_ago_date = self.today_date - datetime.timedelta(days=7)
        self.next_two_days_date = self.today_date + datetime.timedelta(days=2)

    def get_past_matches(self):
        """Get matches from the past week"""
        data = json.loads(
            requests.get(
                f"https://api.pandascore.co/{self.game}/matches/past/?token={self.token}&range[begin_at]={self.week_ago_date},{self.today_date}&page[size]=100"
            ).content
        )
        data2 = json.loads(
            requests.get(
                f"https://api.pandascore.co/{self.game}/matches/past/?token={self.token}&range[begin_at]={self.week_ago_date},{self.today_date}&page[size]=100&page[number]=2"
            ).content
        )
        data_merged = data + data2
        past_matches = []
        # extract from the request only the needed data
        for item in data_merged:
            match = {
                "date": item["scheduled_at"][:10],
                "event": item["tournament"]["slug"].replace("-", " ").upper(),
                "format": "bo" + str(item["number_of_games"]),
                "winner": item["winner"]["name"]
                if item["winner"] is not None
                else None,
                "team1": {
                    "name": item["opponents"][0]["opponent"]["name"],
                    "location": item["opponents"][0]["opponent"]["location"],
                    "score": item["results"][0]["score"],
                },
                "team2": {
                    "name": item["opponents"][1]["opponent"]["name"],
                    "location": item["opponents"][1]["opponent"]["location"],
                    "score": item["results"][1]["score"],
                },
            }
            past_matches.append(match)
        # write the needed data to a json file
        with open(f"database/{self.game}/pastMatches.json", "w") as file:
            file.write(json.dumps(past_matches, indent=4))

    def get_upcoming_matches(self):
        """Get matches for the next two days"""
        # ask the API
        data = json.loads(
            requests.get(
                f"https://api.pandascore.co/{self.game}/matches/upcoming/?token={self.token}&range[begin_at]={self.today_date},{self.next_two_days_date}"
            ).content
        )
        upcoming_matches = []
        # extract from the request only the needed data
        for item in data:
            # if the opponents are not populated, name them as TBD by default
            if not item["opponents"]:
                match = {
                    "date": item["scheduled_at"],
                    "event": item["tournament"]["slug"].replace("-", " ").upper(),
                    "format": "bo" + str(item["number_of_games"]),
                    "stream": item["streams"]["official"]["raw_url"],
                    "team1": {"name": "TBD", "location": None},
                    "team2": {"name": "TBD", "location": None},
                }
            # if only one opponent is known
            elif len(item["opponents"]) == 1:
                match = {
                    "date": item["scheduled_at"],
                    "event": item["tournament"]["slug"].replace("-", " ").upper(),
                    "format": "bo" + str(item["number_of_games"]),
                    "stream": item["streams"]["official"]["raw_url"],
                    "team1": {
                        "name": item["opponents"][0]["opponent"]["name"],
                        "location": item["opponents"][0]["opponent"]["location"],
                    },
                    "team2": {"name": "TBD", "location": None},
                }
            # if both opponents are known
            else:
                match = {
                    "date": item["scheduled_at"],
                    "event": item["tournament"]["slug"].replace("-", " ").upper(),
                    "format": "bo" + str(item["number_of_games"]),
                    "stream": item["streams"]["official"]["raw_url"],
                    "team1": {
                        "name": item["opponents"][0]["opponent"]["name"],
                        "location": item["opponents"][0]["opponent"]["location"],
                    },
                    "team2": {
                        "name": item["opponents"][1]["opponent"]["name"],
                        "location": item["opponents"][1]["opponent"]["location"],
                    },
                }
            upcoming_matches.append(match)
        # save to a json file
        with open(f"database/{self.game}/upcomingMatches.json", "w") as file:
            file.write(json.dumps(upcoming_matches, indent=4))

    def get_running_matches(self):
        """get currently ongoing matches"""
        data = json.loads(
            requests.get(
                f"https://api.pandascore.co/{self.game}/matches/running?token={self.token}"
            ).content
        )
        running_matches = []
        # we take some more data from pandascore
        for item in data:
            match = {
                "event": item["tournament"]["slug"].replace("-", " ").upper(),
                "format": "bo" + str(item["number_of_games"]),
                "date": item["scheduled_at"],
                "stream": item["official_stream_url"],
                "team1": {
                    "name": item["opponents"][0]["opponent"]["name"],
                    "logo": item["opponents"][0]["opponent"]["image_url"],
                    "location": item["opponents"][0]["opponent"]["location"],
                    "score": item["results"][0]["score"],
                },
                "team2": {
                    "name": item["opponents"][1]["opponent"]["name"],
                    "logo": item["opponents"][1]["opponent"]["image_url"],
                    "location": item["opponents"][1]["opponent"]["location"],
                    "score": item["results"][1]["score"],
                },
            }
            running_matches.append(match)
        # write the result to a json file
        with open(f"database/{self.game}/runningMatches.json", "w") as file:
            file.write(json.dumps(running_matches, indent=4))
