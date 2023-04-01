from func.supabase import supabase
from func.cicina import get_random_cicina

import disnake
from disnake.ext import commands

from datetime import datetime
from pytz import timezone


class Cicina(commands.Cog):
    def __init__(self, client):
        """Cicina command."""
        self.client = client

    @commands.slash_command(name="cicina", description="Shows your cicina size")
    async def _cicina(
            self,
            inter: disnake.ApplicationCommandInteraction
    ):
        today = datetime.now(timezone('Europe/Prague')).strftime("%Y-%m-%d")
        cicina = get_random_cicina()

        cicina_db = supabase.from_('users').select('cicina').eq('id', inter.author.id).execute()
        cicina_last = cicina_db.data[0]['cicina']['last']
        cicina_longest = cicina_db.data[0]['cicina']['longest']
        cicina_avg = cicina_db.data[0]['cicina']['average']
        cicina_count = cicina_db.data[0]['cicina']['count']

        if cicina_last != today:
            emote = disnake.utils.get(self.client.emojis, name="resttHA")
            msg = f"Dĺžka tvojej ciciny je {cicina} centimetrov {emote}"

        else:
            midnight_ts = int(datetime.now(timezone('Europe/Prague')).replace(hour=0, minute=0, second=0).timestamp() + 86400)
            return await inter.response.send_message(f"Cicina sa ti resetuje zajtra (~<t:{midnight_ts}:R>)")

        cicina_for_db = cicina if (cicina > cicina_longest) else cicina_longest

        if cicina_count is None:
            new_avg = cicina
            new_count = 1
        else:
            new_avg = (cicina_avg * cicina_count + cicina) / (cicina_count + 1)
            new_count = cicina_count + 1

        data = {
            "longest": cicina_for_db,
            "last": today,
            "average": new_avg,
            "count": new_count
        }
        supabase.from_('users').update({'cicina': data}).eq('id', inter.author.id).execute()
        await inter.response.send_message(msg)


def setup(client):
    client.add_cog(Cicina(client))
