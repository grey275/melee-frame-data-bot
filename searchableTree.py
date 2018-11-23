import logging

from fuzzywuzzy import process

import config

from messages import WrittenMSG
from response import Response

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)

class SearchableTree(Response):
    """
    Abstract class for classes which contain dictionary which points to
    a bunch of possible responses to a user query, and matches a response
    with respond().
    """

    conf = config.SearchableTree

    def __init__(self, name, dm=False):
        """
        options holds other Response objects, and
        output holds any actual content to be displayed.
        """
        super().__init__(name, dm)
        self._children = dict()

    def respond(self, usr_msg_obj, *args):
        if args:
            return self._match(usr_msg_obj, *args)
        elif not self._output:
            error = WrittenMSG("RequiresArg",
                               name=self.name,
                               valid_args=self._children.keys())
            return [error.get()]
        else:
            return self._output, self._dm

    def _match(self, msg_obj, guess, *args):
        """
        Searches the tree based on user input.
        This method is indirectly recursive, in
        that it accesses itself from other instance
        objects."""
        match, rate = process.extractOne(guess, self._children.keys())
        if rate < self.conf.min_match_percent:
            not_found_msg = WrittenMSG("MatchNotFound",
                                       guess=guess,
                                       category=self.name,
                                       closest_match=match,
                                       match_rate=rate)

            return [not_found_msg.get()]

        return self._children[match].respond(msg_obj, *args)
