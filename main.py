#!/usr/bin/pipenv run
from client import MyDiscordClient
from config import Config

client = MyDiscordClient()

client.run(Config.discord_token)
