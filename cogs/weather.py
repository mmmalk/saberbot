import discord
from discord.ext import commands
import json, urllib.request, io, re

class Weather:
    """Weather class handles weather using openweather api
    params:
        
    attributes:
        apikey: api key for openweather
        config_location: configuration location for saberbot
        locations: json file containing the openweathermap location data
    """

    def __init__(self, bot):
        self.bot = bot
        self.conf = self.bot.config["weather"]
        self.apikey = self.conf["apikey"]
        with open(self.conf["citylist"]) as jsonfile:
            self.locations_json = json.loads(jsonfile.read())
    
    def parsequery(self, *args):
        """parses list of argument to string"""
        querystring = ""
        keywords = {}
        print(args)
        for arg in args:
            if "=" in arg:
                larg = arg.split("=")
                keywords[larg[0]] = larg[1]
                continue
            querystring += f" {str(arg)}"
        querystring = querystring.lstrip()
        return querystring, keywords

    def get_location_id(self, location, country):
        print(location)
        for item in self.locations_json:
            if item["name"] == location:
                if not country or item["country"]== country.upper():
                    return item["id"]
        return None
    
    def get_data(self, id):
        """params: id - location id
        returns: data - dictionary object containing json response"""
        url_string=f"http://api.openweathermap.org/data/2.5/weather?id={id}&APPID={self.apikey}"        
        response = urllib.request.urlopen(url_string)
        data = json.loads(response.read())        
        return data
   
    def get_info(self, data):
        """params: data
        returns: info"""
        info = []
        info.append(data["weather"][0]["description"])
        info.append(data["main"]["temp"])
        info.append(data["sys"]["country"])
        return info

    def kelvin_to_celcius(self, k):
        return k - 273.15

    def celcius_to_fahrenheit(self, c):
        return (9/5)*c+32



    @commands.command(pass_context=True)
    async def weather(self, ctx, *args):
        """says weather data on discord channel
        params: location
        returns: None"""
        location, keywords = self.parsequery(*args) 
        if keywords:
            country = keywords["country"]
        else:
            country = ""
        regex = re.compile("([^\w\s{1}]|\d|_|\s+)") #\W_ didn't work in testing for some reason?
        location = re.sub(regex, "", location) #transform location into string with spaces
        l = []
        l.append(country)
        l.append(location)
        print(l)
        location_id = self.get_location_id(location, country)
        if location_id != None:
            weatherdata = self.get_data(location_id)
            relevant = self.get_info(weatherdata)
            c = self.kelvin_to_celcius(relevant[1])
            f = self.celcius_to_fahrenheit(c)
            await self.bot.send_message(ctx.message.channel, f"weather for {location}, {relevant[2]}  {relevant[0]} ({int(c)} °C / {int(f)} °F)")
        else:
            await self.bot.send_message(ctx.message.channel, f"Sorry, I don't know where {location} is")

def setup(bot):
    bot.add_cog(Weather(bot))
