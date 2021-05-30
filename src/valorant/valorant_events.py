import json
import requests
from bs4 import BeautifulSoup


class ValorantEvents(object):
    def __init__(self):
        self.headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def get_past_events(self):
        """Get the last 10 events from VLR.gg"""
        page = BeautifulSoup(
            requests.get("https://www.vlr.gg/events", headers=self.headers).text, "lxml"
        )
        events = page.find_all("div", {"class": "events-container-col"})[1]
        events_list = []
        for event in events.find_all("a")[:10]:
            newevent = {
                "name": event.find("div", {"class": "event-item-inner"})
                .find("div", {"class": "event-item-title"})
                .text.strip(),
                "dates": "".join(
                    event.find("div", {"class": "event-item-inner"})
                    .find("div", {"class": "event-item-desc-item mod-dates"})
                    .find_all(text=True, recursive=False)
                )
                .strip()
                .replace("\u2014", "-"),
                "prizepool": "".join(
                    event.find("div", {"class": "event-item-inner"})
                    .find("div", {"class": "event-item-desc-item mod-prize"})
                    .find_all(text=True, recursive=False)
                ).strip(),
            }
            events_list.append(newevent)
        with open("database/valorant/pastEvents.json", "w") as file:
            file.write(json.dumps(events_list, indent=4))

    def get_ongoing_upcoming_events(self):
        """Get the upcoming and ongoing events from VLR.gg"""
        page = BeautifulSoup(
            requests.get("https://www.vlr.gg/events", headers=self.headers).text, "lxml"
        )
        events = page.find_all("div", {"class": "events-container-col"})[0]
        # because the upcoming and ongoing events are within the same div,
        # we create two lists that will be written to two different files
        ongoing_events_list = []
        upcoming_events_list = []
        for event in events.find_all("a"):
            if (
                event.find("div", {"class": "event-item-inner"})
                .find("div", {"class": "event-item-desc-item"})
                .find("span")
                .text
                == "ongoing"
            ):
                ongoing_event = {
                    "name": event.find("div", {"class": "event-item-inner"})
                    .find("div", {"class": "event-item-title"})
                    .text.strip(),
                    "dates": "".join(
                        event.find("div", {"class": "event-item-inner"})
                        .find("div", {"class": "event-item-desc-item mod-dates"})
                        .find_all(text=True, recursive=False)
                    )
                    .strip()
                    .replace("\u2014", "-"),
                    "prizepool": "".join(
                        event.find("div", {"class": "event-item-inner"})
                        .find("div", {"class": "event-item-desc-item mod-prize"})
                        .find_all(text=True, recursive=False)
                    ).strip(),
                }
                ongoing_events_list.append(ongoing_event)
            elif (
                event.find("div", {"class": "event-item-inner"})
                .find("div", {"class": "event-item-desc-item"})
                .find("span")
                .text
                == "upcoming"
            ):
                upcoming_event = {
                    "name": event.find("div", {"class": "event-item-inner"})
                    .find("div", {"class": "event-item-title"})
                    .text.strip(),
                    "dates": "".join(
                        event.find("div", {"class": "event-item-inner"})
                        .find("div", {"class": "event-item-desc-item mod-dates"})
                        .find_all(text=True, recursive=False)
                    )
                    .strip()
                    .replace("\u2014", "-"),
                    "prizepool": "".join(
                        event.find("div", {"class": "event-item-inner"})
                        .find("div", {"class": "event-item-desc-item mod-prize"})
                        .find_all(text=True, recursive=False)
                    ).strip(),
                }
                upcoming_events_list.append(upcoming_event)
        with open("database/valorant/runningEvents.json", "w") as file:
            file.write(json.dumps(ongoing_events_list, indent=4))
        with open("database/valorant/upcomingEvents.json", "w") as file:
            file.write(json.dumps(upcoming_events_list, indent=4))
