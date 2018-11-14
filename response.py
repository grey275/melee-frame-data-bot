import yaml
import discord

from fuzzywuzzy import process

from config import Config


class Response:
    """
    Describes a response to a user query, Usually just a message,
    but might change the state of the program somehow."""

    def __init__(self):
        self._name: str
        self._output = list()

    def respond(self):
        """
        Redefinition of this method later will allow for
        commands to change the state of the program."""
        return self._output

    def _formatOutputList(self, lst):
        *most, last = lst
        return "".join(["{}, ".format(c) for c in most] + [last])

    def _makeEmbedOBJ(self, fields, **embed_info):
        """
        Constructs a discord embed object for display.
        """
        embed = discord.Embed(fields=[], **embed_info)
        for field in fields:
            embed.add_field(**field)
        return embed
