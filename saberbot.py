#!/usr/bin/python3
from discord.ext import commands
import discord
import datetime, asyncio
import configparser, os

def main():
    """calls method to load the .ini config, then spawns new instance of bot and starts it"""
    initialize_bot() 
    bot=SaberBot(description=desc)
    bot.run(oauth)

def initialize_bot(config_path = "config.ini"):
    """reads the user configurable values from .ini file, assumed to be on the root of folder
    TODO: make parsing the actual input file more neat"""
    global oauth, desc # just, like, find a better way to deal with oauth
    config_path = os.getcwd() + "/" + config_path #bit ugly I'd guess but works
    print(f"opening up config file from {config_path}")
    cfg = configparser.ConfigParser()
    cfg.read(config_path) #this bit also needs bit rewriting
    cfg = cfg['saberbot'] #as config file grows
    oauth = cfg['oauth']
    desc = cfg['desc']

class SaberBot(commands.Bot):
    """the main class that contains the bot"""
    def __init__(self, **kwargs):
        super().__init__(command_prefix=self.get_prefix_, description=desc)
        self.start_time=None
        self.__version__ = "0.1.0"
        self.loop.create_task(self.track_start()) #unused yet, will be used for timing stuff
        self.loop.create_task(self.load_extensions())
    
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
    main()
