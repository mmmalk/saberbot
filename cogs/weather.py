import discord
from discord.ext import commands
import cogs.getconfig as getconfig
import json, pycurl, io 

class Weather:
    """Weather class handles weather using openweather api
    params:
        
    attributes:
        apikey: api key for openweather
        config_location: configuration location for saberbot
        locations: json file containing the openweathermap location data
    """

    def __init__(self, bot):
        config_getter = getconfig.Config()
        config = config_getter.get_config()
        with open(f"{config_getter.get_botpath()}/data/city.list.json", "r") as locations:
            self.locations_json = json.load(locations)
        self.apikey = config["weather"]["apikey"]
        print(self.apikey)
        self.bot = bot
    
    def get_config_location(self):
        """args: none
        return: self.config_location"""
        return self.config_location
    
    def get_config_attribute(self, attr):
        """params: attr - attribute from config file
        returns: c['weather'][attr] - attribute from config file"""
        return self.c["weather"][attr]
    
    def get_location_id(self, location):
        for item in self.locations_json:
            if item["name"] == location:
                return item["id"]
        return None
    
    def get_data(self, id):
        """params: id - location id
        returns: json.loads(data) - dictionary object containing json response"""
        bytes = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, f"http://api.openweathermap.org/data/2.5/weather?id={id}&APPID={self.apikey}")
        curl.setopt(curl.WRITEFUNCTION, bytes.write)
        curl.perform()
        data = bytes.getvalue().decode("UTF-8")
        return json.loads(data)
   
    def get_info(self, data):
        """params: data
        returns: info"""
        info = []
        info.append(data["weather"][0]["description"])
        info.append(data["main"]["temp"])
        return info

    def kelvin_to_celcius(self, k):
        return k - 273.15

    def celcius_to_fahrenheit(self, c):
        return (9/5)*c+32



    @commands.command()
    async def weather(self, location):
        """says weather data on discord channel
        params: location
        returns: None"""
        location = location.lower().capitalize() #rudimentary user input sanitization
        location_id = self.get_location_id(location)
        if location_id != None:
            weatherdata = self.get_data(location_id)
            relevant = self.get_info(weatherdata)
            c = self.kelvin_to_celcius(relevant[1])
            f = self.celcius_to_fahrenheit(c)        
            await self.bot.say(f"weather for {location}: {relevant[0]} - {c} °C - {f} °F")
        else:
            await self.bot.say(f"Sorry, I don't know where {location} is")

def setup(bot):
    bot.add_cog(Weather(bot))
