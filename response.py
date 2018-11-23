from messages import WrittenMSG


class Response:
    """
    Describes a possible response to a user query, which is by default just
    sending a list of dicts representing discord messages to the channel
    the query came from.
    """
    def __init__(self, name, dm=False):
        """
        If dm is true, the client will direct message the user instead.
        """
        self.name = name
        self._dm = dm
        self._output = list()

    def respond(self, usr_msg_obj, *args):
        """
        Redefinition of this method later will allow for
        commands to change the state of the program.
        """
        self._action(usr_msg_obj, *args)
        if args:
            error = WrittenMSG("NoArgTaken", name=self.name).get()
            return [error], self._dm
        else:
            return self._output, self._dm

    def _action(self, usr_msg_obj, *args):
        """
        Executed during a call to respond.
        """
        pass

    def _formatOutputList(self, lst):
        """
        formats a list of elements into a string to be
        displayed to the user directly.
        """
        *most, last = lst
        return "".join(["{}, ".format(c) for c in most] + [last])


class ListResponse(Response):

    def __init__(self, name, lst, dm=False):
        super().__init__(name, dm)
        msg = self._formatOutputList(lst)
        self._output.append({"content": msg})


class WrittenResponse(Response):
    def __init__(self, key, dm=False, **info):
        super().__init__(key, dm)
        msg = WrittenMSG(key, **info).get()
        self._output.append(msg)
