from discord.ext import commands
import boterror

class Base:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    async def echo(self, *args):
        await self.bot.say("  ".join(args))

    @commands.group(pass_context=True, hidden=True)
    async def admin(self, ctx):
        if not self.bot.owner_id == ctx.message.author.id:
           await self.bot.say("You're not allowed to do that")
           raise boterror.InsufficientRights(f"{ctx.message.author} invoked owner-only command: {ctx.message.channel}: {ctx.message.content}")
        if ctx.invoked_subcommand is None:
            await self.bot.say("Your command is invalid")
        
    @admin.command()
    async def reload(self, *args):
        for arg in args:
            try:
                self.bot.unload_extension(f"cogs.{arg}")
                self.bot.load_extension(f"cogs.{arg}")
                await self.bot.say(f"{arg} reloaded")
            except ModuleNotFoundError:
                await self.bot.say(f"Can't find module {arg}")

    @admin.command()
    async def unload(self, *args):
        for arg in args:
            try:
                self.bot.unload_extension(f"cogs.{arg}")
                await self.bot.say(f"{arg} loaded")
            except ModuleNotFoundError:
                await self.bot.say(f"Can't find module {arg}")


    @admin.command()
    async def load(self, *args):
        for arg in args:
            try:
                self.bot.load_extension(f"cogs.{arg}")
                await self.bot.say(f"{arg} loaded")
            except ModuleNotFoundError:
                await self.bot.say(f"Can't find module {arg}")
            except CommandInvokeError as cie:
                await self.bot.say(f"bleep bloop, I don't understand {arg}")
                await self.bot.whisper(self.bot.owner, cie)


def setup(bot):
    bot.add_cog(Base(bot))
