from discord.ext import commands
import pyrebase, yaml, json

################################################################ Config Load ##
config = yaml.safe_load(open("config.yml"))
cl = config.get('console_logging')

################################################################### Firebase ##
fb = json.loads(config.get('firebase'))
firebase = pyrebase.initialize_app(fb)
db = firebase.database()

################################################################### Commands ##
class RandomEvents(commands.Cog):
    def __init__(self, client):
        """Random events."""
        self.client = client


    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if cl: print('START on_user_update ', end="")
        # When a user changes their Discord username or profile picture
        # this updates that data in the database
        data = {
        "username": str(after),
        "avatar_url":str(after.avatar_url_as(size=4096))
        }
        db.child('users').child(after.id).update(data)
        if cl: print("END")


def setup(client):
    client.add_cog(RandomEvents(client))
