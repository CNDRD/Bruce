from discord.ext import commands
import pyrebase, yaml, json, os

from dotenv import load_dotenv
load_dotenv()

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()

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
        data = {
        "username": str(after),
        "avatar_url":str(after.avatar_url_as(size=4096))
        }
        db.child('users').child(after.id).update(data)


def setup(client):
    client.add_cog(OnUserUpdate(client))
