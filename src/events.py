import json
import time
import datetime
import os
import requests


class Events(object):
    def __init__(self, game):
        self.game = game
        self.token = os.getenv("PANDASCORE_TOKEN")
        self.today_date = datetime.date.today()
        self.week_ago_date = self.today_date - datetime.timedelta(days=7)

    def get_past_events(self):
        """Get last 10 events and their respective prizepool and winner"""
        data = json.loads(
            requests.get(
                f"https://api.pandascore.co/{self.game}/tournaments/past?token={self.token}&page[size]=10"
            ).content
        )
        past_events = []
        for item in data:
            if item["winner_id"] is None:
                event = {
                    "start_date": item["begin_at"][:10],
                    "end_date": item["end_at"][:10],
                    "name": item["slug"].replace("-", " ").upper(),
                    "prizepool": item["prizepool"],
                    "winner": None,
                }
            else:
                for team in item["teams"]:
                    winner_name = (
                        team["name"] if item["winner_id"] == team["id"] else None
                    )
                event = {
                    "start_date": item["begin_at"][:10],
                    "end_date": item["end_at"][:10],
                    "name": item["slug"].replace("-", " ").upper(),
                    "prizepool": item["prizepool"],
                    "winner": winner_name,
                }
            past_events.append(event)
        with open(f"database/{self.game}/pastEvents.json", "w") as file:
            file.write(json.dumps(past_events, indent=4))

    def get_upcoming_events(self):
        """Get the upcoming 10 events, the prizepool and the dates"""
        data = json.loads(
            requests.get(
                f"https://api.pandascore.co/{self.game}/tournaments/upcoming?token={self.token}&page[size]=10"
            ).content
        )
        upcoming_events = []
        for item in data:
            event = {
                "start_date": item["begin_at"][:10],
                "end_date": item["end_at"][:10] if item["end_at"] is not None else None,
                "name": item["slug"].replace("-", " ").upper(),
                "prizepool": item["prizepool"],
            }
            upcoming_events.append(event)
        with open(f"database/{self.game}/upcomingEvents.json", "w") as file:
            file.write(json.dumps(upcoming_events, indent=4))

    def get_running_events(self):
        """Get the ongoing events"""
        data = json.loads(
            requests.get(
                f"https://api.pandascore.co/{self.game}/tournaments/running/?token={self.token}&range[begin_at]={self.week_ago_date},{self.today_date}"
            ).content
        )
        running_events = []
        for item in data:
            event = {
                "start_date": item["begin_at"][:10],
                "end_date": item["end_at"][:10] if item["end_at"] is not None else None,
                "name": item["slug"].replace("-", " ").upper(),
                "prizepool": item["prizepool"],
            }
            running_events.append(event)
        with open(f"database/{self.game}/runningEvents.json", "w") as file:
            file.write(json.dumps(running_events, indent=4))
