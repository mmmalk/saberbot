from discord.ext import commands
import discord, json, requests


class YoutubeSearch:

    def __init__(self, bot):
        self.apiurl = "https://www.googleapis.com/youtube/v3/"
        self.bot = bot

    def search(self, *args):
        querystring = "&q="+"+".join(args)
        apikey = self.bot.config["youtube"]["apikey"]
        queryurl=self.apiurl + "search?part=snippet&type=video"+querystring+"&key="+apikey
        data = self.get_json(queryurl)
        return self.get_videourl(data)

    def get_json(self, url):
        response = requests.get(url)
        data = json.loads(response.text)
        return data

    def get_videourl(self, data):
        video_baseurl = "https://www.youtube.com/watch?v="
        return video_baseurl + data["items"][0]["id"]["videoId"]


    @commands.command(pass_context=True)
    @commands.cooldown(1, 5.0, commands.BucketType.server)
    async def youtube(self, ctx, *args):
        """searches youtube for video"""
        video = self.search(*args)
        await self.bot.send_message(ctx.message.channel, video)

def setup(bot):
    bot.add_cog(YoutubeSearch(bot))
    
