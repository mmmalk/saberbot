from discord.ext import commands

class Base:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def echo(self, *args, **kwargs):
        for i in range(0, len(args)):
            await self.bot.say(args[i])
        for i in range(0, len(kwargs)):
            await self.bot.say(kwargs[i])

def setup(bot):
    bot.add_cog(Base(bot))
