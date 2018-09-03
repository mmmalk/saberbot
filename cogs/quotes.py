from discord.ext import commands
import pickle, random, requests

class Quotes:
    """Simple class containing the methods for hooking up to the Nightbot quote api""" 
    def __init__(self, bot, *args):
        self.baseurl = "http://twitch.center/customapi/quote/list?token="
        self.bot = bot
        self.token = bot.config["quote"]["token"]

    def get_quotes(self):
        rq = requests.get(self.baseurl+self.token)
        qlist = rq.text.split("\n")
        with open(self.bot.config["quote"]["location"], "wb") as file:
            pickle.dump(qlist, file)

    def get_qlist(self):
        qlist = []
        with open(self.bot.config["quote"]["location"], "rb") as file:
            qlist = pickle.load(file)
        return qlist

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def quote(self, ctx, *args):
        """Nightbot quotes on Discord.
        usage: !quote for random quote, or !quote <number>"""
        quotelist = self.get_qlist()
        if not args:
            await self.bot.send_message(ctx.message.channel, random.choice(quotelist))
        else:
            quote = int(args[0])-1
            await self.bot.send_message(ctx.message.channel, quotelist[quote])

    @commands.command(hidden=True, pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def updatequotes(self, ctx):
        self.get_quotes()
        await self.bot.send_message(ctx.message.channel, "Updated quotes")


def setup(bot):
    bot.add_cog(Quotes(bot))
