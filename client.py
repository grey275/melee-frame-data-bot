import discord

import serviceAccount
import sheets
import messages

from config import Config


class MyDiscordClient(discord.Client):
    """
    Client which handles discord events
    """
    command_prefix = Config.command_prefix
    activity_msg = Config.discord_activity_msg

    def __init__(self):
        """
        All main objects are instantiated here to
        be referenced during events.
        """
        game_msg = discord.Game(name=self.activity_msg)
        super().__init__(activity=game_msg)
        session = serviceAccount.createSession()
        self.data = sheets.AllStructuredData(session)

    async def on_ready(self):
        print('Logged in as')
        print(self.user.id)
        print(self.user.name)
        print('------')

    async def on_connect(self):
        """
        redefinition of the on_connect() event object
        method that reloads the cache
        """
        print("We're Online!".format())

    async def on_message(self, message):
        """
        Redefinition of the on_message event object.
        Checks to see if command prefix is present.
        """
        if not self._isCommand(message):
            return
        output = self._query(message.content)
        for out in output:
            await message.channel.send(**out)

    async def on_message_edit(self, before, after):
        """
        Redefinition of library event object.
        Checks to see if the command prefix is present.
        """
        checks = (self._isCommand(after),
                  before != after)
        if not all(checks):
            return
        output = self._query(after.content)
        for out in output:
            await after.channel.send(**out)

    def _query(self, content):
        all_args = self._parse(content)
        if not all_args:
            return messages.NO_COMMAND

        guess, *args = all_args
        return self.data.match(guess, args)

    def _parse(self, content):
        return content[len(self.command_prefix):].split()

    def _isCommand(self, message):
        checks = (message.content.startswith(self.command_prefix),
                  message.author != self.user)
        return all(checks)
