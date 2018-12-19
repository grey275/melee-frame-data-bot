import json

import messages
import config


class Response:
    """
    Describes a possible response to a user query, which is by default just
    sending a list of dicts representing discord messages to the channel
    the query came from.
    """
    def __init__(self, node):
        """
        If dm is true, the client will direct message the user instead.
        """
        self.name = name
        self._output = list()
        self._send_dm_default = send_dm_default

    def respond(self, msg_obj, args, options):
        """
        Responds to a discord message
        """

        send_dm = self._checkOptions(options)
        if args:
            return self._handleArgs(self, args, send_dm, options)

        return self._output, send_dm

    def _handleArgs(self, msg_obj, args, send_dm, options):
        return messages.WrittenMSG("NoArgTaken", name=self.name).get(), send_dm

    def _formatOutputList(self, lst):
        """
        formats a list of elements into a string to be
        displayed to the user directly.
        """
        *most, last = lst
        return "".join(["{}, ".format(c) for c in most] + [last])


class ListResponse(Response):

    def __init__(self, name, lst, send_dm=False):
        super().__init__(name, send_dm)
        msg = self._formatOutputList(lst)
        self._output.append({"content": msg})


