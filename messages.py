import logging
import yaml

import discord

import config

logger = logging.getLogger(__name__)
logger.propagate


class WrittenMSG:
    """
    Handwritten messages for the user.
    """
    config = config.WrittenMSG

    def _fetchRawMsgs(message_file):
        with open(message_file, 'r') as f:
            msg_dict = yaml.load(f.read())
        return msg_dict

    _raw_msgs = _fetchRawMsgs(config.message_file)

    def __init__(self, key, **info):
        msg = self._raw_msgs[key]
        self._info = info
        assert msg is not None
        if info:
            msg = self._format(msg)
        if "embed" in msg:
            embed = discord.Embed(**msg["embed"])
            for field in msg["embed"]["fields"]:
                embed.add_field(**field)
            msg["embed"] = embed
        self._msg = msg

    def get(self):
        return self._msg

    def _format(self, msg):
        """
        Calls format(self._info) on all strings with self._info
        in potentially nested list, dict or str.
        """
        if isinstance(msg, str):
            return self._formatText(msg)
        elif isinstance(msg, list):
            return self._formatList(msg)
        elif isinstance(msg, dict):
            return self._formatDict(msg)
        else:
            raise TypeError("Invalid type:{}".format(type(msg)))


    def _formatDict(self, dct):
        """
        Recursively applies format(**info) to all strings in a dict.
        Embed objects can be constructed from a dict.
        """
        for key, val in dct.items():
            if val is None:
                breakpoint()
            dct[key] = self._format(val)
        return dct

    def _formatList(self, lst):
        """
        Formats all text in list.
        """
        return [self._format(txt) for txt in lst]

    def _formatText(self, txt):
        return txt.format(**self._info)
