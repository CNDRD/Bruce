from func.firebase_init import db
from func.cicina import get_cicina_today

import disnake
from disnake.ext import commands

from datetime import datetime, time
from pytz import timezone
import numpy as np

class Cicina(commands.Cog):
    def __init__(self, client):
        """
        Cicina command.
        """
        self.client = client
        self.local_timezone = 'Europe/Prague'


    @commands.slash_command(
        name="cicina",
        description="Shows your cicina size",
        options=[
            disnake.Option(
                name="top",
                description="Shows top 30 cicina users for today"
            )
        ]
    )
    async def cicina(self, inter, top: str = None):
        uid = inter.author.id
        today = datetime.now(timezone(self.local_timezone)).strftime('%Y-%m-%d')
        cicina = np.random.randint(0,51)

        # Cicina Top
        if top is not None and top.lower() == "top":
            cicinaToday = db.child('cicinaToday').get().val() or None
            listOfToday = get_cicina_today(cicinaToday, today)

            if cicinaToday is None or listOfToday is None:
                return await inter.response.send_message("Nobody claimed their cicina today")

            listOfTodaySorted = sorted(listOfToday, key = lambda x: x['cicina'], reverse=True)

            topMsg = "**Today's top cicina's:**\n"
            peepCount = 0
            for _ in listOfTodaySorted:
                usr = self.client.get_user(int(listOfTodaySorted[peepCount]['uid']))
                if not usr: continue
                cic = listOfTodaySorted[peepCount]['cicina']
                topMsg += f"**{peepCount+1}.** {usr.name} with ***{cic}*** *cm*\n"
                peepCount += 1
                if peepCount == 30: break
            return await inter.response.send_message(topMsg)


        cicinaLast = db.child('users').child(uid).child('cicina_last').get().val() or 0
        cicinaLongest = db.child('users').child(uid).child('cicina_longest').get().val() or 0

        if cicinaLast != today:
            emote = disnake.utils.get(self.client.emojis, name="resttHA")
            msg = f'{inter.author.mention} - Dĺžka tvojej ciciny je {cicina} centimetrov {emote}'

            cicinaTodayData = {"uid": uid, "cicina": cicina, "date": today}
            db.child('cicinaToday').child(uid).update(cicinaTodayData)

        else:
            midnight_ts = int(datetime.now(timezone(self.local_timezone)).replace(hour=0, minute=0, second=0).timestamp() + 86400)
            msg = f'{inter.author.mention} - Cicina sa ti resetuje zajtra (~<t:{midnight_ts}:R>)'
            return await inter.response.send_message(msg)


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
        await inter.response.send_message(msg)


def setup(client):
    client.add_cog(Cicina(client))
