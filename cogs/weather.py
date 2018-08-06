import discord
from discord.ext import commands
import json, configparser, pycurl, io, os

class Weather:
    """Weather class handles weather using openweather api
    params:
        
    attributes:
        p: filepath where saberbot lives
        c: configparser.RawConfigParser
        api_key: api key for openweather
        config_location: configuration location for saberbot
        locations: json file containing the openweathermap location data
    
    methods:
        get_config_location:
            params: none
            returns: self.config_location
        
        get_config_attribute:
            params: attribute
            returns: self.c["weather"][attribute]
            
        get_location_id:
            params: location
            returns: location id
            
        get_data:
            params: id
            return: json.loads(data)
        
        get_info:
            params: data
            return: info
        
        kelvin_to_celcius:
            params: kelvin
            returns: celcius
        
        celcius_to_fahrenheit:
            params: celcius
            returns: fahrenheit
        
        @commands.command()
        async weather:
            params: location
            returns: None"""

    def __init__(self, bot):
        p = os.path.abspath(__file__)
        p = p.split("/") # no easy relative path? just make it a list
        p = p[0:len(p)-2] # slice it 
        p = "/".join(p) # make it a string again
        with open(f"{p}/tmp/config_location", "r") as location:
            self.config_location=location.read()
            self.c = configparser.RawConfigParser()
        with open(self.config_location, "r") as config:
            self.c.readfp(config)
        with open(f"{p}/cogs/city.list.json", "r") as locations:
            self.locations_json = json.load(locations)
        self.api_key = self.c["weather"]["api_key"]
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
        for c in self.locations_json:
            if c['name'] == location:
                return c['id']
        return None
    
    def get_data(self, id):
        """params: id - location id
        returns: json.loads(data) - dictionary object containing json response"""
        bytes = io.BytesIO()
        apikey = self.get_config_attribute("api_key")
        curl = pycurl.Curl()
        curl.setopt(curl.URL, f"http://api.openweathermap.org/data/2.5/weather?id={id}&APPID={apikey}")
        curl.setopt(pycurl.WRITEFUNCTION, bytes.write)
        curl.perform()
        data = bytes.getvalue().decode('UTF-8')
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
        location_id = self.get_location_id(location)
        weatherdata = self.get_data(location_id)
        relevant = self.get_info(weatherdata)
        c = self.kelvin_to_celcius(relevant[1])
        f = self.celcius_to_fahrenheit(c)        
        await self.bot.say(f"weather for {location}: {relevant[0]} - {c} °C - {f} °F")

def setup(bot):
    bot.add_cog(Weather(bot))
