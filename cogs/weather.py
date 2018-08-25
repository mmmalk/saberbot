import discord
from discord.ext import commands
import json, requests, io, re

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
                    return str(item["id"])
        return None
    
    def get_data(self, id, url_string):
        """params: id - location id
        returns: data - dictionary object containing json response"""
        response = requests.get(url_string)
        data = json.loads(response.text)        
        return data
    
    def CtoF(self, c):
        return (9/5)*c+32

    @commands.command(pass_context=True)
    async def weather(self, ctx, *args):
        """says weather data on discord channel
        params: location
        returns: None"""
        relevant = {}
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
            weather_url=f"https://api.openweathermap.org/data/2.5/weather?id={location_id}&units=metric&APPID={self.apikey}"
            forecast_url=f"https://api.openweathermap.org/data/2.5/forecast/?id={location_id}&cnt=1&units=metric&APPID={self.apikey}"
            weatherdata = self.get_data(location_id, weather_url)
            forecastdata = self.get_data(location_id, forecast_url)
            country = weatherdata["sys"]["country"]
            print(weatherdata)
            relevant["today"] = {"desc" : weatherdata["weather"][0]["description"], "temp" : weatherdata["main"]["temp"]}
            relevant["tomorrow"] = {"desc" : forecastdata["list"][0]["weather"][0]["description"], "temp" : forecastdata["list"][0]["main"]["temp"]} 
            await self.bot.send_message(ctx.message.channel, f"weather for {location}, {country}: today  {relevant['today']['desc']} {int(relevant['today']['temp'])} °C / {int(self.CtoF(relevant['today']['temp']))} °F")    
            await self.bot.send_message(ctx.message.channel, f"tomorrow: {relevant['tomorrow']['desc']}, {int(relevant['tomorrow']['temp'])} °C / {int(self.CtoF(relevant['tomorrow']['temp']))} °F")
        else:
            await self.bot.send_message(ctx.message.channel, f"Sorry, I don't know where {location} is")

def setup(bot):
    bot.add_cog(Weather(bot))
