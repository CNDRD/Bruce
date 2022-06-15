from func.cicina import get_cicina_today, get_random_cicina
from func.firebase_init import db

import disnake
from disnake.ext.commands import Param
from disnake.ext import commands

from datetime import datetime
from typing import Literal
from pytz import timezone
import yaml


# Config Load
local_timezone = yaml.safe_load(open("config.yml")).get("local_timezone")


class Cicina(commands.Cog):
    def __init__(self, client):
        """Cicina command."""
        self.client = client

    @commands.slash_command(name="cicina", description="Shows your cicina size")
    async def cicina(
            self,
            inter: disnake.ApplicationCommandInteraction,
            board: Literal["Today", "Average", "All Time"] = Param(None, desc="Pick a leaderboard")
    ):
        await inter.response.defer()

        uid = inter.author.id
        today = datetime.now(timezone(local_timezone)).strftime("%Y-%m-%d")
        cicina = get_random_cicina()

        match board:
            case "Today":
                cicina_today = db.child("cicinaToday").get().val() or None
                list_of_today = get_cicina_today(cicina_today, today)

                if cicina_today is None or list_of_today is None:
                    return await inter.edit_original_message(content="Nobody claimed their cicina today")

                list_of_today_sorted = sorted(list_of_today, key=lambda x: x["cicina"], reverse=True)

                top_msg = "**Today's top cicina's:**\n"
                peep_count = 0
                for _ in list_of_today_sorted:
                    usr = self.client.get_user(int(list_of_today_sorted[peep_count]["uid"]))
                    if not usr:
                        continue
                    cic = list_of_today_sorted[peep_count]["cicina"]
                    top_msg += f"**{peep_count + 1}.** {usr.name} with ***{cic}*** *cm*\n"
                    peep_count += 1
                    if peep_count == 30:
                        break
                return await inter.edit_original_message(content=top_msg)

            case "Average" | "All Time":
                db_entry = "cicina_avg" if board == "Average" else "cicina_longest"

                all_users = db.child("users").get()
                users_with_cicina = [user.val() for user in all_users.each() if user.val().get("cicina_avg")]

                # Only show peeps that tried their cicina more than once
                users_with_cicina = [u for u in users_with_cicina if u.get("cicina_count") > 1]
                # And sort them from biggest to smallest
                users_with_cicina = sorted(users_with_cicina, key=lambda x: x[db_entry], reverse=True)[:30]

                mess = f"**Best {board.lower()} cicina** {'*(Top 30)*' if len(users_with_cicina) > 30 else ''}\n"
                place = 1
                for u in users_with_cicina:
                    mess += f"**{place}.** {u.get('username').split('#')[0]} with ***{round(u.get(db_entry), 3)}*** *cm*\n"
                    place += 1

                return await inter.edit_original_message(content=mess)

            case _:
                cicina_last = db.child("users").child(uid).child("cicina_last").get().val() or 0
                cicina_longest = db.child("users").child(uid).child("cicina_longest").get().val() or 0

                if cicina_last != today:
                    emote = disnake.utils.get(self.client.emojis, name="resttHA")
                    msg = f"Dĺžka tvojej ciciny je {cicina} centimetrov {emote}"

                    cicina_today_data = {"uid": uid, "cicina": cicina, "date": today}
                    db.child("cicinaToday").child(uid).update(cicina_today_data)

                else:
                    midnight_ts = int(datetime.now(timezone(local_timezone)).replace(hour=0, minute=0, second=0).timestamp() + 86400)
                    return await inter.edit_original_message(content=f"Cicina sa ti resetuje zajtra (~<t:{midnight_ts}:R>)")

                cicina_for_db = cicina if (cicina > cicina_longest) else cicina_longest

                cicina_avg = db.child("users").child(uid).child("cicina_avg").get().val()
                cicina_count = db.child("users").child(uid).child("cicina_count").get().val()

                if cicina_count is None:
                    new_avg = cicina
                    new_count = 1
                else:
                    new_avg = (cicina_avg * cicina_count + cicina) / (cicina_count + 1)
                    new_count = cicina_count + 1

                db.child("users").child(uid).update({
                    "cicina_longest": cicina_for_db,
                    "cicina_last": today,
                    "cicina_avg": new_avg,
                    "cicina_count": new_count
                })
                await inter.edit_original_message(content=msg)


def setup(client):
    client.add_cog(Cicina(client))
