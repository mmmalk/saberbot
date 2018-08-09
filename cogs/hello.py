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
    
    @commands.command(pass_context=True, hidden=True)
    async def owner(self, ctx):
           await self.bot.say(f"{self.bot.owner.mention} is") 

    @commands.command(pass_context=True)
    async def cool(self, ctx):
        await self.bot.send_message(ctx.message.channel, f"who's cool? {ctx.message.author.mention} is!")

    async def on_member_join(self, member):
        """in cogs, events don't need pie decorator, we can directly react to them
        checks out what server join happened, check's the default channel and displays greet"""
        welcome_channel = member.server.default_channel
        welcome_message = f"hello, @{member.name}, check out rules and don't be a git :)"
        print(f"{welcome_channel}@{member.server} : {welcome_message}")
        await self.bot.send_message(welcome_channel, welcome_message)
        

def setup(bot): #setup method to load the actual function to the bot
    bot.add_cog(Hello(bot))
