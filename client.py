import traceback
import sys

import discord

import config

import logs

logger = logs.my_logger.getChild(__name__)

class Client(discord.Client):
    """
    Client which finds and parses user commands
    """
    conf = config.Client

    def __init__(self, data):
        """
        All main objects are instantiated here to
        be referenced during events.
        """
        self.data = data
        game_msg = discord.Game(name=self.conf.activity_msg)
        super().__init__(activity=game_msg)

    def run(self):
        super().run(self.conf.token)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user.name}\n"
                    f"id: {self.user.id}\n"
                    f"------")

    async def on_connect(self):
        """
        redefinition of the on_connect() event object
        method that reloads the cache
        """
        logger.info("Connected to Discord")

        guild_msg = f"Guilds: {self.guilds}"
        guild_num_msg = "Number of Guilds: {}".format(len(self.guilds))

        logger.debug("We're Online!")
        logger.info(f"{guild_msg}\n{guild_num_msg}")

    async def on_guild_join(self, guild):
        num_guilds = len(self.guilds)
        logger.info(f"Joined guild {num_guilds}.\n ")

    async def on_message(self, message):
        """
        Redefinition of the on_message event object.
        Checks to see if command prefix is present.
        """
        if not self._isCommand(message):
            return
        logger.debug(f"Command Recieved: {message}")
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
        logger.debug("Command Recieved: {}")
        output = self._query(after)
        await self._send(after.channel, output)

    async def _handle(self, message):
        output, send_dm = self._query(message)
        if send_dm:
            if not message.author.dm_channel:
                await message.author.create_dm()
            channel = message.author.dm_channel
            logger.debug(f"Sending output to {channel}")
        else:
            channel = message.channel
            logger.debug(f"Sending output to {channel}")
        await self._send(channel, output)

    def _query(self, msg_obj):
        args = self._parse(msg_obj.content)

        return self.data.respond(msg_obj, *args)

    def _parse(self, content):
        return content[len(self.conf.command_prefix):].split()

    def _isCommand(self, message):
        checks = (message.content.startswith(self.conf.command_prefix),
                  message.author != self.user)
        return all(checks)

    async def _send(self, channel, output):
        if not output:
            logger.debug("Silent commmand!")
        for out in output:
            await channel.send(**out)

    async def on_error(self, event_method, *args, **kwargs):
        print('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()
        logger.exception("Exception:")
