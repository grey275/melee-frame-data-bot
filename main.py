import asyncio
import json
import os
import requests

from fuzzywuzzy import process
from googleapiclient.discovery import build
from httplib2 import Http

# https://drive.google.com/open?id=11i-YwUajgc6aWD8wSetYrb_bAM4RmL4FZi8XdBrMHo8


class Sheets:
    """
    Class for getting sheet data, parsing it to allow for faster and simpler data retrieval,
    and storing as a json in a chosen location.
    """
    def __init__(self, spreadsheet_ID, google_API_key):
        """
        Just initializing variables. These shouldn't be modified later.
        """
        self.SSID = spreadsheet_ID
        self.APIKey = google_API_key
        self.sheet_names = ["Fox", "Falco", "Marth", "Sheik", "Jigglypuff", "Peach",
                            "Ice Climbers", "Captain Falcon", "Pikachu", "Samus",
                            "Template", "Universal Data", "helpme"]

        self.dict_data = self.get()

    def get(self):
        """
        Performs the class's main functionality.
        Retrieves data, parses, and writes to a json file.
        """
        valueRanges = self.fetchDataFromSheet()
        return self.parseCharacterData(valueRanges)

    def fetchDataFromSheet(self):
        """
        gets data from the google api. Returns a list of valueRanges for the
        spreadsheets
        """
        service =  build('sheets', 'v4', developerKey=self.APIKey)
        request = service.spreadsheets().values().batchGet(spreadsheetId=self.SSID,
                                                           ranges=self.sheet_names)
        # print("got data")
        return request.execute().get("valueRanges")


    def parseCharacterData(self, valueRanges):
        """
        parses character data into more workable form
        and returns resulting dict
        """
        #TODO add methods for other character data

        sheet_dict = dict()
        characters = self.sheet_names[:-3]
        character_data = valueRanges[:-3]
        for i, d in enumerate(character_data):
            sheet_dict[characters[i]] = self.addMoves(d["values"],
                                                      characters[i])
        return sheet_dict


    def addMoves(self, char_data, char_name):
        """
        structures a character's moves as a dict and stores the result
        of calling embed on each move, the range 2:10 is the range of
        the move columns. There is move info from row 3 to the end.
        """
        moves = dict()
        labels = char_data[2][2:10]
        for y in range(3, len(char_data)):
            move_name = char_data[y][1]
            data = char_data[y][2:10]
            moves[move_name] = self.embed(data, labels,
                                          char_name, move_name)
        return moves

    def embed(self, data, labels, char_name, move_name):
        """
        Transforms move data into a form that works with discord.embed,
        and calls makeEmbedOBJ on the result. 
        """
        move_dict = dict()
        move_dict["title"] = "{}'s {}".format(char_name, move_name)
        move_dict["fields"] = self.addFields(data, labels)
        return self.makeEmbedOBJ(move_dict)

    def addFields(self, data, labels):
        """
        Turns the input data into a list of fields to be used
        in the embed object.
        """
        fields = []
        for i, v in enumerate(data):
            if v == '-':
                continue
            d = dict()
            d["name"] = labels[i]
            d["value"] = v
            fields.append(d)
        return fields

    def makeEmbedOBJ(self, data):
        """
        Makes an embed obj out of a move's embed-ready data.
        """
        embed = discord.Embed(title=data["title"])
        fields = data["fields"]
        for f in fields:
            embed.add_field(name=f["name"], value=f["value"])
        return embed

class Config:

    def __init__(self, config_location="config.json"):
        with open(config_location) as f:
            config_dict = json.loads(f.read())

        self.api_key = config_dict["google_api_key"]
        self.discord_token = config_dict["discord_token"]

        self.sheet_url = config_dict["sheet_url"]
        self.sheet_id = self.getSpreadsheetID(self.sheet_url)

    def getSpreadsheetID(self, url):
        start = re.search("id\=", url).end()
        return url[start:]


class Command:

    def __init__(self, sheets, min_match_rate=80):
        """
        none of these variables will change
        """
        self.sheet_names = sheets.sheet_names
        self.refresh_cache = sheets.get
        self.dict_data = sheets.dict_data

        self.special_commands = {"refresh": [self.refresh_cache, {}],
                                 "help": [self.getHelpMessage, {}],
                                 "test": [self.test, {}],
                                 "listCharacters": [self.listCharacters, {}],
                                 "listMoves": [self.listMoves, set(self.sheet_names)]}

        self.error_file = "errors.json"
        self.error_messages = self.fetchErrorMessages()

        self.min_match_rate = min_match_rate



    def execute(self, msg_string):
        """
        parses and executes command
        """
        if not msg_string:
            return self.getErrorMessage("No-Command")
        user_command, *user_args = [w.replace("_", " ") for w in msg_string.split()]
        #finds matches in case command is a special or move info command
        character_match_info = self.matchCommand(user_command,
                                                 self.dict_data.keys())
        special_match_info = self.matchCommand(user_command,
                                               self.special_commands.keys())
        character_match_rate = character_match_info[0]
        special_match_rate = special_match_info[0]

        # move commands and special commands are handled differently.
        if character_match_rate > special_match_rate:
            info = character_match_info
            is_special = False
        else:
            info = special_match_info
            is_special = True

        if info[1] == "No-Such-Command":
            error_message = info[2]
            return error_message

        else:
            # print(is_special)
            return self.getCommand(info, user_args, is_special)

    def matchCommand(self, user_command, valid_commands):
        """
        matches command to a valid command, or returns an error message if the
        command doesn't match sufficiently with any valid command.
        """
        # print("user command: {}\nvalid commands: {}".format(user_command, valid_commands))
        match, match_rate = process.extractOne(user_command, valid_commands)
        if match_rate < self.min_match_rate:
            # print("not found!")
            error = "No-Such-Command"
            error_message = self.getErrorMessage(error=error,
                                                 user_command=user_command,
                                                 matched_command=match,
                                                 match_rate=match_rate)
            return match_rate, error, error_message

        return match_rate, match

    def getCommand(self, info, user_args, is_special):
        matched_command = info[1]

        if is_special:
            valid_args = self.special_commands[matched_command][1]
        else:
            valid_args = self.dict_data[matched_command].keys()


        if not user_args:
            if not valid_args:
                if is_special:
                    return self.special_commands[matched_command][0]()
                raise Exception("No valid args for {}!".format(matched_command))
            return self.getErrorMessage(error="Requires-Arg",
                                        matched_command=matched_command)
        if not valid_args:
            return self.getErrorMessage(error="No-Arg-Taken",
                                        matched_command=matched_command)

        num_user_args = len(user_args)
        # Right now all commands only take 1 argument. If that's ever not
        # the case this needs to be updated.
        if num_user_args > 1:
            return self.getErrorMessage(error="Wrong-Number-Of-Args",
                                        matched_command=matched_command,
                                        expected_num_args=1,
                                        num_user_args=num_user_args,)
        user_arg = user_args[0]
        #print("user arg:{}".format(user_arg))
        matched_arg, error_message = self.matchArg(matched_command,
                                                   valid_args, user_arg)
        if not matched_arg:
            return error_message
        if is_special:
            return self.special_commands[matched_command][0](matched_arg)

        return self.dict_data[matched_command][matched_arg]


    def matchArg(self, matched_command, valid_args, user_arg):
        #print("valid args: ".format(valid_args))
        match, match_rate = process.extractOne(user_arg, valid_args)
        if match_rate < self.min_match_rate:
            error = "No-Such-Argument"
            error_message = self.getErrorMessage(error, user_arg=user_arg,
                                                 matched_command=matched_command,
                                                 matched_arg=match)
            return False, error_message

        #print("arg match: {}".format(match))
        return match, False

    def fetchErrorMessages(self):
        with open(self.error_file) as f:
            return json.loads(f.read())

    def getErrorMessage(self, error, **info):
        message = self.error_messages[error]
        return message.format(**info)

    def test(self):
        return self.dict_data["Falco"].keys()

    def getHelpMessage(self):
        with open("help.md", "r") as f:
            message = f.read()
        return message

    def listCharacters(self):
        return self.formatOutputList(self.sheet_names[:-3])

    def listMoves(self, matched_character):
        lst = list(self.dict_data[matched_character].keys())
        return self.formatOutputList(lst)
    # TODO format with embed instead and categorize by move type

    def formatOutputList(self, lst):
        allbutlast =  "".join(["{}, ".format(e) for e in lst])
        last = "{}.".format(lst[-1])
        return allbutlast + last

def main():
    conf = Config()

    sheets = Sheets(spreadsheet_ID=conf.sheet_id,
                    google_API_key=conf.api_key)

    command = Command(sheets)
    client = discord.Client()

    @client.event
    async def on_connect():
        """
        redefinition of the on_connect() event object
        method that reloads the cache
        """
        nonlocal client
        nonlocal sheets
        print("We're Online! user = {0.user}".format(client))


    @client.event
    async def on_message(message):
        """
        Redefinition of the on_message event object
        which carries out user commands.
        the argument 'message' in the function definition is the newly
        received message.
        """
        nonlocal command
        if message.author == client.user:
            return
        if message.content.startswith("$fd"):
            response = command.execute(message.content[3:])
            #print("response!")
            if type(response) == discord.embeds.Embed:
                await message.channel.send(embed=response)
            else:
                await message.channel.send(response)

    client.run(conf.discord_token)

if __name__ == "__main__":
    main()
