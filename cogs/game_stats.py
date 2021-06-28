from func.r6 import rainbow6statsv7

import pyrebase, yaml, json, asyncio, time, os
from discord.ext import commands, tasks

from dislash import *

from dotenv import load_dotenv
load_dotenv()

## Monkey patch
import nest_asyncio
nest_asyncio.apply()

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')
slash_guilds = config.get('slash_guilds')
dbr6_loop = config.get('dbr6_loop')
dbr6_loop_time = config.get('dbr6_loop_time')

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()

class GameStats(commands.Cog):
    def __init__(self, client):
        """
        Various Game Stats gathering loops.

        - dbr6 (loop)
        - stats_update
        """
        self.client = client
        if dbr6_loop: self.dbr6.start()


    @tasks.loop(minutes=dbr6_loop_time)
    async def dbr6(self):
        users = db.child('GameStats').child('IDs').get()
        a = {}
        for u in users.each():
            if (ubi_id := u.val().get('ubiID')) is not None:
                a[ubi_id] = u.val().get('discordUsername')

        data = asyncio.new_event_loop().run_until_complete(rainbow6statsv7(a))
        db.child('GameStats').child('R6Sv8').update(data)
        db.child('GameStats').child('lastUpdate').update({'R6Sv8':int(time.time())})


    @slash_commands.command(
        guild_ids=slash_guilds,
        description="Manually update game stats."
    )
    @slash_commands.has_role(bot_mod_role_id)
    async def stats_update(self, ctx):
        # Stops and then promptly starts all stats loops
        if dbr6_loop: self.dbr6.cancel()
        # This 0.5s delay needs to be here because who the fuck knows why
        await asyncio.sleep(0.5)
        if dbr6_loop: self.dbr6.start()
        await ctx.create_response("Stats updated!", ephemeral=True)


def setup(client):
    client.add_cog(GameStats(client))
