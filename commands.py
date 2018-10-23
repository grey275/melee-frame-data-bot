import yaml
import re

from dataclasses import dataclass

import fuzzywuzzy

from main import main

def parse(self, msg_string):
    """
    parses and executes command
    """
    if not msg_string:
        return self.getMessage("No-Command")
    user_command, *user_args = 
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


class Command():
    def __init__(self, key, options, func):
        self.key = key
        self.options = options
        self.func = func


class Messages(dict):

    def __init__(self, message_file):
        self._raw = self._fetchRawMsgs(message_file)

    def _buildMessages(self):
        for key, data in self._raw.items():
            self.[key] = Message(key, data['str'], data['req_info'])

    def _fetchRawMsgs(self, message_file):
        with open(message_file, 'r') as f:
            raw_msgs = yaml.load(f.read())
        return raw_msgs


class Message:

    def __init__(self, name, raw_str): 
        # super(Message, self).__init__()
        self.name = name
        self.raw_str = raw_str
        self.req_info = self.findReqInfo(raw_str)

    def findReqInfo(self, raw_str):
        re.findall{""}

class Commands(dict):

    def add(self, command):
        assert isinstance(command, Command)
        self.[command.key] = command

    def match(self, user_command, command, min_match_rate):
        match, match_rate = fuzzywuzzy.process.extractOne(user_command,
                                                          self.keys())
        if match_rate < min_match_rate:
            return Message()

class UserCommand:
    commands = Commands()

    def __init__(self, message):
        self.user_key, self.user_option = self.parse(message.content())

    def _parse(self, com_string):
        return [w.replace("_", " ") for w in msg_string.split()]

    def _match(self):


def fetchMessages(message_file):
    with open(message_file, 'r') as f:
        messages = yaml.load(f.read())
    return messages
