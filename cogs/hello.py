import discord
from discord.ext import commands

class Hello:
    """simple greeter class, loaded using cogs system"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def hi(self, ctx):
        """says hello when tagged"""
        await self.bot.send_message(ctx.message.channel, "hi")
    
    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def owner(self, ctx):
        re = await self.bot.is_owner(ctx.message.author)
        if re:
            await self.bot.send_message(ctx.message.channel, f"you're owner, {ctx.message.author.mention}")
        if not re:
            await self.bot.send_message(ctx.message.channel, f"you're not owner, {ctx.message.author.mention}")

    @commands.command(pass_context=True, hidden=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def ami(self, ctx):
        print(ctx.message.author)
        re = self.bot.is_owner(ctx.message.author.id)
        await self.bot.send_message(ctx.message.author, re)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def cool(self, ctx):
        """tells user who's cool"""
        await self.bot.send_message(ctx.message.channel, f"who's cool? {ctx.message.author.mention} is!")

    async def on_member_join(self, member):
        """in cogs, events don't need pie decorator, we can directly react to them
        checks out what server join happened, check's the default channel and displays greet"""
        welcome_channel = self.bot.get_channel(self.bot.config["saberbot"]["welcome_channel"])
        welcome_message = f"hello, @{member.name}, check out rules and don't be a git :)"
        await self.bot.send_message(welcome_channel, welcome_message)
        

def setup(bot): #setup method to load the actual function to the bot
    bot.add_cog(Hello(bot))
