from func.r6 import rainbow6stats
from func.firebase_init import db

import pyrebase, yaml, json, asyncio, time, os
from discord.ext import commands, tasks

## Monkey patch
import nest_asyncio
nest_asyncio.apply()

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')
slash_guilds = config.get('slash_guilds')
dbr6_loop = config.get('dbr6_loop')
dbr6_loop_time = config.get('dbr6_loop_time')

R6STATS_VERSION = 9

class GameStats(commands.Cog):
    def __init__(self, client):
        """
        Various Game Stats gathering loops.

        - dbr6 (loop)
        - stats_update
        """
        self.client = client
        self.first_boot = True
        if dbr6_loop: self.dbr6.start()

        self.last_siege_update_ts = db.child("GameStats").child("lastUpdate").child(f"R6Sv{R6STATS_VERSION}").get().val()
        def wrtus(message):
            "Website Request To Update Siege"
            if self.first_boot:
                self.first_boot = not self.first_boot
            else:
                request_diff = message["data"] - self.last_siege_update_ts
                if request_diff >= (180):
                    print("Restarting DBR6 following a wesite request")
                    if dbr6_loop:
                        if self.dbr6.is_running():
                            self.dbr6.restart()
                        else:
                            self.dbr6.start()
                        self.last_siege_update_ts = time.time()

        db.child("GameStats").child("updateRequests").child("R6S").stream(wrtus)


    @tasks.loop(minutes=dbr6_loop_time)
    async def dbr6(self):
        users = db.child('GameStats').child('IDs').get()
        a = {}
        for u in users.each():
            if (ubi_id := u.val().get('ubiID')) is not None:
                a[ubi_id] = u.val().get('discordUsername')

        data = asyncio.new_event_loop().run_until_complete(rainbow6stats(a))
        db.child('GameStats').child(f'R6Sv{R6STATS_VERSION}').update(data)
        db.child('GameStats').child('lastUpdate').update({f'R6Sv{R6STATS_VERSION}':int(time.time())})


    @dbr6.before_loop
    async def before_dbr6(self):
        print('dbr6 - wait_until_ready()')
        await self.client.wait_until_ready()


    @dbr6.after_loop
    async def after_dbr6(self):
        print("R6 Loop Done")


    @commands.command(aliases=['su'])
    @commands.has_role(bot_mod_role_id)
    async def stats_update(self, ctx):
        # Stops and then prompltly starts all stats loops
        if dbr6_loop: self.dbr6.cancel()
        # This 0.5s delay needs to be here because who the fuck knows why
        await asyncio.sleep(0.5)
        if dbr6_loop: self.dbr6.start()
        await ctx.message.add_reaction('✅')


def setup(client):
    client.add_cog(GameStats(client))
