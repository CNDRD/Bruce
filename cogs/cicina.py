from func.console_logging import cl

import pyrebase, yaml, json, datetime, discord
from discord.ext import commands
from pytz import timezone
import numpy as np

## Config Load ##
config = yaml.safe_load(open('config.yml'))

## Firebase Database ##
db = pyrebase.initialize_app( json.loads(config.get('firebase')) ).database()


class Cicina(commands.Cog):
    def __init__(self, client):
        """Cicina command."""
        self.client = client


    @commands.command()
    async def cicina(self, ctx):
        cl(ctx)
        uid = ctx.author.id
        today = datetime.datetime.now(timezone('Europe/Prague')).strftime('%Y-%m-%d')
        cicina = np.random.randint(0,51)

        cicinaLast = db.child('users').child(uid).child('cicina_last').get().val()
        if cicinaLast is None: cicinaLast = 0

        cicinaLongest = db.child('users').child(uid).child('cicina_longest').get().val()
        if cicinaLongest is None: cicinaLongest = 0

        if cicinaLast != today:
            emote = discord.utils.get(ctx.guild.emojis, name="resttHA")
            msg = f'{ctx.author.mention} - Dĺžka tvojej ciciny je {cicina} centimetrov {emote}'

        else:
            msg = f'{ctx.author.mention} - Cicina sa ti resetuje zajtra'


        if cicina > cicinaLongest:
            cicina_for_db = cicina
        else:
            cicina_for_db = cicinaLongest


        cicinaAvg = db.child('users').child(uid).child('cicina_avg').get().val()
        cicinaCount = db.child('users').child(uid).child('cicina_count').get().val()


        if cicinaCount is None:
            new_count = 1
            new_avg = cicina

        else:
            new_avg = (cicinaAvg * cicinaCount + cicina) / (cicinaCount + 1)
            new_count = cicinaCount + 1

        data = {
            'cicina_longest':cicina_for_db,
            'cicina_last':today,

            'cicina_avg':new_avg,
            'cicina_count':new_count}

        db.child('users').child(uid).update(data)
        await ctx.send(msg)



def setup(client):
    client.add_cog(Cicina(client))
