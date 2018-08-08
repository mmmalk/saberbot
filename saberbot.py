#!/usr/bin/python3
from discord.ext import commands
import discord
import datetime, asyncio
import sys, configparser, os

def main(config_file):
    """calls method to load the .ini-style config, then spawns new instance of bot and starts it
    params: 
        config_file - name of configuration file
    return: 
        None"""
    c=config_file
    print(f"using configuration: {c}")
    with open('tmp/config_location', "w+") as location:
        location.write(f"{os.path.abspath(c)}")    
    bot=SaberBot(c)
    bot.run(bot.config["saberbot"]["oauth"])

class SaberBot(commands.Bot):
    """the main class that contains the bot"""
    def __init__(self, conf):
        super().__init__(command_prefix=self.get_prefix_)
        self.start_time=None
        self.__version__ = "0.1.0"
        self.loop.create_task(self.track_start()) #unused yet, will be used for timing stuff
        self.loop.create_task(self.load_extensions())
        self.config = configparser.RawConfigParser()
        with open(conf, 'r') as file:
            self.config.readfp(file)
        self.load_extensions()
        

    def get_version(self):
        """return: version"""
        return self.__version__
    
    async def get_prefix_(self, bot, message):
        """defines the prefixes used for commands
        prefix = list[string] or when mentioned
        params: 
            bot - the bot itself
            message
        """
        prefix = ["!", "?", "."]
        return commands.when_mentioned_or(*prefix)(bot, message)

    async def track_start(self):
        """logs the starting moment as datetime object as an start_time attribute
        returns: none"""
        await self.wait_until_ready()
        self.start_time=datetime.datetime.utcnow()

    async def load_extensions(self):
        """method that handles loading the extensions from cogs-directory
        remember the dotpaths! (cogs.foo)
        params:
            None
        returns: 
            None
        """
        await self.wait_until_ready()
        await asyncio.sleep(1)
        for cog in self.config['saberbot']['cogs'].split(','):
            self.load_extension(f"cogs.{cog.lstrip()}")
            print(f"loaded cog: {cog.lstrip()}")
   
    async def on_ready(self):
        """print some debug data when connected
        params:
            None
        returns:
            None
        """
        print("SaberBot version:")
        print(self.__version__)
        print("Logged in as:")
        print(self.user.name)
        print("discord.py version:")
        print(discord.__version__)
    
    async def on_message(self, message):
        """event for messages on servers bot joins
        calls process_commands handler to parse them
        params:
            message
        returns:
            None"""
        if message.author.bot: #we really don't want possible other bots to trigger commands
            return
        await self.process_commands(message)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("please specify config file")
    else:
        main(sys.argv[1])
