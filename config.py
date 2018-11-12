import re

from credentials import Creds


class Config(Creds):
    """
    General Configuration.
    Inherits credentials from userCredentials.py
    """

    command_prefix = "$d"

    sheet_url = "https://docs.google.com/spreadsheets/d/12dwtMFdi95l03npBFuWI0fK62V0QZ6xET3qJ4oVdGc0&edit#gid=1165995726"

    sheet_id = re.search("id\=", sheet_url).end()

    message_file = "messages.yaml"

    min_match_percent = 80

    character_names = {
        "Fox",
        "Falco",
        "Marth",
        }

        #"Sheik",
        #"Jigglypuff",
        #"Peach",
        #"Ice Climbers",
        #"Captain Falcon",
        #"Pikachu",
        # "Samus",
    discord_activity_msg = "{} help for Commands".format(command_prefix)
    contributor_list = ["sp99", "cfx"]
    invite_link = "https://discordapp.com/oauth2/authorize?client_id=492378733399900169&scope=bot&permissions=67584"
