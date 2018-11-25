import re

from credentials import Creds

develop = True


class ServiceAccount:
    creds = Creds.service_account_creds


class Client:
    token = Creds.discord_token
    command_prefix = "$d"
    activity_msg = "{} help for Commands".format(command_prefix)


class SearchableTree:
    min_match_percent = 80


class AllStructuredData(SearchableTree):
    sheet_url = "https://docs.google.com/spreadsheets/d/12dwtMFdi95l03npBFuWI0fK62V0QZ6xET3qJ4oVdGc0&edit#gid=1165995726"

    sheet_id = re.search("id\=", sheet_url).end()
    char_names = {
        "Fox",
        # "Falco",
        # "Marth",
        # "Samus",
        # "Sheik",
        # "Jigglypuff",
        # "Peach",
        # "Ice Climbers",
        # "Captain Falcon",
        # "Pikachu",
        # "Samus",
        # "Yoshi"
        }
    contrib_list = ["sp99", "cfx"]
    invite_link = "https://discordapp.com/oauth2/authorize?client_id=492378733399900169&scope=bot&permissions=67584"

class HelpResponse:
    contrib_list = ["sp99", "cfx"]


class WrittenMSG:
    message_file = "messages.yaml"




