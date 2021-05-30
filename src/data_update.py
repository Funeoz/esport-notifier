from csgo.csgo_matches import CsgoMatches
from csgo.csgo_events import CsgoEvents
from csgo import csgo_ranking
from valorant.valorant_events import ValorantEvents
from valorant.valorant_matches import ValorantMatches
from r6siege.r6siege_matches import R6siegeMatches
from r6siege.r6siege_events import R6siegeEvents
from lol.lol_matches import LolMatches
from lol.lol_events import LolEvents
from dota2.dota2_matches import Dota2Matches
from dota2.dota2_events import Dota2Events
import dota2.dota2_ranking as dota2_ranking
import lol.lol_ranking as lol_ranking

# from valorant import ranking as valorant_ranking


def update_all_data():
    print("Updating events")
    # Update CSGO events
    csgo_events = CsgoEvents()
    csgo_events.get_past_events()
    csgo_events.get_running_events()
    csgo_events.get_upcoming_events()
    # Update Valorant events
    valorant_events = ValorantEvents()
    valorant_events.get_ongoing_upcoming_events()
    valorant_events.get_past_events()
    # Update LOL Events
    lol_events = LolEvents()
    lol_events.get_past_events()
    lol_events.get_running_events()
    lol_events.get_upcoming_events()
    # Update Dota2 Events
    dota2_events = Dota2Events()
    dota2_events.get_past_events()
    dota2_events.get_running_events()
    dota2_events.get_upcoming_events()
    # Update R6Siege Events
    r6siege_events = R6siegeEvents()
    r6siege_events.get_past_events()
    r6siege_events.get_running_events()
    r6siege_events.get_upcoming_events()
    print("Updating matches")
    # Update CSGO matches
    csgo_matches = CsgoMatches()
    csgo_matches.get_running_matches()
    csgo_matches.get_past_matches()
    csgo_matches.get_upcoming_matches()
    # Update Valorant matches
    valorant_matches = ValorantMatches()
    valorant_matches.get_past_matches()
    # Update LOL Matches
    lol_m = LolMatches()
    lol_m.get_past_matches()
    lol_m.get_running_matches()
    lol_m.get_upcoming_matches()
    # Update Dota2 Matches
    dota2_m = Dota2Matches()
    dota2_m.get_past_matches()
    dota2_m.get_running_matches()
    dota2_m.get_upcoming_matches()
    # Update R6Siege Matches
    r6siege_m = R6siegeMatches()
    r6siege_m.get_past_matches()
    r6siege_m.get_running_matches()
    r6siege_m.get_upcoming_matches()
    print("Updating rankings")
    csgo_ranking.get_world_ranking()
    dota2_ranking.get_world_ranking()
    lol_ranking.get_world_ranking()
