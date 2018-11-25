import traceback
import sys

import discord

import config
import messages

import logs

logger = logs.my_logger.getChild(__name__)


class Client(discord.Client):
    """
    Client which finds and parses user commands
    """
    conf = config.Client

    def __init__(self, data):
        self.data = data
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
                  before != after)
        if not all(checks):
            return
        output = self._query(after)
        await self._send(after.channel, output)

    async def _handle(self, message):
        """
        queries data with command and sends ouptut to either
        the command message's channel or to a DM with the author.
        """
        output, send_dm = self._query(message)
        if send_dm:
            if not message.author.dm_channel:
                logger.info(f'new dm channel for {message.author}')
                await message.author.create_dm()
            logger.info(f'dm sent to {message.author}')
            dm_notify = [messages.WrittenMSG("DMNotify").get()]
            await self._send(message.channel, dm_notify)
            channel = message.author.dm_channel
        else:
            channel = message.channel
        logger.info(f'Command Handled | message: {message},'
                    f'command: {message.content}'
                    f'author: {message.author} output: {output}')
        await self._send(channel, output)

    def _query(self, msg_obj):
        args, options = self._parse(msg_obj.content)

        return self.data.respond(msg_obj, args, options)

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

    def _isCommand(self, message):
        checks = (message.content.startswith(self.conf.command_prefix),
                  message.author != self.user)
        return all(checks)

    async def _send(self, channel, output):
        if not output:
            logger.debug('Silent Command!')
        for out in output:
            await channel.send(**out)

    async def on_error(self, event_method, *args, **kwargs):
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()
        logger.exception()
