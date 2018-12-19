import re
import os

from . import creds
develop = True

CONFIG_DIR = os.path.dirname(__file__)
BOT_DIR = os.path.join(CONFIG_DIR, '../')
ROOT_DIR = os.path.join(BOT_DIR), '../'
TREE_LOC = os.path.join(BOT_DIR, "tree.json")


class ServiceAccount:
    creds = creds.service_account_creds


class Client:
    token = creds.discord_token
    command_prefix = "$d"
    activity_msg = "{} help for Commands".format(command_prefix)


class Handler:
    command_prefix = Client.command_prefix


class UserFacingNode:
    min_match_percent = 80


class Root(UserFacingNode):
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

class Suggest(UserFacingNode):
    suggestion_que_loc = os.path.join(BOT_DIR, 'suggestionQueue.json')

class HelpResponse:
    contrib_list = ["sp99", "cfx"]


class WrittenMSG:
    message_file = os.path.join(os.path.dirname(__file__),
                                "messages.yaml")
