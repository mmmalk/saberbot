from discord.ext import commands
from urllib import parse
from os import path
from http import cookiejar
import discord, json, pickle, random, re, requests, time

def setup(bot):
    bot.add_cog(Gog(bot))
    bot.add_cog(Steam(bot))

class GameSearch:
    """Module that's used to search games from gog.com and steam"""
    def __init__(self, bot, *arg): #__init__(self, bot) for deployment
        self.last_result = {}
        self.bot = bot
        self.safe = re.compile("[^a-zA-Z0-9\s+]")

    def get_json(self, addr):
        """fetches the .json
        params:
            addr = address of the json
        returns:
            data = dictionary formed from json data"""
        response = requests.get(addr) 
        data = response.json()
        response.close()
        return data
    
    def formquery(self, *args):
        """ parses the arguments to list of terms to query for
        params:
                *args - list of search arguments
        returns:
                query = list of words to make query from
                results = how many results will be returned(defaults to 1)"""
        query = []
        results = 1
        for item in args:
            if "=" in item:
                if item.startswith("links"):
                    results = int(item[6:])
                continue
            query.append(item)
        return query, results
    
    def formregex(self, querylist):
        """forms regex from list of search terms
        params:
            querylist - list of strings containing search terms
        returns:
            re_string - the regex pattern"""
        all = "[a-z\s]*"
        re_string = all
        for word in querylist:
            re_string += f"({word})" +"{1}"+all
        re_string += all
        return re_string


class Gog(GameSearch):
    
    def __init__(self, bot, *args):
        super().__init__(self, bot)
        self.apiurl = "http://embed.gog.com/games/ajax/filtered?mediaType=game&search="
        self.baseurl = "http://www.gog.com"
        self.safe = re.compile("[^a-zA-Z0-9\s+]")
        self.config = bot.config
        self.bot = bot
    
    def parse_reply(self, data, results):
        """parses the gog response into list of games
        params:
            data = the json response from gogcom server
            results = int of number of games to search for
        returns:
            games[] = list of dicts, games[{'id': 'int', 'url': 'str'}]"""
        games = []
        if results > len(data["products"]):
            results = len(data["products"])
        if results > 5:
            results = 1
        for i in range(results):
            currentgame = data["products"][i]
            games.append({"id" : currentgame["id"], "url" : currentgame["url"]})
        return games
    
    def search(self, query):
        """forms the url for json query
        params:
            query = list of strings containing search terms
        returns:
            searchurl = the string containing the url for json query"""
        query = [word.strip() for word in query]
        keyword = "  ".join(query) 
        keyword = self.safe.sub("", keyword) #parse all but alphanumerics and space
        keyword = parse.quote(keyword)
        searchurl = self.apiurl+keyword
        return searchurl

    def get_random(self):
        """Gets random game from gog.com by getting random ID from a list containing store IDs
        params:
            none
        returns:
            storeurl = string containing url for store page"""
        idlist = []
        with open(self.config["gamesearch"]["gog_idlist"], "rb") as file:
            idlist = pickle.load(file)
        re = requests.get(f"https://api.gog.com/products/{random.choice(idlist)}")
        while re.status_code != 200:
            re = requests.get(f"https://api.gog.com/products/{random.choice(idlist)}")
        gamedata = json.loads(re.text)
        return gamedata["links"]["product_card"]

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def gog(self, ctx, *args):
        """Search gogcom games
        usage: !gog <query> optionally specify links=<number> for amount of links or simply !gog for random store pag or simply !gog for random store page"""
        query, results = self.formquery(*args)
        self.bot.logger.info(query)
        if not query:
            url = self.get_random()
            await self.bot.send_message(ctx.message.channel, url + self.bot.config["gamesearch"]["gog_parameters"])
            return
        url = self.search(query)
        query = self.get_json(url)
        gamelist = self.parse_reply(query, results)
        for game in gamelist:
            await self.bot.send_message(ctx.message.channel, self.baseurl + game["url"] + self.bot.config["gamesearch"]["gog_parameters"])


class Steam(GameSearch):
    """Submodule for fetching Steam game from store"""
            
    def __init__(self, bot, *args):
         super().__init__(self, bot)
         self.bot = bot
         self.apiurl = "https://api.steampowered.com"
         self.baseurl = "https://store.steampowered.com/app/"
    
    def search(self, querylist):
        """performs the steam store search, forms query and queries the local copy of json containing the ids of the games
        params:
            querylist = list of strings containing search terms
        returns:
            results = sorted(by the length of the name) dictionary containing the results"""
        for word in querylist:
            querylist[querylist.index(word)] = self.safe.sub("", word).lower() #remove anything but alphanumerics, make it lowercase
        regex_str = self.formregex(querylist)
        query_regex = re.compile(regex_str)
        jsonpath = self.bot.config["gamesearch"]["jsonpath"]
        with open(jsonpath, "rb") as jsonfile: #could also use get_json
            applist = pickle.load(jsonfile)    #but then you'd fetch whole appid list each time function gets called
        results = self.parseapplist(query_regex, applist)
        results = sorted(results, key=lambda k : len(k['name'])) #sort by the value of len(d[index]['name'])
        return results

    def parseapplist(self, query_regex, data):
        """goes through the given dict, and matches the names of the games against given regex of the query
        params:
            query_regex = the regex to match game names against
            data = the dict containing the names and other stuff about games
        returns:
            results = dict containing appid and name results{'id': 'int', 'name' : 'str'}"""
        applications = data['applist']['apps']
        results = []
        for app in applications:
            appname = self.safe.sub("", app['name']).lower() #appname =string without anything but alphanumerics
            if re.match(query_regex, appname):
                if self.checkgame(app["appid"]):
                    results.append({"id" : app["appid"], "name" : appname})
        return results

    def checkgame(self, appid):
        """method checks if the store page actually exists
        params:
            appid = the id of the store item to check
        returns:
            status = boolean whether store page exists(if there's redirect or not)"""
        appurl = self.baseurl + str(appid)
        response = requests.get(appurl, allow_redirects=False)
        status = response.status_code
        response.close()
        if 300 < status < 400:
            return False
        return True
    
    def refreshapps(self):
        """method used for reading the GetAppList resource from json, then pickling it for local storage
        params, returns:
            none"""
        jsonurl = self.apiurl + "/ISteamApps/GetAppList/v2"
        jsonpath = self.bot.config["gamesearch"]["jsonpath"]
        jsonpath = path.abspath(jsonpath)
        jsondata = self.get_json(jsonurl)
        with open(jsonpath, "wb") as jsonfile:
            pickle.dump(jsondata, jsonfile)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def steam(self, ctx, *args):
        """Search steam games
        usage: !steam <query> optionally specify links=<number> for amount of links"""
        query, results = self.formquery(*args)
        if not query:
            return
        try:
            games = self.search(query)
            if results > len(games):
                results = len(games)
            for index in range(results):
                gameurl = self.baseurl + str(games[index]["id"])
                await self.bot.say(gameurl)
                time.sleep(3)
        except FileNotFoundError:
            await self.bot.send_message(ctx.message.channel, "can't find jsonpath")

    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def updatesteam(self, ctx, *args):
        """command to update steam game database
        usage: updatesteam"""
        try:
            self.refreshapps()
            await self.bot.send_message(ctx.message.channel, "jsonfile updated!")
        except Exception as e:
            await self.bot.say(e.__cause__)
            await self.bot.say(e.__context__)


