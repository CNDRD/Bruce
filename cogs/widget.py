from func.firebase_init import db
from func.widget import gimme_them_stats

from disnake.ext import commands, tasks

import yaml


## Config Load ##
config = yaml.safe_load(open('config.yml'))
server_id = config.get('server_id')
bot_mod_role_id = config.get('bot_mod_role_id')


class Widget(commands.Cog):
    def __init__(self, client):
        """Custom Widget."""
        self.client = client
        self.widget_loop.start()

    @tasks.loop(hours=69.69)
    async def widget_loop(self):
        diskito = self.client.get_guild(server_id)
        widgeee = {}
        for member in diskito.members:
            if not member.bot:
                widgeee[member.id] = gimme_them_stats(member)
        db.child("widget").set(widgeee)


    @widget_loop.before_loop
    async def before_widget_loop(self):
        await self.client.wait_until_ready()


    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if after.guild.id != server_id: return
        if after.bot: return

        x = gimme_them_stats(after)
        db.child("widget").child(x["uid"]).update(x)


def setup(client):
    client.add_cog(Widget(client))
