from func.cicina import get_cicina_today, get_random_cicina
from func.firebase_init import db

import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

from datetime import datetime
from pytz import timezone
import yaml
import os
from dotenv import load_dotenv
load_dotenv()

random_org_api_key = os.getenv("RANDOM_ORG_API_KEY")

# Config Load
local_timezone = yaml.safe_load(open('config.yml')).get('local_timezone')


class Cicina(commands.Cog):
    def __init__(self, client):
        """Cicina command."""
        self.client = client

    @commands.slash_command(name="cicina", description="Shows your cicina size")
    async def cicina(
            self,
            inter: disnake.ApplicationCommandInteraction,
            top: str = Param(None, desc="Shows top 30 cicina users for today")
    ):
        uid = inter.author.id
        today = datetime.now(timezone(local_timezone)).strftime('%Y-%m-%d')
        cicina = get_random_cicina(random_org_api_key)

        # Cicina Top
        if top is not None and top.lower() == "top":
            cicina_today = db.child('cicinaToday').get().val() or None
            list_of_today = get_cicina_today(cicina_today, today)

            if cicina_today is None or list_of_today is None:
                return await inter.response.send_message("Nobody claimed their cicina today")

            list_of_today_sorted = sorted(list_of_today, key=lambda x: x['cicina'], reverse=True)

            top_msg = "**Today's top cicina's:**\n"
            peep_count = 0
            for _ in list_of_today_sorted:
                usr = self.client.get_user(int(list_of_today_sorted[peep_count]['uid']))
                if not usr:
                    continue
                cic = list_of_today_sorted[peep_count]['cicina']
                top_msg += f"**{peep_count + 1}.** {usr.name} with ***{cic}*** *cm*\n"
                peep_count += 1
                if peep_count == 30:
                    break
            return await inter.response.send_message(top_msg)

        cicina_last = db.child('users').child(uid).child('cicina_last').get().val() or 0
        cicina_longest = db.child('users').child(uid).child('cicina_longest').get().val() or 0

        if cicina_last != today:
            emote = disnake.utils.get(self.client.emojis, name="resttHA")
            msg = f'Dĺžka tvojej ciciny je {cicina} centimetrov {emote}'

            cicina_today_data = {"uid": uid, "cicina": cicina, "date": today}
            db.child('cicinaToday').child(uid).update(cicina_today_data)

        else:
            midnight_ts = int(
                datetime.now(timezone(local_timezone)).replace(hour=0, minute=0, second=0).timestamp() + 86400)
            msg = f'Cicina sa ti resetuje zajtra (~<t:{midnight_ts}:R>)'
            return await inter.response.send_message(msg, ephemeral=True)

        if cicina > cicina_longest:
            cicina_for_db = cicina
        else:
            cicina_for_db = cicina_longest

        cicina_avg = db.child('users').child(uid).child('cicina_avg').get().val()
        cicina_count = db.child('users').child(uid).child('cicina_count').get().val()

        if cicina_count is None:
            new_count = 1
            new_avg = cicina

        else:
            new_avg = (cicina_avg * cicina_count + cicina) / (cicina_count + 1)
            new_count = cicina_count + 1

        data = {
            'cicina_longest': cicina_for_db,
            'cicina_last': today,

            'cicina_avg': new_avg,
            'cicina_count': new_count}

        db.child('users').child(uid).update(data)
        await inter.response.send_message(msg)


def setup(client):
    client.add_cog(Cicina(client))
