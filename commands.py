import yaml
import re
import math

from collections import namedtuple
from types import FunctionType
from dataclasses import dataclass


import discord
import tablib
import fuzzywuzzy

from main import main




@dataclass
class Command:

    key: str
    func: FunctionType
    valid_args: set

    def execute(self, args):
        assert arg in self.valid_args
        return self.func(self, arg)


class UserQuery:
    def __init__(self, message):

        usr_str = message.content[main.Config.command:]
        self.args = self._parse(usr_str)

    def _parse(self, usr_str):
        return tuple(w.replace("_", " ") for w in usr_str.split())


class Messages(dict):

    def __init__(self, message_file="messages.yaml"):
        super(Messages, self).__init__()

        msg_dict = self._fetchRawMsgs(message_file)
        self._buildMessages(msg_dict)

    def _buildMessages(self, msg_dict):
        for key, raw_msg in msg_dict.items():
            self[key] = Message(key, raw_msg)

    def _fetchRawMsgs(self, message_file):
        with open(message_file, 'r') as f:
            msg_dict = yaml.load(f.read())
        return msg_dict


class Message:

    def __init__(self, key, raw_msg):
        self.key = key
        self.raw_msg = raw_msg
        self.req_info = self._findReqInfo(raw_msg)

    def _findReqInfo(self, msg):
        matches = re.findall("\{\w+\}", msg)
        return {m[1:-1] for m in matches}
