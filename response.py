import discord

import messages

from fuzzywuzzy import process

from config import Config


class Response:
    """
    Responses make up every function
    and piece of data that the user can access.
    A tree of responses is searched by the user
    with match.
    """

    min_match = Config.min_match_percent

    def __init__(self):
        """
        options holds other Response objects, and
        output holds any actual content to be displayed."""
        self._name: str
        self._children = dict()
        self.output = list()

    def match(self, guess, args):
        """
        Searches the tree based on user input.
        This method is indirectly recursive, in
        that it accesses itself from other instance
        objects."""
        if self._children:
            match, rate = process.extractOne(guess,
                                             self._children.keys())
            if rate < self.min_match:
                return messages.build("MatchNotFound",
                                      guess=guess,
                                      category=self._name,
                                      closest_match=match,
                                      match_rate=rate)
            if args:
                guess, *args = args
                return self._children[match].match(guess, args)
            else:
                return self._children[match].output

        return messages.build("NoArgTaken",
                              name=match)

    def _makeEmbedOBJ(self, fields=[], **embed_info):
        embed = discord.Embed(**embed_info)
        for field in fields:
            embed.add_field(**field)
        return embed

    def _formatOutputList(self, lst):
        *most, last = lst
        return "".join(["{}, ".format(c) for c in most] + [last])
