from func.r6 import rainbow6stats
from func.apex import apex_stats
from func.firebase_init import db

from disnake.ext import commands, tasks

import asyncio
import yaml
import time

# Monkey patch
import nest_asyncio

nest_asyncio.apply()

# Config Load
config = yaml.safe_load(open("config.yml"))
dbr6_loop = config.get("dbr6_loop")
dbr6_loop_time = config.get("dbr6_loop_time")
apex_loop = config.get("apex_loop")
apex_loop_time = config.get("apex_loop_time")
r6_channel_id = config.get("r6_channel_id")

R6STATS_VERSION = 10
APEX_VERSION = 1


class GameStats(commands.Cog):
    def __init__(self, client):
        """Various Game Stats gathering loops."""
        self.client = client
        self.first_boot = True
        if dbr6_loop:
            self.dbr6.start()
        if apex_loop:
            self.apex.start()

        self.last_siege_update_ts = db.child("GameStats").child("lastUpdate").child(f"R6Sv{R6STATS_VERSION}").get().val()

        def wrtus(message):
            """Website Request To Update Siege."""
            if self.first_boot:
                self.first_boot = not self.first_boot
            else:
                request_diff = message["data"] - self.last_siege_update_ts
                if request_diff >= 180:
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
        users = db.child("GameStats").child("IDs").get()
        mmr_watch_data = db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").child("mmr_watch").get().val()
        a = {}
        for u in users.each():
            if (ubi_id := u.val().get("ubiID")) is not None:
                a[ubi_id] = u.val().get("discordUsername")

        data, mmr_message = asyncio.new_event_loop().run_until_complete(rainbow6stats(a, mmr_watch_data, self.last_siege_update_ts))
        if mmr_message:
            await self.client.get_channel(r6_channel_id).send(mmr_message)

        db.child("GameStats").child(f"R6Sv{R6STATS_VERSION}").update(data)
        db.child('GameStats').child("lastUpdate").update({f"R6Sv{R6STATS_VERSION}": int(time.time())})
        self.last_siege_update_ts = time.time()

    @dbr6.before_loop
    async def before_dbr6(self):
        await self.client.wait_until_ready()

    @tasks.loop(minutes=apex_loop_time)
    async def apex(self):
        ape_sex_stats = apex_stats()
        db.child("GameStats").child(f"ApexV{APEX_VERSION}").update(ape_sex_stats)
        db.child("GameStats").child("lastUpdate").update({f"ApexV{APEX_VERSION}": int(time.time())})

    @apex.before_loop
    async def before_apex(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(GameStats(client))
