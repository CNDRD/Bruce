from func.r6 import rainbow6stats
from func.firebase_init import db
from func.pubg import pubg_stats

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
r6_channel_id = config.get("r6_channel_id")
pubg_loop = config.get("pubg_loop")
pubg_loop_time = config.get("pubg_loop_time")

R6STATS_VERSION = 11


class GameStats(commands.Cog):
    def __init__(self, client):
        """Game Stat gathering loops."""
        self.client = client
        self.first_boot = True

        if dbr6_loop:
            self.dbr6.start()
        if pubg_loop:
            self.pubg.start()

        self.last_siege_update_ts = db.child("GameStats").child("lastUpdate").child(f"R6Sv{R6STATS_VERSION}").get().val()

        def wrtus(message):
            """Website Request To Update Siege."""
            if self.first_boot:
                self.first_boot = not self.first_boot
            else:
                request_diff = message["data"] - self.last_siege_update_ts
                if request_diff >= 180:
                    print("Restarting DBR6 following a website request")
                    if dbr6_loop:
                        if self.dbr6.is_running():
                            self.dbr6.restart()
                        else:
                            self.dbr6.start()
                        self.last_siege_update_ts = time.time()

        db.child("GameStats").child("updateRequests").child("R6S").stream(wrtus)

    @tasks.loop(minutes=dbr6_loop_time)
    async def dbr6(self):
        mmr_message = asyncio.new_event_loop().run_until_complete(rainbow6stats())
        if mmr_message:
            await self.client.get_channel(r6_channel_id).send(mmr_message)
        self.last_siege_update_ts = time.time()

    @dbr6.before_loop
    async def before_dbr6(self):
        await self.client.wait_until_ready()

    @tasks.loop(minutes=pubg_loop_time)
    async def pubg(self):
        pubg_stats()

    @pubg.before_loop
    async def before_pubg(self):
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(GameStats(client))
