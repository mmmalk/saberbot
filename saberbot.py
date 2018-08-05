#!/usr/bin/python3
from discord.ext import commands
import discord
import datetime, asyncio
import os, configparser

def main(config_file):
    """calls method to load the .ini/yaml-style config, then spawns new instance of bot and starts it"""
    config = configparser.ConfigParser()
    config.read(config_file)
    bot=SaberBot(description=config["saberbot"]["desc"])
    bot.run(config["saberbot"]["oauth"])

class SaberBot(commands.Bot):
    """the main class that contains the bot"""
    def __init__(self, **kwargs):
        super().__init__(command_prefix=self.get_prefix_, description=desc)
        self.start_time=None
        self.__version__ = "0.1.0"
        self.loop.create_task(self.track_start()) #unused yet, will be used for timing stuff
        self.loop.create_task(self.load_extensions())

    def get_version(self):
        return self.__version__
    
    async def get_prefix_(self, bot, message):
        """defines the prefixes used for commands
        prefix = list[string] or when mentioned"""
        prefix = ["!", "?", "."]
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def track_start(self):
        """logs the starting moment as datetime object as an start_time attribute"""
        await self.wait_until_ready()
        self.start_time=datetime.datetime.utcnow()

    async def load_extensions(self):
        """method that handles loading the extensions from cogs-directory
        remember the dotpaths! (cogs.foo)"""
        await self.wait_until_ready()
        await asyncio.sleep(1)
        self.load_extension("cogs.hello")
   
    async def on_ready(self):
        """print some debug data when connected"""
        print("SaberBot version:")
        print(self.__version__)
        print("Logged in as:")
        print(self.user.name)
        print("discord.py version:")
        print(discord.__version__)
    
    async def on_message(self, message):
        """event for messages on servers bot joins
        calls process_commands handler to parse them"""
        if message.author.bot: #we really don't want possible other bots to trigger commands
            return
        await self.process_commands(message)

if __name__ == "__main__":
    try:
        config_file = sys.argv[1]
        main(config_file)
    except NameError:
        print("usage: saberbot.py <path_to_config_file>")
