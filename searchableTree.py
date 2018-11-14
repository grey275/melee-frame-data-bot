from fuzzywuzzy import process

from config import Config
from messages import Message
from response import Response

class SearchableTree(Response):
    """
    contains dictionary which points to a bunch of possible responses
    to a user query, and matches a response with match().
    """

    min_match = Config.min_match_percent

    def __init__(self):
        """
        options holds other Response objects, and
        output holds any actual content to be displayed."""
        super().__init__()
        self._children: dict()

    def match(self, guess, args):
        """
        Searches the tree based on user input.
        This method is indirectly recursive, in
        that it accesses itself from other instance
        objects."""
        match, rate = process.extractOne(guess,
                                         self._children.keys())
        if rate < self.min_match:
            not_found_msg = Message("MatchNotFound",
                                     guess=guess,
                                     category=self._name,
                                     closest_match=match,
                                     match_rate=rate)

            return not_found_msg

        if args:
            guess, *args = args
            return self._children[match].match(guess, args)
        else:
            return self._children[match]
