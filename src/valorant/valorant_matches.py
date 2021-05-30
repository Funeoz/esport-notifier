import json
import requests
import datetime
from bs4 import BeautifulSoup, NavigableString


class ValorantMatches(object):
    def __init__(self):
        pass

    def get_past_matches(self):
        """Get the last 3 days matches and results"""
        page = BeautifulSoup(
            requests.get(
                "https://www.vlr.gg/matches/results",
                headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            ).text,
            "lxml",
        )

        matches = page.find("div", {"class": "col-container"})
        matches_list = []
        for match in matches.find_all("div", {"class": "wf-card"})[1:]:
            for item in match.find_all("a"):
                if (
                    item.find("div", {"class": "match-item-vs"})
                    .find_all("div")[3]
                    .text.strip()
                    .replace("\u2013", "-")
                    != "-"
                    and item.find("div", {"class": "match-item-vs"})
                    .find_all("div")[7]
                    .text.strip()
                    .replace("\u2013", "-")
                    != "-"
                ):
                    if int(
                        item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[3]
                        .text.strip()
                    ) > int(
                        item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[7]
                        .text.strip()
                    ):
                        winner = (
                            item.find("div", {"class": "match-item-vs"})
                            .find_all("div")[2]
                            .text.strip()
                        )
                    elif int(
                        item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[3]
                        .text.strip()
                    ) < int(
                        item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[7]
                        .text.strip()
                    ):
                        winner = (
                            item.find("div", {"class": "match-item-vs"})
                            .find_all("div")[6]
                            .text.strip()
                        )
                    else:
                        winner = None
                else:
                    winner = None
                original_date = datetime.datetime.strptime(
                    match.find_previous_sibling("div")
                    .text.replace("Today", "")
                    .replace("Yesterday", "")
                    .strip(),
                    "%a, %B %d, %Y",
                )
                converted_date = original_date.strftime("%Y-%m-%d")
                newmatch = {
                    "date": converted_date,
                    "team1": {
                        "name": item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[2]
                        .text.strip(),
                        "score": item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[3]
                        .text.strip()
                        .replace("\u2013", "n/a"),
                    },
                    "team2": {
                        "name": item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[6]
                        .text.strip(),
                        "score": item.find("div", {"class": "match-item-vs"})
                        .find_all("div")[7]
                        .text.strip()
                        .replace("\u2013", "n/a"),
                    },
                    "winner": winner,
                    "event": "".join(
                        item.find(
                            "div", {"class": "match-item-event text-of"}
                        ).find_all(text=True, recursive=False)
                    ).strip(),
                }
                matches_list.append(newmatch)
        with open("database/valorant/pastMatches.json", "w") as file:
            file.write(json.dumps(matches_list, indent=4))
