from discord.ext import commands
import discord

class Plug:

    def __init__(self, bot):
        self.bot = bot
        self.name = self.bot.config["plug"]["shilled_name"]

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def twitter(self, ctx):
        """check out twitter"""
        name = self.bot.config["plug"]["shilled_name"]
        twitter = self.bot.config["plug"]["twitter"]
        await self.bot.send_message(ctx.message.channel, f"Streamer of some renown, {name} is on twitter: {twitter}")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def affiliate(self, ctx):
        """someone got affiliated"""
        name = self.bot.config["plug"]["shilled_name"]
        affiliate_url = self.bot.config["plug"]["affiliate_url"]
        await self.bot.send_message(ctx.message.channel, f"{name} is now gog.com affiliate! You can use this affiliate link when you buy games (valid for 24 hours after clicking) to support them! {affiliate_url}")

def setup(bot):
    bot.add_cog(Plug(bot))

