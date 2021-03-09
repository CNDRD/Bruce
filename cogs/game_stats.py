from func.console_logging import cl
from func.siege import rainbow6stats
from func.csgo import csgostats

from discord.ext import commands, tasks
import pyrebase, yaml, json, asyncio

## Config Load ##
config = yaml.safe_load(open('config.yml'))
bot_mod_role_id = config.get('bot_mod_role_id')
r6s_role_id = config.get('r6s_role_id')

error_channel_id = config.get('error_channel_id')

dbr6_loop = config.get('dbr6_loop')
dbr6_loop_time = config.get('dbr6_loop_time')
dbcsgo_loop = config.get('dbcsgo_loop')
dbcsgo_loop_time = config.get('dbcsgo_loop_time')

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class GameStats(commands.Cog):
    def __init__(self, client):
        """
        Various Game Stats gathering loops.

        - dbr6 (loop)
        - dbcsgo (loop)
        - stats_update
        """
        self.client = client
        if dbr6_loop: self.dbr6.start()
        if dbcsgo_loop: self.dbcsgo.start()


    @tasks.loop(minutes=dbcsgo_loop_time)
    async def dbcsgo(self):
        cl('', 'GameStats', 'dbcsgo')
        users = db.child('GameStats').child('IDs').get()
        for u in users.each():
            if (steam_id := u.val().get('steamID64')) is not None:
                stats = csgostats(int(steam_id), u.val().get('discordUsername'))
                db.child('GameStats').child('CSGO').child(steam_id).update(stats)


    @tasks.loop(minutes=dbr6_loop_time)
    async def dbr6(self):
        cl('', 'GameStats', 'dbr6')
        users = db.child('GameStats').child('IDs').get()
        for u in users.each():
            if (ubi_id := u.val().get('ubiID')) is not None:
                data = Rainbow6StatsV2(ubi_id, u.val().get('discordUsername'))
                db.child('GameStats').child('R6S').child(ubi_id).update(data)


    @commands.command(aliases=['su'])
    @commands.has_role(bot_mod_role_id)
    async def stats_update(self, ctx):
        cl(ctx)
        # Stops and then prompltly starts all stats loops
        self.dbcsgo.cancel()
        self.dbr6.cancel()
        # This 0.5s delay needs to be here because who the fuck knows why
        await asyncio.sleep(0.5)
        self.dbcsgo.start()
        self.dbr6.start()
        await ctx.message.add_reaction('✅')


def setup(client):
    client.add_cog(GameStats(client))
