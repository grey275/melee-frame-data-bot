import traceback
import sys

import discord

import serviceAccount
import userFacingTree
import NodeStrategies
import config
import logs
import messages


logger = logs.my_logger.getChild(__name__)


class Client(discord.Client):
    """
    Client which finds and parses user commands
    """
    conf = config.Client

    def __init__(self):
        game_msg = discord.Game(name=self.conf.activity_msg)
        super().__init__(activity=game_msg)

    def run(self):
        super().run(self.conf.token)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user.name} "
                    f"| id: {self.user.id}")

    async def on_connect(self):
        """
        redefinition of the on_connect() event object
        method that reloads the cache
        """
        num_guilds = len(self.guilds)
        logger.info('Connected to Discord '
                    f"| Guilds:{self.guilds} "
                    f"| Number of Guilds: {num_guilds}")

    async def on_guild_join(self, guild):
        num_guilds = len(self.guilds)
        logger.info(f'Joined guild {self.guild} '
                    f'| Number of guilds: {num_guilds}')

    async def on_message(self, message):
        """
        Redefinition of the on_message event object.
        Checks to see if command prefix is present.
        """
        if not self._isCommand(message):
            return
        logger.debug("Message {} is Command".format(message))
        await self._handle(message)

    async def on_message_edit(self, before, after):
        """
        Redefinition of library event object.
        Checks to see if the command prefix is present.
        """
        checks = (self._isCommand(after),
                  # before != after
                  )
        if not all(checks):
            return
        await self._handle(after)

    def _isCommand(self, message):
        checks = (message.content.startswith(self.conf.command_prefix),
                  message.author != self.user)
        return all(checks)

    async def _handle(self, msg_obj):
        handler = Handler(msg_obj)
        await handler.query()

    async def on_error(self, event_method, *args, **kwargs):
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()
        logger.exception("Exception:")


class Handler:
    conf = config.Handler
    session = serviceAccount.createSession()
    _tree = userFacingTree.load()

    def __init__(self, msg_obj):
        args, options = self._parse(msg_obj.content)
        response = self._tree.respond(msg_obj, args, options=options)
        self._output, self._behaviors = response
        self._msg_obj = msg_obj

    async def query(self):
        channel = await self._getChannel(self._behaviors.send_dm)
        if self._behaviors.re_load:
            pass
            # Handler._tree = userFacingTree.load()
        if not self._output:
            logger.debug('silent command!')
        await self._send(channel, self._output)
        logger.info(f'Command Handled | msg_obj: {self._msg_obj},'
                    f'command: {self._msg_obj.content}'
                    f'author: {self._msg_obj.author} output: {self._output}')

    def _parse(self, content):
        """
        Parses command string into arguments to search through
        the datastructure with, and options (words prefixed with a -)
        to pass to the response that's returned. The
        command prefix as well as the leading dash on options
        are dropped.
        """
        words = content[len(self.conf.command_prefix):].split()
        args = []
        options = []
        for w in words:
            if w[0] == '-':
                options.append(w[1:])
            else:
                args.append(w)
        return args, options

    async def _getChannel(self, send_dm):
        if self._msg_obj.channel == self._msg_obj.author.dm_channel:
            return self._msg_obj.channel
        if send_dm:
            logger.info(f'dm sent to {self._msg_obj.author}')
            dm_notify = [messages.WrittenMSG("DMNotify").get()]
            await self._send(self._msg_obj.channel, dm_notify)
            return await self._getDMChannel()
        else:
            return self._msg_obj.channel

    async def _send(self, channel, output):
        if not output:
            logger.debug('Silent Command!')
        else:
            logger.debug(f'sending {output}')
            for out in output:
                await channel.send(**out)

    async def _getDMChannel(self):
        """
        return's the author's dm channel with this client,
        creating one if it didn't exist.
        """
        author = self._msg_obj.author
        if not author.dm_channel:
            logger.info(f'new dm channel for {self._msg_obj.author}')
            await author.create_dm()
        channel = author.dm_channel
        return channel


if __name__ == '__main__':
    Client().run()
