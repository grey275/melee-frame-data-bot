from .. import messages
from .basic import Basic


class Response(Basic.Response):
    def __init__(self, output, msg_obj, options=None, **kwargs):
        self._output = output
        self._msg_obj = msg_obj
        self._options = options
        self._notification = messages.WrittenMSG('DMNotify').get()

    async def execResponse(self):
        if self._options is not None and 'nodm' in self._options:
            await self._send(self._output, self._msg_obj.channel)
        else:
            await self._sendDM()

    async def _sendDM(self):
        author = self._msg_obj.author
        if not author.dm_channel:
            await author.create_dm()
        await self._send(self._output,
                         self._msg_obj.author.dm_channel)
        await self._send(self._notification,
                         self._msg_obj.channel)


class DMInstead(Basic):
    Response = Response
