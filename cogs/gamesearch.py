from discord.ext import commands
from urllib import parse
from urllib import request
from os import path
import discord, json, pickle, re
import cogs.getconfig as getconfig


def setup(bot):
    bot.add_cog(GameSearch(bot))

class GameSearch:

    def __init__(self, bot, *arg): #__init__(self, bot) for deployment
        self.last_result = {}
        self.bot = bot
        self.safe = re.compile("[^a-zA-Z0-9\s+]")

    def get_json(self, addr): #used for fetching json from server, for GameSearch.Steam() use get_from_file(filename) 
        response = request.urlopen(addr, None, 5) 
        data = json.loads(response.read())
        return data
    
    def formquery(self, *args):
        query = list(args)
        results = 1
        for item in query:
            if item.startswith("links="):
                results = int(item[6:])
                del query[query.index(item)]
        return query, results
    
    def formregex(self, querylist):
        all = "[a-z\s]*"
        re_string = all
        for word in querylist:
            re_string += f"({word})" +"{1}"+all
        re_string += all
        return re_string

    @commands.command()
    async def gog(self, *args):
        query, results = self.formquery(*args)
        if not query:
            return
        gogsearch = Gog(self.bot)
        url = gogsearch.search(query)
        query = gogsearch.get_json(url)
        gamelist = gogsearch.parse_reply(query, results)
        for game in gamelist:
            print(game)
            await self.bot.say(gogsearch.baseurl + game["url"])

    @commands.command()
    async def steam(self, *args):
        s = Steam(self.bot)
        print("=============SEARCH BEGINS==============")
        print(f"commands.command().steam: {args}")
        query, results = self.formquery(*args)
        print(query)
        if not query:
            return
        try:
            games = s.search(query)
            print(games)
            if results > len(games):
                results = len(games)
            for index in range(results):
                gameurl = s.baseurl + str(games[index]["id"])
                await self.bot.say(gameurl)
        except FileNotFoundError:
            await self.bot.say("can't find jsonpath")

    @commands.command()
    async def updatesteam(self, *args):
        s = Steam(self.bot)
        try:
            s.refreshapps()
            await self.bot.say("jsonfile updated!")
        except Exception as e:
            await self.bot.say(e.__cause__)
            await self.bot.say(e.__context__)

class Gog(GameSearch):
    
    def __init__(self, *args):
        super().__init__(self, args)
        self.apiurl = "http://embed.gog.com/games/ajax/filtered?mediaType=game&search="
        self.baseurl = "http://www.gog.com"
        self.safe = re.compile("[^a-zA-Z0-9\s+]")
    
    def parse_reply(self, data, results):
        games = []
        if results > len(data["products"]):
            results = len(data["products"])
        if results > 5:
            results = 1
        for i in range(results):
            currentgame = data["products"][i]
            games.append({'id': currentgame['title'], 'url' : currentgame['url']})
        return games
    
    def search(self, query):
        query = [word.strip() for word in query]
        keyword = "  ".join(query) 
        keyword = self.safe.sub("", keyword) #parse all but alphanumerics and space
        keyword = parse.quote(keyword)
        searchurl = self.apiurl+keyword
        return searchurl

class Steam(GameSearch):
            
    def __init__(self, bot, *args):
         super().__init__(self, args)
         self.bot = bot
         self.apiurl = "https://api.steampowered.com"
         self.baseurl = "https://store.steampowered.com/app/"
    
    def search(self, querylist):
        for word in querylist:
            querylist[querylist.index(word)] = self.safe.sub("", word).lower() #remove anything but alphanumerics, make it lowercase
        regex_str = self.formregex(querylist)
        print(regex_str)
        query_regex = re.compile(regex_str)
        jsonpath = path.abspath("tmp/steamapps")
        with open(jsonpath, "rb") as jsonfile: #could also use get_json
            applist = pickle.load(jsonfile)    #but then you'd fetch whole appid list each time function gets called
        results = self.parseapplist(query_regex, applist)
        results = sorted(results, key=lambda k : len(k['name'])) #sort by the value of len(d[index]['name'])
        return results

    def parseapplist(self, query_regex, data):
        applications = data['applist']['apps']
        results = []
        for app in applications:
            appname = self.safe.sub("", app['name']).lower() #appname =string without anything but alphanumerics
            if re.match(query_regex, appname):
                results.append({'id' : app['appid'], 'name' : appname})
        return results
    
    def refreshapps(self):
        jsonurl = self.apiurl + "/ISteamApps/GetAppList/v2"
        jsonpath = self.bot.config["gamesearch"]["jsonpath"]
        jsonpath = path.abspath(jsonpath)
        print(jsonpath)
        print(jsonurl)
        print(f"getting the json from {jsonurl}")
        jsondata = self.get_json(jsonurl)
        with open(jsonpath, "wb") as jsonfile:
            print(f"writing {jsonpath}")
            pickle.dump(jsondata, jsonfile)
        print("done")
        
    
