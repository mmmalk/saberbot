from discord.ext import commands
import boterror, random

class Base:

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(pass_context=True)
    async def love(self, ctx, *args):
        """tells how much love is in between user and argument"""
        love = " ".join(args)
        if str(ctx.message.author.name) == love:
            await self.bot.send_message(ctx.message.channel, "Love thyself")
            return
        amount = random.randrange(0,100)
        await self.bot.send_message(ctx.message.channel, f"There's {amount}% of love between {ctx.message.author.mention} and {love}")

    @commands.command(pass_context=True)
    async def hug(self, ctx):
        """hugs you. ewww"""
        await self.bot.send_message(ctx.message.channel, f"_hugs_ {ctx.message.author.mention}")
    
    @commands.command(pass_context=True, hidden=True)
    async def echo(self, ctx, *args):
        await self.bot.send_message(ctx.message.channel, "  ".join(args))

    @commands.group(pass_context=True, hidden=True)
    async def admin(self, ctx):
        if not self.bot.owner_id == ctx.message.author.id:
           await self.bot.send_message(ctx.message.channel, "You're not allowed to do that")
           raise boterror.InsufficientRights(f"{ctx.message.author} invoked owner-only command: {ctx.message.channel}: {ctx.message.content}")
        if ctx.invoked_subcommand is None:
            await self.bot.send_message(ctx.message.channel, "Your command is invalid")
        
    @admin.command(pass_context=True)
    async def reload(self, ctx, *args):
        for arg in args:
            try:
                self.bot.unload_extension(f"cogs.{arg}")
                self.bot.load_extension(f"cogs.{arg}")
                self.bot.logger.info(f"{arg} reloaded")
                await self.bot.send_message(ctx.message.channel, f"{arg} reloaded")
            except ModuleNotFoundError:
                await self.bot.send_message(ctx.message.channel, f"Can't find module {arg}")

    @admin.command(pass_context=True)
    async def unload(self, ctx, *args):
        for arg in args:
            try:
                self.bot.unload_extension(f"cogs.{arg}")
                self.bot.logger.info(f"{arg} unloaded")
                await self.bot.send_message(ctx.message.channel, f"{arg} unloaded")
            except ModuleNotFoundError:
                await self.bot.send_message(ctx.message.channel, f"Can't find module {arg}")


    @admin.command(pass_context=True)
    async def load(self, ctx, *args):
        for arg in args:
            try:
                self.bot.load_extension(f"cogs.{arg}")
                self.bot.logger.info(f"{arg} loaded")
                await self.bot.send_message(ctx.message.channel, f"{arg} loaded")
            except ModuleNotFoundError:
                await self.bot.say(f"Can't find module {arg}")
            except CommandInvokeError as cie:
                await self.bot.send_message(ctx.message.channel, f"bleep bloop, I don't understand {arg}")
                await self.bot.whisper(self.bot.owner, cie)


def setup(bot):
    bot.add_cog(Base(bot))
