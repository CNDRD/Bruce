from func.console_logging import cl

from discord.ext import commands
import pyrebase, yaml, json

## Config Load ##
config = yaml.safe_load(open("config.yml"))

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()

## Commands ##
class OnUserUpdate(commands.Cog):
    def __init__(self, client):
        """
        On User Update Event.

        Updates users username and avatar url in the database
        whenever they change anything about their account
        """
        self.client = client


    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        cl('', 'OnUserUpdate', 'on_user_update')
        data = {
        "username": str(after),
        "avatar_url":str(after.avatar_url_as(size=4096))
        }
        db.child('users').child(after.id).update(data)


def setup(client):
    client.add_cog(OnUserUpdate(client))
