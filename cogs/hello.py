import discord
from discord.ext import commands

class Hello:
    """simple greeter class, loaded using cogs system"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hi(self):
        """says hello when tagged"""
        await self.bot.say("hi")

    async def on_member_join(self, member):
        """in cogs, events don't need pie decorator, we can directly react to them
        checks out what server join happened, check's the default channel and displays greet"""
        welcome_channel = member.server.default_channel
        welcome_message = f"hello, @{member.name}, check out rules and don't be a git :)"
        print(f"{welcome_channel}@{member.server} : {welcome_message}")
        await self.bot.send_message(welcome_channel, welcome_message)
        

def setup(bot): #setup method to load the actual function to the bot
    bot.add_cog(Hello(bot))
