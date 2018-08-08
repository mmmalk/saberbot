from discord.ext import commands
import discord, json, urllib.request, re
import cogs.getconfig as getconfig


class GameSearch:

    def __init__(self, bot):
        config_getter = getconfig.Config()
        self.config = config_getter.get_config()
        self.last_result = {}
        self.bot = bot
        self.safe_chars=re.compile('[^a-zA-Z0-9]')

    def gogcomsearch(self, *args):
        keyword = "  ".join(args)
        keyword = self.safe_chars.sub("", keyword)
        keyword = urllib.parse.quote(keyword)
        searchurl = f"http://embed.gog.com/games/ajax/filtered?mediaType=game&search={keyword}"
        response = urllib.request.urlopen(searchurl, None, 5)
        data = json.loads(response.read())
        return data
    
    def parse_gogreply(self, data, results):
        games = {}
        if results > len(data["products"]):
            results = len(data["products"])
        for i in range(results):
            currentgame = data["products"][i]
            games[currentgame['title']] = currentgame['url']
        return games
          
    @commands.command()
    async def gog(self, message : str, results : int=1):
        baseurl = "https://gog.com"
        query = self.gogcomsearch(message)
        gamedict = self.parse_gogreply(query, results)
        for key in gamedict:
            await self.bot.say(baseurl + gamedict[key])

def setup(bot):
    bot.add_cog(GameSearch(bot))
