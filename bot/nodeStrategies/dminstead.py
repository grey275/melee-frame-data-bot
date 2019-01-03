from .. import messages
from .basic import Basic


class Response(Basic.Response):
    """
    All that is changed here is sending the static output to
    the user's dm channel, with only a message to explain to other
    users what happened.
    """
    def __init__(self, output, msg_obj, options=None, **kwargs):
        self._output = output
        self._msg_obj = msg_obj
        self._options = options
        self._notification = messages.WrittenMSG('DMNotify').get()

    async def execResponse(self):
        """
        Checks for an option 'nodm' which would negate this
        node's special behaviour.
        """
        if self._options is not None and 'nodm' in self._options:
            await self._send(self._output, self._msg_obj.channel)
        else:
            await self._sendDM()

    async def _sendDM(self):
        """
        If a dm channel does not exist with this user yet, we need
        to create a new one.
        """
        author = self._msg_obj.author
        if not author.dm_channel:
            await author.create_dm()
        await self._send(self._output,
                         self._msg_obj.author.dm_channel)
        await self._send(self._notification,
                         self._msg_obj.channel)


# Inheritance because lazy
class DMInstead(Basic):
    Response = Response
