"""
Entry point. Run this module from '../run'.
"""
import traceback
import sys

import discord

from . import config
from . import logs
from . import handler


logger = logs.my_logger.getChild(__file__)


class Client(discord.Client):
    """
    Client which finds and handles user commands via
    the handler module.
    """
    conf = config.Client

    def __init__(self):
        """
        Passes in the activity message from config, which just
        explains how to call the help message for more info.
        """
        game_msg = discord.Game(name=self.conf.activity_msg)
        super().__init__(activity=game_msg)

    def run(self):
        super().run(self.conf.token)

    async def on_ready(self):
        """
        For logging purposes only.
        """
        logger.info(f"Logged in as {self.user.name} "
                    f"| id: {self.user.id}")

    async def on_connect(self):
        """
        For logging purposes only.
        """
        num_guilds = len(self.guilds)
        logger.info('Connected to Discord '
                    f"| Guilds:{self.guilds} "
                    f"| Number of Guilds: {num_guilds}")

    async def on_guild_join(self, guild):
        """
        For logging purposes only.
        """
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
        await handler.handle(message)

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
        await handler.handle(after)

    def _isCommand(self, message):
        """
        Initial validation. Further validation is done by the handler
        and in the sequence of UserFacingNode objects which will
        process this command.
        """
        checks = (message.content.startswith(self.conf.command_prefix),
                  message.author != self.user)
        return all(checks)

    async def on_error(self, event_method, *args, **kwargs):
        """
        For logging purposes only
        """
        logger.debug('Ignoring exception in {}'.format(event_method), file=sys.stderr)
        traceback.print_exc()
        logger.exception("Exception:")
