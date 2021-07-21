import pyrebase, yaml, json, datetime, discord, os
from discord.ext import commands
from pytz import timezone
import numpy as np

from dotenv import load_dotenv
load_dotenv()

## Firebase Database ##
firebase_config = {"apiKey": "AIzaSyDe_xKKup4lVoPasLmAQW9Csc1zUzsxB0U","authDomain": "chuckwalla-69.firebaseapp.com",
  "databaseURL": "https://chuckwalla-69.firebaseio.com","storageBucket": "chuckwalla-69.appspot.com",
  "serviceAccount": json.loads(os.getenv("serviceAccountKeyJSON"))}
db = pyrebase.initialize_app(firebase_config).database()


class Cicina(commands.Cog):
    def __init__(self, client):
        """Cicina command."""
        self.client = client


    @commands.command()
    async def cicina(self, ctx):
        uid = ctx.author.id
        today = datetime.datetime.now(timezone('Europe/Prague')).strftime('%Y-%m-%d')
        cicina = np.random.randint(0,51)

        cicinaLast = db.child('users').child(uid).child('cicina_last').get().val() or 0
        cicinaLongest = db.child('users').child(uid).child('cicina_longest').get().val() or 0

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
