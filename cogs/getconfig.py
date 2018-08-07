from os import path
from configparser import ConfigParser

class Config:
    
    def __init__(self):
        self.location = self.get_config_location()
    
    def get_config_location(self):
        """returns full path of saberbot/tmp/config_location"""
        temppath = self.get_botpath()
        temppath += "/tmp/config_location"
        with open(temppath) as locationfile:
            configpath = locationfile.read()
        return configpath

    def get_botpath(self):
        """ returns the path where bot lives """
        botpath = path.abspath(__file__) # check the absolute path for this file
        botpath = botpath.split("/") # no easy relative path? just make it a list
        botpath = botpath[0:len(botpath)-2] # slice it 
        botpath = "/".join(botpath) # make it a string again
        return botpath


    def get_config(self):
        """returns config file as dict"""
        cfgparser = ConfigParser()
        cfgparser.read(self.location)
        return cfgparser
