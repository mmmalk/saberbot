#!/usr/bin/python3
from discord.ext import commands
import discord
import datetime, asyncio, logging
import sys, configparser, os

def main(config_file):
    """calls method to load the .ini-style config, then spawns new instance of bot and starts it
    params: 
        config_file - name of configuration file
    return: 
        None"""
    c=config_file
    print(f"using configuration: {c}")
    logger = logging.getLogger("discord")
    logger.setLevel(logging.WARNING)
    loghandler = logging.FileHandler(filename="log/saberbot.log", mode="w")
    loghandler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
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
        self.config = configparser.ConfigParser()
        with open(conf) as file:
            self.config.read_file(file)
        self.owner_id = self.config['owner']['id']
    
    async def is_owner(self, usr):
        return self.owner == usr


    async def get_version(self):
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
            logger.info(f"loaded cog {cog.lstrip()}")
epAugu
    async def on_ready(self):
        """log some debug data when connected
        params:
            None
        returns:
            None
        """
        logging.info(f"version: {self.__version__}")
        logging.info(f"username: {self.user.name}")
        logging.info(f"discord.py version: {discord.__version__}")
        if not hasattr(self, "appinfo"):
            self.appinfo = await self.application_info()
        logging.info(self.appinfo)
        self.owner = await self.get_user_info(self.owner_id)
        logging.info(self.owner)

    async def on_message(self, msg):
        """event for messages on servers bot joins
        calls process_commands handler to parse them
        params:
            message
        returns:
            None"""
        self.last_ctx = ctx
        if msg.author.bot: #we really don't want possible other bots to trigger commands
            return
        logging.info(f"{msg.timestamp}\t{msg.author}:{msg.content}") 
        await self.process_commands(msg)
    
    async def on_error(self, *args, **kwargs):
        """logs the error message on error
        params:
            msg - the message that caused the error"""
        msg=args[0]
        logging.warning(f"{msg.timestamp}\t{msg.author}@{msg.channel}: {msg.content}")
        logging.warning(traceback.format_exc()) #traceback.format_exc returns str, instead of writing to a file
        await self.send_message(message.channel, "I'm sorry, I didn't quite understand, please try again. See !help for command info.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("please specify config file")
    else:
        main(sys.argv[1])
