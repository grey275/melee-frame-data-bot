import re

from userCredentials import Creds


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
        "Sheik",
        "Jigglypuff",
        "Peach",
        "Ice Climbers",
        "Captain Falcon",
        "Pikachu",
        "Samus",
    }
