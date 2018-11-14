import yaml

import discord

from response import Response
from config import Config

class Message(Response):
    """
    Handwritten messages for the user.
    """
    def _fetchRawMsgs(message_file):
        with open(message_file, 'r') as f:
            msg_dict = yaml.load(f.read())
        return msg_dict


    _raw_msgs = _fetchRawMsgs(Config.message_file)

    def __init__(self, key, **info):
        super().__init__()
        raw_msg = self._raw_msgs[key]
        self._output = list()
        if isinstance(raw_msg, str):
            self._output.append({"content": raw_msg.format(**info)})
        else:
            embed_info = dict()
            fields = []
            for k, v in raw_msg.items():
                if k == "fields":
                    fields = v
                    print("fields found")
                else:
                    embed_info[k] = v
            self._output.append({"embed": self._makeEmbedOBJ(fields=fields, **embed_info)})

    def _addInfo(self, raw_msg, info):
        pass

class PreBuiltMsgs:
    help_msg = Message("Help", contributor_list=Config.contributor_list)
    no_command_msg = Message("NoCommand")
    info_msg = Message("Info")
    invite_msg = Message("Invite")
